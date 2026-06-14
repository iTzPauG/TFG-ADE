# Fase 5A — Interpretación de resultados

> **Corpus ampliado — 196 empresas / 586 documentos `sus` (Decisión 036).**
> Re-ejecutado desde cero sobre `corpus.parquet` (1172 filas = 586 docs × 2
> secciones). La metodología no cambia respecto a la versión original (97
> empresas / 289 docs, Decisión 021); solo los números.

> Generado con `scripts/nlp/fase5a_descriptivos.py` (Decisión 021/036).
> Tablas en `results/tables/5a_*.csv` · Figuras en `results/figures/5a_*.png`.

---

## 1. `5a_descriptivos_corpus.csv` + `5a_distribucion_tokens.png`

**Qué mide:** extensión del texto extraído (en tokens lematizados) por sección y año.

| seccion | año | n   | media  | mediana |
|---------|-----|-----|--------|---------|
| mr      | 2022| 194 | 38.309 | 29.822  |
| mr      | 2023| 196 | 40.617 | 33.939  |
| mr      | 2024| 196 | 39.736 | 31.216  |
| **sus** | **2022**| **194** | **11.208** | **6.894** |
| **sus** | **2023**| **196** | **13.201** | **9.513** |
| **sus** | **2024**| **196** | **20.477** | **17.041** |

**Conclusión principal — señal directa de RQ4:**
La sección `sus` casi se duplica/triplica entre 2022 y 2024 (+83 % en media, **+147 % en
mediana**). La sección `mr` se mantiene estable (~38-41k tokens): el crecimiento textual
sigue siendo específico de la subsección de sostenibilidad, no del informe en su conjunto.

El patrón es **idéntico al de la muestra original** (97 empresas: 10.9k→23.1k en media;
196 empresas: 11.2k→20.5k), confirmando que no es un artefacto de la muestra inicial sino
una tendencia generalizada del STOXX 600: las empresas están expandiendo su reporting ESG
entre el régimen NFRD (2022-23) y el umbral CSRD (2024).

**Nota metodológica:** la diferencia entre media y mediana (ej. sus 2024: 20.5k vs 17.0k)
indica distribución con cola derecha — unas pocas empresas escriben informes muy extensos
(max 108k tokens en 2023), lo que sesga la media. Para análisis estadísticos en 5E usar
mediana o transformación logarítmica.

---

## 2. `5a_cobertura_esrs.csv` — Matriz ESRS (586 × 11)

**Qué mide:** para cada documento `sus`, qué fracción de los términos del diccionario
`esrs_keywords.json` aparece al menos una vez en el texto. Rango [0, 1].

**Importante — qué NO mide:**
- **NO es un score de cumplimiento normativo.** Una empresa puede cubrir E3 (agua) en
  profundidad usando sinónimos o terminología propia sin que aparezcan exactamente nuestros
  keywords. El indicador mide *anchura de vocabulario*, no profundidad ni conformidad legal.
- **NO todas las empresas están bajo CSRD en todos los años.** CSRD solo es de obligado
  cumplimiento para grandes PIEs a partir del ejercicio **FY2024** (primer informe en 2025).
  En 2022-23 las empresas estaban bajo NFRD, que era mucho menos prescriptivo y no requería
  el nivel de detalle de ESRS.

### Cobertura media por categoría y año

| Cat. | Nombre | 2022 | 2023 | 2024 | Δ 22→24 |
|------|--------|------|------|------|---------|
| E1   | Climate Change | 0.393 | 0.444 | **0.558** | +0.165 |
| S1   | Own Workforce | 0.406 | 0.435 | **0.528** | +0.122 |
| ESRS2| Gen. Disclosures | 0.296 | 0.347 | **0.464** | +0.168 |
| G1   | Business Conduct | 0.281 | 0.301 | **0.377** | +0.096 |
| E5   | Circular Economy | 0.240 | 0.280 | **0.360** | +0.120 |
| S2   | Value Chain Workers | 0.193 | 0.220 | **0.313** | +0.120 |
| E3   | Water & Marine | 0.178 | 0.207 | **0.281** | +0.103 |
| S4   | Consumers | 0.171 | 0.198 | **0.263** | +0.092 |
| E4   | Biodiversity | 0.147 | 0.166 | **0.241** | +0.094 |
| S3   | Communities | 0.153 | 0.167 | **0.225** | +0.072 |
| E2   | Pollution | 0.112 | 0.129 | **0.195** | +0.083 |

**Conclusiones (confirman el patrón de la muestra original, 97 empresas):**
- **Todas las categorías crecen** 2022→2024, con el salto mayor en 2023→2024, coherente
  con la inminencia de CSRD. Esto confirma la hipótesis de RQ4 ahora sobre el conjunto
  completo del STOXX 600 muestreado.
- **E1 y S1 siguen siendo las categorías más cubiertas** (0.56 y 0.53 en 2024): clima y
  fuerza laboral son los temas con mayor tradición de reporte bajo NFRD y TCFD.
- **ESRS2 sube de 0.30 a 0.46**: la adopción del lenguaje de doble materialidad,
  gobernanza de sostenibilidad y marcos como ESRS/CSRD/GRI se acelera claramente.
- **E2 (Contaminación) sigue siendo la más baja** (0.20 en 2024). Esto es esperable:
  el reporte de contaminación requiere datos de medición muy específicos (NOx, SOx, VOCs,
  microplásticos) que solo tienen empresas industriales/manufactureras. Para una empresa
  de servicios financieros o tecnología, E2 no es material → no reporta. El bajo valor
  no indica falta de cumplimiento sino un sesgo sectorial real.
- **S3 (Comunidades) baja relativa** (0.23 en 2024): comunidades locales e indígenas son
  material principalmente para sectores extractivos y utilities. En una muestra diversificada
  del STOXX 600, la mayoría de empresas no tienen impactos relevantes aquí.

### ¿Son los valores "bajísimos" para algo obligatorio por ley?

**No, y hay tres razones:**

1. **2022-23 no eran CSRD.** Bajo NFRD las empresas elegían qué reportar entre 5 temas
   amplios (ambiente, social, empleados, DDHH, anticorrupción) sin KPIs obligatorios.
   Que E2=0.11 en 2022 refleja que pocas empresas reportaban contaminación en detalle —
   exactamente lo que CSRD quiere cambiar.

2. **Doble materialidad.** ESRS no obliga a reportar todas las categorías, sino solo las
   que sean materiales para la empresa (impacto o financiero). Una aseguradora no tiene
   por qué reportar E3 (agua) si no tiene exposición material. El bajo valor no es incumplimiento.

3. **El indicador es conservador.** Mide si los términos exactos de nuestro diccionario
   aparecen en el texto. Una empresa puede cubrir E5 (economía circular) con términos como
   "product lifespan", "repair services" o "remanufacturing" sin que aparezca "circular
   economy" o "circularity" — y el indicador la penaliza aunque haya cobertura real.

**Lo que SÍ es relevante** es el **delta 2022→2024** (+0.07 a +0.17 según categoría) y el
crecimiento del texto (+147% en mediana de tokens). Eso es la señal de cumplimiento emergente
de CSRD. Para el TFG, el argumento es: *antes de CSRD las empresas ya reportaban
selectivamente; con CSRD la cobertura léxica de todos los pilares ESRS sube de forma
sistemática, y este patrón se mantiene al ampliar la muestra de 97 a 196 empresas.*

---

## 3. `5a_cobertura_esrs_año.csv` + `5a_cobertura_esrs_año.png`

**Qué mide:** media de cobertura por categoría ESRS y año, en formato pivotado (para el gráfico).

**Para el TFG:** este gráfico de líneas es directamente citable como figura en el capítulo
de resultados de RQ4. Muestra que el perfil de cobertura ESRS cambia entre regímenes normativos.

---

## 4. `5a_heatmap_esrs.png`

**Qué mide:** cobertura media 2022-2024 por empresa (filas) y categoría ESRS (columnas),
ahora con **196 empresas** (antes 97). Ordenado de mayor a menor cobertura total
(empresas arriba = más comprehensivas).

**Para el TFG:** permite identificar outliers visualmente:
- Empresas con alta cobertura en todas las categorías (reporters líderes)
- Empresas con cobertura concentrada en 1-2 categorías (reporters selectivos)
- Filas casi blancas = `densidad_baja` (secciones parciales, ver análisis de sensibilidad)

---

## 5. `5a_tfidf_sus.csv` + `5a_tfidf_mr.csv` + `5a_tfidf_top_{sus,mr}.png`

**Qué mide:** los 20 términos con mayor TF-IDF medio en cada sección. TF-IDF pondera
frecuencia del término en el documento contra su prevalencia en el corpus completo.

**Lectura de los resultados (586 docs):**

Los términos más altos en `sus` son: *sustainability, report, financial, statement,
information, group, non, annual*. En `mr`: *report, annual, financial, statement,
group, universal, sustainability, document*.

**Nota importante:** cuando se aplica TF-IDF a nivel de corpus completo (media de scores),
los términos con score más alto tienden a ser los que aparecen en *muchos* documentos pero
no en todos. Por eso dominan palabras genéricas del contexto de reporting.
Este resultado es esperable y correcto: confirma que el corpus ampliado sigue siendo
coherente y que los 196 informes comparten un vocabulario de reporting corporativo uniforme.

**Lo que aporta para el TFG:**
- Confirma que `sus` y `mr` tienen vocabularios parcialmente solapados pero con diferencias
  clave: `sustainability`, `non` (de "non-financial") son más prominentes en `sus`;
  `universal`, `document` (URD — Universal Registration Document) en `mr`.
- Para discriminación inter-empresa e inter-año, el TF-IDF por grupo (5B/5C) será más
  informativo que el agregado global.

---

## 6. `5a_ngrams_top.csv`

**Qué mide:** los 15 bi/trigramas con mayor TF-IDF medio por sección y año.

**Hallazgos destacables (586 docs):**

| Sección | Año | N-gramas relevantes (top 6) |
|---------|-----|------------------------------|
| sus | 2022 | *annual report, non financial, sustainability report, financial statement, corporate governance, long term* |
| sus | 2023 | *non financial, sustainability report, sustainability statement, annual report, financial statement, approach sustainability* |
| sus | 2024 | **sustainability statement, annual report, sustainability report, general information, corporate governance, non financial** |
| mr  | 2022-24 | *annual report, financial statement, non financial, registration document* |

**Conclusión:** El bigrama *"sustainability statement"* sigue escalando de tercer lugar en
2023 a **primer lugar en 2024**, replicando exactamente el patrón observado en la muestra
original — refleja la adopción del lenguaje CSRD ("Non-Financial Statement" → "Sustainability
Statement"). Con 196 empresas esta señal lingüística de la transición NFRD→CSRD se confirma
a escala del STOXX 600 muestreado.

---

## 7. Análisis de sensibilidad (`densidad_baja`)

Sobre las **586 filas** (Decisión 035), `sus_confianza`: `alta` 233, `densidad` 292,
`densidad_baja` 46, `media` 8, `aceptado_sin_financieros` 7.

Excluyendo las 46 filas `densidad_baja` (secciones parciales), la cobertura media
sube de forma marcada (E1: 0.50 vs 0.08; S1: 0.46-0.53 vs 0.12). El efecto es real y
de magnitud similar al de la muestra original (97 empresas, 16 filas `densidad_baja`),
lo que confirma la Decisión 019: incluirlas en el análisis principal con nota de limitación.

| Confianza | n | E1 | E2 | E3 | S1 | ESRS2 |
|-----------|---|----|----|----|----|-------|
| alta | 233 | 0.507 | 0.177 | 0.237 | 0.525 | 0.425 |
| densidad | 292 | 0.498 | 0.139 | 0.237 | 0.458 | 0.372 |
| media | 8 | 0.179 | 0.067 | 0.129 | 0.244 | 0.167 |
| **densidad_baja** | **46** | **0.083** | **0.016** | **0.042** | **0.121** | **0.088** |
| aceptado_sin_fin. | 7 | 0.541 | 0.305 | 0.399 | 0.555 | 0.468 |

El contraste `alta` vs `densidad_baja` (E1: 0.51 vs 0.08) confirma que estas 46 filas
son secciones parciales, no informes completos — mismo patrón que en la muestra original
(0.57 vs 0.12).

---

## Resumen para el TFG

| Hallazgo | Relevancia |
|----------|-----------|
| Sus 11.2k→20.5k tokens media (2022→2024); mediana 6.9k→17.0k (+147%) | Evidencia directa RQ4: expansión reporting CSRD, confirmada a 196 empresas |
| `sus` crece marcadamente; `mr` estable (~38-41k) | El cambio es específico de sostenibilidad, no del informe |
| E1+S1 = temas más cubiertos (0.56 / 0.53 en 2024) | Coherente con tradición TCFD/GRI pre-CSRD |
| E2+S3 = temas menos cubiertos (0.20 / 0.23 en 2024) | Efecto sectorial + doble materialidad, no incumplimiento |
| Todas las categorías ESRS +7 a +17pp en 2 años | Señal de adopción CSRD sistemática, robusta al ampliar muestra |
| "sustainability statement" → top bigrama 2024 | Cambio léxico NFRD→CSRD capturado, replicado con 196 empresas |
