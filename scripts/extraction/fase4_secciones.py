"""
Fase 4 — Bloque 4C: aislamiento del management report y de la subsección de sostenibilidad.

Estrategia primaria: usar el ÍNDICE/marcadores del PDF (get_toc) para localizar:
  - management report  = [inicio del cuerpo, primer epígrafe de gobernanza/estados financieros)
  - subsección sost.   = capítulos de sostenibilidad / información no financiera dentro de él
Fallback (PDFs sin índice usable): heurística sobre el texto extraído (líneas-epígrafe).

Salidas:
  - data/interim/secciones/{id}_{ticker}_{año}_mr.txt   (management report)
  - data/interim/secciones/{id}_{ticker}_{año}_sus.txt  (subsección sostenibilidad, si se halla)
  - data/interim/secciones_manifest.csv                 (rangos de página, método, cobertura)

Uso:
  python scripts/extraction/fase4_secciones.py            # todo el corpus
  python scripts/extraction/fase4_secciones.py --empresa KER --año 2024
  python scripts/extraction/fase4_secciones.py --solo-manifest  # no escribe .txt, solo manifiesto
"""

import argparse
import re
import warnings
from pathlib import Path

import fitz  # PyMuPDF
import pandas as pd

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
INTERIM_DIR = BASE_DIR / "data" / "interim"
SEC_DIR = INTERIM_DIR / "secciones"
TRACKING_PATH = BASE_DIR / "data" / "external" / "tracking_descargas.csv"
MANIFEST_PATH = INTERIM_DIR / "secciones_manifest.csv"

MIN_TOC = 8  # entradas mínimas para fiarnos del índice

# Epígrafes FUERTES que marcan el FIN del management report (substring sobre el título de NIVEL 1).
# Solo límites de capítulo inequívocos: gobernanza y estados financieros.
END_MARKERS = [
    "corporate governance", "financial statements", "remuneration report",
    "report of the supervisory board", "governance report", "statutory accounts",
    "annual accounts", "company accounts",
]
# Epígrafes de la subsección de sostenibilidad / información no financiera (substring, niveles 1-3).
SUS_MARKERS = [
    "sustainability", "non-financial", "non financial", "extra-financial", "extra financial",
    "corporate social responsibility", "sustainable development",
    "environmental, social and governance", "esg report", "csr report",
    "statement of non-financial", "declaration of extra",
]
# Arranque del cuerpo narrativo (para saltar portada/índice)
SKIP_START = ["contents", "table of contents", "cover", "glossary", "how to read"]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"^[\d\.\s•·\-]+", "", s)).strip().lower()


def match_any(title: str, markers: list[str]) -> bool:
    t = norm(title)
    return any(t == m or t.startswith(m) for m in markers)


def localizar_pdf(pais, ticker, año):
    p = RAW_DIR / pais / ticker / f"{ticker}_{año}_integrated.pdf"
    if p.exists():
        return p
    m = list(RAW_DIR.glob(f"**/{ticker}_{año}_*.pdf"))
    return m[0] if m else None


def secciones_por_toc(toc, npages):
    """Devuelve (mr_ini, mr_fin, sus_ini, sus_fin) en páginas 1-based, o None si no fiable."""
    entradas = [(lvl, norm(t), pg) for lvl, t, pg in toc if len(t) > 2]
    n1 = [e for e in entradas if e[0] == 1]
    if len(entradas) < 4:
        return None

    # Fin del MR: primer END_MARKER (substring) en NIVEL 1 tras el 8% del documento.
    umbral = max(2, int(0.08 * npages))

    def es_fin(t):
        return any(m in t for m in END_MARKERS)

    mr_fin = None
    candidatos = n1 if n1 else [e for e in entradas if e[0] <= 2]
    for lvl, t, pg in candidatos:
        if pg >= umbral and es_fin(t):
            mr_fin = pg
            break
    if mr_fin is None:
        mr_fin = npages

    # Inicio del MR: primera entrada de contenido (saltando portada/índice) antes del fin
    mr_ini = 1
    for lvl, t, pg in candidatos:
        if pg >= mr_fin:
            break
        if not any(t == m or t.startswith(m) for m in SKIP_START):
            mr_ini = pg
            break

    # Subsección sostenibilidad dentro de [mr_ini, mr_fin): niveles 1-3, substring.
    sus = [e for e in entradas if e[0] <= 3]
    sus_ini = sus_fin = None
    for i, (lvl, t, pg) in enumerate(sus):
        if mr_ini <= pg < mr_fin and any(m in t for m in SUS_MARKERS):
            sus_ini = pg
            for lvl2, t2, pg2 in sus[i + 1:]:
                if pg2 > pg and lvl2 <= lvl:
                    sus_fin = pg2
                    break
            sus_fin = sus_fin or mr_fin
            break
    return mr_ini, mr_fin, sus_ini, sus_fin


def pseudo_toc_por_fuente(doc):
    """Reconstruye un índice aproximado usando el tamaño de fuente: los epígrafes
    se imprimen en fuente notablemente mayor que el cuerpo. Devuelve [(nivel, título, pág)]
    con nivel 1 = fuente más grande, 2 = mediana. Para PDFs sin marcadores (TOC)."""
    from collections import Counter
    tam = Counter()
    for page in doc:
        for b in page.get_text("dict").get("blocks", []):
            for line in b.get("lines", []):
                for sp in line.get("spans", []):
                    if sp["text"].strip():
                        tam[round(sp["size"])] += len(sp["text"])
    if not tam:
        return []
    cuerpo = tam.most_common(1)[0][0]  # tamaño de fuente del cuerpo (el más frecuente)
    g1, g2 = cuerpo * 1.6, cuerpo * 1.25  # umbrales de epígrafe grande / mediano

    headings = []
    for pno, page in enumerate(doc, start=1):
        for b in page.get_text("dict").get("blocks", []):
            for line in b.get("lines", []):
                spans = [s for s in line.get("spans", []) if s["text"].strip()]
                if not spans:
                    continue
                txt = " ".join(s["text"] for s in spans).strip()
                size = max(s["size"] for s in spans)
                if 3 < len(txt) < 80 and not txt.replace(" ", "").isdigit():
                    if size >= g1:
                        headings.append((1, txt, pno))
                    elif size >= g2:
                        headings.append((2, txt, pno))
    return headings


def texto_paginas(doc, ini, fin):
    """Texto de las páginas [ini, fin) 1-based."""
    if ini is None:
        return ""
    return "\n".join(doc[i].get_text() for i in range(ini - 1, min(fin - 1, doc.page_count)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--empresa")
    ap.add_argument("--año")
    ap.add_argument("--solo-manifest", action="store_true")
    args = ap.parse_args()
    SEC_DIR.mkdir(parents=True, exist_ok=True)

    tr = pd.read_csv(TRACKING_PATH, dtype=str).fillna("")
    corp = tr[tr.estado == "descargado"]
    if args.empresa:
        corp = corp[corp.ticker == args.empresa]
    if args.año:
        corp = corp[corp.año == str(args.año)]

    filas = []
    for r in corp.itertuples():
        pdf = localizar_pdf(r.pais, r.ticker, r.año)
        if not pdf:
            continue
        doc = fitz.open(pdf)
        npages = doc.page_count
        toc = doc.get_toc(simple=True)
        metodo, res = "sin_toc", None
        if len(toc) >= MIN_TOC:
            res = secciones_por_toc(toc, npages)
            if res:
                metodo = "toc"
        if res is None:  # fallback: pseudo-índice por tamaño de fuente
            pseudo = pseudo_toc_por_fuente(doc)
            if pseudo:
                res = secciones_por_toc(pseudo, npages)
                if res:
                    metodo = "fuente"
        if res is None:
            doc.close()
            filas.append({"id_empresa": r.id_empresa, "ticker": r.ticker, "año": r.año,
                          "npaginas": npages, "metodo": metodo, "mr_ini": "", "mr_fin": "",
                          "mr_pp": "", "sus_ini": "", "sus_fin": "", "sus_pp": "", "sus_ok": False})
            continue

        mr_ini, mr_fin, sus_ini, sus_fin = res
        mr_pp = mr_fin - mr_ini
        sus_pp = (sus_fin - sus_ini) if sus_ini else 0

        if not args.solo_manifest:
            (SEC_DIR / f"{r.id_empresa}_{r.ticker}_{r.año}_mr.txt").write_text(
                texto_paginas(doc, mr_ini, mr_fin), encoding="utf-8")
            if sus_ini:
                (SEC_DIR / f"{r.id_empresa}_{r.ticker}_{r.año}_sus.txt").write_text(
                    texto_paginas(doc, sus_ini, sus_fin), encoding="utf-8")
        doc.close()

        filas.append({"id_empresa": r.id_empresa, "ticker": r.ticker, "año": r.año,
                      "npaginas": npages, "metodo": metodo,
                      "mr_ini": mr_ini, "mr_fin": mr_fin, "mr_pp": mr_pp,
                      "sus_ini": sus_ini or "", "sus_fin": sus_fin or "", "sus_pp": sus_pp,
                      "sus_ok": bool(sus_ini)})

    man = pd.DataFrame(filas)
    man.to_csv(MANIFEST_PATH, index=False)

    n = len(man)
    loc = man[man.metodo.isin(["toc", "fuente"])]
    print(f"=== Manifiesto: {n} informes ===")
    print("Método:", man.metodo.value_counts().to_dict())
    print(f"MR localizado: {len(loc)}/{n} ({100*len(loc)/n:.0f}%) | "
          f"sostenibilidad hallada: {loc.sus_ok.sum()}/{n} ({100*loc.sus_ok.mean():.0f}% de los localizados)")
    if loc.sus_ok.any():
        print(f"MR páginas mediana: {int(loc.mr_pp.median())} | sost. páginas mediana: "
              f"{int(loc[loc.sus_ok].sus_pp.median())}")
    print(f"No localizado (ni TOC ni fuente): {(man.metodo=='sin_toc').sum()}")
    print(f"Manifiesto: {MANIFEST_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
