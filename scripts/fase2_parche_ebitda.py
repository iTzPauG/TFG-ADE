"""
fase2_parche_ebitda.py — Rellena EBITDA faltante en empresas_muestra.csv
-------------------------------------------------------------------------
Problema: yfinance no devuelve el campo "EBITDA" directo para entidades
financieras (bancos, seguros, servicios financieros) porque su estructura
de cuenta de resultados es distinta a la de empresas industriales.

Solución: cascada de cómputo con trazabilidad de fuente.
  1. "EBITDA"                         — campo directo (preferido)
  2. "Normalized EBITDA"              — variante Yahoo Finance
  3. "EBIT" + "Reconciled Depreciation"
  4. "Operating Income" + "Reconciled Depreciation"
  5. "Pretax Income"  + "Reconciled Depreciation"  — proxy para financieras

La fuente usada se guarda en la columna `fuente_ebitda` del dataset maestro.
Los 4 gaps de FY2022 por año fiscal no-diciembre no se tocan (ROA también NaN).

Uso:
  python scripts/fase2_parche_ebitda.py
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

CASCADA_KEYS = [
    ("EBITDA",                                         "direct"),
    ("Normalized EBITDA",                              "normalized"),
]
CASCADA_COMPUESTA = [
    ("EBIT",            "Reconciled Depreciation", "ebit+da"),
    ("Operating Income","Reconciled Depreciation", "oi+da"),
    ("Pretax Income",   "Reconciled Depreciation", "pretax+da"),
]
# Evitar cadenas que pandas convierte a NaN al leer CSV ("n/a", "NA", etc.)
FUENTE_SIN_DATOS = "sin_datos"


def _val(series: pd.Series, key: str):
    v = series.get(key)
    try:
        return float(v) if pd.notna(v) else None
    except (TypeError, ValueError):
        return None


def calcular_ebitda_cascada(inc_s: pd.Series) -> tuple[float | None, str]:
    """Devuelve (valor, fuente) usando la cascada definida arriba."""
    for key, fuente in CASCADA_KEYS:
        v = _val(inc_s, key)
        if v is not None:
            return v, fuente

    da = _val(inc_s, "Reconciled Depreciation")
    if da is not None:
        for key_a, key_b, fuente in CASCADA_COMPUESTA:
            a = _val(inc_s, key_a)
            if a is not None:
                return a + da, fuente

    return None, FUENTE_SIN_DATOS


def parche_empresa(ticker_yf: str, años_faltantes: list[int]) -> dict[int, tuple]:
    """
    Descarga income_stmt y devuelve {año: (ebitda, fuente)} solo para años con EBITDA nulo
    (excluye años sin datos financieros en absoluto, p.ej. gaps FY2022).
    """
    resultado = {}
    try:
        t = yf.Ticker(ticker_yf)
        inc = t.income_stmt
        for año in años_faltantes:
            col = next((c for c in inc.columns if hasattr(c, "year") and c.year == año), None)
            if col is None:
                resultado[año] = (None, "sin_columna")
                continue
            inc_s = inc[col]
            # Si no hay ningún dato financiero (gap FY), skip
            if inc_s.isna().all():
                resultado[año] = (None, "gap_fy")
                continue
            v, fuente = calcular_ebitda_cascada(inc_s)
            resultado[año] = (v, fuente)
    except Exception as e:
        for año in años_faltantes:
            resultado[año] = (None, f"error: {e}")
    return resultado


def main():
    print("\n=== Parche EBITDA — Fase 2 ===\n")

    maestro_path = EXTERNAL / "empresas_muestra.csv"
    df = pd.read_csv(maestro_path)

    # Columna de trazabilidad (inicializar si no existe)
    if "fuente_ebitda" not in df.columns:
        df["fuente_ebitda"] = ""
    # Marcar como 'direct' las filas que ya tienen EBITDA y sin fuente anotada
    mask_ok = df["ebitda"].notna() & (df["fuente_ebitda"].isna() | (df["fuente_ebitda"] == ""))
    df.loc[mask_ok, "fuente_ebitda"] = "direct"

    # Identificar empresas y años con EBITDA nulo
    mask_nulo = df["ebitda"].isna()
    empresas_nulas = (
        df[mask_nulo]
        .groupby(["id_empresa", "nombre", "ticker_yf"])["año"]
        .apply(list)
        .reset_index()
    )

    print(f"Empresas con EBITDA nulo: {len(empresas_nulas)}")
    for _, r in empresas_nulas.iterrows():
        print(f"  {r['id_empresa']} {r['nombre']:<35} años={r['año']}")

    print()
    resumen = []
    for _, row in empresas_nulas.iterrows():
        eid       = row["id_empresa"]
        nombre    = row["nombre"]
        ticker_yf = row["ticker_yf"]
        años_nulos = row["año"]

        # Excluir años sin datos financieros en absoluto (gap FY: ROA también NaN)
        años_sin_datos = df[(df["id_empresa"] == eid) & df["ROA"].isna()]["año"].tolist()
        años_a_reparar = [a for a in años_nulos if a not in años_sin_datos]

        # Marcar siempre los años sin datos financieros como gap_fy
        for año in años_sin_datos:
            if año in años_nulos:
                mask = (df["id_empresa"] == eid) & (df["año"] == año)
                df.loc[mask, "fuente_ebitda"] = "gap_fy"

        print(f"[{eid}] {nombre} ({ticker_yf})", end="")
        if not años_a_reparar:
            print(" → solo gaps FY sin datos financieros, se omite")
            continue
        print(f" — reparando años {años_a_reparar}...")

        resultado = parche_empresa(ticker_yf, años_a_reparar)
        time.sleep(0.5)

        for año, (valor, fuente) in resultado.items():
            mask = (df["id_empresa"] == eid) & (df["año"] == año)
            if valor is not None:
                df.loc[mask, "ebitda"]       = valor
                df.loc[mask, "fuente_ebitda"] = fuente
                print(f"    FY{año}: {valor:,.0f}  [{fuente}]")
            else:
                df.loc[mask, "fuente_ebitda"] = fuente
                print(f"    FY{año}: n/a  [{fuente}]")
            resumen.append({"empresa": nombre, "año": año, "ebitda": valor, "fuente": fuente})

    df.to_csv(maestro_path, index=False)
    print(f"\n[OK] empresas_muestra.csv actualizado — {len(df)} filas")

    # Resumen final
    print("\n=== RESUMEN ===")
    print(f"  EBITDA nulos restantes: {df['ebitda'].isna().sum()}")
    print(f"  Fuentes usadas:")
    print(df["fuente_ebitda"].value_counts().to_string())
    print()

    cobertura_año = {}
    for año in AÑOS:
        sub = df[df["año"] == año]
        n_ok = sub["ebitda"].notna().sum()
        n_tot = len(sub)
        cobertura_año[año] = (n_ok, n_tot)
        print(f"  EBITDA {año}: {n_ok}/{n_tot} ({100*n_ok/n_tot:.0f}%)")


if __name__ == "__main__":
    main()
