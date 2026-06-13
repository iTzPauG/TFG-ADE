"""
Fase 2 — Corrección de duplicados Vinci y Bouygues en la muestra de 196
-------------------------------------------------------------------------
La sustitución de E112 (Decisión 027, "Saint-Gobain" duplicado → Vinci) introdujo
sin querer un duplicado: Vinci ya estaba en la muestra original como E018 (mismo
ticker `DG`, mismo ISIN real `FR0000125486`). Además, E116 (override de ticker
"BOUY"→ticker_yf `EN.PA`) resultó ser el mismo Bouygues que E019 (mismo ISIN
`FR001400UJU6`).

Esta corrección quirúrgica sustituye ambos, manteniendo el mismo sector ICB
(Construction and Materials):
  - E112 Vinci (Francia) → Heidelberg Materials (Alemania, ticker `HEI`)
  - E116 Bouygues (Francia) → Wienerberger (Austria, ticker `WIE`)

Adicionalmente, Castellum aparece dos veces en stoxx600_componentes.csv (ticker
`CAST` y `CASP`, mismo ticker_yf `CAST.ST`, mismo ISIN `SE0020202745`):
  - E061 Castellum (Suecia) — se mantiene.
  - E185 Castellum (Suecia) → LEG Immobilien (Alemania, ticker `LEG`, mismo
    sector Real Estate).

Y un cuarto duplicado: "Davide Campari-Milano" (E038) y "Gruppo Campari" (E194)
son la misma empresa (cambio de nombre en 2022), mismo ticker_yf `CPR.MI`:
  - E038 Davide Campari-Milano (Italia) — se mantiene.
  - E194 Gruppo Campari (Italia) → Lindt & Sprüngli (Suiza, ticker `LISN`, mismo
    sector Food, Beverage and Tobacco).

Re-descarga financieros yfinance para las 2 empresas afectadas y actualiza
muestra_seleccionada.csv, yfinance_datos.csv, empresas_muestra.csv y
tracking_descargas.csv.

Uso:
  python scripts/fase2_correccion_duplicados_vinci_bouygues.py
"""

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fase2_muestra as f2
from fase2_ampliacion import construir_filas_maestro

ROOT = f2.ROOT
EXTERNAL = f2.EXTERNAL
AÑOS = f2.AÑOS

# id_empresa -> nueva empresa (ticker_wiki, nombre, sector_icb, pais, sede)
SWAPS = {
    "E112": ("HEI", "Heidelberg Materials", "Construction and Materials", "Germany", "Heidelberg"),
    "E116": ("WIE", "Wienerberger",         "Construction and Materials", "Austria", "Vienna"),
    "E185": ("LEG",  "LEG Immobilien",       "Real Estate",                 "Germany",     "Düsseldorf"),
    "E194": ("LISN", "Lindt & Sprüngli",     "Food, Beverage and Tobacco",  "Switzerland", "Kilchberg"),
}


def main():
    muestra = pd.read_csv(EXTERNAL / "muestra_seleccionada.csv")

    print("[1/4] Aplicando 2 sustituciones de empresas...")
    for id_emp, (ticker_wiki, nombre, sector_icb, pais, sede) in SWAPS.items():
        idx = muestra.index[muestra["id_empresa"] == id_emp]
        assert len(idx) == 1, id_emp
        i = idx[0]
        old_nombre = muestra.at[i, "nombre"]
        muestra.at[i, "ticker_wiki"] = ticker_wiki
        muestra.at[i, "nombre"] = nombre
        muestra.at[i, "sector_icb"] = sector_icb
        muestra.at[i, "pais"] = pais
        muestra.at[i, "sede"] = sede
        print(f"    {id_emp}: {old_nombre!r} → {nombre!r} ({pais}, {sector_icb})")

    print("\n[2/4] Recalculando ticker_yf / supersector...")
    muestra = f2.aplicar_overrides_a_muestra(muestra)
    out_muestra = EXTERNAL / "muestra_seleccionada.csv"
    muestra.to_csv(out_muestra, index=False)
    print(f"    Guardado {out_muestra.relative_to(ROOT)}")

    ids_afectados = list(SWAPS.keys())
    afectadas = muestra[muestra["id_empresa"].isin(ids_afectados)].reset_index(drop=True)
    print(f"\n[3/4] Re-descargando financieros yfinance para {len(afectadas)} empresas...")

    registros = []
    for i, row in afectadas.iterrows():
        ticker = row["ticker_yf"]
        nombre_corto = row["nombre"][:30]
        print(f"    [{i+1}/{len(afectadas)}] {row['id_empresa']} {ticker:<12} {nombre_corto:<30}", end="", flush=True)
        datos = f2.obtener_financieros_empresa(ticker)
        datos.update({
            "id_empresa":  row["id_empresa"],
            "nombre":      row["nombre"],
            "ticker_wiki": row["ticker_wiki"],
            "pais":        row["pais"],
            "sector_icb":  row["sector_icb"],
            "supersector": row["supersector"],
            "nota":        f2.NOTAS_COBERTURA.get(row["ticker_wiki"], ""),
        })
        ok = "OK" if datos.get("market_cap") else "sin datos"
        n_años_ok = sum(1 for a in AÑOS if datos.get(f"ingresos_{a}") is not None)
        pct = (i + 1) / len(afectadas) * 100
        print(f" → {ok} ({n_años_ok}/{len(AÑOS)} años) [{pct:5.1f}%]")
        registros.append(datos)
        time.sleep(0.5)

    df_yf_nuevos = pd.DataFrame(registros)

    # --- yfinance_datos.csv: reemplazar filas de los ids afectados ---
    yf_path = EXTERNAL / "yfinance_datos.csv"
    yf = pd.read_csv(yf_path)
    yf = yf[~yf["id_empresa"].isin(ids_afectados)]
    yf = pd.concat([yf, df_yf_nuevos], ignore_index=True)
    yf.to_csv(yf_path, index=False)
    print(f"\n✓ {yf_path.relative_to(ROOT)} actualizado ({len(yf)} filas)")

    # --- empresas_muestra.csv: reemplazar filas (3/empresa) de los ids afectados ---
    print("\n[4/4] Reconstruyendo filas del panel maestro y tracking...")
    em_path = EXTERNAL / "empresas_muestra.csv"
    em = pd.read_csv(em_path)
    em = em[~em["id_empresa"].isin(ids_afectados)]
    nuevas_filas = construir_filas_maestro(afectadas, df_yf_nuevos)
    em = pd.concat([em, nuevas_filas], ignore_index=True)
    em = em.sort_values(["id_empresa", "año"]).reset_index(drop=True)
    em.to_csv(em_path, index=False)
    print(f"✓ {em_path.relative_to(ROOT)} actualizado ({len(em)} filas, {em['id_empresa'].nunique()} empresas)")

    # --- tracking_descargas.csv: actualizar empresa/ticker/pais y resetear estado ---
    tr_path = EXTERNAL / "tracking_descargas.csv"
    tr = pd.read_csv(tr_path)
    for id_emp in SWAPS:
        row = afectadas[afectadas["id_empresa"] == id_emp].iloc[0]
        mask = tr["id_empresa"] == id_emp
        tr.loc[mask, "empresa"] = row["nombre"]
        tr.loc[mask, "ticker"] = row["ticker_wiki"]
        tr.loc[mask, "pais"] = row["pais"]
        tr.loc[mask, "estado"] = "pendiente"
        tr.loc[mask, "url_fuente"] = ""
        tr.loc[mask, "fecha_descarga"] = ""
        tr.loc[mask, "n_paginas"] = float("nan")
        tr.loc[mask, "idioma"] = ""
        tr.loc[mask, "notas"] = "sustituye duplicado (ver docs/decisiones.md)"
    tr.to_csv(tr_path, index=False)
    print(f"✓ {tr_path.relative_to(ROOT)} actualizado (empresa/ticker/país de las {len(SWAPS)} sustituciones, estado→pendiente)")

    sin_datos = df_yf_nuevos[df_yf_nuevos["market_cap"].isna()]
    print(f"\n=== RESUMEN ===")
    print(f"Empresas corregidas: {len(afectadas)}")
    if len(sin_datos):
        print(f"AVISO — {len(sin_datos)} siguen sin datos financieros:")
        print(sin_datos[["id_empresa", "nombre", "ticker_yf"]].to_string(index=False))
    else:
        print("Todas con datos financieros completos.")


if __name__ == "__main__":
    main()
