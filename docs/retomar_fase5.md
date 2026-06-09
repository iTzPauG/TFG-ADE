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

## Siguiente: Fase 5
Topic modeling sobre **párrafos** (Paso 5.8) y FinBERT/ClimateBERT sobre **frases**
(Pasos 5.11-5.13), troceando `clean_text`. La granularidad sección→párrafo/frase es de Fase 5.
