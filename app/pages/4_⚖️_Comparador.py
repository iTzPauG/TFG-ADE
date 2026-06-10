import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.data import cargar_panel  # noqa: E402

st.set_page_config(page_title="Comparador — TFG ADE", page_icon="⚖️", layout="wide")
st.title("⚖️ Comparador de empresas")

panel = cargar_panel()

c1, c2 = st.columns([1, 3])
with c1:
    anio = st.selectbox("Año", sorted(panel["año"].unique(), reverse=True))
with c2:
    empresas_disponibles = sorted(panel.loc[panel["año"] == anio, "empresa"].unique())
    seleccion = st.multiselect(
        "Empresas a comparar (2-6)",
        empresas_disponibles,
        default=empresas_disponibles[:3],
    )

datos = panel[(panel["año"] == anio) & (panel["empresa"].isin(seleccion))]

if len(seleccion) < 2:
    st.info("Selecciona al menos 2 empresas para comparar.")
    st.stop()

st.divider()

st.markdown("### Métricas clave")
metricas = {
    "GW_index": "GW_index (mayor = más señales de greenwashing textual)",
    "finbert_tone": "Tono FinBERT",
    "climate_specificity_spec": "Especificidad climática",
    "climate_sentiment_risk": "Riesgo climático",
    "climate_sentiment_opportunity": "Oportunidad climática",
    "hedging_ratio": "Ratio de hedging",
    "ratio_cuantitativo": "Ratio cuantitativo",
}
cols = st.columns(2)
for i, (col, label) in enumerate(metricas.items()):
    fig = px.bar(datos.sort_values(col), x="empresa", y=col, title=label, color="empresa")
    fig.update_layout(height=320, margin=dict(t=40, b=20), showlegend=False)
    cols[i % 2].plotly_chart(fig, width="stretch")

st.divider()

st.markdown("### Perfil normalizado (radar, z-score sobre el panel completo de 289 docs)")
radar_cols = ["GW_index", "finbert_tone", "climate_specificity_spec",
               "climate_sentiment_risk", "climate_sentiment_opportunity", "hedging_ratio"]
zscored = panel.copy()
for c in radar_cols:
    zscored[c] = (zscored[c] - zscored[c].mean()) / zscored[c].std()

fig = go.Figure()
for empresa in seleccion:
    fila = zscored[(zscored["año"] == anio) & (zscored["empresa"] == empresa)]
    if fila.empty:
        continue
    fig.add_trace(go.Scatterpolar(
        r=fila[radar_cols].values.flatten(), theta=radar_cols, fill="toself", name=empresa,
    ))
fig.update_layout(polar=dict(radialaxis=dict(visible=True)), title=f"Perfil z-score — {anio}")
st.plotly_chart(fig, width="stretch")

st.divider()

st.markdown("### Tabla comparativa")
tabla_cols = ["empresa", "supersector", "pais", "GW_index", "finbert_tone",
               "climate_specificity_spec", "n_tokens", "capitalización"]
st.dataframe(datos[tabla_cols].set_index("empresa"), width="stretch")
