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

# Fin del bloque narrativo = inicio de los ESTADOS FINANCIEROS (límite duro e inequívoco).
# NO se usa gobernanza como fin: en muchos URD la sostenibilidad va DESPUÉS de gobernanza.
FIN_MARKERS = [
    "consolidated financial statements", "financial statements",
    "parent company financial statements", "company financial statements",
    "statutory accounts", "annual accounts", "company accounts",
]
# Epígrafes de la subsección de sostenibilidad / información no financiera (substring).
SUS_MARKERS = [
    "sustainability", "non-financial", "non financial", "extra-financial", "extra financial",
    "corporate social responsibility", "sustainable development",
    "environmental, social and governance", "esg report", "csr report",
    "statement of non-financial", "declaration of extra", "non financial",
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


def find_sections(entradas, npages):
    """Lógica unificada para índice del PDF y pseudo-índice por fuente.
    entradas = lista de (nivel, título_normalizado, página). Nivel 1 = capítulo.
    Devuelve (mr_ini, mr_fin, sus_ini, sus_fin) en páginas 1-based, o None."""
    ents = [(lvl, norm(t), pg) for lvl, t, pg in entradas if pg >= 1 and len(norm(t)) > 2]
    if len(ents) < 4:
        return None
    caps = [e for e in ents if e[0] == 1] or [e for e in ents if e[0] <= 2]
    caps = sorted(caps, key=lambda e: e[2])
    umbral = max(2, int(0.06 * npages))

    # Fin del bloque narrativo = primer capítulo de estados financieros tras el umbral.
    mr_fin = npages
    for lvl, t, pg in caps:
        if pg >= umbral and any(m in t for m in FIN_MARKERS):
            mr_fin = pg
            break

    # Inicio: primer capítulo de contenido (saltando portada/índice).
    mr_ini = 1
    for lvl, t, pg in caps:
        if pg >= mr_fin:
            break
        if not any(t == m or t.startswith(m) for m in SKIP_START):
            mr_ini = pg
            break

    # Sostenibilidad: inicio = epígrafe (niveles 1-3) que casa con SUS_MARKERS dentro de
    # [mr_ini, mr_fin). Fin = siguiente CAPÍTULO que NO sea de sostenibilidad (así se agrupa
    # todo el capítulo CSR aunque tenga muchos sub-epígrafes). Se elige el inicio que
    # maximice la extensión resultante (el capítulo principal, no una mención corta).
    def es_sus(t):
        return any(m in t for m in SUS_MARKERS)

    sus_ents = [e for e in ents if e[0] <= 3]
    starts = sorted({pg for lvl, t, pg in sus_ents if mr_ini <= pg < mr_fin and es_sus(t)})

    def fin_de(start):
        for lvl, t, pg in caps:  # caps ya ordenado por página
            if pg > start and not es_sus(t):
                return min(pg, mr_fin)
        return mr_fin

    cand = [(s, fin_de(s)) for s in starts]
    sus_ini = sus_fin = None
    if cand:
        sus_ini, sus_fin = max(cand, key=lambda c: c[1] - c[0])
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
    g1, g2 = cuerpo * 1.7, cuerpo * 1.5  # umbrales de capítulo / sub-epígrafe

    headings = []
    for pno, page in enumerate(doc, start=1):
        for b in page.get_text("dict").get("blocks", []):
            lines = b.get("lines", [])
            if len(lines) > 3:  # bloques largos = párrafos, no epígrafes
                continue
            for line in lines:
                spans = [s for s in line.get("spans", []) if s["text"].strip()]
                if not spans:
                    continue
                txt = " ".join(s["text"] for s in spans).strip()
                size = max(s["size"] for s in spans)
                if 3 < len(txt) < 55 and re.search(r"[A-Za-z]", txt) and not txt.replace(" ", "").isdigit():
                    if size >= g1:
                        headings.append((1, norm(txt), pno))
                    elif size >= g2:
                        headings.append((2, norm(txt), pno))
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
            res = find_sections(toc, npages)
            if res:
                metodo = "toc"
        if res is None:  # fallback: pseudo-índice por tamaño de fuente
            pseudo = pseudo_toc_por_fuente(doc)
            if pseudo:
                res = find_sections(pseudo, npages)
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
