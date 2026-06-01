"""
Fase 4 — Bloque 4B: detección de idioma de cada informe.

Lee los .txt de data/interim/ (generados en 4A), detecta el idioma con langdetect
sobre los primeros 5000 caracteres con contenido (Paso 4.5) y vuelca:
  - data/interim/idiomas.csv  — tabla por documento (id, ticker, año, idioma, confianza)
  - docs/fase4_idiomas.md     — informe legible con la distribución de idiomas

No traduce ni decide nada: solo detecta y reporta para que el estudiante decida
la estrategia 4B (traducir vs. multilingüe) viendo la distribución real.

Uso:
  python scripts/extraction/fase4_idioma.py
"""

import re
from collections import Counter
from datetime import date
from pathlib import Path

import pandas as pd
from langdetect import DetectorFactory, detect_langs

DetectorFactory.seed = 42  # reproducibilidad (convención del proyecto: random_state=42)

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM_DIR = BASE_DIR / "data" / "interim"
LOG_PATH = INTERIM_DIR / "extraccion_log.csv"
OUT_CSV = INTERIM_DIR / "idiomas.csv"
OUT_MD = BASE_DIR / "docs" / "fase4_idiomas.md"

N_CHARS = 5000   # ventana de detección (Paso 4.5)
N_VENTANAS = 9   # nº de ventanas repartidas por el documento para votar idioma
TAM_VENTANA = 3000
CONF_MIN = 0.90  # confianza mínima de langdetect para que una ventana cuente

NOMBRE_IDIOMA = {
    "en": "Inglés", "es": "Español", "de": "Alemán", "fr": "Francés",
    "it": "Italiano", "nl": "Neerlandés", "da": "Danés", "sv": "Sueco",
    "fi": "Finés", "no": "Noruego", "pt": "Portugués", "ca": "Catalán",
}


# Palabras función por idioma (para medir legibilidad en el idioma correcto)
STOPWORDS = {
    "en": {"the", "and", "of", "to", "in", "that", "for", "with", "is", "are"},
    "fr": {"le", "la", "les", "de", "des", "et", "que", "pour", "dans", "est"},
    "es": {"el", "la", "los", "las", "de", "que", "en", "para", "con", "es"},
    "de": {"der", "die", "das", "und", "von", "den", "mit", "für", "ist", "im"},
    "it": {"il", "la", "di", "che", "per", "con", "del", "una", "sono", "nel"},
    "nl": {"de", "het", "en", "van", "een", "voor", "met", "dat", "is", "op"},
    "sv": {"och", "att", "det", "som", "för", "med", "den", "är", "av", "till"},
    "da": {"og", "at", "det", "som", "for", "med", "den", "er", "af", "til"},
    "fi": {"ja", "on", "että", "ovat", "sekä", "joka", "ovat", "tai", "kuin", "myös"},
}


def calidad_texto(texto: str, idioma: str) -> tuple[float, float]:
    """Devuelve (densidad palabras-función en el idioma detectado, ratio caracteres de control).

    Señales de extracción corrupta (fuente con CMap rota / sin ToUnicode):
    muchos caracteres de control (señal agnóstica al idioma) y/o casi 0%
    palabras función reales del idioma del documento."""
    ctrl = sum(1 for c in texto if ord(c) < 32 and c not in "\n\t\r") / max(len(texto), 1)
    sw = STOPWORDS.get(idioma, STOPWORDS["en"])
    toks = re.findall(r"[a-zà-öø-ÿ]+", texto.lower())
    fw = sum(1 for t in toks if t in sw) / max(len(toks), 1)
    return fw, ctrl


def detectar_idioma(texto: str) -> tuple[str, float]:
    """Detecta idioma por voto de varias ventanas repartidas por el documento.

    Robusto a secciones corruptas (portadas con fuentes rotas): cada ventana
    vota su idioma si la confianza ≥ CONF_MIN; se devuelve el idioma mayoritario
    y la fracción de ventanas que lo apoyan."""
    t = texto.strip()
    if not t:
        return "??", 0.0
    if len(t) <= TAM_VENTANA:
        ventanas = [t]
    else:
        paso = max((len(t) - TAM_VENTANA) // (N_VENTANAS - 1), 1)
        ventanas = [t[i:i + TAM_VENTANA] for i in range(0, len(t) - TAM_VENTANA + 1, paso)][:N_VENTANAS]
    votos = []
    for w in ventanas:
        try:
            top = detect_langs(w)[0]
            if top.prob >= CONF_MIN:
                votos.append(top.lang)
        except Exception:
            pass
    if not votos:
        return "??", 0.0
    idioma, n = Counter(votos).most_common(1)[0]
    return idioma, round(n / len(votos), 3)


def main():
    log = pd.read_csv(LOG_PATH, dtype=str)
    log = log[log["estado"] == "ok"].copy()

    registros = []
    for _, fila in log.iterrows():
        txt_path = BASE_DIR / fila["txt_path"]
        if not txt_path.exists():
            print(f"[aviso] falta {txt_path.name}")
            continue
        texto = txt_path.read_text(encoding="utf-8")
        idioma, conf = detectar_idioma(texto)
        fw, ctrl = calidad_texto(texto[:50000], idioma)
        # Flag de extracción dudosa: muchos caracteres de control (agnóstico al idioma)
        # o casi nula densidad de palabras función en el idioma detectado.
        extraccion_ok = ctrl < 0.02 and fw >= 0.03
        registros.append({
            "id_empresa": fila["id_empresa"], "ticker": fila["ticker"],
            "pais": fila["pais"], "año": fila["año"],
            "idioma": idioma, "confianza": conf,
            "extraccion_ok": extraccion_ok,
            "palabras_funcion": round(fw, 3), "ratio_control": round(ctrl, 4),
        })

    df = pd.DataFrame(registros).sort_values(["id_empresa", "año"])
    df.to_csv(OUT_CSV, index=False)

    # --- Distribución ---
    dist = df["idioma"].value_counts()
    baja_conf = df[df["confianza"] < 1.0].sort_values("confianza")
    extr_mala = df[~df["extraccion_ok"]].sort_values("palabras_funcion")

    print("\n=== Distribución de idiomas (289 informes) ===")
    for idi, n in dist.items():
        print(f"  {idi} ({NOMBRE_IDIOMA.get(idi, '?')}): {n}")
    print(f"\nVoto de idioma no unánime entre ventanas: {len(baja_conf)}")
    print(f"Extracción dudosa (CMap rota / caracteres de control): {len(extr_mala)}")
    for _, r in extr_mala.iterrows():
        print(f"  ⚠ {r.id_empresa} {r.ticker} {r.año}: palabras_func={r.palabras_funcion}, ctrl={r.ratio_control}")

    # --- Informe Markdown ---
    total = len(df)
    lineas = [
        "# Fase 4B — Detección de idioma de los informes",
        "",
        f"> Generado el {date.today()} por `scripts/extraction/fase4_idioma.py`.",
        f"> Detección con `langdetect` por **voto de {N_VENTANAS} ventanas** de {TAM_VENTANA} caracteres "
        "repartidas por cada documento (robusto a portadas/secciones con fuentes corruptas).",
        f"> Corpus: **{total} informes** (97 empresas × 3 años − DIA 2022 y NEM 2022 descartados).",
        "",
        "## Distribución de idiomas",
        "",
        "| Idioma | Código | Informes | % |",
        "|--------|--------|---------:|----:|",
    ]
    for idi, n in dist.items():
        lineas.append(f"| {NOMBRE_IDIOMA.get(idi, '?')} | `{idi}` | {n} | {100*n/total:.1f}% |")

    # Distribución por país (informativo: ¿el idioma sigue al país?)
    lineas += ["", "## Idiomas por país", "",
               "| País | Idiomas (nº informes) |", "|------|----------------------|"]
    for pais, sub in df.groupby("pais"):
        c = Counter(sub["idioma"])
        detalle = ", ".join(f"{k}×{v}" for k, v in c.most_common())
        lineas.append(f"| {pais} | {detalle} |")

    # Empresas que NO reportan en inglés (relevante para la decisión de traducción)
    no_en = df[df["idioma"] != "en"].sort_values(["pais", "id_empresa", "año"])
    lineas += ["", f"## Informes NO en inglés ({len(no_en)} de {total})", ""]
    if len(no_en):
        lineas += ["| id | ticker | país | año | idioma | confianza |",
                   "|----|--------|------|-----|--------|-----------|"]
        for _, r in no_en.iterrows():
            lineas.append(f"| {r.id_empresa} | {r.ticker} | {r.pais} | {r.año} | "
                          f"`{r.idioma}` ({NOMBRE_IDIOMA.get(r.idioma,'?')}) | {r.confianza} |")
    else:
        lineas.append("_Todos los informes están en inglés._")

    # Calidad de extracción (problema de Fase 4A, no de idioma)
    lineas += ["", f"## ⚠ Calidad de extracción: {len(extr_mala)} informe(s) con texto corrupto", "",
               "Detectados por baja densidad de palabras función reales y/o exceso de caracteres "
               "de control → fuentes con CMap rota (sin mapa ToUnicode). El idioma mostrado es el de "
               "las secciones legibles. **Requiere remediación 4A** (OCR con Tesseract o re-descarga "
               "de una copia con capa de texto correcta).", ""]
    if len(extr_mala):
        lineas += ["| id | ticker | país | año | idioma | palabras_función | ratio_control |",
                   "|----|--------|------|-----|--------|-----------------:|--------------:|"]
        for _, r in extr_mala.iterrows():
            lineas.append(f"| {r.id_empresa} | {r.ticker} | {r.pais} | {r.año} | `{r.idioma}` | "
                          f"{r.palabras_funcion} | {r.ratio_control} |")
    else:
        lineas.append("_Ninguno: todas las extracciones son legibles._")

    # Voto de idioma no unánime (posibles documentos bilingües o con secciones corruptas)
    lineas += ["", f"## Voto de idioma no unánime entre ventanas: {len(baja_conf)}", "",
               "Fracción de ventanas que apoyan el idioma mayoritario < 1.0. "
               "Puede indicar documentos bilingües o con secciones corruptas/tabulares.", ""]
    if len(baja_conf):
        lineas += ["| id | ticker | año | idioma | % ventanas de acuerdo |",
                   "|----|--------|-----|--------|----------------------:|"]
        for _, r in baja_conf.iterrows():
            lineas.append(f"| {r.id_empresa} | {r.ticker} | {r.año} | `{r.idioma}` | {r.confianza} |")
    else:
        lineas.append("_Ninguna: voto unánime en todos los documentos._")

    # Implicación para la decisión 4B
    pct_en = 100 * dist.get("en", 0) / total
    lineas += [
        "", "## Implicación para la decisión 4B (traducir vs. multilingüe)", "",
        f"- **{pct_en:.1f}%** del corpus ya está en inglés.",
        f"- **{len(no_en)}** informes requerirían traducción si se opta por herramientas English-only "
        "(Loughran-McDonald, FinBERT — ver Decisión 001).",
        "- Alternativa: modelos multilingües (XLM-RoBERTa, mBERT) que evitan la traducción.",
        "", "_Decisión pendiente de confirmar con el estudiante/tutor._", "",
    ]

    OUT_MD.write_text("\n".join(lineas), encoding="utf-8")
    print(f"\nCSV:  {OUT_CSV.relative_to(BASE_DIR)}")
    print(f"Informe: {OUT_MD.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
