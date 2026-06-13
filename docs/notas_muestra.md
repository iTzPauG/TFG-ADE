# Notas sobre la Muestra — Fase 2

## Muestra seleccionada

- **Universo:** STOXX Europe 600 (`stoxx600_componentes.csv`: 534 filas listadas en
  Wikipedia, 473 nombres únicos tras depurar duplicados de ticker)
- **Muestra:** **196 empresas** mediante muestreo estratificado por sector ICB con cap
  geográfico (ampliación de la muestra original de 97; Decisiones 002, 027, 028, 030)
- **Semilla aleatoria:** `random_state=42` (reproducibilidad)
- **Años:** 2022, 2023 y 2024 (transición NFRD → CSRD)
- **Panel:** 588 filas (196 empresas × 3 años) en `data/external/empresas_muestra.csv`
- **Scripts:** `scripts/fase2_muestra.py` (muestra original) +
  `scripts/fase2_ampliacion.py` y `scripts/fase2_correcciones_ampliacion.py` (ampliación)

## Justificación del diseño muestral

**Por qué muestreo estratificado:**
El STOXX 600 está muy concentrado sectorialmente (Financial Services + Industrials
representan >40%). Un muestreo aleatorio simple daría representación excesiva a estos
sectores y dejaría sin representación a sectores pequeños pero relevantes para el análisis
de sostenibilidad (Real Estate, Utilities). La estratificación garantiza que cada
supersector ICB aporte al análisis comparativo (RQ2).

**Por qué aleatorio dentro del estrato (no top por capitalización):**
La selección por capitalización sesga hacia mega-caps con mayor capacidad de reporting
(más recursos, más presión mediática). Para estudiar variación en calidad de disclosure
necesitamos dispersión dentro de cada sector, no solo los líderes. El muestreo aleatorio
dentro del estrato es metodológicamente más sólido para generalizar al sector.

**Por qué 196 empresas (ampliación de 97 a 196):**
La muestra original (Decisión 002) fijó una cuota de 5 empresas por sector ICB (objetivo
100, resultado 97 tras el cap geográfico). La ampliación (Decisión 027) recalculó la cuota
a **10 empresas por sector ICB** (objetivo 200), conservando intactas las 97 empresas
originales (mismos `id_empresa`) y añadiendo 99 nuevas (E098–E196). El resultado fue de
**196 empresas** (déficit de 4 sobre el objetivo de 200 por falta de candidatas en algunos
sectores pequeños tras el cap). Con 196 empresas × 3 años = 588 observaciones, el panel
ofrece potencia suficiente para los tests inferenciales por sector y región (RQ2, RQ3) y
para el contraste pareado NFRD→CSRD (RQ4).

**Por qué 2022, 2023 y 2024:**
- 2022: último ejercicio mayoritariamente bajo NFRD (baseline pre-CSRD)
- 2023: informes bajo expectativas CSRD crecientes (publicados en 2024)
- 2024: **primer ejercicio de reporte obligatorio bajo CSRD** para grandes empresas de
  interés público (PIEs >500 empleados), publicado en primavera de 2025
- La comparativa 2022→2024 permite responder RQ4 sobre la evolución del reporting

**Cap geográfico (≤15 original; ≤30 en la ampliación):**
UK representaba el 32% estructural del STOXX 600. El cap corrige este sesgo sin alterar la
lógica de estratificación sectorial. En la ampliación, el cap se recalculó a 30 (15% de
200, misma proporción que el cap=15/100 original) y se aplicó **solo sobre las 99 empresas
nuevas**, nunca sobre las 97 originales (Decisión 027).

## Distribución por supersector (196 empresas)

| Supersector | Empresas |
|-------------|----------|
| Consumer Discretionary | 39 |
| Financials | 33 |
| Industrials | 20 |
| Basic Materials | 18 |
| Communication Services | 18 |
| Consumer Staples | 17 |
| Technology | 11 |
| Energy | 10 |
| Health Care | 10 |
| Real Estate | 10 |
| Utilities | 10 |

*Los sectores ICB de Wikipedia (ej. "Industrial Goods and Services", "Construction and
Materials") se agrupan en 11 supersectores estándar mediante el mapeo SUPERSECTORES en
`scripts/fase2_muestra.py`. La estratificación se realizó sobre los **20 sectores ICB**, no
sobre los supersectores.*

## Distribución por país (196 empresas)

| País | Empresas |
|------|----------|
| United Kingdom | 30 |
| Germany | 29 |
| France | 28 |
| Switzerland | 19 |
| Spain | 17 |
| Netherlands | 15 |
| Italy | 14 |
| Sweden | 11 |
| Norway | 8 |
| Belgium | 7 |
| Finland | 5 |
| Austria | 4 |
| Denmark | 3 |
| Ireland | 2 |
| Portugal | 2 |
| Luxembourg | 1 |
| Israel | 1 |

## Duplicados detectados y corregidos en la ampliación

Durante la integración se detectaron empresas que figuraban dos veces en
`stoxx600_componentes.csv` (mismo emisor con dos tickers de Wikipedia) y habían caído
duplicadas en la muestra. Se sustituyeron conservando el sector:

- **Decisión 028** — Delivery Hero (E062 `DHER` / E157 `DASH`, mismo ISIN): **E157
  sustituido por Inditex** (ITX, España, Retail).
- **Decisión 030** — Vinci (E112=E018), Bouygues (E116=E019), Castellum (E185=E061) y
  Gruppo Campari (E194=E038, cambio de nombre): sustituidos por **Heidelberg Materials**
  (E112), **Wienerberger** (E116), **LEG Immobilien** (E185) y **Lindt & Sprüngli** (E194).

196 empresas son entidades únicas confirmadas (sin duplicados por ISIN ni `ticker_yf`).

## Datos financieros (yfinance)

- **Cobertura capitalización:** 196/196 empresas (588/588 filas)
- **Cobertura ingresos / ROA / ROE / deuda-equity / total activos:** 579/588 filas
- **Cobertura EBITDA:** 573/588 filas; el EBITDA de entidades financieras se reconstruye
  por **proxy en cascada** (Decisión 007)
- **Datos disponibles vía yfinance:** ROA, ROE, deuda/equity, ingresos, EBITDA, beneficio
  neto, total de activos, capitalización (año a año, 2022–2024)

### Huecos financieros FY2022 (9 filas)

Las 9 filas sin ratios corresponden todas al **FY2022** de empresas con **año fiscal
no-diciembre** (Decisión 006), donde yfinance no cubre el ejercicio completo: Richemont,
3i, JD Sports, Vodafone e Inditex (Decisión 028), entre otras. Se excluyen de las
regresiones que usan financieros (n=579 en lugar de 588).

### Correcciones de tickers

`scripts/fase2_muestra.py` aplica overrides de tickers donde el ticker de Wikipedia no
funciona en yfinance (clase B con espacio → guión, ADR con mejor cobertura, etc.). La
ampliación añadió **22 overrides nuevos** (Decisión 027), p. ej. Michelin `MICP→ML.PA`,
Sanofi `SNY→SAN.PA`, Novartis `"NOV N"→NOVN.SW`, ArcelorMittal `MT→MT.AS`, UniCredit
`UC→UCG.MI`. El listado completo está en el diccionario `TICKER_OVERRIDES` del script.

## Corpus NLP resultante (Fase 4)

De las 588 filas, **586 documentos** entran en el corpus de análisis textual: se descartan
**DIA 2022** y **Nemetschek 2022** por carecer de contenido ESG analizable (Decisión 010).
El corpus final (`data/processed/corpus.parquet`) tiene 1.172 filas = 586 documentos × 2
secciones (`mr`, `sus`).

## Variables proxy de greenwashing (Fase 5)

Se adopta la **Opción A** (Decisión 001): el greenwashing se operacionaliza mediante
variables textuales internas, **sin scores ESG de terceros**. Las métricas se calculan
sobre la sección `sus` (Decisión 019).

| Variable | Tipo | Fuente | Descripción |
|----------|------|--------|-------------|
| `finbert_tone` | float | FinBERT | % frases positivas − % negativas por documento |
| `climate_specificity_spec` | float 0–1 | ClimateBERT-specificity | % de frases climáticas específicas (con cifras/metas) |
| `hedging_ratio` | float | Loughran-McDonald | uncertainty + weak modal / total |
| `ratio_cuantitativo` | float 0–1 | regex | % frases con cifras concretas |
| `ratio_futuro_sin_cifra` | float 0–1 | regex | % frases prospectivas sin cuantificar (promesa vaga) |
| `cobertura_ESRS_*` | float 0–1 | diccionario ESRS | densidad de keywords por categoría ESRS |
| `GW_index` | float | combinado | índice de greenwashing textual (z-score compuesto) |
| `topic_dominante` | str | LDA/BERTopic | topic más prevalente del documento |

**Referencia:** Bingler et al. (2022) — *Cheap talk and cherry-picking* — usa
ClimateBERT-specificity.

---

## Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `data/external/stoxx600_componentes.csv` | 534 filas del índice (473 nombres únicos) con sector ICB y país |
| `data/external/muestra_seleccionada.csv` | 196 empresas seleccionadas con tickers y metadatos |
| `data/external/isins_wikidata.csv` | ISINs obtenidos vía Wikidata SPARQL (propiedad P946) |
| `data/external/yfinance_datos.csv` | Datos financieros de yfinance por empresa y año |
| `data/external/empresas_muestra.csv` | Dataset maestro (588 filas: 196 empresas × 3 años) |
| `data/external/tracking_descargas.csv` | Hoja de seguimiento de la recolección de informes (Fase 3) |
