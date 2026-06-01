# Registro de decisiones metodológicas

> Cada entrada documenta una decisión relevante y su justificación. Útil para la defensa del TFG.

---

## Plantilla

**Decisión:** [qué se decidió]
**Alternativas consideradas:** [qué otras opciones había]
**Justificación:** [por qué se eligió esta opción]

---

## Decisión 001 — Proxy de greenwashing basado en texto

**Decisión:** Medir greenwashing mediante variables textuales internas exclusivamente: especificidad (ClimateBERT), hedging, ratio cuantitativo y tono (FinBERT).

**Justificación:**
1. **Coherencia metodológica:** Usar ratings de terceros construidos parcialmente a partir de los mismos informes que analizamos introduce circularidad. Un proxy puramente textual es más coherente con el diseño de análisis de contenido.
2. **Precedente académico:** Bingler et al. (2022) — "Cheap talk and cherry-picking" — miden greenwashing exclusivamente con ClimateBERT-specificity sobre el texto, sin score externo. Es el referente directo de este TFG.
3. **Riqueza analítica:** Los proxies textuales permiten análisis granulares (por sección, por párrafo) imposibles con un único score numérico anual.

**Implicación para el TFG:** Explicar en Metodología que se adopta una definición operativa de greenwashing basada en la brecha entre tono comunicativo y especificidad de compromisos, en línea con la literatura de impression management (Cho et al., 2015; Hahn & Lülfs, 2014).

---

## Decisión 002 — Muestreo estratificado con cap geográfico (v2)

**Decisión:** Muestreo aleatorio estratificado por sector ICB (20 sectores × 5 = 100 empresas objetivo), con cap geográfico iterativo de máximo 15 empresas por país. Muestra final: **97 empresas** (3 menos por restricciones de diversidad geográfica en Media y Technology). `random_state=42`.

**Alternativas consideradas:**
- v1: 60 empresas, 3/sector, sin cap geográfico → UK era el 32% de la muestra
- Top-5 por capitalización dentro de cada sector → sesgo mega-cap
- Muestreo aleatorio simple sin estratificación

**Justificación:**
- **n=97 vs n=60**: con 3 empresas por sector, los tests Kruskal-Wallis intra-sector eran inviables. Con 5/sector, los supersectores tienen entre 4 y 20 empresas, suficiente para análisis descriptivo-inferencial.
- **AÑOS [2022,2023,2024]**: FY2024 es el primer ejercicio de reporte obligatorio bajo CSRD para grandes PIEs (publicado primavera 2025). Permite analizar la transición NFRD→CSRD empíricamente (RQ4).
- **Cap geográfico (≤15)**: UK representaba el 32% estructural del STOXX 600; el cap corrige este sesgo sin alterar la lógica de estratificación sectorial. Francia (21 en v1 por reemplazos de UK) quedó correctamente en 15 tras la aplicación iterativa del cap.
- **Datos financieros año-específicos**: desde v2 se usan `income_stmt` y `balance_sheet` de yfinance para calcular ROA, ROE, ingresos y deuda por año. En v1, los ratios de `.info` eran idénticos para 2022 y 2023 (trailing value), lo que invalidaba cualquier análisis longitudinal de variables financieras de control.

**Cobertura final:**
- 95/97 empresas con datos financieros completos (98%)
- 2 sin datos: TUI Group (ticker TUI.DE sin cobertura yfinance; usar TUI1.DE en iteraciones futuras) y Schibsted (SCHA.OL sin cobertura confirmada)
- 28/97 empresas con ISIN verificado; 69 en `isins_pendientes.csv` para búsqueda manual

---

## Decisión 003 — Período de análisis 2022-2024

**Decisión:** Incluir el ejercicio 2024 además de 2022 y 2023.

**Justificación:** La CSRD (Directiva 2022/2464) establece que las grandes empresas de interés público (PIEs con >500 empleados) deben reportar por primera vez para el **ejercicio fiscal 2024**, con publicación en primavera 2025. Incluir 2024 permite:
1. Comparar directamente informes NFRD (2022-2023) con CSRD (2024) — clave para RQ4.
2. Detectar cambios en estructura, cobertura ESRS y tono entre regímenes.
3. Aumentar el panel a 291 observaciones (vs 120 en v1), mejorando el poder estadístico de los modelos de regresión.

**Implicación metodológica:** No todas las empresas publican en el mismo formato bajo CSRD en 2024 (algunas todavía bajo exención o reporting voluntario). Documentar en Metodología qué empresas de la muestra estaban sujetas a CSRD obligatorio en 2024 vs voluntario.

---

## Decisión 004 — ISINs: fuentes y cobertura parcial aceptable

**Decisión:** Usar ISINs de tres fuentes en cascada (yfinance → Wikidata SPARQL → búsqueda manual via `isins_pendientes.csv`); resolución automatizada con `completar_isins.py`.

**Justificación:** El ISIN es relevante para identificar informes en registros oficiales (BORME, Bundesanzeiger, Companies House) pero no es necesario para el pipeline NLP (extracción de texto, análisis de sentimiento, topic modeling). La búsqueda automática de ISINs para listings europeos es estructuralmente limitada: yfinance devuelve ISINs de ADRs para muchos tickers europeos, y no existe una API gratuita y fiable que cubra el universo STOXX 600 de forma completa. La cascada yfinance → Wikidata (propiedad P946) con `completar_isins.py` resolvió el total de la muestra.

**Cobertura final:** 97/97 empresas con ISIN verificado. `isins_pendientes.csv` vacío.

---

## Decisión 005 — Sustitución de Schibsted por Universal Music Group

**Decisión:** Reemplazar Schibsted (SCHA.OL, Noruega) por Universal Music Group (UMG.AS, Países Bajos) en la muestra. Ejecutado en `scripts/fase2_parche_deuda.py`.

**Alternativas consideradas:**
- Vivendi (VIV.PA): descartada porque Francia ya alcanza el cap de 15 empresas.
- CTS Eventim (CTS.DE), Sanoma (SANO.HE): sin cobertura en yfinance.
- Mantener Schibsted con ROA=NaN para los 3 años: inviable — empresa sin ningún dato financiero de control, lo que la excluiría de todos los modelos de regresión (Fase 5E).

**Justificación:**
- Schibsted (SCHA.OL) no tiene cobertura en yfinance: ni income_stmt, ni balance_sheet, en ningún ticker alternativo (SCHB.OL, SCHA.OL, SCHDY, SCHBF). Causa probable: empresa fuera del universo cubierto por Yahoo Finance API para el mercado noruego.
- UMG (UMG.AS): misma categoría sectorial (Media / Communication Services), cotiza en Euronext Amsterdam, año fiscal diciembre, cobertura 3/3 años con datos completos (ROA, ROE, ingresos 2022-2024). ISIN: NL0015000IY2.
- Impacto geográfico: Países Bajos pasa de 5 a 6 empresas (cap ≤ 15, sin problema). Noruega pasa de 5 a 4.

---

## Decisión 006 — Gap datos financieros FY2022 en empresas con año fiscal no-diciembre

**Decisión:** Aceptar 4 filas con ROA=NaN en FY2022 (Richemont, 3i Group, JD Sports, Vodafone) y documentarlo en el campo `nota` del dataset maestro.

**Causa técnica:** yfinance proporciona `balance_sheet` de los últimos 4 ejercicios fiscales. Para empresas con cierre distinto a diciembre, el ejercicio "2022" corresponde a la columna más antigua (2022-03-31 o 2022-01-31), que en algunos casos ya no está disponible en el caché de Yahoo Finance, o existe pero con todos los valores NaN.

**Empresas afectadas y cierre fiscal:**
| Empresa | Ticker | Cierre FY | Años con datos |
|---------|--------|-----------|----------------|
| Richemont | CFR.SW | 31 marzo | 2023, 2024 |
| 3i Group | III.L | 31 marzo | 2023, 2024 |
| JD Sports | JD.L | 31 enero | 2023, 2024 |
| Vodafone | VOD.L | 31 marzo | 2023, 2024 |

**Alternativas descartadas:**
- Reconstruir FY2022 desde quarterly financials: yfinance no tiene `quarterly_income_stmt` para estas empresas en ese período.
- Fuentes alternativas (Macrotrends, GuruFocus): requieren scraping complejo, fuera del alcance de la Fase 2.

**Implicación metodológica:** Estas 4 observaciones tendrán variables financieras de control ausentes para 2022 y quedarán excluidas de los modelos de regresión del Panel para ese año. Representan 4/291 = 1.4% del panel, lo que no afecta materialmente al poder estadístico. Mencionar en la sección de Metodología como limitación menor.

---

## Decisión 007 — EBITDA para entidades financieras: cascada de cómputo

**Decisión:** Para las 12 entidades financieras de la muestra (4 bancos, 5 aseguradoras, 3i) donde yfinance no devuelve el campo "EBITDA" directo, se calcula mediante una cascada: (1) "EBITDA" → (2) "Normalized EBITDA" → (3) EBIT + D&A → (4) Operating Income + D&A → (5) Pretax Income + D&A. La fuente empleada se registra en la columna `fuente_ebitda`. Implementada en `scripts/fase2_parche_ebitda.py` y en `fase2_muestra.py`.

**Cobertura resultante:**
| FY | EBITDA disponible | % |
|----|------------------|---|
| 2022 | 93/97 | 96% |
| 2023 | 96/97 | 99% |
| 2024 | 97/97 | 100% |

**Nulos residuales (5/291 = 1.7%):**
- Richemont, 3i, JD Sports, Vodafone — FY2022: gap por año fiscal no-diciembre (ver Decisión 006)
- AXA — FY2023: income_stmt sin ninguno de los campos de la cascada para ese año concreto

**Fuentes usadas:**
- `direct` (255 filas): campo "EBITDA" de yfinance — empresas industriales/no financieras
- `ebit+da` (13 filas): EBIT + Reconciled Depreciation — principalmente aseguradoras
- `pretax+da` (18 filas): Pretax Income + Reconciled Depreciation — bancos y 3i

**Justificación:** El EBITDA no es un campo estándar en la cuenta de resultados de entidades financieras: los bancos no tienen "Operating Income" separado de su actividad financiera, y las aseguradoras separan el resultado técnico del financiero. La cascada garantiza la mayor comparabilidad posible. En la sección de Metodología del TFG documentar que el EBITDA de entidades financieras es un proxy reconstruido y que los resultados de regresión son robustos si se excluyen esas 12 empresas de los modelos que usen EBITDA como variable de control.

---

## Decisión 008 — Tipo de informe en Fase 3: informe anual integrado

**Decisión:** Descargar el informe anual integrado (integrated annual report) como documento primario para cada empresa-año. No se descarga por defecto el informe de sostenibilidad separado salvo que la empresa no publique informe anual integrado.

**Justificación:**
- El informe anual integrado contiene el management report consolidado, que es el objeto de análisis del TFG.
- Las grandes empresas del STOXX 600 publican mayoritariamente un único documento que integra informe de gestión e información financiera y no financiera.
- Descargar dos documentos (anual + sostenibilidad) duplicaría el volumen de trabajo de extracción en Fase 4 y requeriría lógica adicional de fusión de secciones.

**Convención de nombrado:** `[TICKER]_[AÑO]_integrated.pdf` en `data/raw/[pais]/[ticker]/`.

---

## Decisión 009 — Estrategia de descarga automatizada en Fase 3

**Decisión:** Pipeline de tres estrategias por orden de prioridad:
1. Rastreo de página IR corporativa conocida (base de datos `IR_PAGES` en `fase3_descarga.py`)
2. DuckDuckGo HTML search con filtro de score para priorizar informes anuales y excluir documentos parciales (HGB Einzelabschluss, proxy, convocatorias, etc.)
3. annualreports.com como fuente de terceros con scraping estático

**Por qué no ResponsibilityReports.com:** El sitio solo tiene informes hasta 2016; no cubre el período 2022-2024 que necesitamos.

**Limitación conocida:** Las webs IR corporativas bloquean descargas automatizadas con 403. La URL encontrada por DDG o IR_PAGES se guarda en el tracking; el estudiante la abre en el navegador y descarga manualmente si la descarga directa falla. Se registra con `scripts/fase3_registrar.py`.

**Cobertura esperada:** DDG + IR_PAGES cubre ~50-60% de los informes. El resto (40-50%) requiere búsqueda manual vía `data/external/busqueda_manual.html`.

---

## Decisión 010 — Exclusión de NEM 2022 y DIA 2022 del corpus NLP

**Decisión:** Excluir del análisis NLP (Fase 4-5) dos observaciones empresa-año cuyos informes carecen de contenido de sostenibilidad analizable: **Nemetschek 2022** (NEM, E096) y **Dia 2022** (DIA, E056). El resto de años de ambas empresas (NEM 2023/2024, DIA 2023/2024) se mantienen en el corpus.

**Alternativas consideradas:**
- Buscar un Nachhaltigkeitsbericht / EINF separado de 2022: para NEM probablemente no existe (reporting ESG incipiente en software, 2022); para DIA el EINF podría estar en CNMV, pero la empresa estaba en reestructuración y el contenido sería mínimo.
- Incluir con métricas textuales = 0 o anotando bajo contenido: introduce ruido en los análisis de 2022 y distorsiona los promedios sectoriales.

**Justificación:**
- **NEM 2022** (Geschäftsbericht, 178pp): Cat D en la auditoría de sostenibilidad — 1pp con contenido ESG específico. El Konzern-Lagebericht existe pero la información de sostenibilidad es prácticamente nula. Nemetschek es una empresa de software alemana con reporting ESG incipiente en 2022.
- **DIA 2022** (informe financiero + auditoría, 207pp): Cat E — 0pp ESG detectadas. Dia estaba en plena reestructuración; el documento es el informe de auditoría y estados financieros consolidados, sin información no financiera analizable.
- La evolución 2022→2024 de ambas empresas (de ausencia de ESG a reporting estructurado) es en sí misma un hallazgo coherente con la implantación gradual de CSRD, no una pérdida de información.

**Implementación:** Se marcan como `estado=descartado` en `tracking_descargas.csv` y se anota la exclusión en el campo `nota` de `empresas_muestra.csv`. **No se eliminan las filas**: se preserva el panel financiero y la traza documental. El pipeline de Fase 4 debe filtrar las observaciones con `estado=descartado` antes de extraer texto.

**Impacto en la muestra:** Corpus NLP = **289 observaciones empresa-año** (vs 291 del panel financiero). 2/291 = 0.7% del total. No afecta materialmente al poder estadístico. Documentar en Metodología como exclusión justificada por ausencia de contenido analizable.
