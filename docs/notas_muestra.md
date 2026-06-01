# Notas sobre la Muestra — Fase 2

## Muestra seleccionada

- **Universo:** STOXX Europe 600 (534 empresas listadas en Wikipedia, actualización marzo 2026)
- **Muestra:** 60 empresas mediante muestreo estratificado proporcional por supersector ICB
- **Semilla aleatoria:** `random_state=42` (reproducibilidad)
- **Años:** 2022 y 2023 (pre y post entrada en vigor CSRD)
- **Script:** `scripts/fase2_muestra.py`

## Justificación del diseño muestral

**Por qué muestreo estratificado:**  
El STOXX 600 está muy concentrado sectorialmente (Financial Services + Industrials representan >40%). Un muestreo aleatorio simple daría representación excesiva a estos sectores y dejaría sin representación a sectores pequeños pero relevantes para el análisis de sostenibilidad (Real Estate, Utilities). La estratificación garantiza que cada supersector ICB aporte al análisis comparativo (RQ2).

**Por qué aleatorio dentro del estrato (no top por capitalización):**  
La selección por capitalización sesga hacia mega-caps con mayor capacidad de reporting (más recursos, más presión mediática). Para estudiar variación en calidad de disclosure necesitamos dispersión dentro de cada sector, no solo los líderes. El muestreo aleatorio dentro del estrato es metodológicamente más sólido para generalizar al sector.

**Por qué 60 empresas:**  
60 × 2 años = 120 documentos. Con los métodos propuestos (LDA, BERTopic, FinBERT, ClimateBERT) este volumen permite análisis estadístico con suficiente potencia (n > 30 por grupo sectorial agregado) sin hacer el pipeline de extracción de PDFs inmanejable.

**Por qué 2022 y 2023:**  
- 2022: último año mayoritariamente bajo NFRD (baseline pre-CSRD)
- 2023: primeros informes bajo expectativas CSRD (publicados en 2024)
- La comparativa 2022→2023 permite responder RQ4 sobre evolución del reporting

## Distribución por supersector

| Supersector | Empresas |
|-------------|----------|
| Industrials | 13 |
| Financials | 10 |
| Consumer Discretionary | 10 |
| Communication Services | 5 |
| Health Care | 5 |
| Basic Materials | 4 |
| Utilities | 3 |
| Technology | 3 |
| Consumer Staples | 3 |
| Real Estate | 2 |
| Energy | 2 |

*Los sectores ICB de Wikipedia (ej. "Industrial Goods and Services", "Construction and Materials") se agrupan en supersectores estándar mediante el mapeo SUPERSECTORES en `scripts/fase2_muestra.py`.*

## Distribución por país

| País | Empresas |
|------|----------|
| United Kingdom | 21 |
| Netherlands | 7 |
| France | 6 |
| Switzerland | 6 |
| Germany | 5 |
| Sweden | 4 |
| Italy | 3 |
| Ireland | 2 |
| Norway | 2 |
| Spain | 2 |
| Finland | 1 |
| Denmark | 1 |

## Datos financieros (yfinance)

- **Cobertura capitalización:** 55/60 empresas (92%)
- **Cobertura ISIN:** 60/60 — completado con Wikidata SPARQL
- **Datos disponibles vía yfinance:** ROA, ROE, deuda/equity, ingresos, EBITDA, margen de beneficio

### Empresas sin datos en yfinance (5/60)

| Empresa | Ticker | Motivo | Acción recomendada |
|---------|--------|--------|--------------------|
| Smurfit Kappa | SKG | Fusionada en Smurfit WestRock (SW, NYSE) en 2024; SKG.IR retirado | Datos financieros históricos no disponibles en yfinance |
| Phoenix Group | PHNX | PHNX.L da 404 en yfinance (bug conocido); empresa activa en LSE | Datos financieros no disponibles en yfinance |
| Adevinta | ADH | Privatizada por consorcio PE en 2023; sin cotización activa | Datos financieros no disponibles en yfinance |
| Lumibird | LUMI | Micro-cap francesa sin cobertura en yfinance | Datos financieros no disponibles en yfinance |
| Swedish Match | SWMA | Adquirida por Philip Morris y retirada de bolsa en 2022 | Considerar sustitución en la muestra si se necesitan 2 años completos |

### Correcciones de tickers aplicadas

El script aplica 13 overrides de tickers donde el ticker de Wikipedia no funciona en yfinance:

| Ticker Wikipedia | Ticker yfinance | Motivo |
|-----------------|-----------------|--------|
| NOVO B | NOVO-B.CO | Clase B con espacio → guión |
| SKA B | SKA-B.ST | Clase B con espacio → guión |
| ERICb | ERIC-B.ST | Formato incorrecto → guión |
| BT.A | BT-A.L | Punto → guión |
| STMPA | STM | NYSE tiene mejor cobertura que Amsterdam |
| QIA | QGEN | NYSE tiene mejor cobertura que Amsterdam |
| STLAM | STLA | NYSE tiene mejor cobertura que Amsterdam |
| HMB | HNNMY | ADR americano (HMB.ST sin datos en yfinance) |
| ENGIE | ENGI.PA | ENGIE.PA da 404; ENGI.PA funciona |
| AKERBP | AKRBP.OL | AKERBP.OL da 404; AKRBP.OL funciona |
| INP | INVP.L | INP es ticker incorrecto; INVP es el correcto en LSE |
| TOM | TOM2.AS | TOM.AS sin datos; TOM2.AS funciona |
| FLTR | FLTR.L | FLTR.IR sin datos; FLTR.L (London) funciona |

## Variables proxy de greenwashing (Fase 5 → columnas futuras en empresas_muestra.csv)

Se adopta la **Opción A** (Decisión 001 en `docs/decisiones.md`): el greenwashing se operacionaliza mediante variables textuales internas.

Las siguientes columnas se añadirán al dataset maestro al ejecutar los scripts de Fase 5:

| Variable | Tipo | Fuente | Descripción |
|----------|------|--------|-------------|
| `tono_positivo` | float 0–1 | FinBERT | Media de score "positive" por documento |
| `tono_negativo` | float 0–1 | FinBERT | Media de score "negative" por documento |
| `especificidad` | float 0–1 | ClimateBERT-specificity | % de oraciones climáticas con compromisos concretos |
| `hedging_ratio` | float 0–1 | Loughran-McDonald | Modal/uncertainty words / total tokens |
| `ratio_cuantitativo` | float 0–1 | regex | % oraciones con cifras, %, años concretos |
| `ratio_futuro` | float 0–1 | spaCy POS | % verbos en futuro/condicional |
| `cobertura_ESRS_E` | float 0–1 | diccionario ESRS | Densidad de keywords ambientales (E1-E5) |
| `cobertura_ESRS_S` | float 0–1 | diccionario ESRS | Densidad de keywords sociales (S1-S4) |
| `cobertura_ESRS_G` | float 0–1 | diccionario ESRS | Densidad de keywords gobernanza (G1) |
| `GW_index` | float | combinado | Índice de greenwashing textual (z-score compuesto) |
| `n_tokens` | int | spaCy | Longitud del management report en tokens |
| `topic_dominante` | str | BERTopic | Topic más prevalente del documento |

**Referencia:** Bingler et al. (2022) — "Cheap talk and cherry-picking" — usa ClimateBERT-specificity.

---

## Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `data/external/stoxx600_componentes.csv` | 534 empresas del índice con sector ICB y país |
| `data/external/muestra_seleccionada.csv` | 60 empresas seleccionadas con tickers y metadatos |
| `data/external/isins_wikidata.csv` | ISINs obtenidos vía Wikidata SPARQL (59 automáticos + 6 correcciones manuales) |
| `data/external/yfinance_datos.csv` | Datos financieros de yfinance por empresa |
| `data/external/empresas_muestra.csv` | Dataset maestro (120 filas: 60 empresas × 2 años) |
| `data/external/tracking_descargas.csv` | Hoja de seguimiento para recolección de informes (Fase 3) |
