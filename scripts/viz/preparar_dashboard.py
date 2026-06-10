"""
Fase 6 — Precálculo de tablas ligeras para el dashboard Streamlit.

Combina las salidas de 5A/5C/5E en un único panel por documento (289 filas, sección `sus`)
y agrega la asignación de tópicos BERTopic a nivel documento (a partir del parquet de
párrafos, demasiado pesado para cargar en la app).

Outputs en results/tables/dashboard/:
  - panel.csv              — panel maestro 289 docs (GW_index, sentimiento, ESRS, ESG-9, financieros)
  - bertopic_doc_topics.csv — topic dominante (excluyendo outlier -1) y su share por documento

Uso:
  conda run -n tfg-ade python scripts/viz/preparar_dashboard.py
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "results" / "tables"
OUT = TABLES / "dashboard"
OUT.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    print(f"[preparar_dashboard] {msg}")


def construir_panel() -> pd.DataFrame:
    log("[1/2] Construyendo panel maestro (5e_panel + 5a_cobertura_esrs + 5c_esg9)…")

    panel = pd.read_csv(TABLES / "5e_panel.csv")
    esrs = pd.read_csv(TABLES / "5a_cobertura_esrs.csv")
    esg9_cols = [c for c in pd.read_csv(TABLES / "5c_doc_agregado.csv", nrows=0).columns
                  if c.startswith("esg9_")]
    esg9 = pd.read_csv(TABLES / "5c_doc_agregado.csv", usecols=["doc_id"] + esg9_cols)

    esrs_cols = ["E1", "E2", "E3", "E4", "E5", "S1", "S2", "S3", "S4", "G1", "ESRS2"]
    esrs_subset = esrs[["id"] + esrs_cols].rename(columns={"id": "doc_id"})

    panel = panel.merge(esrs_subset, on="doc_id", how="left")
    panel = panel.merge(esg9, on="doc_id", how="left")

    log(f"  → panel: {panel.shape[0]} filas × {panel.shape[1]} columnas")
    return panel


def construir_bertopic_doc() -> pd.DataFrame:
    log("[2/2] Agregando topic dominante BERTopic por documento (puede tardar ~30s)…")

    bt = pd.read_parquet(TABLES / "5b_bertopic_para_topics.parquet",
                          columns=["doc_id", "topic"])

    rows = []
    docs = bt["doc_id"].unique()
    n = len(docs)
    for i, (doc_id, grp) in enumerate(bt.groupby("doc_id")):
        total = len(grp)
        sin_outlier = grp[grp["topic"] != -1]
        if len(sin_outlier):
            top = sin_outlier["topic"].value_counts().index[0]
            share = (sin_outlier["topic"] == top).sum() / total
        else:
            top, share = -1, 0.0
        outlier_share = (grp["topic"] == -1).sum() / total
        rows.append({
            "doc_id": doc_id,
            "n_parrafos": total,
            "topic_dominante": int(top),
            "topic_dominante_share": round(share, 4),
            "outlier_share": round(outlier_share, 4),
        })
        if (i + 1) % 50 == 0 or (i + 1) == n:
            pct = (i + 1) / n * 100
            print(f"  [{i+1:>3}/{n}] {pct:5.1f}%", end="\r")
    print()

    df = pd.DataFrame(rows)
    log(f"  → bertopic_doc_topics: {df.shape[0]} filas")
    return df


def main():
    panel = construir_panel()
    panel.to_csv(OUT / "panel.csv", index=False)
    log(f"Guardado {OUT / 'panel.csv'}")

    bt_doc = construir_bertopic_doc()
    bt_doc.to_csv(OUT / "bertopic_doc_topics.csv", index=False)
    log(f"Guardado {OUT / 'bertopic_doc_topics.csv'}")

    log("✓ Completo")


if __name__ == "__main__":
    main()
