"""
Fase 4 — Bloque 4C (complemento): aislamiento de la sección de sostenibilidad por
DENSIDAD DE VOCABULARIO ESG, para los informes donde el índice del PDF NO da una
subsección fiable (método 'fuente', 'sin_toc', o 'toc' sin sostenibilidad localizada).

Idea: puntuar cada página por nº de términos ESG por 100 palabras y quedarse con el
bloque contiguo de páginas con densidad alta (fusionando huecos cortos). Es robusto e
INDEPENDIENTE de los epígrafes y la maquetación (resuelve informes con mucho diseño
tipo Kering/Gecina donde la heurística de epígrafes falla).

NO toca las 126 secciones fiables ya extraídas por índice (Decisión 012): solo rellena
las dudosas. Escribe `_sus.txt` y actualiza `secciones_manifest.csv`
(columnas sus_ini/sus_fin/sus_pp/sus_ok/sus_confianza = 'densidad').

Uso:
  python scripts/extraction/fase4_sost_densidad.py            # rellena las dudosas
  python scripts/extraction/fase4_sost_densidad.py --empresa KER --año 2024
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
SEC_DIR = BASE_DIR / "data" / "interim" / "secciones"
TRACKING_PATH = BASE_DIR / "data" / "external" / "tracking_descargas.csv"
MANIFEST_PATH = BASE_DIR / "data" / "interim" / "secciones_manifest.csv"

# Vocabulario ESG (raíces, minúsculas). Cubre medio ambiente, social y gobernanza + CSRD/ESRS.
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

UMBRAL = 2.5    # términos ESG por 100 palabras para marcar página "de sostenibilidad"
GAP = 3         # huecos de hasta 3 páginas no rompen el bloque (fotos, separadores)
MIN_LEN = 5     # bloques de < 5 páginas se descartan (picos aislados)


def densidad_paginas(doc):
    out = []
    for p in doc:
        t = p.get_text().lower()
        w = len(t.split())
        out.append(len(RX.findall(t)) / max(w, 1) * 100)
    return out


def mayor_bloque(dn, umb=UMBRAL, gap=GAP, minlen=MIN_LEN):
    """Mayor bloque contiguo (por masa ESG) de páginas con densidad >= umb, fusionando
    huecos <= gap. Devuelve (ini, fin) 1-based [ini, fin), o None."""
    runs = []
    i, n = 0, len(dn)
    while i < n:
        if dn[i] >= umb:
            last = i
            k = i + 1
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
    best = max(runs, key=lambda r: sum(dn[r[0]:r[1]]))
    return best[0] + 1, best[1]


def localizar_pdf(pais, ticker, año):
    p = RAW_DIR / pais / ticker / f"{ticker}_{año}_integrated.pdf"
    if p.exists():
        return p
    m = list(RAW_DIR.glob(f"**/{ticker}_{año}_*.pdf"))
    return m[0] if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--empresa")
    ap.add_argument("--año")
    ap.add_argument("--nuevos", action="store_true",
                    help="Solo las 99 empresas de la ampliación (E098-E196).")
    args = ap.parse_args()

    man = pd.read_csv(MANIFEST_PATH, dtype=str)
    tr = pd.read_csv(TRACKING_PATH, dtype=str).fillna("")
    if "sus_confianza" not in man.columns:
        man["sus_confianza"] = ""

    # Dudosos = NO tienen sostenibilidad fiable por índice (Decisión 012/013).
    fiable = (man.metodo == "toc") & (man.sus_ok == "True")
    objetivo = man[~fiable].copy()
    if args.empresa:
        objetivo = objetivo[objetivo.ticker == args.empresa]
    if args.año:
        objetivo = objetivo[objetivo.año == str(args.año)]
    if args.nuevos:
        objetivo = objetivo[objetivo.id_empresa.str[1:].astype(int) >= 98]

    n_ok = n_no = 0
    for r in objetivo.itertuples():
        row = tr[(tr.id_empresa == r.id_empresa) & (tr.año == r.año)]
        pais = row.iloc[0]["pais"] if not row.empty else ""
        pdf = localizar_pdf(pais, r.ticker, r.año)
        if not pdf:
            continue
        doc = fitz.open(pdf)
        dn = densidad_paginas(doc)
        blk = mayor_bloque(dn)
        idx = man.index[(man.id_empresa == r.id_empresa) & (man.año == r.año)]
        if blk:
            ini, fin = blk
            texto = "\n".join(doc[i].get_text() for i in range(ini - 1, min(fin - 1, doc.page_count)))
            (SEC_DIR / f"{r.id_empresa}_{r.ticker}_{r.año}_sus.txt").write_text(texto, encoding="utf-8")
            man.loc[idx, ["sus_ini", "sus_fin", "sus_pp", "sus_ok", "sus_confianza"]] = \
                [str(ini), str(fin), str(fin - ini), "True", "densidad"]
            n_ok += 1
        else:
            man.loc[idx, "sus_confianza"] = "densidad_sin_bloque"
            n_no += 1
        doc.close()

    man.to_csv(MANIFEST_PATH, index=False)
    print(f"Densidad ESG aplicada a {len(objetivo)} dudosos → {n_ok} con bloque, {n_no} sin bloque.")
    fiable_n = int(fiable.sum())
    total_sus = (man.sus_ok == "True").sum()
    print(f"Sostenibilidad total ahora: {total_sus}/{len(man)} "
          f"(índice fiable {fiable_n} + densidad {n_ok}).")
    print("sus_confianza:", man.sus_confianza.value_counts().to_dict())


if __name__ == "__main__":
    main()
