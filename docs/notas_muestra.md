# Notas sobre la Muestra — Fase 2

## Muestra seleccionada

- **Universo:** STOXX Europe 600 (534 empresas listadas en Wikipedia, actualización marzo 2026)
- **Muestra:** 60 empresas mediante muestreo estratificado proporcional por supersector ICB
- **Semilla aleatoria:** `random_state=42` (reproducibilidad)
- **Años:** 2022 y 2023 (pre y post entrada en vigor CSRD)
- **Script:** `scripts/fase2_muestra.py`

## Justificación del diseño muestral

**Por qué muestreo estratificado:**  
El STOXX 600 está muy concentrado sectorialmente (Financial Services + Industrials representan >40%). Un muestreo aleatorio simple daría representación excesiva a estos sectores y dejaría sin representación a sectores pequeños pero relevantes para el análisis ESG (Real Estate, Utilities). La estratificación garantiza que cada supersector ICB aporte al análisis comparativo (RQ2).

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
| Industrial Goods and Services | 10 |
| Financials | 10 |
| Communication Services | 5 |
| Health Care | 5 |
| Basic Materials | 4 |
| Consumer Products and Services | 3 |
| Utilities | 3 |
| Construction and Materials | 3 |
| Consumer Discretionary | 3 |
| Technology | 3 |
| Food, Beverage and Tobacco | 2 |
| Real Estate | 2 |
| Energy | 2 |
| Travel and Leisure | 2 |
| Automobiles and Parts | 2 |
| Personal Care, Drug and Grocery Stores | 1 |

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

- **Cobertura market_cap:** 42/60 empresas (70%)
- **Cobertura ESG scores:** 0/60 — yfinance ha deprecado la API de sostenibilidad para acciones europeas
- **Datos disponibles vía yfinance:** ROA, ROE, deuda/equity, ingresos, EBITDA, margen de beneficio

## ESG scores — plan para obtenerlos

Los scores ESG **no están disponibles en yfinance** para la mayoría de empresas europeas. Opciones por orden de preferencia:

### Opción A — Refinitiv/LSEG Workspace (recomendada)
Pedir acceso en la **Biblioteca de Económicas de la UV**. Permite exportar directamente una tabla con:
- ESG Combined Score
- Environmental Score (E)
- Social Score (S)
- Governance Score (G)
- Controversies Score
- Para todos los años 2022 y 2023

Pasos: buscar las empresas por ISIN o nombre → seleccionar campos ESG → exportar CSV → merge con `empresas_muestra.csv`.

### Opción B — Sustainalytics (manual)
Buscar empresa por empresa en https://www.sustainalytics.com/esg-ratings  
- Da ESG Risk Rating (numérico, a menor valor = menor riesgo)
- Tedioso pero gratuito
- Guardar en `data/external/sustainalytics_manual.csv` con columnas: `nombre, ESG_risk_score, ESG_risk_categoria`

### Opción C — MSCI ESG Ratings (limitado)
https://www.msci.com/our-solutions/esg-investing/esg-ratings-climate-search-tool  
Solo da la categoría (AAA/AA/A/BBB/BB/B/CCC), no el score numérico.

### Cómo incorporarlos al dataset maestro
Una vez obtenidos, hacer merge sobre `empresas_muestra.csv` por `nombre` o `ticker`:

```python
import pandas as pd
maestro = pd.read_csv("data/external/empresas_muestra.csv")
esg = pd.read_csv("data/external/esg_scores_refinitiv.csv")  # exportado de Refinitiv
maestro = maestro.merge(esg, on=["ticker", "año"], how="left")
maestro.to_csv("data/external/empresas_muestra.csv", index=False)
```

## Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `data/external/stoxx600_componentes.csv` | 534 empresas del índice con sector ICB y país |
| `data/external/muestra_seleccionada.csv` | 60 empresas seleccionadas con tickers y metadatos |
| `data/external/yfinance_datos.csv` | Datos financieros de yfinance por empresa |
| `data/external/empresas_muestra.csv` | Dataset maestro (120 filas: 60 empresas × 2 años) |
| `data/external/tracking_descargas.csv` | Hoja de seguimiento para recolección de informes (Fase 3) |
