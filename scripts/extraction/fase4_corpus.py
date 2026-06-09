"""
Fase 4D — Limpieza de texto y construcción del corpus.

Genera `data/processed/corpus.parquet` con UNA FILA POR SECCIÓN (Decisión 017, híbrida):
  - seccion="mr"  → management report SIN la subsección de sostenibilidad (mr menos sus,
                     para evitar el doble conteo ya que sus ⊂ mr, Decisión 016).
  - seccion="sus" → subsección de sostenibilidad aislada (Fase 4C).

Columnas: id, empresa, año, seccion, idioma, clean_text, tokens, confianza, n_tokens, n_chars
  - clean_text: texto limpio conservando MAYÚSCULAS y PUNTUACIÓN (para BERT/FinBERT/ClimateBERT).
  - tokens:     lemas en minúscula, sin stopwords ni puntuación (spaCy en_core_web_sm; LDA/TF-IDF).

Limpieza (Paso 4.11): cabeceras/pies repetidos, números de página, caracteres de control,
normalización de espacios, reconstrucción de párrafos rotos por columnas.

Uso:
  python scripts/extraction/fase4_corpus.py
  python scripts/extraction/fase4_corpus.py --limit 10   # prueba
"""

import argparse
import json
import os
import re
import sys
import time
import warnings
from collections import Counter
from pathlib import Path

import pandas as pd
import spacy

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM = BASE_DIR / "data" / "interim"
SEC_DIR = INTERIM / "secciones"
MANIFEST = INTERIM / "secciones_manifest.csv"
IDIOMAS = INTERIM / "idiomas.csv"
MUESTRA = BASE_DIR / "data" / "external" / "empresas_muestra.csv"
OUT = BASE_DIR / "data" / "processed" / "corpus.parquet"
PARTIAL = BASE_DIR / "data" / "processed" / "_corpus_partial.jsonl"  # checkpoint resumible

CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
PAGENUM = re.compile(r"^\s*(?:page|página|pag\.?|p\.)?\s*[ivxlcdm\d]{1,7}\s*(?:/\s*\d+)?\s*$", re.I)
SENT_END = re.compile(r"[.!?:][\"'»)\]]?$")


def f(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def quitar_cabeceras(lineas, n_pag):
    """Elimina cabeceras/pies (líneas que reaparecen ~una vez por página) y números de página."""
    strip = [l.strip() for l in lineas]
    freq = Counter(s for s in strip if s)
    umbral = max(4, int(0.20 * max(n_pag, 1)))
    out = []
    for raw, s in zip(lineas, strip):
        if not s:
            out.append("")
            continue
        if len(s) < 130 and freq[s] >= umbral:      # cabecera/pie repetido
            continue
        if PAGENUM.match(s):                          # número de página suelto
            continue
        out.append(raw)
    return out


def reconstruir_parrafos(texto):
    """Une líneas partidas por maquetación (line-wrap/columnas); de-hifenación; una frase
    por línea. Conserva mayúsculas y puntuación."""
    out, buf = [], ""
    for l in texto.split("\n"):
        s = l.strip()
        if not s:
            if buf:
                out.append(buf)
                buf = ""
            continue
        if not buf:
            buf = s
        elif buf.endswith("-"):
            buf = buf[:-1] + s                        # palabra cortada con guion
        else:
            buf += " " + s
        if SENT_END.search(buf):
            out.append(buf)
            buf = ""
    if buf:
        out.append(buf)
    return "\n".join(out)


def limpiar(texto, n_pag):
    texto = CTRL.sub(" ", texto)
    lineas = quitar_cabeceras(texto.split("\n"), n_pag)
    texto = reconstruir_parrafos("\n".join(lineas))
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r" *\n *", "\n", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def lemmas_de(nlp, texto, chunk=120_000):
    """Lematiza UN texto troceándolo en chunks (frontera de línea) y procesándolos
    en-proceso (nproc=1, sin IPC, una sola copia del modelo → memoria mínima).
    Devuelve la lista de lemas. Los Doc se liberan en cada iteración."""
    piezas = []
    if len(texto) <= chunk:
        piezas = [texto]
    else:
        pos = 0
        while pos < len(texto):
            end = min(pos + chunk, len(texto))
            if end < len(texto):
                nl = texto.rfind("\n", pos, end)
                if nl > pos:
                    end = nl
            piezas.append(texto[pos:end])
            pos = end
    toks = []
    for doc in nlp.pipe(piezas, batch_size=4):
        toks.extend(t.lemma_.lower() for t in doc
                    if t.is_alpha and not t.is_stop and len(t.lemma_) > 2)
    return toks


def mr_menos_sus(mr_txt, sus_txt):
    """Quita del management report el bloque contiguo de la sostenibilidad (sus ⊂ mr).
    sus_txt es substring de mr_txt (ambos salen del mismo pags[]). Si no se localiza
    exacto, recorta por solापe de prefijo/sufijo; en último caso devuelve mr completo."""
    if not sus_txt:
        return mr_txt, True
    i = mr_txt.find(sus_txt)
    if i != -1:
        resto = (mr_txt[:i] + "\n" + mr_txt[i + len(sus_txt):]).strip()
        return resto, True
    # fallback: quitar por bloque de líneas coincidentes (tolerante a un \n distinto)
    head = sus_txt[:200]
    j = mr_txt.find(head)
    if j != -1:
        tail = sus_txt[-200:]
        k = mr_txt.find(tail, j)
        if k != -1:
            resto = (mr_txt[:j] + "\n" + mr_txt[k + len(tail):]).strip()
            return resto, True
    return mr_txt, False  # no se pudo restar (raro)


def filas_de_doc(r, nombres, lang):
    """Devuelve la(s) fila(s) (metadatos + clean_text) de un documento del manifiesto,
    SIN lematizar. Lee los .txt aquí para no tener todo el corpus en RAM a la vez."""
    base = f"{r.id_empresa}_{r.ticker}_{r.año}"
    mr_p = SEC_DIR / f"{base}_mr.txt"
    sus_p = SEC_DIR / f"{base}_sus.txt"
    mr_txt = mr_p.read_text(encoding="utf-8", errors="ignore") if mr_p.exists() else ""
    sus_txt = sus_p.read_text(encoding="utf-8", errors="ignore") if sus_p.exists() else ""
    npp = f(r.npaginas)
    empresa = nombres.get(r.id_empresa, r.ticker)
    idioma = lang.get((r.id_empresa, r.año), "en")
    out = []
    if sus_txt.strip():
        cl = limpiar(sus_txt, f(r.sus_pp))
        if len(cl) > 100:
            out.append((dict(id=base, empresa=empresa, año=r.año, seccion="sus",
                             idioma=idioma, confianza=r.sus_confianza or "sus"), cl))
    if mr_txt.strip():
        resto, ok = mr_menos_sus(mr_txt, sus_txt)
        cl = limpiar(resto, max(f(r.mr_pp) - f(r.sus_pp), 1))
        if len(cl.split()) > 40:        # descarta MR-resto trivial (doc ~todo sostenibilidad)
            full = f(r.mr_fin) >= 0.85 * npp and npp > 0
            conf = "mr_con_financieros" if full else "mr"
            out.append((dict(id=base, empresa=empresa, año=r.año, seccion="mr",
                             idioma=idioma, confianza=conf), cl))
    return out, (0 if ok else 1) if mr_txt.strip() else 0


def jsonl_a_parquet():
    """Convierte el checkpoint JSONL -> parquet en BATCHES (memoria acotada: nunca
    carga el corpus entero en un DataFrame)."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    cols = ["id", "empresa", "año", "seccion", "idioma",
            "clean_text", "tokens", "confianza", "n_tokens", "n_chars"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    writer = None
    n = 0
    sec = Counter()
    conf = Counter()
    sus_tok, mr_tok = [], []
    buf = []
    with open(PARTIAL, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            buf.append(rec)
            n += 1
            sec[rec["seccion"]] += 1
            conf[rec["confianza"]] += 1
            (sus_tok if rec["seccion"] == "sus" else mr_tok).append(rec["n_tokens"])
            if len(buf) >= 40:
                tbl = pa.Table.from_pylist(buf).select(cols)
                writer = writer or pq.ParquetWriter(OUT, tbl.schema)
                writer.write_table(tbl); buf = []
    if buf:
        tbl = pa.Table.from_pylist(buf).select(cols)
        writer = writer or pq.ParquetWriter(OUT, tbl.schema)
        writer.write_table(tbl)
    if writer:
        writer.close()
    med = lambda x: int(pd.Series(x).median()) if x else 0
    print(f"\n=== corpus.parquet: {n} filas ===")
    print(f"  guardado en {OUT.relative_to(BASE_DIR)} ({OUT.stat().st_size//1024} KB)")
    print("  por sección:", dict(sec))
    print(f"  tokens/fila — mediana sus: {med(sus_tok)} | mr: {med(mr_tok)}")
    print("  confianza:", dict(conf))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--fresh", action="store_true", help="ignora el checkpoint y empieza de cero")
    ap.add_argument("--chunk", type=int, default=120_000)
    args = ap.parse_args()

    man = pd.read_csv(MANIFEST, dtype=str).fillna("")
    nombres = pd.read_csv(MUESTRA, dtype=str).drop_duplicates("id_empresa").set_index("id_empresa")["nombre"].to_dict()
    idi = pd.read_csv(IDIOMAS, dtype=str).fillna("")
    lang = {(r.id_empresa, r.año): r.idioma for r in idi.itertuples()}
    if args.limit:
        man = man.head(args.limit)

    PARTIAL.parent.mkdir(parents=True, exist_ok=True)
    if args.fresh and PARTIAL.exists():
        PARTIAL.unlink()

    # claves ya hechas (resume tras reinicio): el JSONL es la fuente de verdad
    hechas = set()
    if PARTIAL.exists():
        with open(PARTIAL, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        rr = json.loads(line)
                        hechas.add(f"{rr['id']}|{rr['seccion']}")
                    except Exception:
                        pass
    print(f"Checkpoint: {len(hechas)} filas ya hechas. Manifiesto: {len(man)} docs.", flush=True)

    # carga spaCy UNA vez (tagger+lemmatizer; sin parser/ner). En-proceso: 1 sola copia.
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    nlp.max_length = args.chunk + 5000

    total_docs = len(man)
    t0 = time.time()
    n_nuevas = 0
    n_resta_fallida = 0
    fh = open(PARTIAL, "a", encoding="utf-8")
    try:
        for di, r in enumerate(man.itertuples(), 1):
            filas, rf = filas_de_doc(r, nombres, lang)
            n_resta_fallida += rf
            for rec, cl in filas:
                clave = f"{rec['id']}|{rec['seccion']}"
                if clave in hechas:
                    continue
                toks = lemmas_de(nlp, cl, chunk=args.chunk)
                rec["clean_text"] = cl
                rec["tokens"] = toks
                rec["n_tokens"] = len(toks)
                rec["n_chars"] = len(cl)
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
                os.fsync(fh.fileno())          # persistido a disco YA (sobrevive a reinicio)
                hechas.add(clave)
                n_nuevas += 1
            # progreso en % por documentos del manifiesto
            pct = int(100 * di / total_docs)
            el = time.time() - t0
            eta = el / max(di, 1) * (total_docs - di)
            bar = "#" * (pct // 4) + "-" * (25 - pct // 4)
            sys.stdout.write(f"\r  [{bar}] {pct:3d}%  doc {di}/{total_docs}  "
                             f"filas+{n_nuevas}  {el:5.0f}s  ETA {eta:5.0f}s   ")
            sys.stdout.flush()
    finally:
        fh.close()
    print(f"\n  lematización OK en {time.time()-t0:.0f}s "
          f"(+{n_nuevas} filas nuevas, resta MR fallida: {n_resta_fallida})", flush=True)

    # ensamblado final JSONL -> parquet (en batches, memoria acotada)
    jsonl_a_parquet()


if __name__ == "__main__":
    main()
