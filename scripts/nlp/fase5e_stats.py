"""
Fase 5E — Estadística inferencial (RQ2, RQ3, RQ4)

Combina los outputs de 5C/5D (`5d_gwindex.csv`) con el dataset financiero/sectorial
(`empresas_muestra.csv`) y `corpus.parquet` (n_tokens) en un panel de 289 documentos `sus`.

Análisis:
  RQ2 — Kruskal-Wallis: GW_index, finbert_tone, climate_specificity_spec
        ~ supersector (11 grupos) y ~ país (14 grupos, descriptivo)
  RQ4 — Test pareado 2022 vs 2024 (95 empresas comunes): t-test + Wilcoxon para
        GW_index, finbert_tone, climate_specificity_spec, climate_sentiment_risk/opportunity, n_tokens
  RQ3 — 2 regresiones OLS (errores robustos HC3) + VIF:
        Reg1: GW_index ~ log(capitalización) + ROA + deuda_equity + C(supersector) + C(año) + C(region)
        Reg2: finbert_tone ~ climate_specificity_spec + log(capitalización) + ROA
              + C(supersector) + C(año) + C(region)
        `region` = agrupación de los 14 países en 4 zonas (Nórdicos/Centro/Sur/UK&Irlanda).

Inputs:
  results/tables/5d_gwindex.csv
  data/processed/corpus.parquet      (n_tokens, sección sus)
  data/external/empresas_muestra.csv (sector, país, tamaño, financieros)

Outputs:
  results/tables/5e_panel.csv                  — panel combinado (289 filas)
  results/tables/5e_kruskal_supersector.csv
  results/tables/5e_kruskal_pais.csv
  results/tables/5e_pareado_2022_2024.csv
  results/tables/5e_regresion1_gwindex.csv     + 5e_regresion1_vif.csv
  results/tables/5e_regresion2_tono.csv        + 5e_regresion2_vif.csv
  results/figures/5e_gwindex_supersector.png
  results/figures/5e_gwindex_region.png
  results/figures/5e_pareado_2022_2024.png

Uso:
  conda run -n tfg-ade python scripts/nlp/fase5e_stats.py
"""

import warnings
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from patsy import dmatrices
from scipy.stats import kruskal, ttest_rel, wilcoxon
from statsmodels.stats.outliers_influence import variance_inflation_factor

warnings.filterwarnings("ignore")

BASE_DIR  = Path(__file__).resolve().parents[2]
CORPUS    = BASE_DIR / "data" / "processed" / "corpus.parquet"
EMPRESAS  = BASE_DIR / "data" / "external" / "empresas_muestra.csv"
TABLES    = BASE_DIR / "results" / "tables"
FIGURES   = BASE_DIR / "results" / "figures"
LOG_FILE  = BASE_DIR / "results" / "5e_progress.log"

for d in (TABLES, FIGURES):
    d.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=0.95)

REGION_MAP = {
    "Sweden": "Nordicos", "Norway": "Nordicos", "Denmark": "Nordicos", "Finland": "Nordicos",
    "France": "Centro", "Germany": "Centro", "Switzerland": "Centro", "Austria": "Centro",
    "Belgium": "Centro", "Netherlands": "Centro",
    "Spain": "Sur", "Italy": "Sur",
    "United Kingdom": "UK_Irlanda", "Ireland": "UK_Irlanda",
}

DV_RQ2 = ["GW_index", "finbert_tone", "climate_specificity_spec"]
DV_RQ4 = ["GW_index", "finbert_tone", "climate_specificity_spec",
          "climate_sentiment_risk", "climate_sentiment_opportunity", "n_tokens"]


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


# ─── paso 1: panel combinado ───────────────────────────────────────────────────

def construir_panel() -> pd.DataFrame:
    log("[1/4] Construyendo panel combinado (5d_gwindex + empresas_muestra + corpus)…")

    gw = pd.read_csv(TABLES / "5d_gwindex.csv")
    gw["id_empresa"] = gw["doc_id"].str.split("_").str[0]

    log("  cargando corpus.parquet (n_tokens, sección sus)…")
    corpus = pd.read_parquet(CORPUS, columns=["id", "seccion", "n_tokens"])
    sus_tokens = corpus[corpus["seccion"] == "sus"][["id", "n_tokens"]] \
        .rename(columns={"id": "doc_id"})
    gw = gw.merge(sus_tokens, on="doc_id", how="left")

    emp = pd.read_csv(EMPRESAS)
    emp_cols = ["id_empresa", "año", "supersector", "pais", "capitalización",
                 "ROA", "ROE", "deuda_equity", "total_assets"]
    panel = gw.merge(emp[emp_cols], on=["id_empresa", "año"], how="left")

    panel["region"] = panel["pais"].map(REGION_MAP)
    panel["log_cap"] = np.log(panel["capitalización"])

    n_sin_pais = panel["pais"].isna().sum()
    n_sin_fin = panel[["ROA", "deuda_equity"]].isna().any(axis=1).sum()
    log(f"  panel: {len(panel)} filas | sin sector/país: {n_sin_pais} | sin ROA/deuda_equity: {n_sin_fin}")

    out = TABLES / "5e_panel.csv"
    panel.to_csv(out, index=False)
    log(f"  → {out.name}")
    return panel


# ─── paso 2: RQ2 — Kruskal-Wallis por sector y país ────────────────────────────

def kruskal_por_grupo(panel: pd.DataFrame, group_col: str, label: str) -> pd.DataFrame:
    rows = []
    for dv in DV_RQ2:
        sub = panel[[group_col, dv]].dropna()
        groups = {g: vals[dv].values for g, vals in sub.groupby(group_col) if len(vals) >= 2}
        if len(groups) < 2:
            continue
        H, p = kruskal(*groups.values())
        n = sum(len(v) for v in groups.values())
        eta2 = H / (n - 1)  # tamaño del efecto (epsilon^2 aprox.)
        rows.append({
            "variable": dv, "n_grupos": len(groups), "n_obs": n,
            "H": H, "p_valor": p, "eta2": eta2,
        })
        # medianas por grupo (para interpretación)
        medianas = sub.groupby(group_col)[dv].median().sort_values(ascending=False)
        log(f"    {dv} ~ {label}: H={H:.2f}, p={p:.4f}, eta2={eta2:.3f}")
        log(f"      medianas: " + ", ".join(f"{g}={v:.3f}" for g, v in medianas.items()))
    return pd.DataFrame(rows)


def rq2_kruskal(panel: pd.DataFrame) -> None:
    log("[2/4] RQ2 — Kruskal-Wallis por supersector y por país…")

    log("  -- por supersector (11 grupos) --")
    res_sector = kruskal_por_grupo(panel, "supersector", "supersector")
    res_sector.to_csv(TABLES / "5e_kruskal_supersector.csv", index=False)

    log("  -- por país (14 grupos, descriptivo, grupos pequeños) --")
    res_pais = kruskal_por_grupo(panel, "pais", "país")
    res_pais.to_csv(TABLES / "5e_kruskal_pais.csv", index=False)

    log("  → 5e_kruskal_supersector.csv / 5e_kruskal_pais.csv")

    # figuras
    fig, ax = plt.subplots(figsize=(11, 5))
    orden = panel.groupby("supersector")["GW_index"].median().sort_values(ascending=False).index
    sns.boxplot(data=panel, x="supersector", y="GW_index", order=orden, ax=ax)
    ax.axhline(0, color="grey", linestyle="--", linewidth=1)
    ax.set_title("GW_index por supersector ICB")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(FIGURES / "5e_gwindex_supersector.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    orden = panel.groupby("region")["GW_index"].median().sort_values(ascending=False).index
    sns.boxplot(data=panel, x="region", y="GW_index", order=orden, ax=ax)
    ax.axhline(0, color="grey", linestyle="--", linewidth=1)
    ax.set_title("GW_index por región")
    fig.tight_layout()
    fig.savefig(FIGURES / "5e_gwindex_region.png", dpi=150)
    plt.close(fig)

    log("  → 5e_gwindex_supersector.png / 5e_gwindex_region.png")


# ─── paso 3: RQ4 — test pareado 2022 vs 2024 ───────────────────────────────────

def rq4_pareado(panel: pd.DataFrame) -> None:
    log("[3/4] RQ4 — test pareado 2022 vs 2024 (NFRD vs CSRD)…")

    p22 = panel[panel["año"] == 2022].set_index("id_empresa")
    p24 = panel[panel["año"] == 2024].set_index("id_empresa")
    comunes = p22.index.intersection(p24.index)
    log(f"  empresas comunes 2022 y 2024: {len(comunes)}")

    rows = []
    for dv in DV_RQ4:
        a = p22.loc[comunes, dv]
        b = p24.loc[comunes, dv]
        valid = a.notna() & b.notna()
        a, b = a[valid], b[valid]
        diff = b - a
        t, pt = ttest_rel(b, a)
        w, pw = wilcoxon(b, a)
        rows.append({
            "variable": dv, "n": len(a),
            "media_2022": a.mean(), "media_2024": b.mean(), "diff_media": diff.mean(),
            "t": t, "p_ttest": pt, "W": w, "p_wilcoxon": pw,
        })
        log(f"    {dv}: 2022={a.mean():.4f} → 2024={b.mean():.4f} "
            f"(Δ={diff.mean():+.4f})  t-test p={pt:.4f}  Wilcoxon p={pw:.4f}")

    res = pd.DataFrame(rows)
    res.to_csv(TABLES / "5e_pareado_2022_2024.csv", index=False)
    log("  → 5e_pareado_2022_2024.csv")

    # figura: GW_index por empresa, 2022 vs 2024
    plot_df = pd.DataFrame({
        "empresa": list(comunes) * 2,
        "año": [2022] * len(comunes) + [2024] * len(comunes),
        "GW_index": list(p22.loc[comunes, "GW_index"]) + list(p24.loc[comunes, "GW_index"]),
    })
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=plot_df, x="año", y="GW_index", ax=ax)
    sns.stripplot(data=plot_df, x="año", y="GW_index", color="black", alpha=0.3, ax=ax)
    ax.axhline(0, color="grey", linestyle="--", linewidth=1)
    ax.set_title(f"GW_index 2022 vs 2024 ({len(comunes)} empresas comunes)")
    fig.tight_layout()
    fig.savefig(FIGURES / "5e_pareado_2022_2024.png", dpi=150)
    plt.close(fig)
    log("  → 5e_pareado_2022_2024.png")


# ─── paso 4: RQ3 — regresiones OLS (HC3) + VIF ─────────────────────────────────

def calcular_vif(formula_rhs: str, data: pd.DataFrame) -> pd.DataFrame:
    # OJO: el intercepto debe permanecer en la matriz de diseño al calcular el VIF
    # (variance_inflation_factor regresa cada columna sobre las demás INCLUYENDO la
    # constante; eliminarlo convierte las regresiones auxiliares en "a través del
    # origen" e infla artificialmente variables no centradas en 0, p.ej. log_cap).
    _, X = dmatrices("1 ~ " + formula_rhs, data=data, return_type="dataframe")
    vif = pd.DataFrame({
        "variable": X.columns,
        "VIF": [variance_inflation_factor(X.values, i) for i in range(X.shape[1])],
    })
    return vif[vif["variable"] != "Intercept"].reset_index(drop=True)


def rq3_regresiones(panel: pd.DataFrame) -> None:
    log("[4/4] RQ3 — regresiones OLS (HC3) + VIF…")

    cols_modelo = ["GW_index", "finbert_tone", "climate_specificity_spec", "log_cap",
                    "ROA", "deuda_equity", "supersector", "año", "region"]
    reg_df = panel.dropna(subset=cols_modelo).copy()
    reg_df["año"] = reg_df["año"].astype(str)
    log(f"  observaciones para regresión (tras eliminar NaN financieros/sector): {len(reg_df)} / {len(panel)}")

    rhs1 = "log_cap + ROA + deuda_equity + C(supersector) + C(año) + C(region)"
    m1 = smf.ols(f"GW_index ~ {rhs1}", data=reg_df).fit(cov_type="HC3")
    log("  -- Reg1: GW_index ~ tamaño + financieros + sector + año + región --")
    log(f"    R2={m1.rsquared:.3f}  R2_adj={m1.rsquared_adj:.3f}  n={int(m1.nobs)}")
    for var, coef, p in zip(m1.params.index, m1.params.values, m1.pvalues.values):
        if p < 0.10:
            log(f"    {var:30s} coef={coef:+.4f}  p={p:.4f}")
    m1.summary2().tables[1].to_csv(TABLES / "5e_regresion1_gwindex.csv")
    vif1 = calcular_vif(rhs1, reg_df)
    vif1.to_csv(TABLES / "5e_regresion1_vif.csv", index=False)
    log(f"    VIF máximo: {vif1['VIF'].max():.2f} ({vif1.loc[vif1['VIF'].idxmax(), 'variable']})")

    rhs2 = "climate_specificity_spec + log_cap + ROA + C(supersector) + C(año) + C(region)"
    m2 = smf.ols(f"finbert_tone ~ {rhs2}", data=reg_df).fit(cov_type="HC3")
    log("  -- Reg2: finbert_tone ~ especificidad + tamaño + financieros + sector + año + región --")
    log(f"    R2={m2.rsquared:.3f}  R2_adj={m2.rsquared_adj:.3f}  n={int(m2.nobs)}")
    for var, coef, p in zip(m2.params.index, m2.params.values, m2.pvalues.values):
        if p < 0.10:
            log(f"    {var:30s} coef={coef:+.4f}  p={p:.4f}")
    m2.summary2().tables[1].to_csv(TABLES / "5e_regresion2_tono.csv")
    vif2 = calcular_vif(rhs2, reg_df)
    vif2.to_csv(TABLES / "5e_regresion2_vif.csv", index=False)
    log(f"    VIF máximo: {vif2['VIF'].max():.2f} ({vif2.loc[vif2['VIF'].idxmax(), 'variable']})")

    log("  → 5e_regresion{1,2}_{gwindex,tono}.csv + 5e_regresion{1,2}_vif.csv")


# ─── main ───────────────────────────────────────────────────────────────────────

def main():
    inicio = datetime.now()
    log("=== Fase 5E — Estadística inferencial (RQ2, RQ3, RQ4) ===")

    panel = construir_panel()
    rq2_kruskal(panel)
    rq4_pareado(panel)
    rq3_regresiones(panel)

    minutos = (datetime.now() - inicio).total_seconds() / 60
    log(f"✓ Fase 5E completa en {minutos:.1f} min")


if __name__ == "__main__":
    main()
