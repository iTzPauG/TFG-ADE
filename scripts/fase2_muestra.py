"""
Fase 2 — Construcción de la muestra
------------------------------------
Pasos:
  2.1  Descarga composición STOXX Europe 600 desde Wikipedia
  2.2  Mapeo de tickers al formato yfinance (sufijos de bolsa por país)
  2.3  Muestreo estratificado por supersector ICB (60 empresas)
  2.4  Descarga de datos financieros y ESG vía yfinance para los 60 seleccionados
  2.5  Construcción del dataset maestro (60 empresas × 2 años = 120 filas)
"""

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

AÑOS = [2022, 2023]
N_MUESTRA = 60
RANDOM_STATE = 42

# Sufijos de bolsa por país (yfinance)
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

# Correcciones manuales: tickers de Wikipedia → ticker correcto en yfinance
# Razones: espacios en clases de acciones (B shares), tickers con puntos, etc.
TICKER_FIXES = {
    "NOVO B":   "NOVO-B",   # Novo Nordisk clase B (Denmark)
    "SKA B":    "SKA-B",    # Skanska clase B (Sweden)
    "ERICb":    "ERIC-B",   # Ericsson clase B (Sweden)
    "BT.A":     "BT-A",     # BT Group clase A (UK)
    "STMPA":    "STM",      # STMicroelectronics → US ticker más fiable
    "ENGIE":    "ENGI",     # Engie (Paris)
    "AKERBP":   "AKRBP",    # Aker BP (Oslo)
    "STLAM":    "STLAM",    # Stellantis → probar con .MI
    "SKG":      "SKG",      # Smurfit Kappa → probar .L (cotiza también en Londres)
    "QIA":      "QGEN",     # Qiagen → US ticker más fiable
    "INP":      "INPP",     # Investec → ticker alternativo
    "LUMI":     "LUMI",     # Lumibird → muy pequeña, puede faltar en yfinance
    "TOM":      "TOM2",     # TomTom (Amsterdam)
    "ADH":      "ADHR",     # Adevinta (Oslo)
    "PHNX":     "PHNX",     # Phoenix Group → probar sin sufijo
    "FLTR":     "PDYPY",    # Flutter Entertainment → ADR americano
    "SWMA":     "SWMAY",    # Swedish Match → ADR americano
    "HMB":      "HNNMY",    # H&M → ADR americano
}

# Supersectores ICB (agrupación de sectores detallados)
SUPERSECTORES = {
    "Oil & Gas":                        "Energy",
    "Oil, Gas and Coal":                "Energy",
    "Basic Resources":                  "Basic Materials",
    "Chemicals":                        "Basic Materials",
    "Construction & Materials":         "Industrials",
    "Industrial Goods & Services":      "Industrials",
    "Automobiles & Parts":              "Consumer Discretionary",
    "Food & Beverage":                  "Consumer Staples",
    "Personal Care, Drug & Grocery":    "Consumer Staples",
    "Health Care":                      "Health Care",
    "Retail":                           "Consumer Discretionary",
    "Media":                            "Communication Services",
    "Telecommunications":               "Communication Services",
    "Technology":                       "Technology",
    "Banks":                            "Financials",
    "Financial Services":               "Financials",
    "Insurance":                        "Financials",
    "Real Estate":                      "Real Estate",
    "Utilities":                        "Utilities",
    "Travel & Leisure":                 "Consumer Discretionary",
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

    # La tabla con tickers es la que tiene columna 'Ticker'
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
# PASO 2.2 — Ticker yfinance (añade sufijo de bolsa por país)
# ---------------------------------------------------------------------------
def construir_ticker_yfinance(df: pd.DataFrame) -> pd.DataFrame:
    print("\n[2.2] Mapeando tickers al formato yfinance...")
    df["sufijo"] = df["pais"].map(SUFIJOS).fillna("")

    def aplicar_fix(ticker_wiki: str) -> str:
        # Espacios → guion (clases de acciones: "NOVO B" → "NOVO-B")
        ticker = ticker_wiki.replace(" ", "-")
        # Correcciones manuales
        for original, corregido in TICKER_FIXES.items():
            if ticker_wiki == original or ticker == original:
                return corregido
        return ticker

    df["ticker_base"] = df["ticker_wiki"].apply(aplicar_fix)
    df["ticker_yf"] = df["ticker_base"] + df["sufijo"]

    # Para los ADR americanos (corrección apunta a ticker sin sufijo)
    for original, corregido in TICKER_FIXES.items():
        mask = df["ticker_wiki"].str.replace(" ", "-") == original
        if mask.any() and not corregido.endswith(tuple(SUFIJOS.values())):
            df.loc[mask, "ticker_yf"] = corregido  # sin sufijo

    sin_sufijo = df[df["sufijo"] == ""]["pais"].unique()
    if len(sin_sufijo):
        print(f"    AVISO — países sin sufijo mapeado: {list(sin_sufijo)}")
    return df


# ---------------------------------------------------------------------------
# PASO 2.3 — Muestreo estratificado por supersector
# ---------------------------------------------------------------------------
def muestreo_estratificado(df: pd.DataFrame, n: int) -> pd.DataFrame:
    print(f"\n[2.3] Muestreo estratificado (n={n}) por supersector ICB...")
    df["supersector"] = df["sector_icb"].map(SUPERSECTORES).fillna(df["sector_icb"])

    conteo = df["supersector"].value_counts()
    total = len(df)
    asignacion = (conteo / total * n).round().astype(int)
    # Ajustar para que sumen exactamente n
    diferencia = n - asignacion.sum()
    if diferencia != 0:
        idx_max = asignacion.idxmax() if diferencia < 0 else asignacion.idxmin()
        asignacion[idx_max] += diferencia

    muestra_frames = []
    for supersector, cuota in asignacion.items():
        if cuota <= 0:
            continue
        sub = df[df["supersector"] == supersector]
        k = min(cuota, len(sub))
        muestra_frames.append(sub.sample(n=k, random_state=RANDOM_STATE))

    muestra = pd.concat(muestra_frames).reset_index(drop=True)
    muestra["id_empresa"] = [f"E{i+1:03d}" for i in range(len(muestra))]
    print("    Distribución por supersector:")
    print(muestra["supersector"].value_counts().to_string())
    print(f"    Total seleccionadas: {len(muestra)}")
    out = EXTERNAL / "muestra_seleccionada.csv"
    muestra.to_csv(out, index=False)
    print(f"    Guardado en {out.relative_to(ROOT)}")
    return muestra


# ---------------------------------------------------------------------------
# PASO 2.4 — Datos financieros y ESG vía yfinance
# ---------------------------------------------------------------------------
CAMPOS_INFO = {
    "longName":          "nombre_largo",
    "country":           "pais_yf",
    "sector":            "sector_yf",
    "industry":          "industria_yf",
    "marketCap":         "market_cap",
    "trailingPE":        "PE_ratio",
    "returnOnAssets":    "ROA",
    "returnOnEquity":    "ROE",
    "debtToEquity":      "deuda_equity",
    "totalDebt":         "deuda_total",
    "totalRevenue":      "ingresos",
    "ebitda":            "ebitda",
    "profitMargins":     "margen_beneficio",
    "currency":          "moneda",
}

CAMPOS_ESG = {
    "totalEsg":          "ESG_score",
    "environmentScore":  "ESG_env",
    "socialScore":       "ESG_soc",
    "governanceScore":   "ESG_gov",
    "percentile":        "ESG_percentil",
    "esgPerformance":    "ESG_categoria",
    "controversyLevel":  "controversias",
}


def obtener_datos_empresa(ticker_yf: str) -> dict:
    datos = {"ticker_yf": ticker_yf, "error": None}
    try:
        t = yf.Ticker(ticker_yf)
        info = t.info or {}
        for campo_yf, col in CAMPOS_INFO.items():
            datos[col] = info.get(campo_yf)
        try:
            esg = t.sustainability
            if esg is not None and not esg.empty:
                esg_dict = esg.iloc[:, 0].to_dict()
                for campo_yf, col in CAMPOS_ESG.items():
                    datos[col] = esg_dict.get(campo_yf)
            else:
                for col in CAMPOS_ESG.values():
                    datos[col] = None
        except Exception:
            for col in CAMPOS_ESG.values():
                datos[col] = None
    except Exception as e:
        datos["error"] = str(e)
    return datos


def descargar_datos_yfinance(muestra: pd.DataFrame) -> pd.DataFrame:
    print(f"\n[2.4] Descargando datos yfinance para {len(muestra)} empresas...")
    registros = []
    for i, row in muestra.iterrows():
        ticker = row["ticker_yf"]
        print(f"    [{i+1:02d}/{len(muestra)}] {ticker:<15} {row['nombre'][:40]}", end="", flush=True)
        datos = obtener_datos_empresa(ticker)
        datos.update({
            "id_empresa":   row["id_empresa"],
            "nombre":       row["nombre"],
            "ticker_wiki":  row["ticker_wiki"],
            "pais":         row["pais"],
            "sector_icb":   row["sector_icb"],
            "supersector":  row["supersector"],
            "sede":         row.get("sede", ""),
        })
        ok = "OK" if datos.get("market_cap") else "sin datos"
        esg_ok = "ESG OK" if datos.get("ESG_score") else "sin ESG"
        print(f" → {ok} | {esg_ok}")
        registros.append(datos)
        time.sleep(0.3)  # evitar rate limiting

    df_yf = pd.DataFrame(registros)
    out = EXTERNAL / "yfinance_datos.csv"
    df_yf.to_csv(out, index=False)
    print(f"    Guardado en {out.relative_to(ROOT)}")
    cobertura_esg = df_yf["ESG_score"].notna().sum()
    cobertura_mktcap = df_yf["market_cap"].notna().sum()
    print(f"    Cobertura market cap: {cobertura_mktcap}/{len(df_yf)}")
    print(f"    Cobertura ESG score:  {cobertura_esg}/{len(df_yf)}")
    return df_yf


# ---------------------------------------------------------------------------
# PASO 2.5 — Dataset maestro (empresa × año)
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
                "id_empresa":        row_m["id_empresa"],
                "nombre":            row_m["nombre"],
                "ticker":            row_m["ticker_wiki"],
                "ticker_yf":         row_m["ticker_yf"],
                "pais":              row_m["pais"],
                "sector_icb":        row_m["sector_icb"],
                "supersector":       row_m["supersector"],
                "año":               año,
                "market_cap":        row_yf.get("market_cap"),
                "ingresos":          row_yf.get("ingresos"),
                "ebitda":            row_yf.get("ebitda"),
                "ROA":               row_yf.get("ROA"),
                "ROE":               row_yf.get("ROE"),
                "deuda_equity":      row_yf.get("deuda_equity"),
                "deuda_total":       row_yf.get("deuda_total"),
                "margen_beneficio":  row_yf.get("margen_beneficio"),
                "moneda":            row_yf.get("moneda"),
                "ESG_score":         row_yf.get("ESG_score"),
                "ESG_env":           row_yf.get("ESG_env"),
                "ESG_soc":           row_yf.get("ESG_soc"),
                "ESG_gov":           row_yf.get("ESG_gov"),
                "ESG_percentil":     row_yf.get("ESG_percentil"),
                "ESG_categoria":     row_yf.get("ESG_categoria"),
                "controversias":     row_yf.get("controversias"),
                "sector_yf":         row_yf.get("sector_yf"),
                "industria_yf":      row_yf.get("industria_yf"),
                "pais_yf":           row_yf.get("pais_yf"),
                "error_yf":          row_yf.get("error"),
            }
            filas.append(fila)

    maestro = pd.DataFrame(filas)
    out = EXTERNAL / "empresas_muestra.csv"
    maestro.to_csv(out, index=False)
    print(f"    Dataset maestro: {len(maestro)} filas x {len(maestro.columns)} columnas")
    print(f"    Guardado en {out.relative_to(ROOT)}")

    print("\n    === RESUMEN FINAL ===")
    print(f"    Empresas:      {maestro['id_empresa'].nunique()}")
    print(f"    Años:          {sorted(maestro['año'].unique())}")
    print(f"    Supersectores: {maestro['supersector'].nunique()}")
    print(f"    Países:        {maestro['pais'].nunique()}")
    print(f"    Con ESG score: {maestro[maestro['año']==2023]['ESG_score'].notna().sum()} empresas")
    print(f"    Países en muestra:")
    print(maestro[maestro['año']==2023]['pais'].value_counts().to_string())
    return maestro


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    df_stoxx  = descargar_stoxx600()
    df_stoxx  = construir_ticker_yfinance(df_stoxx)
    muestra   = muestreo_estratificado(df_stoxx, N_MUESTRA)
    df_yf     = descargar_datos_yfinance(muestra)
    maestro   = construir_dataset_maestro(muestra, df_yf)
    print("\n✓ Fase 2 completada.")
