"""Integra los PDFs descargados manualmente en data/raw/_staging_ampliacion/lote{1..5}
a su ubicación definitiva data/raw/<pais>/<ticker>/<ticker>_<año>_integrated.pdf
y actualiza data/external/tracking_descargas.csv.

Decisión: ver docs/retomar_busqueda_manual.md.
"""
import glob
import os
import shutil
from datetime import date

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGING = os.path.join(ROOT, "data", "raw", "_staging_ampliacion")
TRACKING = os.path.join(ROOT, "data", "external", "tracking_descargas.csv")
MUESTRA = os.path.join(ROOT, "data", "external", "empresas_muestra.csv")

HOY = date.today().isoformat()

# URLs conocidas (recogidas en esta sesión por los agentes de búsqueda).
# clave: (ticker, año)
URLS = {
    ("BAER", 2022): "https://vpr.hkma.gov.hk/statics/assets/doc/100301/ar_22/ar_22_eng.pdf",
    ("BAER", 2023): "https://vpr.hkma.gov.hk/statics/assets/doc/100301/ar_23/ar_23_eng.pdf",
    ("BAER", 2024): "https://vpr.hkma.gov.hk/statics/assets/doc/100301/ar_24/ar_24_eng.pdf",
    ("TEV", 2024): "https://s24.q4cdn.com/720828402/files/doc_financials/2024/ar/2024-10-K-final-bannerless-ADA-tagged.pdf",
    ("CBK", 2024): "https://investor-relations.commerzbank.com/media/document/b986ba5a-dc1d-41a7-a708-dc3a010ecc32/assets/Commerzbank_Group_Annual_Report_2024.pdf",
    ("MEL", 2022): "https://www.cnmv.es/webservices/verdocumento/ver?e=v9HqPNns5YlUSPtwPKSsHiJs3cK80xVpwaYndxidzOuEhY8wWp9yOrsFup0pipEp",
    ("MEL", 2023): "https://www.cnmv.es/webservices/verdocumento/ver?e=6aBlB6q6WS2XwBwrYPeOryJs3cK80xVpwaYndxidzOuEhY8wWp9yOrsFup0pipEp",
    ("MEL", 2024): "https://www.cnmv.es/webservices/verdocumento/ver?e=4GB%2f848nSn2hla5pyYgtgSJs3cK80xVpwaYndxidzOuEhY8wWp9yOrsFup0pipEp",
    ("SRG", 2022): "https://www.snam.it/content/dam/snam/pages-attachments-search/en/documenti/bilanci-annuali/2022/annual_report_2022.pdf",
    ("SRG", 2023): "https://www.snam.it/content/dam/snam/pages-attachments-search/en/documenti/bilanci-annuali/2023/annual_report_2023.pdf",
    ("SRG", 2024): "https://www.snam.it/content/dam/snam/pages-attachments-search/en/documenti/bilanci-annuali/2024/annual_report_2024.pdf",
    ("DIE", 2022): "https://dieterengroup.imgix.net/annual-reports/INTEGRATED-REPORT-2022-ENG.pdf",
    ("DIE", 2023): "https://dieterengroup.imgix.net/annual-reports/240425_DIET_RA-2023_EN_interactive.pdf",
    ("DIE", 2024): "https://dieterengroup.imgix.net/annual-reports/250428_DIETEREN-RA24_UK-web-2_2025-08-12-161346_ujhd.pdf",
}

NOTAS_CON_URL = {
    ("MEL", 2022): "descarga manual ampliación (lote 4) — web oficial bloquea (403 Akamai), descargado vía registro CNMV (Management Report, EN)",
    ("MEL", 2023): "descarga manual ampliación (lote 4) — web oficial bloquea (403 Akamai), descargado vía registro CNMV (Management Report, EN)",
    ("MEL", 2024): "descarga manual ampliación (lote 4) — web oficial bloquea (403 Akamai), descargado vía registro CNMV (Management Report, EN)",
    ("TEV", 2024): "descarga manual ampliación (lote 4) — Teva presenta 10-K (no 20-F), EN",
    ("RIGN", 2024): "descarga manual ampliación (lote 3) — Transocean FY2024 = Form 10-K de SEC convertido a PDF (no hay annual report PDF separado)",
}

NOTA_GENERICA = "descargado en ampliación 99 empresas (búsqueda manual, lote {lote}) — URL no registrada"


def main():
    muestra = pd.read_csv(MUESTRA)
    ticker_pais = muestra.drop_duplicates("ticker").set_index("ticker")["pais"].to_dict()

    trk = pd.read_csv(TRACKING)
    cols = list(trk.columns)
    trk = trk.set_index(["ticker", "año"])

    files = []
    for lote in range(1, 6):
        for f in sorted(glob.glob(os.path.join(STAGING, f"lote{lote}", "*.pdf"))):
            files.append((lote, f))

    print(f"Total ficheros a integrar: {len(files)}")
    n_ok, n_err = 0, 0
    for i, (lote, f) in enumerate(files, 1):
        base = os.path.basename(f)
        ticker, año_str = os.path.splitext(base)[0].split("_")
        año = int(año_str)

        pais = ticker_pais.get(ticker)
        if pais is None:
            print(f"  [SKIP] {base}: ticker '{ticker}' no encontrado en empresas_muestra.csv")
            n_err += 1
            continue

        dest_dir = os.path.join(ROOT, "data", "raw", pais, ticker)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, f"{ticker}_{año}_integrated.pdf")

        if os.path.exists(dest):
            print(f"  [SKIP] {base}: ya existe {dest}")
            n_err += 1
            continue

        shutil.move(f, dest)

        # actualizar tracking
        key = (ticker, año)
        if key not in trk.index:
            print(f"  [WARN] {base}: ({ticker}, {año}) no encontrado en tracking_descargas.csv")
        else:
            trk.loc[key, "estado"] = "descargado"
            trk.loc[key, "tipo_informe"] = "integrated"
            trk.loc[key, "fecha_descarga"] = HOY
            if key in URLS:
                trk.loc[key, "url_fuente"] = URLS[key]
            if key in NOTAS_CON_URL:
                trk.loc[key, "notas"] = NOTAS_CON_URL[key]
            else:
                trk.loc[key, "notas"] = NOTA_GENERICA.format(lote=lote)

        n_ok += 1
        pct = 100 * i / len(files)
        print(f"  [{i}/{len(files)} {pct:.0f}%] {base} -> {dest}")

    trk = trk.reset_index()[cols]
    trk.to_csv(TRACKING, index=False)
    print(f"\nOK: {n_ok} movidos/actualizados, {n_err} omitidos.")
    print(f"tracking_descargas.csv reescrito: {TRACKING}")


if __name__ == "__main__":
    main()
