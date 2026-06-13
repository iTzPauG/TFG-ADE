# Fase 5A — Interpretación de resultados

> **⚠ Foto previa a la ampliación — 97 empresas / 289 documentos `sus`.** Los resultados de este documento se calcularon sobre la **muestra original de 97 empresas (289 docs `sus`)**, antes de la ampliación a 196 (Decisiones 027-035). Tras re-ejecutar la Fase 5 sobre el corpus ampliado (**196 empresas / 586 documentos**) estas cifras deberán actualizarse; la metodología no cambia.

> Generado con `scripts/nlp/fase5a_descriptivos.py` (Decisión 021).
> Tablas en `results/tables/5a_*.csv` · Figuras en `results/figures/5a_*.png`.

---

## 1. `5a_descriptivos_corpus.csv` + `5a_distribucion_tokens.png`

**Qué mide:** extensión del texto extraído (en tokens lematizados) por sección y año.

| seccion | año | n  | media  | mediana |
|---------|-----|----|--------|---------|
| mr      | 2022| 95 | 36.768 | 29.777  |
| mr      | 2023| 97 | 39.601 | 32.110  |
| mr      | 2024| 97 | 36.656 | 30.937  |
| **sus** | **2022**| **95** | **10.947** | **7.138** |
| **sus** | **2023**| **97** | **14.556** | **12.067** |
| **sus** | **2024**| **97** | **23.068** | **19.774** |

**Conclusión principal — señal directa de RQ4:**
La sección `sus` más que se duplica en dos años (+111 % en media, +177 % en mediana).
La sección `mr` se mantiene estable (~36-40k tokens): el crecimiento textual es
específico de la subsección de sostenibilidad, no del informe en su conjunto.

Esto es la primera evidencia cuantitativa de que las empresas STOXX 600 están expandiendo
su reporting ESG entre el régimen NFRD (2022-23) y el umbral CSRD (2024).

**Nota metodológica:** la diferencia entre media y mediana (ej. sus 2024: 23k vs 20k)
indica distribución con cola derecha — unas pocas empresas escriben informes muy extensos
(max 88k tokens), lo que sesga la media. Para análisis estadísticos en 5E usar mediana o
transformación logarítmica.

---

## 2. `5a_cobertura_esrs.csv` — Matriz ESRS (289 × 11)

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
| E1   | Climate Change | 0.429 | 0.479 | **0.599** | +0.170 |
| S1   | Own Workforce | 0.424 | 0.472 | **0.564** | +0.140 |
| ESRS2| Gen. Disclosures | 0.315 | 0.375 | **0.492** | +0.177 |
| G1   | Business Conduct | 0.295 | 0.337 | **0.404** | +0.109 |
| E5   | Circular Economy | 0.256 | 0.307 | **0.395** | +0.139 |
| S2   | Value Chain Workers | 0.211 | 0.247 | **0.334** | +0.123 |
| E3   | Water & Marine | 0.188 | 0.214 | **0.304** | +0.116 |
| S4   | Consumers | 0.181 | 0.199 | **0.280** | +0.099 |
| E4   | Biodiversity | 0.152 | 0.177 | **0.260** | +0.108 |
| S3   | Communities | 0.158 | 0.176 | **0.242** | +0.084 |
| E2   | Pollution | 0.106 | 0.130 | **0.212** | +0.106 |

**Conclusiones:**
- **Todas las categorías crecen** 2022→2024, con el salto mayor en 2023→2024, coherente
  con la inminencia de CSRD. Esto confirma la hipótesis de RQ4.
- **E1 y S1 son las categorías más cubiertas** (0.60 y 0.56 en 2024): clima y fuerza
  laboral son los temas con mayor tradición de reporte bajo NFRD y TCFD.
- **ESRS2 sube de 0.32 a 0.49**: la adopción del lenguaje de doble materialidad,
  gobernanza de sostenibilidad y marcos como ESRS/CSRD/GRI se acelera claramente.
- **E2 (Contaminación) sigue siendo la más baja** (0.21 en 2024). Esto es esperable:
  el reporte de contaminación requiere datos de medición muy específicos (NOx, SOx, VOCs,
  microplásticos) que solo tienen empresas industriales/manufactureras. Para una empresa
  de servicios financieros o tecnología, E2 no es material → no reporta. El bajo valor
  no indica falta de cumplimiento sino un sesgo sectorial real.
- **S3 (Comunidades) baja relativa** (0.24 en 2024): comunidades locales e indígenas son
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

**Lo que SÍ es relevante** es el **delta 2022→2024** (+0.10 a +0.18 según categoría) y el
crecimiento del texto (+111% en tokens). Eso es la señal de cumplimiento emergente de CSRD.
Para el TFG, el argumento es: *antes de CSRD las empresas ya reportaban selectivamente;
con CSRD la cobertura léxica de todos los pilares ESRS sube de forma sistemática.*

---

## 3. `5a_cobertura_esrs_año.csv` + `5a_cobertura_esrs_año.png`

**Qué mide:** media de cobertura por categoría ESRS y año, en formato pivotado (para el gráfico).

**Para el TFG:** este gráfico de líneas es directamente citable como figura en el capítulo
de resultados de RQ4. Muestra que el perfil de cobertura ESRS cambia entre regímenes normativos.

---

## 4. `5a_heatmap_esrs.png`

**Qué mide:** cobertura media 2022-2024 por empresa (filas) y categoría ESRS (columnas).
Ordenado de mayor a menor cobertura total (empresas arriba = más comprehensivas).

**Para el TFG:** permite identificar outliers visualmente:
- Empresas con alta cobertura en todas las categorías (reporters líderes)
- Empresas con cobertura concentrada en 1-2 categorías (reporters selectivos)
- Filas casi blancas = `densidad_baja` (secciones parciales, ver análisis de sensibilidad)

---

## 5. `5a_tfidf_sus.csv` + `5a_tfidf_mr.csv` + `5a_tfidf_top_{sus,mr}.png`

**Qué mide:** los 20 términos con mayor TF-IDF medio en cada sección. TF-IDF pondera
frecuencia del término en el documento contra su prevalencia en el corpus completo.

**Lectura de los resultados:**

Los términos más altos en `sus` son: *sustainability, report, statement, financial,
annual, governance, esg, social*. En `mr`: *report, annual, financial, statement,
consolidated, registration, governance, board*.

**Nota importante:** cuando se aplica TF-IDF a nivel de corpus completo (media de scores),
los términos con score más alto tienden a ser los que aparecen en *muchos* documentos pero
no en todos. Por eso dominan palabras genéricas del contexto de reporting.
Este resultado es esperable y correcto: confirma que el corpus es coherente y que
los informes comparten un vocabulario de reporting corporativo uniforme.

**Lo que aporta para el TFG:**
- Confirma que `sus` y `mr` tienen vocabularios parcialmente solapados pero con diferencias
  clave: `esg`, `social`, `sustainability` son más prominentes en `sus`; `registration`,
  `universal` (URD francés), `consolidated` en `mr`.
- Para discriminación inter-empresa e inter-año, el TF-IDF por grupo (5B/5C) será más
  informativo que el agregado global.

---

## 6. `5a_ngrams_top.csv`

**Qué mide:** los 15 bi/trigramas con mayor TF-IDF medio por sección y año.

**Hallazgos destacables:**

| Sección | Año | N-gramas relevantes |
|---------|-----|---------------------|
| sus | 2022 | *financial statement, non financial, annual report, human right* |
| sus | 2023 | *non financial, sustainability report, sustainability statement, non financial information* |
| sus | 2024 | **sustainability statement, corporate governance, general information, risk management** |
| mr  | 2022-24 | *annual report, financial statement, non financial, registration document* |

**Conclusión:** El bigrama *"sustainability statement"* escala de irrelevante en 2022 a
**primer lugar en 2024** (TF-IDF 0.086), lo que refleja directamente la adopción del
lenguaje CSRD ("Non-Financial Statement" → "Sustainability Statement"). Esta es una de
las señales lingüísticas más claras de la transición NFRD→CSRD.

---

## 7. Análisis de sensibilidad (`densidad_baja`)

Excluyendo las 16 filas `densidad_baja` (secciones parciales), la cobertura media
sube 2-5 puntos porcentuales uniformemente. El efecto es real pero pequeño, lo que
confirma la Decisión 019: incluirlas en el análisis principal con nota de limitación.

| Confianza | n | E1 | S1 | ESRS2 |
|-----------|---|----|----|-------|
| alta | 115 | 0.573 | 0.583 | 0.462 |
| densidad | 143 | 0.505 | 0.458 | 0.382 |
| media | 8 | 0.179 | 0.244 | 0.167 |
| **densidad_baja** | **16** | **0.124** | **0.148** | **0.102** |
| aceptado_sin_fin. | 7 | 0.541 | 0.555 | 0.468 |

El contraste `alta` vs `densidad_baja` (E1: 0.57 vs 0.12) confirma que las
16 filas son secciones parciales, no informes completos.

---

## Resumen para el TFG

| Hallazgo | Relevancia |
|----------|-----------|
| Sus 10.9k→23.1k tokens (2022→2024) | Evidencia directa RQ4: expansión reporting CSRD |
| `sus` crece; `mr` estable | El cambio es específico de sostenibilidad, no del informe |
| E1+S1 = temas más cubiertos | Coherente con tradición TCFD/GRI pre-CSRD |
| E2+S3 = temas menos cubiertos | Efecto sectorial + doble materialidad, no incumplimiento |
| Todas las categorías +10-18pp en 2 años | Señal de adopción CSRD sistemática |
| "sustainability statement" → top bigrama 2024 | Cambio léxico NFRD→CSRD capturado |
