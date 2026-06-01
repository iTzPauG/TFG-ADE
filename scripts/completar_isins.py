"""
completar_isins.py — Resolución automática de ISINs vía Wikidata SPARQL
-----------------------------------------------------------------------
Lee isins_pendientes.csv, consulta Wikidata para cada empresa y escribe
los ISINs encontrados en empresas_muestra.csv.

Fuente: Wikidata propiedad P946 (ISIN).
Cobertura esperada: ~70-85% de las empresas grandes del STOXX 600.

Uso:
  python scripts/completar_isins.py          # completa los pendientes
  python scripts/completar_isins.py --todos  # reintenta todas las empresas
"""

import sys
import time
from pathlib import Path

import pandas as pd
import requests

ROOT     = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "data" / "external"

WIKIDATA_URL = "https://query.wikidata.org/sparql"
HEADERS = {"User-Agent": "TFG-ADE-CSRD-Research/2.0 (pgesparterpubli@gmail.com)"}
SLEEP   = 1.2   # segundos entre queries (respeta rate limit de Wikidata)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _sparql_isin_exact(name: str) -> list[tuple[str, str]]:
    """Busca ISIN por label exacto en inglés."""
    query = f"""
    SELECT ?item ?itemLabel ?isin WHERE {{
      ?item rdfs:label "{name}"@en .
      ?item wdt:P946 ?isin .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }} LIMIT 5
    """
    return _run_sparql(query)


def _sparql_isin_contains(name: str) -> list[tuple[str, str]]:
    """Busca ISIN por substring del label en inglés."""
    # Escapar comillas simples para no romper SPARQL
    safe = name.replace('"', '\\"').replace("'", "\\'")
    query = f"""
    SELECT DISTINCT ?item ?itemLabel ?isin WHERE {{
      ?item wdt:P946 ?isin .
      ?item rdfs:label ?label .
      FILTER(LANG(?label) = "en")
      FILTER(CONTAINS(LCASE(?label), LCASE("{safe}")))
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }} LIMIT 5
    """
    return _run_sparql(query)


def _run_sparql(query: str) -> list[tuple[str, str]]:
    """Ejecuta una query SPARQL y devuelve lista de (label, isin)."""
    try:
        r = requests.get(
            WIKIDATA_URL,
            params={"query": query, "format": "json"},
            headers=HEADERS,
            timeout=20,
        )
        if r.status_code != 200:
            return []
        bindings = r.json().get("results", {}).get("bindings", [])
        return [
            (
                b.get("itemLabel", {}).get("value", ""),
                b.get("isin", {}).get("value", ""),
            )
            for b in bindings
            if b.get("isin", {}).get("value")
        ]
    except Exception:
        return []


def _mejor_isin(resultados: list[tuple[str, str]], nombre_buscado: str, pais: str) -> str | None:
    """
    Elige el ISIN más adecuado de entre los resultados de Wikidata.
    Preferencia:
      1. Label exacto (case-insensitive)
      2. Label que contiene el nombre buscado
      3. ISIN cuyo prefijo de país coincide con el país de la empresa
    Devuelve None si no hay resultados.
    """
    if not resultados:
        return None

    # Prefijos de país (ISO 3166-1 → prefijo ISIN)
    ISIN_PAIS = {
        "Germany": "DE", "France": "FR", "United Kingdom": "GB",
        "Spain": "ES", "Switzerland": "CH", "Sweden": "SE",
        "Netherlands": "NL", "Italy": "IT", "Denmark": "DK",
        "Norway": "NO", "Finland": "FI", "Belgium": "BE",
        "Ireland": "IE", "Austria": "AT", "Portugal": "PT",
    }
    pais_prefix = ISIN_PAIS.get(pais, "")

    nb_lower = nombre_buscado.lower().strip()

    # Puntuación: exact match > name contains > country prefix
    def score(label, isin):
        s = 0
        if label.lower().strip() == nb_lower:
            s += 100
        elif nb_lower in label.lower():
            s += 50
        if pais_prefix and isin.startswith(pais_prefix):
            s += 10
        return s

    ranked = sorted(resultados, key=lambda x: score(x[0], x[1]), reverse=True)
    return ranked[0][1]


def resolver_isin(nombre: str, pais: str, ticker: str) -> tuple[str | None, str]:
    """
    Intenta resolver el ISIN de una empresa usando Wikidata.
    Devuelve (isin, fuente) donde fuente es 'exact', 'contains' o 'not_found'.
    """
    # Intento 1: label exacto
    resultados = _sparql_isin_exact(nombre)
    time.sleep(SLEEP)
    if resultados:
        isin = _mejor_isin(resultados, nombre, pais)
        if isin:
            return isin, "exact"

    # Intento 2: substring match con nombre completo
    resultados = _sparql_isin_contains(nombre)
    time.sleep(SLEEP)
    if resultados:
        isin = _mejor_isin(resultados, nombre, pais)
        if isin:
            return isin, "contains"

    # Intento 3: nombre simplificado (primera palabra + segunda si existe)
    palabras = nombre.split()
    if len(palabras) >= 2:
        nombre_corto = " ".join(palabras[:2])
        resultados = _sparql_isin_contains(nombre_corto)
        time.sleep(SLEEP)
        if resultados:
            isin = _mejor_isin(resultados, nombre, pais)
            if isin:
                return isin, f"short:{nombre_corto}"

    return None, "not_found"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    todos = "--todos" in sys.argv

    pendientes_path = EXTERNAL / "isins_pendientes.csv"
    maestro_path    = EXTERNAL / "empresas_muestra.csv"

    if not pendientes_path.exists():
        print("No se encontró isins_pendientes.csv — nada que hacer.")
        return

    pendientes = pd.read_csv(pendientes_path)
    maestro    = pd.read_csv(maestro_path)

    if not todos:
        # Solo empresas que siguen sin ISIN en el maestro
        sin_isin_ids = set(
            maestro[maestro["ISIN"].isna()]["id_empresa"].unique()
        )
        pendientes = pendientes[pendientes["id_empresa"].isin(sin_isin_ids)]

    print(f"\n[ISINs] Resolviendo {len(pendientes)} empresas via Wikidata...")
    print(f"        (rate limit: {SLEEP}s/query × ~3 queries/empresa ≈ {len(pendientes)*3*SLEEP/60:.0f} min)\n")

    resultados = []
    for i, row in pendientes.iterrows():
        nombre = row["nombre"]
        pais   = row["pais"]
        ticker = row["ticker"]
        print(f"  [{i+1:02d}/{len(pendientes)}] {nombre:35s} ({pais})", end="", flush=True)

        isin, fuente = resolver_isin(nombre, pais, ticker)

        if isin:
            print(f" → {isin}  [{fuente}]")
        else:
            print(f" → NOT FOUND")

        resultados.append({
            "id_empresa": row["id_empresa"],
            "nombre":     nombre,
            "pais":       pais,
            "ticker":     ticker,
            "isin_wikidata": isin,
            "fuente":     fuente,
        })

    df_res = pd.DataFrame(resultados)
    encontrados = df_res[df_res["isin_wikidata"].notna()]
    print(f"\n  Encontrados: {len(encontrados)}/{len(pendientes)}")

    # Aplicar al maestro
    isin_map = dict(zip(encontrados["id_empresa"], encontrados["isin_wikidata"]))
    maestro["_isin_new"] = maestro["id_empresa"].map(isin_map)
    maestro["ISIN"] = maestro.apply(
        lambda r: r["_isin_new"] if pd.notna(r["_isin_new"]) else r["ISIN"],
        axis=1,
    )
    maestro.drop(columns=["_isin_new"], inplace=True)
    maestro.to_csv(maestro_path, index=False)

    # Actualizar isins_pendientes.csv con los que siguen sin resolver
    aun_sin = set(maestro[maestro["ISIN"].isna()]["id_empresa"].unique())
    pendientes_nuevo = pendientes[pendientes["id_empresa"].isin(aun_sin)].copy()
    pendientes_nuevo.to_csv(pendientes_path, index=False)

    # Resumen final
    n_con  = maestro["ISIN"].notna().nunique()   # filas con ISIN
    n_emp  = maestro["id_empresa"].nunique()
    n_con_emp = maestro[maestro["ISIN"].notna()]["id_empresa"].nunique()
    print(f"\n  Empresas con ISIN: {n_con_emp}/{n_emp}")
    print(f"  Sin ISIN (quedan en isins_pendientes.csv): {len(pendientes_nuevo)}")
    print(f"\n  Guardado en {maestro_path.relative_to(ROOT)}")

    if pendientes_nuevo.empty:
        print("\n  ✓ Todos los ISINs resueltos.")
    else:
        print("\n  Para los restantes, busca manualmente en:")
        print("    • Euronext: https://live.euronext.com  (busca por nombre o ticker)")
        print("    • Deutsche Börse: https://www.xetra.com")
        print("    • LSE: https://www.londonstockexchange.com")
        print("    • BME: https://www.bolsasymercados.es")
        print("    • SIX: https://www.six-group.com")
        print("  Rellena la col. 'isin_wikidata' en isins_pendientes.csv y vuelve a correr:")
        print("    python scripts/completar_isins.py --todos")


if __name__ == "__main__":
    main()
