"""
fase2_parche_deuda.py — Resolución de deuda técnica Fase 2
----------------------------------------------------------
Acciones:
  1. Sustituye Schibsted (E097, SCHA.OL) por Universal Music Group (UMG.AS)
     en empresas_muestra.csv, muestra_seleccionada.csv, yfinance_datos.csv
     y tracking_descargas.csv.
     Motivo: Schibsted no tiene cobertura en yfinance (ningún ticker alternativo).
     UMG: Países Bajos, sector Media, 3/3 años con datos (dic FY).

  2. Añade nota en nota/error_yf para las 4 empresas con gap FY2022 por
     año fiscal no-diciembre (balance_sheet yfinance limitado a 4 años):
       - E023 Richemont   (CFR.SW,  FY ends March 31)
       - E034 3i Group    (III.L,   FY ends March 31)
       - E066 JD Sports   (JD.L,    FY ends January 31)
       - E070 Vodafone    (VOD.L,   FY ends March 31)

Uso:
  python scripts/fase2_parche_deuda.py
"""

import time
import warnings
from pathlib import Path

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

ROOT     = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "data" / "external"
AÑOS     = [2022, 2023, 2024]

# ---------------------------------------------------------------------------
# Empresa de sustitución
# ---------------------------------------------------------------------------
UMG = {
    "id_empresa":  "E097",
    "nombre":      "Universal Music Group",
    "ticker":      "UMG",
    "ticker_yf":   "UMG.AS",
    "pais":        "Netherlands",
    "sector_ICB":  "Media",
    "supersector": "Communication Services",
    "sector_icb":  "Media",
}

# Notas para empresas con gap FY2022
NOTA_FY_NONDEC = (
    "yfinance sin datos FY{año} (año fiscal no-diciembre; "
    "balance_sheet cubre solo últimos 4 ejercicios)"
)
EMPRESAS_FY_GAP = {
    "E023": "March 31",
    "E034": "March 31",
    "E066": "January 31",
    "E070": "March 31",
}


# ---------------------------------------------------------------------------
# Helpers financieros (misma lógica que fase2_muestra.py)
# ---------------------------------------------------------------------------
def _val(series: pd.Series, key: str):
    v = series.get(key)
    try:
        return float(v) if pd.notna(v) else None
    except (TypeError, ValueError):
        return None


def _ratio(a, b):
    if a is not None and b is not None and b != 0:
        return a / b
    return None


def obtener_financieros_umg() -> dict:
    tkr = UMG["ticker_yf"]
    print(f"  Descargando datos yfinance para {UMG['nombre']} ({tkr})...")
    t = yf.Ticker(tkr)
    info = t.info or {}

    datos = {
        "ticker_yf":    tkr,
        "error":        None,
        "market_cap":   info.get("marketCap"),
        "moneda":       info.get("currency"),
        "sector_yf":    info.get("sector"),
        "industria_yf": info.get("industry"),
        "pais_yf":      info.get("country"),
        "ISIN":         None,
    }

    try:
        isin = t.isin
        datos["ISIN"] = isin if isin and isin != "-" else None
    except Exception:
        pass

    inc = t.income_stmt
    bs  = t.balance_sheet

    for año in AÑOS:
        col_inc = next((c for c in inc.columns if hasattr(c, "year") and c.year == año), None)
        col_bs  = next((c for c in bs.columns  if hasattr(c, "year") and c.year == año), None)

        inc_s = inc[col_inc] if col_inc is not None else pd.Series(dtype=float)
        bs_s  = bs[col_bs]   if col_bs  is not None else pd.Series(dtype=float)

        ni     = _val(inc_s, "Net Income")
        rev    = _val(inc_s, "Total Revenue")
        ebitda = _val(inc_s, "EBITDA")
        assets = _val(bs_s,  "Total Assets")
        equity = _val(bs_s,  "Stockholders Equity")
        debt   = _val(bs_s,  "Total Debt")

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

        ok = "✓" if rev is not None else "✗"
        print(f"    FY{año} ({str(col_inc.date()) if col_inc else 'NO'}): ingresos={ok}")

    datos.update({
        "id_empresa":  UMG["id_empresa"],
        "nombre":      UMG["nombre"],
        "ticker_wiki": UMG["ticker"],
        "pais":        UMG["pais"],
        "sector_icb":  UMG["sector_ICB"],
        "supersector": UMG["supersector"],
        "nota":        "",
    })

    return datos


def construir_filas_maestro(datos_yf: dict) -> list[dict]:
    filas = []
    for año in AÑOS:
        filas.append({
            "id_empresa":    UMG["id_empresa"],
            "nombre":        UMG["nombre"],
            "ticker":        UMG["ticker"],
            "ticker_yf":     UMG["ticker_yf"],
            "ISIN":          datos_yf.get("ISIN"),
            "pais":          UMG["pais"],
            "sector_ICB":    UMG["sector_ICB"],
            "supersector":   UMG["supersector"],
            "año":           año,
            "capitalización": datos_yf.get("market_cap"),
            "moneda":         datos_yf.get("moneda"),
            "ingresos":       datos_yf.get(f"ingresos_{año}"),
            "ebitda":         datos_yf.get(f"ebitda_{año}"),
            "net_income":     datos_yf.get(f"net_income_{año}"),
            "total_assets":   datos_yf.get(f"total_assets_{año}"),
            "equity":         datos_yf.get(f"equity_{año}"),
            "deuda":          datos_yf.get(f"deuda_{año}"),
            "ROA":            datos_yf.get(f"ROA_{año}"),
            "ROE":            datos_yf.get(f"ROE_{año}"),
            "margen_beneficio": datos_yf.get(f"margen_beneficio_{año}"),
            "deuda_equity":   datos_yf.get(f"deuda_equity_{año}"),
            "sector_yf":     datos_yf.get("sector_yf"),
            "industria_yf":  datos_yf.get("industria_yf"),
            "pais_yf":       datos_yf.get("pais_yf"),
            "nota":          "",
            "error_yf":      datos_yf.get("error"),
        })
    return filas


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("\n=== Fase 2 — Parche deuda técnica ===\n")

    # --- Paso 1: datos yfinance para UMG ---
    datos_umg = obtener_financieros_umg()
    time.sleep(0.5)

    # --- Paso 2: empresas_muestra.csv ---
    maestro_path = EXTERNAL / "empresas_muestra.csv"
    maestro = pd.read_csv(maestro_path)

    # Reemplazar filas E097 (Schibsted) con UMG
    maestro = maestro[maestro["id_empresa"] != "E097"].copy()
    filas_umg = construir_filas_maestro(datos_umg)
    maestro = pd.concat([maestro, pd.DataFrame(filas_umg)], ignore_index=True)
    maestro = maestro.sort_values(["id_empresa", "año"]).reset_index(drop=True)

    # Añadir notas a empresas con gap FY2022
    for eid, fy_end in EMPRESAS_FY_GAP.items():
        mask_gap = (maestro["id_empresa"] == eid) & (maestro["ROA"].isna())
        años_gap = maestro.loc[mask_gap, "año"].tolist()
        if años_gap:
            nota = f"yfinance sin datos financieros para {'/'.join(str(a) for a in años_gap)} (FY ends {fy_end}; balance_sheet cubre solo últimos 4 ejercicios)"
            maestro.loc[mask_gap, "nota"] = nota
            print(f"  Nota añadida: {eid} ({', '.join(str(a) for a in años_gap)})")

    maestro.to_csv(maestro_path, index=False)
    print(f"\n  [OK] empresas_muestra.csv → {len(maestro)} filas")

    # --- Paso 3: muestra_seleccionada.csv ---
    sel_path = EXTERNAL / "muestra_seleccionada.csv"
    sel = pd.read_csv(sel_path)
    sel = sel[sel["id_empresa"] != "E097"].copy()

    umg_row = {
        "ticker_wiki": UMG["ticker"],
        "nombre":      UMG["nombre"],
        "sector_icb":  UMG["sector_ICB"],
        "pais":        UMG["pais"],
        "sufijo":      ".AS",
        "ticker_yf":   UMG["ticker_yf"],
        "supersector": UMG["supersector"],
        "id_empresa":  UMG["id_empresa"],
    }
    # Añadir columnas que puedan faltar
    for col in sel.columns:
        if col not in umg_row:
            umg_row[col] = None

    sel = pd.concat([sel, pd.DataFrame([umg_row])], ignore_index=True)
    sel = sel.sort_values("id_empresa").reset_index(drop=True)
    sel.to_csv(sel_path, index=False)
    print(f"  [OK] muestra_seleccionada.csv → {len(sel)} empresas")

    # --- Paso 4: yfinance_datos.csv ---
    yf_path = EXTERNAL / "yfinance_datos.csv"
    yf_df = pd.read_csv(yf_path)
    yf_df = yf_df[yf_df["id_empresa"] != "E097"].copy()
    yf_df = pd.concat([yf_df, pd.DataFrame([datos_umg])], ignore_index=True)
    yf_df.to_csv(yf_path, index=False)
    print(f"  [OK] yfinance_datos.csv → {len(yf_df)} empresas")

    # --- Paso 5: tracking_descargas.csv ---
    track_path = EXTERNAL / "tracking_descargas.csv"
    track = pd.read_csv(track_path)
    track = track[track["id_empresa"] != "E097"].copy()

    track_rows = []
    for año in AÑOS:
        track_rows.append({
            "id_empresa":    UMG["id_empresa"],
            "empresa":       UMG["nombre"],
            "ticker":        UMG["ticker"],
            "pais":          UMG["pais"],
            "año":           año,
            "tipo_informe":  "",
            "url_fuente":    "",
            "fecha_descarga": "",
            "n_paginas":     "",
            "idioma":        "",
            "estado":        "pendiente",
            "notas":         "",
        })
    track = pd.concat([track, pd.DataFrame(track_rows)], ignore_index=True)
    track = track.sort_values(["id_empresa", "año"]).reset_index(drop=True)
    track.to_csv(track_path, index=False)
    print(f"  [OK] tracking_descargas.csv → {len(track)} filas")

    # --- Resumen final ---
    print("\n=== RESUMEN ===")
    maestro_final = pd.read_csv(maestro_path)
    nulls = maestro_final[maestro_final["ROA"].isna()]
    print(f"  Total filas: {len(maestro_final)}")
    print(f"  Filas con ROA nulo: {len(nulls)}")
    if not nulls.empty:
        print(f"  Empresas afectadas:")
        for _, r in nulls[["id_empresa","nombre","año","nota"]].iterrows():
            print(f"    {r['id_empresa']} {r['nombre']} {r['año']}: {r['nota'][:80]}")

    n_ok = maestro_final["ROA"].notna().sum()
    pct  = 100 * n_ok / len(maestro_final)
    print(f"\n  Cobertura ROA: {n_ok}/{len(maestro_final)} ({pct:.1f}%)")
    print(f"\n  Países (año 2024):")
    print(maestro_final[maestro_final["año"]==2024]["pais"].value_counts().to_string())


if __name__ == "__main__":
    main()
