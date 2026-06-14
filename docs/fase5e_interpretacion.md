# Fase 5E — Interpretación de resultados

> **Corpus ampliado — 196 empresas / 586 documentos `sus` (Decisión 036).**
> Re-ejecutado desde cero. La metodología (Kruskal-Wallis RQ2, test pareado
> RQ4, regresiones OLS-HC3 RQ3) no cambia respecto a la versión original (97
> empresas / 289 docs, Decisión 026); solo los números, que **confirman y en
> varios casos refuerzan** los hallazgos previos.

`scripts/nlp/fase5e_stats.py` (Decisión 026/036). Panel: 586 documentos `sus`
(`results/tables/5e_panel.csv`) = `5d_gwindex.csv` (GW_index, tono, especificidad,
sentimiento climático) + `n_tokens` (`corpus.parquet`) + sector/país/financieros
(`empresas_muestra.csv`).

---

## 1. Construcción del panel

`5e_panel.csv`: **586 filas** × columnas de `5d_gwindex.csv` + `n_tokens` + `supersector`,
`pais`, `region`, `capitalización`, `log_cap`, `ROA`, `ROE`, `deuda_equity`,
`total_assets`. Sin NaN en sector/país (586/586); **9 filas** (FY2022, empresas con año
fiscal no-diciembre — Dec.006/028) sin `ROA`/`deuda_equity`, excluidas de las regresiones
(n=577).

`region` agrupa los **17 países** (ahora incluye Portugal, Luxemburgo e Israel tras la
ampliación, Decisión 036) en **5 zonas** para evitar sobreajuste en las regresiones:
**Nórdicos** (Suecia, Noruega, Dinamarca, Finlandia, n=81), **Centro** (Francia, Alemania,
Suiza, Austria, Bélgica, Países Bajos, Luxemburgo, n=308), **Sur** (España, Italia,
Portugal, n=98), **UK&Irlanda** (Reino Unido, Irlanda, n=96), **Otros** (Israel, n=3).
Se reportan ambos niveles de análisis: Kruskal-Wallis por país (17 grupos, descriptivo)
y `region` como control en las regresiones.

⚠️ **Otros** (Israel, n=3) es un grupo muy pequeño con un valor de `GW_index` extremo
(mediana 3.01, ver §2) — su coeficiente en las regresiones (§4) tiene error estándar muy
grande y debe leerse como anecdótico, no representativo.

---

## 2. RQ2 — Diferencias por sector y país (`5e_gwindex_supersector.png`, `5e_gwindex_region.png`)

Kruskal-Wallis (no paramétrico, apropiado para distribuciones no normales):

| Variable | ~ supersector | ~ país |
|---|---|---|
| `GW_index` | H=57.39, **p<0.0001**, η²=0.100 (n=577) | H=85.26, **p<0.0001**, η²=0.148 (n=577) |
| `finbert_tone` | H=36.45, **p<0.0001**, η²=0.062 (n=586) | H=62.13, **p<0.0001**, η²=0.106 (n=586) |
| `climate_specificity_spec` | H=66.29, **p<0.0001**, η²=0.115 (n=577) | H=44.51, **p<0.001**, η²=0.077 (n=577) |

Todos los tests son significativos al 0.1% (a diferencia de la muestra original, donde
`finbert_tone ~ supersector` era solo marginal, p=0.046) — con el doble de empresas, las
diferencias por sector y país se confirman con mucha mayor solidez.

**Por sector (mediana, 586 docs):**

| Sector | GW_index | finbert_tone | climate_specificity_spec |
|---|---|---|---|
| **Financials** | **+1.380** | 0.163 | 0.197 |
| **Technology** | **+1.184** | 0.156 | 0.189 |
| Consumer Staples | +0.199 | 0.169 | 0.272 |
| Health Care | −0.033 | 0.182 | 0.241 |
| Consumer Discretionary | −0.047 | 0.192 | 0.270 |
| Communication Services | −0.233 | 0.117 | 0.263 |
| Industrials | −0.236 | 0.166 | 0.258 |
| Energy | −0.314 | 0.105 | 0.277 |
| Basic Materials | −0.444 | 0.143 | 0.310 |
| Real Estate | −0.515 | 0.115 | 0.281 |
| **Utilities** | **−1.616** | 0.155 | 0.292 |

- `GW_index` más alto: **Financials** (1.38), **Technology** (1.18) — confirma el patrón
  original. Más bajo: **Utilities** (−1.62), **Real Estate** (−0.52), **Basic Materials**
  (−0.44).
- `climate_specificity_spec` más alto: **Basic Materials** (0.310), Utilities (0.292). Más
  bajo: **Technology** (0.189), **Financials** (0.197).
- Patrón confirmado: los sectores con mayor `GW_index` (Tech, Financials) son precisamente
  los de **menor especificidad climática** — consistente con la lógica del índice (su
  reporting climático es más cualitativo/genérico, ya sea porque su huella climática
  directa es menor o porque su materialidad climática es predominantemente financiera/
  transicional, no operativa).

**Por país/región (mediana, 586 docs):**

| Región | GW_index | finbert_tone | climate_specificity_spec |
|---|---|---|---|
| **Otros** (Israel, n=3) | **+3.007** | −0.283 | 0.061 |
| **UK&Irlanda** | +0.651 | 0.220 | 0.258 |
| Nórdicos | +0.021 | 0.115 | 0.286 |
| Centro | −0.116 | 0.149 | 0.250 |
| **Sur** | **−0.921** | 0.147 | 0.225 |

- `GW_index` más alto por país: **Suiza** (0.78), **Austria** (0.75), **Noruega/Reino
  Unido** (0.68). Más bajo: **Portugal** (−3.39), **Francia** (−1.30), **Italia** (−1.01).
  Portugal (n=2: Galp Energia, Jerónimo Martins, empresas nuevas de la ampliación) entra
  con un GW_index muy bajo, arrastrando la mediana de "Sur" muy por debajo de la de Centro.
- Confirma el patrón original: **UK&Irlanda y Nórdicos > Centro > Sur** en GW_index —
  coherente con la regresión (§4): Centro es la referencia, y Nórdicos/UK&Irlanda tienen
  GW_index significativamente mayor.
- ⚠️ Limitación persistente: varios de los 17 países tienen pocas empresas (Israel=1,
  Luxemburgo=1, Portugal=2, Austria=2-3) — el test por país sigue siendo
  descriptivo/exploratorio. Por eso se usa `region` (5 grupos) en las regresiones.

---

## 3. RQ4 — Test pareado 2022 vs 2024 (`5e_pareado_2022_2024.png`)

**194 empresas comunes** presentes en ambos años (NFRD 2022 vs CSRD 2024) — el doble que en
la muestra original (95):

| Variable | n | media 2022 | media 2024 | Δ | t-test p | Wilcoxon p |
|---|---|---|---|---|---|---|
| `GW_index` | 190 | −0.208 | +0.339 | **+0.547** | **0.0092** | **0.0051** |
| `finbert_tone` | 194 | 0.1885 | 0.1422 | **−0.0463** | **<0.0001** | **<0.0001** |
| `climate_specificity_spec` | 190 | 0.263 | 0.244 | −0.0188 | 0.113 | 0.126 |
| `climate_sentiment_risk` | 190 | 0.1106 | 0.1651 | **+0.0545** | **<0.0001** | **<0.0001** |
| `climate_sentiment_opportunity` | 190 | 0.2069 | 0.1604 | **−0.0465** | **<0.001** | **<0.0001** |
| `n_tokens` (sus) | 194 | 11.208 | 20.603 | **+9.395** | **<0.0001** | **<0.0001** |

Esto es la **confirmación inferencial formal**, ahora sobre el doble de empresas, de los
hallazgos descriptivos de 5A (Dec.021/036), 5C (Dec.024/036) y 5D (Dec.025/036): el
reporting de sostenibilidad bajo CSRD (2024) es significativamente más extenso, menos
optimista, con más discurso de riesgo climático y un GW_index significativamente más alto
que en 2022 (NFRD).

**Cambios respecto a la muestra original:**
- `GW_index`: el **t-test pasa a ser significativo** (p=0.0092, antes 0.055 marginal),
  además del Wilcoxon (p=0.0051, antes 0.021) — la mayor n da potencia para confirmar
  formalmente con ambos tests.
- `climate_specificity_spec`: sigue **sin alcanzar significación** (Wilcoxon p=0.126,
  antes p=0.086) — el deterioro de especificidad climática es consistente en dirección
  (−0.019 vs −0.020 original) pero sigue siendo la señal más sutil de las seis, y con más
  datos se confirma que probablemente no sea un efecto sistemático fuerte sino ruido +
  tendencia débil.
- Todas las demás variables (`finbert_tone`, `climate_sentiment_risk/opportunity`,
  `n_tokens`) mantienen significación **<0.0001**, con magnitudes de cambio muy similares
  a la muestra original.

---

## 4. RQ3 — Regresiones OLS (HC3 robust SE), n=577 (`5e_regresion*.csv`)

### Reg1: `GW_index ~ log(capitalización) + ROA + deuda_equity + supersector + año + región`

R²≈0.141. Categorías de referencia: sector=Basic Materials, año=2022, región=Centro.

| Predictor | Coef. | p | Interpretación |
|---|---|---|---|
| `Financials` | **+2.034** | **<0.001** | Mayor GW_index que Basic Materials |
| `Technology` | **+1.338** | **0.002** | Mayor GW_index que Basic Materials |
| `región Nórdicos` | **+0.612** | **0.022** | Mayor GW_index que Centro |
| `región UK&Irlanda` | **+0.751** | **0.003** | Mayor GW_index que Centro |
| `región Otros` (Israel, n=3) | +3.77 | 0.378 | n.s. — error estándar enorme (n=3) |
| `año 2024` | **+0.510** | **0.030** | Mayor GW_index en 2024 vs 2022 |
| `año 2023` | −0.010 | 0.969 | n.s. |
| `Real Estate` | −0.332 | 0.461 | n.s. (en la muestra original era significativo y negativo) |
| `log_cap`, `ROA`, `deuda_equity` | n.s. | — | Sin efecto detectable |

**Diferencias clave respecto a la muestra original:**
- **`log_cap` deja de ser significativo** (p=0.72; antes −0.268, p=0.024). El efecto
  "empresas más grandes → menor GW_index" **no se confirma** con la muestra ampliada —
  parece haber sido en parte un artefacto de la muestra de 97 empresas.
- **`año 2024` ahora SÍ es significativo** (+0.510, p=0.030; antes +0.60, p=0.104,
  n.s.). Con el doble de empresas, el efecto temporal bruto de RQ4 **sobrevive** al
  control por sector/tamaño/región — a diferencia de la conclusión original ("el efecto es
  composicional"), ahora hay evidencia de un **efecto CSRD genuino** sobre el GW_index,
  independiente de la composición sectorial/geográfica de la muestra.
- Los efectos sectoriales (Financials/Technology con mayor GW_index) y regionales
  (Nórdicos/UK&Irlanda > Centro) **se mantienen** y siguen siendo los predictores más
  fuertes (coeficientes >1 con p<0.01-0.001).

### Reg2: `finbert_tone ~ climate_specificity_spec + log(capitalización) + ROA + supersector + año + región`

R²≈0.156.

| Predictor | Coef. | p | Interpretación |
|---|---|---|---|
| `climate_specificity_spec` | **+0.194** | **0.003** | **Más especificidad → tono MÁS positivo** |
| `año 2024` | **−0.0476** | **<0.001** | Caída de tono robusta, independiente de especificidad/sector/tamaño |
| `región UK&Irlanda` | **+0.0635** | **<0.001** | Mayor tono que Centro |
| `Real Estate` | **−0.0692** | **<0.001** | Menor tono que Basic Materials |
| `Energy` | **−0.0746** | **0.021** | Menor tono que Basic Materials |
| `Communication Services` | **−0.0464** | **0.028** | Menor tono que Basic Materials |
| `Utilities` | −0.0478 | 0.077 | Marginal, menor tono que Basic Materials |
| `log_cap`, `ROA`, `año 2023`, `región Otros` | n.s. | — | Sin efecto detectable |

**Hallazgo clave (confirmado a 196 empresas):** la relación `especificidad → tono` sigue
siendo **positiva** (+0.194, p=0.003 — prácticamente idéntico a +0.220, p=0.003 en la
muestra original). Esto **sigue sin apoyar** la hipótesis simple "tono optimista ↔ menos
especificidad" como patrón cross-seccional: las empresas que hablan de forma más específica
sobre clima tienden también a tener un tono financiero general más positivo — posiblemente
porque la especificidad suele acompañar a comunicación de logros/avances concretos. El
**efecto temporal** (`año 2024`, p<0.001) confirma de nuevo que el tono cae 2022→2024 de
forma robusta, independientemente de cuánto hable la empresa de clima de forma específica.
Real Estate vuelve a tener el menor tono entre sectores (confirmado), y ahora también
Energy y Communication Services emergen como sectores con tono significativamente menor.

### VIF

Máximo VIF ≈ 2.6-3 en ambas regresiones (umbral de preocupación habitual >5-10) → sin
problema relevante de multicolinealidad entre `log_cap`, financieros, sector, año y región,
igual que en la muestra original.

⚠️ **Nota técnica heredada (Dec.026)**: el cálculo de VIF requiere mantener el intercepto
en la matriz de diseño (`variance_inflation_factor` regresa cada predictor sobre el resto
**incluyendo la constante**). Calcularlo sin intercepto infla artificialmente el VIF de
variables no centradas en 0 como `log_cap`.

---

## 5. Síntesis para el TFG

| Elemento | Dónde | Capítulo TFG | RQ |
|---|---|---|---|
| KW GW_index/tono/especificidad por sector y país (todos p<0.001 con 586 docs) | `5e_kruskal_*.csv` + `5e_gwindex_*.png` | Resultados | RQ2 |
| Test pareado 2022↔2024, 194 empresas (6 variables, 5/6 significativas) | `5e_pareado_2022_2024.csv/.png` | Resultados | RQ4 |
| Reg1: GW_index ~ tamaño/sector/región/año (R²≈0.141; año 2024 ahora significativo) | `5e_regresion1_gwindex.csv` | Resultados | RQ3, RQ4 |
| Reg2: tono ~ especificidad/sector/región/año (R²≈0.156; especificidad→tono positivo, confirmado) | `5e_regresion2_tono.csv` | Resultados | RQ3 |
| Discusión: relación especificidad-tono positiva (no la hipótesis simple), confirmada a 196 empresas | §4 | Discusión | RQ3 |
| Discusión: efecto año 2024 ahora significativo en GW_index tras controles — evidencia de efecto CSRD genuino | §4 | Discusión | RQ3, RQ4 |
| Discusión: efecto tamaño (`log_cap`) sobre GW_index NO se replica con 196 empresas | §4 | Discusión / Limitaciones | RQ3 |

---

## 6. Resumen ejecutivo

- **RQ2**: el GW_index, el tono y la especificidad climática difieren significativamente
  por sector (Financials/Technology = más cheap talk/menos específicos; Utilities/Real
  Estate = lo contrario) y por país/región (Sur y Centro tienen GW_index más bajo que
  Nórdicos/UK&Irlanda), **todos los tests ahora p<0.001** (vs uno marginal en la muestra
  original).
- **RQ3**: la hipótesis "más optimismo ↔ menos especificidad" sigue **sin confirmarse** en
  corte transversal — la relación especificidad→tono es positiva (+0.194, p=0.003,
  prácticamente idéntico a la muestra original). Los efectos sectoriales/regionales sobre
  GW_index se mantienen robustos. **Novedad**: el efecto de tamaño empresarial
  (`log_cap`) sobre GW_index, significativo en la muestra de 97, **no se replica** con 196
  — se reinterpreta como hallazgo no robusto de la muestra pequeña.
- **RQ4**: confirmación inferencial formal de la transición NFRD→CSRD en 5/6 variables
  clave de 5A/5C/5D (especificidad climática sigue siendo la señal marginal, ahora p=0.126).
  **Novedad importante**: con 194 empresas, el efecto `año 2024` sobre el GW_index
  **se mantiene significativo tras controlar por sector/tamaño/región** (p=0.030, antes
  n.s. con p=0.104) — evidencia más sólida de un **efecto CSRD genuino**, no meramente
  composicional, sobre el "cheap talk" textual.
- Con esto se completa la re-ejecución del bloque analítico de Fase 5 (5A-5E) sobre el
  corpus ampliado (196 empresas / 586 docs, Decisión 036). Siguiente: Fase 6 (regenerar
  dashboard sobre 586 docs) y Fase 7 (redacción del TFG).
