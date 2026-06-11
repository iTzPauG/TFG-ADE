"""
Fase 2 — Ampliación de la muestra de 97 a ~200 empresas (Decisión 027)
------------------------------------------------------------------------
Amplía la muestra estratificada existente (97 empresas, Decisión 002) a un
objetivo de N_OBJETIVO=200, **conservando intactas las 97 originales**
(mismo id_empresa, mismas filas) y añadiendo nuevas empresas hasta completar
la cuota de 10/sector ICB (200 / 20 sectores), con cap geográfico CAP_PAIS_N=30
(15% de 200, misma proporción que el cap original de 15/100).

Pasos:
  1. Carga `stoxx600_componentes.csv` (universo) y `muestra_seleccionada.csv` (97 actuales).
  2. Para cada sector ICB, calcula el déficit respecto a la cuota de 10 y muestrea
     nuevas empresas (sin repetir, excluyendo TICKERS_EXCLUIDOS) con random_state=42.
  3. Cubre déficits de sectores con pocas empresas disponibles (p.ej. Personal Care,
     Drug & Grocery Stores) con extras del resto del pool.
  4. Aplica el cap geográfico SOLO sobre las empresas nuevas (nunca sobre las 97
     originales) — si un país supera el cap, sustituye el exceso de las nuevas por
     candidatas de otros países del mismo sector.
  5. Asigna id_empresa correlativos E098...E2xx a las nuevas.
  6. Descarga financieros yfinance SOLO para las nuevas (las 97 ya están en
     yfinance_datos.csv) y los añade (append).
  7. Reconstruye empresas_muestra.csv (panel año×empresa) añadiendo las nuevas filas
     a las 291 existentes.
  8. Añade filas "pendiente" a tracking_descargas.csv para las nuevas (Fase 3).

Uso:
  python scripts/fase2_ampliacion.py             # ejecuta todo
  python scripts/fase2_ampliacion.py --dry-run   # solo calcula y muestra la selección, no descarga ni guarda
"""

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fase2_muestra as f2  # reutiliza overrides, supersectores, excluidos, descarga financiera

ROOT = f2.ROOT
EXTERNAL = f2.EXTERNAL

N_OBJETIVO = 200
CAP_PAIS_N = 30
RANDOM_STATE = f2.RANDOM_STATE  # 42
AÑOS = f2.AÑOS


def seleccionar_nuevas(stoxx: pd.DataFrame, actuales: pd.DataFrame) -> pd.DataFrame:
    print("\n[1/4] Seleccionando empresas nuevas para ampliar la muestra...")

    stoxx = f2.construir_ticker_yfinance(stoxx)
    stoxx["supersector"] = stoxx["sector_icb"].map(f2.SUPERSECTORES).fillna(stoxx["sector_icb"])

    pool = stoxx[~stoxx["ticker_wiki"].isin(f2.TICKERS_EXCLUIDOS)].copy()
    pool = pool[~pool["ticker_wiki"].isin(actuales["ticker_wiki"])].copy()
    pool = pool.drop_duplicates(subset=["ticker_wiki", "pais"]).reset_index(drop=True)

    sectores = sorted(stoxx["sector_icb"].unique())
    n_sectores = len(sectores)
    k_base = N_OBJETIVO // n_sectores
    resto = N_OBJETIVO - k_base * n_sectores

    nuevas_frames = []
    deficit = 0
    for i, sector in enumerate(sectores):
        cuota = k_base + (1 if i < resto else 0)
        n_actuales_sector = int((actuales["sector_icb"] == sector).sum())
        need = max(0, cuota - n_actuales_sector)
        if need == 0:
            continue
        sub = pool[pool["sector_icb"] == sector]
        disponibles = len(sub)
        if disponibles < need:
            print(f"    AVISO — '{sector}': solo {disponibles} disponibles (necesarias {need})")
            deficit += need - disponibles
            need = disponibles
        if need == 0:
            continue
        sel = sub.sample(n=need, random_state=RANDOM_STATE)
        nuevas_frames.append(sel)
        pool = pool[~pool["ticker_wiki"].isin(sel["ticker_wiki"])]

    nuevas = pd.concat(nuevas_frames).reset_index(drop=True) if nuevas_frames else pd.DataFrame(columns=pool.columns)

    if deficit > 0:
        n_extra = min(deficit, len(pool))
        extras = pool.sample(n=n_extra, random_state=RANDOM_STATE + 1)
        print(f"    Déficit de {deficit} cubierto con {n_extra} empresa(s) adicionale(s) de otros sectores")
        nuevas = pd.concat([nuevas, extras]).reset_index(drop=True)
        pool = pool[~pool["ticker_wiki"].isin(extras["ticker_wiki"])]

    nuevas = nuevas.drop_duplicates(subset=["ticker_wiki", "pais"]).reset_index(drop=True)

    # --- Cap geográfico: solo se ajustan las NUEVAS, nunca las 97 originales ---
    print(f"\n[2/4] Aplicando cap geográfico (cap={CAP_PAIS_N}, solo sobre empresas nuevas)...")
    rs_offset = 5
    for ronda in range(10):
        combinado = pd.concat([actuales[["pais"]], nuevas[["pais"]]])
        counts = combinado["pais"].value_counts()
        exceso_paises = counts[counts > CAP_PAIS_N].index.tolist()
        if not exceso_paises:
            break
        pais = counts[exceso_paises].idxmax()
        exceso_n = int(counts[pais]) - CAP_PAIS_N
        en_nuevas_pais = nuevas[nuevas["pais"] == pais]
        n_quitar = min(exceso_n, len(en_nuevas_pais))
        if n_quitar == 0:
            print(f"    AVISO — {pais} supera el cap ({int(counts[pais])}>{CAP_PAIS_N}) "
                  f"solo por empresas de la muestra original; no se modifica.")
            break
        a_quitar = en_nuevas_pais.sample(n=n_quitar, random_state=RANDOM_STATE + rs_offset)
        nuevas = nuevas[~nuevas.index.isin(a_quitar.index)].copy()

        ya = set(actuales["ticker_wiki"]) | set(nuevas["ticker_wiki"])
        reemplazos = []
        for sector in a_quitar["sector_icb"].unique():
            n_need = int((a_quitar["sector_icb"] == sector).sum())
            counts_actual = pd.concat([actuales[["pais"]], nuevas[["pais"]]])["pais"].value_counts()
            candidatos = pool[
                (pool["sector_icb"] == sector) &
                (~pool["ticker_wiki"].isin(ya)) &
                (~pool["pais"].isin(counts_actual[counts_actual >= CAP_PAIS_N].index))
            ]
            tomar = min(n_need, len(candidatos))
            if tomar > 0:
                sel = candidatos.sample(n=tomar, random_state=RANDOM_STATE + rs_offset + 1)
                reemplazos.append(sel)
                ya.update(sel["ticker_wiki"].tolist())
                pool = pool[~pool["ticker_wiki"].isin(sel["ticker_wiki"])]

        if reemplazos:
            nuevas = pd.concat([nuevas] + reemplazos).reset_index(drop=True)

        nuevo_count = int((pd.concat([actuales[["pais"]], nuevas[["pais"]]])["pais"] == pais).sum())
        print(f"    Cap {pais}: {int(counts[pais])} → {nuevo_count} empresas")
        rs_offset += 10

    # --- Asignar id_empresa correlativos a partir del último existente ---
    ultimo_n = max(int(x[1:]) for x in actuales["id_empresa"])
    nuevas = nuevas.reset_index(drop=True)
    nuevas["id_empresa"] = [f"E{ultimo_n + i + 1:03d}" for i in range(len(nuevas))]

    print(f"\n[3/4] Resumen de la ampliación:")
    print(f"    Muestra original:  {len(actuales)} empresas")
    print(f"    Empresas nuevas:   {len(nuevas)} empresas")
    print(f"    Total:             {len(actuales) + len(nuevas)} empresas")
    print(f"\n    Distribución por sector ICB (cuota objetivo: {k_base}/sector):")
    combinado = pd.concat([actuales, nuevas])
    print(combinado["sector_icb"].value_counts().sort_index().to_string())
    print(f"\n    Distribución por país (cap={CAP_PAIS_N}):")
    print(combinado["pais"].value_counts().to_string())
    print(f"\n    Distribución por supersector:")
    print(combinado["supersector"].value_counts().to_string())

    return nuevas


def descargar_financieros_nuevas(nuevas: pd.DataFrame) -> pd.DataFrame:
    print(f"\n[4/4] Descargando datos yfinance para {len(nuevas)} empresas nuevas...")
    registros = []
    for i, row in nuevas.iterrows():
        ticker = row["ticker_yf"]
        nombre_corto = row["nombre"][:30]
        print(f"    [{i+1:03d}/{len(nuevas)}] {ticker:<16} {nombre_corto:<30}", end="", flush=True)

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
        pct = (i + 1) / len(nuevas) * 100
        print(f" → {ok} ({n_años_ok}/{len(AÑOS)} años financieros) [{pct:5.1f}%]")
        registros.append(datos)
        time.sleep(0.5)

    return pd.DataFrame(registros)


def construir_filas_maestro(nuevas: pd.DataFrame, df_yf: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for _, row_m in nuevas.iterrows():
        row_yf = df_yf[df_yf["id_empresa"] == row_m["id_empresa"]]
        if row_yf.empty:
            continue
        row_yf = row_yf.iloc[0]
        for año in AÑOS:
            fila = {
                "id_empresa":    row_m["id_empresa"],
                "nombre":        row_m["nombre"],
                "ticker":        row_m["ticker_wiki"],
                "ticker_yf":     row_m["ticker_yf"],
                "ISIN":          row_yf.get("ISIN"),
                "pais":          row_m["pais"],
                "sector_ICB":    row_m["sector_icb"],
                "supersector":   row_m["supersector"],
                "año":           año,
                "capitalización": row_yf.get("market_cap"),
                "moneda":         row_yf.get("moneda"),
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
                "sector_yf":    row_yf.get("sector_yf"),
                "industria_yf": row_yf.get("industria_yf"),
                "pais_yf":      row_yf.get("pais_yf"),
                "nota":         row_yf.get("nota", ""),
                "error_yf":     row_yf.get("error"),
            }
            filas.append(fila)
    return pd.DataFrame(filas)


def generar_tracking_nuevas(nuevas: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for _, row in nuevas.iterrows():
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
    return pd.DataFrame(filas)


def main():
    dry_run = "--dry-run" in sys.argv

    stoxx = pd.read_csv(EXTERNAL / "stoxx600_componentes.csv")
    actuales = pd.read_csv(EXTERNAL / "muestra_seleccionada.csv")

    nuevas = seleccionar_nuevas(stoxx, actuales)

    if dry_run:
        print("\n--dry-run: no se descarga ni se guarda nada.")
        print(nuevas[["id_empresa", "nombre", "ticker_wiki", "pais", "sector_icb"]].to_string(index=False))
        return

    # 1) muestra_seleccionada.csv ampliada
    muestra_completa = pd.concat([actuales, nuevas[actuales.columns]], ignore_index=True)
    out_muestra = EXTERNAL / "muestra_seleccionada.csv"
    muestra_completa.to_csv(out_muestra, index=False)
    print(f"\n✓ {out_muestra.relative_to(ROOT)} ampliado a {len(muestra_completa)} empresas")

    # 2) yfinance_datos.csv: append de las nuevas
    df_yf_nuevas = descargar_financieros_nuevas(nuevas)
    yf_path = EXTERNAL / "yfinance_datos.csv"
    yf_actual = pd.read_csv(yf_path)
    yf_completo = pd.concat([yf_actual, df_yf_nuevas], ignore_index=True)
    yf_completo.to_csv(yf_path, index=False)
    print(f"✓ {yf_path.relative_to(ROOT)} ampliado a {len(yf_completo)} empresas")
    n_ok = df_yf_nuevas["market_cap"].notna().sum()
    print(f"  Nuevas con market_cap: {n_ok}/{len(df_yf_nuevas)}")

    # 3) empresas_muestra.csv: append de las nuevas filas (empresa x año)
    nuevas_filas = construir_filas_maestro(nuevas, df_yf_nuevas)
    em_path = EXTERNAL / "empresas_muestra.csv"
    em_actual = pd.read_csv(em_path)
    em_completo = pd.concat([em_actual, nuevas_filas], ignore_index=True)
    em_completo.to_csv(em_path, index=False)
    print(f"✓ {em_path.relative_to(ROOT)} ampliado a {len(em_completo)} filas "
          f"({em_completo['id_empresa'].nunique()} empresas x {len(AÑOS)} años)")

    # 4) tracking_descargas.csv: append "pendiente" para las nuevas
    tracking_nuevas = generar_tracking_nuevas(nuevas)
    tr_path = EXTERNAL / "tracking_descargas.csv"
    tr_actual = pd.read_csv(tr_path)
    tr_completo = pd.concat([tr_actual, tracking_nuevas], ignore_index=True)
    tr_completo.to_csv(tr_path, index=False)
    print(f"✓ {tr_path.relative_to(ROOT)} ampliado a {len(tr_completo)} filas "
          f"({len(tracking_nuevas)} nuevas pendientes)")

    print(f"\n=== RESUMEN ===")
    print(f"Empresas totales: {muestra_completa['id_empresa'].nunique()} "
          f"({len(actuales)} originales + {len(nuevas)} nuevas)")
    sin_cap = df_yf_nuevas[df_yf_nuevas["market_cap"].isna()]
    if len(sin_cap):
        print(f"AVISO — {len(sin_cap)} empresas nuevas sin datos financieros yfinance:")
        print(sin_cap[["id_empresa", "nombre", "ticker_yf"]].to_string(index=False))


if __name__ == "__main__":
    main()
