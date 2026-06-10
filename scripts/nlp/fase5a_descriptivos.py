"""
Fase 5A — Estadísticas descriptivas + cobertura ESRS

Outputs (en results/tables/ y results/figures/):
  tables/5a_descriptivos_corpus.csv     — stats por sección/año/empresa
  tables/5a_cobertura_esrs.csv          — matriz ESRS (289 sus × 11 categorías)
  tables/5a_cobertura_esrs_sector.csv   — cobertura media por categoría ESRS y año
  tables/5a_tfidf_sus.csv               — top-20 términos TF-IDF por sección sus
  tables/5a_tfidf_mr.csv                — top-20 términos TF-IDF por sección mr
  tables/5a_ngrams_top.csv              — bigramas/trigramas más frecuentes por sección y año
  figures/5a_heatmap_esrs.png           — heatmap cobertura ESRS por empresa×categoría
  figures/5a_distribucion_tokens.png    — distribución de n_tokens por sección y año
  figures/5a_cobertura_esrs_año.png     — evolución cobertura ESRS 2022→2024
  figures/5a_tfidf_top_sus.png          — barplot TF-IDF top-20 sus

Uso:
  conda run -n tfg-ade python scripts/nlp/fase5a_descriptivos.py
  conda run -n tfg-ade python scripts/nlp/fase5a_descriptivos.py --seccion sus  # solo sus
"""

import argparse
import json
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parents[2]
CORPUS_PATH = BASE_DIR / "data" / "processed" / "corpus.parquet"
ESRS_PATH   = BASE_DIR / "data" / "external" / "diccionarios" / "esrs_keywords.json"
TABLES_DIR  = BASE_DIR / "results" / "tables"
FIGURES_DIR = BASE_DIR / "results" / "figures"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=0.95)


# ─── helpers ────────────────────────────────────────────────────────────────

def load_esrs(path: Path) -> dict[str, list[str]]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v["terms"] for k, v in raw.items() if not k.startswith("_")}


def esrs_coverage(text: str, terms: list[str]) -> float:
    """Fracción de términos presentes en el texto (0–1)."""
    t = text.lower()
    hits = sum(1 for term in terms if term in t)
    return round(hits / len(terms), 4) if terms else 0.0


def compute_esrs_matrix(df: pd.DataFrame, esrs: dict) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        r = {"id": row["id"], "empresa": row["empresa"], "año": row["año"],
             "confianza": row["confianza"]}
        for cat, terms in esrs.items():
            r[cat] = esrs_coverage(row["clean_text"], terms)
        rows.append(r)
    return pd.DataFrame(rows)


def top_tfidf(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    vec = TfidfVectorizer(max_features=5000, min_df=3, ngram_range=(1, 1),
                          token_pattern=r"[a-z]{3,}")
    tokens_col = df["tokens"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
    X = vec.fit_transform(tokens_col)
    scores = np.asarray(X.mean(axis=0)).flatten()
    vocab = vec.get_feature_names_out()
    top_idx = scores.argsort()[::-1][:n]
    return pd.DataFrame({"term": vocab[top_idx], "tfidf_mean": scores[top_idx]})


def top_ngrams(df: pd.DataFrame, n: int = 20, ngram: tuple = (2, 3)) -> pd.DataFrame:
    vec = TfidfVectorizer(max_features=10000, min_df=3, ngram_range=ngram,
                          token_pattern=r"[a-z]{3,}")
    tokens_col = df["tokens"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
    X = vec.fit_transform(tokens_col)
    scores = np.asarray(X.mean(axis=0)).flatten()
    vocab = vec.get_feature_names_out()
    top_idx = scores.argsort()[::-1][:n]
    return pd.DataFrame({"ngram": vocab[top_idx], "tfidf_mean": scores[top_idx]})


# ─── plots ──────────────────────────────────────────────────────────────────

def plot_token_distribution(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=False)
    for ax, sec in zip(axes, ["sus", "mr"]):
        sub = df[df["seccion"] == sec]
        for año in sorted(sub["año"].unique()):
            vals = sub[sub["año"] == año]["n_tokens"]
            sns.kdeplot(vals, ax=ax, label=año, fill=True, alpha=0.25)
        ax.set_title(f"Sección '{sec}'")
        ax.set_xlabel("n_tokens")
        ax.set_ylabel("Densidad")
        ax.legend(title="Año")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.suptitle("Distribución de tokens por sección y año", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "5a_distribucion_tokens.png", dpi=150)
    plt.close(fig)
    print("  → 5a_distribucion_tokens.png")


def plot_esrs_heatmap(cov: pd.DataFrame, esrs_cats: list[str]):
    # pivot: empresa × categoría, media sobre años
    pivot = cov.groupby("empresa")[esrs_cats].mean()
    # ordenar por cobertura total descendente
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(14, max(8, len(pivot) * 0.22)))
    sns.heatmap(pivot, ax=ax, cmap="YlOrRd", vmin=0, vmax=1,
                linewidths=0.3, linecolor="white",
                cbar_kws={"label": "Fracción de términos presentes"})
    ax.set_title("Cobertura ESRS por empresa (media 2022-2024)", fontsize=12)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=6)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "5a_heatmap_esrs.png", dpi=150)
    plt.close(fig)
    print("  → 5a_heatmap_esrs.png")


def plot_esrs_evolution(cov: pd.DataFrame, esrs_cats: list[str]):
    evo = cov.groupby("año")[esrs_cats].mean().T
    fig, ax = plt.subplots(figsize=(10, 5))
    evo.plot(ax=ax, marker="o")
    ax.set_title("Evolución cobertura ESRS media 2022→2024 (sección sus)", fontsize=12)
    ax.set_xlabel("Categoría ESRS")
    ax.set_ylabel("Cobertura media")
    ax.set_ylim(0, 1)
    ax.legend(title="Año", bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "5a_cobertura_esrs_año.png", dpi=150)
    plt.close(fig)
    print("  → 5a_cobertura_esrs_año.png")


def plot_tfidf_top(tfidf_df: pd.DataFrame, seccion: str):
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(data=tfidf_df.head(20), x="tfidf_mean", y="term", ax=ax, color="#4C72B0")
    ax.set_title(f"Top-20 términos TF-IDF — sección '{seccion}'", fontsize=12)
    ax.set_xlabel("TF-IDF medio")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / f"5a_tfidf_top_{seccion}.png", dpi=150)
    plt.close(fig)
    print(f"  → 5a_tfidf_top_{seccion}.png")


# ─── main ───────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seccion", choices=["sus", "mr", "ambas"], default="ambas")
    args = ap.parse_args()

    print("Cargando corpus…")
    df = pd.read_parquet(CORPUS_PATH)
    esrs = load_esrs(ESRS_PATH)
    esrs_cats = list(esrs.keys())

    # ── 1. Estadísticas descriptivas ────────────────────────────────────────
    print("\n[1/6] Estadísticas descriptivas…")
    stats = (df.groupby(["seccion", "año"])["n_tokens"]
               .agg(n="count", media="mean", mediana="median",
                    p25=lambda x: x.quantile(0.25),
                    p75=lambda x: x.quantile(0.75),
                    max="max", min="min")
               .round(0).reset_index())
    stats.to_csv(TABLES_DIR / "5a_descriptivos_corpus.csv", index=False)
    print(stats.to_string(index=False))
    print("  → 5a_descriptivos_corpus.csv")

    # ── 2. Distribución de tokens (plot) ────────────────────────────────────
    print("\n[2/6] Distribución de tokens…")
    plot_token_distribution(df)

    # ── 3. Matriz cobertura ESRS (sobre sus) ─────────────────────────────────
    print("\n[3/6] Matriz cobertura ESRS…")
    sus = df[df["seccion"] == "sus"].copy()
    cov = compute_esrs_matrix(sus, esrs)
    cov.to_csv(TABLES_DIR / "5a_cobertura_esrs.csv", index=False)
    print(f"  Matriz: {cov.shape[0]} docs × {len(esrs_cats)} categorías")
    print("  Cobertura media por categoría:")
    for cat in esrs_cats:
        print(f"    {cat}: {cov[cat].mean():.3f}  (std {cov[cat].std():.3f})")
    print("  → 5a_cobertura_esrs.csv")

    # cobertura media por categoría y año
    evo = cov.groupby("año")[esrs_cats].mean().round(3)
    evo.to_csv(TABLES_DIR / "5a_cobertura_esrs_año.csv")
    print("  → 5a_cobertura_esrs_año.csv")

    plot_esrs_heatmap(cov, esrs_cats)
    plot_esrs_evolution(cov, esrs_cats)

    # fiables vs densidad_baja
    fiable = cov[cov["confianza"] != "densidad_baja"]
    print(f"\n  Sensibilidad (sin densidad_baja, n={len(fiable)}):")
    for cat in esrs_cats:
        print(f"    {cat}: {fiable[cat].mean():.3f}")

    # ── 4. TF-IDF top términos ───────────────────────────────────────────────
    print("\n[4/6] TF-IDF…")
    for sec in ["sus", "mr"]:
        sub = df[df["seccion"] == sec]
        tfidf_df = top_tfidf(sub)
        tfidf_df.to_csv(TABLES_DIR / f"5a_tfidf_{sec}.csv", index=False)
        plot_tfidf_top(tfidf_df, sec)
        print(f"  → 5a_tfidf_{sec}.csv")

    # ── 5. N-gramas ──────────────────────────────────────────────────────────
    print("\n[5/6] N-gramas (bigramas + trigramas)…")
    rows_ng = []
    for sec in ["sus", "mr"]:
        for año in sorted(df["año"].unique()):
            sub = df[(df["seccion"] == sec) & (df["año"] == año)]
            ng = top_ngrams(sub, n=15, ngram=(2, 3))
            ng.insert(0, "seccion", sec)
            ng.insert(1, "año", año)
            rows_ng.append(ng)
    ngrams_df = pd.concat(rows_ng, ignore_index=True)
    ngrams_df.to_csv(TABLES_DIR / "5a_ngrams_top.csv", index=False)
    print("  → 5a_ngrams_top.csv")

    # ── 6. Resumen por confianza ─────────────────────────────────────────────
    print("\n[6/6] Resumen por confianza…")
    resumen = cov.groupby("confianza")[esrs_cats].mean().round(3)
    print(resumen.to_string())

    print("\n✓ Fase 5A completa.")
    print(f"  Tablas → {TABLES_DIR}")
    print(f"  Figuras → {FIGURES_DIR}")


if __name__ == "__main__":
    main()
