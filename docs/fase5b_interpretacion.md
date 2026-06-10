# Fase 5B — Interpretación de resultados

> Generado con `scripts/nlp/fase5b_topics.py` (Decisión 022).
> Tablas en `results/tables/5b_*.csv` · Figuras en `results/figures/5b_*.png` · Modelos en `results/models/`.

---

## 1. Segmentación del corpus en párrafos

| Año | Párrafos | % del total |
|-----|----------|-------------|
| 2022 | 29.762 | 22.7% |
| 2023 | 40.388 | 30.8% |
| 2024 | 60.990 | 46.5% |
| **Total** | **131.140** | — |

Media de 454 párrafos por documento (rango amplio: documentos `alta` tienen más párrafos que `densidad_baja`).

El crecimiento 2022→2024 en número de párrafos (+105%) es coherente con el crecimiento en tokens observado en 5A (+111%), confirmando que las empresas añaden contenido real, no simplemente párrafos más largos.

---

## 2. Selección de K — LDA (coherencia Cv)

| K | Coherencia Cv |
|---|---------------|
| 5 | 0.681 |
| 10 | 0.679 |
| **15** | **0.684** ← óptimo |
| 20 | 0.673 |
| 25 | 0.674 |

La curva de coherencia es relativamente plana (rango 0.672–0.685), lo que es habitual en corpora de reporting corporativo homogéneo. **K=15 es óptimo** pero la diferencia sobre K=5 es pequeña (0.003), lo que indica que los 15 topics son variaciones de ~5 temas centrales con subdivisiones interpretables. Esto es metodológicamente aceptable y coherente con la literatura (Bingler et al. 2022 usan 10-20 topics en corpus similares).

**Para el TFG:** reportar la curva de coherencia (`5b_lda_coherencia.png`) y justificar K=15 por máximo Cv.

---

## 3. Topics LDA K=15 — etiquetas interpretativas

| Topic | Palabras clave | Etiqueta | ESRS | Relevancia RQ |
|-------|---------------|----------|------|---------------|
| **T00** | employees, training, diversity, inclusion, gender, workforce, women | **Capital humano y diversidad** | S1 | RQ1, RQ2 |
| **T01** | data, security, privacy, compliance, regulations, legal, protection | **Privacidad, ciberseguridad y compliance** | S4, G1 | RQ1 |
| **T02** | water, biodiversity, air, pollution, communities, ecosystems, land | **Medio ambiente: agua, biodiversidad, contaminación** | E2, E3, E4 | RQ1 |
| **T03** | million, financial, assets, net, rate, income, cash | **Métricas financieras** | — | Contexto |
| **T04** | human rights, safety, health, suppliers, chain, conduct, corruption | **DDHH, cadena de suministro y ética** | S2, S3, G1 | RQ1, RQ2 |
| **T05** | esrs, gri, disclosure, european, regulation, assurance, standards | **Marco normativo y reporting ESRS/GRI** | ESRS2 | **RQ4** |
| **T06** | emissions, energy, scope, ghg, carbon, renewable, net zero | **Emisiones GHG y energía (clima)** | E1 | RQ1, RQ3 |
| **T07** | climate risk, portfolio, physical, scenario, insurance, investment | **Riesgo climático financiero (TCFD)** | E1, ESRS2 | RQ3 |
| **T08** | board, committee, directors, remuneration, governance, shareholders | **Gobierno corporativo** | G1 | RQ1, RQ2 |
| **T09** | climate impacts, materiality, IROs, value chain, assessment | **Doble materialidad e IROs** | ESRS2 | **RQ4** |
| **T10** | sustainable solutions, customers, innovation, digital, strategy | **Estrategia e innovación sostenible** | ESRS2 | RQ2 |
| **T11** | taxonomy, eligible, aligned, capex, opex, turnover | **Taxonomía UE (alineación económica)** | — | **RQ4** |
| **T12** | shares, capital, debt, funding, france, credit | **Capital y financiación** | — | Contexto |
| **T13** | waste, materials, packaging, circular, raw, recycl | **Economía circular y residuos** | E5 | RQ1 |
| **T14** | esg management, internal process, monitoring, strategy, control | **Sistemas de gestión ESG** | ESRS2, G1 | RQ3 |

### Notas sobre topics específicos

- **T00 — "music":** palabra anómala entre employees/diversity, probablemente artefacto de un informe con sección de cultura corporativa (nombre de empresa/iniciativa). No invalida el topic. En publicación, etiquetar simplemente como "Capital humano y diversidad".

- **T03 y T12 — Topics financieros:** la presencia de dos topics de contenido financiero (métricas de P&L y estructura de capital) en la sección `sus` se explica porque muchos documentos integran tablas de KPIs financieros dentro de la sección de sostenibilidad. Son señal de la estructura híbrida del corpus (Decisión 017: `sus ⊂ mr`). Para análisis de RQ1, se pueden agrupar o excluir como "no-ESG".

- **T07 — AXA específico:** "axa", "insurance", "portfolio" apuntan a que el topic captura específicamente el sector asegurador (AXA, Allianz). Es un topic válido para RQ2 (diferencias por sector).

- **T11 — Taxonomía UE:** la presencia de "capex", "opex", "turnover", "eligible", "aligned" refleja las tablas de alineación con la Taxonomía UE obligatorias para grandes PIEs. Su crecimiento 2022→2024 en BERTopic será una señal directa de RQ4.

- **T05 + T09 + T11:** los tres topics de mayor relevancia para RQ4. Todos reflejan el lenguaje específico de CSRD/ESRS que no existía bajo NFRD. Su evolución temporal (topics_over_time) es la evidencia cuantitativa central del TFG.

---

## 4. Agrupación por ESRS para análisis

Para simplificar la presentación en el TFG, los 15 topics se pueden agrupar en 6 bloques:

| Bloque | Topics | Descripción |
|--------|--------|-------------|
| **Clima** | T06, T07 | E1: emisiones y riesgo climático financiero |
| **Naturaleza** | T02 | E2/E3/E4: agua, biodiversidad, contaminación |
| **Economía circular** | T13 | E5: residuos y materiales |
| **Social** | T00, T04 | S1-S4: personas, DDHH, cadena de suministro |
| **Gobernanza** | T01, T08, T14 | G1/S4: gobierno, compliance, gestión ESG |
| **Marco CSRD** | T05, T09, T11 | ESRS2 + Taxonomía: normativa emergente |
| **Contexto** | T03, T10, T12 | Financiero, estrategia, capital |

---

## 5. Tablas y figuras — descripción detallada

### `5b_paragrafos.parquet`

**Qué contiene:** cada párrafo extraído de los 289 documentos `sus`, con columnas `doc_id, empresa, año, confianza, para_idx, text`. Es el input de todos los modelos de topic modeling.

**Cómo usarla:** punto de entrada para BERTopic, LDA y análisis de sentimiento de 5C (troceo en frases). El campo `para_idx` permite reconstruir el orden original dentro del documento.

---

### `5b_lda_coherencia.csv` + `5b_lda_coherencia.png`

**Qué mide:** la coherencia semántica Cv de cada modelo LDA entrenado, para K∈{5,10,15,20,25}. Cv mide la co-ocurrencia de las palabras top de cada topic en ventanas de texto reales — cuanto más alta, más interpretables son los topics.

**Conclusión:** la curva es plana (0.672–0.685), típico de corpora homogéneos de reporting corporativo donde el vocabulario está muy controlado. K=15 maximiza Cv. La figura es **directamente citable en el capítulo de Metodología** para justificar la elección de K.

**Lo que NO mide:** la utilidad práctica de los topics ni su correspondencia con categorías ESRS. Eso requiere interpretación cualitativa (ver §3 de este documento).

---

### `5b_lda_topics.csv`

**Qué contiene:** para cada uno de los 15 topics, las 15 palabras con mayor peso probabilístico y sus scores. Una fila = un topic.

**Cómo leerlo:** las palabras de mayor score son las más "características" del topic — aparecen con mucha frecuencia en párrafos asignados a ese topic y poco en los demás. No son simplemente las más frecuentes del corpus (eso lo filtra LDA).

**Para el TFG:** convertir esta tabla en la "tabla de topics" del capítulo de Resultados, añadiendo la columna de etiqueta interpretativa (ver §3).

---

### `5b_lda_topics_barplot.png`

**Qué muestra:** para cada uno de los 12 topics más grandes (de 15), un barplot horizontal con las 10 palabras de mayor peso. Formato de cuadrícula 3×4.

**Conclusión visual:** confirma la separabilidad temática de los topics — cada panel tiene un perfil léxico diferenciado. Topics como T06 (ghg, scope, emissions, carbon) y T08 (board, committee, directors) son especialmente limpios. T03 y T12 muestran mezcla de términos financieros, lo que los identifica como topics "contaminados" por el contexto de reporting integrado.

**Para el TFG:** figura de referencia en el Anexo o en el apartado de topic modeling. No es necesario incluir los 15; seleccionar los 8-10 más relevantes para las RQs.

---

### `5b_lda_doc_topics.csv` — Distribución topic × párrafo

**Qué contiene:** cada fila = un párrafo; columnas T00–T14 = probabilidad LDA de pertenecer a cada topic (valores entre 0 y 1, suman 1). Una fila con T06=0.72 significa que ese párrafo es 72% sobre emisiones GHG.

**Cómo agregar a nivel documento:** `df.groupby('doc_id')[topic_cols].mean()` da la distribución temática media de cada documento. El "topic dominante" es `argmax` por párrafo.

**Uso previsto en 5E:**
- Topic dominante por empresa × año → clustering jerárquico (RQ2)
- Evolución de peso de T05/T09/T11 (topics CSRD) por año → test t pareado (RQ4)
- Correlación peso T07 (riesgo climático) × GW_index (RQ3)

**Nota:** esta tabla tiene 131.140 filas (una por párrafo), no 289. Para análisis a nivel documento, siempre agregar primero.

---

## 6. BERTopic — resultados

> Modelo: `all-MiniLM-L6-v2` (MPS) → UMAP(5D, cosine) → HDBSCAN(min_cluster_size=50) → c-TF-IDF.
> Ejecución: 2.5 min (con embeddings cacheados en `results/models/bertopic_sus_embeddings.npy`,
> 17.7 min si se recalculan desde cero). Modelo serializado en `results/models/bertopic_sus/bertopic_model`.

### `5b_bertopic_topics.csv`

**Qué contiene:** 339 topics + el topic -1 (outliers), con columnas `Topic, Count, Name, Representation`. `Count` = nº de párrafos asignados; `Name` = etiqueta auto-generada (palabras top c-TF-IDF); `Representation` = lista completa de palabras/n-gramas representativos.

**Resultado global:**

| Métrica | Valor |
|---------|-------|
| Topics encontrados (sin contar -1) | 339 |
| Outliers (topic -1) | 48,355 / 131,140 (36.9%) |
| Párrafos en topics asignados | 82,785 (63.1%) |

**Top 20 topics por tamaño:**

| Topic | Count | Nombre | Lectura |
|-------|-------|--------|---------|
| -1 | 48,355 | *(outliers)* | emissions/scope/risk/risks — mezcla heterogénea, no interpretable como topic único |
| 0 | 4,200 | human rights, suppliers, due diligence, supply chain | DDHH y cadena de suministro — coincide con T04 LDA (S2/S3) |
| 1 | 2,155 | aena, airport, airports | Específico de empresa (Aena) — sector aeroportuario |
| 2 | 1,816 | board, director, directors, supervisory | Gobierno corporativo — coincide con T08 LDA (G1) |
| 3 | 1,522 | water, water consumption, withdrawal, wastewater | Gestión del agua — subtema de T02 LDA (E3) |
| 4 | 1,478 | bouygues, bouygues construction/immobilier | Específico de empresa (Bouygues) |
| 5 | 1,387 | axa, axas, axa groups, insurance | Específico de empresa (AXA) — coincide con T07 LDA |
| 6 | 1,336 | valeo, sustainable development, carbon neutrality | Específico de empresa (Valeo) |
| 7 | 1,155 | materiality, double materiality, materiality assessment, IROs | **Doble materialidad — coincide con T09 LDA (ESRS2)** |
| 8 | 1,110 | biodiversity, ecosystems, species | Biodiversidad — subtema de T02 LDA (E4) |
| 9 | 1,095 | porsche, vehicle, volkswagen | Específico de empresa (Porsche/VW) |
| 10 | 1,091 | orange, digital, equipment | Específico de empresa (Orange) |
| 11 | 1,087 | orkla, companies | Específico de empresa (Orkla) |
| 12 | 1,064 | learning, talent, skills, development | Desarrollo del talento — subtema de T00 LDA (S1) |
| 13 | 1,038 | mercedes-benz, vans, mercedes cars | Específico de empresa (Mercedes-Benz) |
| 14 | 985 | pernod, ricard, drinking | Específico de empresa (Pernod Ricard) |
| 15 | 954 | climate-related, physical, climate-related risks, scenario | **Riesgo climático físico — coincide con T07 LDA** |
| 16 | 807 | taxonomy, taxonomy regulation, economic activities, eligible | **Taxonomía UE — coincide con T11 LDA** |
| 17 | 806 | caixabank, financing | Específico de empresa (CaixaBank) |
| 18 | 745 | shares, voting, shareholders, meeting | Estructura accionarial — subtema de T08/T12 LDA |

**Diferencia clave con LDA:** BERTopic agrupa por similitud semántica en embeddings (384→5 dims), capturando granularidad mucho mayor. Mientras LDA produce 15 macro-temas, BERTopic detecta tanto **subtemas ESRS específicos** (agua, biodiversidad, doble materialidad, taxonomía — cada uno como topic propio) como **topics específicos de empresa** (AXA, Aena, Bouygues, Porsche, Valeo, Orkla, Mercedes-Benz, Pernod Ricard, Orange, CaixaBank, Campari, Ontex). Esto es esperable: estas empresas usan vocabulario de marca/producto muy distintivo (nombres propios, líneas de producto) que el embedding semántico agrupa naturalmente, y que LDA (basado en co-ocurrencia léxica general) diluye dentro de topics más amplios.

**El 36.9% de outliers** es coherente con `min_cluster_size=50` sobre un corpus heterogéneo: párrafos genéricos de transición, boilerplate legal, o mezclas temáticas que no forman un cluster denso. Se excluyen del análisis (no se interpretan como "topic -1").

**Para el TFG:** usar esta tabla como evidencia de robustez — los topics más grandes y temáticamente puros (T0, T2, T3, T7, T8, T15, T16) **validan independientemente** los topics LDA correspondientes (triangulación, Decisión 023). Los topics específicos de empresa (T1, T4, T5, T6, T9, T10, T11, T13, T14, T17) son útiles para RQ2 (diferencias por empresa/sector) pero deben agruparse o filtrarse para análisis agregados de contenido ESG.

---

### `5b_bertopic_para_topics.parquet`

**Qué contiene:** el parquet de párrafos (`5b_paragrafos.parquet`, 131,140 filas) enriquecido con la columna `topic` (entero, -1 = outlier, 0-338 = topic asignado).

**Uso clave:** cruzar `topic` × `año` × `empresa` para análisis de evolución temporal (RQ4) y diferencias sectoriales/empresariales (RQ2). Es el input directo de `5b_topics_over_time.csv`.

---

### `5b_bertopic_barchart.png`

**Qué muestra:** barplot horizontal de los 20 topics más frecuentes (en nº de párrafos asignados, sin contar -1), con sus nombres auto-generados.

**Para el TFG:** figura comparativa con el barplot LDA (`5b_lda_topics_barplot.png`) — la coexistencia de topics ESRS genéricos (DDHH, agua, biodiversidad, materialidad, taxonomía, riesgo climático, gobierno) con topics específicos de empresa demuestra que BERTopic captura tanto la dimensión normativa común como la heterogeneidad real del corpus (estructura híbrida `sus ⊂ mr`, Decisión 017).

---

### `5b_topics_over_time.csv` + `5b_topics_over_time.png`

**Qué mide:** para cada uno de los 339 topics, su frecuencia (nº de párrafos) en cada uno de los 3 años (2022, 2023, 2024). 1.003 filas (año × topic, con huecos donde un topic no aparece en un año).

**Resultado clave para RQ4 — topics con mayor crecimiento absoluto 2022→2024 (entre los 60 topics más grandes):**

| Topic | 2022 | 2023 | 2024 | Crecimiento | Ratio 2024/2022 | Nombre |
|-------|------|------|------|-------------|------------------|--------|
| **T7** | 104 | 186 | 865 | +761 | **8.2×** | Doble materialidad / IROs |
| T0 | 936 | 1,222 | 2,042 | +1,106 | 2.2× | DDHH y cadena de suministro |
| T3 | 292 | 366 | 864 | +572 | 3.0× | Agua |
| T8 | 193 | 242 | 675 | +482 | 3.5× | Biodiversidad |
| T29 | 91 | 143 | 393 | +302 | 4.3× | Whistleblowing |
| T31 | 99 | 110 | 390 | +291 | 3.9× | Negociación colectiva / diálogo social |
| **T16** | 199 | 259 | 349 | +150 | 1.8× | **Taxonomía UE** |
| T15 | 252 | 266 | 436 | +184 | 1.7× | Riesgo climático físico (TCFD) |

**Hallazgo central RQ4:** el topic **T7 "doble materialidad / IROs"** crece **8.2×** entre 2022 y 2024 (104→865 párrafos), el mayor crecimiento relativo de cualquier topic grande. La doble materialidad es el concepto central introducido por **CSRD/ESRS** (no existía bajo NFRD) — su explosión en 2024 (primer ejercicio CSRD obligatorio para grandes PIEs) es **evidencia textual directa y cuantificada** del cambio de régimen regulatorio. Esto confirma y refina el hallazgo de T09 LDA ("doble materialidad e IROs").

El topic **T16 "Taxonomía UE"** crece de forma más moderada (199→349, +1.8×) porque la Taxonomía UE ya era parcialmente exigible desde 2022 (fases de implementación progresiva del Reglamento 2020/852); su crecimiento refleja la ampliación de actividades elegibles/alineadas reportadas, no la aparición ex novo del tema (a diferencia de T7).

T0 (DDHH/cadena de suministro, +1,106 párrafos en términos absolutos) y T3/T8 (agua, biodiversidad) muestran el crecimiento general de cobertura ESG ya documentado en 5A (+111% tokens 2022→2024), consistente con mayor detalle en todas las categorías ESRS, no solo las nuevas.

**Para el TFG:** la figura `5b_topics_over_time.png` (líneas T7, T16, T15, T0, T3, T8) es **la evidencia visual central de RQ4**. Recomendación: presentar T7 como hallazgo principal (crecimiento más pronunciado y conceptualmente ligado a CSRD), con T16 y T15 como evidencia complementaria de profundización temática bajo el nuevo marco.

---

## 7. Para el TFG — qué reportar de 5B

| Elemento | Dónde | Capítulo TFG |
|----------|-------|--------------|
| Curva de coherencia (K=15) | `5b_lda_coherencia.png` | Metodología |
| Tabla topics con etiquetas | `5b_lda_topics.csv` + tabla arriba | Resultados RQ1 |
| Barplot top palabras por topic | `5b_lda_topics_barplot.png` | Resultados RQ1 |
| Top 20 topics BERTopic | `5b_bertopic_topics.csv` + `5b_bertopic_barchart.png` | Resultados RQ1 (triangulación) |
| Evolución topics CSRD 2022→2024 (T7 doble materialidad +8.2×, T16 Taxonomía +1.8×) | `5b_topics_over_time.png` | **Resultados RQ4** |
| Párrafos por año (crecimiento +105%) | `5b_paragrafos.parquet` stats | Resultados RQ4 |

---

## 8. Resumen ejecutivo BERTopic

- **339 topics** (HDBSCAN, min_cluster_size=50), **36.9% outliers** (esperado, corpus heterogéneo).
- **Triangulación con LDA confirmada**: los 8 topics LDA principales (S1, E1-E5, G1, ESRS2/CSRD)
  tienen equivalentes directos entre los topics BERTopic más grandes (T0, T2, T3, T7, T8, T15, T16).
- **Granularidad adicional**: BERTopic separa subtemas ESRS (agua, biodiversidad, materialidad,
  taxonomía, riesgo climático físico) que en LDA quedaban mezclados dentro de topics más amplios,
  y aísla 11 topics específicos de empresa (AXA, Aena, Bouygues, Porsche/VW, Valeo, Orkla,
  Mercedes-Benz, Pernod Ricard, Orange, CaixaBank, Campari, Ontex) — útiles para RQ2.
- **Hallazgo RQ4**: T7 (doble materialidad/IROs) crece 8.2× 2022→2024 — la señal textual más
  fuerte de transición NFRD→CSRD encontrada hasta ahora en el proyecto.
