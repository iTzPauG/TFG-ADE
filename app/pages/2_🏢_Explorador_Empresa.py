import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.data import ESRS_COLS, cargar_bertopic_doc_topics, cargar_bertopic_topics, cargar_panel  # noqa: E402

st.set_page_config(page_title="Explorador de empresa — TFG ADE", page_icon="🏢", layout="wide")
st.title("🏢 Explorador por empresa")

panel = cargar_panel()
bt_doc = cargar_bertopic_doc_topics()
bt_topics = cargar_bertopic_topics().set_index("Topic")

empresas = sorted(panel["empresa"].unique())
empresa = st.selectbox("Empresa", empresas)

datos = panel[panel["empresa"] == empresa].sort_values("año")

st.markdown(f"### {empresa} — {datos['supersector'].iloc[0]} · {datos['pais'].iloc[0]}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("GW_index 2024", f"{datos['GW_index'].iloc[-1]:.2f}",
          delta=f"{datos['GW_index'].iloc[-1] - datos['GW_index'].iloc[0]:+.2f} vs 2022" if len(datos) > 1 else None)
c2.metric("Tono FinBERT 2024", f"{datos['finbert_tone'].iloc[-1]:.3f}")
c3.metric("Especificidad climática 2024", f"{datos['climate_specificity_spec'].iloc[-1]:.2%}")
c4.metric("Tokens (sus) 2024", f"{int(datos['n_tokens'].iloc[-1]):,}")

st.divider()

st.markdown("### Evolución temporal (2022-2024)")
metricas = {
    "GW_index": "Índice de greenwashing textual (GW_index)",
    "finbert_tone": "Tono FinBERT (positivo - negativo)",
    "climate_specificity_spec": "Especificidad climática (% frases específicas)",
    "climate_sentiment_risk": "Riesgo climático (% frases)",
    "climate_sentiment_opportunity": "Oportunidad climática (% frases)",
    "hedging_ratio": "Ratio de hedging (palabras modales débiles LM)",
    "ratio_cuantitativo": "Ratio de frases cuantitativas",
    "n_tokens": "Nº tokens sección sostenibilidad",
}
cols = st.columns(2)
for i, (col, label) in enumerate(metricas.items()):
    fig = px.line(datos, x="año", y=col, markers=True, title=label)
    fig.update_layout(height=300, margin=dict(t=40, b=20))
    cols[i % 2].plotly_chart(fig, width="stretch")

st.divider()

st.markdown("### Cobertura ESRS por año")
esrs_long = datos.melt(id_vars="año", value_vars=ESRS_COLS, var_name="categoría", value_name="cobertura")
fig = go.Figure()
for anio in sorted(esrs_long["año"].unique()):
    sub = esrs_long[esrs_long["año"] == anio]
    fig.add_trace(go.Scatterpolar(r=sub["cobertura"], theta=sub["categoría"], fill="toself", name=str(anio)))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), title="Cobertura ESRS — radar por año")
st.plotly_chart(fig, width="stretch")

st.divider()

st.markdown("### Tópicos BERTopic dominantes (sección sostenibilidad)")
bt_emp = bt_doc.merge(panel[["doc_id", "empresa", "año"]], on="doc_id").query("empresa == @empresa")
for _, row in bt_emp.sort_values("año").iterrows():
    topic_id = row["topic_dominante"]
    nombre = bt_topics.loc[topic_id, "Name"] if topic_id in bt_topics.index else "—"
    st.markdown(
        f"**{int(row['año'])}**: tópico dominante `{nombre}` "
        f"({row['topic_dominante_share']:.0%} de los párrafos no-outlier; "
        f"{row['outlier_share']:.0%} párrafos outlier)"
    )

st.divider()

st.markdown("### Datos financieros")
fin_cols = ["año", "capitalización", "ROA", "ROE", "deuda_equity", "total_assets"]
st.dataframe(datos[fin_cols].set_index("año"), width="stretch")
