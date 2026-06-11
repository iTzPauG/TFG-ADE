"""
Fase 2 — Construcción de la muestra  (v2)
------------------------------------------
Pasos:
  2.1  Descarga composición STOXX Europe 600 desde Wikipedia
  2.2  Mapeo de tickers al formato yfinance (sufijos de bolsa por país)
  2.3  Muestreo estratificado por sector ICB — 5 empresas × ~20 sectores = 100.
       + cap geográfico: máximo CAP_PAIS_N empresas de cualquier país único para
       evitar sobrerepresentación (UK era el 32% de la muestra v1).
  2.4  Descarga de datos financieros vía yfinance:
       - Estáticos: market_cap, moneda, sector, ISIN
       - Año-específicos desde income_stmt / balance_sheet:
         ROA, ROE, ingresos, EBITDA, deuda, margen (2022, 2023, 2024)
  2.5  Construcción del dataset maestro (100 empresas × 3 años = 300 filas)
  2.5b Enriquecimiento de ISINs con Wikidata + reporte de faltantes
  2.6  Generación de tracking_descargas.csv para seguimiento de PDFs (Fase 3)

Cambios respecto a v1 (60 empresas × 2 años):
  - N_MUESTRA 60→100 (5/sector en vez de 3): poder estadístico intra-sector viable
  - AÑOS [2022,2023]→[2022,2023,2024]: captura transición NFRD→CSRD
    (FY2024 = primer ejercicio de reporte obligatorio bajo CSRD para grandes PIEs)
  - CAP_PAIS_N=15 (≤15%): corrige sobrerepresentación de UK
  - Datos financieros año-específicos calculados desde income_stmt/balance_sheet
    en lugar de los campos trailing de .info (que eran idénticos para ambos años)

Uso:
  python fase2_muestra.py                  # re-descarga yfinance con tickers corregidos
  python fase2_muestra.py --regen-muestra  # regenera muestra completa desde Wikipedia
"""

import sys
import time
import warnings
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "data" / "external"
EXTERNAL.mkdir(parents=True, exist_ok=True)

AÑOS         = [2022, 2023, 2024]   # 2024 = primer año CSRD obligatorio (grandes PIEs)
N_MUESTRA    = 100                  # 5 empresas × ~20 sectores ICB
CAP_PAIS_N   = 15                   # máximo empresas de un mismo país (≤15 % de 100)
RANDOM_STATE = 42

# ---------------------------------------------------------------------------
# Sufijos de bolsa por país (yfinance)
# ---------------------------------------------------------------------------
SUFIJOS = {
    "Switzerland":      ".SW",
    "United Kingdom":   ".L",
    "Germany":          ".DE",
    "France":           ".PA",
    "Netherlands":      ".AS",
    "Spain":            ".MC",
    "Italy":            ".MI",
    "Sweden":           ".ST",
    "Denmark":          ".CO",
    "Norway":           ".OL",
    "Finland":          ".HE",
    "Belgium":          ".BR",
    "Portugal":         ".LS",
    "Ireland":          ".IR",
    "Luxembourg":       ".LU",
    "Austria":          ".VI",
    "Poland":           ".WA",
    "Czech Republic":   ".PR",
    "Hungary":          ".BD",
}

# Tickers completos que no siguen la regla ticker_wiki + SUFIJOS[pais].
# Razones documentadas: clases de acciones (B shares), tickers con puntos,
# cambio de nombre, cobertura ausente en yfinance → se usa ticker NYSE/ADR.
TICKER_OVERRIDES = {
    # Clases de acciones con espacio → guión + sufijo correcto
    "NOVO B":   "NOVO-B.CO",   # Novo Nordisk clase B (Copenhagen)
    "SKA B":    "SKA-B.ST",    # Skanska clase B (Stockholm)
    # Ticker con letras minúsculas / punto → guión + sufijo
    "ERICb":    "ERIC-B.ST",   # Ericsson clase B (Stockholm)
    "BT.A":     "BT-A.L",      # BT Group clase A (London)
    # US-listed (NYSE): mejor cobertura de datos que el listing europeo
    "STMPA":    "STM",         # STMicroelectronics (NYSE) — Amsterdam sin datos
    "QIA":      "QGEN",        # Qiagen (NYSE) — Amsterdam sin datos
    "STLAM":    "STLA",        # Stellantis (NYSE) — Amsterdam sin datos
    "HMB":      "HNNMY",       # H&M (US ADR) — HMB.ST sin datos en yfinance
    # Ticker correcto distinto del de Wikipedia
    "ENGIE":    "ENGI.PA",     # Engie en Euronext Paris (ENGIE.PA no funciona en yfinance)
    "AKERBP":   "AKRBP.OL",    # Aker BP Oslo (AKERBP.OL da 404)
    "INP":      "INVP.L",      # Investec plc, London (INP incorrecto; INVP es LSE)
    "TOM":      "TOM2.AS",     # TomTom Amsterdam (TOM.AS sin datos; TOM2.AS funciona)
    "FLTR":     "FLTR.L",      # Flutter Entertainment, London (FLTR.IR sin datos)
    # Tickers con sufijo de bolsa incorrecto o clase de acción no detectada
    "SEB":    "SEB-A.ST",    # Skandinaviska Enskilda Banken clase A (Stockholm)
    "BRNW":   "BC.MI",       # Brunello Cucinelli: ticker correcto Borsa Italiana
    "NSN":    "NESTE.HE",    # Neste: ticker completo en Helsinki (NSN.HE sin datos)
    "ALLFG":  "ALLFG.AS",    # Allfunds Group: Amsterdam tiene datos; Madrid no
    "WEND":   "MF.PA",       # Wendel: ticker en Euronext Paris (WEND.PA sin datos)
    "GLB":    "GLB.L",       # Glanbia: listing London tiene datos; Dublin no
    "ONT":    "ONTEX.BR",    # Ontex: ticker completo Brussels (ONT.BR sin datos)
    # Tickers de Wikipedia con sufijo incorrecto (nombre distinto en Yahoo Finance)
    "EFGI":   "FGR.PA",      # Eiffage: ticker en Yahoo Finance es FGR, no EFGI
    "VESTAS": "VWS.CO",      # Vestas: ticker en Yahoo Finance es VWS, no VESTAS
    "PERP":   "RI.PA",       # Pernod Ricard: ticker es RI en Euronext Paris
    "ORAN":   "ORA.PA",      # Orange S.A.: ticker es ORA en Euronext Paris
    "IPX":    "IPS.PA",      # Ipsos: ticker es IPS en Euronext Paris
    "PSN":    "PUB.PA",      # Publicis: ticker es PUB en Euronext Paris
    "STER":   "STERV.HE",    # Stora Enso: ticker es STERV en Helsinki (STER sin datos)
    "CAPP":   "CAP.PA",      # Capgemini: ticker es CAP en Euronext Paris
    "CARR":   "CA.PA",       # Carrefour: ticker es CA en Euronext Paris
    "TUI":    "TUI1.DE",     # TUI Group: ticker en Frankfurt es TUI1 (TUI.DE sin datos)
    "TEV":    "TEVA",        # Teva Pharmaceutical: ADR NASDAQ (TEV sin sufijo de bolsa europeo)
    # --- Ampliación a 196 (Decisión 027) — overrides de tickers Wikipedia incorrectos ---
    "MICP":   "ML.PA",       # Michelin: ticker correcto ML en Euronext Paris
    "FERR":   "RACE.MI",     # Ferrari: ticker correcto RACE (Borsa Italiana / NYSE)
    "RENA":   "RNO.PA",      # Renault: ticker correcto RNO en Euronext Paris
    "UC":     "UCG.MI",      # UniCredit: ticker correcto UCG en Borsa Italiana
    "MT":     "MT.AS",       # ArcelorMittal: listing Amsterdam (MT.LU sin datos)
    "BOUY":   "EN.PA",       # Bouygues: ticker correcto EN en Euronext Paris
    "HLI":    "HLN.L",       # Haleon: ticker correcto HLN en Londres
    "ENX":    "ENX.PA",      # Euronext: listing Paris (ENX.AS sin datos)
    "IGGI":   "IGG.L",       # IG Group: ticker correcto IGG en Londres
    "CCH":    "CCH.L",       # Coca-Cola HBC: listing Londres (CCH.SW sin datos)
    "ESLX":   "EL.PA",       # EssilorLuxottica: ticker correcto EL en Euronext Paris
    "SNY":    "SAN.PA",      # Sanofi: ticker correcto SAN en Euronext Paris (SNY es el ADR NYSE)
    "NOV N":  "NOVN.SW",     # Novartis: ticker correcto NOVN en SIX Swiss Exchange
    "SRENH":  "SREN.SW",     # Swiss Re: ticker correcto SREN en SIX Swiss Exchange
    "SANO":   "SANOMA.HE",   # Sanoma: ticker completo en Helsinki (SANO.HE sin datos)
    "DASH":   "DHER.DE",     # Delivery Hero: ticker correcto DHER en Frankfurt
    "ATOS":   "ATO.PA",      # Atos: ticker correcto ATO en Euronext Paris
    "AMS":    "AMS.SW",      # ams OSRAM: listing SIX Swiss Exchange (AMS.VI sin datos)
    "CASP":   "CAST.ST",     # Castellum: ticker correcto CAST en Estocolmo
    "RIGN":   "RIG",         # Transocean: ticker correcto RIG (NYSE, RIGN.SW sin datos)
    "GWI":    "CPR.MI",      # Gruppo Campari: ticker correcto CPR en Borsa Italiana
    "CTS":    "EVD.DE",      # CTS Eventim: ticker correcto EVD en Frankfurt
    "SRB":    "STB.OL",      # Storebrand: ticker correcto STB en Oslo (SRB.OL sin datos)
    # Sin datos en yfinance — excluidas vía TICKERS_EXCLUIDOS
    # SKG: Smurfit Kappa → Smurfit WestRock (NYSE:SW) 2024
    # ADH: Adevinta privatizada 2023
    # PHNX: Phoenix Group PHNX.L da 404 (bug confirmado)
    # SWMA: Swedish Match adquirida PMI 2022; retirada de bolsa
    # LUMI: Lumibird micro-cap sin cobertura yfinance
}

# Supersectores ICB — agrupa los sectores detallados en categorías más amplias.
SUPERSECTORES = {
    "Oil & Gas":                             "Energy",
    "Oil, Gas and Coal":                     "Energy",
    "Basic Resources":                       "Basic Materials",
    "Chemicals":                             "Basic Materials",
    "Construction & Materials":              "Industrials",
    "Construction and Materials":            "Industrials",
    "Industrial Goods & Services":           "Industrials",
    "Industrial Goods and Services":         "Industrials",
    "Automobiles & Parts":                   "Consumer Discretionary",
    "Automobiles and Parts":                 "Consumer Discretionary",
    "Food & Beverage":                       "Consumer Staples",
    "Food, Beverage and Tobacco":            "Consumer Staples",
    "Personal Care, Drug & Grocery":         "Consumer Staples",
    "Personal Care, Drug and Grocery Stores": "Consumer Staples",
    "Consumer Products and Services":        "Consumer Discretionary",
    "Health Care":                           "Health Care",
    "Retail":                                "Consumer Discretionary",
    "Media":                                 "Communication Services",
    "Telecommunications":                    "Communication Services",
    "Technology":                            "Technology",
    "Banks":                                 "Financials",
    "Financial Services":                    "Financials",
    "Insurance":                             "Financials",
    "Real Estate":                           "Real Estate",
    "Utilities":                             "Utilities",
    "Travel & Leisure":                      "Consumer Discretionary",
    "Travel and Leisure":                    "Consumer Discretionary",
}

# Notas sobre empresas con cobertura limitada en yfinance
NOTAS_COBERTURA = {
    "SKG":  "Smurfit Kappa fusionada en Smurfit WestRock (SW) 2024; sin historial en yfinance",
    "ADH":  "Adevinta privatizada por consorcio PE 2023; sin cotización activa",
    "PHNX": "Phoenix Group PHNX.L: 404 persistente en yfinance; empresa activa en LSE",
    "SWMA": "Swedish Match adquirida por Philip Morris y retirada de bolsa en 2022",
    "LUMI": "Lumibird: micro-cap francesa sin cobertura en yfinance",
}

# Tickers excluidos del muestreo por imposibilidad de obtener datos financieros.
TICKERS_EXCLUIDOS = {
    "SKG",   # Smurfit Kappa → Smurfit WestRock 2024; sin historial en ticker original
    "ADH",   # Adevinta: privatizada PE 2023; sin cotización activa
    "SWMA",  # Swedish Match: adquirida Philip Morris 2022; retirada de bolsa
    "LUMI",  # Lumibird: micro-cap; sin cobertura yfinance
    "PHNX",  # Phoenix Group: PHNX.L devuelve 404 (bug yfinance confirmado)
}


# ---------------------------------------------------------------------------
# PASO 2.1 — Descarga del índice desde Wikipedia
# ---------------------------------------------------------------------------
def descargar_stoxx600() -> pd.DataFrame:
    print("\n[2.1] Descargando composición STOXX Europe 600 desde Wikipedia...")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
    }
    r = requests.get("https://en.wikipedia.org/wiki/STOXX_Europe_600", headers=headers, timeout=20)
    r.raise_for_status()
    tablas = pd.read_html(StringIO(r.text), flavor="lxml")

    df = next(t for t in tablas if "Ticker" in t.columns)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "Ticker":       "ticker_wiki",
        "Company":      "nombre",
        "ICB Sector":   "sector_icb",
        "Country":      "pais",
        "Headquarters": "sede",
    })
    df = df.dropna(subset=["ticker_wiki", "nombre"]).reset_index(drop=True)
    print(f"    {len(df)} empresas encontradas, {df['sector_icb'].nunique()} sectores ICB.")
    out = EXTERNAL / "stoxx600_componentes.csv"
    df.to_csv(out, index=False)
    print(f"    Guardado en {out.relative_to(ROOT)}")
    return df


# ---------------------------------------------------------------------------
# PASO 2.2 — Ticker yfinance (añade sufijo de bolsa por país o usa override)
# ---------------------------------------------------------------------------
def construir_ticker_yfinance(df: pd.DataFrame) -> pd.DataFrame:
    print("\n[2.2] Mapeando tickers al formato yfinance...")
    df["sufijo"] = df["pais"].map(SUFIJOS).fillna("")

    def get_ticker_yf(row: pd.Series) -> str:
        wiki = row["ticker_wiki"]
        if wiki in TICKER_OVERRIDES:
            return TICKER_OVERRIDES[wiki]
        sufijo = SUFIJOS.get(row["pais"], "")
        return wiki.replace(" ", "-") + sufijo

    df["ticker_yf"] = df.apply(get_ticker_yf, axis=1)

    sin_sufijo = df[(df["sufijo"] == "") & (~df["ticker_wiki"].isin(TICKER_OVERRIDES))]["pais"].unique()
    if len(sin_sufijo):
        print(f"    AVISO — países sin sufijo mapeado (no override): {list(sin_sufijo)}")
    overrides_usados = df[df["ticker_wiki"].isin(TICKER_OVERRIDES)]["ticker_wiki"].unique()
    print(f"    Overrides aplicados: {len(overrides_usados)}")
    return df


def aplicar_overrides_a_muestra(muestra: pd.DataFrame) -> pd.DataFrame:
    """Aplica TICKER_OVERRIDES, SUPERSECTORES y advierte sobre TICKERS_EXCLUIDOS en muestra existente."""
    presentes = muestra[muestra["ticker_wiki"].isin(TICKERS_EXCLUIDOS)]
    if len(presentes):
        print(f"    AVISO — muestra existente contiene {len(presentes)} empresa(s) excluida(s):")
        for _, r in presentes.iterrows():
            print(f"      {r['ticker_wiki']} ({r['nombre']}): {NOTAS_COBERTURA.get(r['ticker_wiki'], '')}")
        print("    Ejecuta con --regen-muestra para regenerar la muestra sin ellas.")

    muestra["sufijo"] = muestra["pais"].map(SUFIJOS).fillna("")

    def get_ticker_yf(row: pd.Series) -> str:
        wiki = row["ticker_wiki"]
        if wiki in TICKER_OVERRIDES:
            return TICKER_OVERRIDES[wiki]
        sufijo = SUFIJOS.get(row["pais"], "")
        return wiki.replace(" ", "-") + sufijo

    muestra["ticker_yf"] = muestra.apply(get_ticker_yf, axis=1)
    muestra["supersector"] = muestra["sector_icb"].map(SUPERSECTORES).fillna(muestra["sector_icb"])
    return muestra


# ---------------------------------------------------------------------------
# PASO 2.3 — Muestreo estratificado (5/sector) + cap geográfico
# Estrategia:
#   1. Muestreo proporcional por sector ICB (cuota base = N // n_sectores).
#   2. Cap geográfico: si un país supera CAP_PAIS_N, el exceso se reemplaza por
#      empresas de otros países dentro del mismo sector ICB (misma cuota disponible).
#      Esto corrige la sobrerepresentación estructural de UK en el STOXX 600.
# ---------------------------------------------------------------------------
def muestreo_estratificado(df: pd.DataFrame, n: int, cap_pais: int = CAP_PAIS_N) -> pd.DataFrame:
    print(f"\n[2.3] Muestreo estratificado (n={n}, cap_pais={cap_pais}) — por sector ICB...")

    excluidas = df[df["ticker_wiki"].isin(TICKERS_EXCLUIDOS)]
    df = df[~df["ticker_wiki"].isin(TICKERS_EXCLUIDOS)].copy()
    if len(excluidas):
        print(f"    Excluidas: {excluidas[['nombre','ticker_wiki','sector_icb']].values.tolist()}")

    df["supersector"] = df["sector_icb"].map(SUPERSECTORES).fillna(df["sector_icb"])

    sectores = sorted(df["sector_icb"].unique())
    n_sectores = len(sectores)
    k_base = n // n_sectores
    resto  = n - k_base * n_sectores

    muestra_frames = []
    deficit = 0
    for i, sector in enumerate(sectores):
        sub = df[df["sector_icb"] == sector]
        cuota = k_base + (1 if i < resto else 0)
        disponibles = len(sub)
        if disponibles < cuota:
            print(f"    AVISO — '{sector}': solo {disponibles} disponibles (cuota {cuota})")
            deficit += cuota - disponibles
            cuota = disponibles
        muestra_frames.append(sub.sample(n=cuota, random_state=RANDOM_STATE))

    muestra = pd.concat(muestra_frames).reset_index(drop=True)

    if deficit > 0:
        ya = set(muestra["ticker_wiki"])
        candidatos = df[~df["ticker_wiki"].isin(ya)].copy()
        extras = candidatos.sample(n=min(deficit, len(candidatos)), random_state=RANDOM_STATE + 1)
        muestra = pd.concat([muestra, extras]).reset_index(drop=True)
        print(f"    Déficit cubierto con {len(extras)} empresa(s) adicionale(s)")

    # --- Deduplicar por ticker_wiki + pais (puede haber repetidos en la Wikipedia) ---
    antes_dup = len(muestra)
    muestra = muestra.drop_duplicates(subset=["ticker_wiki", "pais"]).reset_index(drop=True)
    if len(muestra) < antes_dup:
        print(f"    Deduplicados: {antes_dup - len(muestra)} filas eliminadas")

    # --- Cap geográfico iterativo ---
    # Se itera hasta que ningún país supere el cap, reemplazando en cada ronda
    # el exceso del país más sobrerepresentado. Evita que los reemplazos de un
    # país disparen otro país por encima del cap.
    rs_offset = 5
    for _ in range(10):  # máximo 10 rondas
        pais_counts = muestra["pais"].value_counts()
        paises_exceso = pais_counts[pais_counts > cap_pais].index.tolist()
        if not paises_exceso:
            break

        # Tratar el país con mayor exceso primero
        pais = pais_counts[paises_exceso].idxmax()
        exceso_n = int(pais_counts[pais]) - cap_pais
        en_muestra_pais = muestra[muestra["pais"] == pais]
        a_quitar = en_muestra_pais.sample(n=exceso_n, random_state=RANDOM_STATE + rs_offset)
        muestra = muestra[~muestra.index.isin(a_quitar.index)].copy()

        ya = set(muestra["ticker_wiki"])
        sectores_afectados = a_quitar["sector_icb"].unique()
        reemplazos = []
        for sector in sectores_afectados:
            n_need = int((a_quitar["sector_icb"] == sector).sum())
            # Candidatos: mismo sector, no seleccionados, no del país excedente
            # y que el país de destino tampoco supere el cap tras la adición
            for _ in range(3):  # intentar hasta 3 veces con diferentes filtros
                pais_counts_actual = muestra["pais"].value_counts()
                candidatos = df[
                    (df["sector_icb"] == sector) &
                    (~df["ticker_wiki"].isin(ya))
                ].copy()
                # Excluir países ya en el cap
                candidatos = candidatos[~candidatos["pais"].isin(
                    pais_counts_actual[pais_counts_actual >= cap_pais].index
                )]
                if len(candidatos) >= n_need:
                    break
                # Si no hay suficientes, relajar: admitir países hasta cap+1
                candidatos = df[
                    (df["sector_icb"] == sector) &
                    (~df["ticker_wiki"].isin(ya)) &
                    (df["pais"] != pais)
                ]
                break

            tomar = min(n_need, len(candidatos))
            if tomar > 0:
                sel = candidatos.sample(n=tomar, random_state=RANDOM_STATE + rs_offset + 1)
                reemplazos.append(sel)
                ya.update(sel["ticker_wiki"].tolist())

        if reemplazos:
            muestra = pd.concat([muestra] + reemplazos).reset_index(drop=True)

        nuevo_count = int((muestra["pais"] == pais).sum())
        print(f"    Cap {pais}: {int(pais_counts[pais])} → {nuevo_count} empresas")
        rs_offset += 10

    muestra["id_empresa"] = [f"E{i+1:03d}" for i in range(len(muestra))]

    print(f"\n    Distribución por sector ICB (cuota base: {k_base}/sector):")
    print(muestra["sector_icb"].value_counts().sort_index().to_string())
    print(f"\n    Distribución por supersector:")
    print(muestra["supersector"].value_counts().to_string())
    print(f"\n    Distribución por país (cap={cap_pais}):")
    print(muestra["pais"].value_counts().to_string())
    print(f"\n    Total seleccionadas: {len(muestra)}")

    out = EXTERNAL / "muestra_seleccionada.csv"
    muestra.to_csv(out, index=False)
    print(f"    Guardado en {out.relative_to(ROOT)}")
    return muestra


# ---------------------------------------------------------------------------
# PASO 2.4 — Datos financieros vía yfinance (año-específicos)
#
# Cambio clave respecto a v1: en lugar de usar los campos trailing de .info
# (returnOnAssets, returnOnEquity, totalRevenue…), que son el último valor
# disponible y quedan idénticos para todos los años, ahora se extraen
# income_stmt y balance_sheet anuales y se calculan los ratios por año.
#
# Columnas en yfinance_datos.csv:
#   - Estáticas: id_empresa, ticker_wiki, market_cap, moneda, ISIN, sector_yf, ...
#   - Año-específicas: ingresos_YYYY, ebitda_YYYY, net_income_YYYY,
#     total_assets_YYYY, equity_YYYY, deuda_YYYY,
#     ROA_YYYY, ROE_YYYY, margen_beneficio_YYYY, deuda_equity_YYYY
# ---------------------------------------------------------------------------
def _val(series: pd.Series, key: str):
    """Extrae un valor numérico de una Series, devuelve None si ausente o NaN."""
    v = series.get(key)
    try:
        return float(v) if pd.notna(v) else None
    except (TypeError, ValueError):
        return None


def _ratio(a, b):
    """División segura; devuelve None si algún operando es None/0."""
    if a is not None and b is not None and b != 0:
        return a / b
    return None


def obtener_financieros_empresa(ticker_yf: str) -> dict:
    datos = {
        "ticker_yf":    ticker_yf,
        "error":        None,
        "market_cap":   None,
        "moneda":       None,
        "sector_yf":    None,
        "industria_yf": None,
        "pais_yf":      None,
        "ISIN":         None,
    }
    # Inicializar columnas año-específicas a None
    cols_anuales = ["ingresos", "ebitda", "net_income", "total_assets",
                    "equity", "deuda", "ROA", "ROE", "margen_beneficio", "deuda_equity"]
    for año in AÑOS:
        for col in cols_anuales:
            datos[f"{col}_{año}"] = None

    try:
        t = yf.Ticker(ticker_yf)
        info = t.info or {}

        datos["market_cap"]   = info.get("marketCap")
        datos["moneda"]       = info.get("currency")
        datos["sector_yf"]    = info.get("sector")
        datos["industria_yf"] = info.get("industry")
        datos["pais_yf"]      = info.get("country")

        try:
            isin = t.isin
            datos["ISIN"] = isin if isin and isin != "-" else None
        except Exception:
            pass

        # Financieros históricos año a año
        try:
            inc = t.income_stmt
            bs  = t.balance_sheet

            for año in AÑOS:
                col_inc = next((c for c in inc.columns if hasattr(c, "year") and c.year == año), None)
                col_bs  = next((c for c in bs.columns  if hasattr(c, "year") and c.year == año), None)

                inc_s = inc[col_inc] if col_inc is not None else pd.Series(dtype=float)
                bs_s  = bs[col_bs]   if col_bs  is not None else pd.Series(dtype=float)

                ni     = _val(inc_s, "Net Income")
                rev    = _val(inc_s, "Total Revenue")
                assets = _val(bs_s,  "Total Assets")
                equity = _val(bs_s,  "Stockholders Equity")
                debt   = _val(bs_s,  "Total Debt")

                # EBITDA: cascada directa → normalizada → EBIT+D&A → OI+D&A → Pretax+D&A
                ebitda = _val(inc_s, "EBITDA")
                if ebitda is None:
                    ebitda = _val(inc_s, "Normalized EBITDA")
                if ebitda is None:
                    da = _val(inc_s, "Reconciled Depreciation")
                    for base_key in ("EBIT", "Operating Income", "Pretax Income"):
                        base = _val(inc_s, base_key)
                        if base is not None and da is not None:
                            ebitda = base + da
                            break

                datos[f"ingresos_{año}"]         = rev
                datos[f"ebitda_{año}"]           = ebitda
                datos[f"net_income_{año}"]       = ni
                datos[f"total_assets_{año}"]     = assets
                datos[f"equity_{año}"]           = equity
                datos[f"deuda_{año}"]            = debt
                datos[f"ROA_{año}"]              = _ratio(ni, assets)
                datos[f"ROE_{año}"]              = _ratio(ni, equity)
                datos[f"margen_beneficio_{año}"] = _ratio(ni, rev)
                datos[f"deuda_equity_{año}"]     = _ratio(debt, equity)

        except Exception as e_fin:
            datos["error"] = f"financials: {e_fin}"

    except Exception as e:
        datos["error"] = str(e)

    return datos


def descargar_datos_yfinance(muestra: pd.DataFrame) -> pd.DataFrame:
    print(f"\n[2.4] Descargando datos yfinance para {len(muestra)} empresas...")
    registros = []
    for i, row in muestra.iterrows():
        ticker = row["ticker_yf"]
        nombre_corto = row["nombre"][:30]
        print(f"    [{i+1:03d}/{len(muestra)}] {ticker:<16} {nombre_corto:<30}", end="", flush=True)

        datos = obtener_financieros_empresa(ticker)
        datos.update({
            "id_empresa":  row["id_empresa"],
            "nombre":      row["nombre"],
            "ticker_wiki": row["ticker_wiki"],
            "pais":        row["pais"],
            "sector_icb":  row["sector_icb"],
            "supersector": row["supersector"],
            "nota":        NOTAS_COBERTURA.get(row["ticker_wiki"], ""),
        })

        ok = "OK" if datos.get("market_cap") else "sin datos"
        # Mostrar cuántos años con financieros
        n_años_ok = sum(1 for a in AÑOS if datos.get(f"ingresos_{a}") is not None)
        print(f" → {ok} ({n_años_ok}/{len(AÑOS)} años financieros)")
        registros.append(datos)
        time.sleep(0.5)

    df_yf = pd.DataFrame(registros)
    out = EXTERNAL / "yfinance_datos.csv"
    df_yf.to_csv(out, index=False)
    print(f"    Guardado en {out.relative_to(ROOT)}")
    print(f"    Cobertura market_cap: {df_yf['market_cap'].notna().sum()}/{len(df_yf)}")
    for año in AÑOS:
        n_ok = df_yf[f"ingresos_{año}"].notna().sum()
        print(f"    Ingresos {año}: {n_ok}/{len(df_yf)}")
    sin_datos = df_yf[df_yf["market_cap"].isna()]["nombre"].tolist()
    if sin_datos:
        print(f"    Sin datos financieros: {sin_datos}")
    return df_yf


# ---------------------------------------------------------------------------
# PASO 2.5 — Dataset maestro (empresa × año, con financieros año-específicos)
# ---------------------------------------------------------------------------
def construir_dataset_maestro(muestra: pd.DataFrame, df_yf: pd.DataFrame) -> pd.DataFrame:
    print(f"\n[2.5] Construyendo dataset maestro ({len(muestra)} empresas × {len(AÑOS)} años)...")
    filas = []
    for _, row_m in muestra.iterrows():
        row_yf = df_yf[df_yf["id_empresa"] == row_m["id_empresa"]]
        if row_yf.empty:
            continue
        row_yf = row_yf.iloc[0]

        for año in AÑOS:
            fila = {
                # Identificadores
                "id_empresa":    row_m["id_empresa"],
                "nombre":        row_m["nombre"],
                "ticker":        row_m["ticker_wiki"],
                "ticker_yf":     row_m["ticker_yf"],
                "ISIN":          row_yf.get("ISIN"),
                # Clasificación
                "pais":          row_m["pais"],
                "sector_ICB":    row_m["sector_icb"],
                "supersector":   row_m["supersector"],
                "año":           año,
                # Tamaño (market_cap = proxy estático de tamaño; ver Metodología)
                "capitalización": row_yf.get("market_cap"),
                "moneda":         row_yf.get("moneda"),
                # Financieros año-específicos calculados desde income_stmt/balance_sheet
                "ingresos":         row_yf.get(f"ingresos_{año}"),
                "ebitda":           row_yf.get(f"ebitda_{año}"),
                "net_income":       row_yf.get(f"net_income_{año}"),
                "total_assets":     row_yf.get(f"total_assets_{año}"),
                "equity":           row_yf.get(f"equity_{año}"),
                "deuda":            row_yf.get(f"deuda_{año}"),
                "ROA":              row_yf.get(f"ROA_{año}"),
                "ROE":              row_yf.get(f"ROE_{año}"),
                "margen_beneficio": row_yf.get(f"margen_beneficio_{año}"),
                "deuda_equity":     row_yf.get(f"deuda_equity_{año}"),
                # Metadatos yfinance
                "sector_yf":    row_yf.get("sector_yf"),
                "industria_yf": row_yf.get("industria_yf"),
                "pais_yf":      row_yf.get("pais_yf"),
                "nota":         row_yf.get("nota", ""),
                "error_yf":     row_yf.get("error"),
            }
            filas.append(fila)

    maestro = pd.DataFrame(filas)
    out = EXTERNAL / "empresas_muestra.csv"
    maestro.to_csv(out, index=False)
    print(f"    Dataset maestro: {len(maestro)} filas x {len(maestro.columns)} columnas")
    print(f"    Guardado en {out.relative_to(ROOT)}")

    año_ref = max(AÑOS)
    df_ref = maestro[maestro["año"] == año_ref]
    print(f"\n    === RESUMEN FINAL (año {año_ref}) ===")
    print(f"    Empresas:           {maestro['id_empresa'].nunique()}")
    print(f"    Años:               {sorted(maestro['año'].unique())}")
    print(f"    Supersectores:      {df_ref['supersector'].nunique()}")
    print(f"    Países:             {df_ref['pais'].nunique()}")
    print(f"    Con capitalización: {df_ref['capitalización'].notna().sum()}")
    print(f"    Con ROA {año_ref}:      {df_ref['ROA'].notna().sum()}")
    print(f"    Con ISIN:           {df_ref['ISIN'].notna().sum()}")

    print(f"\n    Distribución por supersector:")
    print(df_ref["supersector"].value_counts().to_string())
    print(f"\n    Países en muestra:")
    print(df_ref["pais"].value_counts().to_string())

    sin_cap = df_ref[df_ref["capitalización"].isna()][["id_empresa", "nombre", "ticker", "nota"]]
    if not sin_cap.empty:
        print(f"\n    AVISO — {len(sin_cap)} empresas sin datos financieros:")
        print(sin_cap.to_string(index=False))

    return maestro


# ---------------------------------------------------------------------------
# PASO 2.5b — Enriquecimiento de ISINs (Wikidata + reporte de pendientes)
#
# Fuentes por orden de preferencia:
#   1. isins_wikidata.csv: ISINs del listing primario europeo de Wikidata
#   2. yfinance .isin: cubre bien tickers US (NYSE/NASDAQ); menos fiable europeos
#   3. isins_pendientes.csv: lista generada para búsqueda manual de los restantes
# ---------------------------------------------------------------------------
def enriquecer_isins(maestro: pd.DataFrame) -> pd.DataFrame:
    print(f"\n[2.5b] Enriqueciendo ISINs con Wikidata...")

    isin_path = EXTERNAL / "isins_wikidata.csv"
    if isin_path.exists():
        df_wiki = pd.read_csv(isin_path)
        df_wiki = df_wiki[df_wiki["isin_wikidata"].notna()].copy()
        df_wiki["nombre_norm"] = df_wiki["nombre"].str.lower().str.strip()
        isin_map = dict(zip(df_wiki["nombre_norm"], df_wiki["isin_wikidata"]))

        maestro["_nombre_norm"] = maestro["nombre"].str.lower().str.strip()
        maestro["_isin_wiki"] = maestro["_nombre_norm"].map(isin_map)

        antes = maestro["ISIN"].notna().sum()

        def isin_final(row):
            # Wikidata primero (listing primario europeo); yfinance como fallback
            if pd.notna(row["_isin_wiki"]):
                return row["_isin_wiki"]
            return row["ISIN"]

        maestro["ISIN"] = maestro.apply(isin_final, axis=1)
        maestro.drop(columns=["_nombre_norm", "_isin_wiki"], inplace=True)

        despues = maestro["ISIN"].notna().sum()
        n_con = maestro[maestro["ISIN"].notna()]["id_empresa"].nunique()
        n_tot = maestro["id_empresa"].nunique()
        print(f"    ISINs filas: {antes} → {despues} / {len(maestro)}")
        print(f"    Empresas con ISIN: {n_con}/{n_tot}")
    else:
        print("    isins_wikidata.csv no encontrado — omitido.")

    # Reporte de pendientes para búsqueda manual
    sin_isin = (
        maestro[maestro["ISIN"].isna()][["id_empresa", "nombre", "ticker", "pais", "sector_ICB"]]
        .drop_duplicates("id_empresa")
        .sort_values("id_empresa")
    )
    if not sin_isin.empty:
        pendientes_path = EXTERNAL / "isins_pendientes.csv"
        sin_isin.to_csv(pendientes_path, index=False)
        print(f"\n    {len(sin_isin)} empresas sin ISIN → {pendientes_path.name}")
        print("    Fuentes recomendadas: Euronext live search, LSE.co.uk, Borsa Italiana,")
        print("    Deutsche Börse o la página IR de la empresa.")
        print("    Rellena la columna 'ISIN' y vuelve a correr: python scripts/merge_isins.py")

    out = EXTERNAL / "empresas_muestra.csv"
    maestro.to_csv(out, index=False)
    print(f"\n    Guardado en {out.relative_to(ROOT)}")
    return maestro


# ---------------------------------------------------------------------------
# PASO 2.6 — Hoja de seguimiento de descargas (preparación Fase 3)
# ---------------------------------------------------------------------------
def generar_tracking_descargas(muestra: pd.DataFrame) -> pd.DataFrame:
    print(f"\n[2.6] Generando hoja de seguimiento de descargas (Fase 3)...")
    filas = []
    for _, row in muestra.iterrows():
        for año in AÑOS:
            filas.append({
                "id_empresa":     row["id_empresa"],
                "empresa":        row["nombre"],
                "ticker":         row["ticker_wiki"],
                "pais":           row["pais"],
                "año":            año,
                "tipo_informe":   "",
                "url_fuente":     "",
                "fecha_descarga": "",
                "n_paginas":      "",
                "idioma":         "",
                "estado":         "pendiente",
                "notas":          "",
            })
    df = pd.DataFrame(filas)
    out = EXTERNAL / "tracking_descargas.csv"
    if out.exists():
        existing = pd.read_csv(out)
        has_progress = (
            (existing["estado"] != "pendiente").any() or
            existing["url_fuente"].notna().any()
        )
        if has_progress:
            print(f"    AVISO — {out.name} ya tiene datos parciales. No se sobreescribe.")
            return existing
    df.to_csv(out, index=False)
    print(f"    Tracking generado: {len(df)} filas → {out.relative_to(ROOT)}")
    return df


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    regen_muestra = "--regen-muestra" in sys.argv

    if regen_muestra:
        print(f"Modo: regeneración completa de la muestra (n={N_MUESTRA}, años={AÑOS})")
        df_stoxx = descargar_stoxx600()
        df_stoxx = construir_ticker_yfinance(df_stoxx)
        muestra = muestreo_estratificado(df_stoxx, N_MUESTRA, cap_pais=CAP_PAIS_N)
    else:
        print(f"[2.1-2.3] Usando muestra existente en muestra_seleccionada.csv")
        print(f"          (pasa --regen-muestra para regenerar desde Wikipedia con n={N_MUESTRA})")
        muestra_path = EXTERNAL / "muestra_seleccionada.csv"
        if not muestra_path.exists():
            print("  ERROR: muestra_seleccionada.csv no encontrado. Ejecuta con --regen-muestra")
            sys.exit(1)
        muestra = pd.read_csv(muestra_path)
        muestra = aplicar_overrides_a_muestra(muestra)
        muestra.to_csv(muestra_path, index=False)
        print(f"    Muestra cargada: {len(muestra)} empresas")

    df_yf = descargar_datos_yfinance(muestra)
    maestro = construir_dataset_maestro(muestra, df_yf)
    maestro = enriquecer_isins(maestro)
    generar_tracking_descargas(muestra)
    print(f"\n✓ Fase 2 completada. Dataset: {len(maestro)} filas ({maestro['id_empresa'].nunique()} empresas × {len(AÑOS)} años).")
