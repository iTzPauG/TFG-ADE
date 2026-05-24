# TFG ADE — Guía de trabajo paso a paso

> **Objetivo:** Análisis de informes de sostenibilidad del STOXX Europe 600 mediante PLN (NLP) para detectar impression management / greenwashing bajo el marco regulatorio CSRD/ESRS.

---

## Índice de fases

| Fase | Descripción | Semanas |
|------|-------------|---------|
| [Fase 0](#fase-0-setup-técnico-inicial) | Setup técnico inicial | Días 1-3 |
| [Fase 1](#fase-1-marco-teórico-y-diseño-metodológico) | Marco teórico y diseño metodológico | Semanas 1-3 |
| [Fase 2](#fase-2-construcción-de-la-muestra) | Construcción de la muestra | Semana 4 |
| [Fase 3](#fase-3-recolección-de-informes) | Recolección de informes | Semanas 5-6 |
| [Fase 4](#fase-4-extracción-y-limpieza-de-texto) | Extracción y limpieza de texto | Semanas 7-8 |
| [Fase 5](#fase-5-análisis-con-pln) | Análisis con PLN | Semanas 9-12 |
| [Fase 6](#fase-6-dashboard-y-reproducibilidad) | Dashboard y reproducibilidad | Semana 13 |
| [Fase 7](#fase-7-redacción-del-tfg) | Redacción del TFG | Semanas 14-16 |

---

## FASE 0. Setup técnico inicial

> **Cuándo:** Días 1-3, antes de empezar nada.

### Paso 0.1 — Instalar el entorno de trabajo

- Python 3.11 desde [python.org](https://python.org) (no uses 3.12+: algunas librerías de PLN dan problemas)
- VS Code desde [code.visualstudio.com](https://code.visualstudio.com)
- Git desde [git-scm.com](https://git-scm.com) y configura nombre y email:
  ```bash
  git config --global user.name "Tu Nombre"
  git config --global user.email "tu@email.com"
  ```

### Paso 0.2 — Extensiones de VS Code obligatorias

| Extensión | Motivo |
|-----------|--------|
| Python (Microsoft) | Soporte Python y ejecución de scripts |
| Ruff | Linter rápido que detecta errores y mantiene el código limpio |
| GitLens | Historial de Git visual, útil para revisar cambios por línea |
| Excel Viewer | Ver .xlsx sin salir de VS Code |
| Markdown All in One | Editar esta guía con preview integrado |

### Paso 0.3 — Entorno conda

Conda permite gestionar tanto Python como las librerías científicas (numpy, spaCy, PyTorch) de forma unificada y evita conflictos de dependencias frecuentes en proyectos de PLN.

```bash
conda create -n tfg-ade python=3.11
conda activate tfg-ade
```

Para instalar paquetes, mezcla conda y pip según la disponibilidad:
```bash
conda install pandas numpy scikit-learn matplotlib seaborn
pip install pdfplumber pymupdf spacy bertopic streamlit
```

Exporta el entorno para reproducibilidad:
```bash
conda env export > environment.yml
```

### Paso 0.4 — Estructura de carpetas

Una estructura clara desde el principio evita que el proyecto se convierta en un cajón desastre. Separar `raw`, `interim` y `processed` garantiza que siempre puedas volver al dato original si algo sale mal en el pipeline.

```
TFG-ADE/
├── data/
│   ├── raw/              # PDFs originales — nunca se modifican
│   ├── interim/          # textos extraídos sin limpiar
│   ├── processed/        # textos limpios y segmentados
│   └── external/         # datos ESG, financieros
├── scripts/              # scripts Python (.py) por fase
│   ├── scraping/
│   ├── extraction/
│   ├── nlp/
│   └── viz/
├── results/
│   ├── figures/
│   ├── tables/
│   └── models/
├── docs/                 # borradores del TFG
├── references/           # PDFs de papers leídos
├── environment.yml
└── README.md
```

### Paso 0.5 — Repositorio Git

El repositorio ya existe. Añade un `.gitignore` que excluya los datos pesados y el entorno:

```
/data/
__pycache__/
*.pdf
.env
*.pyc
```

> Los PDFs no se versionan — son demasiado pesados y no aportan al historial de código. Guárdalos en Google Drive o disco local como backup.

### Paso 0.6 — Registro de decisiones

Crea `docs/decisiones.md` y anota cada decisión metodológica relevante con su justificación: por qué elegiste esa muestra, ese modelo, ese umbral. No es un diario — no necesita fechas ni actividad diaria. Solo las decisiones que un miembro del tribunal podría cuestionar en la defensa.

---

## FASE 1. Marco teórico y diseño metodológico

> **Cuándo:** Semanas 1-3.

### Bloque 1A — Marco regulatorio (semana 1, días 1-4)

**Paso 1.1.** Lee el texto consolidado de la **CSRD** (Directiva 2022/2464) en EUR-Lex. Toma notas sobre:
- Ámbito de aplicación y calendario
- Principio de doble materialidad
- Obligación de aseguramiento

**Paso 1.2.** Estudia los **ESRS** publicados por EFRAG en efrag.org. Son 12 estándares:
- 2 transversales (ESRS 1 y 2)
- 5 ambientales (E1-E5)
- 4 sociales (S1-S4)
- 1 de gobernanza (G1)

Haz una tabla resumen con los disclosure requirements de cada uno. Esta tabla será la base de tu diccionario de keywords en la Fase 5.

**Paso 1.3.** Lee la **Taxonomía UE** (Reglamento 2020/852): los seis objetivos ambientales y los criterios "contribución sustancial" y "DNSH".

**Paso 1.4.** Repasa el **SFDR** (Reglamento 2019/2088): distinción entre productos artículo 6, 8 y 9.

**Paso 1.5.** Contextualiza con la **NFRD** (Directiva 2014/95) como antecedente: qué cambia con CSRD.

> **Entregable:** Capítulo borrador de 8-10 páginas con tabla comparativa NFRD vs CSRD.

---

### Bloque 1B — Literatura académica (semana 1 día 5 - semana 2)

**Paso 1.6.** Búsqueda sistemática en **Web of Science y Scopus**. Cadenas sugeridas:
```
("sustainability report*" OR "ESG disclosure" OR "non-financial report*") AND ("text analysis" OR "NLP" OR "content analysis")
("impression management" OR "greenwashing") AND ("corporate report*")
("CSRD" OR "ESRS") AND ("disclosure" OR "reporting")
```
Filtra por: 2015-2025, revistas Q1-Q2. Exporta a Zotero en formato RIS.

**Paso 1.7.** Lectura obligatoria de papers fundacionales:

| Autor | Año | Sobre qué |
|-------|-----|-----------|
| Loughran & McDonald | 2011 | Diccionarios financieros ("When is a liability not a liability?") |
| Hahn & Lülfs | 2014 | Legitimación en informes de sostenibilidad |
| Cho et al. | 2015 | Organizational façades |
| Bingler et al. | 2022 | ClimateBERT: "Cheap talk and cherry-picking" |
| Michelon et al. | 2015 | Calidad de información de sostenibilidad |

**Paso 1.8.** Crea una **matriz de literatura**: autor / año / muestra / método / hallazgos / gap. Sirve para identificar tu hueco de investigación.

**Paso 1.9.** Revisa TFGs similares en RODERIC (UV), TDX y Dialnet para calibrar el nivel esperado.

---

### Bloque 1C — Preguntas de investigación e hipótesis (semana 3, días 1-3)

**Paso 1.10.** Formula 3-4 preguntas de investigación:

- **RQ1:** ¿Qué temas predominan en el management report de las empresas del STOXX 600?
- **RQ2:** ¿Existen diferencias significativas en contenido y tono según sector y país?
- **RQ3:** ¿Hay correlación entre tono optimista y desempeño ESG real (proxy de greenwashing)?
- **RQ4:** ¿Cómo ha evolucionado el reporting entre el régimen NFRD y los primeros informes bajo CSRD?

**Paso 1.11.** Para cada RQ, deriva hipótesis testables. Ejemplo:
> "H3: empresas con peor ESG score tienden a usar lenguaje más optimista y más vago que las de alto score."

**Paso 1.12.** Reúnete con tu tutor para validar preguntas y enfoque. **No avances sin su visto bueno.**

---

### Bloque 1D — Pre-registro metodológico (semana 3, días 4-5)

**Paso 1.13.** Escribe un documento de 3-4 páginas con: preguntas, hipótesis, muestra prevista, variables y métodos. Esto evita el "fishing" estadístico y te obliga a pensar antes de hacer.

---

## FASE 2. Construcción de la muestra

> **Cuándo:** Semana 4.

**Paso 2.1.** Descarga la composición del STOXX Europe 600:

```python
import pandas as pd

url = "https://en.wikipedia.org/wiki/STOXX_Europe_600"
tablas = pd.read_html(url)
df_stoxx = tablas[0]  # comprueba el índice correcto
df_stoxx.to_csv("data/external/stoxx600_componentes.csv", index=False)
```

**Paso 2.2.** Enriquece la tabla con sector ICB, país y capitalización:

```python
import yfinance as yf

for ticker in df_stoxx["Ticker"]:
    info = yf.Ticker(ticker).info
    # extrae sector, industry, marketCap, country
```

**Paso 2.3.** Decide el diseño muestral. Recomendación: **muestreo estratificado** por sector ICB × región (Europa continental / UK / Nórdicos).

> 60 empresas ≈ 3 por cada uno de los 20 supersectores ICB. Documenta la justificación citando el principio de saturación cualitativa.

**Paso 2.4.** Selecciona dentro de cada estrato:
- Por **capitalización** (top-3 por sector): mejor disponibilidad de datos
- **Aleatoriamente** con `df.sample(random_state=42)`: mejor representatividad

**Paso 2.5.** Consigue datos ESG y financieros de control (por orden de preferencia):

| Fuente | Acceso | Qué da |
|--------|--------|--------|
| Refinitiv/LSEG Workspace | Biblioteca UV (pide en Económicas) | Scores ESG completos, datos financieros |
| Bloomberg Terminal | Sala de la facultad | Ídem |
| MSCI ESG Ratings | msci.com (limitado, gratuito) | Ratings ESG |
| CDP | cdp.net (abierto) | Datos climáticos |
| Sustainalytics | sustainalytics.com (empresa a empresa) | ESG Risk Ratings |
| yfinance | pip install yfinance | ROA, ROE, tamaño, sector |

**Paso 2.6.** Construye el **dataset maestro** en `data/external/empresas_muestra.csv`:

Columnas: `id_empresa, nombre, ticker, ISIN, país, sector_ICB, supersector, capitalización, ESG_score, ESG_env, ESG_soc, ESG_gov, controversias, ROA, ROE, deuda, año`

Estructura: 60 empresas × 2 años = **120 filas**.

**Paso 2.7.** Valida la muestra con tu tutor antes de seguir.

---

## FASE 3. Recolección de informes

> **Cuándo:** Semanas 5-6.

**Paso 3.1.** Decide el tipo de informe a recoger: informe anual integrado o informe de gestión consolidado (donde está el management report propiamente dicho). Descarga también el informe de sostenibilidad separado si existe.

**Paso 3.2.** Crea `data/external/tracking_descargas.csv` con columnas:
```
empresa, año, tipo_informe, url_fuente, fecha_descarga, n_paginas, idioma, estado, notas
```
Estado puede ser: `pendiente / descargado / problema / descartado`

**Paso 3.3.** Primera pasada en **ResponsibilityReports.com** — cubre el 60-70% de la muestra.

**Paso 3.4.** Segunda pasada: **webs corporativas** — `[empresa].com → Investors / Sustainability → Reports`. Para automatizar usa Google Custom Search API o hazlo a mano (en 60 empresas, 4 horas).

**Paso 3.5.** Tercera pasada: **registros oficiales**:
- España: BORME
- Alemania: Bundesanzeiger
- UK: Companies House

**Paso 3.6.** Renombra todos los PDFs con convención estricta:
```
[TICKER]_[AÑO]_[TIPO].pdf
# Ejemplo: IBE.MC_2023_integrated.pdf
```
Guárdalos en `data/raw/[pais]/[ticker]/`.

**Paso 3.7.** Auditoría: ¿tienes ambos años para todas las empresas? Si falta más del 20% en alguna celda, amplía la muestra o cambia el periodo. Documenta exclusiones con motivo.

**Paso 3.8.** **Backup.** Sube `data/raw/` a Google Drive o OneDrive. Si pierdes los PDFs por fallo de disco, pierdes 2 semanas de trabajo.

---

## FASE 4. Extracción y limpieza de texto

> **Cuándo:** Semanas 7-8.

### Bloque 4A — Extracción de texto bruto (semana 7, días 1-3)

**Paso 4.1.** Instala las librerías:

```bash
pip install pdfplumber pymupdf pytesseract pdf2image langdetect spacy pandas
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download de_core_news_sm
python -m spacy download fr_core_news_sm
```

Para OCR necesitas Tesseract a nivel sistema:
```bash
# Mac
brew install tesseract
# Linux
apt install tesseract-ocr
# Windows: descargar instalador desde GitHub
```

**Paso 4.2.** Crea `src/extraction/pdf_to_text.py`:

```python
import fitz  # pymupdf

def extract_pdf(path):
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)
```

Si el resultado tiene menos de 1000 caracteres por cada 10 páginas → PDF escaneado → aplica OCR con `pdf2image + pytesseract` (tarda 10-20 min por informe, planifícalo).

**Paso 4.3.** Crea `notebooks/01_extraction.ipynb` que itere sobre `data/raw/` y guarde `.txt` en `data/interim/`. Loggea errores en un CSV.

**Paso 4.4.** Inspección manual: abre 5-10 textos al azar y compáralos con los PDFs. Verifica que no faltan secciones, que los caracteres especiales se preservan.

---

### Bloque 4B — Detección de idioma y traducción (semana 7, días 4-5)

**Paso 4.5.** Detecta idioma con `langdetect` en los primeros 5000 caracteres. Guarda el idioma en el dataset maestro.

**Paso 4.6.** Decisión: ¿traducir o trabajar multilingüe?

| Opción | Cómo | Cuándo usarla |
|--------|------|---------------|
| A | Traducir con `deep-translator` (Google Translate) | Si necesitas el diccionario Loughran-McDonald (inglés only) |
| B (recomendada) | Modelos multilingües: XLM-RoBERTa, mBERT, multilingual-MiniLM | Evita distorsión por traducción |

---

### Bloque 4C — Aislamiento del management report (semana 8, días 1-3)

**Paso 4.7.** El "management report" tiene nombres distintos por país:

| País | Nombre |
|------|--------|
| UK/Internacional | "Management Report", "Strategic Report", "Directors' Report", "OFR" |
| España | "Informe de Gestión" |
| Alemania | "Lagebericht", "Konzernlagebericht" |
| Francia | "Rapport de Gestion" |
| Italia | "Relazione sulla Gestione" |

**Paso 4.8.** Construye un detector heurístico con regex:
1. Localiza epígrafes mediante lista de variantes
2. Identifica el siguiente epígrafe de nivel similar (fin de sección)
3. Extrae el bloque intermedio

**Paso 4.9.** Valida con 10 informes manualmente. Si falla en más del 20%, refina la heurística o marca inicio/fin en una hoja de cálculo y trocea con script.

**Paso 4.10.** Dentro del management report, aísla la **subsección de sostenibilidad / información no financiera** — bajo CSRD sigue la estructura ESRS y es fácil de localizar.

---

### Bloque 4D — Limpieza del texto (semana 8, días 4-5)

**Paso 4.11.** Pipeline de limpieza:

1. Eliminar cabeceras/pies repetidos (líneas que aparecen en >50% de páginas)
2. Quitar números de página sueltos
3. Normalizar espacios en blanco y saltos de línea
4. Eliminar caracteres de control y artefactos OCR
5. Reconstruir párrafos rotos por columnas
6. **Conservar** mayúsculas y puntuación (necesarias para análisis de sentimiento)

**Paso 4.12.** Tokenización y lematización con spaCy. Genera dos versiones por documento:
- `clean_text`: texto limpio con mayúsculas y puntuación (para BERT/transformers)
- `tokens_lemmatized`: lista de lemas en minúscula sin stopwords (para LDA, TF-IDF)

**Paso 4.13.** Guarda en `data/processed/corpus.parquet` (no CSV — los textos largos rompen Excel):

```
Columnas: id, empresa, año, seccion, idioma, clean_text, tokens
```

---

## FASE 5. Análisis con PLN

> **Cuándo:** Semanas 9-12.

### Bloque 5A — Análisis descriptivo y de frecuencias (semana 9)

**Paso 5.1.** Estadísticas descriptivas del corpus: nº documentos, nº tokens por documento, distribución por sector/país/año.

**Paso 5.2.** Construye tu **diccionario ESRS**: mapea palabras clave a las 12 categorías ESRS. Ejemplo para E1 (cambio climático):
```
emissions, GHG, scope 1, scope 2, scope 3, carbon neutral, net zero,
transition plan, climate risk, decarbonization, science-based targets...
```
Necesitas 30-50 términos por categoría. Dedica 1-2 días a esto revisando los ESRS.

**Paso 5.3.** Calcula la **cobertura ESRS** por documento: qué % de tokens caen en cada categoría. Genera matriz `documentos × 12_categorías` con valores normalizados.

**Paso 5.4.** **TF-IDF** con sklearn: identifica palabras más distintivas por sector, país, año. Visualiza con heatmaps.

**Paso 5.5.** **Bigramas y trigramas** frecuentes con `nltk` o `gensim.models.Phrases` ("net zero", "double materiality", "value chain").

---

### Bloque 5B — Topic modeling (semana 10)

**Paso 5.6.** Baseline con **LDA** (gensim):
1. Construye diccionario y corpus bag-of-words
2. Entrena con k = {5, 10, 15, 20} topics
3. Calcula coherencia (`CoherenceModel`, métrica `c_v`) para cada k y elige el mejor
4. Interpreta los topics (top-10 palabras por topic)

**Paso 5.7.** **BERTopic** (la estrella del proyecto):

```bash
pip install bertopic
```

Pipeline:
1. Genera embeddings con `sentence-transformers/all-MiniLM-L6-v2` (rápido) o `paraphrase-multilingual-MiniLM-L12-v2` (multilingüe)
2. Reducción dimensional con UMAP, clustering con HDBSCAN (BERTopic los integra)
3. Entrena: `BERTopic(language="multilingual")`
4. Inspecciona con `.get_topic_info()`, `.visualize_topics()`, `.visualize_barchart()`
5. Reduce si hay demasiados topics: `.reduce_topics(nr_topics="auto")`

**Paso 5.8.** Para topic modeling usa **párrafos**, no documentos enteros — mejora dramáticamente la calidad de los topics.

**Paso 5.9.** Etiqueta los topics interpretativamente ("Topic 3: descarbonización"). Mapea cada topic a su categoría ESRS más cercana.

**Paso 5.10.** Análisis dinámico: ¿cómo cambia la prevalencia de topics entre 2022 y 2023? Usa `topics_over_time` de BERTopic.

---

### Bloque 5C — Análisis de sentimiento y tono (semana 11, días 1-3)

**Paso 5.11.** **Diccionario Loughran-McDonald** (sraf.nd.edu): aplícalo párrafo a párrafo contando palabras positivas, negativas, de incertidumbre, litigiosas, modales.

**Paso 5.12.** **FinBERT** (`ProsusAI/finbert` en HuggingFace): clasifica oraciones como positive/negative/neutral en contexto financiero.

**Paso 5.13.** **ClimateBERT** (4 modelos especializados en HuggingFace):

| Modelo | Detecta |
|--------|---------|
| `climatebert/distilroberta-base-climate-detector` | ¿Es contenido climático? |
| `climatebert/distilroberta-base-climate-sentiment` | ¿Qué sentimiento tiene? |
| `climatebert/distilroberta-base-climate-commitment` | ¿Es un compromiso concreto? |
| `climatebert/distilroberta-base-climate-specificity` | ¿Es específico o vago? |

Estos cuatro modelos juntos son la base para detectar greenwashing.

---

### Bloque 5D — Detección de greenwashing y vaguedad (semana 11, días 4-5)

**Paso 5.14.** Define métricas operativas de "vaguedad":
- Ratio de **hedging words** ("aim", "strive", "intend", "could", "may") sobre total
- Ratio de declaraciones **cuantitativas** (con cifras/%) vs cualitativas
- Presencia de **fechas concretas** en compromisos vs compromisos sin plazo
- Ratio de verbos en **futuro/condicional** vs presente/pasado

**Paso 5.15.** Aplica ClimateBERT-specificity y construye un **score de especificidad** por documento.

**Paso 5.16.** Define el **"índice de greenwashing"** como combinación:
```
Alto tono optimista + baja especificidad + bajo ESG score real = sospecha de greenwashing
```
Es un proxy, no una prueba — redáctalo con cautela en el TFG.

---

### Bloque 5E — Análisis estadístico comparativo (semana 12)

**Paso 5.17.** Tests estadísticos:
- **ANOVA / Kruskal-Wallis**: diferencias entre sectores
- **Tests t pareados**: cambios entre 2022 y 2023
- **Correlaciones** (Pearson/Spearman): métricas textuales vs scores ESG

**Paso 5.18.** Regresión con `statsmodels`:
```
ESG_score ~ tono_positivo + especificidad + cobertura_E + cobertura_S + cobertura_G
          + log(capitalización) + sector + país + año
```
Reporta coeficientes, errores estándar robustos, R², diagnósticos.

**Paso 5.19.** Visualizaciones finales (semana 12, días 4-5):
- Heatmap de cobertura ESRS por sector
- Boxplots de sentimiento por país
- Scatterplot tono vs ESG score con línea de regresión
- Mapa coroplético de Europa con métrica destacada (geopandas + shapefile NUTS de Eurostat)
- Evolución temporal de topics (BERTopic temporal viz)

Guarda todas en `results/figures/` en **PNG (300 dpi) y SVG**.

---

## FASE 6. Dashboard y reproducibilidad

> **Cuándo:** Semana 13.

**Paso 6.1.** Construye un dashboard en **Streamlit**:

```bash
pip install streamlit
```

Estructura:
- Página 1: Overview del corpus (selectores por sector/país/año)
- Página 2: Explorador por empresa (perfil ESG + métricas textuales)
- Página 3: Visualizador de topics interactivo
- Página 4: Comparador entre empresas

Despliégalo en **Streamlit Community Cloud** (gratis) y enlaza la URL en el TFG.

**Paso 6.2.** Escribe el `README.md` del repositorio: descripción, requisitos, cómo reproducir, estructura de carpetas, licencia (MIT o CC-BY).

**Paso 6.3.** Fija versiones exactas exportando el entorno conda:
```bash
conda env export > environment.yml
```

**Paso 6.4.** Crea `notebooks/99_reproduccion.ipynb` que ejecute todo el pipeline de punta a punta.

---

## FASE 7. Redacción del TFG

> **Cuándo:** Semanas 14-16.

**Paso 7.1.** Configura **Overleaf** (gratis con cuenta universitaria). Pide a tu tutor la plantilla LaTeX oficial de la UV para TFG de ADE; si no existe, usa una plantilla genérica.

**Paso 7.2.** Conecta **Zotero** con Overleaf vía Better BibTeX: exporta tu biblioteca a `.bib` y mantenlo sincronizado.

**Paso 7.3.** Estructura del documento (60-80 páginas):

| Sección | Extensión |
|---------|-----------|
| Resumen / Abstract (ES + EN) | 1 pág |
| Introducción | 4-5 pp |
| Marco teórico | 8-10 pp |
| Marco normativo europeo | 6-8 pp |
| Metodología | 10-12 pp |
| Resultados | 15-20 pp |
| Discusión | 6-8 pp |
| Conclusiones, limitaciones y líneas futuras | 4-5 pp |
| Bibliografía (APA 7ª o Harvard) | — |
| Anexos (diccionario ESRS, código → link GitHub) | — |

**Paso 7.4.** Redacta en este orden (no lineal):
```
Metodología → Resultados → Marco normativo → Marco teórico
→ Discusión → Introducción → Conclusiones → Resumen
```
> Empezar por la introducción es el error más común — déjala para cuando sepas qué has hecho.

**Paso 7.5.** Cada figura y tabla debe estar numerada, titulada, con fuente y referenciada en el texto.

**Paso 7.6.** Plan de revisión (semana 16):

| Día | Tarea |
|-----|-------|
| 1-2 | Revisión propia con lectura en voz alta |
| 3 | Corrector automático (LanguageTool o Grammarly) |
| 4 | Enviar a tutor con margen para sus comentarios |
| 5 | Incorporar correcciones |
| 6-7 | Formato final, portada, paginación, índices automáticos, exportar PDF |

**Paso 7.7.** Presentación de defensa: 15-20 slides.

Estructura:
```
Problema (2) → Marco (3) → Metodología (4) → Resultados clave (6) → Conclusiones (3) → Preguntas (1)
```
Ensaya cronometrado al menos **5 veces**.

---

## Recomendaciones transversales

**Sobre el tiempo.** 16 semanas es ajustado pero factible con 15-20 horas semanales. Si vas justo, reduce muestra a 30 empresas y un solo año — un análisis sólido de 30 vale más que uno superficial de 200.

**Sobre el tutor.** Reuniones cada 2 semanas mínimo, con agenda escrita previa y acta breve posterior. No le pidas opinión genérica: llévale decisiones concretas a validar.

**Sobre el código.** Commits diarios con mensajes descriptivos. Rama `main` estable + ramas `feature/...` para experimentos. Nunca trabajes directamente en `main`.

**Sobre los modelos pesados.** BERTopic y ClimateBERT requieren GPU para ser rápidos. Si tu portátil no tiene:
- **Google Colab** gratuito (12h de GPU al día) — puedes instalar el entorno con `pip install` directamente en la sesión
- **Kaggle Notebooks** (30h semanales de GPU)
- Conecta Colab con tu GitHub para sincronizar código y resultados

**Sobre el plagio y la IA.** Documenta cualquier uso de Claude/ChatGPT en la sección de metodología si tu universidad lo requiere. El uso de modelos PLN como herramienta de análisis es legítimo y no es "IA generativa para escribir el TFG".
