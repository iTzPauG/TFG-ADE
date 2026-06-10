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

---

## Decisión 018 — Diccionario ESRS (Fase 5A): construcción manual enriquecida con EFRAG

**Decisión:** Construir el diccionario de keywords ESRS manualmente a partir del Reglamento Delegado (UE) 2023/2772, con validación cruzada contra la EFRAG ESRS XBRL Taxonomy (Annex 1). Guardado en `data/external/diccionarios/esrs_keywords.json` (v1.1). Referencia metodológica: Suta et al. (2025).

**Alternativas consideradas:**
- **A (elegida):** Construcción manual basada en los Disclosure Requirements de los 12 ESRS + enriquecimiento con términos técnicos del Excel EFRAG XBRL (`EFRAG_ESRS_XBRL_Taxonomy_Annex1.xlsx`, descargado en `data/external/diccionarios/`).
- **B:** Usar un diccionario publicado por investigadores (Suta et al. 2025 — acceso al material suplementario pendiente; FinBERT-ESG-9-categories como clasificador complementario en 5C).
- **C:** Extracción automática del PDF de los ESRS — descartada porque la taxonomía XBRL contiene etiquetas estructurales (nombres de campos de reporting), no vocabulario que aparezca en el texto de los informes.

**Justificación:**
- La opción A produce un diccionario directamente orientado a búsqueda de subcadenas en texto, que es lo que requiere el análisis de cobertura ESRS.
- El Excel de EFRAG (1.600+ datapoints) solo aportó 4-5 términos técnicos nuevos genuinamente útiles (`substances of very high concern`, `SVHC`, `sbtn`, `supervisory bodies`, `remuneration committee`) — confirma que el diccionario manual ya cubría bien el espacio conceptual.
- Suta et al. (2025) — *"Dictionary-based assessment of ESRS disclosure topics"*, Discover Sustainability 6, 146 — valida el enfoque dictionary-based para los 12 ESRS y es citable directamente en la sección de Metodología del TFG.
- El diccionario puede defenderse como: *"Construido manualmente a partir de los Disclosure Requirements del Reglamento Delegado (UE) 2023/2772, con validación cruzada contra la taxonomía XBRL oficial de EFRAG y en línea con la metodología de Suta et al. (2025)."*

**Estructura:** 11 categorías (E1-E5, S1-S4, G1, ESRS2), 25-44 términos/raíces por categoría. Uso: búsqueda de subcadena (`str.contains`) sobre `clean_text.lower()`. Las raíces cubren variantes morfológicas (e.g. `"decarboni"` → decarbonisation/decarbonization).

**Cobertura media en corpus `sus` (289 docs):** E1=0.50 · S1=0.49 · ESRS2=0.39 · G1=0.36 · E5=0.32 · S2=0.26 · E3=0.24 · S4=0.22 · E4=0.20 · S3=0.19 · E2=0.15. Jerarquía coherente con la priorización real de los estándares en los informes.

---

## Decisión 019 — Sección de análisis para RQ3 y tratamiento de densidad_baja (Fase 5)

**Decisión:** El análisis de greenwashing (RQ3: especificidad ClimateBERT, GW_index) se aplica sobre la sección **`sus`** exclusivamente. Las 16 filas con `confianza = densidad_baja` se **incluyen en el análisis principal** pero se documentan como limitación.

**Justificación:**
- Aplicar FinBERT y ClimateBERT sobre `sus` es coherente con la literatura de referencia (Bingler et al. 2022 aplica ClimateBERT sobre la sección climática de los informes) y evita mezclar señales de la narrativa de negocio con señales de sostenibilidad.
- Las 16 filas `densidad_baja` corresponden a empresas que publican la sostenibilidad en informe separado (Engie ×3, Richemont ×3, Lonza ×2, Telecom Italia, RBI, Alcon 2024, Flutter, Bolloré 2022, Dia 2024, Brunello Cucinelli 2022/2023). Su exclusión reduciría la muestra en 5.5% (16/289) y eliminaría sistemáticamente ciertos sectores. Se mantienen con nota de que sus scores de cobertura ESRS y especificidad serán structuralmente más bajos por la parcialidad del texto extraído.
- **Análisis de sensibilidad recomendado:** repetir los tests estadísticos clave (5E) con y sin `densidad_baja` para verificar robustez. Reportar ambos resultados en el TFG.

**Implementación:** filtrar con `df[df['seccion']=='sus']` para todos los análisis de RQ3. Añadir columna `fiable = confianza != 'densidad_baja'` para facilitar el análisis de sensibilidad.

---

## Decisión 020 — Recursos adicionales para Fase 5C: FinBERT-ESG y Suta et al.

**Decisión:** Añadir **FinBERT-ESG-9-categories** (`yiyanghkust/finbert-esg-9-categories`, HuggingFace) como clasificador complementario en el bloque 5C, además de los modelos ya previstos (FinBERT ProsusAI, ClimateBERT ×4, Loughran-McDonald).

**Justificación:**
- FinBERT-ESG-9-categories clasifica frases en 9 categorías ESG (Climate Change, Natural Capital, Pollution & Waste, Human Capital, Product Liability, Community Relations, Corporate Governance, Business Ethics & Values, Non-ESG) con ~14.000 frases anotadas manualmente. Permite obtener una distribución de topics ESG a nivel de frase, complementando el topic modeling de 5B.
- Correspondencia aproximada con ESRS: E1≈Climate Change, E2≈Pollution & Waste, E3/E4≈Natural Capital, S1/S2/S3≈Human Capital+Community Relations, G1≈Corporate Governance. No cubre E5 (circular economy) ni S4 (consumers) — limitación a documentar.
- **No sustituye** al diccionario ESRS (Decisión 018) ni a ClimateBERT: son complementarios. El diccionario mide cobertura; FinBERT-ESG mide distribución temática a nivel de frase; ClimateBERT mide especificidad/vaguedad.
- Modelo disponible en: `https://huggingface.co/yiyanghkust/finbert-esg-9-categories`

---

## Decisión 021 — Fase 5A: parámetros metodológicos y hallazgos

**Fecha:** 2026-06-09
**Script:** `scripts/nlp/fase5a_descriptivos.py`
**Outputs:** `results/tables/5a_*.csv`, `results/figures/5a_*.png`

**Parámetros TF-IDF:**
- Input: columna `tokens` (lemas en minúscula, sin stopwords, spaCy `en_core_web_sm`)
- `TfidfVectorizer(max_features=5000, min_df=3, ngram_range=(1,1), token_pattern=r"[a-z]{3,}")`
- N-gramas: `ngram_range=(2,3)`, `max_features=10000`, `min_df=3`

**Cobertura ESRS (media 289 docs `sus`, diccionario v1.1):**

| Categoría | Media | Std | Sin densidad_baja (n=273) |
|-----------|-------|-----|--------------------------|
| E1 | 0.503 | 0.213 | 0.525 |
| S1 | 0.487 | 0.234 | 0.507 |
| ESRS2 | 0.394 | 0.177 | 0.412 |
| G1  | 0.346 | 0.193 | 0.363 |
| E5  | 0.320 | 0.192 | 0.337 |
| S2  | 0.264 | 0.168 | 0.277 |
| E3  | 0.236 | 0.208 | 0.247 |
| S4  | 0.220 | 0.151 | 0.231 |
| E4  | 0.196 | 0.173 | 0.205 |
| S3  | 0.192 | 0.136 | 0.201 |
| E2  | 0.150 | 0.152 | 0.158 |

**Hallazgos estadísticos relevantes (RQ4):**
- Sección `sus` (n_tokens medio): 2022 → 10.947, 2023 → 14.556, 2024 → **23.068** (+111% en dos años).
- Sección `mr` es estable (~36-40k tokens), lo que confirma que el crecimiento es específico de la subsección de sostenibilidad.
- `densidad_baja` muestra coberturas estructuralmente bajas (E1=0.124 vs 0.573 para `alta`), confirmando que son secciones parciales, no ausencia de contenido. Justifica su tratamiento como limitación (Decisión 019).

---

## Decisión 022 — Fase 5B: parámetros de topic modeling

**Fecha:** 2026-06-09
**Script:** `scripts/nlp/fase5b_topics.py`

**Segmentación de párrafos:**
- Unidad: líneas de `clean_text` con ≥ 20 palabras (separadas por `\n`)
- Resultado: ~131.000 párrafos de 289 documentos sus (~453 párrafos/doc de media)

**LDA (gensim LdaMulticore):**
- Input: columna `tokens` re-tokenizada a nivel de párrafo (regex `[a-z]{3,}`, sin stopwords NLTK + lista de términos de reporting genéricos)
- `filter_extremes(no_below=5, no_above=0.85)`
- Selección de K: búsqueda por coherencia Cv en rango K∈{5,10,15,20,25}, 10 passes, 2 workers, `random_state=42`
- K óptimo: determinado por máximo Cv (ver `results/tables/5b_lda_coherencia.csv`)
- `alpha="asymmetric"`, `eta="auto"`

**BERTopic:**
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (384 dims), device MPS (M4)
- UMAP: `n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=42`
- HDBSCAN: `min_cluster_size=50, min_samples=10, metric="euclidean", eom`
- CountVectorizer: `ngram_range=(1,2), min_df=5, token_pattern=[a-z]{3,}`
- topics_over_time: 3 bins (2022/2023/2024)

**Justificación de elecciones:**
- `all-MiniLM-L6-v2`: modelo compacto (80MB) optimizado para inglés, equilibrio calidad/velocidad en M4.
- `min_cluster_size=50`: evita topics de una sola empresa; con 131k párrafos garantiza topics representativos.
- Segmentación por `\n` (no `\n\n`): `clean_text` no tiene doble salto de línea (verificado en Fase 5B); los saltos simples corresponden a párrafos del PDF original.

**Resultados LDA (actualizado con resultados reales):**
- K óptimo = 15 (Cv=0.684, curva plana entre 0.672–0.685)
- 15 topics interpretables: T06=Emisiones GHG (E1), T02=Agua/Biodiversidad (E2-E4), T13=Circular (E5), T00=Fuerza laboral (S1), T04=DDHH/cadena (S2-S3), T01=Privacidad (S4), T08=Gobernanza (G1), T05=Marco ESRS/GRI (ESRS2), T09=Doble materialidad (ESRS2), T11=Taxonomía UE, T07=Riesgo climático financiero
- Topics para RQ4: T05, T09, T11 (lenguaje específico CSRD, inexistente bajo NFRD)
- Artefactos: "music" en T00 (anómalo, no invalida topic); T03/T12 financieros dentro de sus (estructura híbrida corpus)

**Resultados BERTopic (completado):**
- 339 topics + outliers (topic -1): 48.355/131.140 párrafos (36.9%)
- Triangulación con LDA confirmada: T0 (DDHH/cadena, 4.200 párrafos) ≈ T04 LDA; T2 (gobierno, 1.816) ≈ T08; T3 (agua, 1.522) y T8 (biodiversidad, 1.110) ⊂ T02; T7 (doble materialidad/IROs, 1.155) ≈ T09; T15 (riesgo climático físico, 954) ≈ T07; T16 (Taxonomía UE, 807) ≈ T11
- 11 topics específicos de empresa detectados (Aena, Bouygues, AXA, Valeo, Porsche/VW, Orange, Orkla, Mercedes-Benz, Pernod Ricard, CaixaBank, Campari, Ontex) — granularidad adicional vs. LDA, útil para RQ2
- **topics_over_time (RQ4)**: T7 "doble materialidad/IROs" crece de 104→865 párrafos (2022→2024, ×8.2) — la señal textual más fuerte de transición NFRD→CSRD detectada en el proyecto. T16 "Taxonomía UE" crece 199→349 (×1.8, implementación progresiva ya iniciada en 2022). T15 (riesgo climático físico) crece 252→436 (×1.7)
- Tiempo de ejecución: 17.7 min (embeddings desde cero, cacheados en `bertopic_sus_embeddings.npy`) + 2.5 min (re-ejecución con caché)

---

## Decisión 023 — Selección de modelos para Fase 5: justificación frente a alternativas

**Fecha:** 2026-06-09
**Alcance:** todo el stack PLN de Fase 5 (5A–5E)

Esta decisión documenta explícitamente por qué se eligió cada modelo/herramienta sobre
sus alternativas directas. Es la base para la sección de Metodología del TFG.

---

### 5B — Topic Modeling

#### Justificación de usar LDA Y BERTopic conjuntamente (triangulación)

Se aplican ambos modelos en paralelo deliberadamente, no por redundancia sino por **triangulación metodológica**:

- **LDA** opera sobre bolsa de palabras (BoW): detecta topics por co-ocurrencia léxica. Es transparente, probabilístico y permite distribuciones topic×documento para las regresiones de 5E. Limitación: dos frases con el mismo significado pero palabras distintas van a topics distintos.
- **BERTopic** opera sobre embeddings semánticos: agrupa párrafos por significado, no por palabras. Captura sinónimos y frases relacionadas. Limitación: menos interpretable (UMAP+HDBSCAN son cajas negras parciales), K no es fijo ni reproducible entre ejecuciones sin semilla.

La combinación aporta: (1) si ambos modelos identifican los mismos temas con métodos radicalmente distintos, la robustez de los resultados queda validada; (2) donde divergen, señalan párrafos semánticamente complejos que merecen análisis cualitativo; (3) LDA alimenta las regresiones de 5E; BERTopic alimenta la evidencia temporal (topics_over_time) de RQ4. Esta estrategia de triangulación es coherente con el enfoque mixto cuantitativo-interpretativo del TFG.

---

#### LDA (Latent Dirichlet Allocation) — gensim LdaMulticore

**Elegido sobre:**

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| **NMF** (Non-negative Matrix Factorization) | Topics igualmente interpretables pero sin fundamento probabilístico; LDA es el estándar en la literatura de análisis de informes corporativos (Bingler et al. 2022, Loughran & McDonald 2011). |
| **LSA/LSI** (Latent Semantic Analysis) | No produce distribuciones probabilísticas; topics menos interpretables; no genera probabilidad de topic por documento, necesaria para 5E. |
| **CTM** (Correlated Topic Model) | Más expresivo pero >10× más lento, sin ventaja demostrada en corpora homogéneos de reporting (vocabulario controlado). |
| **NTM** (Neural Topic Models, p.ej. ProdLDA) | Requieren GPU para entrenamiento; resultados comparables a LDA en corpora especializados; añade dependencia de framework neural sin ganancia clara (Grootendorst 2022). |

**Razones positivas:**
- Referente metodológico directo: Bingler et al. (2022) usan LDA sobre informes climáticos.
- Produce distribución probabilística de topics por párrafo → directamente usable en regresiones de 5E.
- Interpretable: cada topic = lista de palabras con peso, citable en el TFG sin "caja negra".
- Robusto con vocabulario especializado en inglés (corpus homogéneo).
- `LdaMulticore` escala a 131k párrafos en <40 min en CPU.

---

#### BERTopic — sentence-transformers + UMAP + HDBSCAN

**Elegido sobre:**

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| **Top2Vec** | Arquitectura similar (embeddings + clustering) pero menos flexible, sin integración nativa de topics_over_time ni c-TF-IDF customizable. |
| **Guided LDA** | Requiere seeds manuales por topic → introduce sesgo; BERTopic descubre topics sin supervisión. |
| **STM** (Structural Topic Model) | Diseñado para R (stm package); incorpora metadatos (año, sector) en el modelo, pero requiere trasladar el corpus a R y el entrenamiento es muy lento para 131k párrafos. Útil como alternativa de robustez si se dispone de tiempo. |
| **LLM prompting** (p.ej. GPT-4 topic labeling) | No reproducible, costoso, no escalable a 131k párrafos, sin licencia abierta. |

**Razones positivas:**
- Captura semántica real: sinónimos y frases relacionadas van al mismo topic aunque no compartan palabras (LDA no puede).
- K automático: HDBSCAN decide el número de topics sin intervención → evita sesgo en la elección de K.
- Maneja outliers (-1): párrafos sin topic claro no contaminan los topics relevantes.
- `topics_over_time` nativo: la función de BERTopic calcula directamente la evolución temporal, clave para RQ4.
- Estado del arte en topic modeling (Grootendorst 2022, *"BERTopic: Neural topic modelling with a class-based TF-IDF procedure"*).

---

#### Modelo de embeddings: `all-MiniLM-L6-v2` (sentence-transformers)

**Elegido sobre:**

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| `all-mpnet-base-v2` | Mejor calidad (+1-2% en SBERT benchmarks) pero 3× más grande (420MB vs 80MB) y 2× más lento; la ganancia marginal no justifica el coste en M4 con disco lleno. |
| `paraphrase-multilingual-mpnet-base-v2` | Diseñado para multilingüe; el corpus es 100% inglés → overhead sin beneficio. |
| `BERT-base-uncased` (HuggingFace) | Produce embeddings de token, no de frase; requiere pooling manual; all-MiniLM ya lo hace optimizado. |
| `finance-bert` / `FinBERT` embeddings | FinBERT está optimizado para clasificación de sentimiento financiero, no para embeddings de similitud semántica general. Reservado para 5C. |
| `text-embedding-3-small` (OpenAI) | Requiere API key + coste por llamada; no reproducible offline; datos salen del entorno local. |

**Razones positivas:**
- 80MB, optimizado para velocidad en CPU/MPS; no supone riesgo de llenado de disco.
- Puntuación alta en SBERT benchmark para inglés en tareas de similitud semántica (Reimers & Gurevych 2019, *"Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks"*, EMNLP).
- Entrenado con destilación sobre MPNet: calidad próxima a modelos grandes a fracción del coste.
- Licencia Apache 2.0 → citable y reproducible en el TFG sin restricciones.
- Optimizado específicamente para tareas de similitud/clustering, que es exactamente el uso en BERTopic.

---

#### UMAP (Uniform Manifold Approximation and Projection)

**Elegido sobre:**

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| **PCA** | Reducción lineal: no captura relaciones no lineales en embeddings de alta dimensión (384 dims). Pierde la mayor parte de la estructura semántica. |
| **t-SNE** | Excelente para visualización (2D) pero: (1) no-paramétrico → no se puede aplicar a nuevos datos; (2) no preserva estructura global; (3) mucho más lento que UMAP a 131k puntos. |
| **Autoencoder** | Requiere entrenamiento adicional; añade complejidad sin garantía de mejora para clustering. |

**Razones positivas:**
- Preserva estructura local Y global del espacio de embeddings (McInnes et al. 2018, *"UMAP: Uniform Manifold Approximation and Projection"*).
- Escalable: 131k puntos × 384 dims reducidos a 5 dims en ~3-5 min en CPU.
- `n_components=5`: cinco dimensiones retienen más varianza semántica que 2D (visualización) y son suficientes para que HDBSCAN separe clusters de forma robusta; valor estándar en BERTopic para corpora grandes.
- **Nota técnica:** se usa la implementación estándar `umap-learn` (no-paramétrica), lo que significa que no es directamente aplicable a nuevos documentos sin re-entrenar. Para este TFG esto no es una limitación: el corpus es fijo y el modelo se entrena una sola vez.

---

#### HDBSCAN (Hierarchical DBSCAN)

**Elegido sobre:**

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| **K-means** | Requiere K fijo; asume clusters esféricos; no maneja ruido/outliers. Inadecuado cuando los topics no tienen fronteras claras. |
| **DBSCAN** | No jerárquico: muy sensible a `epsilon`; difícil calibrar a 131k puntos en 5D. |
| **GMM** (Gaussian Mixture Models) | Asume distribuciones gaussianas; clusters de topics no lo son. Alto coste computacional. |
| **Agglomerative clustering** | O(n²) en memoria → inviable para 131k puntos. |

**Razones positivas:**
- K automático: el número de topics emerge de los datos.
- Manejo explícito de outliers (cluster -1): párrafos genéricos o ambiguos no contaminan los topics.
- Jerárquico: permite explorar la jerarquía de topics a diferentes granularidades.
- `min_cluster_size=50`: garantiza topics con al menos 50 párrafos (~0.04% del corpus), evitando microtopics de una sola empresa.

---

### 5A — TF-IDF

**Elegido sobre:**

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| **Word2Vec / GloVe** | Embeddings de palabras: no producen scores de importancia directamente interpretables por término. TF-IDF es más transparente para análisis léxico descriptivo. |
| **BM25** | Diseñado para recuperación de información (ranking de documentos), no para análisis descriptivo de vocabulario. |
| **Frecuencia bruta** | No penaliza términos ubícuos (p.ej. "sustainability" aparece en todos los docs) → resultados poco informativos. TF-IDF normaliza por esto. |

**Razones positivas:**
- Estándar en análisis de contenido textual (Loughran & McDonald 2011 lo usan como baseline).
- Interpretable: score = importancia del término en ese documento relativa al corpus.
- Sin entrenamiento: determinista y reproducible.
- Input: columna `tokens` (ya lematizada y sin stopwords por spaCy en Fase 4) → evita duplicar preprocesamiento.

---

### 5C — Modelos de sentimiento y clasificación (decisión previa Dec.020, ampliada aquí)

#### Loughran-McDonald (LM) Financial Sentiment Dictionary

**Elegido sobre:**

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| **VADER** | Diseñado para redes sociales (tweets, reviews); el léxico positivo/negativo no está calibrado para texto corporativo financiero. "Liability" sería neutral en VADER, negativo en LM. |
| **SentiWordNet** | Léxico genérico; mismos problemas que VADER en contexto financiero. |
| **Harvard General Inquirer** | Menos preciso que LM para textos financieros (Loughran & McDonald 2011 lo demuestran empíricamente). |

**Razones positivas:**
- Diseñado específicamente para texto financiero y corporativo (Loughran & McDonald 2011, *"When Is a Liability Not a Liability?"*, JF).
- 6 categorías: Negative, Positive, Uncertainty, Litigious, Strong Modal, Weak Modal → útil para GW_index (uncertainty + weak modal = hedging).
- Estándar de facto en análisis de texto financiero; citable directamente.

---

#### FinBERT — `ProsusAI/finbert`

**Elegido sobre:**

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| **BERT-base** sentimiento general | No fine-tuneado para texto financiero; menor precisión en frases con jerga corporativa. |
| **RoBERTa** base | Ídem; sin adaptación al dominio financiero. |
| **DistilBERT** | Más rápido pero menor precisión; para 5C la calidad prevalece sobre velocidad (se corre una vez). |
| **GPT-4 / Claude** clasificación | No reproducible, costoso, sin licencia para investigación académica reproducible. |

**Razones positivas:**
- Fine-tuneado sobre Financial PhraseBank (~4.800 frases anotadas de noticias financieras) + corpus de Reuters y earnings calls; Araci (2019) reporta >97% accuracy en clasificación financiera.
- Tres clases: positive / negative / neutral → directamente aplicable a frases de informes de sostenibilidad sin adaptación adicional.
- Referente estándar en análisis de sentimiento financiero con BERT (Araci 2019, *"FinBERT: Financial Sentiment Analysis with Pre-trained Language Models"*; usado en Bingler et al. 2022 como baseline).
- Disponible en HuggingFace (`ProsusAI/finbert`) con licencia Apache 2.0.

---

#### ClimateBERT — 4 modelos especializados

**Elegido sobre:**

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| **FinBERT solo** | No captura especificidad climática; "We aim to reduce emissions" y "We will reduce emissions by 40% by 2030" serían igualmente "positivos" para FinBERT. ClimateBERT specificity los diferencia. |
| **Modelos de NLI generales** (p.ej. DeBERTa-NLI) | No fine-tuneados para compromisos climáticos; peor calibración en este dominio. |
| **Zero-shot con LLMs** | No reproducible; sin benchmark en sustainability reporting. |

**Razones positivas — 4 modelos distintos con roles complementarios:**

| Modelo ClimateBERT | Función | Por qué necesario |
|--------------------|---------|-------------------|
| `climatebert/distilroberta-base-climate-detector` | Detecta si la frase es sobre clima | Filtrar frases no-climáticas antes de sentiment |
| `climatebert/distilroberta-base-climate-sentiment` | Sentimiento climático (opportunity/neutral/risk) | Complementa FinBERT con dimensión riesgo/oportunidad |
| `climatebert/distilroberta-base-climate-commitment` | Distingue compromiso real vs. vago | Clave para GW_index (Dec.019/5D) |
| `climatebert/distilroberta-base-climate-specificity` | Mide especificidad cuantitativa | Core del GW_index: específico ↔ vago |

- Referente metodológico directo: Bingler et al. (2022), *"Cheap talk and cherry-picking"*.
- Fine-tuneados sobre corpus de sustainability reports → máxima relevancia para este TFG.

---

#### FinBERT-ESG-9-categories — `yiyanghkust/finbert-esg-9-categories`

**Elegido sobre:**

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| **Clasificación manual por reglas** | No escalable a 131k párrafos; introducción de sesgo del investigador. |
| **Zero-shot NLI** (p.ej. `facebook/bart-large-mnli`) | Menor precisión en textos ESG especializados; sin fine-tuning sobre datos ESG anotados. |
| **Diccionario ESRS solo** | Mide presencia de keywords, no clasificación de frases completas. Complementario, no sustituto. |

**Razones positivas:**
- ~14.000 frases ESG anotadas manualmente → alta fiabilidad en el dominio.
- 9 categorías alineadas con ESRS (ver Dec.020): permite comparar clasificación model-based vs. diccionario ESRS (Dec.018) → triangulación metodológica.
- Complementa ClimateBERT (que solo cubre E1) con una visión multi-pilar ESG.

---

## Decisión 024 — Fase 5C: parámetros de sentimiento, granularidad y pipeline en cascada

**Fecha:** 2026-06-10
**Script:** `scripts/nlp/fase5c_sentimiento.py`

### Granularidad: frases (no párrafos)

**Decisión:** segmentar `clean_text` de los 289 documentos `sus` en **frases** (spaCy `sentencizer`,
rule-based, sin parser/NER), filtrando frases con < 4 palabras (encabezados/viñetas).

**Resultado:** 285.509 frases (media 988/doc), frente a 131.140 párrafos de 5B.

**Justificación:**
- FinBERT, ClimateBERT (4 modelos) y FinBERT-ESG-9 fueron **fine-tuneados sobre frases**
  individuales (Financial PhraseBank, corpus de Bingler et al. 2022, ~14k frases ESG anotadas).
  Aplicarlos a párrafos completos (varias frases con tonos potencialmente distintos) introduciría
  ruido y se alejaría de la distribución de entrenamiento.
- El `sentencizer` rule-based (basado en puntuación) es ~100x más rápido que el pipeline completo
  de spaCy (`tok2vec+parser`) y suficiente porque `clean_text` conserva puntuación normalizada
  (Decisión 017). Se sube `nlp.max_length=3_000_000` porque sin parser/NER no hay riesgo de
  memoria cuadrática.
- Frases < 4 palabras (p.ej. "2.1 Climate change", viñetas sueltas) se descartan: no son
  unidades de sentimiento interpretables y distorsionarían los ratios LM (división por pocas palabras).

### Pipeline en cascada para ClimateBERT (siguiendo a Bingler et al. 2022)

**Decisión:** ejecutar `climate-detector` sobre las 285.509 frases primero; los 3 modelos
restantes (`climate-sentiment`, `climate-commitment`, `climate-specificity`) se aplican
**solo sobre las frases marcadas como `yes` por el detector**.

**Justificación:**
- Es el diseño del propio ClimateBERT: `climate-sentiment/commitment/specificity` se
  entrenaron sobre frases ya filtradas como climáticas; aplicarlos a frases no-climáticas
  (p.ej. tablas financieras, gobernanza) produce clasificaciones sin sentido interpretativo.
- Ahorro de cómputo: si ~25-35% de las frases son climáticas, los 3 modelos sub-secuentes
  procesan ~70-100k frases en vez de 285k cada uno (~3 × 40 min ahorrados).

### Optimización de inferencia: fp16 + max_length=96 (sin cambios metodológicos)

**Decisión:** todos los modelos de clasificación (ClimateBERT ×4, FinBERT, FinBERT-ESG-9) se
cargan en **fp16** sobre MPS y se trunca a **max_length=96 tokens**.

**Justificación (medición empírica en M4):**
- `max_length=256` (por defecto): ~117 min/modelo sobre 285k frases → ~10-12h para 6 modelos. Inviable.
- `max_length=96` + `fp32`: ~51 min/modelo.
- `max_length=96` + **fp16**: **~40 min/modelo** → total estimado pipeline completo ~3h.
- Percentiles de longitud de frase: p50=23 palabras, p90=47, **p95=63**, p99=142. `max_length=96`
  cubre el percentil 95 sin truncar; solo el 5% de frases más largas (típicamente listados
  enumerativos o frases con múltiples cláusulas) se truncan, lo cual es aceptable porque la
  clasificación de sentimiento/tono se decide mayoritariamente por las primeras cláusulas.
- fp16 en MPS no afecta a la clase predicha (softmax + argmax) de forma material; es la
  precisión estándar para inferencia (no entrenamiento) y ampliamente usada en producción.

### Resumibilidad y checkpointing

Cada paso (`frases`, `lm`, `climate_detector`, `climate_sub`, `finbert`, `esg9`, `agregar`)
guarda su propio parquet/csv en `results/tables/5c_*` y se salta si ya existe (`--fresh` para
forzar regeneración). Permite re-ejecutar tras un fallo sin recalcular pasos costosos ya
completados — mismo patrón que la caché de embeddings de BERTopic (Decisión 022).

### Outputs y agregación

A nivel documento (289 filas), se agregan:
- **Loughran-McDonald**: media de 7 ratios (negative, positive, uncertainty, litigious,
  strong_modal, weak_modal, constraining) por frase.
- **% frases climáticas** (climate-detector).
- **Tono FinBERT** = % frases positivas − % frases negativas; distribución completa
  positive/negative/neutral.
- **Distribución climate-sentiment/commitment/specificity** (sobre frases climáticas).
- **Distribución FinBERT-ESG-9** (9 categorías, todas las frases).

Estos agregados (`5c_doc_agregado.csv`) son el input directo de **5D** (`GW_index`) y **5E**
(regresiones, tests por año/sector).

### Incidencias durante la ejecución (documentadas para reproducibilidad)

La ejecución completa tomó **625.7 min (~10h25)** repartidos en varios lanzamientos por tres
incidencias técnicas, todas resueltas sin pérdida de checkpoints ya calculados:

1. **Cuelgue de FinBERT por fragmentación de memoria MPS.** Tras los 4 modelos ClimateBERT
   secuenciales (`climate-detector` + `climate-sentiment/commitment/specificity`), la carga
   de `ProsusAI/finbert` (5º modelo) se quedó colgada indefinidamente en `.to("mps").half()`
   (reproducido dos veces, con y sin `HF_HUB_OFFLINE=1`). **Fix:** se añadió limpieza de memoria
   al final de `clasificar()` (`del mdl, tok; gc.collect(); torch.mps.empty_cache()`), liberando
   el modelo anterior antes de cargar el siguiente. Tras el fix, FinBERT y FinBERT-ESG-9 cargaron
   con normalidad.

2. **El Mac entró en suspensión durante la noche**, pausando el proceso ~8.5h reales con solo
   1:30 min de CPU consumidos (de 04:03 a 05:56 prácticamente sin avance). **Fix:** se relanzó
   el proceso bajo `caffeinate -dimsu -w <PID>` para impedir la suspensión hasta que el proceso
   terminase. Tras esto, el ritmo volvió a ~19s/batch normal.

3. **FinBERT-ESG-9 produjo resultados inválidos por una caché de tokenizer incompleta.**
   El primer cálculo de `5c_esg9.parquet` dio `esg9_label = "Non-ESG"` en el 99.2% de las
   285.509 frases con `esg9_score` medio = 0.267 (≈ uniforme entre 9 clases). Diagnóstico:
   `AutoTokenizer.from_pretrained("yiyanghkust/finbert-esg-9-categories")` cargó un tokenizer
   degenerado (`vocab_size=5`, solo tokens especiales PAD/UNK/CLS/SEP/MASK) porque `vocab.txt`
   nunca se descargó correctamente a la caché de HuggingFace (solo `config.json` y
   `pytorch_model.bin` estaban presentes en el snapshot) — probablemente por *rate-limiting*
   de descargas no autenticadas. Como consecuencia, casi todas las palabras se tokenizaban
   como `[UNK]`. Se descartó fp16/MPS como causa (se probaron las 4 combinaciones
   fp16/fp32 × cpu/mps con resultados idénticos). **Fix:** se re-descargó el tokenizer con
   acceso a red (sin modo offline), quedando `vocab_size=30873` correcto; se verificó con 4
   frases de prueba que el modelo produce predicciones coherentes y confiadas
   (Climate Change 0.996, Corporate Governance 0.994, Human Capital 0.993, Non-ESG 0.994).
   Se borraron `5c_esg9.parquet`, `5c_doc_agregado.csv` y `5c_esg9_distribucion.png` (los
   únicos outputs afectados; el resto de checkpoints —frases, LM, ClimateBERT×4, FinBERT—
   eran válidos y se reutilizaron) y se re-ejecutaron solo los pasos `esg9` + `agregar`
   (~70 min). El resultado corregido tiene `esg9_score` medio = 0.857 y las 9 categorías
   representadas con distribuciones no triviales.

### Resultados (289 documentos `sus`, 285.509 frases)

**Loughran-McDonald (medias de ratio por frase, ×100 ≈ % de palabras del diccionario):**

| Año | Negative | Positive | Uncertainty | Litigious | Strong modal | Weak modal | Constraining |
|-----|----------|----------|-------------|-----------|--------------|------------|--------------|
| 2022 | 0.0101 | 0.0149 | 0.0085 | 0.0042 | 0.0031 | 0.0016 | 0.0047 |
| 2023 | 0.0107 | 0.0142 | 0.0097 | 0.0048 | 0.0028 | 0.0018 | 0.0052 |
| 2024 | 0.0127 | 0.0138 | 0.0110 | 0.0050 | 0.0026 | 0.0021 | 0.0058 |

Tendencia 2022→2024: el lenguaje **negativo, de incertidumbre y "constraining" aumenta**
mientras el **positivo y "strong modal" disminuyen**. Es coherente con un reporting CSRD más
prudente/cauteloso (más riesgos, condicionales y limitaciones reconocidas) frente al tono más
promocional del régimen NFRD — señal preliminar relevante para RQ4 y RQ3 (menos "cheap talk"
optimista).

**Frases climáticas (ClimateBERT climate-detector):** 118.321 / 285.509 (41.4% del total).
Estable por año: 43.4% (2022), 42.6% (2023), 44.2% (2024).

**FinBERT (tono financiero, todas las frases):**

| Año | % positivo | % negativo | % neutral | Tono (pos−neg) |
|-----|-----------|-----------|-----------|----------------|
| 2022 | 24.7% | 4.5% | 70.9% | 0.202 |
| 2023 | 23.4% | 4.6% | 72.0% | 0.188 |
| 2024 | 20.8% | 5.5% | 73.6% | 0.153 |

El tono positivo neto **cae de forma monótona** 2022→2024 (−0.049), con descenso del % de
frases positivas y ligero aumento del % negativas. Consistente con la tendencia LM: el
reporting bajo CSRD es menos "promocional".

**ClimateBERT cascada (sobre las 118.321 frases climáticas):**

| Año | Sentiment neutral | Opportunity | Risk | Commitment: no | Commitment: sí | Specificity: no | Specificity: sí |
|-----|-------------------|-------------|------|-----------------|------------------|-------------------|-------------------|
| 2022 | 68.0% | 21.5% | 10.4% | 65.5% | 34.5% | 71.9% | 28.1% |
| 2023 | 67.2% | 20.2% | 12.6% | 68.0% | 32.0% | 71.2% | 28.8% |
| 2024 | 66.6% | 16.2% | 17.2% | 72.5% | 27.5% | 74.3% | 25.7% |

Tres señales convergentes 2022→2024: **el discurso de oportunidad climática cae** (21.5%→16.2%),
**el de riesgo climático sube** (10.4%→17.2%, +65% relativo), y **tanto los compromisos
explícitos como la especificidad de las frases climáticas disminuyen ligeramente**
(commitment sí: 34.5%→27.5%; specificity sí: 28.1%→25.7%). La combinación de "más riesgo,
menos compromiso y menos especificidad" es una señal textual de interés directo para
**RQ3 (greenwashing/GW_index, Fase 5D)**: no se observa que el tono más optimista vaya
acompañado de mayor especificidad; si acaso ocurre lo contrario en agregado.

**FinBERT-ESG-9 (distribución de categorías, todas las frases, tras corrección del tokenizer):**

| Categoría | 2022 | 2023 | 2024 |
|-----------|------|------|------|
| Climate Change | 22.8% | 22.4% | 22.7% |
| Human Capital | 21.2% | 19.2% | 19.3% |
| Corporate Governance | 16.2% | 17.0% | 16.8% |
| Non-ESG | 12.0% | 15.0% | 14.1% |
| Community Relations | 7.1% | 6.7% | 5.4% |
| Product Liability | 5.5% | 5.3% | 5.9% |
| Business Ethics & Values | 5.8% | 5.4% | 5.9% |
| Pollution & Waste | 4.1% | 4.2% | 4.6% |
| Natural Capital | 5.2% | 4.8% | 5.2% |

Climate Change es la categoría dominante y estable (~22-23%), coherente con el peso de E1
encontrado en 5A/5B. Human Capital decrece ligeramente (21.2%→19.3%) y Non-ESG aumenta
(12.0%→14.1%), posiblemente reflejando mayor proporción de contenido normativo/de gobernanza
genérico (ESRS2) clasificado como "Non-ESG" por este modelo (limitación ya anotada en
Decisión 020: FinBERT-ESG-9 no cubre E5 ni S4 explícitamente).

Interpretación detallada y tablas/figuras completas en `docs/fase5c_interpretacion.md`.

---

## Decisión 025 — Fase 5D: definición y resultados del GW_index

**Fecha:** 2026-06-10. **Script:** `scripts/nlp/fase5d_gwindex.py`. **Granularidad:** 289
documentos `sus` (igual que 5C). Input: `5c_frases.parquet` (285.509 frases) +
`5c_doc_agregado.csv`.

### Definición operativa

Siguiendo la Decisión 001 (proxy de greenwashing basado en texto: especificidad, hedging,
ratio cuantitativo y tono), el `GW_index` combina cinco componentes a nivel documento:

| Componente | Definición | Origen |
|---|---|---|
| `hedging_ratio` | `lm_uncertainty + lm_weak_modal` (medias por frase) | ya calculado en 5C |
| `climate_specificity_spec` | % de frases climáticas clasificadas como específicas (ClimateBERT) | ya calculado en 5C |
| `ratio_cuantitativo` | % de frases con al menos una cifra, **excluyendo años sueltos** (`19xx`/`20xx`) | NUEVO (regex sobre `5c_frases.parquet`) |
| `ratio_futuro` | % de frases con lenguaje prospectivo (`will`, `shall`, `plan/aim/intend to`, `target`, `commit(ment)`, `by 20XX`, `ambition`, `pledge`, `goal`, `objective`, `going to`, `expect to`, `next year(s)/decade`, `upcoming`, `future`) | NUEVO (regex) |
| `ratio_futuro_sin_cifra` | % de frases prospectivas que **no** contienen ninguna cifra → "promesa vaga" (cheap talk) | NUEVO (combinación de los dos anteriores) |

Una frase como *"we aim to reduce emissions by 2030"* cuenta como `es_futuro=True` pero
`tiene_cifra=False` (2030 es un año, se excluye) → `futuro_sin_cifra=True`. Una frase como
*"we aim to reduce emissions by 40% by 2030"* tiene cifra (40%) → no cuenta como promesa vaga.

### Fórmula del índice

```
GW_index = z(hedging_ratio) + z(ratio_futuro_sin_cifra) − z(ratio_cuantitativo) − z(climate_specificity_spec)
```

Z-scores calculados sobre los 289 documentos. Valores altos = más lenguaje cauteloso/de
promesas vagas y futuras sin cuantificar, y menos especificidad climática y datos
cuantitativos → mayor señal de "cheap talk". El tono FinBERT **no** se incluye en el índice
(se reporta aparte como variable de contraste, para no mezclar sentimiento financiero
general con la definición operativa de greenwashing basada en LM+ClimateBERT).

Decisión confirmada con el usuario: fórmula de z-scores tal cual, `ratio_futuro` por
lista de keywords/regex (no ClimateBERT-commitment), y los dos ratios nuevos calculados
sobre **todas** las frases `sus` (285.509), igual que los ratios LM (consistente con Dec.019).

### Resultados (medias por año)

| Año | GW_index | hedging_ratio | ratio_cuantitativo | ratio_futuro | ratio_futuro_sin_cifra | climate_specificity_spec |
|-----|----------|---------------|---------------------|--------------|------------------------|---------------------------|
| 2022 | −0.196 | 0.0102 | 0.322 | 0.192 | 0.130 | 0.281 |
| 2023 | −0.329 | 0.0115 | 0.336 | 0.188 | 0.123 | 0.288 |
| 2024 | **+0.521** | 0.0132 | 0.304 | 0.189 | 0.125 | 0.257 |

- **GW_index aumenta marcadamente en 2024** (primer año CSRD obligatorio), tras un ligero
  descenso 2022→2023. El salto 2024 está impulsado por: hedging al alza (+29% vs 2022),
  especificidad climática a la baja (−8.5%) y ratio cuantitativo a la baja (−5.6%).
  `ratio_futuro_sin_cifra` se mantiene prácticamente plano (0.130→0.125).
- **Robusto a Dec.019**: excluyendo las 16 filas `densidad_baja`, la tendencia es idéntica
  (−0.284 → −0.450 → +0.532).
- **Test pareado 2022↔2024** (95 empresas con datos en ambos años): Wilcoxon p=0.021
  (significativo), t-test p=0.055 (marginal) → el aumento de GW_index 2024 vs 2022 es
  estadísticamente robusto a nivel no paramétrico.
- **Correlaciones cruzadas** (289 docs): GW_index correlaciona positivamente con
  `climate_sentiment_risk` (r=0.50) y negativamente con `climate_sentiment_opportunity`
  (r=−0.24) y `climate_commitment_yes` (r=−0.12). Correlación con `finbert_tone` es débil
  (r=0.10) en corte transversal — pero la **relación temporal** es la relevante para RQ4:
  el tono cae (Dec.024) mientras el GW_index sube, es decir, el discurso es simultáneamente
  menos optimista y más "cheap talk" (más hedging, menos especificidad/cuantificación), no
  un patrón de "más optimismo sin sustancia" pero sí de "menos sustancia en general" bajo CSRD.

### Para RQ3/RQ4

El aumento del GW_index en 2024 es la pieza que faltaba en la triangulación de 5C: el
descenso simultáneo de especificidad, compromiso y oportunidad climática (Dec.024) **no**
viene acompañado de mayor cuantificación (`ratio_cuantitativo` también baja) ni de menos
promesas vagas (`ratio_futuro_sin_cifra` estable) — el índice agregado confirma que el
reporting 2024 es más cauteloso/hedged y menos específico/cuantificado en términos
relativos, compatible con una señal de "cheap talk" creciente bajo CSRD. Input directo
para 5E (regresiones con sector/país/tamaño como predictores de GW_index).

Tabla completa: `results/tables/5d_gwindex.csv`. Figuras: `5d_gwindex_evolucion.png`,
`5d_componentes.png`, `5d_gwindex_vs_tono.png`. Interpretación: `docs/fase5d_interpretacion.md`.

---

## Decisión 026 — Fase 5E: estadística inferencial (RQ2, RQ3, RQ4)

**Fecha:** 2026-06-10. **Script:** `scripts/nlp/fase5e_stats.py`. **Panel:** 289 docs `sus`
(`5e_panel.csv`) = `5d_gwindex.csv` + `n_tokens` (`corpus.parquet`) + sector/país/financieros
(`empresas_muestra.csv`).

### Decisiones de diseño confirmadas con el usuario

- **País (14 niveles, varios n<5):** se reportan **ambos** análisis — Kruskal-Wallis
  descriptivo por país (RQ2, 14 grupos) **y además** una variable `region` (4 zonas:
  Nórdicos, Centro, Sur, UK&Irlanda) usada como control adicional en las regresiones.
  Mapeo: Nórdicos = {Suecia, Noruega, Dinamarca, Finlandia}; Centro = {Francia, Alemania,
  Suiza, Austria, Bélgica, Países Bajos}; Sur = {España, Italia}; UK&Irlanda = {Reino
  Unido, Irlanda}. Verificado sin colinealidad perfecta sector×región (cada supersector
  presente en ≥2 regiones).
- **2 regresiones OLS, errores robustos HC3**, variable de tamaño = `log(capitalización)`
  (sin NaN, a diferencia de `total_assets`/`ROA` que tienen 4 NaN en FY2022, Dec.006 — esas
  4 filas se excluyen de las regresiones, n=285/289).
- **VIF**: la matriz de diseño para `variance_inflation_factor` debe **incluir el
  intercepto** (de lo contrario las regresiones auxiliares se calculan "a través del
  origen" e inflan artificialmente variables no centradas en 0 como `log_cap`, dando
  VIF≈15-23 espurios). Corregido en el script; VIF reales ≤2.6 en ambas regresiones →
  sin problema de multicolinealidad.

### RQ2 — Kruskal-Wallis (¿difiere por sector/país?)

| Variable | ~ supersector (11 grupos) | ~ país (14 grupos, descriptivo) |
|---|---|---|
| `GW_index` | H=43.53, p<0.001, η²=0.151 | H=49.46, p<0.001, η²=0.172 |
| `finbert_tone` | H=18.58, p=0.046, η²=0.065 | H=45.31, p<0.001, η²=0.157 |
| `climate_specificity_spec` | H=49.08, p<0.001, η²=0.170 | H=33.90, p=0.001, η²=0.118 |

- **GW_index por sector**: máximo en Technology (mediana 1.39) y Financials (1.14);
  mínimo en Utilities (−1.89), Communication Services (−1.19) y Real Estate (−0.89).
- **GW_index por país**: máximo en Suiza (1.22) y Reino Unido (0.85); mínimo en Italia
  (−1.89) y Francia (−1.52) — coherente con el resultado de la regresión (región Centro
  como referencia tiene GW_index más bajo que Nórdicos/UK&Irlanda).
- **Especificidad climática**: mayor en Real Estate (0.339) y menor en Technology (0.200)
  y Financials (0.204) — sectores financieros/tecnológicos hablan más de clima en términos
  generales/cualitativos.
- Aviso: los grupos de país con n<5 (Austria, Irlanda, Bélgica, Dinamarca, Finlandia) hacen
  el test por país menos fiable; se reporta como evidencia complementaria, no concluyente.

Tablas: `5e_kruskal_supersector.csv`, `5e_kruskal_pais.csv`. Figuras:
`5e_gwindex_supersector.png`, `5e_gwindex_region.png`.

### RQ4 — Test pareado 2022 vs 2024 (NFRD→CSRD, 95 empresas comunes)

| Variable | 2022 | 2024 | Δ | t-test p | Wilcoxon p |
|---|---|---|---|---|---|
| `GW_index` | −0.196 | +0.424 | **+0.620** | 0.055 | **0.021** |
| `finbert_tone` | 0.202 | 0.157 | −0.046 | **0.0015** | **0.0003** |
| `climate_specificity_spec` | 0.281 | 0.261 | −0.020 | 0.210 | 0.086 |
| `climate_sentiment_risk` | 0.104 | 0.164 | **+0.060** | **<0.0001** | **<0.0001** |
| `climate_sentiment_opportunity` | 0.215 | 0.165 | −0.051 | **0.0018** | **0.0006** |
| `n_tokens` (sus) | 10.947 | 23.380 | **+12.433** | **<0.0001** | **<0.0001** |

Confirma con significación formal (no solo descriptiva, Dec.021/024) los hallazgos de
5A/5C/5D: el reporting 2024 es significativamente más extenso, menos optimista (tono↓,
oportunidad↓), con más discurso de riesgo climático y un GW_index significativamente más
alto. La caída de especificidad climática es marginal (p≈0.09) a nivel pareado.

Tabla: `5e_pareado_2022_2024.csv`. Figura: `5e_pareado_2022_2024.png`.

### RQ3 — Regresiones OLS (HC3), n=285

**Reg1: `GW_index ~ log(capitalización) + ROA + deuda_equity + supersector + año + región`**
(R²=0.223, R²adj=0.171). Referencia: sector=Basic Materials, año=2022, región=Centro.

- `log_cap`: **−0.268, p=0.024** → empresas más grandes tienen menor GW_index (menos
  "cheap talk"), controlando por sector/región/año.
- `Financials`: **+2.10, p<0.001**; `Technology`: **+1.90, p=0.011** → mayor GW_index que
  Basic Materials. `Real Estate`: **−1.93, p=0.014** → menor.
- `región Nórdicos`: **+1.34, p<0.001**; `región UK&Irlanda`: **+1.07, p=0.011** → mayor
  GW_index que Centro (consistente con KW por país: Francia/Italia bajos).
- `año 2024`: +0.598, p=0.104 — **no significativo una vez controlado por
  sector/tamaño/región**: el efecto temporal bruto de RQ4 (+0.62, Wilcoxon p=0.021) se
  explica en parte por composición sectorial/regional, no es un efecto CSRD homogéneo
  puro.
- `ROA`, `deuda_equity`: no significativos.

**Reg2: `finbert_tone ~ climate_specificity_spec + log(capitalización) + ROA + supersector + año + región`**
(R²=0.206, R²adj=0.152).

- `climate_specificity_spec`: **+0.220, p=0.0032** → **más especificidad climática se
  asocia con tono MÁS positivo** (no menos), en corte transversal. Esto **no apoya** la
  hipótesis simple "más optimismo ↔ menos especificidad" como patrón cross-sectional —
  empresas con discurso climático más concreto tienden además a un tono financiero
  general más positivo (posiblemente porque reportan logros/avances concretos en términos
  positivos).
- `año 2024`: **−0.042, p=0.013** → el descenso de tono 2022→2024 (Dec.024) **se mantiene
  significativo incluso controlando por especificidad, sector, tamaño y región** — es un
  efecto temporal robusto, no explicado por composición.
- `Health Care`: +0.130, p=0.042; `Real Estate`: −0.075, p<0.001; `región UK&Irlanda`:
  +0.070, p<0.001.
- `log_cap`, `ROA`: no significativos.

VIF máximo en ambas regresiones = 2.6 (sin problema de multicolinealidad). Tablas:
`5e_regresion1_gwindex.csv`, `5e_regresion2_tono.csv` + `5e_regresion{1,2}_vif.csv`.

### Síntesis para RQ3/RQ4

- **RQ3**: el GW_index varía sistemáticamente por sector (Tech/Financials altos,
  Real Estate/Utilities bajos) y por tamaño (empresas grandes → menos cheap talk). La
  hipótesis "tono optimista ↔ menos especificidad" **no se sostiene** en corte
  transversal (Reg2): la relación es positiva, no negativa. La señal de mayor "cheap
  talk" en 2024 (RQ4/5D) es en parte composicional (sector/región), pero el descenso de
  tono es un efecto temporal robusto independiente de esos controles.
- **RQ4**: confirmación estadística formal de la transición NFRD→CSRD: más extensión
  textual, menos tono positivo, más riesgo climático y mayor GW_index — todos
  significativos a nivel pareado salvo la especificidad climática (marginal).

Interpretación completa: `docs/fase5e_interpretacion.md`.
