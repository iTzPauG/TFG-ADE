# Fase 5B — Interpretación de resultados

> **Corpus ampliado — 196 empresas / 586 documentos `sus` (Decisión 036).**
> LDA y BERTopic **re-entrenados desde cero** sobre 245.400 párrafos (antes
> 131.140 sobre 97 empresas). El K óptimo de LDA cambia de 15 a **25**, y
> BERTopic pasa de 339 a **578 topics** — los IDs de topic **no son
> comparables 1:1** con la versión anterior (Decisión 022), pero el contenido
> temático y los hallazgos de RQ1/RQ4 se replican y refinan.

> Generado con `scripts/nlp/fase5b_topics.py` (Decisión 022/036).
> Tablas en `results/tables/5b_*.csv` · Figuras en `results/figures/5b_*.png` · Modelos en `results/models/`.

---

## 1. Segmentación del corpus en párrafos

| Año | Párrafos | % del total |
|-----|----------|-------------|
| 2022 | 62.053 | 25.3% |
| 2023 | 74.767 | 30.5% |
| 2024 | 108.580 | 44.2% |
| **Total** | **245.400** | — |

Media de ~419 párrafos por documento (586 docs). El crecimiento 2022→2024 en número de
párrafos (+75%) es coherente con el crecimiento en tokens observado en 5A (mediana
+147%), confirmando que las empresas añaden contenido real, no simplemente párrafos
más largos. La proporción relativa por año (25/31/44%) es muy similar a la de la
muestra original (23/31/47%).

---

## 2. Selección de K — LDA (coherencia Cv)

| K | Coherencia Cv |
|---|---------------|
| 5 | 0.6442 |
| 10 | 0.6944 |
| 15 | 0.6832 |
| 20 | 0.6934 |
| **25** | **0.7060** ← óptimo |
| 30 | 0.6839 |

A diferencia de la muestra original (curva plana, 0.672–0.685, óptimo en K=15), con
586 docs la curva sube de forma más clara hasta K=25 (Cv=0.706) y vuelve a bajar en
K=30. **K=25 es el nuevo óptimo**: con más del doble de párrafos, el corpus soporta una
descomposición temática más fina sin perder coherencia — esperable, dado que LDA
necesita suficientes documentos por topic para estimar distribuciones estables.

**Para el TFG:** reportar la curva de coherencia (`5b_lda_coherencia.png`) y justificar
K=25 por máximo Cv. Mencionar que la ampliación de la muestra (97→196 empresas) permitió
una granularidad temática mayor (15→25 topics) sin degradar la coherencia.

---

## 3. Topics LDA K=25 — etiquetas interpretativas

| Topic | Palabras clave (top 7) | Etiqueta | ESRS | Relevancia RQ |
|-------|------------------------|----------|------|---------------|
| **T00** | waste, products, materials, use, product, circular, economy | **Economía circular y residuos** | E5 | RQ1 |
| **T01** | requirements, regulations, standards, companies, standard, compliance, regulatory | **Marco normativo general (ISO, regulación)** | ESRS2 | RQ1, RQ4 |
| **T02** | compliance, conduct, code, corruption, ethics, policy, employees | **Ética, anticorrupción y código de conducta** | G1 | RQ1, RQ2 |
| **T03** | stakeholders, engagement, survey, employees, dialogue, stakeholder, industry | **Diálogo con grupos de interés** | ESRS2 | RQ1 |
| **T04** | sustainable, development, strategy, commitment, people, culture, ensure | **Estrategia y compromiso de sostenibilidad** | ESRS2 | RQ2 |
| **T05** | investment, portfolio, financial, assets, investments, companies, capital | **Inversión y activos financieros (sector financiero)** | — | RQ2, contexto |
| **T06** | risk, management, internal, process, risks, measures, system | **Sistemas de gestión de riesgos** | ESRS2, G1 | RQ3 |
| **T07** | activities, taxonomy, eligible, aligned, economic, activity, capex | **Taxonomía UE (alineación económica)** | — | **RQ4** |
| **T08** | targets, target, carbon, climate, transition, zero, plan | **Metas climáticas y planes de transición** | E1 | RQ1, RQ3 |
| **T09** | due, could, increased, increase, market, costs, changes | **Lenguaje de riesgo financiero (boilerplate)** | — | Contexto |
| **T10** | risks, climate, impacts, opportunities, material, related, risk | **Doble materialidad (riesgos/impactos/oportunidades)** | ESRS2 | **RQ4** |
| **T11** | new, training, development, support, program, learning, digital | **Formación y desarrollo del talento** | S1 | RQ1 |
| **T12** | sustainability, performance, esg, strategy, environmental, governance, management | **Resumen ejecutivo ESG / desempeño** | ESRS2 | RQ2 |
| **T13** | water, sites, production, air, site, consumption, pollution | **Agua, emisiones al aire y contaminación local** | E2, E3 | RQ1 |
| **T14** | employees, health, safety, employee, work, diversity, workforce | **Plantilla propia: salud, seguridad y diversidad** | S1 | RQ1, RQ2 |
| **T15** | board, committee, executive, directors, management, members, remuneration | **Gobierno corporativo** | G1 | RQ1, RQ2 |
| **T16** | energy, consumption, hydro, renewable, electricity, efficiency, gas | **Energía y eficiencia energética** | E1 | RQ1, RQ3 |
| **T17** | data, services, customers, customer, security, service, products | **Productos, clientes y ciberseguridad/privacidad** | S4 | RQ1 |
| **T18** | reporting, esrs, financial, gri, sustainability, statements, disclosure | **Marco de reporting ESRS/GRI/CSRD** | ESRS2 | **RQ4** |
| **T19** | million, share, net, revenue, income, per, december | **Métricas financieras (P&L)** | — | Contexto |
| **T20** | years, france, first, europe, two, spain, germany | **Geografía / contexto internacional** | — | Contexto |
| **T21** | biodiversity, environmental, impact, impacts, areas, communities, local | **Biodiversidad e impactos en comunidades locales** | E4, S3 | RQ1 |
| **T22** | emissions, scope, ghg, data, emission, gas, greenhouse | **Emisiones GHG (Scope 1/2/3)** | E1 | RQ1, RQ3 |
| **T23** | human, rights, labour, principles, workers, labor, due | **Derechos humanos y debida diligencia laboral** | S2 | RQ1, RQ2 |
| **T24** | chain, suppliers, value, supply, supplier, procurement, prime | **Cadena de suministro y proveedores** | S2 | RQ1, RQ2 |

### Notas sobre topics específicos

- **Comparación con K=15 (Decisión 022):** la mayoría de los 15 topics originales se
  "desdoblan" en 2-3 topics más finos con K=25. Por ejemplo, el antiguo T02 (agua +
  biodiversidad + contaminación, E2/E3/E4) ahora se separa en **T13** (agua/aire/
  contaminación, E2/E3) y **T21** (biodiversidad/comunidades, E4/S3); el antiguo T06
  (emisiones+energía, E1) se separa en **T22** (emisiones GHG) y **T16** (energía).
  Esta granularidad mayor es consistente con el aumento de Cv (0.684→0.706).

- **T09 — lenguaje de riesgo financiero genérico:** topic "boilerplate" (could, due,
  increased, costs, changes, market) — equivalente al antiguo T03/T09-mezcla. Refleja
  la estructura híbrida del corpus (`sus ⊂ mr`, Decisión 017): secciones de
  sostenibilidad que incorporan lenguaje estándar de "factores de riesgo" del informe
  anual. Para RQ1 se puede agrupar como "no-ESG" / contexto.

- **T07 — Taxonomía UE:** "taxonomy, eligible, aligned, capex, opex, turnover,
  activities" — equivalente directo al antiguo T11. Topic limpio y muy específico de
  CSRD/Taxonomía Reglamento (UE) 2020/852.

- **T10 — Doble materialidad:** "risks, climate, impacts, opportunities, material,
  related, materiality, assessment" — equivalente directo al antiguo T09, ahora más
  puro (separado del lenguaje de riesgo financiero genérico, que migra a T09).

- **T01 + T18 — Marco normativo / reporting ESRS:** dos topics relacionados con el
  lenguaje regulatorio: T01 es más genérico (ISO, "regulations", "standards"), T18 es
  específico de reporting de sostenibilidad ("esrs, gri, sustainability, statements,
  disclosure"). Ambos relevantes para RQ4 — equivalentes al antiguo T05.

- **T07, T10, T18 — los tres topics de mayor relevancia para RQ4** (igual que en la
  muestra original T05/T09/T11). Todos reflejan el lenguaje específico de CSRD/ESRS
  que no existía bajo NFRD. Su evolución temporal (vía BERTopic, §6) sigue siendo la
  evidencia cuantitativa central del TFG.

---

## 4. Agrupación por ESRS para análisis

Para simplificar la presentación en el TFG, los 25 topics se pueden agrupar en 7 bloques:

| Bloque | Topics | Descripción |
|--------|--------|-------------|
| **Clima** | T08, T16, T22 | E1: metas/transición, energía, emisiones GHG |
| **Naturaleza** | T13, T21 | E2/E3/E4: agua, aire, contaminación, biodiversidad, comunidades |
| **Economía circular** | T00 | E5: residuos y materiales |
| **Social (propio)** | T11, T14 | S1: formación, salud, seguridad, diversidad |
| **Social (cadena de valor)** | T23, T24 | S2/S3: DDHH, debida diligencia, proveedores |
| **Gobernanza y conducta** | T02, T06, T15, T17 | G1/S4: gobierno, riesgos, ética, ciberseguridad |
| **Marco CSRD/Taxonomía** | T01, T07, T10, T18 | ESRS2 + Taxonomía: normativa emergente |
| **Contexto** | T03, T04, T05, T09, T12, T19, T20 | Stakeholders, estrategia, financiero, geografía |

---

## 5. Tablas y figuras — descripción detallada

### `5b_paragrafos.parquet`

**Qué contiene:** cada párrafo extraído de los **586** documentos `sus`, con columnas
`doc_id, empresa, año, confianza, para_idx, text` (245.400 filas). Es el input de todos
los modelos de topic modeling.

**Cómo usarla:** punto de entrada para BERTopic, LDA y análisis de sentimiento de 5C
(troceo en frases). El campo `para_idx` permite reconstruir el orden original dentro
del documento.

---

### `5b_lda_coherencia.csv` + `5b_lda_coherencia.png`

**Qué mide:** la coherencia semántica Cv de cada modelo LDA entrenado, para
K∈{5,10,15,20,25,30}. Cv mide la co-ocurrencia de las palabras top de cada topic en
ventanas de texto reales — cuanto más alta, más interpretables son los topics.

**Conclusión:** la curva ahora tiene un máximo claro en K=25 (Cv=0.706), con K=30
bajando (0.684). La figura es **directamente citable en el capítulo de Metodología**
para justificar la elección de K=25 sobre el corpus ampliado.

**Lo que NO mide:** la utilidad práctica de los topics ni su correspondencia con
categorías ESRS. Eso requiere interpretación cualitativa (ver §3 de este documento).

---

### `5b_lda_topics.csv`

**Qué contiene:** para cada uno de los 25 topics, las 15 palabras con mayor peso
probabilístico y sus scores. Una fila = un topic.

**Cómo leerlo:** las palabras de mayor score son las más "características" del topic —
aparecen con mucha frecuencia en párrafos asignados a ese topic y poco en los demás.
No son simplemente las más frecuentes del corpus (eso lo filtra LDA).

**Para el TFG:** convertir esta tabla en la "tabla de topics" del capítulo de
Resultados, añadiendo la columna de etiqueta interpretativa (ver §3).

---

### `5b_lda_topics_barplot.png`

**Qué muestra:** para los topics más grandes (de 25), un barplot horizontal con las 10
palabras de mayor peso, en cuadrícula.

**Conclusión visual:** confirma la separabilidad temática de los topics — cada panel
tiene un perfil léxico diferenciado. Topics como T22 (emissions, scope, ghg, carbon) y
T15 (board, committee, directors, remuneration) son especialmente limpios. T09 y T19
muestran mezcla de lenguaje financiero/boilerplate, identificándolos como topics
"contaminados" por el contexto de reporting integrado (igual que T03/T12 en K=15).

**Para el TFG:** figura de referencia en el Anexo o en el apartado de topic modeling.
No es necesario incluir los 25; seleccionar los 8-10 más relevantes para las RQs
(T07, T08, T10, T13, T14, T15, T18, T22, T23, T24).

---

### `5b_lda_doc_topics.csv` — Distribución topic × párrafo

**Qué contiene:** cada fila = un párrafo (245.400 filas); columnas T00–T24 = probabilidad
LDA de pertenecer a cada topic (valores entre 0 y 1, suman 1).

**Cómo agregar a nivel documento:** `df.groupby('doc_id')[topic_cols].mean()` da la
distribución temática media de cada documento. El "topic dominante" es `argmax` por
párrafo.

**Uso previsto en 5E:**
- Topic dominante por empresa × año → clustering jerárquico (RQ2)
- Evolución de peso de T07/T10/T18 (topics CSRD) por año → test t pareado (RQ4)
- Correlación peso T08/T22 (clima) × GW_index (RQ3)

**Nota:** esta tabla tiene 245.400 filas (una por párrafo), no 586. Para análisis a
nivel documento, siempre agregar primero.

---

## 6. BERTopic — resultados

> Modelo: `all-MiniLM-L6-v2` (MPS) → UMAP(5D, cosine) → HDBSCAN(min_cluster_size=50) →
> c-TF-IDF. Ejecución completa (586 docs, 245.400 párrafos): ~48 min (embeddings ~30
> min + UMAP ~4 min + HDBSCAN/c-TF-IDF <1 min). Modelo serializado en
> `results/models/bertopic_sus/bertopic_model`.

### `5b_bertopic_topics.csv`

**Qué contiene:** **578 topics** + el topic -1 (outliers), con columnas
`Topic, Count, Name, Representation`.

**Resultado global:**

| Métrica | Valor |
|---------|-------|
| Topics encontrados (sin contar -1) | 578 |
| Outliers (topic -1) | 98.721 / 245.400 (**40.2%**) |
| Párrafos en topics asignados | 146.679 (59.8%) |

El número de topics casi se duplica (339→578) y el % de outliers sube ligeramente
(36.9%→40.2%), coherente con un corpus más grande y heterogéneo: más empresas →
más vocabulario específico de marca/sector → más clusters pequeños y específicos.

**Top 20 topics por tamaño:**

| Topic | Count | Nombre | Lectura |
|-------|-------|--------|---------|
| -1 | 98.721 | *(outliers)* | mezcla heterogénea (emisiones/scope/riesgo/financiero), no interpretable como topic único |
| 0 | 3.608 | physical, climate-related, climate, climate-related risks | **Riesgo climático físico (TCFD)** — equivalente al antiguo T15 |
| 1 | 3.129 | board, director, directors, independent | Gobierno corporativo — equivalente al antiguo T2 |
| 2 | 3.003 | suppliers, supplier, procurement, ecovadis | Cadena de suministro y evaluación de proveedores (EcoVadis) |
| 3 | 2.964 | water, water consumption, withdrawal, wastewater | Gestión del agua — equivalente al antiguo T3 |
| 4 | 2.291 | biodiversity, ecosystems, species, biodiversity ecosystems | Biodiversidad — equivalente al antiguo T8 |
| 5 | 2.012 | women, female, gender, positions | Diversidad de género |
| 6 | 1.795 | fresenius, patients, patient, medical | Específico de empresa (Fresenius) — sector salud |
| 7 | 1.770 | aena, airport, airports, aenas | Específico de empresa (Aena) — equivalente al antiguo T1 |
| 8 | 1.597 | learning, talent, skills, leadership | Desarrollo del talento |
| 9 | 1.573 | safety, health safety, health, occupational | Salud y seguridad laboral |
| 10 | 1.549 | axa, axas, axa groups, insurance | Específico de empresa (AXA) — equivalente al antiguo T5 |
| 11 | 1.524 | committee, sustainability, board, sustainability committee | Comité de sostenibilidad (gobernanza ESG) |
| 12 | 1.439 | bouygues, bouygues construction/immobilier | Específico de empresa (Bouygues) — equivalente al antiguo T4 |
| 13 | 1.398 | waste, disposal, nonhazardous, hazardous waste | Gestión de residuos |
| 14 | 1.380 | corruption, anticorruption, bribery, antibribery | Anticorrupción |
| 15 | 1.350 | human rights, rights, human, declaration | Derechos humanos — equivalente al antiguo T15(LDA-K15) |
| **16** | **1.330** | **materiality, double materiality, double, materiality assessment** | **Doble materialidad — equivalente al antiguo T7** |
| **17** | **1.305** | **taxonomy, taxonomy regulation, regulation, economic activities** | **Taxonomía UE — equivalente al antiguo T16** |
| 18 | 1.274 | valeo, valeos, sustainable development, carbon neutrality | Específico de empresa (Valeo) — equivalente al antiguo T6 |
| 19 | 1.190 | security, cyber, cybersecurity, cyber security | Ciberseguridad |

**Diferencia clave con LDA:** BERTopic agrupa por similitud semántica en embeddings
(384→5 dims), capturando granularidad mucho mayor. Mientras LDA produce 25 macro-temas,
BERTopic detecta tanto **subtemas ESRS específicos** (agua, biodiversidad, doble
materialidad, taxonomía, ciberseguridad, anticorrupción — cada uno como topic propio)
como **topics específicos de empresa** (Fresenius, Aena, AXA, Bouygues, Valeo, y muchos
más entre los 578). Con el doble de empresas en la muestra, el número de topics
específicos de empresa también aumenta proporcionalmente — esperable.

**El 40.2% de outliers** (ligeramente superior al 36.9% original) es coherente con
`min_cluster_size=50` sobre un corpus más grande y heterogéneo: más párrafos
"genéricos" de transición o boilerplate legal que no forman clusters densos
adicionales. Se excluyen del análisis (no se interpretan como "topic -1").

**Para el TFG:** usar esta tabla como evidencia de robustez — los topics más grandes y
temáticamente puros (T0, T1, T3, T4, T16, T17, T22 entre otros) **validan
independientemente** los topics LDA correspondientes (triangulación, Decisión 023).
Los topics específicos de empresa son útiles para RQ2 (diferencias por
empresa/sector) pero deben agruparse o filtrarse para análisis agregados de contenido
ESG.

---

### `5b_bertopic_para_topics.parquet`

**Qué contiene:** el parquet de párrafos (`5b_paragrafos.parquet`, 245.400 filas)
enriquecido con la columna `topic` (entero, -1 = outlier, 0-577 = topic asignado).

**Uso clave:** cruzar `topic` × `año` × `empresa` para análisis de evolución temporal
(RQ4) y diferencias sectoriales/empresariales (RQ2). Es el input directo de
`5b_topics_over_time.csv`.

---

### `5b_bertopic_barchart.png`

**Qué muestra:** barplot horizontal de los 20 topics más frecuentes (en nº de párrafos
asignados, sin contar -1), con sus nombres auto-generados.

**Para el TFG:** figura comparativa con el barplot LDA (`5b_lda_topics_barplot.png`) —
la coexistencia de topics ESRS genéricos (agua, biodiversidad, materialidad, taxonomía,
gobierno, ciberseguridad, anticorrupción) con topics específicos de empresa demuestra
que BERTopic captura tanto la dimensión normativa común como la heterogeneidad real del
corpus ampliado (estructura híbrida `sus ⊂ mr`, Decisión 017).

---

### `5b_topics_over_time.csv` + `5b_topics_over_time.png`

**Qué mide:** para cada uno de los 578 topics, su frecuencia (nº de párrafos) en cada
uno de los 3 años (2022, 2023, 2024). 1.692 filas (año × topic, con huecos donde un
topic no aparece en un año).

**Resultado clave para RQ4 — topics con mayor crecimiento absoluto/relativo
2022→2024 (entre los 60 topics más grandes):**

| Topic | 2022 | 2023 | 2024 | Δ absoluto | Ratio 2024/2022 | Nombre |
|-------|------|------|------|------------|------------------|--------|
| **T16** | 107 | 222 | 1.001 | +894 | **9.3×** | **Doble materialidad** |
| T4 | 408 | 527 | 1.356 | +948 | 3.3× | Biodiversidad |
| T3 | 641 | 828 | 1.495 | +854 | 2.3× | Agua |
| T0 | 870 | 1.030 | 1.708 | +838 | 2.0× | Riesgo climático físico (TCFD) |
| T2 | 807 | 903 | 1.293 | +486 | 1.6× | Cadena de suministro/proveedores |
| T11 | 349 | 384 | 791 | +442 | 2.3× | Comité de sostenibilidad |
| T15 | 294 | 351 | 705 | +411 | 2.4× | Derechos humanos |
| T49 | 99 | 133 | 406 | +307 | 4.1× | Diálogo con grupos de interés |
| T40 | 114 | 172 | 453 | +339 | 3.9× | Whistleblowing |
| **T17** | 346 | 386 | 573 | +227 | 1.7× | **Taxonomía UE** |

**Hallazgo central RQ4 (replica y refina T7/T09 de la muestra original):** el topic
**T16 "doble materialidad"** crece **9.3×** entre 2022 y 2024 (107→1.001 párrafos), el
mayor crecimiento relativo de cualquier topic grande — incluso más pronunciado que el
8.2× observado en la muestra de 97 empresas (T7, 104→865). La doble materialidad es el
concepto central introducido por **CSRD/ESRS** (no existía bajo NFRD) — su explosión en
2024 (primer ejercicio CSRD obligatorio para grandes PIEs) sigue siendo **la evidencia
textual más fuerte y cuantificada del cambio de régimen regulatorio**, ahora confirmada
sobre el conjunto completo de 196 empresas del STOXX 600 muestreado.

El topic **T17 "Taxonomía UE"** crece de forma más moderada (346→573, 1.7×, vs 1.8× en
la muestra original) porque la Taxonomía UE ya era parcialmente exigible desde 2022
(fases de implementación progresiva del Reglamento 2020/852); su crecimiento refleja la
ampliación de actividades elegibles/alineadas reportadas, no la aparición ex novo del
tema (a diferencia de T16).

T4 (biodiversidad, 3.3×) y T3 (agua, 2.3×) muestran un crecimiento aún mayor que en la
muestra original (donde eran 3.0× y 1.8×/3.5× respectivamente, con IDs distintos) — el
crecimiento general de cobertura ESG documentado en 5A (E3 +0.10, E4 +0.09 en 2 años)
se confirma a nivel de párrafo con la muestra ampliada.

**Para el TFG:** la figura `5b_topics_over_time.png` (líneas T16, T4, T3, T0, T17) es
**la evidencia visual central de RQ4**. Recomendación: presentar T16 (doble
materialidad) como hallazgo principal (crecimiento más pronunciado y conceptualmente
ligado a CSRD), con T17 (Taxonomía), T0 (riesgo climático físico), T3/T4 (agua/
biodiversidad) como evidencia complementaria de profundización temática bajo el nuevo
marco.

---

## 7. Para el TFG — qué reportar de 5B

| Elemento | Dónde | Capítulo TFG |
|----------|-------|--------------|
| Curva de coherencia (K=25, Cv=0.706) | `5b_lda_coherencia.png` | Metodología |
| Tabla topics K=25 con etiquetas | `5b_lda_topics.csv` + tabla §3 | Resultados RQ1 |
| Barplot top palabras por topic | `5b_lda_topics_barplot.png` | Resultados RQ1 |
| Top 20 topics BERTopic (578) | `5b_bertopic_topics.csv` + `5b_bertopic_barchart.png` | Resultados RQ1 (triangulación) |
| Evolución topics CSRD 2022→2024 (T16 doble materialidad ×9.3, T17 Taxonomía ×1.7) | `5b_topics_over_time.png` | **Resultados RQ4** |
| Párrafos por año (62k/75k/109k, +75%) | `5b_paragrafos.parquet` stats | Resultados RQ4 |

---

## 8. Resumen ejecutivo BERTopic

- **578 topics** (HDBSCAN, min_cluster_size=50), **40.2% outliers** (esperado, corpus
  más grande y heterogéneo que con 97 empresas).
- **Triangulación con LDA K=25 confirmada**: los topics LDA principales (E1-E5, S1-S4,
  G1, ESRS2/CSRD) tienen equivalentes directos entre los topics BERTopic más grandes
  (T0 riesgo climático, T1 gobierno, T2 proveedores, T3 agua, T4 biodiversidad, T13
  residuos, T15 DDHH, T16 doble materialidad, T17 taxonomía, T19 ciberseguridad).
- **Granularidad adicional**: BERTopic separa subtemas ESRS específicos y aísla
  numerosos topics específicos de empresa (Fresenius, Aena, AXA, Bouygues, Valeo, etc.)
  — útiles para RQ2.
- **Hallazgo RQ4**: T16 (doble materialidad) crece **9.3×** 2022→2024 — la señal
  textual más fuerte de transición NFRD→CSRD encontrada en el proyecto, ahora
  confirmada y ligeramente más pronunciada sobre el corpus ampliado de 196 empresas.

---

## 9. Pendiente

Esta reinterpretación cubre los topics y hallazgos principales sobre el corpus
ampliado. Quedan pendientes para una revisión más fina (no bloqueante para 5C-5E ni
para el TFG en su versión actual):

- Mapeo completo de los 578 topics BERTopic a categorías ESRS (solo se han etiquetado
  los 20 más grandes).
- Verificación cualitativa de que ningún topic grande corresponde a contenido
  no-sostenibilidad colado por la segmentación 4C (revisión de muestra aleatoria de
  párrafos por topic).
