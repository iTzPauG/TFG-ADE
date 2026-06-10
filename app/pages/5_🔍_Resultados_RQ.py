import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.data import cargar_kruskal, cargar_pareado, cargar_regresion, figura  # noqa: E402

st.set_page_config(page_title="Resultados RQ — TFG ADE", page_icon="🔍", layout="wide")
st.title("🔍 Resultados por pregunta de investigación")

st.caption("Análisis estadístico inferencial — Fase 5E (Decisión 026). Panel de 289 documentos `sus`.")

tab1, tab2, tab3, tab4 = st.tabs(["RQ1 — Temas", "RQ2 — Sector/País", "RQ3 — Determinantes", "RQ4 — NFRD→CSRD"])

# ── RQ1 ────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### RQ1 — ¿Qué temas predominan en el reporting de sostenibilidad?")
    st.markdown(
        """
- **LDA (K=15, Cv=0.684)**: 15 tópicos interpretables, mapeados a categorías ESRS
  (E1, E2-E4, E5, S1, S2-S3, G1, + 3 tópicos genéricos CSRD).
- **BERTopic**: 339 tópicos + 36.9% outliers. Triangulación con LDA confirmada —
  los temas dominantes coinciden entre ambos modelos.
- Los temas más frecuentes giran en torno a **emisiones/riesgo climático (E1)**,
  **plantilla propia (S1)** y, de forma creciente, **doble materialidad / IROs** (CSRD).

Ver detalle completo en la página **🧩 Topics**.
"""
    )
    st.image(str(figura("5b_topics_over_time.png")), width="stretch")

# ── RQ2 ────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### RQ2 — ¿Hay diferencias de contenido y tono por sector y país?")
    st.markdown(
        "Test de Kruskal-Wallis sobre GW_index, tono FinBERT y especificidad climática, "
        "agrupando por supersector ICB y por región/país."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Por supersector")
        df = cargar_kruskal("supersector")
        st.dataframe(df, width="stretch", hide_index=True)
        st.image(str(figura("5e_gwindex_supersector.png")), width="stretch")
    with c2:
        st.markdown("#### Por país")
        df = cargar_kruskal("pais")
        st.dataframe(df, width="stretch", hide_index=True)
        st.image(str(figura("5e_gwindex_region.png")), width="stretch")

    st.markdown(
        """
**Hallazgos:**
- GW_index y especificidad difieren significativamente por sector y región (p < 0.001 en general).
- **Tech y Financials** muestran mayor GW_index; **Real Estate** mayor especificidad.
- La región **Centro** (Europa continental) presenta menor GW_index que **Nórdicos** y **UK**.
"""
    )

# ── RQ3 ────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### RQ3 — Determinantes de especificidad/cobertura y relación tono-especificidad")
    st.markdown(
        "Dos regresiones OLS con errores robustos HC3 (R² ≈ 0.21-0.22, VIF máx 2.6 — sin "
        "problemas de multicolinealidad relevantes)."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Modelo 1 — GW_index ~ sector + región + año + tamaño + financieros")
        df = cargar_regresion("1_gwindex").rename(columns={"Unnamed: 0": "término"})
        st.dataframe(df, width="stretch", hide_index=True)
        with st.expander("VIF — Modelo 1"):
            st.dataframe(cargar_regresion("1_vif"), width="stretch", hide_index=True)
    with c2:
        st.markdown("#### Modelo 2 — Tono FinBERT ~ especificidad + sector + región + año + tamaño")
        df = cargar_regresion("2_tono").rename(columns={"Unnamed: 0": "término"})
        st.dataframe(df, width="stretch", hide_index=True)
        with st.expander("VIF — Modelo 2"):
            st.dataframe(cargar_regresion("2_vif"), width="stretch", hide_index=True)

    st.markdown(
        """
**Hallazgos:**
- **Empresas más grandes (mayor log-capitalización) → menor GW_index** (p = 0.024).
- **Especificidad → tono positivo** (p = 0.003): relación **positiva**, no apoya la hipótesis
  simple "más optimismo ↔ menos especificidad".
- El año 2024 es significativo en el modelo de tono (p = 0.013) pero no en GW_index tras
  controles — efecto compositivo, no temporal puro.
"""
    )

# ── RQ4 ────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### RQ4 — Evolución NFRD (2022-23) → CSRD (2024)")
    st.markdown("Test de Wilcoxon pareado 2022 ↔ 2024 (n=95 empresas con ambos años).")

    df = cargar_pareado()
    st.dataframe(df, width="stretch", hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.image(str(figura("5d_gwindex_evolucion.png")), width="stretch")
    with c2:
        st.image(str(figura("5e_pareado_2022_2024.png")), width="stretch")

    st.markdown(
        """
**Hallazgos confirmados con significación formal (p < 0.05):**
- **GW_index ↑** (-0.196 → +0.521): hedging↑, especificidad↓, **ratio cuantitativo↓** (hallazgo nuevo).
- **Tono FinBERT ↓** (0.202 → 0.153): comunicación cada vez menos optimista.
- **Riesgo climático ↑**, **oportunidad climática ↓**.
- **n_tokens ↑**: las secciones de sostenibilidad casi se duplican (10.9k → 23.1k tokens).
- Especificidad climática marginal (p = 0.086), no significativa al 5%.
- Promesas vagas (`ratio_futuro_sin_cifra`) se mantienen estables.

La transición a CSRD viene acompañada de informes más extensos, con más cobertura ESRS
y más menciones a doble materialidad — pero también con tono más cauteloso, más hedging
y menos cifras concretas: un patrón consistente con mayor "ruido regulatorio" y, a la vez,
señales textuales de posible impresión gestionada (proxy, no prueba directa de greenwashing).
"""
    )
