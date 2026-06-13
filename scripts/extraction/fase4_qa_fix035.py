"""
Fase 4 — QA corpus.parquet: aplicación de las 4 correcciones quirúrgicas
detectadas por `fase4_qa_corpus.py` (Decisión 035).

1. Restos de "dot-leader" de TOC mal codificados (\\ufffd / runs de '.�') en
   clean_text de 10 filas (6 docs): E010_BOL_2023|mr, E045_BOL_2023|mr,
   E053_VPLAY B_2022|sus+mr, E053_VPLAY B_2023|sus+mr, E053_VPLAY B_2024|sus+mr,
   E061_CAST_2023|mr, E131_TEV_2022|sus. Se eliminan los runs y se recalcula n_chars
   (tokens/n_tokens no cambian: ni '.' ni '\\ufffd' son alfabéticos).

2. Línea de cabecera repetida 111 veces no eliminada en E013_1COV_2024|sus
   ("CAPITAL MARKET MANAGEMENT REPORT COMPENSATION REPORT FINANCIAL STATEMENTS
   FURTHER INFORMATION"). Se elimina y se re-lematiza esa fila.

3. Caracteres de control \\x7f (glifo de viñeta sin mapeo Unicode) en 5 filas
   (E089_ADEN_2022|mr, E089_ADEN_2023|sus, E089_ADEN_2024|sus+mr,
   E180_BAER_2023|mr). Se eliminan y se recalcula n_chars.

4. E174_NTGY_2023|sus tenía sus_ini/sus_fin=651-662 (bloque de densidad ESG mal
   ubicado, dentro de un anexo de auditoría escaneado, sus_fin=662 > mr_fin=334
   violando sus⊂mr) → solo 226 caracteres / 21 tokens. El TOC del PDF identifica
   "II. Non-financial information statement" en páginas 265-662; el bloque de
   mayor densidad ESG (264-340) confirma que el contenido relevante empieza en
   265. Se corrige a sus_ini=265, sus_fin=334 (=mr_fin, respeta sus⊂mr),
   sus_confianza='alta' (confirmado por TOC). Se regenera `_sus.txt`, se actualiza
   el manifiesto, y se regeneran las filas sus y mr de E174_NTGY_2023 en el corpus
   (mr_menos_sus ahora sí encuentra sus_txt dentro de mr_txt).

Backups: corpus.parquet -> corpus.parquet.bak_qa035 ; secciones_manifest.csv ->
secciones_manifest.csv.bak_qa035 ; _sus.txt antiguo de E174 -> _bak_qa035/.

Uso:
  python scripts/extraction/fase4_qa_fix035.py
"""

import re
import shutil
import warnings
from pathlib import Path

import fitz
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import spacy

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parents[2]
CORPUS = BASE_DIR / "data" / "processed" / "corpus.parquet"
MANIFEST = BASE_DIR / "data" / "interim" / "secciones_manifest.csv"
SEC_DIR = BASE_DIR / "data" / "interim" / "secciones"
BAK_DIR = SEC_DIR / "_bak_qa035"

DOTLEADER_RX = re.compile(r"[.�]{4,}")
MULTISPACE_RX = re.compile(r" {2,}")

# --- fixes 1+3: limpieza de clean_text por regex, recalcula n_chars ---
ROWS_DOTLEADER = [
    "E010_BOL_2023|mr", "E045_BOL_2023|mr",
    "E053_VPLAY B_2022|sus", "E053_VPLAY B_2022|mr",
    "E053_VPLAY B_2023|sus", "E053_VPLAY B_2023|mr",
    "E053_VPLAY B_2024|sus", "E053_VPLAY B_2024|mr",
    "E061_CAST_2023|mr", "E131_TEV_2022|sus",
]
ROWS_X7F = [
    "E089_ADEN_2022|mr", "E089_ADEN_2023|sus",
    "E089_ADEN_2024|sus", "E089_ADEN_2024|mr",
    "E180_BAER_2023|mr",
]

HEADER_E013 = ("CAPITAL MARKET MANAGEMENT REPORT COMPENSATION REPORT FINANCIAL "
               "STATEMENTS FURTHER INFORMATION\n")

# --- fix 4: rango sus corregido para E174_NTGY_2023 ---
E174_PDF = BASE_DIR / "data" / "raw" / "Spain" / "NTGY" / "NTGY_2023_integrated.pdf"
E174_SUS_INI, E174_SUS_FIN = 265, 334  # 1-indexado, inclusive-exclusivo como el resto del manifiesto


# --- limpieza/lematización (copiados de fase4_corpus.py para consistencia) ---
CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
PAGENUM = re.compile(r"^\s*(?:page|página|pag\.?|p\.)?\s*[ivxlcdm\d]{1,7}\s*(?:/\s*\d+)?\s*$", re.I)
SENT_END = re.compile(r"[.!?:][\"'»)\]]?$")


def quitar_cabeceras(lineas, n_pag):
    from collections import Counter
    strip = [l.strip() for l in lineas]
    freq = Counter(s for s in strip if s)
    umbral = max(4, int(0.20 * max(n_pag, 1)))
    out = []
    for raw, s in zip(lineas, strip):
        if not s:
            out.append("")
            continue
        if len(s) < 130 and freq[s] >= umbral:
            continue
        if PAGENUM.match(s):
            continue
        out.append(raw)
    return out


def reconstruir_parrafos(texto):
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
            buf = buf[:-1] + s
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
    if not sus_txt:
        return mr_txt, True
    i = mr_txt.find(sus_txt)
    if i != -1:
        resto = (mr_txt[:i] + "\n" + mr_txt[i + len(sus_txt):]).strip()
        return resto, True
    head = sus_txt[:200]
    j = mr_txt.find(head)
    if j != -1:
        tail = sus_txt[-200:]
        k = mr_txt.find(tail, j)
        if k != -1:
            resto = (mr_txt[:j] + "\n" + mr_txt[k + len(tail):]).strip()
            return resto, True
    return mr_txt, False


def main():
    print("Cargando corpus.parquet...", flush=True)
    df = pd.read_parquet(CORPUS)
    df["__clave"] = df["id"] + "|" + df["seccion"]

    # backups
    shutil.copy2(CORPUS, str(CORPUS) + ".bak_qa035")
    shutil.copy2(MANIFEST, str(MANIFEST) + ".bak_qa035")
    print("Backups creados: corpus.parquet.bak_qa035, secciones_manifest.csv.bak_qa035")

    # --- fix 1: dot-leader / ufffd ---
    n1 = 0
    for clave in ROWS_DOTLEADER:
        idx = df.index[df.__clave == clave]
        assert len(idx) == 1, clave
        i = idx[0]
        txt = df.at[i, "clean_text"]
        nuevo = MULTISPACE_RX.sub(" ", DOTLEADER_RX.sub(" ", txt))
        df.at[i, "clean_text"] = nuevo
        df.at[i, "n_chars"] = len(nuevo)
        n1 += 1
    print(f"[1/4] dot-leader/ufffd limpiado en {n1} filas")

    # --- fix 3: \x7f ---
    n3 = 0
    for clave in ROWS_X7F:
        idx = df.index[df.__clave == clave]
        assert len(idx) == 1, clave
        i = idx[0]
        txt = df.at[i, "clean_text"]
        nuevo = MULTISPACE_RX.sub(" ", txt.replace("\x7f", ""))
        df.at[i, "clean_text"] = nuevo
        df.at[i, "n_chars"] = len(nuevo)
        n3 += 1
    print(f"[3/4] caracteres de control \\x7f eliminados en {n3} filas")

    # carga spaCy (solo necesaria para fixes 2 y 4)
    print("Cargando spaCy en_core_web_sm...", flush=True)
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    nlp.max_length = 125_000

    # --- fix 2: cabecera repetida E013_1COV_2024|sus ---
    clave = "E013_1COV_2024|sus"
    idx = df.index[df.__clave == clave]
    assert len(idx) == 1, clave
    i = idx[0]
    txt = df.at[i, "clean_text"]
    n_antes = txt.count(HEADER_E013)
    nuevo = txt.replace(HEADER_E013, "")
    toks = lemmas_de(nlp, nuevo)
    df.at[i, "clean_text"] = nuevo
    df.at[i, "n_chars"] = len(nuevo)
    df.at[i, "tokens"] = toks
    df.at[i, "n_tokens"] = len(toks)
    print(f"[2/4] {clave}: eliminadas {n_antes} repeticiones de cabecera, "
          f"n_chars {len(txt)}->{len(nuevo)}, n_tokens recalculado={len(toks)}")

    # --- fix 4: rango sus de E174_NTGY_2023 ---
    man = pd.read_csv(MANIFEST, dtype=str)
    mi = man.index[(man.id_empresa == "E174") & (man.año == "2023")]
    assert len(mi) == 1
    mi = mi[0]
    mr_pp = float(man.at[mi, "mr_pp"])
    npp = float(man.at[mi, "npaginas"])

    BAK_DIR.mkdir(exist_ok=True)
    sus_p = SEC_DIR / "E174_NTGY_2023_sus.txt"
    if sus_p.exists():
        shutil.copy2(sus_p, BAK_DIR / sus_p.name)

    doc = fitz.open(E174_PDF)
    nuevo_sus_txt = "\n".join(doc[p].get_text() for p in range(E174_SUS_INI - 1, E174_SUS_FIN))
    doc.close()
    sus_p.write_text(nuevo_sus_txt, encoding="utf-8")

    sus_pp = E174_SUS_FIN - E174_SUS_INI
    man.loc[mi, ["sus_ini", "sus_fin", "sus_pp", "sus_confianza"]] = \
        [str(E174_SUS_INI), str(E174_SUS_FIN), str(sus_pp), "alta"]
    man.to_csv(MANIFEST, index=False)
    print(f"[4/4] E174_NTGY_2023: manifiesto actualizado sus 651-662(11pp,densidad) "
          f"-> {E174_SUS_INI}-{E174_SUS_FIN}({sus_pp}pp,alta); _sus.txt regenerado "
          f"(backup en {BAK_DIR.relative_to(BASE_DIR)})")

    # regenerar fila sus
    cl_sus = limpiar(nuevo_sus_txt, sus_pp)
    toks_sus = lemmas_de(nlp, cl_sus)
    clave_sus = "E174_NTGY_2023|sus"
    i_sus = df.index[df.__clave == clave_sus][0]
    df.at[i_sus, "clean_text"] = cl_sus
    df.at[i_sus, "tokens"] = toks_sus
    df.at[i_sus, "n_tokens"] = len(toks_sus)
    df.at[i_sus, "n_chars"] = len(cl_sus)
    df.at[i_sus, "confianza"] = "alta"
    print(f"     E174_NTGY_2023|sus: n_chars={len(cl_sus)}, n_tokens={len(toks_sus)}, confianza=alta")

    # regenerar fila mr (mr_menos_sus ahora encuentra sus_txt dentro de mr_txt)
    mr_p = SEC_DIR / "E174_NTGY_2023_mr.txt"
    mr_txt = mr_p.read_text(encoding="utf-8", errors="ignore")
    resto, ok = mr_menos_sus(mr_txt, nuevo_sus_txt)
    cl_mr = limpiar(resto, max(mr_pp - sus_pp, 1))
    toks_mr = lemmas_de(nlp, cl_mr)
    full = E174_SUS_FIN >= 0.85 * npp and npp > 0  # = mr_fin >= 0.85*npp, sin cambios
    conf_mr = "mr_con_financieros" if full else "mr"
    clave_mr = "E174_NTGY_2023|mr"
    i_mr = df.index[df.__clave == clave_mr][0]
    df.at[i_mr, "clean_text"] = cl_mr
    df.at[i_mr, "tokens"] = toks_mr
    df.at[i_mr, "n_tokens"] = len(toks_mr)
    df.at[i_mr, "n_chars"] = len(cl_mr)
    df.at[i_mr, "confianza"] = conf_mr
    print(f"     E174_NTGY_2023|mr: resta_mr_ok={ok}, n_chars={len(cl_mr)}, "
          f"n_tokens={len(toks_mr)}, confianza={conf_mr}")

    # --- escribir corpus.parquet ---
    df = df.drop(columns="__clave")
    df["tokens"] = df["tokens"].apply(lambda x: list(x) if x is not None else [])
    esquema_original = pq.read_schema(str(CORPUS) + ".bak_qa035")
    tabla = pa.Table.from_pandas(df, schema=esquema_original, preserve_index=False)
    pq.write_table(tabla, CORPUS)
    print(f"\nGuardado {CORPUS.relative_to(BASE_DIR)} ({CORPUS.stat().st_size//1024//1024} MB)")


if __name__ == "__main__":
    main()
