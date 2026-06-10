# Nota para retomar en Fase 5 (PLN)

## Estado de Fase 4 al cerrar (2026-06-09)
Fase 4 **COMPLETA** (4A → 4B → 4C → 4D). Commit `42de410`.

`data/processed/corpus.parquet`: **578 filas** (289 `sus` + 289 `mr`), 97 empresas,
años 2022-2024, 100% inglés, 0 filas vacías, 113 MB.
Columnas: `id, empresa, año, seccion, idioma, clean_text, tokens, confianza, n_tokens, n_chars`.
- `clean_text` conserva mayúsculas y puntuación → para BERT/FinBERT/ClimateBERT.
- `tokens` = lemas en minúscula sin stopwords ni puntuación (spaCy `en_core_web_sm`) → para LDA/TF-IDF.

## Ficheros dataless (evacuados a iCloud) — re-materializar ANTES de correr nada
Los `.txt` de `data/interim/secciones/` y el `data/processed/corpus.parquet` se
**re-evacúan a iCloud** cada vez que el disco se llena o el Mac se reinicia. Si un
script de Fase 5 (topic modeling, FinBERT/ClimateBERT) los lee como **0 bytes**, NO
están corruptos: están `dataless`. Re-materializar primero:

```bash
brctl download data/processed/corpus.parquet
find data/interim/secciones -maxdepth 1 -name '*.txt' -exec brctl download {} \;
# esperar a que `stat -f '%Sf' <fichero>` deje de decir "dataless"
```

Detectar sin disparar descarga (leer un dataless **bloquea** el proceso):
`stat -f '%Sf' fichero` → muestra `dataless` en los flags. Detalle completo en `error.md` (raíz).

## Recordatorio del build 4D (si hay que regenerar el corpus)
Correr SIEMPRE con `nproc=1` (por defecto):

```bash
python -u scripts/extraction/fase4_corpus.py
```

- **NO usar `nproc>1`**: reinicia el Mac (8 copias del modelo spaCy + 188M chars en RAM
  con disco lleno → sin swap → kernel panic).
- Es **resumible**: si se corta, re-lanzar SIN `--fresh` continúa desde
  `data/processed/_corpus_partial.jsonl`.
- `data/processed/` está en `.gitignore`: el corpus **no** se versiona, hay que regenerarlo
  o recuperarlo de iCloud.

## Fase 5 — Estado y decisiones (2026-06-09)

Fase 5 **EN CURSO**. Decisiones 018-020 tomadas y registradas en `docs/decisiones.md`.

### Decisiones clave ya tomadas

| Dec. | Qué | Detalle |
|------|-----|---------|
| 018 | Diccionario ESRS | `data/external/diccionarios/esrs_keywords.json` v1.1, 11 categorías, construido manualmente + validado con EFRAG XBRL. Citar Suta et al. (2025) como ref. metodológica. |
| 019 | Sección para RQ3 | Usar solo `sus` (289 filas). `densidad_baja` (16 filas) incluida en análisis principal como limitación; añadir análisis de sensibilidad sin ellas. Filtro: `df[df['seccion']=='sus']`, col `fiable = confianza != 'densidad_baja'`. |
| 020 | Clasificadores 5C | FinBERT-ESG-9-categories (`yiyanghkust/finbert-esg-9-categories`) añadido como clasificador complementario. Mapping aproximado ESRS: E1≈Climate Change, G1≈Corporate Governance, etc. No cubre E5 ni S4 — documentar como limitación. |

### Arquitectura Fase 5

```
5A  Descriptivos + cobertura ESRS   →  scripts/nlp/fase5a_descriptivos.py   ← SIGUIENTE
5B  LDA + BERTopic (párrafos)       →  scripts/nlp/fase5b_topics.py
5C  Loughran-McDonald + FinBERT + ClimateBERT×4 + FinBERT-ESG-9  →  scripts/nlp/fase5c_sentiment.py
5D  GW_index                        →  scripts/nlp/fase5d_gwindex.py
5E  Estadísticas + regresiones      →  scripts/nlp/fase5e_stats.py
```

### Recursos y referencias

- **Diccionario ESRS:** `data/external/diccionarios/esrs_keywords.json` v1.1 — 11 categorías, búsqueda por `str.contains` sobre `clean_text.lower()`
- **EFRAG XBRL Taxonomy:** `data/external/diccionarios/EFRAG_ESRS_XBRL_Taxonomy_Annex1.xlsx` — taxonomía estructural XBRL, NO keywords; usar solo como referencia/cita
- **Suta et al. (2025):** "Dictionary-based assessment of ESRS disclosure topics", Discover Sustainability 6, 146 — referencia metodológica principal para enfoque diccionario
- **FinBERT-ESG-9-categories:** `yiyanghkust/finbert-esg-9-categories` — 9 categorías ESG, ~14k frases anotadas; instalar con `pip install transformers`
- **Hardware:** MacBook Air M4, 24 GB unified memory, MPS disponible → todos los modelos corren localmente (`device="mps"`)

### Cobertura ESRS validada (diccionario v1.1, media sobre 289 docs `sus`)

| Categoría | Cobertura media |
|-----------|----------------|
| E1 | 0.503 |
| S1 | 0.487 |
| ESRS2 | 0.394 |
| G1 | 0.358 |
| E5 | 0.320 |
| S2 | 0.264 |
| E3 | 0.236 |
| S4 | 0.220 |
| E4 | 0.204 |
| S3 | 0.192 |
| E2 | 0.152 |

### ✅ 5A COMPLETO — `scripts/nlp/fase5a_descriptivos.py` (Decisión 021)

Outputs en `results/tables/` y `results/figures/`:
- `5a_descriptivos_corpus.csv` — stats por sección/año
- `5a_cobertura_esrs.csv` — matriz 289 sus × 11 categorías
- `5a_cobertura_esrs_año.csv` — evolución 2022→2024
- `5a_tfidf_{sus,mr}.csv` + `5a_ngrams_top.csv` — léxico dominante
- `5a_heatmap_esrs.png`, `5a_distribucion_tokens.png`, `5a_cobertura_esrs_año.png`, `5a_tfidf_top_sus.png`

**Hallazgos clave:**
- `sus` n_tokens: 2022=10.947 → 2023=14.556 → 2024=**23.068** (+111%) → señal fuerte RQ4 CSRD
- `mr` estable (~36-40k): el crecimiento es específico de la sección de sostenibilidad
- Mejor cobertura ESRS: **E1** (0.503) y **S1** (0.487); peor: **E2** (0.150) y **S3** (0.192)
- `densidad_baja` confirma coberturas estructuralmente bajas (E1=0.124 vs 0.573 `alta`)

### 5B — Topic modeling ✅ COMPLETO

`scripts/nlp/fase5b_topics.py` — LDA baseline + BERTopic sobre 131.140 párrafos de `clean_text` (sus).
Interpretación completa en `docs/fase5b_interpretacion.md`. Resultados en Decisión 022.

- **LDA**: K=15 (Cv=0.684). 15 topics interpretables, mapeados a ESRS.
- **BERTopic**: 339 topics, 36.9% outliers. Embeddings cacheados en `results/models/bertopic_sus_embeddings.npy`.
- **Hallazgo RQ4**: topic "doble materialidad/IROs" crece ×8.2 (104→865 párrafos) 2022→2024 —
  señal textual más fuerte de transición NFRD→CSRD del proyecto.

### 5C — Sentimiento y especificidad ✅ COMPLETO

`scripts/nlp/fase5c_sentimiento.py` (Decisión 024). Granularidad: **285.509 frases** (no
párrafos) sobre `clean_text` de `sus` (segmentación spaCy sentencizer, ≥4 palabras).

Pipeline completo (6 pasos): LM (7 ratios) → ClimateBERT cascada (`climate-detector` →
`sentiment`/`commitment`/`specificity` sobre 118.321 frases climáticas, 41.4%) → FinBERT
(`ProsusAI/finbert`) → FinBERT-ESG-9 (`yiyanghkust/finbert-esg-9-categories`) → agregación
→ `5c_doc_agregado.csv` (289 docs) + 4 figuras en `results/figures/5c_*`.

Tomó 625.7 min (~10h25) por 3 incidencias técnicas documentadas y resueltas en Decisión 024
(cuelgue MPS por fragmentación de memoria al cargar FinBERT, suspensión nocturna del Mac
resuelta con `caffeinate`, caché de tokenizer ESG-9 incompleta detectada y corregida —
re-ejecución de los pasos `esg9`+`agregar`).

**Hallazgos clave:**
- Tono cada vez menos optimista 2022→2024, triangulado por 3 modelos: LM positive
  0.0149→0.0138, FinBERT tono 0.202→0.153, ClimateBERT opportunity 21.5%→16.2%.
- En frases climáticas, caen a la vez oportunidad, compromiso explícito (34.5%→27.5%) y
  especificidad (28.1%→25.7%) mientras sube el riesgo (10.4%→17.2%) — relevante para RQ3,
  a confirmar con `GW_index` (5D).
- FinBERT-ESG-9 confirma centralidad de Climate Change/E1 (~22-23% estable), triangulando
  con 5A y 5B.

Documentación completa: `docs/fase5c_interpretacion.md`. Resultados y las 3 incidencias en
Decisión 024 (`docs/decisiones.md`).

### 5D — GW_index ✅ COMPLETO

`scripts/nlp/fase5d_gwindex.py` (Decisión 025). `GW_index = z(hedging_ratio) +
z(ratio_futuro_sin_cifra) − z(ratio_cuantitativo) − z(climate_specificity_spec)`, sobre
los 289 docs `sus`. Dos componentes nuevos (`ratio_cuantitativo`, `ratio_futuro[_sin_cifra]`)
calculados con regex sobre `5c_frases.parquet` (285.509 frases).

**Hallazgos clave:**
- GW_index sube netamente 2022→2024: −0.196 → −0.329 → **+0.521**, impulsado por
  hedging↑ (+29%), especificidad climática↓ (−8.5%) y **ratio cuantitativo↓** (−5.6%,
  hallazgo nuevo no visto en 5A-5C).
- `ratio_futuro_sin_cifra` (promesas vagas) estable (0.130→0.125): el deterioro no es
  "más promesas vagas" sino "menos sustancia" en general.
- Robusto a exclusión de `densidad_baja` (Dec.019). Test pareado 2022↔2024 (95 empresas):
  Wilcoxon p=0.021.
- GW_index correlaciona con `climate_sentiment_risk` (r=0.50), negativo con
  `opportunity`/`commitment`.

Documentación completa: `docs/fase5d_interpretacion.md`. Resultados en Decisión 025
(`docs/decisiones.md`). Output: `results/tables/5d_gwindex.csv` (289 docs) + 3 figuras
`5d_*`.

### 5E — Estadística inferencial ✅ COMPLETO

`scripts/nlp/fase5e_stats.py` (Decisión 026). Panel de 289 docs `sus`
(`5e_panel.csv`) = `5d_gwindex.csv` + `n_tokens` + sector/país/financieros
(`empresas_muestra.csv`). País (14 niveles, varios n<5) → KW descriptivo por país +
variable `region` (4 zonas) como control en regresiones.

**Hallazgos clave:**
- **RQ2**: GW_index y especificidad climática difieren significativamente por sector
  (Tech/Financials = más GW_index/menos específicos; Real Estate = lo contrario, todos
  p<0.001) y por país/región (Centro Europa, sobre todo Francia/Italia, GW_index más
  bajo que Nórdicos/UK&Irlanda).
- **RQ3**: Reg1 (GW_index ~ tamaño+sector+región+año, R²=0.223): empresas más grandes →
  menor GW_index (p=0.024); Financials/Technology más alto, Real Estate más bajo
  (p<0.05); año 2024 NO significativo tras controles (p=0.104, efecto composicional).
  Reg2 (tono ~ especificidad+controles, R²=0.206): especificidad → tono **positivo**
  (p=0.003, no apoya hipótesis simple "optimismo↔menos especificidad"); año 2024
  significativo y negativo (p=0.013, robusto). VIF máx=2.6 (sin multicolinealidad).
- **RQ4**: test pareado 2022↔2024 (95 empresas) confirma con significación formal:
  GW_index↑ (Wilcoxon p=0.021), tono↓ (p=0.0003), riesgo climático↑ (p<0.0001),
  oportunidad↓ (p=0.0006), n_tokens↑ (p<0.0001); especificidad↓ marginal (p=0.086).

⚠️ Nota técnica: VIF requiere mantener el intercepto en la matriz de diseño (sin él,
`log_cap` daba VIF≈15-23 espurio).

Documentación completa: `docs/fase5e_interpretacion.md`. Resultados en Decisión 026
(`docs/decisiones.md`). Outputs: `5e_panel.csv`, `5e_kruskal_*.csv`,
`5e_pareado_2022_2024.csv`, `5e_regresion{1,2}_{gwindex,tono}.csv` +
`5e_regresion{1,2}_vif.csv` + 3 figuras `5e_*`.

---

## Fase 5 (PLN) — COMPLETA (5A-5E). Siguiente: Fase 6 (dashboard Streamlit + reproducibilidad)
