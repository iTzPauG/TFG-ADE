"""
Fase 4 — Bloque 4C (cierre): resolución de los 13 casos marcados 'revisar' por
fase4_recalcular_limites.py --nuevos.

Estos 13 casos tienen metodo='toc' y sus_ok=True, pero el rango de sostenibilidad
localizado por índice cubre 58-99% del documento (claramente erróneo: o bien el
título de portada contiene "sustainability" y rompe la heurística de fin_de(), o
bien el capítulo de sostenibilidad del índice incluye después secciones de gobierno
corporativo/riesgos/estados financieros no separadas a nivel de índice).

Solución: aplicar el MISMO método de densidad de vocabulario ESG (mayor_bloque,
fase4_sost_densidad.py) ya usado para 280/586 documentos, restringido a localizar
el bloque contiguo de mayor densidad ESG en todo el documento. Verificado caso a
caso contra el índice del PDF (ver Decisión 033): en los casos con índice fiable
(SAN, ITX, TEF, FERR) el bloque de densidad cae DENTRO del capítulo de sostenibilidad
indicado por el índice; en los casos con índice degenerado (HEI, PUM) es la única
señal disponible.

Escribe el nuevo `_sus.txt` (backup del anterior en _bak_revisar13/) y actualiza
sus_ini/sus_fin/sus_pp/sus_confianza='densidad' en secciones_manifest.csv.
mr_ini/mr_fin/_mr.txt NO se tocan (fase4_corpus.py recalcula mr menos sus por texto).

Uso:
  python scripts/extraction/fase4_revisar13.py --dry-run  # solo muestra
  python scripts/extraction/fase4_revisar13.py            # aplica los 13
"""

import argparse
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
SEC_DIR = BASE_DIR / "data" / "interim" / "secciones"
BAK_DIR = SEC_DIR / "_bak_revisar13"
TRACKING_PATH = BASE_DIR / "data" / "external" / "tracking_descargas.csv"
MANIFEST_PATH = BASE_DIR / "data" / "interim" / "secciones_manifest.csv"

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
UMBRAL, GAP, MIN_LEN = 2.5, 3, 5


def densidad_paginas(doc):
    return [len(RX.findall(p.get_text().lower())) / max(len(p.get_text().split()), 1) * 100
            for p in doc]


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
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    man = pd.read_csv(MANIFEST_PATH, dtype=str)
    tr = pd.read_csv(TRACKING_PATH, dtype=str).fillna("")
    objetivo = man[man.sus_confianza == "revisar"]
    print(f"Casos 'revisar': {len(objetivo)}")

    if not args.dry_run:
        BAK_DIR.mkdir(exist_ok=True)

    for i, r in enumerate(objetivo.itertuples(), 1):
        row = tr[(tr.id_empresa == r.id_empresa) & (tr.año == r.año)]
        pais = row.iloc[0]["pais"] if not row.empty else ""
        pdf = localizar_pdf(pais, r.ticker, r.año)
        doc = fitz.open(pdf)
        dn = densidad_paginas(doc)
        blk = mayor_bloque(dn)
        npp = doc.page_count
        base = f"{r.id_empresa}_{r.ticker}_{r.año}"
        if not blk:
            print(f"[{i}/{len(objetivo)}] {base}: SIN bloque de densidad -> no se toca")
            doc.close()
            continue
        ini, fin = blk
        print(f"[{i}/{len(objetivo)}] {base}: sus {r.sus_ini}-{r.sus_fin} "
              f"({int(float(r.sus_fin) - float(r.sus_ini))}pp, {npp}pp doc) "
              f"-> {ini}-{fin} ({fin - ini}pp) [densidad]")

        if not args.dry_run:
            sus_p = SEC_DIR / f"{base}_sus.txt"
            if sus_p.exists():
                shutil.copy2(sus_p, BAK_DIR / sus_p.name)
            texto = "\n".join(doc[p].get_text() for p in range(ini - 1, min(fin - 1, npp)))
            sus_p.write_text(texto, encoding="utf-8")
            idx = man.index[(man.id_empresa == r.id_empresa) & (man.año == r.año)]
            man.loc[idx, ["sus_ini", "sus_fin", "sus_pp", "sus_confianza"]] = \
                [str(ini), str(fin), str(fin - ini), "densidad"]
        doc.close()

    if not args.dry_run:
        man.to_csv(MANIFEST_PATH, index=False)
        print("\n[APLICADO] manifiesto actualizado. Backups en", BAK_DIR)
        print("sus_confianza:", man.sus_confianza.value_counts().to_dict())
    else:
        print("\n[DRY-RUN] usa --apply (sin --dry-run) para aplicar.")


if __name__ == "__main__":
    main()
