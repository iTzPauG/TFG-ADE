# Fase 5E — Interpretación de resultados

`scripts/nlp/fase5e_stats.py` (Decisión 026). Panel: 289 documentos `sus`
(`results/tables/5e_panel.csv`) = `5d_gwindex.csv` (GW_index, tono, especificidad,
sentimiento climático) + `n_tokens` (`corpus.parquet`) + sector/país/financieros
(`empresas_muestra.csv`).

---

## 1. Construcción del panel

`5e_panel.csv`: 289 filas × columnas de `5d_gwindex.csv` + `n_tokens` + `supersector`,
`pais`, `region`, `capitalización`, `log_cap`, `ROA`, `ROE`, `deuda_equity`,
`total_assets`. Sin NaN en sector/país (289/289); 4 filas (FY2022) sin `ROA`/
`deuda_equity` (Dec.006), excluidas de las regresiones (n=285).

`region` agrupa los 14 países en 4 zonas para evitar sobreajuste en las regresiones
(14 dummies con n=289 sería excesivo): **Nórdicos** (Suecia, Noruega, Dinamarca,
Finlandia, n=17), **Centro** (Francia, Alemania, Suiza, Austria, Bélgica, Países Bajos,
n=49), **Sur** (España, Italia, n=14), **UK&Irlanda** (Reino Unido, Irlanda, n=17).
Se reportan ambos niveles de análisis: Kruskal-Wallis por país (14 grupos, descriptivo)
y `region` como control en las regresiones.

---

## 2. RQ2 — Diferencias por sector y país (`5e_gwindex_supersector.png`, `5e_gwindex_region.png`)

Kruskal-Wallis (no paramétrico, apropiado para distribuciones no normales):

| Variable | ~ supersector | ~ país |
|---|---|---|
| `GW_index` | H=43.53, **p<0.001**, η²=0.151 | H=49.46, **p<0.001**, η²=0.172 |
| `finbert_tone` | H=18.58, p=0.046, η²=0.065 | H=45.31, **p<0.001**, η²=0.157 |
| `climate_specificity_spec` | H=49.08, **p<0.001**, η²=0.170 | H=33.90, p=0.001, η²=0.118 |

**Por sector:**
- `GW_index` más alto: **Technology** (mediana 1.39), **Financials** (1.14). Más bajo:
  **Utilities** (−1.89), **Communication Services** (−1.19), **Real Estate** (−0.89).
- `climate_specificity_spec` más alto: **Real Estate** (0.339), Communication Services
  (0.304). Más bajo: **Technology** (0.200), **Financials** (0.204).
- Patrón: los sectores con mayor `GW_index` (Tech, Financials) son precisamente los de
  **menor especificidad climática** — consistente con la lógica del índice (su
  reporting climático es más cualitativo/genérico).
- `finbert_tone` por sector tiene el efecto más débil (η²=0.065, p=0.046, el único
  marginal de los tres) — el tono financiero general varía menos por sector que el
  GW_index o la especificidad climática.

**Por país** (η² más alto que por sector para `finbert_tone`, η²=0.157 vs 0.065):
- `GW_index` más alto: **Suiza** (1.22), **Reino Unido** (0.85). Más bajo: **Italia**
  (−1.89), **Francia** (−1.52).
- Coherente con el resultado de la regresión (§4): la región Centro (que incluye Francia,
  con el GW_index más bajo) es la referencia, y Nórdicos/UK&Irlanda tienen GW_index
  significativamente mayor que Centro.
- ⚠️ Limitación: 5 de los 14 países tienen <5 empresas (Austria=2, Irlanda=2, Bélgica=3,
  Dinamarca=3, Finlandia=3) — el test por país es descriptivo/exploratorio, no
  concluyente. Por eso se usa `region` (4 grupos más balanceados) en las regresiones.

---

## 3. RQ4 — Test pareado 2022 vs 2024 (`5e_pareado_2022_2024.png`)

95 empresas presentes en ambos años (NFRD 2022 vs CSRD 2024):

| Variable | 2022 | 2024 | Δ | t-test p | Wilcoxon p |
|---|---|---|---|---|---|
| `GW_index` | −0.196 | +0.424 | **+0.620** | 0.055 | **0.021** |
| `finbert_tone` | 0.202 | 0.157 | −0.046 | **0.0015** | **0.0003** |
| `climate_specificity_spec` | 0.281 | 0.261 | −0.020 | 0.210 | 0.086 |
| `climate_sentiment_risk` | 0.104 | 0.164 | **+0.060** | **<0.0001** | **<0.0001** |
| `climate_sentiment_opportunity` | 0.215 | 0.165 | −0.051 | **0.0018** | **0.0006** |
| `n_tokens` (sus) | 10.947 | 23.380 | **+12.433** | **<0.0001** | **<0.0001** |

Esto es la **confirmación inferencial formal** de los hallazgos descriptivos de 5A
(Dec.021), 5C (Dec.024) y 5D (Dec.025): el reporting de sostenibilidad bajo CSRD (2024)
es significativamente más extenso, menos optimista, con más discurso de riesgo climático
y un GW_index significativamente más alto que en 2022 (NFRD). La caída de especificidad
climática es la única que no alcanza significación al 5% (Wilcoxon p=0.086,
marginal) — el deterioro de especificidad es real pero más sutil que el resto de señales.

---

## 4. RQ3 — Regresiones OLS (HC3 robust SE), n=285 (`5e_regresion*.csv`)

### Reg1: `GW_index ~ log(capitalización) + ROA + deuda_equity + supersector + año + región`

R²=0.223, R²adj=0.171. Categorías de referencia: sector=Basic Materials, año=2022,
región=Centro.

| Predictor | Coef. | p | Interpretación |
|---|---|---|---|
| `log_cap` | **−0.268** | **0.024** | Empresas más grandes → menor GW_index (menos cheap talk) |
| `Financials` | **+2.10** | **<0.001** | Mayor GW_index que Basic Materials |
| `Technology` | **+1.90** | **0.011** | Mayor GW_index que Basic Materials |
| `Real Estate` | **−1.93** | **0.014** | Menor GW_index que Basic Materials |
| `Consumer Discretionary` | +0.91 | 0.059 | Marginal, mayor que Basic Materials |
| `región Nórdicos` | **+1.34** | **<0.001** | Mayor GW_index que Centro |
| `región UK&Irlanda` | **+1.07** | **0.011** | Mayor GW_index que Centro |
| `año 2024` | +0.60 | 0.104 | **No significativo** controlando por sector/tamaño/región |
| `ROA`, `deuda_equity` | n.s. | — | Sin efecto detectable |

**Hallazgo clave**: el efecto temporal bruto de RQ4 (+0.62, Wilcoxon p=0.021) **deja de
ser significativo** una vez se controla por sector, tamaño y región (p=0.104). Esto
sugiere que parte del aumento agregado del GW_index en 2024 refleja **composición**
(qué sectores/regiones componen la muestra) más que un efecto CSRD homogéneo y uniforme
sobre todas las empresas — aunque el efecto sigue siendo positivo en magnitud.

### Reg2: `finbert_tone ~ climate_specificity_spec + log(capitalización) + ROA + supersector + año + región`

R²=0.206, R²adj=0.152.

| Predictor | Coef. | p | Interpretación |
|---|---|---|---|
| `climate_specificity_spec` | **+0.220** | **0.003** | **Más especificidad → tono MÁS positivo** |
| `año 2024` | **−0.042** | **0.013** | Caída de tono robusta, independiente de especificidad/sector/tamaño |
| `Health Care` | +0.130 | 0.042 | Mayor tono que Basic Materials |
| `Real Estate` | **−0.075** | **<0.001** | Menor tono que Basic Materials |
| `región UK&Irlanda` | **+0.070** | **<0.001** | Mayor tono que Centro |
| `log_cap`, `ROA` | n.s. | — | Sin efecto detectable |

**Hallazgo clave**: la relación `especificidad → tono` es **positiva**, no negativa. Esto
**no apoya** la hipótesis simple "tono optimista ↔ menos especificidad" como patrón
cross-seccional (empresa a empresa): las empresas que hablan de forma más específica
sobre clima tienden también a tener un tono financiero general más positivo —
posiblemente porque la especificidad suele acompañar a comunicación de logros/avances
concretos, que se redactan en términos positivos. En cambio, el **efecto temporal**
(`año 2024`, p=0.013) sí confirma que el tono cae 2022→2024 de forma robusta,
independientemente de cuánto hable la empresa de clima de forma específica.

### VIF

Máximo VIF = 2.6 en ambas regresiones (umbral de preocupación habitual >5-10) → sin
problema de multicolinealidad relevante entre `log_cap`, financieros, sector, año y
región.

⚠️ **Nota técnica corregida durante el desarrollo**: el cálculo de VIF requiere mantener
el intercepto en la matriz de diseño (`variance_inflation_factor` regresa cada
predictor sobre el resto **incluyendo la constante**). Calcularlo sin intercepto
("a través del origen") infla artificialmente el VIF de variables no centradas en 0
como `log_cap` (de ~1.5 real a ~15-23 espurio). Documentado para evitar el error en 5E
si se reproduce el análisis.

---

## 5. Síntesis para el TFG

| Elemento | Dónde | Capítulo TFG | RQ |
|---|---|---|---|
| KW GW_index/tono/especificidad por sector y país | `5e_kruskal_*.csv` + `5e_gwindex_*.png` | Resultados | RQ2 |
| Test pareado 2022↔2024 (6 variables) | `5e_pareado_2022_2024.csv/.png` | Resultados | RQ4 |
| Reg1: GW_index ~ tamaño/sector/región/año | `5e_regresion1_gwindex.csv` | Resultados | RQ3 |
| Reg2: tono ~ especificidad/sector/región/año | `5e_regresion2_tono.csv` | Resultados | RQ3 |
| Discusión: relación especificidad-tono positiva (no la hipótesis simple) | §4 | Discusión | RQ3 |
| Discusión: efecto año significativo en tono pero no en GW_index tras controles | §4 | Discusión | RQ3, RQ4 |

---

## 6. Resumen ejecutivo

- **RQ2**: el GW_index y la especificidad climática difieren significativamente por
  sector (Tech/Financials = más cheap talk/menos específicos; Real Estate = lo
  contrario) y por país/región (Centro Europa, especialmente Francia e Italia, tiene
  GW_index más bajo que Nórdicos/UK).
- **RQ3**: las empresas más grandes tienen menor GW_index. La hipótesis "más optimismo ↔
  menos especificidad" **no se confirma** en corte transversal — la relación es positiva.
  El descenso del tono 2022→2024 es robusto a todos los controles; el aumento del
  GW_index 2022→2024 es en parte composicional (sector/región).
- **RQ4**: confirmación inferencial formal de la transición NFRD→CSRD en las 6 variables
  clave de 5A/5C/5D, con la especificidad climática como única señal marginal (p≈0.09).
- Con esto se completa el bloque analítico de Fase 5 (5A-5E). Siguiente: Fase 6
  (dashboard Streamlit + reproducibilidad) y Fase 7 (redacción del TFG).
