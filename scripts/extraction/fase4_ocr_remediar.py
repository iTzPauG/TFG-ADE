"""
Fase 4A (remediación) — OCR híbrido de informes con fuentes corruptas.

Para los PDFs cuya capa de texto está rota (fuente embebida sin cmap/ToUnicode,
ver docs/fase4_idiomas.md), reconstruye el .txt así:
  - páginas con texto nativo legible  → se conserva el texto nativo (mejor calidad)
  - páginas corruptas                 → se rasterizan con PyMuPDF y se pasan por OCR

No usa pdf2image/poppler: rasteriza con `fitz` (PyMuPDF) directamente.
Sobrescribe data/interim/{id}_{ticker}_{año}.txt y guarda copia del original en
data/interim/_corruptos/{...}.pre_ocr.txt para trazabilidad.

Uso:
  python scripts/extraction/fase4_ocr_remediar.py --id E041            # idioma auto (idiomas.csv)
  python scripts/extraction/fase4_ocr_remediar.py --id E033 --lang fra
  python scripts/extraction/fase4_ocr_remediar.py --id E041 --dpi 400  # más resolución
"""

import argparse
import io
import os
import re
import shutil
from pathlib import Path

import fitz  # PyMuPDF
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
INTERIM_DIR = BASE_DIR / "data" / "interim"
BACKUP_DIR = INTERIM_DIR / "_corruptos"
TMP_OCR = INTERIM_DIR / "_tmp_ocr"

# IMPORTANTE: pytesseract escribe imágenes temporales y se las pasa a tesseract por ruta.
# El entorno bloquea la lectura de /tmp a subprocesos, así que forzamos TMPDIR dentro del
# repo (accesible) ANTES de importar pytesseract/usar tempfile.
TMP_OCR.mkdir(parents=True, exist_ok=True)
os.environ["TMPDIR"] = str(TMP_OCR)

import pytesseract  # noqa: E402
from PIL import Image  # noqa: E402

# Tesseract suele instalarse fuera del PATH del entorno conda
for cand in ("/opt/homebrew/bin/tesseract", "/usr/local/bin/tesseract", shutil.which("tesseract")):
    if cand and Path(cand).exists():
        pytesseract.pytesseract.tesseract_cmd = cand
        break
TRACKING_PATH = BASE_DIR / "data" / "external" / "tracking_descargas.csv"
IDIOMAS_PATH = INTERIM_DIR / "idiomas.csv"

# Mapeo código langdetect → código Tesseract
LANG_TESS = {"en": "eng", "fr": "fra", "es": "spa", "de": "deu", "it": "ita"}

SW = {"the", "and", "of", "to", "in", "for", "le", "la", "les", "de", "des",
      "et", "que", "pour", "dans", "el", "los", "las", "en", "con"}


def pagina_corrupta(texto: str) -> bool:
    """True si la capa de texto de la página está rota (CMap inválida)."""
    if len(texto) < 50:
        return False  # página (casi) vacía: nada que OCR-ear ni que esté 'roto'
    ctrl = sum(1 for c in texto if ord(c) < 32 and c not in "\n\t\r") / len(texto)
    toks = re.findall(r"[a-zà-öø-ÿ]+", texto.lower())
    fw = sum(1 for t in toks if t in SW) / max(len(toks), 1)
    return ctrl > 0.05 or fw < 0.03


def main():
    p = argparse.ArgumentParser(description="OCR híbrido de informes con capa de texto corrupta")
    p.add_argument("--id", required=True, help="id_empresa (ej. E041)")
    p.add_argument("--año", required=True, help="año del informe (ej. 2024)")
    p.add_argument("--lang", help="idioma Tesseract (eng/fra/spa/deu/ita). Por defecto: auto desde idiomas.csv")
    p.add_argument("--dpi", type=int, default=300, help="resolución de rasterizado para OCR")
    args = p.parse_args()

    track = pd.read_csv(TRACKING_PATH, dtype=str).fillna("")
    fila = track[(track["id_empresa"] == args.id) & (track["año"] == str(args.año))
                 & (track["estado"] == "descargado")]
    if fila.empty:
        print(f"[error] id {args.id} año {args.año} no encontrado / no descargado")
        return
    fila = fila.iloc[0]
    ticker, pais, año = fila["ticker"], fila["pais"], fila["año"]

    # Idioma
    lang = args.lang
    if not lang and IDIOMAS_PATH.exists():
        idi = pd.read_csv(IDIOMAS_PATH, dtype=str)
        m = idi[(idi["id_empresa"] == args.id) & (idi["año"] == str(args.año))]
        if not m.empty:
            lang = LANG_TESS.get(m.iloc[0]["idioma"], "eng")
    lang = lang or "eng"

    pdf = RAW_DIR / pais / ticker / f"{ticker}_{año}_integrated.pdf"
    if not pdf.exists():
        matches = list(RAW_DIR.glob(f"**/{ticker}_{año}_*.pdf"))
        pdf = matches[0] if matches else None
    if not pdf:
        print(f"[error] PDF no encontrado para {ticker} {año}")
        return

    txt_path = INTERIM_DIR / f"{args.id}_{ticker}_{año}.txt"
    print(f"OCR híbrido: {args.id} {ticker} {año} | idioma={lang} | dpi={args.dpi}")
    print(f"PDF: {pdf.relative_to(BASE_DIR)}")

    doc = fitz.open(pdf)
    partes, n_ocr, n_nativo = [], 0, 0
    for i, page in enumerate(doc):
        nativo = page.get_text()
        if pagina_corrupta(nativo):
            pix = page.get_pixmap(dpi=args.dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr = pytesseract.image_to_string(img, lang=lang)
            partes.append(ocr)
            n_ocr += 1
            if n_ocr % 20 == 0:
                print(f"  ...OCR {n_ocr} páginas")
        else:
            partes.append(nativo)
            n_nativo += 1
    doc.close()
    texto = "\n".join(partes)

    # Backup del original corrupto y sobrescritura
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if txt_path.exists():
        shutil.copy2(txt_path, BACKUP_DIR / f"{txt_path.stem}.pre_ocr.txt")
    txt_path.write_text(texto, encoding="utf-8")

    # Calidad final
    ctrl = sum(1 for c in texto if ord(c) < 32 and c not in "\n\t\r") / max(len(texto), 1)
    toks = re.findall(r"[a-zà-öø-ÿ]+", texto.lower())
    fw = sum(1 for t in toks if t in SW) / max(len(toks), 1)
    print(f"\n=== Resultado ===")
    print(f"Páginas: {n_nativo} nativas + {n_ocr} OCR = {n_nativo + n_ocr}")
    print(f"Texto final: {len(texto):,} chars | ratio_control={ctrl:.4f} | palabras_función={fw:.3f}")
    print(f"Backup original: {(BACKUP_DIR / (txt_path.stem + '.pre_ocr.txt')).relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
