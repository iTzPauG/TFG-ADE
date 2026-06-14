"""
Fase 6 — Genera el dashboard estático (HTML + JS, Plotly.js vía CDN).

Lee las tablas ligeras de results/tables/ (y results/tables/dashboard/, generadas por
preparar_dashboard.py) y produce un único fichero results/dashboard/index.html,
autocontenido salvo por las imágenes de results/figures/ (referenciadas con ruta relativa
../figures/) y la librería Plotly.js (CDN).

Uso:
  conda run -n tfg-ade python scripts/viz/preparar_dashboard.py   # si no existe results/tables/dashboard/
  conda run -n tfg-ade python scripts/viz/build_dashboard.py

Despliegue local: abrir results/dashboard/index.html en el navegador, o servir la carpeta
results/ con un servidor estático (p.ej. `python -m http.server` desde la raíz del repo).
"""

import json
import math
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "results" / "tables"
DASHBOARD_TABLES = TABLES / "dashboard"
OUT_DIR = ROOT / "results" / "dashboard"
TEMPLATES = Path(__file__).resolve().parent / "templates"

ESRS_COLS = ["E1", "E2", "E3", "E4", "E5", "S1", "S2", "S3", "S4", "G1", "ESRS2"]
ESG9_COLS = [
    "esg9_business_ethics_and_values", "esg9_climate_change", "esg9_community_relations",
    "esg9_corporate_governance", "esg9_human_capital", "esg9_natural_capital",
    "esg9_non-esg", "esg9_pollution_and_waste", "esg9_product_liability",
]

LDA_ESRS_MAP = {
    "T06": "E1 — Cambio climático", "T02": "E2-E4 — Contaminación/Recursos/Biodiversidad",
    "T13": "E5 — Economía circular", "T00": "S1 — Plantilla propia",
    "T04": "S2-S3 — Cadena de valor/Comunidades", "T08": "G1 — Conducta empresarial",
    "T05": "CSRD genérico", "T09": "CSRD genérico", "T11": "CSRD genérico",
}

N_BERTOPIC_TOP = 40


def log(msg: str) -> None:
    print(f"[build_dashboard] {msg}")


def cargar_datos() -> dict:
    log("[1/3] Cargando tablas…")

    panel = pd.read_csv(DASHBOARD_TABLES / "panel.csv")
    bt_doc = pd.read_csv(DASHBOARD_TABLES / "bertopic_doc_topics.csv")

    desc = pd.read_csv(TABLES / "5a_descriptivos_corpus.csv")
    cov_anio = pd.read_csv(TABLES / "5a_cobertura_esrs_año.csv")

    lda_topics = pd.read_csv(TABLES / "5b_lda_topics.csv")
    lda_topics["topic_id"] = lda_topics["topic"].apply(lambda t: f"T{int(t):02d}")
    lda_topics["mapeo_ESRS"] = lda_topics["topic_id"].map(LDA_ESRS_MAP).fillna("—")
    lda_coherencia = pd.read_csv(TABLES / "5b_lda_coherencia.csv")

    bt_topics = pd.read_csv(TABLES / "5b_bertopic_topics.csv",
                             usecols=["Topic", "Count", "Name", "Representation"])
    bt_top = bt_topics[bt_topics["Topic"] != -1].sort_values("Count", ascending=False).head(N_BERTOPIC_TOP)
    bt_all_names = bt_topics.set_index("Topic")["Name"].to_dict()  # nombre de los 340 tópicos

    tot = pd.read_csv(TABLES / "5b_topics_over_time.csv")
    tot_top = tot[tot["Topic"].isin(bt_top["Topic"])].copy()
    tot_top["Name"] = tot_top["Topic"].map(bt_topics.set_index("Topic")["Name"])

    kruskal_pais = pd.read_csv(TABLES / "5e_kruskal_pais.csv")
    kruskal_supersector = pd.read_csv(TABLES / "5e_kruskal_supersector.csv")
    pareado = pd.read_csv(TABLES / "5e_pareado_2022_2024.csv")
    reg1 = pd.read_csv(TABLES / "5e_regresion1_gwindex.csv").rename(columns={"Unnamed: 0": "término"})
    reg1_vif = pd.read_csv(TABLES / "5e_regresion1_vif.csv")
    reg2 = pd.read_csv(TABLES / "5e_regresion2_tono.csv").rename(columns={"Unnamed: 0": "término"})
    reg2_vif = pd.read_csv(TABLES / "5e_regresion2_vif.csv")

    log(f"  panel: {panel.shape}, bertopic_doc: {bt_doc.shape}, bertopic_top: {bt_top.shape}")

    return dict(
        panel=panel, bt_doc=bt_doc, desc=desc, cov_anio=cov_anio,
        lda_topics=lda_topics, lda_coherencia=lda_coherencia,
        bt_topics=bt_top, bt_all_names=bt_all_names, tot=tot_top,
        kruskal_pais=kruskal_pais, kruskal_supersector=kruskal_supersector,
        pareado=pareado, reg1=reg1, reg1_vif=reg1_vif, reg2=reg2, reg2_vif=reg2_vif,
    )


def round_floats(records: list[dict], ndigits: int = 4) -> list[dict]:
    for row in records:
        for k, v in row.items():
            if isinstance(v, float):
                if math.isnan(v) or math.isinf(v):
                    row[k] = None
                else:
                    row[k] = round(v, ndigits)
    return records


def construir_data_json(d: dict) -> dict:
    log("[2/3] Construyendo JSON embebido…")

    panel = d["panel"]
    bt_topics_idx = d["bt_topics"].set_index("Topic")["Name"].to_dict()

    radar_cols = ["GW_index", "finbert_tone", "climate_specificity_spec",
                   "climate_sentiment_risk", "climate_sentiment_opportunity", "hedging_ratio"]
    stats = {c: {"mean": float(panel[c].mean()), "std": float(panel[c].std())} for c in radar_cols}

    return {
        "panel": round_floats(panel.to_dict(orient="records")),
        "bt_doc": round_floats(d["bt_doc"].to_dict(orient="records")),
        "bt_topic_names": {int(k): v for k, v in bt_topics_idx.items()},
        "bt_topic_names_all": {int(k): v for k, v in d["bt_all_names"].items()},
        "esrs_cols": ESRS_COLS,
        "esg9_cols": ESG9_COLS,
        "radar_cols": radar_cols,
        "radar_stats": stats,
        "desc": round_floats(d["desc"].to_dict(orient="records")),
        "cov_anio": round_floats(d["cov_anio"].to_dict(orient="records")),
        "lda_coherencia": round_floats(d["lda_coherencia"].to_dict(orient="records")),
        "bt_top": round_floats(d["bt_topics"].to_dict(orient="records")),
        "topics_over_time": round_floats(d["tot"].to_dict(orient="records")),
    }


def construir_tablas_html(d: dict) -> dict:
    """Tablas pequeñas y estáticas, renderizadas directamente como HTML."""
    log("[3/3] Renderizando tablas estáticas…")

    def to_html(df: pd.DataFrame, **kw) -> str:
        return df.to_html(index=False, classes="data-table", border=0, **kw)

    def to_html_lda(df: pd.DataFrame) -> str:
        return df.to_html(index=False, classes="data-table lda-table", border=0)

    return {
        "desc_table": to_html(d["desc"], float_format=lambda x: f"{x:,.0f}"),
        "lda_topics_table": to_html_lda(d["lda_topics"][["topic_id", "mapeo_ESRS", "palabras"]]),
        "kruskal_pais_table": to_html(d["kruskal_pais"], float_format=lambda x: f"{x:.4g}"),
        "kruskal_supersector_table": to_html(d["kruskal_supersector"], float_format=lambda x: f"{x:.4g}"),
        "pareado_table": to_html(d["pareado"], float_format=lambda x: f"{x:.4g}"),
        "reg1_table": to_html(d["reg1"], float_format=lambda x: f"{x:.4g}"),
        "reg1_vif_table": to_html(d["reg1_vif"], float_format=lambda x: f"{x:.3f}"),
        "reg2_table": to_html(d["reg2"], float_format=lambda x: f"{x:.4g}"),
        "reg2_vif_table": to_html(d["reg2_vif"], float_format=lambda x: f"{x:.3f}"),
    }


def main():
    d = cargar_datos()
    data_json = construir_data_json(d)
    tablas = construir_tablas_html(d)

    panel = d["panel"]
    summary = {
        "n_empresas": int(panel["empresa"].nunique()),
        "n_docs": len(panel),
        "n_paises": int(panel["pais"].nunique()),
        "n_supersectores": int(panel["supersector"].nunique()),
    }

    env = Environment(loader=FileSystemLoader(str(TEMPLATES)))
    template = env.get_template("dashboard.html.j2")
    html = template.render(
        data_json=json.dumps(data_json, ensure_ascii=False, allow_nan=False),
        summary=summary,
        **tablas,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / "index.html"
    out_file.write_text(html, encoding="utf-8")
    log(f"✓ Generado {out_file} ({out_file.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
