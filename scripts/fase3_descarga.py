"""
Fase 3 — Descarga automatizada de informes anuales integrados.

Estrategias por orden de prioridad:
  1. annualreports.com  (agregador público, no bloquea, buena cobertura 2022-2023)
  2. URL directa conocida por (empresa, año)  — base de datos de patrones verificados
  3. Rastreo de página IR corporativa
  4. DuckDuckGo  (opcional, --sin-ddg para omitir si está bloqueado)

Uso:
  python scripts/fase3_descarga.py                       # procesa todos los pendientes
  python scripts/fase3_descarga.py --empresa E001        # solo por ID
  python scripts/fase3_descarga.py --año 2024            # solo un ejercicio
  python scripts/fase3_descarga.py --dry-run             # sin descargar
  python scripts/fase3_descarga.py --solo-urls           # guarda URLs, no descarga
  python scripts/fase3_descarga.py --sin-ddg             # omite DuckDuckGo
"""

import argparse
import time
import urllib.parse
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
TRACKING_PATH = BASE_DIR / "data" / "external" / "tracking_descargas.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

SLEEP_IR = 1.5       # entre peticiones a webs IR
SLEEP_DDG = 12.0    # entre queries DDG (agresivo para evitar 403)
TIMEOUT = 30
MAX_PDF_MB = 300

# Circuit-breaker para DDG: si falla N veces consecutivas, se desactiva
DDG_MAX_FAILS = 3
_ddg_fails = 0        # contador de fallos DDG
_ddg_disabled = False # se activa cuando supera el límite

# ---------------------------------------------------------------------------
# Palabras que descartan un PDF como informe anual integrado
# ---------------------------------------------------------------------------
EXCLUDE_KEYWORDS = [
    "einzelabschluss", "hgb", "agm", "proxy", "prospectus", "registration",
    "form-20f", "form20f", "6-k", "8-k", "20-f", "half-year", "halfyear",
    "interim", "quarter", "q1-", "q2-", "q3-", "q4-", "quarterly",
    "notice-of", "convocation", "invitation", "pillar3", "pillar-3",
    "remuneration", "compensation", "solvency",
]

# Palabras que confirman que es el informe correcto (bonus de score)
PREFER_KEYWORDS = [
    "annual-report", "annual_report", "annualreport", "integrated-report",
    "geschaeftsbericht", "jahresbericht", "rapport-annuel", "informe-anual",
    "sustainability-report", "ar20", "ar21", "ar22", "ar23", "ar24",
    "annual-accounts", "jaarverslag", "arsredovisning", "aarsrapport",
]

# ---------------------------------------------------------------------------
# Mapa (ticker, empresa_normalizada) → slug en annualreports.com
# Verificado manualmente o por búsqueda.
# ---------------------------------------------------------------------------
AR_SLUGS: dict[tuple[str, str], str] = {
    ("STLAM", "stellantis"):   "stellantis",
    ("MBG",   "mercedes"):     "mercedes-benz",
    ("CON",   "continental"):  "continental-ag",
    ("P911",  "porsche"):      "porsche",
    ("HSBA",  "hsbc"):         "hsbc-holdings-plc",
    ("UBSG",  "ubs"):          "ubs",
    ("NOVO B","novo"):         "novo-nordisk",
    ("ADS",   "adidas"):       "adidas-ag",
    ("ULVR",  "unilever"):     "unilever",
    ("BOSS",  "hugo"):         "hugo-boss",
    ("KER",   "kering"):       "kering",
    ("REP",   "repsol"):       "repsol",
    ("ENEL",  "enel"):         "enel",
    ("ENGIE", "engie"):        "engie",
    ("OR",    "loreal"):       "loreal",
    ("VOD",   "vodafone"):     "vodafone-group",
    ("ORAN",  "orange"):       "orange",
    ("VOE",   "voestalpine"):  "voestalpine-ag",
    ("1COV",  "covestro"):     "covestro",
    ("SAF",   "safran"):       "safran",
    ("CPG",   "compass"):      "compass-group",
    ("FLTR",  "flutter"):      "flutter-entertainment",
    ("AENA",  "aena"):         "aena",
    ("AF",    "air france"):   "air-france-klm",
    ("SSE",   "sse"):          "sse",
    ("WKL",   "wolters"):      "wolters-kluwer",
    ("HMB",   "hm"):           "hm",
    ("MKS",   "marks"):        "marks-spencer",
    ("SGRO",  "segro"):        "segro",
    ("ZURN",  "zurich"):       "zurich-insurance-group",
    ("AV",    "aviva"):        "aviva",
    ("DG",    "vinci"):        "vinci",
    ("EN",    "bouygues"):     "bouygues",
    ("SY1",   "symrise"):      "symrise",
    ("YAR",   "yara"):         "yara-international",
    ("ADEN",  "adecco"):       "adecco-group",
    ("LONN",  "lonza"):        "lonza-group",
    ("QIA",   "qiagen"):       "qiagen",
    ("ALC",   "alcon"):        "alcon",
    ("BOL",   "boliden"):      "boliden",       # Boliden AB (Suecia)
    ("BOL",   "bolloré"):      "bollore",       # Bolloré (Francia) — mismo ticker, distinta empresa
    ("ACX",   "acerinox"):     "acerinox",
    ("GLB",   "glanbia"):      "glanbia",
    ("BARN",  "barry"):        "barry-callebaut",
    ("CPR",   "campari"):      "davide-campari",
    ("LDO",   "leonardo"):     "leonardo",
    ("TIT",   "telecom"):      "telecom-italia",
    ("STER",  "stora"):        "stora-enso",
}

# ---------------------------------------------------------------------------
# Mapa de URLs directas conocidas de PDFs por (ticker, año)
# Añadir entradas según se vayan verificando manualmente
# ---------------------------------------------------------------------------
DIRECT_URLS: dict[tuple[str, int], str] = {
    ("MBG", 2022): "https://group.mercedes-benz.com/documents/investors/reports/annual-report/mercedes-benz/mercedes-benz-annual-report-2022-incl-combined-management-report-mbg-ag.pdf",
    ("MBG", 2023): "https://group.mercedes-benz.com/documents/investors/reports/annual-report/mercedes-benz/mercedes-benz-annual-report-2023-incl-combined-management-report-mbg-ag.pdf",
    ("MBG", 2024): "https://group.mercedes-benz.com/documents/investors/reports/annual-report/mercedes-benz/mercedes-benz-annual-report-2024-incl-combined-management-report-mbg-ag.pdf",
    ("ADS", 2022): "https://report.adidas-group.com/2022/en/_assets/downloads/annual-report-adidas-ar22.pdf",
    ("ADS", 2023): "https://report.adidas-group.com/2023/en/_assets/downloads/annual-report-adidas-ar23.pdf",
    ("ADS", 2024): "https://report.adidas-group.com/2024/en/_assets/downloads/annual-report-adidas-ar24.pdf",
    ("STLAM", 2022): "https://www.stellantis.com/content/dam/stellantis-corporate/investors/financial-reports/Stellantis-NV-20221231-Annual-Report.pdf",
    ("STLAM", 2023): "https://www.stellantis.com/content/dam/stellantis-corporate/investors/financial-reports/Stellantis-NV-20231231-Annual-Report.pdf",
    ("STLAM", 2024): "https://www.stellantis.com/content/dam/stellantis-corporate/investors/financial-reports/Stellantis-NV-20241231-Annual-Report.pdf",
    ("NOVO B", 2022): "https://www.novonordisk.com/content/dam/nncorp/global/en/investors/irmaterial/annual_report/2023/novo-nordisk-annual-report-2022.pdf",
    ("NOVO B", 2023): "https://www.novonordisk.com/content/dam/nncorp/global/en/investors/irmaterial/annual_report/2024/novo-nordisk-annual-report-2023.pdf",
    ("NOVO B", 2024): "https://www.novonordisk.com/content/dam/nncorp/global/en/investors/irmaterial/annual_report/2025/novo-nordisk-annual-report-2024.pdf",
    ("ENEL", 2022): "https://www.enel.com/content/dam/enel-com/documenti/investors/reports-presentations/reports/annual-report/annual-reports-2022/2022-annual-report.pdf",
    ("ENEL", 2023): "https://www.enel.com/content/dam/enel-com/documenti/investors/reports-presentations/reports/annual-report/annual-reports-2023/2023-annual-report.pdf",
    ("ENEL", 2024): "https://www.enel.com/content/dam/enel-com/documenti/investors/reports-presentations/reports/annual-report/annual-reports-2024/2024-annual-report.pdf",
    ("ULVR", 2022): "https://www.unilever.com/files/92ui5egz/production/16595bc7b5e40fd6a3bba1e8ded0399cfa3f1bed.pdf",
    ("ULVR", 2023): "https://www.unilever.com/files/92ui5egz/production/9ca58cfbcb91b03ae3db849b0cc33e13df74e6d4.pdf",
    ("VOD",  2022): "https://investors.vodafone.com/sites/vodafone-ir/files/vodafone/2022/results/vodafone-annual-report-2022.pdf",
    ("VOD",  2023): "https://investors.vodafone.com/sites/vodafone-ir/files/vodafone/2023/results/vodafone-annual-report-2023.pdf",
    ("VESTAS", 2022): "https://www.vestas.com/content/dam/vestas-com/global/en/investor/reports-and-presentations/financial/2022/Vestas%20Annual%20Report%202022.pdf.coredownload.inline.pdf",
    ("VESTAS", 2023): "https://www.vestas.com/content/dam/vestas-com/global/en/investor/reports-and-presentations/financial/2023/2023-annual-report/Annual%20Report%202023.pdf.coredownload.inline.pdf",
    ("VESTAS", 2024): "https://www.vestas.com/content/dam/vestas-com/global/en/investor/reports-and-presentations/financial/2024/fy-2024/Vestas%20Annual%20Report%202024.pdf.coredownload.inline.pdf",
    ("OR",   2022): "https://www.loreal-finance.com/system/files/2023-03/LOREAL_2022_Annual_Report.pdf",
    ("OR",   2023): "https://www.loreal-finance.com/system/files/2024-03/LOREAL_2023_Annual_Report.pdf",
    ("OR",   2024): "https://www.loreal-finance.com/system/files/2025-03/LOREAL_2024_Annual_Report.pdf",
    ("REP",  2022): "https://www.repsol.com/content/dam/repsol-corporate/es/accionistas-e-inversores/informes-anuales/2022/informe-financiero-anual-consolidado-2022.pdf",
    ("REP",  2023): "https://www.repsol.com/content/dam/repsol-corporate/es/accionistas-e-inversores/informes-anuales/2023/informe-financiero-anual-consolidado.pdf",
    ("REP",  2024): "https://www.repsol.com/content/dam/repsol-corporate/en_gb/accionistas-e-inversores/informes-anuales/2024/consolidated-annual-financial-report-2024.pdf",
    # Continental
    ("CON",  2022): "https://annualreport.continental.com/2022/en/service/docs/annual-report-2022-data.pdf",
    ("CON",  2023): "https://cdn.continental.com/fileadmin/__imported/sites/corporate/_international/english/hubpages/30_20investors/30_20reports/annual_20reports/downloads/annual_report_2023.pdf",
    ("CON",  2024): "https://cdn.continental.com/fileadmin/__imported/sites/corporate/_international/english/hubpages/30_20investors/30_20reports/annual_20reports/downloads/annual-report-2024.pdf",
    # LSEG — URLs correctas del grupo
    ("LSEG", 2022): "https://www.lseg.com/content/dam/lseg/en_us/documents/investor-relations/annual-reports/lseg-annual-report-2022.pdf",
    ("LSEG", 2023): "https://www.lseg.com/content/dam/lseg/en_us/documents/investor-relations/annual-reports/lseg-annual-report-2023.pdf",
    ("LSEG", 2024): "https://www.lseg.com/content/dam/lseg/en_us/documents/investor-relations/annual-reports/lseg-annual-report-2024.pdf",
    # SEB
    ("SEB",  2022): "https://webapp.sebgroup.com/mb/mblib.nsf/alldocsbyunid/90A6F3B0C1DDAFB8C1258960004B71A2/$FILE/annual_report_2022.pdf",
    ("SEB",  2023): "https://sebgroup.com/siteassets/documents/press/cision/documents/2024/20240227-seb-publishes-annual-and-sustainability-report-2023-en-gb-1-3410354-4760766.pdf",
    ("SEB",  2024): "https://webapp.sebgroup.com/mb/mblib.nsf/alldocsbyunid/0C76B7571DFB23F5C1258C4900320544/$FILE/SEB_Annual_Report_2024_ENG.pdf",
    # Voestalpine — cierre fiscal marzo, se mapea al año más representado
    ("VOE",  2022): "https://www.voestalpine.com/group/static/sites/group/.downloads/en/publications-2022-23/2022-23-annual-report.pdf",
    ("VOE",  2023): "https://www.voestalpine.com/group/static/sites/group/.downloads/en/publications-2023-24/2023-24-annual-report.pdf",
    ("VOE",  2024): "https://www.voestalpine.com/group/static/sites/group/.downloads/en/publications-2024-25/2024-25-annual-report.pdf",
    # Covestro
    ("1COV", 2022): "https://report.covestro.com/annual-report-2022/_assets/downloads/covestro-ar22-entire.pdf",
    ("1COV", 2023): "https://report.covestro.com/annual-report-2023/_assets/downloads/covestro-ar23-entire.pdf",
    # Skanska
    ("SKA B", 2022): "https://group.skanska.com/493785/siteassets/investors/reports-publications/annual-reports/2022/annual-and-sustainability-report-2022.pdf",
    ("SKA B", 2023): "https://group.skanska.com/493370/siteassets/investors/reports-publications/annual-reports/2023/annual-and-sustainability-report-2023.pdf",
    ("SKA B", 2024): "https://group.skanska.com/49490b/siteassets/investors/reports-publications/annual-reports/2024/annual-and-sustainability-report-2024.pdf",
    # UPM-Kymmene
    ("UPM",  2022): "https://www.upm.com/siteassets/asset/investors/2022/upm-annual-report-2022.pdf",
    ("UPM",  2023): "https://www.upm.com/siteassets/investors/reports-and-presentations/2023/upm-annual-report-2023.pdf",
    ("UPM",  2024): "https://www.upm.com/siteassets/asset/investors/2024/upm-annual-report-2024.pdf",
    # Symrise
    ("SY1",  2022): "https://symrise.com/corporatereport/2022/downloads/SYM_financialreport_2022_EN.pdf",
    ("SY1",  2023): "https://symrise.com/corporatereport/2023/downloads/SYM_corporatereport_2023_EN.pdf",
    ("SY1",  2024): "https://symrise.com/corporatereport/2024/home/Symrise_Unternehmensbericht_24_EN_interaktiv_geschuetzt.pdf",
    # Acerinox — Informes anuales integrados por año
    ("ACX",  2022): "https://www.acerinox.com/export/sites/acerinox/es/accionistas-e-inversores/informacion-economica-financiera/informe-anual-integrado/.galleries/Informacion-Anual/2022-Consolidated-Annual-Accounts-and-Integrated-Annual-Report.pdf",
    ("ACX",  2023): "https://www.acerinox.com/export/sites/acerinox/es/accionistas-e-inversores/informacion-economica-financiera/informe-anual-integrado/.galleries/Informacion-Anual/2023-Acerinox-Group-Integrated-Annual-Report.pdf",
    ("ACX",  2024): "https://www.acerinox.com/export/sites/acerinox/es/accionistas-e-inversores/informacion-economica-financiera/informe-anual-integrado/.galleries/Informacion-Anual/2024-Acerinox-Group-Consolidated-Management-Report.pdf",
    # CaixaBank — informes anuales consolidados con URL específica por año
    ("CABK", 2022): "https://www.caixabank.com/deployedfiles/caixabank_com/Estaticos/PDFs/Accionistasinversores/Informacion_economico_financiera/CCAA-GRUP-CAIXABANK-ING.pdf",
    ("CABK", 2023): "https://www.caixabank.com/deployedfiles/caixabank_com/Estaticos/PDFs/Accionistasinversores/Informacion_economico_financiera/CAIXABANK_2023_CAC_ING.pdf",
    ("CABK", 2024): "https://www.caixabank.com/deployedfiles/caixabank_com/Estaticos/PDFs/Accionistasinversores/Informacion_economico_financiera/Informe_Anual_Consolidado_2024_ENG.pdf",
    # HSBC Holdings
    ("HSBA", 2022): "https://www.hsbc.com/-/files/hsbc/investors/hsbc-results/2022/annual/pdfs/hsbc-holdings-plc/230221-annual-report-and-accounts-2022.pdf",
    ("HSBA", 2023): "https://www.hsbc.com/-/files/hsbc/investors/hsbc-results/2023/annual/pdfs/hsbc-holdings-plc/240226-annual-report-and-accounts-2023.pdf",
    ("HSBA", 2024): "https://www.hsbc.com/-/files/hsbc/investors/hsbc-results/2024/annual/pdfs/hsbc-holdings-plc/250219-annual-report-and-accounts-2024.pdf",
    # Aviva
    ("AV",   2022): "https://static.aviva.io/content/dam/aviva-corporate/documents/investors/pdfs/reports/2022/aviva-plc-annual-report-and-accounts-2022.pdf",
    ("AV",   2023): "https://static.aviva.io/content/dam/aviva-corporate/documents/investors/pdfs/reports/2023/aviva-plc-annual-report-and-accounts-2023.pdf",
    ("AV",   2024): "https://static.aviva.io/content/dam/aviva-corporate/documents/investors/pdfs/reports/2024/aviva-plc-annual-report-and-accounts-2024.pdf",
    # SSE plc
    ("SSE",  2022): "https://www.sse.com/media/y5ohomz3/38530-sse-ar2022-web.pdf",
    ("SSE",  2023): "https://www.sse.com/media/ucnjhbcv/sse-full-annual-report-revised-web.pdf",
    ("SSE",  2024): "https://www.sse.com/media/0aibgke4/sse_ar24_interactive.pdf",
    # Compass Group
    ("CPG",  2022): "https://www.compass-group.com/content/dam/compass-group/corporate/oar-2022/2022-annual-report-compass-group.pdf",
    ("CPG",  2023): "https://www.compass-group.com/content/dam/compass-group/corporate/oar-2023/annual-report-2023.pdf",
    ("CPG",  2024): "https://www.compass-group.com/content/dam/compass-group/corporate/oar-2024/annual-report-2024.pdf",
    # Zurich Insurance Group
    ("ZURN", 2023): "https://edge.sitecorecloud.io/zurichinsur6934-zwpcorp-prod-ae5e/media/project/zurich/dotcom/investor-relations/docs/financial-reports/2023/annual-report-2023-en.pdf",
    ("ZURN", 2024): "https://edge.sitecorecloud.io/zurichinsur6934-zwpcorp-prod-ae5e/media/project/zurich/dotcom/investor-relations/docs/financial-reports/2024/annual-report-2024-en.pdf",
    # Adecco Group
    ("ADEN", 2022): "https://www.adeccogroup.com/-/media/project/adecco-group/adeccogroup/pdf-links/investors/adecco-group-annual-report-2022.pdf",
    ("ADEN", 2023): "https://www.adeccogroup.com/-/media/project/Adecco%20Group/adeccogroup/pdf-files/2024-march/the-adecco-group-annual-report-2023.pdf",
    ("ADEN", 2024): "https://www.adeccogroup.com/-/media/project/adecco-group/adeccogroup/pdf-files/2025-march/the-adecco-group-annual-report-2024.pdf",
    # Engie
    ("ENGIE",2022): "https://www.engie.com/sites/default/files/assets/documents/2023-02/ENGIE_2022%20Management%20report%20and%20annual%20consolidated%20financial%20statements.pdf",
    ("ENGIE",2023): "https://www.engie.com/sites/default/files/assets/documents/2024-02/2023%20Management%20report%20and%20Annual%20consolidated%20financial%20statements%202.pdf",
    ("ENGIE",2024): "https://www.engie.com/sites/default/files/assets/documents/2025-02/2024%20Management%20report%20and%20Annual%20consolidated%20financial%20statements.pdf",
    # Safran
    ("SAF",  2022): "https://www.safran-group.com/sites/default/files/2023-04/SAFRAN_RI-2022_UK_MEL.pdf",
    ("SAF",  2023): "https://www.safran-group.com/sites/default/files/2024-03/2023-safran-integrated-report.pdf",
    # Marks & Spencer (fiscal year ending March/April)
    ("MKS",  2022): "https://corporate.marksandspencer.com/sites/marksandspencer/files/Annual%20reports/m-and-s_ar22_full-ar.pdf",
    ("MKS",  2023): "https://corporate.marksandspencer.com/sites/marksandspencer/files/2023-06/M-and-S-2023-Annual-Report.pdf",
    ("MKS",  2024): "https://corporate.marksandspencer.com/sites/marksandspencer/files/2024-06/M-and-S-2024-Annual-Report.pdf",
    # Orange S.A.
    ("ORAN", 2022): "https://rai.orange.com/wp-content/uploads/sites/54/2024/02/orange_integratedannualreport_2022_en.pdf",
    # Aker BP
    ("AKERBP",2022): "https://akerbp.com/wp-content/uploads/2023/03/aker-bp-annual-report-2022.pdf",
    ("AKERBP",2023): "https://akerbp.com/wp-content/uploads/2024/03/aker-bp-annual-report-2023.pdf",
    ("AKERBP",2024): "https://akerbp.com/wp-content/uploads/2025/04/annual-report-2024.pdf",
    # Stora Enso
    ("STER", 2022): "https://www.storaenso.com/-/media/documents/download-center/documents/annual-reports/2022/storaenso_annual_report_2022.pdf",
    ("STER", 2023): "https://www.storaenso.com/-/media/documents/download-center/documents/annual-reports/2023/storaenso_annual_report_2023.pdf",
    ("STER", 2024): "https://www.storaenso.com/-/media/documents/download-center/documents/annual-reports/2024/storaenso_annual_report_2024.pdf",
    # H&M Group
    ("HMB",  2022): "https://hmgroup.com/wp-content/uploads/2023/03/HM-Group-Annual-and-Sustainability-Report-2022.pdf",
    ("HMB",  2023): "https://hmgroup.com/wp-content/uploads/2024/03/HM-Group-Annual-and-Sustainability-Report-2023.pdf",
    ("HMB",  2024): "https://hmgroup.com/wp-content/uploads/2025/03/HM-Group-Annual-and-sustainability-report-2024.pdf",
    # Neste
    ("NSN",  2022): "https://www.neste.com/files/pdf/7eb862934530a889c296d0317593e68b-Neste_Annual_Report_2022.pdf",
    ("NSN",  2023): "https://www.neste.com/files/pdf/5pSrq2XvklFNL6GU1cPFNY-Neste_Annual_Report_2023.pdf",
    ("NSN",  2024): "https://www.neste.com/files/pdf/3kFaGuHcQk8hRDLS6tlvqF-Neste_Annual_Report_2024.pdf",
    # Yara International
    ("YAR",  2022): "https://www.yara.com/siteassets/investors/057-reports-and-presentations/annual-reports/2022/yara-integrated-report-2022.pdf",
    ("YAR",  2023): "https://www.yara.com/siteassets/investors/057-reports-and-presentations/annual-reports/2023/yara-integrated-report-2023.pdf",
    ("YAR",  2024): "https://www.yara.com/siteassets/investors/057-reports-and-presentations/annual-reports/2024/yara-integrated-report-2024.pdf",
    # UBS Group
    ("UBSG", 2022): "https://www.ubs.com/content/dam/assets/cc/investor-relations/annual-report/2022/files/annual-report-ubs-group-2022.pdf",
    ("UBSG", 2023): "https://www.ubs.com/content/dam/assets/cc/investor-relations/annual-report/2023/files/annual-report-ubs-group-2023.pdf",
    ("UBSG", 2024): "https://www.ubs.com/content/dam/assets/cc/investor-relations/annual-report/2024/annual-report-ubs-group-2024.pdf",
    # Vinci — Document d'Enregistrement Universel (URD includes annual report)
    ("DG",   2022): "https://www.vinci.com/publi/vinci/vinci-document-enregistrement-universel-2022.pdf",
    ("DG",   2023): "https://www.vinci.com/publi/vinci/vinci-document-enregistrement-universel-2023.pdf",
    ("DG",   2024): "https://www.vinci.com/publi/vinci/vinci-document-enregistrement-universel-2024.pdf",
    # Pernod Ricard — fiscal year ends June 30; year 2022=FY21/22, 2023=FY22/23, 2024=FY23/24
    ("PERP", 2022): "https://www.pernod-ricard.com/sites/default/files/inline-files/RAPR021_GB_WEB_2.pdf",
    ("PERP", 2023): "https://www.pernod-ricard.com/sites/default/files/2023-11/Pernod_Ricard_Rapport_Annuel_202223.pdf",
    ("PERP", 2024): "https://www.pernod-ricard.com/sites/default/files/2024-11/Pernod_AR24_ENGLISH.pdf",
    # Hugo Boss
    ("BOSS", 2022): "https://annualreport.hugoboss.com/2022/_assets/downloads/entire-hb-ar22.pdf",
    ("BOSS", 2023): "https://annualreport.hugoboss.com/2023/_assets/downloads/entire-hb-ar23.pdf",
    ("BOSS", 2024): "https://annualreport.hugoboss.com/2024/_assets/downloads/entire-hb-ar24.pdf",
    # AXA — ticker "CS" in tracking; Universal Registration Document
    ("CS",   2022): "https://www-axa-com.cdn.prismic.io/www-axa-com/aN0PG55xUNkB1WiL_axa_urd2022_accessibleb_va.pdf",
    ("CS",   2023): "https://www-axa-com.cdn.prismic.io/www-axa-com/aNzv0Z5xUNkB1VHO_axa_urd2023_accessibleb_va.pdf",
    ("CS",   2024): "https://www-axa-com.cdn.prismic.io/www-axa-com/aNzv1p5xUNkB1VHR_axa_urd2024_accessible_va.pdf",
    # Kering — Document d'Enregistrement Universel (via bnains.org AMF archive)
    ("KER",  2022): "https://www.bnains.org/archives/communiques/PPR/20230322_Document_d_enregistrement_universel_2022_kering.pdf",
    ("KER",  2023): "https://www.bnains.org/archives/communiques/PPR/20240319_Document_d_enregistrement_universel_2023_kering.pdf",
    ("KER",  2024): "https://www.bnains.org/archives/communiques/PPR/20250318_Document_d_enregistrement_universel_2024_kering.pdf",
    # Wolters Kluwer
    ("WKL",  2022): "https://assets.contenthub.wolterskluwer.com/api/public/content/7ecf79d725094df588fddb8b58370a0c?v=0723f0d6",
    ("WKL",  2023): "https://assets.contenthub.wolterskluwer.com/api/public/content/2190891-wolters-kluwer-2023-annual-report-3ff32c52c4?v=f6d1aeee",
    ("WKL",  2024): "https://assets.contenthub.wolterskluwer.com/api/public/content/2630611-wolters-kluwer-2024-annual-report-cd216d4be7?v=7a259453",
    # Enagás
    ("ENG",  2022): "https://www.enagas.es/content/dam/enagas/en/files/enagas-communication-room/publications/informe-anual/Annual_Report_2022_Enagas.pdf",
    ("ENG",  2023): "https://www.enagas.es/content/dam/enagas/en/files/enagas-communication-room/publications/informe-anual/Annual-Report-2023.pdf",
    ("ENG",  2024): "https://www.enagas.es/content/dam/enagas/en/files/enagas-communication-room/publications/informe-anual/Annual-Report-2024-Enagas.pdf",
    # Bouygues — URD via bnains.org (direct links 403)
    ("EN",   2022): "https://www.bnains.org/archives/communiques/Bouygues/20230322_Document_d_enregistrement_universel_2022_Bouygues.pdf",
    ("EN",   2023): "https://www.bnains.org/archives/communiques/Bouygues/20240322_Document_d_enregistrement_universel_2023_Bouygues.pdf",
    ("EN",   2024): "https://www.bnains.org/archives/communiques/Bouygues/20250325_Document_d_enregistrement_universel_2024_Bouygues.pdf",
    # Eiffage — URD (Universal Registration Document)
    ("EFGI", 2023): "https://www.eiffage.com/files/live/sites/eiffagev2/files/Finance/Rapport%20Annuel/Eiffage_URD_2023_EN.pdf",
    ("EFGI", 2024): "https://www.eiffage.com/files/live/sites/eiffagev2/files/Finance/Rapport%20Annuel/eif-2024_urd_en_mel.pdf",
    # Air France-KLM — URD
    ("AF",   2022): "https://www.airfranceklm.com/sites/default/files/2023-04/AFK_URD_2022_VA_24-04-23.pdf",
    ("AF",   2023): "https://www.airfranceklm.com/sites/default/files/2024-04/af_urd_2023_uk_vmel2_260424.pdf",
    # Porsche AG (P911) — Annual and Sustainability Report
    ("P911", 2023): "https://newsroom.porsche.com/dam/jcr:838a302c-ddc1-46bc-b525-c6c6b18c3800/Annual%20and%20Sustainability%20Report%202023%20Porsche%20AG%20-%20consolidated%20financial%20statements%20IFRS.pdf",
    ("P911", 2024): "https://newsroom.porsche.com/files/Annual_and_Sustainability_Report_2024_Porsche_AG_(Consolidated_Financial_Statements_IFRS).pdf",
    # Telecom Italia (TIT) — via gruppotim.it
    ("TIT",  2022): "https://www.gruppotim.it/content/dam/gt/investitori/doc---avvisi/anno-2023/eng/Annual-report-2022.pdf",
    ("TIT",  2023): "https://www.gruppotim.it/content/dam/gt/investitori/doc---avvisi/anno-2024/eng/Annual-report-2023.pdf",
    ("TIT",  2024): "https://www.gruppotim.it/content/dam/gt/investitori/doc---report-finanziari/2024/Annual%20report%202024.pdf",
    # Brenntag
    ("BNR",  2022): "https://brenntagprod-media.e-spirit.cloud/06432017-be1f-41ce-8d1d-564e2a66d213/documents/corporate/investor-relations/2022/annual-report-2022/brenntagannualreport2022en.pdf",
    ("BNR",  2023): "https://brenntagprod-media.e-spirit.cloud/06432017-be1f-41ce-8d1d-564e2a66d213/documents/corporate/investor-relations/2023/annual-report-2023/brenntag_annualreport-2023_en.pdf",
    ("BNR",  2024): "https://brenntagprod-media.e-spirit.cloud/06432017-be1f-41ce-8d1d-564e2a66d213/documents/corporate/investor-relations/2024/annual-report-2024/brenntag_annual-report-2024_en.pdf",
    # Evonik — Financial Report (integrated content; 2024 renamed to Financial and Sustainability Report)
    ("EVK",  2022): "https://www.evonik.com/content/dam/evonik/documents/Financial%20Report%202022.pdf.coredownload.pdf",
    ("EVK",  2023): "https://www.evonik.com/content/dam/evonik/documents/Evonik%20Financial%20Report%202023_EN.pdf.coredownload.pdf",
    ("EVK",  2024): "https://www.evonik.com/content/dam/evonik/documents/Evonik_Financial_and_Sustainability_Report_2024.pdf.coredownload.pdf",
    # Campari Group (CPR)
    ("CPR",  2022): "https://www.camparigroup.com/sites/default/files/downloads/01.1%20Campari%20Group_Annual%20Report%20for%20the%20year%20ended%2031%20December%202022.pdf",
    ("CPR",  2023): "https://www.camparigroup.com/sites/default/files/downloads/01.1%20Campari%20Group_Annual%20Report%20for%20the%20year%20ended%2031%20December%202023.pdf",
    ("CPR",  2024): "https://www.camparigroup.com/sites/default/files/downloads/01.1%20Campari%20Group_Annual%20Report%20for%20the%20year%20ended%2031%20December%202024.pdf",
    # Leonardo SpA (LDO)
    ("LDO",  2022): "https://www.leonardo.com/documents/15646808/0/Integrated+Annual+Report+2022+per+sito+(1).pdf",
    ("LDO",  2023): "https://www.leonardo.com/documents/15646808/25622604/Integrated+Annual+Report+2023_12032024_per+sito.pdf",
    ("LDO",  2024): "https://www.leonardo.com/documents/15646808/28608810/2024+Integrated+Annual+Report.pdf",
    # Richemont (CFR) — fiscal year ends March 31; FY22→tracking 2022, FY23→2023, FY24→2024
    ("CFR",  2022): "https://www.richemont.com/media/pead1wrd/richemont-fy22-annual-report-en-2.pdf",
    ("CFR",  2023): "https://www.richemont.com/media/vjjclruw/richemont-fy23-annual-report-en.pdf",
    ("CFR",  2024): "https://www.richemont.com/media/ke2kroab/richemont-fy24-annual-report-en.pdf",
    # Aena (AENA) — sustainability/non-financial information statement (integrated format)
    ("AENA", 2022): "https://www.aena.es/sites/Satellite?blobcol=urldata&blobkey=id&blobtable=MungoBlobs&blobwhere=1576862275717&ssbinary=true",
    ("AENA", 2023): "https://www.aena.es/sites/Satellite?blobcol=urldata&blobkey=id&blobtable=MungoBlobs&blobwhere=1576868584275&ssbinary=true",
    ("AENA", 2024): "https://www.aena.es/sites/Satellite?blobcol=urldata&blobkey=id&blobtable=MungoBlobs&blobwhere=1576870867684&ssbinary=true",
    # SGS SA — Integrated Annual Report
    ("SGSN", 2022): "https://www.sgs.com/-/media/sgscorp/documents/corporate/reports-and-presentations/2020s/2022/sgs-2022-integrated-report-en.cdn.en.pdf",
    ("SGSN", 2023): "https://www.sgs.com/-/media/sgscorp/documents/corporate/reports-and-presentations/2020s/2023/sgs-2023-integrated-report-en.cdn.en-FR.pdf",
    ("SGSN", 2024): "https://www.sgs.com/-/media/sgscorp/documents/corporate/reports-and-presentations/2020s/2025/sgs-2024-integrated-report-en.cdn.en-RO.pdf",
    # Exor NV (EXO)
    ("EXO",  2022): "https://www.exor.com/sites/default/files/2023/document-documents/EXOR_Annual%20Report%202022.pdf",
    ("EXO",  2023): "https://exor.com/sites/default/files/2024/document-documents/EXOR%202023%20Annual%20Report.pdf",
    ("EXO",  2024): "https://www.exor.com/system/files/2025/document-documents/EXOR%202024%20Annual%20Report.pdf",
    # 3i Group (III)
    ("III",  2022): "https://www.3i.com/media/3gtlu3yy/3i_group_ar2022_final_a.pdf",
    ("III",  2023): "https://www.3i.com/media/orvbwrof/3i_group_ar23.pdf",
    ("III",  2024): "https://www.3i.com/media/nnrkjwke/annual_report_and_accounts_2024.pdf",
    # Talanx (TLX) — 2022 hosted on Warta (Talanx subsidiary, talanx.com returns 404)
    ("TLX",  2022): "https://www.warta.pl/documents/istotne_dokumenty/2022-Talanx-Group-annual-report-english.pdf",
    ("TLX",  2023): "https://www.talanx.com/media/Files/investor-relations/pdf/ergebnisse/2023/FY/2023_tx_konzern_en.pdf",
    ("TLX",  2024): "https://www.talanx.com/media/Files/investor-relations/pdf/ergebnisse/2024/Q4/2024_talanx_konzern_en_pw.pdf",
    # Covestro (1COV) — 2024 annual report
    ("1COV", 2024): "https://annualreport.covestro.com/ecomaXL/files/Covestro_2024_GB_EN.pdf",
    # Safran (SAF) — 2024 Document d'Enregistrement Universel
    ("SAF",  2024): "https://www.safran-group.com/sites/default/files/2025-03/Document%20d%27enregistrement%20universel%202024%20%28PDF%29.pdf",
    # Zurich Insurance (ZURN) — 2022 via Wayback Machine if_ (raw PDF, no toolbar injection)
    ("ZURN", 2022): "https://web.archive.org/web/20230410154545if_/https://www.zurich.com/-/media/project/zurich/dotcom/investor-relations/docs/financial-reports/2022/annual-report-2022-en.pdf",
    # Melexis (MELE) — Belgian semiconductor
    ("MELE", 2022): "https://media.melexis.com/-/media/files/documents/investor-relations/reports/annual-reports/en/2022-annual-report-melexis-en.pdf",
    ("MELE", 2023): "https://media.melexis.com/-/media/files/documents/investor-relations/reports/annual-reports/en/2023-annual-report-melexis-en.pdf",
    ("MELE", 2024): "https://media.melexis.com/-/media/files/documents/investor-relations/reports/annual-reports/en/2024-annual-report-melexis-en.pdf",
    # Ontex (ONT) — Belgian hygiene products
    ("ONT",  2022): "https://ontex.com/wp-content/uploads/2023/04/Ontex-integrated-annual-report-2022-interactive.pdf",
    ("ONT",  2023): "https://ontex.com/wp-content/uploads/2024/04/Ontex-integrated-annual-report-2023-1-1.pdf",
    ("ONT",  2024): "https://ontex.com/wp-content/uploads/2025/03/24AR_AnnualReport_EN_Final.pdf",
    # Colruyt Group (COLR) — April-March FY; only 2023 (FY2022/23) found via Euronext
    ("COLR", 2023): "https://live.euronext.com/sites/default/files/esg_document_files/2023-11/001881_Annual%20report%20Colruyt%20Group%202022-2023_0_2023-11-07_10:34.pdf",
    # Glanbia (GLB) — Irish nutrition/dairy
    ("GLB",  2022): "https://www.glanbia.com/sites/glanbia-plc/files/glanbia/glanbia-annual-report-2022.pdf",
    ("GLB",  2023): "https://www.glanbia.com/sites/glanbia-plc/files/glanbia/investors/annual-report/2024/annual-report-2023.pdf",
    ("GLB",  2024): "https://www.glanbia.com/sites/glanbia-plc/files/glanbia/investors/annual-report/2025/annual-report-2024.pdf",
    # Flutter Entertainment (FLTR) — Irish gambling
    ("FLTR", 2022): "https://flutter.com/media/ygebk1qa/flutter-entertainment-plc-annual-report-accounts-2022.pdf",
    ("FLTR", 2023): "https://flutter.com/media/3s0peofa/flutter-entertainment-plc-annual-report-and-accounts-2023-10-k_updated.pdf",
    ("FLTR", 2024): "https://flutter.com/media/s44lcmmb/flutter-uk-wrapper-10k_fnl.pdf",
    # Allfunds Group (ALLFG) — fund distribution; 2023 not published
    ("ALLFG",2022): "https://app.allfunds.com/docs/cms/Allfunds_2022_Annual_Report_2d8223ebf7.pdf",
    ("ALLFG",2024): "https://app.allfunds.com/docs/cms/Allfunds_Annual_Report_2024_97e1d5de05.pdf",
    # Delivery Hero (DHER) — German food delivery; 2022 not found
    ("DHER", 2023): "https://www.lobbyregister.bundestag.de/media/9c/ab/313888/Delivery-Hero-Annual-Report-2023.pdf",
    ("DHER", 2024): "https://ir.deliveryhero.com/media/document/c38c7d53-cd6e-44de-8b1f-3559d5c43e6b/assets/DE000A2E4K43-JA-2024-EQ-E-00.pdf",
    # Freenet (FNTN) — German telecom
    ("FNTN", 2022): "https://www.freenet.ag/binaries/_ts_1691410969603/content/assets/freenetgroup/pdf/ir-englisch/finanzberichte/2022/2022_ar_web_freenet.pdf",
    ("FNTN", 2023): "https://www.freenet.ag/binaries/_ts_1713541479442/content/assets/freenetgroup/pdf/ir-englisch/finanzberichte/2023/freenet-gb-2023-e-web.pdf",
    ("FNTN", 2024): "https://www.freenet.ag/binaries/_ts_1743061697640/content/assets/freenetgroup/pdf/ir-englisch/finanzberichte/2024/freenet-gb-2024-en-web.pdf",
    # Nemetschek (NEM) — German construction software; 2022 German-language only
    ("NEM",  2022): "https://www.nemetschek.com/sites/default/files/documents/NGroup%20Gesch%C3%A4ftsbericht%202022.pdf",
    ("NEM",  2023): "https://www.nemetschek.com/sites/default/files/documents/NEM_AnnualReport2023_en.pdf",
    ("NEM",  2024): "https://www.launch2020.nemetschek.com/sites/default/files/documents/NEM_AR2024_EN.pdf",
    # Balfour Beatty (BBY) — UK construction
    ("BBY",  2022): "https://www.balfourbeatty.com/media/0yjl3b0l/balfour-beatty-plc-annual-report-and-accounts-2022.pdf",
    ("BBY",  2023): "https://www.balfourbeatty.com/media/eo0p0h1j/balfour-beatty-annual-report-and-accounts-2023.pdf",
    ("BBY",  2024): "https://www.balfourbeatty.com/media/yx0pn423/balfour-beatty-annual-report-and-accounts-2024.pdf",
    # Travis Perkins (TPK) — UK building materials
    ("TPK",  2022): "https://www.travisperkinsplc.co.uk/media/dqbnofvc/annual-report-and-accounts-2022.pdf",
    ("TPK",  2023): "https://www.travisperkinsplc.co.uk/media/4mznqoer/travis-perkins-annual-report-2023.pdf",
    ("TPK",  2024): "https://www.travisperkinsplc.co.uk/media/uc0oz433/travis-perkins-plc-2024-annual-report.pdf",
    # ConvaTec (CTEC) — UK medical devices
    ("CTEC", 2022): "https://www.convatecgroup.com/globalassets/global-assets/pdf/convatec_ar2022__interactive.pdf",
    ("CTEC", 2023): "https://www.convatecgroup.com/globalassets/global-assets/pdf/convatec-ar-2023_interactive.pdf",
    ("CTEC", 2024): "https://www.convatecgroup.com/siteassets/convatec-ara-2024.pdf",
    # JD Sports Fashion (JD) — UK retail; FY ends late Jan/Feb
    ("JD",   2022): "https://s204.q4cdn.com/980191062/files/doc_financials/2022/ar/final-annual-report-2022.pdf",
    ("JD",   2023): "https://s204.q4cdn.com/980191062/files/doc_financials/2023/ar/jd-annual-report-and-accounts-2023.pdf",
    ("JD",   2024): "https://s204.q4cdn.com/980191062/files/doc_financials/2024/ar/jd-sports-fashion-annual-report-and-accounts-2024.pdf",
    # Segro (SGRO) — UK logistics REIT
    ("SGRO", 2022): "https://www.segro.com/media/enlje3wp/annual-report-2022-final.pdf",
    ("SGRO", 2023): "https://www.segro.com/media/0r4biubx/segro_ar2023.pdf",
    ("SGRO", 2024): "https://www.segro.com/media/1h4c1331/segro_ar24_interactive.pdf",
    # Sage Group (SGE) — UK software; FY ends 30 Sept
    ("SGE",  2022): "https://www.sage.com/en-gb/-/media/files/investors/documents/pdf/annual%20report/sage-annual-report-2022.pdf",
    ("SGE",  2023): "https://www.sage.com/en-gb/-/media/files/investors/documents/pdf/annual%20report/sage-annual-report-2023.pdf",
    ("SGE",  2024): "https://www.sage.com/en-gb/-/media/files/investors/documents/pdf/annual%20report/sage-annual-report-2024.pdf",
    # TUI Group (TUI) — travel; FY ends 30 Sept; EQS filename uses prior calendar year
    ("TUI",  2022): "https://www.eqs-news.com/media/document/e4da4bd6-7ca8-48eb-9d21-1600e6d2d57a/assets/DE000TUAG000-JA-2021-EQ-E-00.pdf",
    ("TUI",  2023): "https://www.eqs-news.com/media/document/5cc7fb56-0777-4d73-95a6-0e4b4aad2dec/assets/DE000TUAG505-JA-2022-EQ-E-00.pdf",
    ("TUI",  2024): "https://www.eqs-news.com/media/document/526d0a0b-e2b8-4fce-9e76-6e21e9f070c5/assets/DE000TUAG505-JA-2023-EQ-E-00.pdf",
    # Valeo (FR) — French automotive supplier; URD via bnains.org/valeo.com
    ("FR",   2022): "https://www.bnains.org/archives/communiques/Valeo/20230330_Document_d_enregistrement_universel_2022_Valeo.pdf",
    ("FR",   2023): "https://www.bnains.org/archives/communiques/Valeo/20240329_Document_d_enregistrement_universel_2023_Valeo.pdf",
    ("FR",   2024): "https://www.valeo.com/wp-content/uploads/2025/04/Valeo_2024-Universal-registration-document.pdf",
    # Gecina (GFC) — French office REIT; URD
    ("GFC",  2022): "https://www.gecina.fr/sites/default/files/2023-02/gecina_-_document_denregistrement_universel_2022.pdf",
    ("GFC",  2023): "https://www.gecina.fr/sites/default/files/2024-02/gecina_document_d_enregistrement_universel_2023.pdf",
    ("GFC",  2024): "https://www.gecina.fr/sites/default/files/2025-02/gecina_-_document_d_enregistrement_universel_2024.pdf",
    # Wendel (WEND) — French holding; URD in French
    ("WEND", 2022): "https://www.wendelgroup.com/wp-content/uploads/2023/04/WENDEL_URD2022_FR.pdf",
    ("WEND", 2023): "https://www.wendelgroup.com/wp-content/uploads/2024/03/wen-2023-urd-fr-v-mel-240327.pdf",
    ("WEND", 2024): "https://www.wendelgroup.com/wp-content/uploads/2025/03/wen-2024-urd-fr-28032025.pdf",
    # Acciona Energía (ANE) — Spanish renewables
    ("ANE",  2022): "https://report2022.acciona-energia.com/pdfs/acciona-energia-2022-integrated-report.pdf",
    ("ANE",  2023): "https://report2023.acciona-energia.com/pdfs/ACCIONAEnergia-Sustainability-report_2023.pdf",
    ("ANE",  2024): "https://www.acciona.com/content/dam/acciona-global/documentos/juntas-generales/2025/en/intregrated-report-2024-acciona.pdf",
    # Merlin Properties (MRL) — Spanish REIT
    ("MRL",  2022): "https://ir.merlinproperties.com/wp-content/uploads/2023/04/Annual-Report-2022.pdf",
    ("MRL",  2023): "https://ir.merlinproperties.com/wp-content/uploads/2024/05/Annual-Report-2023-3-1.pdf",
    ("MRL",  2024): "https://ir.merlinproperties.com/wp-content/uploads/2025/05/Annual-Report-2024_ACC.pdf",
    # Dia Group (DIA) — Spanish discount retail; 2024 not found
    ("DIA",  2022): "https://diacorporate.com/wp-content/uploads/2023/04/Consolidated-Annual-Accounts-and-directors-report-DIA-2022.pdf",
    ("DIA",  2023): "https://diacorporate.com/wp-content/uploads/2024/02/Memoria-Grupo-DIA-e-IG-consolidado-V.ingles-con-IA-xs.pdf",
    # Orkla ASA (ORK) — Norwegian FMCG
    ("ORK",  2022): "https://www.orkla.com/files/Main/19690/3738803/orkla-annual-report-2022.pdf",
    ("ORK",  2023): "https://www.orkla.com/files/Public/19690/3951825/orkla-annual-report-2023.pdf",
    ("ORK",  2024): "https://www.orkla.com/files/mfn/7f0f329a-2944-4496-aec4-b6068d0c6b5c/orkla-annual-report-2024.pdf",
    # TGS ASA (TGS) — Norwegian geoscience data
    ("TGS",  2022): "https://www.tgs.com/hubfs/2022_TGS_Annual%20Report.pdf",
    ("TGS",  2023): "https://www.tgs.com/hubfs/Financial%20Reports/Annual%20Reports/2023%20Annual%20Report/2023%20TGS%20Annual%20Report%20and%20Sustainability%20Report_final.pdf",
    ("TGS",  2024): "https://www.tgs.com/hubfs/Financial%20Reports/Annual%20Reports/2024%20Annual%20Report/TGS%202024%20Annual%20Report.pdf",
    # Tryg (TRYG) — Danish insurance
    ("TRYG", 2022): "https://tryg.com/sites/tryg.com/files/2023-08/Tryg%20AR%202022.pdf",
    ("TRYG", 2023): "https://tryg.com/sites/tryg.com/files/2024-01/Tryg%20Annual%20Report%202023_4.pdf",
    ("TRYG", 2024): "https://tryg.com/sites/tryg.com/files/2025-01/Annual%20Report%202024%20-%20TRYG%20A_S.pdf",
    # Castellum (CAST) — Swedish real estate
    ("CAST", 2022): "https://storage.mfn.se/69d1c438-3577-48e0-a826-b27aa0c51960/castellum-annual-report-and-sustainability-report-2022-print.pdf",
    ("CAST", 2023): "https://storage.mfn.se/f05cdb7c-567f-481b-bc8e-a11da446b807/castellum-annual-report-2023.pdf",
    ("CAST", 2024): "https://storage.mfn.se/e8a0a9e3-9238-42a9-a59a-629f5e32813e/castellum-annual-report-2024.pdf",
    # Wihlborgs Fastigheter (WIHL) — Swedish commercial real estate
    ("WIHL", 2022): "https://mb.cision.com/Main/890/3743603/1954554.pdf",
    ("WIHL", 2023): "https://mb.cision.com/Main/890/3951531/2698409.pdf",
    ("WIHL", 2024): "https://www.wihlborgs.se/globalassets/investor-relations/digital-ar-2024/wihlborgs-annual-and-sustainability-report-2024_ny.pdf",
    # Viaplay Group (VPLAY B) — Swedish streaming
    ("VPLAY B", 2022): "https://www.viaplaygroup.com/sites/viaplay-corp/files/pr/202304044882-1.pdf",
    ("VPLAY B", 2023): "https://www.viaplaygroup.com/sites/viaplay-corp/files/viaplay_group_ab_publ_annual_sustainability_report_2023.pdf",
    ("VPLAY B", 2024): "https://www.viaplaygroup.com/sites/viaplay-corp/files/2025-03/Viaplay_Group_Annual_and_Sustainability_report_2024.pdf",
    # Alcon (ALC) — Swiss eye-care; annual report (not 20-F)
    ("ALC",  2022): "https://s1.q4cdn.com/963204942/files/doc_financials/2022/ar/Alcon-2022-Annual-Report.pdf",
    ("ALC",  2023): "https://s1.q4cdn.com/963204942/files/doc_earnings/2023/q4/supplemental-info/2023-Annual-Report.pdf",
    ("ALC",  2024): "https://s1.q4cdn.com/963204942/files/doc_earnings/2024/q4/supplemental-info/2024-Annual-Report.pdf",
    # Raiffeisen Bank International (RBI) — Austrian bank
    ("RBI",  2022): "https://www.rbinternational.com/content/dam/rbi/ho/investors/results-reports/annual-reports/rbi/2022%20Annual%20Report%20RBI.pdf.coredownload.pdf",
    ("RBI",  2023): "https://www.rbinternational.com/content/dam/rbi/ho/investors/results-reports/annual-reports/rbi/2024-02-22-2023-Annual-Report-RBI.pdf.coredownload.pdf",
    ("RBI",  2024): "https://www.rbinternational.com/content/dam/rbi/ho/investors/results-reports/annual-reports/rbi/2025-02-25%202024-RBI%20Annual%20Report.pdf.coredownload.pdf",
    # Universal Music Group (UMG) — Dutch; 2022/2023 hashes not found
    ("UMG",  2024): "https://downloads.ctfassets.net/e66ejtqbaazg/Yt3zzyacZ1VRFc3dcEt85/b9d00d3ac6ffedea5bb01c770e825c8b/UMG_2024_Annual_Report.pdf",
    # Brunello Cucinelli (BRNW) — Italian luxury
    ("BRNW", 2022): "https://investor.brunellocucinelli.com/yep-content/media/CUCINELLI_CONSOLIDATO_ENG_2022_WEB.pdf",
    ("BRNW", 2023): "https://investor.brunellocucinelli.com/yep-content/media/Consolidated_Financial_Statements_at_31st_December_2023.pdf",
    ("BRNW", 2024): "https://investor.brunellocucinelli.com/yep-content/media/Consolidated_Financial_Statements_2024_including_Consolidated_Sustainability_Report.pdf",
    # Eiffage (EFGI) — 2022 DEU (2023/2024 already in script)
    ("EFGI", 2022): "https://www.eiffage.com/files/live/sites/eiffagev2/files/Finance/Rapport%20Annuel/DEU2022.pdf",
    # Porsche AG (P911) — 2022 standalone annual report (IPO Sept 2022)
    ("P911", 2022): "https://investorrelations.porsche.com/~/media/Files/P/porsche-ir/results-and-presentations/financial-reports-and-presentation/2022/q4-and-full-year/annual-and-sustainability-report-2022-porsche-ag.pdf",
    # Lonza Group (LONN) — via annualreports.com mirror (lonza.com bloquea con Cloudflare)
    ("LONN", 2022): "https://www.annualreports.com/HostedData/AnnualReportArchive/l/lonza_2022.pdf",
    ("LONN", 2023): "https://www.annualreports.com/HostedData/AnnualReportArchive/l/lonza_2023.pdf",
    ("LONN", 2024): "https://www.annualreports.com/HostedData/AnnualReports/PDF/lonza_2024.pdf",
    # Barry Callebaut (BARN) — FY agosto; via companiesmarketcap mirror (barry-callebaut.com bloquea)
    ("BARN", 2022): "https://companiesmarketcap.com/annual-reports/6050.ar.en.2021-2022.pdf",
    ("BARN", 2023): "https://companiesmarketcap.com/annual-reports/6050.ar.en.2022-2023.pdf",
    ("BARN", 2024): "https://companiesmarketcap.com/annual-reports/6050.ar.en.2023-2024.pdf",
    # Vodafone (VOD) — 2024 via FCA National Storage Mechanism
    ("VOD",  2024): "https://data.fca.org.uk/artefacts/NSM/Portal/NI-000097578/NI-000097578.pdf",
    # Universal Music Group (UMG) — 2022/2023 via companiesmarketcap mirror
    ("UMG",  2022): "https://companiesmarketcap.com/annual-reports/75117.ar.en.2022.pdf",
    ("UMG",  2023): "https://companiesmarketcap.com/annual-reports/75117.ar.en.2023.pdf",
    # Orange S.A. (ORAN) — 2023/2024; rapport financier annuel
    ("ORAN", 2023): "https://www.orange-business.com/sites/default/files/rapport-financier-2023.pdf",
    ("ORAN", 2024): "https://mastermedia.dam-broadcast.com/medias/domain12751/media101349/404737-yf5e7h0wx1-75.pdf",
    # Delivery Hero (DHER) — 2022 via EQS (2023 en Bundestag, 2024 en ir.deliveryhero.com)
    ("DHER", 2022): "https://ir-api.eqs.com/media/document/d642242f-833c-45ff-b7b1-9c9784cea279/assets/DeliveryHero_Annual%20Report_2022.pdf?disposition=inline",
    # Colruyt (COLR) — 2024 (FY2023/24) via Euronext ESG filing
    ("COLR", 2024): "https://live.euronext.com/sites/default/files/esg_document_files/2025-04/001881_Annual%20report%20with%20sustainability%20reporting%202023_24_0_2025-04-14_13:09.pdf",
    # Dia Group (DIA) — 2024 (necesita User-Agent; script ya lo tiene)
    ("DIA",  2024): "https://diacorporate.com/wp-content/uploads/2025/06/Annual-Report-2024-Dia-Group_ENG-1.pdf",
    # Qiagen (QIA) — IFRS Annual Reports on q4cdn (not 20-F)
    ("QIA",  2022): "https://s28.q4cdn.com/125951340/files/doc_downloads/other_reports/2022-IFRS-Annual-Report.pdf",
    ("QIA",  2023): "https://s28.q4cdn.com/125951340/files/doc_financials/2023/ar/2023-IFRS-Annual-Report.pdf",
    ("QIA",  2024): "https://s28.q4cdn.com/125951340/files/doc_financials/2024/ar/2024-IFRS-Annual-Report.pdf",
    # Nemetschek 2024 — hosted on legacy subdomain (launch2020.nemetschek.com)
    ("NEM",  2024): "https://www.launch2020.nemetschek.com/sites/default/files/documents/NEM_AR2024_EN.pdf",
}

# Para tickers con conflicto (mismo ticker, dos empresas distintas):
# clave → (ticker, empresa_keyword, año)
DIRECT_URLS_DISAMBIG: dict[tuple[str, str, int], str] = {
    # Boliden AB (Sweden) — BOL ticker shared with Bolloré
    ("BOL", "boliden", 2022): "https://investors.boliden.com/sites/boliden-ir/files/pr/202303076693-1.pdf",
    ("BOL", "boliden", 2023): "https://investors.boliden.com/sites/boliden-ir/files/pr/202403050637-1.pdf",
    ("BOL", "boliden", 2024): "https://investors.boliden.com/sites/boliden-ir/files/pr/202503192744-1.pdf",
    # Bolloré (France) — BOL ticker shared with Boliden; DEU en français
    ("BOL", "bollor", 2022): "https://www.bollore.com/wp-content/uploads/2023/04/0421_boll22t023_deu_fr_pour-mel.pdf",
    ("BOL", "bollor", 2023): "https://www.bollore.com/wp-content/uploads/2024/04/0423_boll23t029_deu_fr_2023.pdf",
    ("BOL", "bollor", 2024): "https://www.bollore.com/wp-content/uploads/2025/04/boll24t035_deu_fr_2024_mel.pdf",
}

# ---------------------------------------------------------------------------
# Mapa de páginas IR actualizadas (solo para las que funcionan)
# ---------------------------------------------------------------------------
IR_PAGES: dict[str, str] = {
    "VESTAS": "https://www.vestas.com/en/investor/financial-reports",
    "SGRO":   "https://www.segro.com/investors/results-reports-and-presentations",
    "WKL":    "https://www.wolterskluwer.com/en/investors/annual-reports",
    "FLTR":   "https://ir.flutter.com/financial-information/annual-reports",
    "BBY":    "https://www.balfourbeatty.com/investors/annual-reports/",
    "III":    "https://www.3i.com/investor-centre/reports-and-presentations/",
    "LSEG":   "https://www.lseg.com/en/investor-relations/annual-reports",
    "HMB":    "https://hmgroup.com/investors/reports-and-presentations/annual-reports/",
    "MKS":    "https://corporate.marksandspencer.com/investors/results-reports-and-publications",
    "NEM":    "https://ir.nemetschek.com/en/publications/annual-reports",
    "TRYG":   "https://investor.tryg.com/en/financial-reports/annual-reports",
    "DHER":   "https://ir.deliveryhero.com/en/publications/annual-reports",
    "LONN":   "https://investors.lonza.com/financial-data/annual-reports",
    "GLB":    "https://www.glanbia.com/investor-relations/reports-publications",
}

# ---------------------------------------------------------------------------
# Tracking helpers
# ---------------------------------------------------------------------------

def load_tracking() -> pd.DataFrame:
    return pd.read_csv(TRACKING_PATH, dtype=str).fillna("")


def save_tracking(df: pd.DataFrame) -> None:
    df.to_csv(TRACKING_PATH, index=False)


def update_row(df: pd.DataFrame, empresa: str, año: str, **kwargs) -> pd.DataFrame:
    mask = (df["empresa"] == empresa) & (df["año"] == str(año))
    for k, v in kwargs.items():
        df.loc[mask, k] = v
    return df


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def get_page(url: str, timeout: int = TIMEOUT) -> BeautifulSoup | None:
    try:
        r = SESSION.get(url, timeout=timeout, allow_redirects=True)
        r.raise_for_status()
        return BeautifulSoup(r.text, "lxml")
    except Exception as e:
        print(f"    [HTTP] {e}")
        return None


def download_pdf(url: str, dest_path: Path, dry_run: bool = False) -> tuple[bool, int]:
    if dry_run:
        print(f"    [DRY-RUN] {url[:90]}")
        return True, 0

    parsed = urllib.parse.urlparse(url)
    domain = parsed.scheme + "://" + parsed.netloc
    # Wayback Machine devuelve HTML si el Referer es el propio archive.org
    if "web.archive.org" in parsed.netloc:
        dl_headers = {**SESSION.headers}
    else:
        dl_headers = {**SESSION.headers, "Referer": domain}

    try:
        with requests.get(url, stream=True, timeout=60, headers=dl_headers) as r:
            r.raise_for_status()
            content_type = r.headers.get("Content-Type", "")
            peek = b""
            size_bytes = 0
            aborted = False
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if not peek:
                        peek = chunk[:8]
                        if not peek.startswith(b"%PDF") and "pdf" not in content_type.lower():
                            print(f"    [skip] No es un PDF")
                            aborted = True
                            break
                    f.write(chunk)
                    size_bytes += len(chunk)
                    if size_bytes > MAX_PDF_MB * 1024 * 1024:
                        print(f"    [skip] Demasiado grande (>{MAX_PDF_MB} MB)")
                        aborted = True
                        break

            if not aborted and size_bytes > 0:
                kb = size_bytes // 1024
                n_pag = max(1, kb // 80)
                print(f"    [OK] {dest_path.name}  ({kb:,} KB, ~{n_pag} pág.)")
                return True, n_pag

        dest_path.unlink(missing_ok=True)
        return False, 0

    except Exception as e:
        print(f"    [error descarga] {e}")
        dest_path.unlink(missing_ok=True)
        return False, 0


# ---------------------------------------------------------------------------
# Estrategia 1 — annualreports.com
# ---------------------------------------------------------------------------

AR_COM = "https://www.annualreports.com"


def _ar_slug(ticker: str, empresa: str) -> str | None:
    """Devuelve el slug de annualreports.com para la empresa, si está en el mapa."""
    empresa_lower = empresa.lower()
    # Búsqueda exacta con ticker + palabra inicial de empresa
    for (t, kw), slug in AR_SLUGS.items():
        if t == ticker and kw in empresa_lower:
            return slug
    # Fallback: solo por ticker (sin ambigüedad)
    matches = {slug for (t, kw), slug in AR_SLUGS.items() if t == ticker}
    if len(matches) == 1:
        return matches.pop()
    return None


def search_annualreports_com(ticker: str, empresa: str, año: int) -> str | None:
    # Intenta primero con slug conocido
    slug = _ar_slug(ticker, empresa)
    if slug:
        url = f"{AR_COM}/Company/{slug}"
        soup = get_page(url)
        if soup:
            result = _find_pdf_in_page(soup, url, año)
            if result:
                return result
        # Slug incorrecto o sin PDFs → cae al search

    # Búsqueda por nombre
    first_word = empresa.split()[0].lower().rstrip(".")
    query = urllib.parse.quote_plus(first_word)
    url = f"{AR_COM}/Companies?search={query}"
    soup = get_page(url)
    if soup is None:
        return None

    for a in soup.select("a[href*='/Company/']"):
        text = a.get_text(strip=True).lower()
        if first_word in text:
            company_url = urllib.parse.urljoin(AR_COM, a["href"])
            time.sleep(1.5)
            soup2 = get_page(company_url)
            if soup2:
                result = _find_pdf_in_page(soup2, company_url, año)
                if result:
                    return result
            break

    return None


def _find_pdf_in_page(soup: BeautifulSoup, base_url: str, año: int) -> str | None:
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        text = a.get_text(" ", strip=True).lower()
        if ".pdf" not in href.lower():
            continue
        if str(año) not in href and str(año) not in text:
            continue
        if any(ex in href.lower() for ex in EXCLUDE_KEYWORDS):
            continue
        return urllib.parse.urljoin(base_url, href)
    return None


# ---------------------------------------------------------------------------
# Estrategia 2 — URL directa conocida
# ---------------------------------------------------------------------------

def get_direct_url(ticker: str, empresa: str, año: int) -> str | None:
    empresa_lower = empresa.lower()
    for (t, kw, y), url in DIRECT_URLS_DISAMBIG.items():
        if t == ticker and kw in empresa_lower and y == año:
            return url
    return DIRECT_URLS.get((ticker, año))


# ---------------------------------------------------------------------------
# Estrategia 3 — Rastreo de página IR corporativa
# ---------------------------------------------------------------------------

def search_ir_page(ticker: str, año: int) -> str | None:
    base_url = IR_PAGES.get(ticker)
    if not base_url:
        return None
    soup = get_page(base_url)
    if soup is None:
        return None
    return _find_pdf_in_page(soup, base_url, año)


# ---------------------------------------------------------------------------
# Estrategia 4 — DuckDuckGo (con circuit-breaker)
# ---------------------------------------------------------------------------

DDG_URL = "https://html.duckduckgo.com/html/"
DDG_QUERIES = [
    '"{empresa}" annual report {año} PDF',
    '"{empresa}" "{año}" annual report filetype:pdf',
]


def search_duckduckgo(empresa: str, año: int, sin_ddg: bool = False) -> str | None:
    global _ddg_fails, _ddg_disabled
    if sin_ddg or _ddg_disabled:
        return None

    for query_tpl in DDG_QUERIES:
        query = query_tpl.format(empresa=empresa, año=año)
        try:
            r = SESSION.post(
                DDG_URL,
                data={"q": query, "b": "", "kl": "wt-wt"},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            _ddg_fails = 0  # reset circuit-breaker en éxito
        except Exception as e:
            _ddg_fails += 1
            print(f"    [DDG {_ddg_fails}/{DDG_MAX_FAILS}] {e}")
            if _ddg_fails >= DDG_MAX_FAILS:
                _ddg_disabled = True
                print("    [DDG] Desactivado por rate-limit — usa --sin-ddg para no intentarlo")
            time.sleep(SLEEP_DDG)
            continue

        soup = BeautifulSoup(r.text, "lxml")
        hrefs = list(dict.fromkeys(
            a["href"] for a in soup.find_all("a", href=True)
            if a["href"].startswith("http")
        ))

        def score(href: str) -> int:
            h = href.lower()
            if any(ex in h for ex in EXCLUDE_KEYWORDS):
                return -1
            s = 0
            if href.lower().endswith(".pdf"):
                s += 2
            if str(año) in href:
                s += 2
            if any(kw in h for kw in PREFER_KEYWORDS):
                s += 3
            return s

        candidates = [h for h in hrefs if ".pdf" in h.lower() and str(año) in h and score(h) >= 0]
        if candidates:
            return max(candidates, key=score)

        time.sleep(SLEEP_DDG)

    return None


# ---------------------------------------------------------------------------
# Orquestador
# ---------------------------------------------------------------------------

def proceso_empresa_año(
    row: pd.Series,
    df: pd.DataFrame,
    dry_run: bool,
    solo_urls: bool,
    sin_ddg: bool,
) -> pd.DataFrame:
    empresa = row["empresa"]
    ticker = row["ticker"]
    pais = row["pais"]
    año = int(row["año"])

    filename = f"{ticker}_{año}_integrated.pdf"
    dest_path = RAW_DIR / pais / ticker / filename

    if dest_path.exists() and not solo_urls:
        print(f"  [ya existe] {filename}")
        df = update_row(df, empresa, str(año),
                        estado="descargado", tipo_informe="integrated",
                        fecha_descarga=str(date.today()))
        return df

    print(f"\n→ {empresa} ({ticker}) — {año}")
    pdf_url = None

    # Estrategia 1: annualreports.com
    print("  [1] annualreports.com…")
    pdf_url = search_annualreports_com(ticker, empresa, año)
    if pdf_url:
        print(f"  [1] {pdf_url[:90]}")
        time.sleep(SLEEP_IR)

    # Estrategia 2: URL directa conocida
    if not pdf_url:
        pdf_url = get_direct_url(ticker, empresa, año)
        if pdf_url:
            print(f"  [2] URL directa: {pdf_url[:90]}")

    # Estrategia 3: IR page
    if not pdf_url and ticker in IR_PAGES:
        print("  [3] Rastreando IR corporativa…")
        pdf_url = search_ir_page(ticker, año)
        if pdf_url:
            print(f"  [3] {pdf_url[:90]}")
        time.sleep(SLEEP_IR)

    # Estrategia 4: DuckDuckGo
    if not pdf_url and not sin_ddg and not _ddg_disabled:
        print("  [4] DuckDuckGo…")
        pdf_url = search_duckduckgo(empresa, año, sin_ddg=sin_ddg)
        if pdf_url:
            print(f"  [4] {pdf_url[:90]}")

    if not pdf_url:
        print("  [!] No encontrado — búsqueda manual necesaria")
        df = update_row(df, empresa, str(año),
                        estado="problema",
                        notas="no encontrado automáticamente")
        return df

    if solo_urls:
        df = update_row(df, empresa, str(año),
                        url_fuente=pdf_url, tipo_informe="integrated")
        return df

    ok, n_pag = download_pdf(pdf_url, dest_path, dry_run=dry_run)

    if ok and not dry_run:
        df = update_row(df, empresa, str(año),
                        estado="descargado", tipo_informe="integrated",
                        url_fuente=pdf_url,
                        fecha_descarga=str(date.today()),
                        n_paginas=str(n_pag) if n_pag else "")
    elif not ok:
        df = update_row(df, empresa, str(año),
                        estado="problema",
                        url_fuente=pdf_url,
                        notas="descarga directa bloqueada — descargar manualmente")
    return df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Fase 3 — descarga de informes anuales")
    p.add_argument("--empresa", help="ID empresa (ej. E001)")
    p.add_argument("--año", type=int, help="Ejercicio fiscal (ej. 2024)")
    p.add_argument("--dry-run", action="store_true", help="Sin descargar")
    p.add_argument("--solo-urls", action="store_true",
                   help="Solo descubre y guarda URLs, no descarga")
    p.add_argument("--sin-ddg", action="store_true",
                   help="Omite DuckDuckGo (útil si está bloqueado por rate-limit)")
    return p.parse_args()


def main():
    args = parse_args()
    df = load_tracking()

    # Procesar también los que tienen 'problema' para reintentar
    mask = df["estado"].isin(["pendiente", "problema"])
    if args.empresa:
        mask &= (df["id_empresa"] == args.empresa) | df["empresa"].str.contains(args.empresa, case=False)
    if args.año:
        mask &= df["año"] == str(args.año)

    pendientes = df[mask].copy()
    total = len(pendientes)
    mode = "SOLO-URLS" if args.solo_urls else ("DRY-RUN" if args.dry_run else "DESCARGA")
    ddg_str = " (sin DDG)" if args.sin_ddg else ""
    print(f"\nFase 3 [{mode}{ddg_str}] — {total} entradas\n")

    for i, (_, row) in enumerate(pendientes.iterrows(), 1):
        print(f"[{i}/{total}]", end="")
        df = proceso_empresa_año(row, df,
                                 dry_run=args.dry_run,
                                 solo_urls=args.solo_urls,
                                 sin_ddg=args.sin_ddg)
        if not args.dry_run:
            save_tracking(df)

    df_final = load_tracking()
    desc = (df_final["estado"] == "descargado").sum()
    prob = (df_final["estado"] == "problema").sum()
    pend = (df_final["estado"] == "pendiente").sum()
    con_url = (df_final["url_fuente"].str.len() > 0).sum()
    print(f"\n{'='*55}")
    print(f"Descargados: {desc} | Problema: {prob} | Pendientes: {pend}")
    print(f"URLs descubiertas en total: {con_url}")
    if _ddg_disabled:
        print("⚠ DDG desactivado por rate-limit. Próxima vez usa --sin-ddg.")
    print(f"{'='*55}")


if __name__ == "__main__":
    main()
