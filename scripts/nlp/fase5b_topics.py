"""
Fase 5B — Topic Modeling: LDA baseline + BERTopic

Pipeline:
  1. Segmentación: cada doc sus → párrafos (líneas ≥ 20 palabras)
  2. LDA (gensim LdaMulticore): selección automática de K por coherencia Cv (rango 5-30)
  3. BERTopic (sentence-transformers + UMAP + HDBSCAN, MPS): asignación y topics_over_time
  4. Exportación de tablas, figuras y modelos

Outputs:
  tables/5b_paragrafos.parquet        — párrafos segmentados con metadatos
  tables/5b_lda_coherencia.csv        — scores Cv por K
  tables/5b_lda_topics.csv            — palabras top-15 por topic LDA (K óptimo)
  tables/5b_lda_doc_topics.csv        — distribución topic por documento
  tables/5b_bertopic_topics.csv       — palabras + representación por topic BERTopic
  tables/5b_bertopic_para_topics.parquet — topic asignado a cada párrafo
  tables/5b_topics_over_time.csv      — frecuencia de topics por año (BERTopic)
  figures/5b_lda_coherencia.png
  figures/5b_lda_topics_barplot.png
  figures/5b_bertopic_barchart.png
  figures/5b_topics_over_time.png
  models/lda_k{K}/                    — modelo gensim serializado
  models/bertopic_sus/                — modelo BERTopic serializado

Uso:
  conda run -n tfg-ade python scripts/nlp/fase5b_topics.py
  conda run -n tfg-ade python scripts/nlp/fase5b_topics.py --modelo lda
  conda run -n tfg-ade python scripts/nlp/fase5b_topics.py --modelo bertopic
  conda run -n tfg-ade python scripts/nlp/fase5b_topics.py --k_fijo 15  # saltar coherencia
"""

import argparse
import re
import ssl
import time
import warnings
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

# SSL workaround para NLTK en macOS
try:
    _create_unverified = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified

import nltk
nltk.download("stopwords", quiet=True)
from nltk.corpus import stopwords as nltk_sw

BASE_DIR = Path(__file__).resolve().parents[2]
CORPUS   = BASE_DIR / "data" / "processed" / "corpus.parquet"
TABLES   = BASE_DIR / "results" / "tables"
FIGURES  = BASE_DIR / "results" / "figures"
MODELS   = BASE_DIR / "results" / "models"
LOG_FILE = BASE_DIR / "results" / "5b_progress.log"

for d in (TABLES, FIGURES, MODELS):
    d.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=0.95)

STOPWORDS = nltk_sw.words("english") + [
    "report", "annual", "information", "company", "group", "business",
    "year", "include", "provide", "also", "following", "see", "page",
    "table", "section", "appendix", "non", "note", "number", "total",
    "based", "may", "well", "within", "across", "given", "part",
    "accordance", "pursuant", "respect",
    "statement", "document", "registration", "universal",
]
STOPWORDS_SET = set(STOPWORDS)

MIN_WORDS_PARA = 20


class _PrecomputedUMAP:
    """Devuelve embeddings UMAP pre-computados a BERTopic (evita doble fit y es serializable)."""
    def __init__(self, emb):
        self._emb = emb
    def fit(self, X, y=None):
        return self
    def fit_transform(self, X, y=None):
        return self._emb
    def transform(self, X):
        return self._emb


# ─── utilidades de progreso ────────────────────────────────────────────────────

def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log(msg: str) -> None:
    """Escribe msg a stdout Y al fichero de log (tail -f results/5b_progress.log)."""
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
    # Al llegar al 100% o en múltiplos de 10% escribe al log
    if current == total or int(pct * 10) > int((current - 1) / total * 10):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line.strip() + "\n")
    if current == total:
        print()


# ─── segmentación ──────────────────────────────────────────────────────────────

def segmentar_corpus(df: pd.DataFrame) -> pd.DataFrame:
    rows  = []
    total = len(df)
    for i, (_, doc) in enumerate(df.iterrows()):
        for j, line in enumerate(doc["clean_text"].split("\n")):
            line = line.strip()
            if len(line.split()) >= MIN_WORDS_PARA:
                rows.append({
                    "doc_id":    doc["id"],
                    "empresa":   doc["empresa"],
                    "año":       doc["año"],
                    "confianza": doc["confianza"],
                    "para_idx":  j,
                    "text":      line,
                })
        if (i + 1) % 10 == 0 or (i + 1) == total:
            progress(i + 1, total, "Segmentando docs")
    return pd.DataFrame(rows)


def tokenizar(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]{3,}", text.lower())
            if w not in STOPWORDS_SET]


# ─── LDA ───────────────────────────────────────────────────────────────────────

def run_lda(paras: pd.DataFrame, k_fijo: int | None = None,
            k_min: int = 5, k_max: int = 30, k_step: int = 5) -> dict:
    from gensim import corpora
    from gensim.models import CoherenceModel, LdaMulticore

    texts_raw = paras["text"].tolist()
    total     = len(texts_raw)
    log(f"Tokenizando {total:,} párrafos para LDA…")
    texts = []
    for i, t in enumerate(texts_raw):
        texts.append(tokenizar(t))
        if (i + 1) % 5000 == 0 or (i + 1) == total:
            progress(i + 1, total, "Tokenizando")
    texts = [t for t in texts if len(t) >= 5]
    log(f"{len(texts):,} párrafos con ≥5 tokens tras filtrado")

    log("Construyendo diccionario y BoW…")
    dictionary  = corpora.Dictionary(texts)
    dictionary.filter_extremes(no_below=5, no_above=0.85)
    corpus_bow  = [dictionary.doc2bow(t) for t in texts]
    log(f"Vocabulario: {len(dictionary):,} términos")

    ks = [k_fijo] if k_fijo else list(range(k_min, k_max + 1, k_step))
    coherencias: dict = {}

    log(f"Búsqueda de K óptimo: {ks}  ({len(ks)} iteraciones)")
    for idx, k in enumerate(ks):
        t0 = time.time()
        log(f"[{idx+1}/{len(ks)}] LDA K={k} — entrenando (10 passes)…")
        mdl = LdaMulticore(
            corpus_bow, num_topics=k, id2word=dictionary,
            passes=10, workers=2, random_state=42,
            alpha="asymmetric", eta="auto",
        )
        log(f"[{idx+1}/{len(ks)}] LDA K={k} — calculando coherencia Cv…")
        cm    = CoherenceModel(model=mdl, texts=texts, dictionary=dictionary, coherence="c_v")
        score = cm.get_coherence()
        elapsed = time.time() - t0
        coherencias[k] = {"model": mdl, "score": score}
        log(f"[{idx+1}/{len(ks)}] K={k} ✓  Cv={score:.4f}  ({elapsed:.0f}s)  "
            f"[progreso global LDA: {(idx+1)/len(ks)*100:.0f}%]")

    best_k   = max(coherencias, key=lambda k: coherencias[k]["score"])
    best_mdl = coherencias[best_k]["model"]
    log(f"K óptimo = {best_k}  (Cv={coherencias[best_k]['score']:.4f})")

    model_dir = MODELS / f"lda_k{best_k}"
    model_dir.mkdir(exist_ok=True)
    best_mdl.save(str(model_dir / "model"))
    dictionary.save(str(model_dir / "dictionary"))
    log(f"Modelo guardado → {model_dir}")

    return {
        "model":       best_mdl,
        "dictionary":  dictionary,
        "corpus_bow":  corpus_bow,
        "texts":       texts,
        "coherencias": {k: v["score"] for k, v in coherencias.items()},
        "best_k":      best_k,
    }


def exportar_lda(res: dict, paras: pd.DataFrame):
    mdl, best_k = res["model"], res["best_k"]

    coh_df = (pd.DataFrame(list(res["coherencias"].items()), columns=["K", "coherencia_Cv"])
                .sort_values("K"))
    coh_df.to_csv(TABLES / "5b_lda_coherencia.csv", index=False)

    topic_rows = []
    for t in range(best_k):
        words = mdl.show_topic(t, topn=15)
        topic_rows.append({
            "topic":    t,
            "palabras": ", ".join(w for w, _ in words),
            "scores":   ", ".join(f"{s:.4f}" for _, s in words),
        })
    topics_df = pd.DataFrame(topic_rows)
    topics_df.to_csv(TABLES / "5b_lda_topics.csv", index=False)
    log(f"Topics LDA (K={best_k}):")
    for _, r in topics_df.iterrows():
        log(f"  T{int(r.topic):02d}: {r.palabras}")

    # Distribución topic × párrafo
    n_bow = len(res["corpus_bow"])
    log(f"Calculando distribución topic por párrafo ({n_bow:,} BoWs)…")
    doc_topics = []
    for i, bow in enumerate(res["corpus_bow"]):
        dists      = dict(mdl.get_document_topics(bow, minimum_probability=0))
        dists_full = [dists.get(t, 0.0) for t in range(best_k)]
        doc_topics.append(dists_full)
        if (i + 1) % 5000 == 0 or (i + 1) == n_bow:
            progress(i + 1, n_bow, "doc_topics")

    dt_df = pd.DataFrame(doc_topics, columns=[f"T{t:02d}" for t in range(best_k)])
    dt_df.to_csv(TABLES / "5b_lda_doc_topics.csv", index=False)

    # Figura coherencia
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(coh_df["K"], coh_df["coherencia_Cv"], marker="o", color="#4C72B0")
    ax.axvline(best_k, ls="--", color="tomato", label=f"K óptimo={best_k}")
    ax.set_xlabel("Número de topics (K)")
    ax.set_ylabel("Coherencia Cv")
    ax.set_title("Selección de K — LDA (sección sus)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "5b_lda_coherencia.png", dpi=150)
    plt.close(fig)

    # Figura palabras por topic
    n_show = min(best_k, 12)
    rows_p = 3 if n_show > 6 else 2
    cols_p = 4
    fig, axes = plt.subplots(rows_p, cols_p, figsize=(16, rows_p * 4))
    axes = axes.flatten()
    for t in range(n_show):
        words = mdl.show_topic(t, topn=10)
        ws, ss = zip(*words)
        axes[t].barh(list(reversed(ws)), list(reversed(ss)), color="#4C72B0")
        axes[t].set_title(f"Topic {t}", fontsize=10)
        axes[t].tick_params(labelsize=8)
    for ax in axes[n_show:]:
        ax.set_visible(False)
    fig.suptitle(f"LDA K={best_k} — top-10 palabras por topic (sus)", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIGURES / "5b_lda_topics_barplot.png", dpi=150)
    plt.close(fig)

    log("→ 5b_lda_coherencia.csv / 5b_lda_topics.csv / 5b_lda_doc_topics.csv")
    log("→ 5b_lda_coherencia.png / 5b_lda_topics_barplot.png")
    log("LDA COMPLETO ✓")


# ─── BERTopic ──────────────────────────────────────────────────────────────────

def run_bertopic(paras: pd.DataFrame) -> dict:
    import torch
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import CountVectorizer
    from umap import UMAP
    import hdbscan

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    docs   = paras["text"].tolist()
    years  = paras["año"].astype(str).tolist()

    log(f"Cargando modelo all-MiniLM-L6-v2 en {device}…")
    emb_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

    BATCH = 512
    n_batches = (len(docs) + BATCH - 1) // BATCH
    emb_cache = MODELS / "bertopic_sus_embeddings.npy"
    if emb_cache.exists():
        log(f"Cargando embeddings desde caché ({emb_cache.name})…")
        embeddings = np.load(str(emb_cache))
        log(f"Embeddings cargados: {embeddings.shape}")
    else:
        log(f"Generando embeddings para {len(docs):,} párrafos "
            f"(batch={BATCH}, {n_batches} batches)…")
        chunks = []
        for i in range(n_batches):
            batch = docs[i * BATCH : (i + 1) * BATCH]
            chunks.append(emb_model.encode(batch, convert_to_numpy=True, show_progress_bar=False))
            # Log cada 10 batches (~5% del total)
            if (i + 1) % 10 == 0 or (i + 1) == n_batches:
                done = (i + 1) * BATCH if (i + 1) < n_batches else len(docs)
                progress(i + 1, n_batches, "Embeddings")
                log(f"  batch {i+1}/{n_batches}  ({done:,}/{len(docs):,} párrafos)")
        embeddings = np.vstack(chunks)
        np.save(str(emb_cache), embeddings)
        log(f"Embeddings listos: {embeddings.shape}  (guardados en caché)")

    log("Ajustando BERTopic — 1/3: UMAP (384→5 dims, ~2-3 min)…")
    umap_real = UMAP(
        n_neighbors=15, n_components=5,
        min_dist=0.0, metric="cosine",
        random_state=42, low_memory=True,
    )
    umap_embeddings = umap_real.fit_transform(embeddings)
    log(f"UMAP listo: {umap_embeddings.shape}")

    log("Ajustando BERTopic — 2/3: HDBSCAN (clustering)…")
    hdb_model = hdbscan.HDBSCAN(
        min_cluster_size=50, min_samples=10,
        metric="euclidean", cluster_selection_method="eom",
        prediction_data=True,
    )
    vec_model = CountVectorizer(
        stop_words=list(STOPWORDS_SET),
        ngram_range=(1, 2), min_df=5,
        token_pattern=r"[a-z]{3,}",
    )
    log("Ajustando BERTopic — 3/3: fit_transform + c-TF-IDF…")
    topic_model = BERTopic(
        umap_model=_PrecomputedUMAP(umap_embeddings),
        hdbscan_model=hdb_model,
        vectorizer_model=vec_model,
        top_n_words=15,
        verbose=True,
        calculate_probabilities=False,
    )
    topics, _ = topic_model.fit_transform(docs, embeddings)
    n_topics  = len(set(t for t in topics if t != -1))
    log(f"BERTopic listo: {n_topics} topics, "
        f"{topics.count(-1):,} outliers ({topics.count(-1)/len(topics)*100:.1f}%)")

    # Guardar modelo y para_topics antes de tot (evita perder todo si tot falla)
    model_dir = MODELS / "bertopic_sus"
    model_dir.mkdir(exist_ok=True)
    topic_model.save(str(model_dir / "bertopic_model"))
    log(f"Modelo BERTopic guardado → {model_dir / 'bertopic_model'}")

    log("Calculando topics_over_time (implementación manual, compatible pandas 2.x)…")
    # BERTopic 0.17.4 usa pd.to_datetime(infer_datetime_format=...) eliminado en pandas 2.x
    # Implementamos manualmente: frecuencia de topics por año
    _para = paras.copy()
    _para["topic"] = topics
    tot = (_para.groupby(["año", "topic"])
                .size()
                .reset_index(name="Frequency")
                .rename(columns={"año": "Timestamp", "topic": "Topic"}))
    tot = tot[tot["Topic"] != -1]  # excluir outliers
    log(f"topics_over_time listo: {len(tot)} filas (año × topic)")

    return {
        "model":      topic_model,
        "topics":     topics,
        "embeddings": embeddings,
        "years":      years,
        "tot":        tot,
        "docs":       docs,
    }


def exportar_bertopic(res: dict, paras: pd.DataFrame):
    topic_model = res["model"]
    topics      = res["topics"]
    tot         = res["tot"]
    n_topics    = len(set(t for t in topics if t != -1))
    n_outlier   = topics.count(-1)
    n_total     = len(topics)

    log(f"Resumen BERTopic: {n_topics} topics | "
        f"outliers: {n_outlier:,}/{n_total:,} ({n_outlier/n_total*100:.1f}%)")

    info = topic_model.get_topic_info()
    info.to_csv(TABLES / "5b_bertopic_topics.csv", index=False)

    para_df = paras.copy()
    para_df["topic"] = topics
    para_df.to_parquet(TABLES / "5b_bertopic_para_topics.parquet", index=False)

    tot.to_csv(TABLES / "5b_topics_over_time.csv", index=False)

    top_info = info[info["Topic"] != -1].head(20)
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.barplot(data=top_info, x="Count", y="Name", ax=ax, color="#4C72B0")
    ax.set_title(f"Top-20 topics BERTopic (sus, {n_topics} total)", fontsize=12)
    ax.set_xlabel("Frecuencia (párrafos)")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(FIGURES / "5b_bertopic_barchart.png", dpi=150)
    plt.close(fig)

    top10    = top_info.head(10)["Topic"].tolist()
    tot_top  = tot[tot["Topic"].isin(top10)]
    fig, ax  = plt.subplots(figsize=(11, 6))
    for t_id, grp in tot_top.groupby("Topic"):
        name  = info.loc[info["Topic"] == t_id, "Name"].values
        label = name[0] if len(name) else str(t_id)
        ax.plot(grp["Timestamp"].astype(str), grp["Frequency"], marker="o", label=label)
    ax.set_title("Topics over time — BERTopic (sección sus, top-10)", fontsize=12)
    ax.set_xlabel("Año")
    ax.set_ylabel("Frecuencia de párrafos")
    ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "5b_topics_over_time.png", dpi=150)
    plt.close(fig)

    log("→ 5b_bertopic_topics.csv / 5b_bertopic_para_topics.parquet")
    log("→ 5b_topics_over_time.csv")
    log("→ 5b_bertopic_barchart.png / 5b_topics_over_time.png")
    log("BERTopic COMPLETO ✓")


# ─── main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", choices=["lda", "bertopic", "ambos"], default="ambos")
    ap.add_argument("--k_fijo", type=int, default=None,
                    help="Fijar K para LDA (omite búsqueda por coherencia)")
    ap.add_argument("--k_min",  type=int, default=5)
    ap.add_argument("--k_max",  type=int, default=30)
    ap.add_argument("--k_step", type=int, default=5)
    args = ap.parse_args()

    t_total = time.time()
    # Reiniciar log al empezar
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(f"# Log Fase 5B — {datetime.now().isoformat()}\n", encoding="utf-8")
    log("Cargando corpus…")
    df  = pd.read_parquet(CORPUS)
    sus = df[df["seccion"] == "sus"].copy()
    log(f"{sus.shape[0]} documentos sus cargados")

    log(f"[1/3] Segmentando corpus (≥{MIN_WORDS_PARA} palabras/párrafo)…")
    paras = segmentar_corpus(sus)
    paras.to_parquet(TABLES / "5b_paragrafos.parquet", index=False)
    log(f"{len(paras):,} párrafos totales  |  media {len(paras)/sus.shape[0]:.0f}/doc")
    log(f"Por año: { paras.groupby('año').size().to_dict() }")
    log("→ 5b_paragrafos.parquet  [SEGMENTACIÓN COMPLETA 1/3]")

    n_pasos = sum([args.modelo in ("lda", "ambos"), args.modelo in ("bertopic", "ambos")])
    paso    = 1

    if args.modelo in ("lda", "ambos"):
        log(f"[{paso+1}/{n_pasos+1}] LDA — INICIO")
        paso += 1
        res_lda = run_lda(paras, k_fijo=args.k_fijo,
                          k_min=args.k_min, k_max=args.k_max, k_step=args.k_step)
        exportar_lda(res_lda, paras)

    if args.modelo in ("bertopic", "ambos"):
        log(f"[{paso+1}/{n_pasos+1}] BERTopic — INICIO")
        res_bt = run_bertopic(paras)
        exportar_bertopic(res_bt, paras)

    elapsed = time.time() - t_total
    log(f"✓ Fase 5B completa en {elapsed/60:.1f} min")
    log(f"Tablas  → {TABLES}")
    log(f"Figuras → {FIGURES}")
    log(f"Modelos → {MODELS}")


if __name__ == "__main__":
    main()
