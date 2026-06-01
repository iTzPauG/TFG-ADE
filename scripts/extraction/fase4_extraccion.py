"""
Fase 4 — Bloque 4A: extracción de texto bruto de los informes (PDF → .txt).

Itera sobre el corpus definido en tracking_descargas.csv (solo estado=descargado;
excluye los marcados como descartado, ver Decisión 010), localiza cada PDF en
data/raw/[pais]/[ticker]/, extrae el texto con PyMuPDF (fitz) y lo guarda en
data/interim/[TICKER]_[AÑO].txt.

Control de calidad: si el texto extraído tiene < 100 caracteres por página
(umbral guía: <1000 chars / 10 pp.) se marca como sospechoso de PDF escaneado
(`sospecha_escaneado=True`) — esos requieren OCR (Tesseract), que se aplica solo
si está disponible y se pasa --ocr. El resultado se registra en
data/interim/extraccion_log.csv para inspección (Paso 4.4).

Uso:
  python scripts/extraction/fase4_extraccion.py              # extrae todo el corpus
  python scripts/extraction/fase4_extraccion.py --empresa VOE  # solo un ticker
  python scripts/extraction/fase4_extraccion.py --limit 5     # prueba con 5 PDFs
  python scripts/extraction/fase4_extraccion.py --dry-run     # no escribe, solo informa
  python scripts/extraction/fase4_extraccion.py --forzar      # reextrae aunque ya exista .txt
  python scripts/extraction/fase4_extraccion.py --ocr         # intenta OCR en escaneados
"""

import argparse
import shutil
import sys
import traceback
from pathlib import Path

import fitz  # PyMuPDF
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
INTERIM_DIR = BASE_DIR / "data" / "interim"
TRACKING_PATH = BASE_DIR / "data" / "external" / "tracking_descargas.csv"
LOG_PATH = INTERIM_DIR / "extraccion_log.csv"

# Umbral de calidad: por debajo de esto, sospechamos PDF escaneado (sin capa de texto)
MIN_CHARS_POR_PAGINA = 100


def localizar_pdf(pais: str, ticker: str, año: str) -> Path | None:
    """Localiza el PDF de una empresa-año. Robusto a variaciones de nombre."""
    candidatos = [
        RAW_DIR / pais / ticker / f"{ticker}_{año}_integrated.pdf",
    ]
    for c in candidatos:
        if c.exists():
            return c
    # Fallback: glob por ticker_año en cualquier subcarpeta
    matches = list(RAW_DIR.glob(f"**/{ticker}_{año}_*.pdf"))
    return matches[0] if matches else None


def extraer_texto_pymupdf(path: Path) -> tuple[str, int]:
    """Extrae texto con PyMuPDF. Devuelve (texto, n_paginas)."""
    doc = fitz.open(path)
    try:
        n_paginas = doc.page_count
        partes = [page.get_text() for page in doc]
        return "\n".join(partes), n_paginas
    finally:
        doc.close()


def extraer_texto_ocr(path: Path) -> str:
    """OCR de respaldo para PDFs escaneados (lento: 10-20 min/informe)."""
    from pdf2image import convert_from_path
    import pytesseract

    imagenes = convert_from_path(str(path), dpi=200)
    partes = []
    for img in imagenes:
        # Multilingüe: inglés + idiomas europeos frecuentes en la muestra
        partes.append(pytesseract.image_to_string(img, lang="eng+spa+deu+fra+ita"))
    return "\n".join(partes)


def main():
    p = argparse.ArgumentParser(description="Fase 4A — extracción de texto bruto de PDFs")
    p.add_argument("--empresa", help="Filtra por ticker (ej. VOE)")
    p.add_argument("--año", help="Filtra por año (combinable con --empresa)")
    p.add_argument("--limit", type=int, help="Procesa como máximo N PDFs (prueba)")
    p.add_argument("--dry-run", action="store_true", help="No escribe nada, solo informa")
    p.add_argument("--forzar", action="store_true", help="Reextrae aunque exista el .txt")
    p.add_argument("--ocr", action="store_true", help="Aplica OCR a escaneados si Tesseract está disponible")
    args = p.parse_args()

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(TRACKING_PATH, dtype=str).fillna("")
    corpus = df[df["estado"] == "descargado"].copy()
    if args.empresa:
        corpus = corpus[corpus["ticker"] == args.empresa]
    if args.año:
        corpus = corpus[corpus["año"] == str(args.año)]
    n_descartados = (df["estado"] == "descartado").sum()

    if args.ocr and shutil.which("tesseract") is None:
        print("[aviso] --ocr pedido pero Tesseract no está instalado; los escaneados se marcarán sin OCR.")
        args.ocr = False

    registros = []
    procesados = 0
    print(f"Corpus: {len(corpus)} informes (estado=descargado). Excluidos descartado: {n_descartados}.\n")

    for _, fila in corpus.iterrows():
        if args.limit and procesados >= args.limit:
            break

        id_emp, ticker, pais, año = fila["id_empresa"], fila["ticker"], fila["pais"], fila["año"]
        pdf = localizar_pdf(pais, ticker, año)
        # id_empresa en el nombre para evitar colisiones de ticker (p.ej. BOL = Boliden y Bolloré)
        txt_path = INTERIM_DIR / f"{id_emp}_{ticker}_{año}.txt"

        base = {
            "id_empresa": id_emp, "ticker": ticker, "pais": pais, "año": año,
            "pdf_path": str(pdf.relative_to(BASE_DIR)) if pdf else "",
            "txt_path": str(txt_path.relative_to(BASE_DIR)),
        }

        if pdf is None:
            print(f"[ERROR] {ticker} {año}: PDF no encontrado en disco")
            registros.append({**base, "n_paginas": "", "n_chars": 0, "chars_por_pagina": 0,
                              "metodo": "", "sospecha_escaneado": "", "estado": "error",
                              "error": "PDF no encontrado"})
            continue

        if txt_path.exists() and not args.forzar:
            print(f"[skip] {ticker} {año}: .txt ya existe (usa --forzar para reextraer)")
            continue

        procesados += 1
        try:
            texto, n_pag = extraer_texto_pymupdf(pdf)
            n_chars = len(texto)
            cpp = n_chars / n_pag if n_pag else 0
            metodo = "pymupdf"
            escaneado = cpp < MIN_CHARS_POR_PAGINA

            if escaneado and args.ocr:
                print(f"[OCR] {ticker} {año}: {cpp:.0f} chars/pág → aplicando OCR (lento)...")
                texto = extraer_texto_ocr(pdf)
                n_chars = len(texto)
                cpp = n_chars / n_pag if n_pag else 0
                metodo = "ocr"
                escaneado = cpp < MIN_CHARS_POR_PAGINA

            flag = "  ⚠ SOSPECHA ESCANEADO" if escaneado else ""
            print(f"[OK] {ticker} {año}: {n_pag} pp, {n_chars:,} chars ({cpp:.0f}/pág){flag}")

            if not args.dry_run:
                txt_path.write_text(texto, encoding="utf-8")

            registros.append({**base, "n_paginas": n_pag, "n_chars": n_chars,
                              "chars_por_pagina": round(cpp, 1), "metodo": metodo,
                              "sospecha_escaneado": escaneado, "estado": "ok", "error": ""})
        except Exception as e:
            print(f"[ERROR] {ticker} {año}: {e}")
            registros.append({**base, "n_paginas": "", "n_chars": 0, "chars_por_pagina": 0,
                              "metodo": "", "sospecha_escaneado": "", "estado": "error",
                              "error": f"{type(e).__name__}: {e}"})
            traceback.print_exc(file=sys.stderr)

    # Volcado del log
    if registros and not args.dry_run:
        log_df = pd.DataFrame(registros)
        if LOG_PATH.exists() and args.empresa:
            # Actualización parcial: fusiona con log previo por (ticker, año)
            prev = pd.read_csv(LOG_PATH, dtype=str)
            prev = prev[~prev.set_index(["ticker", "año"]).index.isin(
                log_df.set_index(["ticker", "año"]).index)]
            log_df = pd.concat([prev, log_df], ignore_index=True)
        log_df.to_csv(LOG_PATH, index=False)

    # Resumen
    ok = sum(1 for r in registros if r["estado"] == "ok")
    err = sum(1 for r in registros if r["estado"] == "error")
    escan = sum(1 for r in registros if r.get("sospecha_escaneado") is True)
    print(f"\n=== Resumen ===")
    print(f"Procesados: {procesados} | OK: {ok} | Errores: {err} | Sospecha escaneado: {escan}")
    if not args.dry_run and registros:
        print(f"Log: {LOG_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
