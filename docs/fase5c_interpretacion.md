# Fase 5C — Interpretación de resultados

> Generado con `scripts/nlp/fase5c_sentimiento.py` (Decisión 024).
> Tablas en `results/tables/5c_*` · Figuras en `results/figures/5c_*.png`.
> Granularidad: 285.509 frases (segmentación spaCy sentencizer, ≥4 palabras) sobre `clean_text`
> de los 289 documentos `sus`. Agregación final a nivel documento: `5c_doc_agregado.csv` (289 filas).

---

## 1. Segmentación en frases

| Métrica | Valor |
|---------|-------|
| Frases totales (≥4 palabras) | 285.509 |
| Media por documento | 988 |
| Frases climáticas (climate-detector = "yes") | 118.321 (41.4%) |

El 41.4% de frases climáticas es estable por año (43.4% en 2022, 42.6% en 2023, 44.2% en
2024) — confirma que el **crecimiento de tokens en `sus`** documentado en 5A (+111%
2022→2024) no se debe a un desplazamiento hacia/desde contenido climático específicamente,
sino a un crecimiento proporcional de todas las temáticas ESG.

---

## 2. Loughran-McDonald (`5c_lm_ratios.png`, columnas `lm_*` en `5c_doc_agregado.csv`)

**Qué mide:** para cada frase, la proporción de palabras que pertenecen a cada una de las 7
categorías del diccionario Loughran-McDonald (Negative, Positive, Uncertainty, Litigious,
Strong Modal, Weak Modal, Constraining). Se agrega como media simple por documento.

| Año | Negative | Positive | Uncertainty | Litigious | Strong modal | Weak modal | Constraining |
|-----|----------|----------|-------------|-----------|--------------|------------|--------------|
| 2022 | 0.0101 | 0.0149 | 0.0085 | 0.0042 | 0.0031 | 0.0016 | 0.0047 |
| 2023 | 0.0107 | 0.0142 | 0.0097 | 0.0048 | 0.0028 | 0.0018 | 0.0052 |
| 2024 | 0.0127 | 0.0138 | 0.0110 | 0.0050 | 0.0026 | 0.0021 | 0.0058 |

**Lectura:**
- **Positive ↓** (0.0149→0.0138, −7.4%) y **Strong Modal ↓** (0.0031→0.0026, −16%): el
  lenguaje afirmativo y categórico ("will", "always", "definitely") **disminuye**.
- **Negative ↑** (0.0101→0.0127, +25.7%), **Uncertainty ↑** (0.0085→0.0110, +29.4%),
  **Constraining ↑** (0.0047→0.0058, +23.4%), **Litigious ↑** (0.0042→0.0050, +19%): el
  lenguaje de riesgo, condicionalidad y restricción legal/regulatoria **aumenta de forma
  consistente** en las 4 categorías.
- **Weak Modal ↑** (0.0016→0.0021, +31%): más lenguaje condicional ("may", "could", "might").

**Interpretación:** el patrón conjunto (↓ tono afirmativo/positivo, ↑ incertidumbre/riesgo/
restricciones legales) es coherente con la transición **NFRD→CSRD**: el régimen CSRD/ESRS
exige reconocer riesgos, dependencias y limitaciones (doble materialidad, IROs) de forma
mucho más explícita que el reporting voluntario/promocional típico de NFRD. Es una señal
**a favor** de mayor "cheap talk" cauteloso pero también potencialmente de mayor honestidad
sobre incertidumbres — ambas lecturas son relevantes para RQ4 y se deben matizar con los
resultados de 5D (especificidad).

**Para el TFG:** `5c_lm_ratios.png` (evolución de las 7 ratios por año) es la figura base
del apartado de tono lingüístico en Resultados RQ4.

---

## 3. ClimateBERT — detección de frases climáticas (`5c_climate_share.png`)

**Qué mide:** `climatebert/distilroberta-base-climate-detector` clasifica cada una de las
285.509 frases como climática (`yes`) o no (`no`).

**Resultado:** 118.321/285.509 = 41.4% climáticas, estable por año (43.4% / 42.6% / 44.2%).

**Para el TFG:** confirma que ~2 de cada 5 frases de la sección `sus` tratan directamente de
clima/energía/emisiones — coherente con que **E1 (Climate Change)** sea la categoría ESRS
mejor cubierta en 5A (0.503) y el topic dominante en 5B (T06 LDA, T7/T15/T16 BERTopic).

---

## 4. ClimateBERT — sentimiento, compromiso y especificidad climática

> Aplicado **solo** sobre las 118.321 frases climáticas (cascada, Decisión 024).

| Año | Sentiment: neutral | Sentiment: opportunity | Sentiment: risk | Commitment: no | Commitment: sí | Specificity: no | Specificity: sí |
|-----|---------------------|--------------------------|--------------------|------------------|-------------------|--------------------|--------------------|
| 2022 | 68.0% | 21.5% | 10.4% | 65.5% | 34.5% | 71.9% | 28.1% |
| 2023 | 67.2% | 20.2% | 12.6% | 68.0% | 32.0% | 71.2% | 28.8% |
| 2024 | 66.6% | 16.2% | 17.2% | 72.5% | 27.5% | 74.3% | 25.7% |

**Lectura por dimensión:**

- **Sentiment** — el **discurso de "oportunidad" climática cae** de 21.5% a 16.2%
  (−5.3 puntos, −25% relativo), mientras el **de "riesgo" sube** de 10.4% a 17.2% (+6.8
  puntos, +65% relativo). En 2022 "oportunidad" duplicaba a "riesgo"; en 2024 ambos están
  casi igualados. Esto es coherente con el hallazgo LM (↓ positive/strong modal, ↑
  uncertainty/negative): el discurso climático se vuelve **menos optimista y más centrado
  en riesgos**.

- **Commitment** — las frases con **compromisos explícitos** ("we will...", "we commit to...")
  **caen** de 34.5% a 27.5% (−7 puntos, −20% relativo). Las frases sin compromiso explícito
  (descriptivas/constatativas) ganan peso relativo.

- **Specificity** — las frases **específicas** (con cifras, fechas, metas concretas) **caen
  ligeramente** de 28.1% a 25.7% (−2.4 puntos, −8.5% relativo). Las frases no específicas
  ganan peso relativo.

**Interpretación conjunta — relevancia directa para RQ3 (Decisión 019, GW_index en 5D):**
las tres series se mueven en la misma dirección 2022→2024: **menos oportunidad, menos
compromiso, menos especificidad**, y simultáneamente **más riesgo**. Si la hipótesis de
"cheap talk"/greenwashing es *tono optimista sin respaldo de especificidad*, el patrón
observado **no apoya un aumento del greenwashing en sentido clásico** — más bien lo
contrario: el discurso se vuelve más cauto (menos oportunidad/compromiso) pero también
menos específico. La lectura más plausible es que el **crecimiento masivo del volumen**
de texto climático (5A: +111% tokens) se debe en gran parte a **contenido descriptivo de
cumplimiento normativo** (definiciones ESRS, metodología de doble materialidad, tablas de
indicadores) más que a nuevos compromisos cuantificados — hipótesis a contrastar
directamente con el `GW_index` (ratio cuantitativo, ratio futuro, hedging ratio) en 5D.

**Para el TFG:** estas 3 series son uno de los hallazgos centrales de 5C para RQ3/RQ4.
Recomendado presentar como gráfico de líneas conjunto (3 paneles o 1 panel con 6 series:
risk/opportunity, commitment yes, specificity yes).

---

## 5. FinBERT — tono financiero (`5c_finbert_sentiment.png`)

**Qué mide:** `ProsusAI/finbert` clasifica cada una de las 285.509 frases como
positive/negative/neutral (finanzas en general, no específico de clima). `finbert_tone`
= % positivas − % negativas por documento.

| Año | % positivo | % negativo | % neutral | Tono (pos−neg) |
|-----|-----------|-----------|-----------|----------------|
| 2022 | 24.7% | 4.5% | 70.9% | 0.202 |
| 2023 | 23.4% | 4.6% | 72.0% | 0.188 |
| 2024 | 20.8% | 5.5% | 73.6% | 0.153 |

**Lectura:** el tono neto **cae de forma monótona y sustancial** (0.202→0.153, −24% relativo
en 3 años), impulsado tanto por **menos frases positivas** (24.7%→20.8%) como por **algo
más de negativas** (4.5%→5.5%). El % neutral crece (70.9%→73.6%) — más texto descriptivo/
técnico, menos discurso evaluativo.

Este resultado es consistente con LM (↓positive, ↑negative) y con ClimateBERT-sentiment
(↓opportunity, ↑risk): **tres modelos independientes, entrenados sobre corpora distintos,
convergen en la misma tendencia direccional** — triangulación fuerte para el hallazgo de
"tono cada vez menos optimista bajo CSRD" (RQ4).

**Distribución global (289 docs, todas las frases):** `finbert_tone` media = 0.181,
mediana = 0.164, rango [-0.139, 0.704] — algunas empresas tienen tono neto negativo
(probablemente sectores en crisis/reestructuración o informes muy centrados en riesgos),
útil para RQ2 (diferencias por sector/empresa).

**Para el TFG:** `5c_finbert_sentiment.png` + tabla de medias por año. Candidato para
correlación con variables financieras (ROA, ROE) en 5E (RQ3).

---

## 6. FinBERT-ESG-9 — distribución de categorías (`5c_esg9_distribucion.png`)

**Qué mide:** `yiyanghkust/finbert-esg-9-categories` clasifica cada frase en una de 9
categorías ESG (Climate Change, Natural Capital, Pollution & Waste, Human Capital, Product
Liability, Community Relations, Corporate Governance, Business Ethics & Values, Non-ESG).
**Confianza media tras la corrección del tokenizer (Decisión 024, incidencia 3): 0.857**
(antes de la corrección era 0.267 — resultados del primer cálculo eran inválidos y se
descartaron).

| Categoría | 2022 | 2023 | 2024 | ESRS aprox. (Dec.020) |
|-----------|------|------|------|------------------------|
| Climate Change | 22.8% | 22.4% | 22.7% | E1 |
| Human Capital | 21.2% | 19.2% | 19.3% | S1 |
| Corporate Governance | 16.2% | 17.0% | 16.8% | G1 |
| Non-ESG | 12.0% | 15.0% | 14.1% | — |
| Community Relations | 7.1% | 6.7% | 5.4% | S3 |
| Product Liability | 5.5% | 5.3% | 5.9% | S4 |
| Business Ethics & Values | 5.8% | 5.4% | 5.9% | G1 |
| Pollution & Waste | 4.1% | 4.2% | 4.6% | E2/E3 |
| Natural Capital | 5.2% | 4.8% | 5.2% | E2/E3/E4 |

**Lectura:**
- **Climate Change domina y es estable** (~22-23%), confirmando triangulación con 5A
  (E1=0.503, mejor cobertura ESRS) y 5B (T06 LDA mayor topic, T7/T15/T16 BERTopic en
  crecimiento).
- **Human Capital decrece** (21.2%→19.3%) — posible dilución relativa frente al crecimiento
  de otras categorías, no necesariamente menos contenido S1 en términos absolutos (5A mostró
  S1=0.487, segunda mejor cobertura, estable).
- **Non-ESG crece** (12.0%→14.1%) — coherente con la hipótesis del §4: parte del crecimiento
  de la sección `sus` bajo CSRD es contenido normativo/estructural (definiciones, alcance,
  gobernanza del proceso de reporting) que este clasificador no asocia a ninguna categoría
  ESG específica.
- **Pollution & Waste y Natural Capital permanecen bajos** (~4-5%), coherente con que **E2**
  fue la categoría ESRS peor cubierta en 5A (0.150-0.152).

**Limitación heredada (Decisión 020):** FinBERT-ESG-9 no tiene categorías equivalentes a
**E5 (economía circular)** ni **S4 (consumidores)** de forma directa — `Product Liability`
es la aproximación más cercana a S4, y E5 probablemente se reparte entre `Pollution & Waste`
y `Natural Capital`. Para RQ1, el diccionario ESRS (5A) y los topics LDA/BERTopic (5B) son
las fuentes primarias; FinBERT-ESG-9 es un clasificador **complementario** de triangulación.

**Para el TFG:** `5c_esg9_distribucion.png` (barras apiladas o líneas por año) como tercera
fuente de evidencia (junto a 5A diccionario y 5B topics) sobre la distribución temática del
corpus — útil para discutir la **convergencia/divergencia entre métodos** en Metodología.

---

## 7. Tabla de salida: `5c_doc_agregado.csv`

**Qué contiene:** 289 filas (una por documento `sus`) × 33 columnas:
`doc_id, empresa, año, confianza, n_frases` + 7 columnas `lm_*` + `pct_climate` +
3 columnas `finbert_pct_*` + `finbert_tone` + 7 columnas `climate_sentiment/commitment/
specificity_*` + 9 columnas `esg9_*`.

**Es el input directo de:**
- **5D** — `GW_index` combinará `lm_*` (hedging ratio vía weak_modal/uncertainty),
  `climate_specificity_spec` (especificidad), y nuevas métricas de ratio cuantitativo/futuro
  a calcular sobre `5c_frases.parquet`.
- **5E** — variable dependiente/independiente en regresiones (tono, especificidad,
  commitment) cruzada con `confianza` (filtro `densidad_baja`, Dec.019), año (test pareado
  2022↔2024, RQ4), sector/país (ANOVA/Kruskal-Wallis, RQ2).

---

## 8. Para el TFG — qué reportar de 5C

| Elemento | Dónde | Capítulo TFG | RQ |
|----------|-------|--------------|-----|
| Evolución 7 ratios LM 2022→2024 | `5c_lm_ratios.png` + tabla §2 | Resultados | RQ4 |
| % frases climáticas (41.4%, estable) | `5c_climate_share.png` | Resultados | RQ1 |
| Sentiment/commitment/specificity climático (↓oportunidad, ↑riesgo, ↓compromiso, ↓especificidad) | tabla §4 | **Resultados** | **RQ3, RQ4** |
| Tono FinBERT decreciente (0.202→0.153) | `5c_finbert_sentiment.png` | Resultados | RQ4 |
| Distribución FinBERT-ESG-9 (triangulación con 5A/5B) | `5c_esg9_distribucion.png` + tabla §6 | Resultados/Metodología | RQ1 |
| Incidencias técnicas (MPS, sleep, tokenizer) | Decisión 024 | Metodología (reproducibilidad) | — |

---

## 9. Resumen ejecutivo

- **285.509 frases** procesadas a través de 6 modelos (LM diccionario + ClimateBERT×4 +
  FinBERT + FinBERT-ESG-9), agregadas a 289 documentos.
- **Triangulación fuerte**: tres modelos independientes (LM, ClimateBERT-sentiment, FinBERT)
  coinciden en que el **tono se vuelve menos optimista 2022→2024** bajo CSRD.
- **Hallazgo central RQ3**: dentro de las frases climáticas, **caen simultáneamente
  oportunidad, compromiso explícito y especificidad**, mientras sube el riesgo — no apoya
  un patrón de "más optimismo sin sustancia" en agregado; sugiere en cambio que el
  crecimiento de volumen es mayormente contenido normativo/descriptivo. A confirmar con
  `GW_index` (5D).
- **FinBERT-ESG-9 confirma** (con confianza media 0.857 tras corregir el bug del tokenizer,
  Decisión 024) la centralidad de Climate Change/E1 ya vista en 5A y 5B.
