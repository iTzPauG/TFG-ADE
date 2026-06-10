"""
Fase 5D — GW_index (índice textual de greenwashing)

Construye un índice compuesto de "cheap talk" combinando, a nivel documento
(289 filas, sección `sus`):

  - hedging_ratio          = lm_uncertainty + lm_weak_modal   (ya en 5c_doc_agregado.csv)
  - climate_specificity_spec = % frases climáticas específicas (ClimateBERT, ya en 5c)
  - ratio_cuantitativo     = % frases con al menos una cifra (excluyendo años sueltos 19xx/20xx) — NUEVO
  - ratio_futuro           = % frases con lenguaje prospectivo (will/plan to/target/by 20XX...) — NUEVO
  - ratio_futuro_sin_cifra = % frases prospectivas SIN ninguna cifra → "promesa vaga" — NUEVO

GW_index = z(hedging_ratio) + z(ratio_futuro_sin_cifra) − z(ratio_cuantitativo) − z(climate_specificity_spec)

Valores altos de GW_index = más lenguaje cauteloso/promesas vagas y futuras sin
cuantificar, y menos especificidad climática → señal de "cheap talk" (Bingler et al. 2022,
Decisión 001).

Inputs:
  results/tables/5c_frases.parquet      — 285.509 frases (texto + ratios LM)
  results/tables/5c_doc_agregado.csv    — 289 docs (hedging, especificidad, tono)

Outputs:
  results/tables/5d_gwindex.csv         — 289 docs: componentes + GW_index
  results/figures/5d_gwindex_evolucion.png
  results/figures/5d_componentes.png
  results/figures/5d_gwindex_vs_tono.png

Uso:
  conda run -n tfg-ade python scripts/nlp/fase5d_gwindex.py
"""

import re
import warnings
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parents[2]
TABLES   = BASE_DIR / "results" / "tables"
FIGURES  = BASE_DIR / "results" / "figures"
LOG_FILE = BASE_DIR / "results" / "5d_progress.log"

for d in (TABLES, FIGURES):
    d.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=0.95)

CHUNK = 20_000  # tamaño de lote para la barra de progreso


# ─── utilidades de progreso ────────────────────────────────────────────────────

def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log(msg: str) -> None:
    line = f"[{ts()}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def progress(current: int, total: int, prefix: str = "", suffix: str = "",
              width: int = 30) -> None:
    pct    = current / total
    filled = int(width * pct)
    bar    = "█" * filled + "░" * (width - filled)
    line   = f"  {ts()} {prefix} [{bar}] {pct*100:5.1f}% ({current}/{total}) {suffix}"
    print(f"\r{line}", end="", flush=True)
    if current == total or int(pct * 10) > int((current - 1) / total * 10):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line.strip() + "\n")
    if current == total:
        print()


# ─── patrones léxicos ──────────────────────────────────────────────────────────

# años sueltos (19xx/20xx) → no cuentan como "cifra" por sí solos
YEAR_RE  = re.compile(r"\b(?:19|20)\d{2}\b")
DIGIT_RE = re.compile(r"\d")

# lenguaje prospectivo: futuro simple, intención, compromisos, metas, horizontes temporales
FUTURE_TERMS = [
    r"\bwill\b", r"\bshall\b", r"\bgoing to\b",
    r"\bplan(?:s|ned|ning)?\s+to\b", r"\baim(?:s|ing)?\s+to\b",
    r"\btarget(?:s|ed|ing)?\b", r"\bcommit(?:s|ted|ment|ments)?\b",
    r"\bintend(?:s|ed|ing)?\s+to\b", r"\bby\s+20\d{2}\b",
    r"\bfuture\b", r"\bexpect(?:s|ed|ing)?\s+to\b",
    r"\baspir(?:e|es|ing)\s+to\b", r"\bambition(?:s)?\b",
    r"\bpledge(?:s|d)?\b", r"\bgoal(?:s)?\b", r"\bobjective(?:s)?\b",
    r"\bnext\s+(?:year|years|decade)\b", r"\bupcoming\b",
]
FUTURE_RE = re.compile("|".join(FUTURE_TERMS), re.IGNORECASE)


# ─── paso 1: flags por frase ───────────────────────────────────────────────────

def calcular_flags(frases: pd.DataFrame) -> pd.DataFrame:
    log("[1/3] Calculando flags por frase (cifra / lenguaje futuro)…")
    n = len(frases)
    tiene_cifra = pd.Series(False, index=frases.index)
    es_futuro   = pd.Series(False, index=frases.index)

    for start in range(0, n, CHUNK):
        end = min(start + CHUNK, n)
        bloque = frases["text"].iloc[start:end]
        sin_anios = bloque.str.replace(YEAR_RE, "", regex=True)
        tiene_cifra.iloc[start:end] = sin_anios.str.contains(DIGIT_RE, regex=True)
        es_futuro.iloc[start:end]   = bloque.str.contains(FUTURE_RE, regex=True)
        progress(end, n, "Flags por frase")

    flags = frases[["doc_id", "empresa", "año", "confianza"]].copy()
    flags["tiene_cifra"]       = tiene_cifra
    flags["es_futuro"]         = es_futuro
    flags["futuro_sin_cifra"]  = es_futuro & ~tiene_cifra

    log(f"  % frases con cifra (no-año): {flags['tiene_cifra'].mean()*100:.1f}%")
    log(f"  % frases con lenguaje futuro: {flags['es_futuro'].mean()*100:.1f}%")
    log(f"  % frases futuras SIN cifra: {flags['futuro_sin_cifra'].mean()*100:.1f}%")
    return flags


# ─── paso 2: agregación + índice ───────────────────────────────────────────────

def construir_indice(flags: pd.DataFrame) -> pd.DataFrame:
    log("[2/3] Agregando a nivel documento y construyendo GW_index…")

    doc_flags = flags.groupby(["doc_id", "empresa", "año", "confianza"]).agg(
        ratio_cuantitativo=("tiene_cifra", "mean"),
        ratio_futuro=("es_futuro", "mean"),
        ratio_futuro_sin_cifra=("futuro_sin_cifra", "mean"),
    ).reset_index()

    agg5c = pd.read_csv(TABLES / "5c_doc_agregado.csv")
    gw = doc_flags.merge(
        agg5c[["doc_id", "lm_uncertainty", "lm_weak_modal", "climate_specificity_spec",
               "finbert_tone", "climate_sentiment_opportunity", "climate_sentiment_risk",
               "climate_commitment_yes"]],
        on="doc_id", how="left",
    )
    gw["hedging_ratio"] = gw["lm_uncertainty"] + gw["lm_weak_modal"]

    def zscore(s: pd.Series) -> pd.Series:
        return (s - s.mean()) / s.std()

    gw["z_hedging"]          = zscore(gw["hedging_ratio"])
    gw["z_futuro_sin_cifra"] = zscore(gw["ratio_futuro_sin_cifra"])
    gw["z_cuantitativo"]     = zscore(gw["ratio_cuantitativo"])
    gw["z_specificity"]      = zscore(gw["climate_specificity_spec"])

    gw["GW_index"] = (gw["z_hedging"] + gw["z_futuro_sin_cifra"]
                       - gw["z_cuantitativo"] - gw["z_specificity"])

    out = TABLES / "5d_gwindex.csv"
    gw.to_csv(out, index=False)
    log(f"  {len(gw)} documentos → {out.name}")

    log("[2/3] Evolución GW_index y componentes por año:")
    resumen = gw.groupby("año")[["GW_index", "hedging_ratio", "ratio_cuantitativo",
                                   "ratio_futuro", "ratio_futuro_sin_cifra",
                                   "climate_specificity_spec"]].mean()
    for col in resumen.columns:
        vals = "  ".join(f"{a}={v:.4f}" for a, v in resumen[col].items())
        log(f"    {col:28s} {vals}")

    return gw


# ─── paso 3: figuras ────────────────────────────────────────────────────────────

def generar_figuras(gw: pd.DataFrame) -> None:
    log("[3/3] Generando figuras…")

    # 1. Evolución del GW_index por año
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=gw, x="año", y="GW_index", ax=ax)
    ax.axhline(0, color="grey", linestyle="--", linewidth=1)
    ax.set_title("GW_index por año (sección sus)")
    fig.tight_layout()
    fig.savefig(FIGURES / "5d_gwindex_evolucion.png", dpi=150)
    plt.close(fig)

    # 2. Componentes (ratios sin estandarizar) por año
    comp_cols = ["hedging_ratio", "ratio_cuantitativo", "ratio_futuro",
                  "ratio_futuro_sin_cifra", "climate_specificity_spec"]
    melted = gw.melt(id_vars=["año"], value_vars=comp_cols,
                      var_name="componente", value_name="valor")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=melted, x="componente", y="valor", hue="año", ax=ax)
    ax.set_title("Componentes del GW_index por año (sección sus)")
    plt.xticks(rotation=20)
    fig.tight_layout()
    fig.savefig(FIGURES / "5d_componentes.png", dpi=150)
    plt.close(fig)

    # 3. GW_index vs tono FinBERT (relación tono-especificidad, Decisión 001)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(data=gw, x="finbert_tone", y="GW_index", hue="año",
                     palette="muted", ax=ax)
    ax.axhline(0, color="grey", linestyle="--", linewidth=1)
    ax.set_title("GW_index vs tono FinBERT por documento")
    fig.tight_layout()
    fig.savefig(FIGURES / "5d_gwindex_vs_tono.png", dpi=150)
    plt.close(fig)

    log("  → 5d_gwindex_evolucion.png / 5d_componentes.png / 5d_gwindex_vs_tono.png")


# ─── main ───────────────────────────────────────────────────────────────────────

def main():
    inicio = datetime.now()
    log("=== Fase 5D — GW_index ===")

    frases = pd.read_parquet(TABLES / "5c_frases.parquet")
    log(f"  {len(frases):,} frases cargadas desde 5c_frases.parquet")

    flags = calcular_flags(frases)
    gw = construir_indice(flags)
    generar_figuras(gw)

    minutos = (datetime.now() - inicio).total_seconds() / 60
    log(f"✓ Fase 5D completa en {minutos:.1f} min")


if __name__ == "__main__":
    main()
