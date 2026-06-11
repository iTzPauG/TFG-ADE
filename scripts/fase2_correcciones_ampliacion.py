"""
Fase 2 — Correcciones puntuales tras la ampliación a 196 (Decisión 027)
------------------------------------------------------------------------
Tras `fase2_ampliacion.py`, 27/99 empresas nuevas quedaron sin datos financieros
yfinance. Esta corrección quirúrgica:

  1. Sustituye 5 empresas problemáticas por alternativas (mismo hueco de
     sector/país en lo posible):
       - E112 Saint-Gobain (ticker "SGOB", entrada duplicada de Wikipedia;
         "SGO" ya está en E114) → Vinci (Construction & Materials, Francia)
       - E123 Lundin Energy (fusionada en Aker BP a finales de 2022, deja de
         existir como entidad para 2023-2024) → Eni (Energy, Italia)
       - E145 Direct Line (sin cobertura yfinance) → Legal & General
         (Insurance, Reino Unido)
       - E147 Schibsted (sin cobertura yfinance, igual que Decisión 005 en la
         muestra original) → Storebrand (Insurance, Noruega) — a petición del
         usuario, mantiene Noruega
       - E159 Just Eat Takeaway (sin cobertura yfinance) → Zalando (Retail,
         Alemania)

  2. Re-aplica TICKER_OVERRIDES (22 nuevos, añadidos a fase2_muestra.py) sobre
     las 22 empresas restantes que solo tenían el ticker yfinance incorrecto
     (p.ej. Michelin MICP→ML.PA, Sanofi SNY→SAN.PA, Novartis "NOV N"→NOVN.SW...).

  3. Re-descarga financieros yfinance para las 27 empresas afectadas y actualiza
     yfinance_datos.csv, empresas_muestra.csv y tracking_descargas.csv.

Uso:
  python scripts/fase2_correcciones_ampliacion.py
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
    "E112": ("DG",   "Vinci",           "Construction and Materials", "France",         "Rueil-Malmaison"),
    "E123": ("ENI",  "Eni",             "Energy",                      "Italy",          "Rome"),
    "E145": ("LGEN", "Legal & General", "Insurance",                   "United Kingdom", "London"),
    "E147": ("SRB",  "Storebrand",      "Insurance",                   "Norway",         "Oslo"),
    "E159": ("ZAL",  "Zalando",         "Retail",                      "Germany",        "Berlin"),
}

# ids cuyo ticker_yf cambia solo por TICKER_OVERRIDES (ver fase2_muestra.py)
IDS_OVERRIDE = [
    "E098", "E100", "E101", "E105", "E108", "E116", "E119", "E125", "E126",
    "E130", "E132", "E133", "E134", "E144", "E150", "E157", "E164", "E165",
    "E185", "E191", "E194", "E195",
]


def main():
    muestra = pd.read_csv(EXTERNAL / "muestra_seleccionada.csv")

    print("[1/4] Aplicando 5 sustituciones de empresas...")
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

    print("\n[2/4] Recalculando ticker_yf / supersector con TICKER_OVERRIDES actualizados...")
    muestra = f2.aplicar_overrides_a_muestra(muestra)
    out_muestra = EXTERNAL / "muestra_seleccionada.csv"
    muestra.to_csv(out_muestra, index=False)
    print(f"    Guardado {out_muestra.relative_to(ROOT)}")

    ids_afectados = list(SWAPS.keys()) + IDS_OVERRIDE
    afectadas = muestra[muestra["id_empresa"].isin(ids_afectados)].reset_index(drop=True)
    print(f"\n[3/4] Re-descargando financieros yfinance para {len(afectadas)} empresas...")

    registros = []
    for i, row in afectadas.iterrows():
        ticker = row["ticker_yf"]
        nombre_corto = row["nombre"][:30]
        print(f"    [{i+1:02d}/{len(afectadas)}] {row['id_empresa']} {ticker:<12} {nombre_corto:<30}", end="", flush=True)
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

    # --- tracking_descargas.csv: actualizar empresa/ticker para las 5 sustituciones ---
    tr_path = EXTERNAL / "tracking_descargas.csv"
    tr = pd.read_csv(tr_path)
    for id_emp in SWAPS:
        row = afectadas[afectadas["id_empresa"] == id_emp].iloc[0]
        mask = tr["id_empresa"] == id_emp
        tr.loc[mask, "empresa"] = row["nombre"]
        tr.loc[mask, "ticker"] = row["ticker_wiki"]
        tr.loc[mask, "pais"] = row["pais"]
    tr.to_csv(tr_path, index=False)
    print(f"✓ {tr_path.relative_to(ROOT)} actualizado (empresa/ticker/país de las {len(SWAPS)} sustituciones)")

    sin_datos = df_yf_nuevos[df_yf_nuevos["market_cap"].isna()]
    print(f"\n=== RESUMEN ===")
    print(f"Empresas corregidas: {len(afectadas)} ({len(SWAPS)} sustituidas + {len(IDS_OVERRIDE)} con ticker corregido)")
    if len(sin_datos):
        print(f"AVISO — {len(sin_datos)} siguen sin datos financieros:")
        print(sin_datos[["id_empresa", "nombre", "ticker_yf"]].to_string(index=False))
    else:
        print("Todas con datos financieros completos.")


if __name__ == "__main__":
    main()
