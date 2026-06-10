"""Carga cacheada de los resultados de Fase 5 para el dashboard."""

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"
DASHBOARD = TABLES / "dashboard"

ESRS_COLS = ["E1", "E2", "E3", "E4", "E5", "S1", "S2", "S3", "S4", "G1", "ESRS2"]

ESG9_COLS = [
    "esg9_business_ethics_and_values", "esg9_climate_change", "esg9_community_relations",
    "esg9_corporate_governance", "esg9_human_capital", "esg9_natural_capital",
    "esg9_non-esg", "esg9_pollution_and_waste", "esg9_product_liability",
]


@st.cache_data
def cargar_panel() -> pd.DataFrame:
    """Panel maestro: 289 docs `sus` con GW_index, sentimiento, cobertura ESRS/ESG-9, financieros."""
    return pd.read_csv(DASHBOARD / "panel.csv")


@st.cache_data
def cargar_descriptivos() -> pd.DataFrame:
    return pd.read_csv(TABLES / "5a_descriptivos_corpus.csv")


@st.cache_data
def cargar_cobertura_esrs_anio() -> pd.DataFrame:
    return pd.read_csv(TABLES / "5a_cobertura_esrs_año.csv")


@st.cache_data
def cargar_lda_topics() -> pd.DataFrame:
    return pd.read_csv(TABLES / "5b_lda_topics.csv")


@st.cache_data
def cargar_lda_coherencia() -> pd.DataFrame:
    return pd.read_csv(TABLES / "5b_lda_coherencia.csv")


@st.cache_data
def cargar_bertopic_topics() -> pd.DataFrame:
    df = pd.read_csv(TABLES / "5b_bertopic_topics.csv")
    return df[["Topic", "Count", "Name", "Representation"]]


@st.cache_data
def cargar_bertopic_doc_topics() -> pd.DataFrame:
    return pd.read_csv(DASHBOARD / "bertopic_doc_topics.csv")


@st.cache_data
def cargar_topics_over_time() -> pd.DataFrame:
    return pd.read_csv(TABLES / "5b_topics_over_time.csv")


@st.cache_data
def cargar_kruskal(nombre: str) -> pd.DataFrame:
    return pd.read_csv(TABLES / f"5e_kruskal_{nombre}.csv")


@st.cache_data
def cargar_pareado() -> pd.DataFrame:
    return pd.read_csv(TABLES / "5e_pareado_2022_2024.csv")


@st.cache_data
def cargar_regresion(nombre: str) -> pd.DataFrame:
    return pd.read_csv(TABLES / f"5e_regresion{nombre}.csv")


def figura(nombre: str) -> Path:
    return FIGURES / nombre
