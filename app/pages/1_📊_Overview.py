import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.data import (  # noqa: E402
    ESRS_COLS,
    cargar_cobertura_esrs_anio,
    cargar_descriptivos,
    cargar_panel,
    figura,
)

st.set_page_config(page_title="Overview — TFG ADE", page_icon="📊", layout="wide")
st.title("📊 Overview del corpus")

panel = cargar_panel()
desc = cargar_descriptivos()

st.markdown("### Tamaño del corpus por sección y año")
sus = desc[desc["seccion"] == "sus"].copy()
mr = desc[desc["seccion"] == "mr"].copy()

col1, col2 = st.columns(2)
with col1:
    fig = px.bar(
        sus, x="año", y="media", error_y=sus["p75"] - sus["media"],
        title="Tokens medios — sección sostenibilidad (sus)",
        labels={"media": "tokens medios", "año": "año"},
    )
    st.plotly_chart(fig, width="stretch")
    st.caption("Crecimiento +111% (10.9k → 23.1k tokens, 2022→2024) — señal RQ4 (NFRD→CSRD).")
with col2:
    fig = px.bar(
        mr, x="año", y="media",
        title="Tokens medios — management report (mr)",
        labels={"media": "tokens medios", "año": "año"},
    )
    st.plotly_chart(fig, width="stretch")
    st.caption("El `mr` se mantiene estable (~36-40k tokens): el crecimiento es específico de `sus`.")

st.dataframe(desc, width="stretch", hide_index=True)

st.divider()

st.markdown("### Cobertura ESRS (diccionario v1.1, 11 categorías)")
st.image(str(figura("5a_heatmap_esrs.png")), width="stretch")

st.markdown("#### Evolución de la cobertura ESRS por año")
cov_anio = cargar_cobertura_esrs_anio()
cov_long = cov_anio.melt(id_vars="año", value_vars=ESRS_COLS, var_name="categoría", value_name="cobertura")
fig = px.line(cov_long, x="año", y="cobertura", color="categoría", markers=True,
               title="Cobertura media por categoría ESRS")
st.plotly_chart(fig, width="stretch")
st.caption("E1 (cambio climático) y S1 (plantilla propia) son las categorías mejor cubiertas en todos los años; "
           "E2 (contaminación) la peor.")

st.divider()

st.markdown("### Composición de la muestra (289 documentos `sus`)")
c1, c2 = st.columns(2)
with c1:
    counts = panel["supersector"].value_counts().reset_index()
    counts.columns = ["supersector", "n"]
    fig = px.bar(counts.sort_values("n"), x="n", y="supersector", orientation="h",
                  title="Documentos por supersector ICB")
    st.plotly_chart(fig, width="stretch")
with c2:
    counts = panel["pais"].value_counts().reset_index()
    counts.columns = ["país", "n"]
    fig = px.bar(counts.sort_values("n"), x="n", y="país", orientation="h",
                  title="Documentos por país")
    st.plotly_chart(fig, width="stretch")

st.divider()

st.markdown("### Léxico distintivo (TF-IDF)")
c1, c2 = st.columns(2)
with c1:
    st.image(str(figura("5a_tfidf_top_sus.png")), width="stretch", caption="Top TF-IDF — sección sostenibilidad")
with c2:
    st.image(str(figura("5a_tfidf_top_mr.png")), width="stretch", caption="Top TF-IDF — management report")

st.markdown("### Distribución de tokens")
st.image(str(figura("5a_distribucion_tokens.png")), width="stretch")
