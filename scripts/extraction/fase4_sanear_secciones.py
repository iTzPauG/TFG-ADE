"""
Fase 4C — Saneamiento de la segmentación management report / sostenibilidad.

Repara, de forma QUIRÚRGICA y solo sobre las entradas afectadas, tres defectos de
calidad detectados en la auditoría de `secciones_manifest.csv` (no toca lo que está bien):

  A) Secciones extraídas del PDF con FUENTE CORRUPTA. Los scripts 4C leían el texto
     nativo del PDF crudo (roto: \\x01\\x04…) en vez del texto remediado por OCR. Se
     re-genera el texto limpio POR PÁGINA (OCR solo en las páginas corruptas, misma
     lógica que `fase4_ocr_remediar.py`) y se reescribe la sección sobre su rango.

  B) `_sus` que en realidad capturó un ÍNDICE/PÁGINA DIVISORIA (no contenido): muy
     pocas palabras o estructura de tabla de contenidos (TGS 2023, AKERBP 2024, AF
     2022…). Se re-detecta la sostenibilidad por DENSIDAD de vocabulario ESG sobre el
     texto limpio (estricta → relajada) y se reescribe si aparece un bloque real.

  C) `_mr` que abarca CASI TODO el documento (fin de la narrativa no detectado → el
     management report incluye los estados financieros). Se busca el inicio de los
     estados financieros en el texto de cabecera de página y se re-corta el MR.

Seguridad: por defecto DRY-RUN (no escribe). Con --apply hace backup de cada fichero
modificado en `secciones/_bak_sanear/` antes de sobrescribir y actualiza el manifiesto.

Uso:
  python scripts/extraction/fase4_sanear_secciones.py            # dry-run (informe)
  python scripts/extraction/fase4_sanear_secciones.py --apply    # aplica cambios
  python scripts/extraction/fase4_sanear_secciones.py --apply --solo A   # solo bloque A
"""

import argparse
import io
import os
import re
import shutil
import warnings
from pathlib import Path

import fitz  # PyMuPDF
import pandas as pd

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
INTERIM_DIR = BASE_DIR / "data" / "interim"
SEC_DIR = INTERIM_DIR / "secciones"
BAK_DIR = SEC_DIR / "_bak_sanear"
TMP_OCR = INTERIM_DIR / "_tmp_ocr"
CACHE_DIR = INTERIM_DIR / "_paginas_ocr"  # texto limpio por página (cacheado para no re-OCR)
PAGE_SEP = "\f"  # separador de página en la caché
TRACKING_PATH = BASE_DIR / "data" / "external" / "tracking_descargas.csv"
MANIFEST_PATH = INTERIM_DIR / "secciones_manifest.csv"
IDIOMAS_PATH = INTERIM_DIR / "idiomas.csv"

# OCR: el entorno bloquea /tmp a subprocesos → TMPDIR dentro del repo antes de importar.
TMP_OCR.mkdir(parents=True, exist_ok=True)
os.environ["TMPDIR"] = str(TMP_OCR)
import pytesseract  # noqa: E402
from PIL import Image  # noqa: E402

for _cand in ("/opt/homebrew/bin/tesseract", "/usr/local/bin/tesseract", shutil.which("tesseract")):
    if _cand and Path(_cand).exists():
        pytesseract.pytesseract.tesseract_cmd = _cand
        break

LANG_TESS = {"en": "eng", "fr": "fra", "es": "spa", "de": "deu", "it": "ita"}
SW = {"the", "and", "of", "to", "in", "for", "le", "la", "les", "de", "des",
      "et", "que", "pour", "dans", "el", "los", "las", "en", "con"}

# Vocabulario ESG (idéntico a fase4_sost_densidad.py)
ESG_TERMS = [
    "climat", "emission", "greenhouse", "ghg", "scope 1", "scope 2", "scope 3", "carbon",
    "decarboni", "net zero", "net-zero", "renewable", "biodivers", "ecosystem", "circular",
    "pollution", "environmental", "sustainab", "esg", "csr", "materiality", "esrs", "taxonomy",
    "stakeholder", "diversity", "inclusion", "gender", "human rights", "supply chain",
    "governance", "ethic", "occupational", "community", "science-based", "sbti", "tcfd",
    "paris agreement", "due diligence", "waste", "water", "social responsib", "workforce",
    "employe", "health and safety", "decent work", "non-financial", "double materiality",
]
RX = re.compile("|".join(re.escape(t) for t in ESG_TERMS))
FIN_MARKERS = [
    "consolidated financial statements", "financial statements",
    "parent company financial statements", "company financial statements",
    "statutory accounts", "annual accounts", "company accounts",
]

UMBRAL, GAP, MIN_LEN = 2.5, 3, 5


def ctrl_ratio(t: str) -> float:
    if not t:
        return 0.0
    return sum(1 for c in t if ord(c) < 32 and c not in "\n\r\t") / len(t)


def pagina_corrupta(texto: str) -> bool:
    if len(texto) < 50:
        return False
    ctrl = ctrl_ratio(texto)
    toks = re.findall(r"[a-zà-öø-ÿ]+", texto.lower())
    fw = sum(1 for t in toks if t in SW) / max(len(toks), 1)
    return ctrl > 0.05 or fw < 0.03


def localizar_pdf(pais, ticker, año):
    p = RAW_DIR / pais / ticker / f"{ticker}_{año}_integrated.pdf"
    if p.exists():
        return p
    m = list(RAW_DIR.glob(f"**/{ticker}_{año}_*.pdf"))
    return m[0] if m else None


def paginas_nativas(doc):
    """Texto nativo por página (rápido, sin OCR). Para docs sin fuente corrupta."""
    return [page.get_text() for page in doc], 0


def paginas_limpias(doc, lang="eng"):
    """Texto por página: nativo, con OCR SOLO en las páginas con la capa de texto rota.
    Reservado a los pocos docs con fuente corrupta (caro: rasteriza + Tesseract)."""
    out, n_ocr = [], 0
    for page in doc:
        nativo = page.get_text()
        if pagina_corrupta(nativo):
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            # Tesseract puede emitir \f (form-feed); colisiona con PAGE_SEP de la caché → se quita.
            ocr = pytesseract.image_to_string(img, lang=lang).replace("\f", " ").replace("\x0c", " ")
            out.append(ocr)
            n_ocr += 1
        else:
            out.append(nativo.replace("\f", " ").replace("\x0c", " "))
    return out, n_ocr


def es_indice_o_divisor(txt: str) -> bool:
    """True si la sección capturó un índice / página divisoria en vez de contenido."""
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if len(txt.split()) < 250:
        return True
    tocish = sum(1 for l in lines if re.search(r"\d+\s*$", l) and len(l) < 80)
    return tocish / max(len(lines), 1) > 0.45


def densidad(paginas):
    out = []
    for t in paginas:
        tl = t.lower()
        out.append(len(RX.findall(tl)) / max(len(tl.split()), 1) * 100)
    return out


def mayor_bloque(dn, umb=UMBRAL, gap=GAP, minlen=MIN_LEN):
    runs, i, n = [], 0, len(dn)
    while i < n:
        if dn[i] >= umb:
            last, k = i, i + 1
            while k < n:
                if dn[k] >= umb:
                    last = k
                elif k - last > gap:
                    break
                k += 1
            runs.append((i, last + 1))
            i = last + 1
        else:
            i += 1
    runs = [r for r in runs if r[1] - r[0] >= minlen]
    if not runs:
        return None
    b = max(runs, key=lambda r: sum(dn[r[0]:r[1]]))
    return b[0] + 1, b[1]


def bloque_relajado(dn):
    pico = max(dn) if dn else 0
    umb = max(1.0, 0.35 * pico)
    runs, i, n = [], 0, len(dn)
    while i < n:
        if dn[i] >= umb:
            last, k = i, i + 1
            while k < n:
                if dn[k] >= umb:
                    last = k
                elif k - last > 3:
                    break
                k += 1
            runs.append((i, last + 1))
            i = last + 1
        else:
            i += 1
    runs = [r for r in runs if r[1] - r[0] >= 3]
    if not runs:
        if not dn:
            return None
        pk = dn.index(pico)
        return max(1, pk - 1), min(n, pk + 3), "densidad_baja"
    ini, fin = max(runs, key=lambda r: sum(dn[r[0]:r[1]]))
    media = sum(dn[ini:fin]) / (fin - ini)
    cal = "densidad" if (media >= 2.5 and fin - ini >= 5) else "densidad_baja"
    return ini + 1, fin, cal


def corte_estados_financieros(paginas):
    """Inicio (1-based) de los estados financieros por cabecera de página, o None.
    Si el marcador aparece en >40% de páginas es un running header → no fiable."""
    n = len(paginas)
    fs = [i for i in range(n) if any(m in paginas[i][:200].lower() for m in FIN_MARKERS)]
    if not fs or len(fs) > 0.4 * n:
        return None
    after = [i for i in fs if i >= 0.30 * n]  # corte en la mitad final
    return (after[0] + 1) if after else None


def escribir(path, texto, apply):
    if not apply:
        return
    BAK_DIR.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, BAK_DIR / path.name)
    path.write_text(texto, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="escribe cambios (por defecto dry-run)")
    ap.add_argument("--solo", choices=["A", "B", "C"], help="ejecutar solo un bloque")
    ap.add_argument("--nuevos", action="store_true",
                    help="Solo procesar las 99 empresas de la ampliación (E098-E196). "
                         "No toca E001-E097 (estado ya validado, Decisiones 015-016).")
    args = ap.parse_args()
    do = lambda b: args.solo is None or args.solo == b

    man = pd.read_csv(MANIFEST_PATH, dtype=str).fillna("")
    tr = pd.read_csv(TRACKING_PATH, dtype=str).fillna("")
    idi = pd.read_csv(IDIOMAS_PATH, dtype=str).fillna("") if IDIOMAS_PATH.exists() else None

    def lang_de(idd, año):
        if idi is None:
            return "eng"
        m = idi[(idi.id_empresa == idd) & (idi.año == str(año))]
        return LANG_TESS.get(m.iloc[0]["idioma"], "eng") if not m.empty else "eng"

    def f(x):
        try:
            return float(x)
        except Exception:
            return 0.0

    cambios = {"A": [], "B": [], "C": []}
    cache = {}  # (id,año) -> (paginas, n_ocr)

    # Set de docs con fuente intrínsecamente corrupta: SOLO estos usan la vía OCR (cara);
    # el resto usa texto nativo directo (rápido). El criterio NO puede ser el estado actual
    # del fichero de sección (si ya se saneó parece "limpio" y el bloque C lo re-extraería
    # del PDF crudo corrupto). Por eso la pertenencia se basa en: (1) existe caché OCR para
    # el doc — la caché solo se crea para PDFs realmente corruptos — y (2) detección por
    # contenido como respaldo. Así un doc corrupto SIEMPRE pasa por la caché en TODOS los bloques.
    corruptos = set()
    if CACHE_DIR.exists():
        for c in CACHE_DIR.glob("*.pages.txt"):
            parts = c.name[: -len(".pages.txt")].split("_")
            corruptos.add((parts[0], parts[-1]))  # (id_empresa, año)
    for r in man.itertuples():
        base = f"{r.id_empresa}_{r.ticker}_{r.año}"
        for suf in ("mr", "sus"):
            p = SEC_DIR / f"{base}_{suf}.txt"
            if p.exists() and ctrl_ratio(p.read_text(encoding="utf-8", errors="ignore")) > 0.02:
                corruptos.add((r.id_empresa, str(r.año)))

    def get_paginas(idd, ticker, año):
        key = (idd, str(año))
        if key in cache:
            return cache[key]
        row = tr[(tr.id_empresa == idd) & (tr.año == str(año))]
        pais = row.iloc[0]["pais"] if not row.empty else ""
        pdf = localizar_pdf(pais, ticker, año)
        if not pdf:
            cache[key] = (None, 0)
            return cache[key]
        if key in corruptos:
            # Caché en disco: el OCR de estos docs (cientos de páginas) se hace UNA vez.
            cpath = CACHE_DIR / f"{idd}_{ticker}_{año}.pages.txt"
            if cpath.exists():
                pags = cpath.read_text(encoding="utf-8").split(PAGE_SEP)
                cache[key] = (pags, 0)
                return cache[key]
            doc = fitz.open(pdf)
            pags, n_ocr = paginas_limpias(doc, lang_de(idd, año))  # OCR dirigido
            doc.close()
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cpath.write_text(PAGE_SEP.join(pags), encoding="utf-8")
        else:
            doc = fitz.open(pdf)
            pags, n_ocr = paginas_nativas(doc)                     # rápido, sin OCR
            doc.close()
        cache[key] = (pags, n_ocr)
        return cache[key]

    for r in man.itertuples():
        if args.nuevos and int(r.id_empresa[1:]) < 98:
            continue
        base = f"{r.id_empresa}_{r.ticker}_{r.año}"
        mr_p = SEC_DIR / f"{base}_mr.txt"
        sus_p = SEC_DIR / f"{base}_sus.txt"

        sus_txt = sus_p.read_text(encoding="utf-8", errors="ignore") if sus_p.exists() else ""
        mr_txt = mr_p.read_text(encoding="utf-8", errors="ignore") if mr_p.exists() else ""
        sus_corrupto = ctrl_ratio(sus_txt) > 0.02
        mr_corrupto = ctrl_ratio(mr_txt) > 0.02
        sus_indice = sus_txt and es_indice_o_divisor(sus_txt)

        # ---- Bloque A+B: corrupción (sus y/o mr) ----
        if do("A") and (sus_corrupto or mr_corrupto):
            pags, n_ocr = get_paginas(r.id_empresa, r.ticker, r.año)
            if pags:
                if mr_corrupto and r.mr_ini and r.mr_fin:
                    ini, fin = int(f(r.mr_ini)), int(f(r.mr_fin))
                    nuevo = "\n".join(pags[ini - 1:fin])
                    escribir(mr_p, nuevo, args.apply)
                    cambios["A"].append(f"{base}_mr  (re-OCR {n_ocr}pp, rango {ini}-{fin})")
                if sus_corrupto:
                    dn = densidad(pags)
                    blk = mayor_bloque(dn) or None
                    if blk:
                        ini, fin, cal = blk[0], blk[1], "densidad"
                    else:
                        ini, fin, cal = bloque_relajado(dn)
                    nuevo = "\n".join(pags[ini - 1:fin])
                    escribir(sus_p, nuevo, args.apply)
                    man.loc[r.Index, ["sus_ini", "sus_fin", "sus_pp", "sus_confianza"]] = \
                        [str(ini), str(fin), str(fin - ini), cal]
                    cambios["A"].append(f"{base}_sus (re-OCR, densidad {ini}-{fin} [{cal}])")
            continue  # ya regenerado; no aplicar B/C encima

        # ---- Bloque B: sus que capturó un índice/divisor ----
        if do("B") and sus_indice and not sus_corrupto:
            pags, _ = get_paginas(r.id_empresa, r.ticker, r.año)
            if pags:
                dn = densidad(pags)
                blk = mayor_bloque(dn)
                if blk:
                    ini, fin, cal = blk[0], blk[1], "densidad"
                else:
                    ini, fin, cal = bloque_relajado(dn)
                nuevo = "\n".join(pags[ini - 1:fin])
                # solo si el bloque nuevo es sustancialmente mayor que el índice capturado
                if len(nuevo.split()) > max(400, 3 * len(sus_txt.split())):
                    escribir(sus_p, nuevo, args.apply)
                    man.loc[r.Index, ["sus_ini", "sus_fin", "sus_pp", "sus_confianza"]] = \
                        [str(ini), str(fin), str(fin - ini), cal]
                    cambios["B"].append(
                        f"{base}_sus  índice→{ini}-{fin} [{cal}]  ({len(sus_txt.split())}→{len(nuevo.split())} palabras)")

        # ---- Bloque C: MR que abarca casi todo el documento ----
        if do("C") and r.npaginas and f(r.mr_fin) >= 0.85 * f(r.npaginas):
            pags, _ = get_paginas(r.id_empresa, r.ticker, r.año)
            if pags:
                corte = corte_estados_financieros(pags)
                ini = int(f(r.mr_ini)) or 1
                if corte and corte > ini and corte < 0.85 * f(r.npaginas):
                    nuevo = "\n".join(pags[ini - 1:corte])
                    escribir(mr_p, nuevo, args.apply)
                    man.loc[r.Index, ["mr_fin", "mr_pp"]] = [str(corte), str(corte - ini)]
                    cambios["C"].append(
                        f"{base}_mr  {int(f(r.mr_fin))}→{corte} (npp={int(f(r.npaginas))}, recorta {int(f(r.mr_fin))-corte}pp)")

    # Informe
    for blk, titulo in [("A", "A) Corrupción de fuente re-OCR"),
                        ("B", "B) _sus que capturó índice/divisor → densidad"),
                        ("C", "C) _mr documento-entero → recorte en estados financieros")]:
        if not do(blk):
            continue
        print(f"\n=== {titulo}: {len(cambios[blk])} cambios ===")
        for c in cambios[blk]:
            print("  " + c)

    total = sum(len(v) for v in cambios.values())
    if args.apply:
        man.to_csv(MANIFEST_PATH, index=False)
        print(f"\n[APLICADO] {total} cambios. Backups en {BAK_DIR.relative_to(BASE_DIR)}. Manifiesto actualizado.")
    else:
        print(f"\n[DRY-RUN] {total} cambios propuestos. Ejecuta con --apply para escribirlos.")


if __name__ == "__main__":
    main()
