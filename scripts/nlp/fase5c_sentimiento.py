"""
Fase 5C — Sentimiento, tono y especificidad textual

Pipeline:
  1. Segmentación en frases (spaCy sentencizer, rule-based) sobre clean_text de `sus`
  2. Loughran-McDonald: ratios de negative/positive/uncertainty/litigious/
     strong_modal/weak_modal/constraining por frase
  3. ClimateBERT en cascada (Bingler et al. 2022):
     a. climate-detector sobre TODAS las frases → ¿es contenido climático?
     b. climate-sentiment / climate-commitment / climate-specificity SOLO sobre
        las frases marcadas como climáticas en (a)
  4. FinBERT (ProsusAI/finbert) sobre todas las frases → sentimiento financiero
  5. FinBERT-ESG-9 (yiyanghkust) sobre todas las frases → categoría ESG
  6. Agregación a nivel documento (289 filas, una por doc `sus`)

Outputs:
  tables/5c_frases.parquet            — frases segmentadas + ratios LM
  tables/5c_climate_detector.parquet  — label+score climate-detector por frase
  tables/5c_climate_sub.parquet       — sentiment/commitment/specificity (solo frases climáticas)
  tables/5c_finbert.parquet           — label+score FinBERT por frase
  tables/5c_esg9.parquet              — label+score FinBERT-ESG-9 por frase
  tables/5c_doc_agregado.csv          — agregados a nivel documento (289 filas)
  figures/5c_lm_ratios.png
  figures/5c_climate_share.png
  figures/5c_finbert_sentiment.png
  figures/5c_esg9_distribucion.png

Resumible: cada paso comprueba si su output existe y lo carga (usar --fresh para regenerar).

Uso:
  conda run -n tfg-ade python scripts/nlp/fase5c_sentimiento.py                    # todo el pipeline
  conda run -n tfg-ade python scripts/nlp/fase5c_sentimiento.py --paso frases
  conda run -n tfg-ade python scripts/nlp/fase5c_sentimiento.py --paso lm
  conda run -n tfg-ade python scripts/nlp/fase5c_sentimiento.py --paso climate_detector
  conda run -n tfg-ade python scripts/nlp/fase5c_sentimiento.py --paso climate_sub
  conda run -n tfg-ade python scripts/nlp/fase5c_sentimiento.py --paso finbert
  conda run -n tfg-ade python scripts/nlp/fase5c_sentimiento.py --paso esg9
  conda run -n tfg-ade python scripts/nlp/fase5c_sentimiento.py --paso agregar
  conda run -n tfg-ade python scripts/nlp/fase5c_sentimiento.py --fresh            # ignora checkpoints
"""

import argparse
import gc
import re
import warnings
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parents[2]
CORPUS   = BASE_DIR / "data" / "processed" / "corpus.parquet"
LM_DICT  = BASE_DIR / "data" / "external" / "diccionarios" / "LoughranMcDonald_MasterDictionary.csv"
TABLES   = BASE_DIR / "results" / "tables"
FIGURES  = BASE_DIR / "results" / "figures"
LOG_FILE = BASE_DIR / "results" / "5c_progress.log"

for d in (TABLES, FIGURES):
    d.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=0.95)

MIN_WORDS_SENT = 4   # frases más cortas (encabezados, viñetas) se descartan
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


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


# ─── paso 1: segmentación en frases ────────────────────────────────────────────

def segmentar_frases() -> pd.DataFrame:
    out = TABLES / "5c_frases_base.parquet"
    if out.exists():
        log(f"[1/6] Frases ya segmentadas → cargando {out.name}")
        return pd.read_parquet(out)

    log("[1/6] Cargando corpus…")
    corpus = pd.read_parquet(CORPUS)
    sus = corpus[corpus["seccion"] == "sus"].reset_index(drop=True)
    log(f"  {len(sus)} documentos sus cargados")

    import spacy
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    nlp.max_length = 3_000_000  # solo sentencizer (rule-based), sin parser/NER → seguro

    log("[1/6] Segmentando en frases (spaCy sentencizer, rule-based)…")
    rows = []
    n = len(sus)
    for i, r in sus.iterrows():
        doc = nlp(r["clean_text"])
        for sent_idx, sent in enumerate(doc.sents):
            text = sent.text.strip()
            n_words = len(text.split())
            if n_words < MIN_WORDS_SENT:
                continue
            rows.append({
                "doc_id": r["id"], "empresa": r["empresa"], "año": r["año"],
                "confianza": r["confianza"], "sent_idx": sent_idx, "text": text,
                "n_words": n_words,
            })
        if (i + 1) % 10 == 0 or (i + 1) == n:
            progress(i + 1, n, "Segmentando docs")

    df = pd.DataFrame(rows)
    log(f"  {len(df):,} frases totales (≥{MIN_WORDS_SENT} palabras)  |  media {len(df)/n:.0f}/doc")
    df.to_parquet(out)
    log(f"  → {out.name}")
    return df


# ─── paso 2: Loughran-McDonald ─────────────────────────────────────────────────

def aplicar_lm(frases: pd.DataFrame) -> pd.DataFrame:
    out = TABLES / "5c_frases.parquet"
    if out.exists():
        log(f"[2/6] LM ya aplicado → cargando {out.name}")
        return pd.read_parquet(out)

    log("[2/6] Cargando diccionario Loughran-McDonald…")
    lm = pd.read_csv(LM_DICT)
    categorias = ["Negative", "Positive", "Uncertainty", "Litigious",
                   "Strong_Modal", "Weak_Modal", "Constraining"]
    word_sets = {}
    for cat in categorias:
        word_sets[cat] = set(lm.loc[lm[cat] != 0, "Word"].str.lower())
        log(f"  {cat}: {len(word_sets[cat])} términos")

    log("[2/6] Calculando ratios LM por frase…")
    n = len(frases)
    counts = {cat: np.zeros(n, dtype=np.float32) for cat in categorias}
    for i, text in enumerate(frases["text"]):
        words = re.findall(r"[a-z']+", text.lower())
        if not words:
            continue
        wlen = len(words)
        for cat in categorias:
            ws = word_sets[cat]
            counts[cat][i] = sum(1 for w in words if w in ws) / wlen
        if (i + 1) % 20000 == 0 or (i + 1) == n:
            progress(i + 1, n, "LM")

    df = frases.copy()
    for cat in categorias:
        df[f"lm_{cat.lower()}"] = counts[cat]
    df.to_parquet(out)
    log(f"  → {out.name}")
    return df


# ─── pipeline genérico de clasificación HF ─────────────────────────────────────

def clasificar(frases: pd.DataFrame, model_name: str, label_prefix: str,
                batch_size: int = 64, max_length: int = 96, log_every: int = 20) -> pd.DataFrame:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    log(f"  Cargando modelo {model_name} en {DEVICE} (fp16, max_length={max_length})…")
    tok = AutoTokenizer.from_pretrained(model_name)
    mdl = AutoModelForSequenceClassification.from_pretrained(model_name).to(DEVICE).half()
    mdl.eval()
    id2label = mdl.config.id2label

    texts = frases["text"].tolist()
    n = len(texts)
    n_batches = (n + batch_size - 1) // batch_size
    labels, scores = [], []

    with torch.no_grad():
        for b in range(n_batches):
            batch = texts[b * batch_size:(b + 1) * batch_size]
            enc = tok(batch, padding=True, truncation=True, max_length=max_length,
                      return_tensors="pt").to(DEVICE)
            logits = mdl(**enc).logits
            probs = torch.softmax(logits, dim=-1)
            top = probs.argmax(dim=-1)
            labels.extend(id2label[int(t)] for t in top)
            scores.extend(float(probs[i, t]) for i, t in enumerate(top))
            if (b + 1) % log_every == 0 or (b + 1) == n_batches:
                done = min((b + 1) * batch_size, n)
                progress(b + 1, n_batches, label_prefix, f"({done:,}/{n:,} frases)")

    result = pd.DataFrame({
        "doc_id": frases["doc_id"].values,
        "sent_idx": frases["sent_idx"].values,
        f"{label_prefix}_label": labels,
        f"{label_prefix}_score": scores,
    })

    del mdl, tok
    gc.collect()
    if DEVICE == "mps":
        torch.mps.empty_cache()

    return result


# ─── paso 3: ClimateBERT cascada ───────────────────────────────────────────────

def climate_detector(frases: pd.DataFrame) -> pd.DataFrame:
    out = TABLES / "5c_climate_detector.parquet"
    if out.exists():
        log(f"[3a/6] climate-detector ya calculado → cargando {out.name}")
        return pd.read_parquet(out)

    log("[3a/6] ClimateBERT — climate-detector (todas las frases)…")
    df = clasificar(frases, "climatebert/distilroberta-base-climate-detector",
                     "climate_detector")
    df.to_parquet(out)
    log(f"  → {out.name}")
    n_climate = (df["climate_detector_label"].str.lower() == "yes").sum()
    log(f"  Frases climáticas: {n_climate:,} / {len(df):,} ({n_climate/len(df)*100:.1f}%)")
    return df


def climate_sub(frases: pd.DataFrame, detector: pd.DataFrame) -> pd.DataFrame:
    out = TABLES / "5c_climate_sub.parquet"
    if out.exists():
        log(f"[3b/6] climate-sub ya calculado → cargando {out.name}")
        return pd.read_parquet(out)

    mask = detector["climate_detector_label"].str.lower() == "yes"
    sub = frases[mask.values].reset_index(drop=True)
    log(f"[3b/6] ClimateBERT — sentiment/commitment/specificity sobre "
        f"{len(sub):,} frases climáticas ({len(sub)/len(frases)*100:.1f}% del total)…")

    res = sub[["doc_id", "sent_idx"]].copy()
    for model_name, prefix in [
        ("climatebert/distilroberta-base-climate-sentiment", "climate_sentiment"),
        ("climatebert/distilroberta-base-climate-commitment", "climate_commitment"),
        ("climatebert/distilroberta-base-climate-specificity", "climate_specificity"),
    ]:
        r = clasificar(sub, model_name, prefix)
        res = res.merge(r, on=["doc_id", "sent_idx"])

    res.to_parquet(out)
    log(f"  → {out.name}")
    return res


# ─── paso 4: FinBERT ────────────────────────────────────────────────────────────

def finbert(frases: pd.DataFrame) -> pd.DataFrame:
    out = TABLES / "5c_finbert.parquet"
    if out.exists():
        log(f"[4/6] FinBERT ya calculado → cargando {out.name}")
        return pd.read_parquet(out)

    log("[4/6] FinBERT (ProsusAI) — sentimiento financiero (todas las frases)…")
    df = clasificar(frases, "ProsusAI/finbert", "finbert")
    df.to_parquet(out)
    log(f"  → {out.name}")
    return df


# ─── paso 5: FinBERT-ESG-9 ──────────────────────────────────────────────────────

def esg9(frases: pd.DataFrame) -> pd.DataFrame:
    out = TABLES / "5c_esg9.parquet"
    if out.exists():
        log(f"[5/6] FinBERT-ESG-9 ya calculado → cargando {out.name}")
        return pd.read_parquet(out)

    log("[5/6] FinBERT-ESG-9 (yiyanghkust) — categoría ESG (todas las frases)…")
    df = clasificar(frases, "yiyanghkust/finbert-esg-9-categories", "esg9")
    df.to_parquet(out)
    log(f"  → {out.name}")
    return df


# ─── paso 6: agregación a nivel documento ──────────────────────────────────────

def agregar(frases: pd.DataFrame, detector: pd.DataFrame, sub: pd.DataFrame,
            fb: pd.DataFrame, esg: pd.DataFrame) -> pd.DataFrame:
    log("[6/6] Agregando a nivel documento…")

    base = frases[["doc_id", "empresa", "año", "confianza", "sent_idx",
                    "lm_negative", "lm_positive", "lm_uncertainty", "lm_litigious",
                    "lm_strong_modal", "lm_weak_modal", "lm_constraining"]].copy()
    base = base.merge(detector[["doc_id", "sent_idx", "climate_detector_label"]],
                       on=["doc_id", "sent_idx"], how="left")
    base = base.merge(fb[["doc_id", "sent_idx", "finbert_label"]],
                       on=["doc_id", "sent_idx"], how="left")
    base = base.merge(esg[["doc_id", "sent_idx", "esg9_label"]],
                       on=["doc_id", "sent_idx"], how="left")
    base = base.merge(sub, on=["doc_id", "sent_idx"], how="left")

    g = base.groupby(["doc_id", "empresa", "año", "confianza"])

    agg = g.agg(
        n_frases=("sent_idx", "count"),
        lm_negative=("lm_negative", "mean"),
        lm_positive=("lm_positive", "mean"),
        lm_uncertainty=("lm_uncertainty", "mean"),
        lm_litigious=("lm_litigious", "mean"),
        lm_strong_modal=("lm_strong_modal", "mean"),
        lm_weak_modal=("lm_weak_modal", "mean"),
        lm_constraining=("lm_constraining", "mean"),
    ).reset_index()

    # proporción de frases climáticas
    agg["pct_climate"] = g["climate_detector_label"].apply(
        lambda x: (x.str.lower() == "yes").mean()).values

    # distribución FinBERT (positive/negative/neutral)
    for lbl in ["positive", "negative", "neutral"]:
        agg[f"finbert_pct_{lbl}"] = g["finbert_label"].apply(
            lambda x, lbl=lbl: (x.str.lower() == lbl).mean()).values
    agg["finbert_tone"] = agg["finbert_pct_positive"] - agg["finbert_pct_negative"]

    # distribución climate-sentiment / commitment / specificity (sobre frases climáticas)
    for col, name in [("climate_sentiment_label", "climate_sentiment"),
                       ("climate_commitment_label", "climate_commitment"),
                       ("climate_specificity_label", "climate_specificity")]:
        dist = base.dropna(subset=[col]).groupby(["doc_id", "empresa", "año", "confianza"])[col] \
            .value_counts(normalize=True).unstack(fill_value=0)
        dist.columns = [f"{name}_{c.lower()}" for c in dist.columns]
        agg = agg.merge(dist.reset_index(), on=["doc_id", "empresa", "año", "confianza"], how="left")

    # distribución ESG-9
    esg_dist = base.groupby(["doc_id", "empresa", "año", "confianza"])["esg9_label"] \
        .value_counts(normalize=True).unstack(fill_value=0)
    esg_dist.columns = [f"esg9_{c.lower().replace(' ', '_').replace('&', 'and')}" for c in esg_dist.columns]
    agg = agg.merge(esg_dist.reset_index(), on=["doc_id", "empresa", "año", "confianza"], how="left")

    out = TABLES / "5c_doc_agregado.csv"
    agg.to_csv(out, index=False)
    log(f"  {len(agg)} documentos agregados → {out.name}")
    return agg


# ─── figuras ────────────────────────────────────────────────────────────────────

def generar_figuras(agg: pd.DataFrame) -> None:
    log("Generando figuras…")

    # 1. Ratios LM por año
    lm_cols = ["lm_negative", "lm_positive", "lm_uncertainty", "lm_litigious",
               "lm_strong_modal", "lm_weak_modal", "lm_constraining"]
    melted = agg.melt(id_vars=["año"], value_vars=lm_cols, var_name="categoria", value_name="ratio")
    melted["categoria"] = melted["categoria"].str.replace("lm_", "")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=melted, x="categoria", y="ratio", hue="año", ax=ax)
    ax.set_title("Ratios Loughran-McDonald por categoría y año (sección sus)")
    ax.set_ylabel("Proporción de palabras por frase")
    plt.xticks(rotation=20)
    fig.tight_layout()
    fig.savefig(FIGURES / "5c_lm_ratios.png", dpi=150)
    plt.close(fig)

    # 2. % frases climáticas por año
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(data=agg, x="año", y="pct_climate", ax=ax, errorbar="sd")
    ax.set_title("% de frases clasificadas como climáticas (ClimateBERT detector)")
    ax.set_ylabel("Proporción de frases")
    fig.tight_layout()
    fig.savefig(FIGURES / "5c_climate_share.png", dpi=150)
    plt.close(fig)

    # 3. Tono FinBERT por año
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=agg, x="año", y="finbert_tone", ax=ax)
    ax.axhline(0, color="grey", linestyle="--", linewidth=1)
    ax.set_title("Tono FinBERT (% positivo − % negativo) por año")
    fig.tight_layout()
    fig.savefig(FIGURES / "5c_finbert_sentiment.png", dpi=150)
    plt.close(fig)

    # 4. Distribución ESG-9 por año
    esg_cols = [c for c in agg.columns if c.startswith("esg9_")]
    melted = agg.melt(id_vars=["año"], value_vars=esg_cols, var_name="categoria", value_name="proporcion")
    melted["categoria"] = melted["categoria"].str.replace("esg9_", "")
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.barplot(data=melted, x="categoria", y="proporcion", hue="año", ax=ax, errorbar=None)
    ax.set_title("Distribución de categorías FinBERT-ESG-9 por año (sección sus)")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(FIGURES / "5c_esg9_distribucion.png", dpi=150)
    plt.close(fig)

    log("  → 5c_lm_ratios.png / 5c_climate_share.png / 5c_finbert_sentiment.png / 5c_esg9_distribucion.png")


# ─── main ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paso", choices=["frases", "lm", "climate_detector", "climate_sub",
                                        "finbert", "esg9", "agregar", "todo"], default="todo")
    ap.add_argument("--fresh", action="store_true", help="ignora checkpoints y regenera todo")
    args = ap.parse_args()

    if args.fresh:
        for f in TABLES.glob("5c_*"):
            f.unlink()
        log("--fresh: checkpoints 5c_* eliminados")

    t0 = datetime.now()

    frases_base = segmentar_frases()
    if args.paso == "frases":
        return

    frases = aplicar_lm(frases_base)
    if args.paso == "lm":
        return

    detector = climate_detector(frases)
    if args.paso == "climate_detector":
        return

    sub = climate_sub(frases, detector)
    if args.paso == "climate_sub":
        return

    fb = finbert(frases)
    if args.paso == "finbert":
        return

    esg = esg9(frases)
    if args.paso == "esg9":
        return

    agg = agregar(frases, detector, sub, fb, esg)
    generar_figuras(agg)

    dt = (datetime.now() - t0).total_seconds() / 60
    log(f"✓ Fase 5C completa en {dt:.1f} min")
    log(f"  Tablas  → {TABLES}")
    log(f"  Figuras → {FIGURES}")


if __name__ == "__main__":
    main()
