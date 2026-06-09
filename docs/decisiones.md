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

---

## Decisión 011 — Extracción de texto (Fase 4A) y remediación por OCR de PDFs con fuente corrupta

**Decisión:** Extraer el texto de los 289 PDFs con **PyMuPDF** (`fitz`, unión de páginas con `\n`). Control de calidad por documento: ratio de caracteres de control y densidad de palabras-función en el idioma detectado. Los PDFs con **fuente embebida sin mapa ToUnicode/cmap válido** (texto ilegible) se remedian con un **OCR híbrido**: se rasteriza con PyMuPDF (`get_pixmap`, 300 dpi) y se pasa por Tesseract **solo las páginas corruptas**, conservando el texto nativo de las páginas legibles.

**Alternativas consideradas:**
- Reparar el mapeo glifo→Unicode leyendo el `cmap`/`post` de la fuente embebida con fontTools: inviable — las fuentes subset (OpenSans/Arial) venían **sin tabla cmap ni post**, así que la correspondencia carácter↔glifo no existe en el PDF.
- pdfminer / pdfplumber como extractor alternativo: devuelven `(cid:NN)` (mismo problema de raíz); no recuperan texto.
- Re-descargar otra copia / poppler: descartado por el usuario (usar los PDFs que ya teníamos, evitar dependencias).
- OCR de todo el documento: descartado — degradaría las páginas con capa de texto nativa (mejor calidad que OCR).

**Justificación:** El OCR híbrido recupera el contenido sin sacrificar la calidad del texto nativo y sin software extra (rasterizado con PyMuPDF, no pdf2image/poppler). Tesseract 5.5.2 con idiomas eng/fra/spa/deu/ita.

**Documentos remediados (6):** ALC 2024 (144/274 pp OCR), WEND 2023 (11 pp), ADEN 2022 (113/198), ADEN 2023 (106/180), BOL-Bolloré 2022 (304/372). Tras OCR: ratio de control 0,09→0,00, palabras-función a niveles sanos. Originales corruptos respaldados en `data/interim/_corruptos/*.pre_ocr.txt`.

**Nota técnica:** colisión de ticker `BOL` (Boliden E010 / Bolloré E045) → los `.txt` se nombran con `id_empresa` (`{id}_{ticker}_{año}.txt`), no con ticker. Barrido full-doc final: **289/289 con texto limpio, 0 corruptos**. Scripts: `scripts/extraction/fase4_extraccion.py`, `fase4_ocr_remediar.py`.

---

## Decisión 012 — Estrategia de idioma (Fase 4B): versiones oficiales en inglés del emisor, sin traducción automática

**Decisión:** El corpus se homogeneiza a **inglés**. Para los 27 informes detectados como no-ingleses (25 francés + 2 español; `langdetect` con voto por 9 ventanas para robustez ante portadas corruptas), se **sustituye el PDF por la versión oficial en inglés publicada por la propia empresa** (Universal Registration Document en inglés / Integrated Management Report), **no** por traducción automática.

**Alternativas consideradas:**
- Traducir los 27 con deep-translator (Google): distorsiona justo las señales que se miden (tono, hedging) y añade un paso no reproducible.
- Modelos multilingües (XLM-R/mBERT): no hay equivalente multilingüe validado de FinBERT/ClimateBERT → rompería la Decisión 001 y obligaría a re-justificar los modelos.
- Híbrido por idioma: incomparabilidad de scores entre subcorpus.

**Justificación:** Casi todas las empresas del STOXX 600 publican una versión inglesa oficial de su informe (traducción profesional del propio emisor), de mucha mayor calidad que la MT y plenamente defendible. Mantiene intacta la Decisión 001 (FinBERT/ClimateBERT/LM, English-only) y la comparabilidad del corpus, sin distorsión de traducción.

**Implementación:** 12 empresas, 27 informes sustituidos (descarga manual del usuario + verificación automática de idioma/empresa/año). Originales fr/es respaldados en `data/raw/_reemplazados_originales/`. Enlaces en `docs/fase4_informes_ingles.md`. **Resultado: corpus 289/289 en inglés.** Scripts: `fase4_mover_ingleses.py`.

---

## Decisión 013 — Aislamiento del management report y la sostenibilidad (Fase 4C): índice del PDF como método primario

**Decisión:** Segmentar cada informe en (a) **bloque narrativo / management report** y (b) **subsección de sostenibilidad**, usando el **índice navegable del PDF** (`get_toc`) como método primario. Operacionalización robusta a la heterogeneidad de formatos (URD numerados, Strategic Report UK, integrados temáticos):
- **Fin del bloque narrativo = primer capítulo de ESTADOS FINANCIEROS** (no la gobernanza: en muchos URD la sostenibilidad va *después* de gobernanza y *antes* de los estados financieros).
- **Subsección de sostenibilidad** = epígrafe que casa con marcadores ESG (sustainability, non-financial, CSR, extra-financial…), agrupando hasta el siguiente capítulo no-sostenible (capta el capítulo CSR completo); se elige el de mayor extensión para descartar menciones cortas.

**Alternativas consideradas:**
- Un único capítulo "Management Report" homogéneo: no existe transversalmente en estos informes.
- Regex sobre texto plano: frágil frente a maquetación y multi-columna.
- Parsear el índice impreso (página "Contents"): los números son páginas impresas con offset respecto al índice del PDF → poco fiable para trocear.

**Justificación:** El TOC del PDF es la lista de epígrafes con su página exacta; el fin en estados financieros es un límite inequívoco y frecuente. Validado a mano (Stellantis, Repsol, Mercedes, Bouygues, Gecina): correcto.

**Cobertura:** management report localizado en **283/289 (98%)**; sostenibilidad fiable por índice en **126** (113 alta confianza ≥8 pp + 13 media). Salidas: `data/interim/secciones/{id}_{ticker}_{año}_{mr,sus}.txt` + manifiesto `secciones_manifest.csv` (rangos, método, `sus_confianza`). Script: `fase4_secciones.py`.

---

## Decisión 014 — Sostenibilidad por densidad de vocabulario ESG (Fase 4C) para informes sin índice fiable

**Decisión:** En los informes donde el índice del PDF **no** da una subsección de sostenibilidad fiable (PDFs sin índice navegable o con maquetación que engaña a la heurística de epígrafes, p. ej. Kering, Gecina, L'Oréal), aislar la sostenibilidad por **densidad de vocabulario ESG por página**: se puntúa cada página por nº de términos ESG por 100 palabras y se toma el **mayor bloque contiguo** de páginas con densidad ≥ 2,5 (fusionando huecos ≤ 3 pp, mínimo 5 pp).

**Alternativas consideradas:**
- Fallback por tamaño de fuente (pseudo-índice): trunca la sostenibilidad a 2-6 pp en informes con mucho diseño/marketing (la fuente grande también se usa en texto promocional y cifras) → descartado.
- Semi-manual (hoja de cálculo, Paso 4.9 de la guía): mayor precisión pero coste alto para el estudiante.

**Justificación:** La densidad ESG es **independiente de los epígrafes y de la maquetación**, por lo que funciona igual en informes de diseño y resuelve los casos que la heurística de epígrafes no podía. Calibrado contra rangos conocidos por índice (Stellantis, Mercedes, Repsol): los inicios coinciden bien (Kering 158 vs 159 real, Mercedes inicio exacto). Captura el grueso del contenido ESG (objetivo del análisis), aunque el final puede quedar 1-2 capítulos corto en algún caso.

**Aplicación:** método primario = índice (Decisión 013) donde sea limpio; densidad ESG en los dudosos. Para llegar a **cobertura 100%** se relajó el detector en los 16 informes con ESG disperso (ventana de mayor masa ESG con umbral relativo, garantiza bloque) y se marcó su menor fiabilidad. Scripts: `fase4_sost_densidad.py` y `fase4_completar_cobertura.py`.

**Resultado final (cobertura 289/289):**
- Management report: **289/289**. 283 por índice/fuente + 6 por fallback (italianos sin índice: Brunello Cucinelli ×3 y Campari ×2 → documento entero por llevar "financial statements" en running header; STMicro 2022 → corte en estados financieros p115).
- Sostenibilidad: **289/289**. `sus_confianza`: **alta 113 + media 13** (índice fiable = 126) + **densidad 147** (bloque ESG estricto) + **densidad_baja 16** (densidad relajada, fiabilidad baja).
- **Italianos (sin índice) reprocesados con densidad ESTRICTA**: BRNW 2024, CPR 2022/2023, STMPA 2022 dieron sección real (`densidad`); BRNW 2022/2023 (pre-CSRD, ESG mínimo) no dieron bloque estricto → finalmente se aceptan con densidad relajada (`densidad_baja`) para mantener cobertura completa.

**Caveats a documentar en el TFG:** (1) las 16 secciones `densidad_baja` corresponden a empresas que publican la sostenibilidad en **informe separado** (Engie ×3, Richemont ×3, Lonza ×2, Telecom Italia, RBI, Alcon 2024, Flutter, Bolloré 2022, Dia 2024) o con ESG mínimo/disperso (Brunello Cucinelli 2022/2023) → su sección extraída es parcial; para máxima calidad, sustituir por el informe de sostenibilidad/CSR separado del emisor (acción opcional). (2) Los bloques por densidad pueden empezar/terminar 1-2 páginas dentro de un capítulo vecino. `sus_confianza` ∈ {alta, media, densidad, densidad_baja} permite filtrar por fiabilidad en la Fase 5.

---

## Decisión 015 — Saneamiento de calidad de la segmentación (Fase 4C)

**Decisión:** Auditar y reparar de forma quirúrgica tres defectos de calidad de las secciones `_mr`/`_sus`, sin rehacer lo correcto. Script: `scripts/extraction/fase4_sanear_secciones.py` (dry-run por defecto, `--apply` con backup en `secciones/_bak_sanear/`). Caché de OCR limpio por página en `data/interim/_paginas_ocr/`.

**Defectos corregidos:**
- **A) Secciones extraídas del PDF con fuente corrupta.** Los scripts 4C leían el texto nativo del PDF crudo (roto) en vez del texto remediado por OCR, dejando 7 secciones ilegibles (ALC 2024, ADEN 2022/2023, AF 2022, AKERBP 2024). Se regeneran desde texto limpio **por página** (OCR solo en las páginas con la capa de texto rota; el resto nativo). El OCR de las páginas corruptas (363 en total) se hace **en paralelo** sobre los núcleos disponibles y se cachea, para no repetirlo.
- **B) `_sus` que capturó un índice o página divisoria** en vez de contenido (TGS 2023 = 1 página divisoria; AKERBP 2023/2024 y AF 2022 = sub-índice del capítulo). Se re-detectan por densidad ESG sobre el texto limpio. MKS 2023 pasó de una intro de 2 pp al *Non-Financial and Sustainability Information Statement* completo (18 pp).
- **C) `_mr` que abarcaba casi todo el documento** (fin de la narrativa no detectado → el management report incluía los estados financieros). Se busca el inicio de los estados financieros en la cabecera de página y se re-corta. **106 → 30** management reports documento-entero; los 30 restantes son informes sin epígrafe localizable de estados financieros (integrados temáticos, varios españoles).

**Justificación:** la corrupción de fuente y los falsos positivos contaminarían el análisis de Fase 5. Todo cambio lleva backup y el script es **idempotente** (un segundo pase propone 0 cambios), lo que garantiza consistencia manifiesto↔fichero. Verificación final: 0 secciones corruptas (antes 7), 0 rangos inválidos, 91 ficheros saneados.

**Resultado (`sus_confianza`):** alta 113 · densidad 152 · media 8 · densidad_baja 16 (= 289). Mediana mr_pp 144, sus_pp 39.

**Caveat:** los 30 management reports sin corte de estados financieros conservan el documento completo; como el análisis de sostenibilidad de Fase 5 opera sobre `_sus` (correctamente aislado), no es bloqueante. Marcable para filtrado si se analiza `_mr` en su conjunto.

---

## Decisión 016 — Corrección del límite del management report y de la sostenibilidad sobre-extraída (Fase 4C)

**Contexto:** una auditoría posterior al saneamiento (Decisión 015) detectó dos defectos que el recorte del *bloque C* no resolvía bien:
- **El recorte de MR del bloque C era poco fiable.** Buscaba el inicio de los estados financieros como "primer epígrafe *financial statements* en cabecera tras el 30% del documento", lo que saltaba con menciones incidentales y **cortaba ~21 MR demasiado pronto** (mr_fin quedaba *antes* del capítulo de sostenibilidad — imposible, ya que la sostenibilidad es narrativa y precede a los financieros). Otros ~22 ya venían mal de la detección original (43 inversiones en total).
- **Sostenibilidad sobre-extraída:** en informes tipo URD, el capítulo de sostenibilidad detectado por índice no hallaba su cierre (los sub-epígrafes "7.1 Climate"… también casan como sostenibilidad) y se desbordaba hasta el 60-91% del documento (RBI 2024 = 552 pp, AENA 2022 = 91%).

**Decisión:** sustituir el recorte heurístico de MR por reglas conservadoras y fiables (`scripts/extraction/fase4_recalcular_limites.py`, dry-run por defecto, `--apply` con backup en `secciones/_bak_limites/`, idempotente):
1. **Invariante `mr_fin ≥ sus_fin`** — el MR siempre contiene la sostenibilidad. Solo se *extiende* mr_fin cuando había quedado por debajo; **nunca se acorta** con heurísticos de financieros (que rompían detecciones correctas por índice). 50 MR corregidos.
2. **Acotado de sostenibilidad sobre-extraída** (≥55% del doc): `sus_fin` = primer epígrafe de estados financieros tras `sus_ini`, **solo si reduce de verdad y el bloque queda <55%**. 6 casos acotados (RBI 552→43 pp, REP 176→75 pp, CS 416→149 pp, ULVR, ACX, REP23) — verificado: arrancan en el epígrafe real de sostenibilidad, densidad ESG 1,5-5,2.
3. **No se adivina:** 4 informes sin corte fiable (sostenibilidad arrancando en portada o financieros no localizables) se marcan **`sus_confianza = revisar`** para revisión/marcado manual (AENA 2022/2024, Engie-ENG 2022/2024).

**Justificación:** el límite exacto de fin del MR no es localizable de forma fiable por texto en muchos informes (integrados temáticos, varios españoles) — es el caso que la GUÍA (Paso 4.9) prevé marcar a mano. Priorizar **no romper lo correcto** sobre forzar un corte. El análisis de Fase 5 opera sobre `_sus` (ahora correctamente acotado), por lo que los **56 MR que abarcan ≥85% del documento** (sin corte fiable de financieros) no son bloqueantes.

**Estado final verificado (289/289):** 0 corrupción · 0 inversiones (`sus_fin ≤ mr_fin`) · 0 rangos inválidos · 0 sobre-extraídos sin marcar. `sus_confianza`: **alta 111 · densidad 150 · media 8 · densidad_baja 16 · revisar 4**. Mediana mr_pp 160, sus_pp 38. **Supersede el recorte de MR del bloque C de la Decisión 015** (la cobertura "106→30" de aquella queda obsoleta).

---

## Decisión 017 — Estructura del corpus (Fase 4D): secciones MR (sin solapamiento) + sostenibilidad

**Decisión:** El `data/processed/corpus.parquet` tiene **una fila por sección** con dos secciones por documento (cuando existen):
- `seccion = "mr"` → **management report SIN la subsección de sostenibilidad** (rango del MR menos el rango de sostenibilidad). Captura la narrativa estratégica/negocio/gobernanza sin solapar con sostenibilidad.
- `seccion = "sus"` → subsección de sostenibilidad aislada (Fase 4C).

Columnas: `id, empresa, año, seccion, idioma, clean_text, tokens, confianza, n_tokens, n_chars`. `clean_text` conserva mayúsculas y puntuación (para BERT/FinBERT/ClimateBERT); `tokens` = lemas en minúscula sin stopwords ni puntuación (spaCy `en_core_web_sm`, para LDA/TF-IDF).

**Justificación (opción híbrida frente a alternativas):**
- **Evita el doble conteo:** por el invariante de la Decisión 016, `sus ⊂ mr`. Meter el MR completo *y* la sostenibilidad duplicaría el texto de sostenibilidad en el corpus, sesgando TF-IDF/LDA/BERTopic y los descriptivos de frecuencia. Restar la sostenibilidad del MR lo elimina.
- **Conserva ambas preguntas:** `mr` (sin sostenibilidad) habilita RQ1 (temas del management report) y RQ4 (evolución NFRD→CSRD); `sus` es la base de RQ3 (greenwashing/especificidad/ESRS).
- **Trazabilidad de calidad:** la columna `confianza` lleva `sus_confianza` (alta/densidad/media/densidad_baja/aceptado_sin_financieros) en las filas `sus`, y marca en las filas `mr` si el management report abarca casi todo el documento (los 56 sin corte fiable de estados financieros → arrastran financieros = ruido, filtrable en RQ1).

**Granularidad:** el corpus se guarda a **nivel sección**. El troceo en **párrafos** (topic modeling, Paso 5.8) y en **frases** (FinBERT/ClimateBERT, Pasos 5.11-5.13) es de la Fase 5, sobre `clean_text`. Script: `scripts/extraction/fase4_corpus.py`.

**Limpieza aplicada (Paso 4.11):** eliminación de cabeceras/pies repetidos (líneas que reaparecen en gran parte de las páginas de la sección), números de página sueltos, caracteres de control y artefactos, normalización de espacios y reconstrucción de párrafos rotos por columnas. Se conservan mayúsculas y puntuación.
