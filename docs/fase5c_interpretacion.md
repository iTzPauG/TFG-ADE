# Fase 5C — Interpretación de resultados

> **Corpus ampliado — 196 empresas / 586 documentos `sus` (Decisión 036).**
> Re-ejecutado desde cero (`--fresh`, ~7.5h, sin incidencias MPS gracias a
> `caffeinate -i`). La metodología (cascada de 6 modelos) no cambia respecto a
> la versión original (97 empresas / 289 docs, Decisión 024); solo los números,
> que **confirman y refuerzan** todos los hallazgos previos.

> Generado con `scripts/nlp/fase5c_sentimiento.py` (Decisión 024/036).
> Tablas en `results/tables/5c_*` · Figuras en `results/figures/5c_*.png`.
> Granularidad: 539.993 frases (segmentación spaCy sentencizer, ≥4 palabras) sobre `clean_text`
> de los 586 documentos `sus`. Agregación final a nivel documento: `5c_doc_agregado.csv` (586 filas).

---

## 1. Segmentación en frases

| Métrica | Valor |
|---------|-------|
| Frases totales (≥4 palabras) | 539.993 |
| Media por documento | 921 |
| Frases climáticas (climate-detector = "yes") | ~228.300 (≈42.3%) |

El ~42.3% de frases climáticas es estable por año (41.6% en 2022, 42.7% en 2023, 43.0% en
2024) — prácticamente idéntico al 41.4% (43.4/42.6/44.2%) de la muestra original. Confirma
de nuevo que el **crecimiento de tokens en `sus`** documentado en 5A (mediana +147%
2022→2024) no se debe a un desplazamiento hacia/desde contenido climático específicamente,
sino a un crecimiento proporcional de todas las temáticas ESG, ahora a escala de 196
empresas.

---

## 2. Loughran-McDonald (`5c_lm_ratios.png`, columnas `lm_*` en `5c_doc_agregado.csv`)

**Qué mide:** para cada frase, la proporción de palabras que pertenecen a cada una de las 7
categorías del diccionario Loughran-McDonald (Negative, Positive, Uncertainty, Litigious,
Strong Modal, Weak Modal, Constraining). Se agrega como media simple por documento.

| Año | Negative | Positive | Uncertainty | Litigious | Strong modal | Weak modal | Constraining |
|-----|----------|----------|-------------|-----------|--------------|------------|--------------|
| 2022 | 0.0105 | 0.0144 | 0.0094 | 0.0046 | 0.0030 | 0.0018 | 0.0049 |
| 2023 | 0.0108 | 0.0144 | 0.0104 | 0.0052 | 0.0028 | 0.0020 | 0.0051 |
| 2024 | 0.0126 | 0.0138 | 0.0122 | 0.0051 | 0.0025 | 0.0024 | 0.0056 |

**Lectura (idéntica en dirección y magnitud a la muestra original):**
- **Positive ↓** (0.0144→0.0138, −4.2%) y **Strong Modal ↓** (0.0030→0.0025, −17%): el
  lenguaje afirmativo y categórico ("will", "always", "definitely") **disminuye**.
- **Negative ↑** (0.0105→0.0126, +20.0%), **Uncertainty ↑** (0.0094→0.0122, +29.8%),
  **Constraining ↑** (0.0049→0.0056, +14.3%): el lenguaje de riesgo, condicionalidad y
  restricción **aumenta de forma consistente**. Litigious se mantiene estable
  (0.0046→0.0051→0.0051, sube en 2023 y se estabiliza en 2024).
- **Weak Modal ↑** (0.0018→0.0024, +33%): más lenguaje condicional ("may", "could", "might").

**Interpretación:** el patrón conjunto (↓ tono afirmativo/positivo, ↑ incertidumbre/riesgo/
restricciones) **se reproduce con magnitudes muy similares** sobre 196 empresas, lo que
descarta que fuera un artefacto de la muestra original de 97. Es coherente con la
transición **NFRD→CSRD**: el régimen CSRD/ESRS exige reconocer riesgos, dependencias y
limitaciones (doble materialidad, IROs) de forma mucho más explícita que el reporting
voluntario/promocional típico de NFRD. Es una señal **a favor** de mayor "cheap talk"
cauteloso pero también potencialmente de mayor honestidad sobre incertidumbres — ambas
lecturas son relevantes para RQ4 y se matizan con los resultados de 5D (especificidad,
ratio cuantitativo).

**Para el TFG:** `5c_lm_ratios.png` (evolución de las 7 ratios por año) es la figura base
del apartado de tono lingüístico en Resultados RQ4.

---

## 3. ClimateBERT — detección de frases climáticas (`5c_climate_share.png`)

**Qué mide:** `climatebert/distilroberta-base-climate-detector` clasifica cada una de las
539.993 frases como climática (`yes`) o no (`no`).

**Resultado:** ~42.3% climáticas, estable por año (41.6% / 42.7% / 43.0%) — coherente con el
41.4% de la muestra original.

**Para el TFG:** confirma que ~2 de cada 5 frases de la sección `sus` tratan directamente de
clima/energía/emisiones — coherente con que **E1 (Climate Change)** sea la categoría ESRS
mejor cubierta en 5A (0.558 en 2024) y un bloque dominante en 5B (T08/T16/T22 LDA K=25, T0
BERTopic).

---

## 4. ClimateBERT — sentimiento, compromiso y especificidad climática

> Aplicado **solo** sobre las frases climáticas (cascada, Decisión 024).

| Año | Sentiment: neutral | Sentiment: opportunity | Sentiment: risk | Commitment: no | Commitment: sí | Specificity: no | Specificity: sí |
|-----|---------------------|--------------------------|--------------------|------------------|-------------------|--------------------|--------------------|
| 2022 | 68.3% | 20.7% | 11.0% | 67.2% | 32.8% | 73.8% | 26.2% |
| 2023 | 67.4% | 20.0% | 12.6% | 68.9% | 31.1% | 72.9% | 27.1% |
| 2024 | 67.3% | 15.9% | 16.8% | 73.9% | 26.1% | 75.9% | 24.1% |

**Lectura por dimensión (mismo patrón que en la muestra original, con magnitudes muy
similares):**

- **Sentiment** — el **discurso de "oportunidad" climática cae** de 20.7% a 15.9% (−4.8
  puntos, −23% relativo), mientras el **de "riesgo" sube** de 11.0% a 16.8% (+5.8 puntos,
  +53% relativo). En 2022 "oportunidad" casi duplicaba a "riesgo" (20.7 vs 11.0); en 2024
  la diferencia se reduce drásticamente (15.9 vs 16.8 — el riesgo ya supera a la
  oportunidad). Coherente con LM (↓positive/strong modal, ↑uncertainty/negative): el
  discurso climático se vuelve **menos optimista y más centrado en riesgos**.

- **Commitment** — las frases con **compromisos explícitos** ("we will...", "we commit
  to...") **caen** de 32.8% a 26.1% (−6.7 puntos, −20% relativo) — prácticamente idéntico
  al −20% de la muestra original (34.5%→27.5%).

- **Specificity** — las frases **específicas** (con cifras, fechas, metas concretas) **caen**
  de 26.2% a 24.1% (−2.1 puntos, −8% relativo) — de nuevo casi idéntico al −8.5% original
  (28.1%→25.7%).

**Interpretación conjunta — relevancia directa para RQ3 (Decisión 019, GW_index en 5D):**
las tres series se mueven en la misma dirección 2022→2024, **replicando exactamente el
patrón de la muestra original a escala de 196 empresas**: **menos oportunidad, menos
compromiso, menos especificidad**, y simultáneamente **más riesgo** (que ahora llega a
superar a la oportunidad en 2024). El patrón observado sigue **no apoyando un aumento del
greenwashing en sentido clásico** (tono optimista sin respaldo) — el discurso se vuelve más
cauto (menos oportunidad/compromiso) pero también menos específico. La lectura más
plausible sigue siendo que el **crecimiento masivo del volumen** de texto climático (5A:
+147% mediana tokens) se debe en gran parte a **contenido descriptivo de cumplimiento
normativo** (definiciones ESRS, metodología de doble materialidad, tablas de indicadores)
más que a nuevos compromisos cuantificados — confirmado directamente por el `GW_index`
(ratio cuantitativo ↓, 5D).

**Para el TFG:** estas 3 series son uno de los hallazgos centrales de 5C para RQ3/RQ4.
Recomendado presentar como gráfico de líneas conjunto (3 paneles o 1 panel con 6 series:
risk/opportunity, commitment yes, specificity yes).

---

## 5. FinBERT — tono financiero (`5c_finbert_sentiment.png`)

**Qué mide:** `ProsusAI/finbert` clasifica cada una de las 539.993 frases como
positive/negative/neutral (finanzas en general, no específico de clima). `finbert_tone`
= % positivas − % negativas por documento.

| Año | % positivo | % negativo | % neutral | Tono (pos−neg) |
|-----|-----------|-----------|-----------|----------------|
| 2022 | 23.50% | 4.65% | 71.84% | 0.1885 |
| 2023 | 23.33% | 4.76% | 71.91% | 0.1857 |
| 2024 | 19.60% | 5.55% | 74.85% | 0.1405 |

**Lectura:** el tono neto **cae de forma monótona y sustancial** (0.1885→0.1405, −25.4%
relativo en 3 años — casi idéntico al −24% de la muestra original), impulsado tanto por
**menos frases positivas** (23.5%→19.6%) como por **algo más de negativas** (4.65%→5.55%).
El % neutral crece (71.8%→74.9%) — más texto descriptivo/técnico, menos discurso
evaluativo. La caída se concentra en 2023→2024 (2022→2023 es casi plana: 0.1885→0.1857),
igual que en el resto de indicadores — consistente con que 2024 es el primer ejercicio
CSRD.

Este resultado es consistente con LM (↓positive, ↑negative) y con ClimateBERT-sentiment
(↓opportunity, ↑risk): **tres modelos independientes, entrenados sobre corpora distintos,
convergen en la misma tendencia direccional**, ahora confirmada sobre 196 empresas —
triangulación fuerte para el hallazgo de "tono cada vez menos optimista bajo CSRD" (RQ4).

**Distribución global (586 docs, todas las frases):** `finbert_tone` media = 0.1715,
mediana = 0.1565, rango [−0.508, 0.706] — el rango se amplía respecto a la muestra original
([-0.139, 0.704]), con algunas empresas (entre las 99 nuevas) con tono neto muy negativo,
útil para RQ2 (diferencias por sector/empresa).

**Para el TFG:** `5c_finbert_sentiment.png` + tabla de medias por año. Candidato para
correlación con variables financieras (ROA, ROE) en 5E (RQ3).

---

## 6. FinBERT-ESG-9 — distribución de categorías (`5c_esg9_distribucion.png`)

**Qué mide:** `yiyanghkust/finbert-esg-9-categories` clasifica cada frase en una de 9
categorías ESG (Climate Change, Natural Capital, Pollution & Waste, Human Capital, Product
Liability, Community Relations, Corporate Governance, Business Ethics & Values, Non-ESG).

| Categoría | 2022 | 2023 | 2024 | ESRS aprox. (Dec.020) |
|-----------|------|------|------|------------------------|
| Climate Change | 20.9% | 21.8% | 22.2% | E1 |
| Human Capital | 19.7% | 18.1% | 18.3% | S1 |
| Corporate Governance | 18.9% | 17.9% | 18.2% | G1 |
| Non-ESG | 13.5% | 15.5% | 15.4% | — |
| Community Relations | 6.9% | 6.5% | 4.8% | S3 |
| Business Ethics & Values | 5.7% | 5.3% | 5.9% | G1 |
| Product Liability | 5.4% | 5.7% | 5.9% | S4 |
| Natural Capital | 4.8% | 4.8% | 4.9% | E2/E3/E4 |
| Pollution & Waste | 4.1% | 4.3% | 4.3% | E2/E3 |

**Lectura (mismo patrón que la muestra original):**
- **Climate Change domina y se mantiene/crece ligeramente** (20.9%→22.2%), confirmando
  triangulación con 5A (E1=0.558 en 2024, mejor cobertura ESRS) y 5B (bloque clima en LDA
  K=25, T0 BERTopic en crecimiento ×2.0).
- **Human Capital decrece levemente** (19.7%→18.3%) y **Corporate Governance también**
  (18.9%→18.2%) — posible dilución relativa frente al crecimiento de Non-ESG y Climate
  Change, no necesariamente menos contenido S1/G1 en términos absolutos (5A mostró S1 y G1
  creciendo en cobertura ESRS, +0.12 y +0.10 respectivamente).
- **Non-ESG crece** (13.5%→15.4%) — coherente con la hipótesis del §4: parte del crecimiento
  de la sección `sus` bajo CSRD es contenido normativo/estructural (definiciones, alcance,
  gobernanza del proceso de reporting) que este clasificador no asocia a ninguna categoría
  ESG específica.
- **Pollution & Waste y Natural Capital permanecen bajos y estables** (~4-5%), coherente con
  que **E2** sigue siendo la categoría ESRS peor cubierta en 5A (0.112→0.195).

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

**Qué contiene:** **586 filas** (una por documento `sus`) × 33 columnas:
`doc_id, empresa, año, confianza, n_frases` + 7 columnas `lm_*` + `pct_climate` +
3 columnas `finbert_pct_*` + `finbert_tone` + 7 columnas `climate_sentiment/commitment/
specificity_*` + 9 columnas `esg9_*`.

**Es el input directo de:**
- **5D** — `GW_index` combina `lm_*` (hedging ratio vía weak_modal/uncertainty),
  `climate_specificity_spec` (especificidad), y métricas de ratio cuantitativo/futuro
  calculadas sobre `5c_frases.parquet` (539.993 frases).
- **5E** — variable dependiente/independiente en regresiones (tono, especificidad,
  commitment) cruzada con `confianza` (filtro `densidad_baja`, Dec.019), año (test pareado
  2022↔2024, RQ4, ahora 194 empresas comunes), sector/país (Kruskal-Wallis, RQ2).

---

## 8. Para el TFG — qué reportar de 5C

| Elemento | Dónde | Capítulo TFG | RQ |
|----------|-------|--------------|-----|
| Evolución 7 ratios LM 2022→2024 | `5c_lm_ratios.png` + tabla §2 | Resultados | RQ4 |
| % frases climáticas (≈42%, estable) | `5c_climate_share.png` | Resultados | RQ1 |
| Sentiment/commitment/specificity climático (↓oportunidad, ↑riesgo, ↓compromiso, ↓especificidad) | tabla §4 | **Resultados** | **RQ3, RQ4** |
| Tono FinBERT decreciente (0.1885→0.1405) | `5c_finbert_sentiment.png` | Resultados | RQ4 |
| Distribución FinBERT-ESG-9 (triangulación con 5A/5B) | `5c_esg9_distribucion.png` + tabla §6 | Resultados/Metodología | RQ1 |
| Reproducción a 196 empresas sin incidencias técnicas | Decisión 036 | Metodología (reproducibilidad) | — |

---

## 9. Resumen ejecutivo

- **539.993 frases** procesadas a través de 6 modelos (LM diccionario + ClimateBERT×4 +
  FinBERT + FinBERT-ESG-9), agregadas a **586 documentos** (196 empresas × 3 años).
- **Réplica casi exacta de la muestra original**: todas las magnitudes (LM ratios, tono
  FinBERT, sentiment/commitment/specificity climático, distribución ESG-9) reproducen los
  hallazgos de la Decisión 024 sobre 97 empresas, con diferencias de orden de magnitud
  ≤2-3 puntos porcentuales en casi todos los indicadores — **fuerte evidencia de robustez**.
- **Triangulación fuerte**: tres modelos independientes (LM, ClimateBERT-sentiment, FinBERT)
  coinciden en que el **tono se vuelve menos optimista 2022→2024** bajo CSRD, y esta vez con
  el doble de empresas.
- **Hallazgo central RQ3**: dentro de las frases climáticas, **caen simultáneamente
  oportunidad, compromiso explícito y especificidad**, mientras sube el riesgo (que en 2024
  ya supera a la oportunidad) — no apoya un patrón de "más optimismo sin sustancia" en
  agregado; sugiere en cambio que el crecimiento de volumen es mayormente contenido
  normativo/descriptivo. Confirmado con `GW_index` (5D): ratio cuantitativo ↓ 2022→2024.
- **Ejecución sin incidencias técnicas** (a diferencia del run original de Decisión 024,
  que tuvo cuelgues MPS/suspensión): `caffeinate -i` evitó la suspensión del Mac durante las
  ~7.5h de procesamiento.
