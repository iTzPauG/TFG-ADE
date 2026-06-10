import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.data import (  # noqa: E402
    cargar_bertopic_topics,
    cargar_lda_coherencia,
    cargar_lda_topics,
    cargar_topics_over_time,
    figura,
)

st.set_page_config(page_title="Topics — TFG ADE", page_icon="🧩", layout="wide")
st.title("🧩 Topic modeling — sección sostenibilidad")

tab_lda, tab_bert = st.tabs(["LDA (K=15)", "BERTopic (339 tópicos)"])

with tab_lda:
    st.markdown(
        "LDA entrenado sobre 131.140 párrafos de la sección de sostenibilidad. "
        "K óptimo = 15 por coherencia Cv (Decisión 022)."
    )

    coh = cargar_lda_coherencia()
    fig = px.line(coh, x="K", y="coherencia_Cv", markers=True, title="Coherencia Cv por K")
    fig.add_vline(x=15, line_dash="dash", line_color="red", annotation_text="K óptimo")
    st.plotly_chart(fig, width="stretch")

    st.image(str(figura("5b_lda_topics_barplot.png")), width="stretch")

    st.markdown("#### Tópicos interpretados (mapeo a ESRS, Dec.022)")
    mapeo = {
        "T06": "E1 — Cambio climático", "T02": "E2-E4 — Contaminación/Recursos/Biodiversidad",
        "T13": "E5 — Economía circular", "T00": "S1 — Plantilla propia",
        "T04": "S2-S3 — Cadena de valor/Comunidades", "T08": "G1 — Conducta empresarial",
        "T05": "CSRD genérico", "T09": "CSRD genérico", "T11": "CSRD genérico",
    }
    lda_topics = cargar_lda_topics()
    lda_topics["topic_id"] = lda_topics["topic"].apply(lambda t: f"T{int(t):02d}")
    lda_topics["mapeo_ESRS"] = lda_topics["topic_id"].map(mapeo).fillna("—")
    st.dataframe(
        lda_topics[["topic_id", "mapeo_ESRS", "palabras"]],
        width="stretch", hide_index=True,
    )

with tab_bert:
    st.markdown(
        "BERTopic sobre los mismos 131.140 párrafos. 339 tópicos + outliers (36.9%). "
        "Triangulación con LDA confirmada (Dec.022)."
    )

    st.image(str(figura("5b_bertopic_barchart.png")), width="stretch")

    bert_topics = cargar_bertopic_topics()
    n = st.slider("Nº de tópicos a mostrar (excluyendo outlier -1)", 5, 50, 20)
    top = bert_topics[bert_topics["Topic"] != -1].sort_values("Count", ascending=False).head(n)
    st.dataframe(top, width="stretch", hide_index=True)

    st.divider()
    st.markdown("#### Evolución temporal de tópicos seleccionados")
    tot = cargar_topics_over_time()
    nombres = bert_topics.set_index("Topic")["Name"]
    opciones = top["Topic"].tolist()
    seleccion = st.multiselect(
        "Tópicos a comparar a lo largo del tiempo",
        options=opciones,
        default=opciones[:5],
        format_func=lambda t: f"{t}: {nombres.get(t, '')}",
    )
    if seleccion:
        sub = tot[tot["Topic"].isin(seleccion)].copy()
        sub["Tópico"] = sub["Topic"].map(nombres)
        fig = px.line(sub, x="Timestamp", y="Frequency", color="Tópico", markers=True,
                       title="Frecuencia (nº párrafos) por año")
        st.plotly_chart(fig, width="stretch")

    st.caption(
        "Hallazgo RQ4: T7 'doble materialidad/IROs' crece ×8.2 (104→865 párrafos, 2022→2024); "
        "T16 'Taxonomía UE' ×1.8; T15 'riesgo climático físico' ×1.7."
    )

    st.image(str(figura("5b_topics_over_time.png")), width="stretch")
