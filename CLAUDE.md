# CLAUDE.md — TFG ADE

Contexto maestro del proyecto. Léelo entero antes de actuar. Para el detalle de cada
decisión metodológica, la fuente de verdad es `docs/decisiones.md` (Decisiones 001–017).

---

## 1. Qué es el proyecto

**TFG de ADE (Universitat Politècnica de València — Facultad de ADE, FADE).** Tutor: Elíes Seguí Mas. Título:
> *"Comunicación corporativa y estrategias de gestión en los informes de sostenibilidad
> de las empresas europeas: un análisis de contenido mediante técnicas de inteligencia artificial."*

**Objetivo:** analizar, con técnicas de PLN, cómo las grandes empresas europeas (STOXX
Europe 600) comunican su estrategia de sostenibilidad en sus informes corporativos, bajo
el marco normativo CSRD / ESRS / Taxonomía UE / SFDR. Se busca identificar discursos,
patrones comunicativos y señales textuales de *greenwashing*.

**Preguntas de investigación:**
- **RQ1** — ¿Qué temas predominan en el management report del STOXX 600? (topic modeling)
- **RQ2** — ¿Hay diferencias significativas de contenido y tono por sector y país?
- **RQ3** — ¿Qué factores (sector, país, tamaño) predicen mayor especificidad y cobertura
  cuantitativa en sostenibilidad? ¿Más tono optimista ↔ menos especificidad (señal de greenwashing)?
- **RQ4** — ¿Cómo evoluciona el reporting entre el régimen NFRD (2022–23) y CSRD (2024)?

**Referente metodológico directo:** Bingler et al. (2022), *"Cheap talk and cherry-picking"*
(ClimateBERT). Marco teórico: Loughran & McDonald (2011), Hahn & Lülfs (2014), Cho et al.
(2015), Michelon et al. (2015). Detalle en `docs/notas_literatura.md`.

---

## 2. Reglas de trabajo (PREFERENCIAS DEL USUARIO — obligatorias)

1. **Responde en español.** El usuario trabaja en español.
2. **NUNCA uses ratings/scores ESG de terceros** (MSCI, Sustainalytics, Refinitiv…). Todo el
   análisis es **textual**: FinBERT, ClimateBERT, diccionario Loughran-McDonald, diccionario
   ESRS propio. Usar scores externos rompe la Decisión 001 (circularidad metodológica).
3. **Correcciones quirúrgicas, no rehacer lo correcto.** Si hay que arreglar un defecto, toca
   solo las entradas afectadas. **Confirma antes de cualquier `rm` masivo** o de regenerar
   trabajo ya validado. El usuario valora mucho no perder trabajo correcto.
4. **No inventes nombres de fichero/script.** Verifica que existen antes de recomendarlos.
5. Todo cambio metodológico relevante se documenta como nueva **Decisión** en `docs/decisiones.md`.
6. Toda decisión medianamente importante se pregunta primero al usuario.
7. Todo script debe tener incluido barras de progreso y porcentajes para poder consultar cual es el progreso.

---

## 3. Entorno y cómo ejecutar

- **Conda env: `tfg-ade`** (Python 3.11), en `/opt/homebrew/Caskroom/miniconda/base/envs/tfg-ade`.
  Tiene pandas, pyarrow, spaCy (`en_core_web_sm`), PyMuPDF, etc. El env `base` **no** tiene pyarrow.
  ```bash
  source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh
  conda activate tfg-ade
  # o bien:  conda run -n tfg-ade python ...
  ```
- **Tesseract** instalado a nivel sistema (OCR, idiomas eng/fra/spa/deu/ita).
- macOS (darwin), shell zsh. El repo vive en `~/Documents` → **se sincroniza con iCloud**.

### ⚠️ GOTCHA crítico: ficheros "dataless" (evacuados a iCloud)
El disco va lleno (~92%) y macOS evacúa ficheros a iCloud ("Optimizar almacenamiento"). Un
fichero evacuado **lee 0 bytes aunque `stat` muestre su tamaño real → NO es corrupción.**
Afecta sobre todo a `data/raw/*.pdf`, `data/interim/secciones/*.txt` y `corpus.parquet`.
- Detectar sin disparar descarga (leer un dataless **bloquea** el proceso):
  `stat -f '%Sf' <fichero>` → muestra `dataless` en los flags.
- Re-materializar **antes** de correr cualquier script que los lea:
  ```bash
  brctl download data/processed/corpus.parquet
  find data/interim/secciones -maxdepth 1 -name '*.txt' -exec brctl download {} \;
  ```
- Scripts versionados que queden dataless: `rm` + `git checkout -f HEAD -- <ruta>`.
- Detalle completo en `error.md` (raíz) y `docs/retomar_fase5.md`.

---

## 4. Estado del pipeline (por fase)

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1 | Marco teórico + normativo + RQs | ✅ Documentado (`docs/notas_*.md`) |
| 2 | Construcción de la muestra | ✅ **196 empresas × 3 años** (ampliación 97→196, Decisiones 027-028-030), financieros 196/196 |
| 3 | Recolección de informes | ✅ **588/588** (586 descargado + 2 descartado intencional, Decisión 010) |
| 4 | Extracción y limpieza de texto | ✅ **COMPLETA (4A-4D) para las 196** (Decisión 033/034). `corpus.parquet`: 1172 filas (586 docs × 2 secciones), 263 MB, QA OK (Decisión 035) |
| 5 | Análisis con PLN | ✅ **COMPLETA (5A-5E) sobre las 196 empresas (586 docs)** — re-ejecutada desde cero (Decisión 036). Pendiente reinterpretación de topics LDA K=25/BERTopic 578 |
| 6 | Dashboard (HTML estático) + reproducibilidad | ✅ dashboard regenerado sobre **196 empresas / 586 docs** (Decisión 036); falta reproducibilidad |
| 7 | Redacción del TFG | ⬜ Pendiente |

La guía paso a paso completa de las 7 fases está en `GUÍA.MD` (raíz).

### Muestra (Fase 2)
- **196 empresas × 3 años (2022, 2023, 2024) = 588 filas** en el panel financiero
  (`data/external/empresas_muestra.csv`).
- Origen: muestra inicial de **97 empresas** (estratificada por sector ICB ~5/sector,
  cap geográfico ≤15/país, corrige el 32% estructural de UK, `random_state=42`,
  Decisiones 002, 005) **ampliada a 196** (Decisión 027) repitiendo el muestreo
  estratificado sobre las restantes empresas del STOXX 600, con el mismo cap
  geográfico aplicado solo a las 99 nuevas (E098-E196).
- **Decisión 028**: Delivery Hero estaba duplicado en `stoxx600_componentes.csv`
  (tickers Wikipedia `DHER` y `DASH` → misma empresa, ISIN `DE000A2E4K43`) y había
  caído dos veces en la muestra (E062 y E157). E157 sustituido por **Inditex** (ITX,
  España, mismo sector Retail).
- **Decisión 030**: 4 duplicados adicionales detectados (misma empresa con 2 entradas
  en `stoxx600_componentes.csv`): E112 Vinci (=E018), E116 Bouygues (=E019), E185
  Castellum (=E061), E194 Gruppo Campari (=E038, cambio de nombre 2022). Sustituidos
  por **Heidelberg Materials** (E112, Alemania, Construction and Materials),
  **Wienerberger** (E116, Austria, Construction and Materials), **LEG Immobilien**
  (E185, Alemania, Real Estate) y **Lindt & Sprüngli** (E194, Suiza, Food, Beverage
  and Tobacco). 196 empresas son ahora entidades únicas confirmadas (sin duplicados
  por ISIN ni ticker_yf).
- 2024 = primer ejercicio **obligatorio CSRD** para grandes PIEs → habilita RQ4 (NFRD→CSRD).
- Dataset maestro: `data/external/empresas_muestra.csv` (financieros año a año desde yfinance:
  ROA, ROE, ingresos, EBITDA, deuda, capitalización…). EBITDA de entidades financieras = proxy
  reconstruido por cascada (Decisión 007). Huecos FY2022 por año fiscal no-diciembre
  (Decisión 006): Richemont, 3i, JD Sports, Vodafone (muestra original) + Inditex (Decisión 028).

### Recolección de informes (Fase 3) — `data/external/tracking_descargas.csv`
- **588 filas** (196 empresas × 3 años). **586 `descargado`**, **2 `descartado`**
  (Dia 2022 y Nemetschek 2022 — PDF existe pero 0-1pp ESG, excluidos del corpus NLP,
  Decisión 010), **0 `problema`**.
- PDFs en `data/raw/<País>/<TICKER>/<TICKER>_<año>_integrated.pdf` (gitignored).
- Las 99 empresas nuevas (E098-E196) están descargadas y **verificadas por contenido**
  (Decisión 029: 9 PDFs de empresa equivocada o truncados detectados y corregidos —
  Swiss Re/Swiss Prime Site/IAG/Norsk Hydro/EssilorLuxottica/ABN AMRO/WDP; más Euronext
  ENX 2023, con fuente sin ToUnicode, sustituido por versión Workiva con texto nativo —
  ninguno necesita OCR). **Han pasado por Fase 4A-4C** (Decisión 033); pendiente 4D
  (`corpus.parquet`) y Fase 5 (PLN).
- **Decisión 031**: QA de contenido completo de los 586 PDFs `descargado` (PyMuPDF,
  recuento de páginas + texto). 24/25 PDFs problemáticos sustituidos por la versión
  correcta en inglés (Annual Report/URD/cuentas consolidadas): 18 de empresa
  equivocada (colisión de ticker con `annualreports.com`: ING, Santander, Flow
  Traders, SCOR, Informa, ams OSRAM, CTS Eventim, Dia 2024) + 6 de tipo de documento
  incorrecto (Michelin 2023-2024, Renault 2022-2024, Naturgy 2023). Originales en
  `data/raw/_reemplazados_decision031/`.
- **Decisión 032**: 2 sustituciones adicionales — Michelin 2022 (URD francés →
  Universal Registration Document inglés, 476 págs) y Puma 2023 (PDF con
  fuente/CMap sin ToUnicode, texto cifrado → Annual Report 2023 con texto
  nativo, 390 págs). Originales en `data/raw/_reemplazados_decision032/`.

### Segmentación (Fase 4C) — `data/interim/secciones_manifest.csv`
- **586 filas (196 empresas × 3 años) COMPLETAS** (Decisión 033): las 297 filas
  de las 99 empresas nuevas (E098-E196) ya tienen `mr_ini/mr_fin/sus_ini/sus_fin`
  y `_mr.txt`/`_sus.txt` generados, con `sus_confianza` normalizado al mismo
  esquema que las 289 originales (`densidad`/`alta`/`densidad_baja`, sin casos
  `revisar` pendientes). Las 289 originales **no se han tocado** (estado
  validado de Decisiones 015-016 preservado).
- `sus_confianza` global (586): `densidad` 292, `alta` 233, `densidad_baja` 46,
  `media` 8, `aceptado_sin_financieros` 7 (tras corrección E174_NTGY_2023,
  Decisión 035).

### Corpus NLP (Fase 4D) — `data/processed/corpus.parquet`
- **1172 filas = 586 documentos × 2 secciones**, las **196 empresas** completas
  (97 originales + 99 ampliación). 586 = 588 − DIA 2022 y NEM 2022, excluidos por
  carecer de contenido ESG analizable (Decisión 010). Regenerado con
  `fase4_corpus.py` (resumible vía checkpoint, `nproc=1`) sobre las 297 filas
  nuevas, preservando las 578 filas originales (Decisión 034). QA completo +
  4 correcciones quirúrgicas (Decisión 035). ~263 MB.
- 196 empresas · años 2022/2023/2024 · **100% inglés** · mediana tokens: sus
  10.104 / mr 31.864.
- Columnas: `id, empresa, año, seccion, idioma, clean_text, tokens, confianza, n_tokens, n_chars`.
  - `seccion ∈ {mr, sus}`. **`mr` = management report SIN la subsección de sostenibilidad**
    (rango MR menos rango sostenibilidad, para evitar doble conteo, ya que `sus ⊂ mr`). `sus` =
    subsección de sostenibilidad aislada. Decisión 017.
  - `clean_text` → conserva mayúsculas y puntuación → para **BERT/FinBERT/ClimateBERT**.
  - `tokens` → lemas en minúscula, sin stopwords ni puntuación (spaCy `en_core_web_sm`) →
    para **LDA/TF-IDF**.
  - `confianza` → fiabilidad de la segmentación de sostenibilidad: `alta` 233, `densidad`
    292, `densidad_baja` 46, `media` 8, `aceptado_sin_financieros` 7 (sus, 586) +
    `mr` 483 / `mr_con_financieros` 103 (mr, 586). `densidad_baja` es la categoría
    menos fiable → filtrable en análisis de sensibilidad (Decisión 019).
- QA exhaustivo (`fase4_qa_corpus.py`): 0 problemas detectados (Decisión 035).

---


## 5. Cómo se construyó la Fase 4 (resumen para no re-derivar)

Pipeline en `scripts/extraction/` (ejecutado en orden):
`fase4_extraccion` → `fase4_idioma` → `fase4_mover_ingleses` → `fase4_ocr_remediar` →
`fase4_secciones` → `fase4_sanear_secciones` → `fase4_recalcular_limites` →
`fase4_sost_densidad` / `fase4_completar_cobertura` → `fase4_corpus`.

- **4A — Extracción** (`fase4_extraccion.py`): PyMuPDF. PDFs con **fuente embebida sin
  ToUnicode/cmap** (texto ilegible) → **OCR híbrido** (`fase4_ocr_remediar.py`): rasteriza con
  PyMuPDF a 300dpi y pasa por Tesseract **solo las páginas corruptas**, conservando texto nativo
  en el resto. Decisión 011. ⚠️ Colisión de ticker `BOL` (Boliden E010 / Bolloré E045) → los
  `.txt` se nombran con `id_empresa`: `{id}_{ticker}_{año}.txt`, no con ticker.
- **4B — Idioma** (`fase4_idioma.py`): `langdetect` con voto por 9 ventanas. Corpus homogeneizado
  a **inglés**: los 27 informes no-EN (fr/es) se **sustituyen por la versión oficial inglesa del
  emisor** (URD/Annual Report en EN), **nunca traducción automática** (rompería FinBERT/ClimateBERT
  EN-only). Decisión 012. Originales en `data/raw/_reemplazados_originales/`.
- **4C — Segmentación** (`fase4_secciones.py` + saneados): aísla (a) management report y
  (b) subsección de sostenibilidad. Método primario = **índice navegable del PDF** (`get_toc`);
  fallback = **densidad de vocabulario ESG por página**. Fin del MR = primer capítulo de
  **estados financieros**. Invariante `sus_fin ≤ mr_fin` (`sus ⊂ mr`). Decisiones 013–016.
  Re-ejecutado para las 99 empresas nuevas con flag `--nuevos` (no toca las 289 originales) en
  `fase4_secciones.py`, `fase4_sanear_secciones.py`, `fase4_recalcular_limites.py`,
  `fase4_sost_densidad.py`; 13 casos `revisar` resueltos con
  `fase4_revisar13.py` (densidad ESG). Decisión 033.
- **4D — Corpus** (`fase4_corpus.py`): construye `corpus.parquet`. Limpieza: cabeceras/pies
  repetidos, números de página, caracteres de control, párrafos rotos por columnas. Decisión 017.
  ⚠️ **Correr SIEMPRE con `nproc=1`** (por defecto): con `nproc>1` (8 copias de spaCy + 188M chars
  en RAM con disco lleno → sin swap) **reinicia el Mac**. Es resumible desde
  `data/processed/_corpus_partial.jsonl` (sin `--fresh`). `data/processed/` está en `.gitignore`.

---

## 6. Qué viene: Fase 5 (PLN) — plan

Granularidad: el corpus está a **nivel sección**; el troceo en **párrafos** (topic modeling) y
**frases** (FinBERT/ClimateBERT) es trabajo de Fase 5, sobre `clean_text`. Scripts irían en
`scripts/nlp/` (vacío) y resultados en `results/{tables,figures,models}/`.

**Decisiones tomadas (Decisiones 018-020):**
- **RQ3 (greenwashing)** → sección `sus` exclusivamente. Dec.019.
- **`densidad_baja`** (16 filas) → incluir en análisis principal + análisis de sensibilidad. Dec.019.
- **Hardware** → M4 MPS local, sin Colab necesario.
- **Diccionario ESRS** → `esrs_keywords.json` (v1.1, 11 cat., validado contra corpus). Dec.018.

**Bloques completados:**
- **5A** — ✅ descriptivos + cobertura ESRS (`fase5a_descriptivos.py`). Dec.021. Hallazgo RQ4: `sus` 10.9k→23.1k tokens 2022→2024. E1+S1 = categorías más cubiertas; E2 = menos.
- **5B (LDA)** — ✅ K=15 óptimo (Cv=0.684). Topics interpretados: T06=E1, T02=E2-E4, T13=E5, T00=S1, T04=S2-S3, T08=G1, T05/T09/T11=CSRD. Dec.022.
- **5B (BERTopic)** — ✅ 339 topics, 36.9% outliers. Triangulación LDA confirmada. Hallazgo RQ4: T7 "doble materialidad/IROs" crece ×8.2 (104→865 párrafos, 2022→2024); T16 "Taxonomía UE" ×1.8; T15 "riesgo climático físico" ×1.7. Dec.022.
- **5C** — ✅ sentimiento (`fase5c_sentimiento.py`). 285.509 frases · LM + ClimateBERT cascada
  (detector→sentiment/commitment/specificity) + FinBERT + FinBERT-ESG-9 → 289 docs
  (`5c_doc_agregado.csv`). Interpretación: `docs/fase5c_interpretacion.md`. Dec.024. Hallazgo
  RQ4: tono cada vez menos optimista 2022→2024 (LM positive ↓, FinBERT tono 0.202→0.153,
  ClimateBERT opportunity 21.5%→16.2%). Hallazgo RQ3: en frases climáticas caen a la vez
  oportunidad, compromiso y especificidad mientras sube el riesgo — a confirmar con GW_index
  (5D). Dec.024 documenta 3 incidencias técnicas (cuelgue MPS, suspensión Mac, caché
  tokenizer ESG-9) y sus fixes.
- **5D** — ✅ `GW_index` (`fase5d_gwindex.py`). Dec.025. `GW_index = z(hedging) +
  z(ratio_futuro_sin_cifra) − z(ratio_cuantitativo) − z(climate_specificity_spec)`, 289 docs.
  Hallazgo RQ4: GW_index sube netamente 2022→2024 (−0.196→+0.521), por hedging↑,
  especificidad↓ y **ratio cuantitativo↓** (hallazgo nuevo). Promesas vagas
  (`ratio_futuro_sin_cifra`) estables. Wilcoxon pareado 2022↔2024 p=0.021. Interpretación:
  `docs/fase5d_interpretacion.md`.
- **5E** — ✅ estadística inferencial (`fase5e_stats.py`). Dec.026. Panel 289 docs (5d_gwindex
  + n_tokens + sector/país/financieros). RQ2: GW_index/especificidad difieren por sector
  (Tech/Financials↑GW_index, Real Estate↑especificidad, p<0.001) y región (Centro↓ vs
  Nórdicos/UK). RQ3: 2 regresiones OLS-HC3 (R²≈0.21-0.22, VIF máx 2.6) — empresas grandes →
  menor GW_index (p=0.024); especificidad→tono **positivo** (p=0.003, no apoya hipótesis
  simple optimismo↔menos especificidad); año 2024 significativo en tono (p=0.013) pero no
  en GW_index tras controles (composicional). RQ4: test pareado 2022↔2024 confirma con
  significación formal GW_index↑, tono↓, riesgo↑, oportunidad↓, n_tokens↑ (todos p<0.05
  salvo especificidad marginal p=0.086). Interpretación: `docs/fase5e_interpretacion.md`.

Fase 5 (5A-5E) **COMPLETA sobre las 97 originales (289 docs)** — bloques arriba.

### Re-ejecución sobre el corpus ampliado (196 empresas, 586 docs)

**✅ COMPLETA (Decisión 036)**, re-ejecutada desde cero (no incremental):

- **5B**: nuevo K óptimo LDA = **25** (antes 15, Cv=0.706); BERTopic 578 topics
  (antes 339, 40.2% outliers). **Reinterpretación de topics pendiente**
  (`docs/fase5b_interpretacion.md` desactualizado).
- **5C**: 539.993 frases → `5c_doc_agregado.csv` (586 docs). Sin incidencias.
- **5D**: GW_index por año: 2022=−0.203, 2023=−0.168, **2024=+0.371** — mismo
  patrón que en la muestra original, más acentuado.
- **5E**: panel 586 docs (568 tras NaN financieros). RQ2 sector (GW_index
  H=57.4 p<0.0001), RQ4 pareado 194 empresas comunes 2022↔2024 (GW_index
  Δ=+0.547 p=0.005, tono Δ=−0.046 p<0.0001, todos significativos salvo
  especificidad p=0.126), RQ3 OLS (R²≈0.14-0.16, VIF máx 2.72) — confirma
  especificidad→tono positivo (p=0.003).
- `docs/fase5{a,b,c,d,e}_interpretacion.md` **actualizados** con los nuevos números
  (586 docs / 196 empresas).

Siguiente: Fase 7 (redacción del TFG).

## 6bis. Fase 6 (dashboard) — estado

✅ **Regenerado sobre 586 docs / 196 empresas** (Decisión 036). Decisión: dashboard como
**HTML estático autocontenido** (sin Streamlit/servidor), para desplegar en local abriendo
el fichero o sirviéndolo con cualquier servidor estático.

- `scripts/viz/preparar_dashboard.py`: precalcula `results/tables/dashboard/panel.csv`
  (panel maestro 586 docs = 5e_panel + cobertura ESRS + ESG-9) y `bertopic_doc_topics.csv`
  (tópico BERTopic dominante por documento, sobre 578 topics). Re-ejecutar si cambian los
  resultados de Fase 5.
- `scripts/viz/build_dashboard.py`: genera `results/dashboard/index.html` — dashboard con
  5 secciones (Overview, Explorador de empresa, Topics, Comparador, Resultados RQ),
  gráficos interactivos con Plotly.js (vía CDN) y datos embebidos como JSON inline.
- Uso: `conda run -n tfg-ade python scripts/viz/build_dashboard.py` y abrir
  `results/dashboard/index.html` en el navegador (las imágenes referencian
  `../figures/*.png` mediante ruta relativa).

**Referencias nuevas identificadas:**
- Suta et al. (2025) — *"Dictionary-based assessment of ESRS disclosure topics"*, Discover Sustainability 6, 146 — citar en Metodología para validar el enfoque dictionary-based ESRS.
- FinBERT-ESG-9-categories (HuggingFace `yiyanghkust`) — 9 categorías ESG, ~14k frases anotadas.

Nota de arranque detallada: `docs/retomar_fase5.md`.

---

## 7. Mapa de ficheros y docs

```
TFG-ADE/
├── GUÍA.MD                      # guía maestra de las 7 fases (paso a paso)
├── error.md                     # incidencia dataless/iCloud (recuperación)
├── CLAUDE.md                    # este fichero
├── data/
│   ├── raw/<País>/<TICKER>/     # PDFs originales (gitignored). Convención {TICKER}_{AÑO}_integrated.pdf
│   ├── interim/                 # .txt extraídos, secciones/, manifest, logs (gitignored)
│   │   ├── secciones/           # {id}_{ticker}_{año}_{mr,sus}.txt (578 ficheros)
│   │   └── secciones_manifest.csv   # rangos, método, sus_confianza por documento
│   ├── processed/corpus.parquet # CORPUS FINAL (gitignored, regenerable)
│   └── external/                # VERSIONADO (csv muestra, normativa/, diccionarios/)
│       ├── empresas_muestra.csv     # dataset maestro 291 filas (97×3)
│       ├── tracking_descargas.csv   # estado descargas Fase 3
│       ├── normativa/               # PDFs CSRD/ESRS/Taxonomía/SFDR/NFRD
│       ├── diccionarios/LoughranMcDonald_MasterDictionary.csv
      ├── diccionarios/esrs_keywords.json          # ★ diccionario ESRS 11 cat. (Dec.018, v1.1)
      └── diccionarios/EFRAG_ESRS_XBRL_Taxonomy_Annex1.xlsx  # referencia oficial EFRAG (no keywords)
├── scripts/
│   ├── fase2_*.py, completar_isins.py     # muestra
│   ├── fase3_*.py                          # descarga/registro
│   ├── extraction/fase4_*.py               # pipeline Fase 4 (ver §5)
│   ├── nlp/                                 # VACÍO — Fase 5
│   └── viz/                                 # VACÍO — Fase 5/6
├── results/{tables,figures,models}/        # VACÍOS — salidas Fase 5+
└── docs/
    ├── decisiones.md            # ★ FUENTE DE VERDAD: Decisiones 001–017
    ├── retomar_fase5.md         # nota de arranque Fase 5
    ├── auditoria_sostenibilidad.md  # clasificación A–E de los 291 PDFs por contenido ESG
    ├── notas_normativa.md       # CSRD/ESRS/Taxonomía/SFDR/NFRD + los 12 ESRS
    ├── notas_literatura.md      # papers fundacionales + matriz de literatura
    ├── notas_muestra.md         # ⚠️ parcialmente DESFASADO (describe v1: 60 empresas/2 años).
    │                            #    Para la muestra vigente manda decisiones.md (97×3)
    ├── fase4_idiomas.md, fase4_informes_ingles.md  # detección idioma + sustituciones EN
    ├── guia_correcciones_pdfs.md, progresopdf.md   # historia de correcciones/descargas Fase 3
    └── links.md                 # todos los enlaces (normativa, modelos HF, papers, datos)
```

---

## 8. Git

Rama principal `main`. Usuario git: `iTzPauG` / `pgesparterpubli@gmail.com`. Commits descriptivos
en español por fase (p. ej. *"Fase 4D: construcción de corpus.parquet (Decisión 017)"*). No se
versionan `data/raw|interim|processed` ni `results/models/*` (ver `.gitignore`). Commitear o
hacer push solo cuando el usuario lo pida.
</content>
