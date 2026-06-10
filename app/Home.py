"""Dashboard TFG ADE — Comunicación corporativa de sostenibilidad (STOXX 600).

Ejecutar con:
  conda run -n tfg-ade streamlit run app/Home.py
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent))

from utils.data import cargar_descriptivos, cargar_panel  # noqa: E402

st.set_page_config(
    page_title="TFG ADE — Sostenibilidad STOXX 600",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 Comunicación corporativa de sostenibilidad — STOXX Europe 600")

st.markdown(
    """
**TFG (ADE, Universidad de Valencia)** — *"Comunicación corporativa y estrategias de
gestión en los informes de sostenibilidad de las empresas europeas: un análisis de
contenido mediante técnicas de inteligencia artificial."*

Este dashboard explora los resultados del análisis PLN (Fase 5) sobre **289 secciones de
sostenibilidad** de informes corporativos de **97 empresas europeas × 3 años (2022-2024)**,
bajo el marco normativo CSRD / ESRS.

⚠️ Todo el análisis es **textual** (FinBERT, ClimateBERT, diccionario Loughran-McDonald,
diccionario ESRS propio) — no se usan ratings ESG de terceros.
"""
)

st.divider()

panel = cargar_panel()
desc = cargar_descriptivos()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Empresas", panel["empresa"].nunique())
c2.metric("Documentos (sección sostenibilidad)", len(panel))
c3.metric("Países", panel["pais"].nunique())
c4.metric("Sectores (supersector ICB)", panel["supersector"].nunique())

st.divider()

st.markdown("### Navegación")
st.markdown(
    """
- **📊 Overview** — descriptivos del corpus, distribución de tokens, cobertura ESRS
- **🏢 Explorador de empresa** — evolución de tono, especificidad y GW_index por empresa
- **🧩 Topics** — modelos LDA y BERTopic sobre los párrafos de sostenibilidad
- **⚖️ Comparador** — comparación de métricas clave entre empresas
- **🔍 Resultados RQ** — hallazgos por pregunta de investigación (RQ1-RQ4)
"""
)

st.caption(
    "Fuente: corpus.parquet (Fase 4) + resultados Fase 5 (5A-5E). "
    "Ver docs/decisiones.md para el detalle metodológico de cada decisión."
)
