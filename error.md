# Incidencia: ficheros "dataless" (evacuados a iCloud) — NO es corrupción

**Fecha:** 2026-06-09

## Qué pasó
Muchos ficheros del repo leen como **0 bytes aunque `stat` muestra su tamaño real**.
Causa real: están marcados `compressed, dataless` → macOS los **evacuó a iCloud**
("Optimize Mac Storage") porque el **disco está al 92% (solo ~17 GB libres)**.
El repo está en `~/Documents`, que se sincroniza con iCloud.

**Los datos NO están perdidos** — están en iCloud y, los ficheros versionados, en git
(el `git fsck --full` salió limpio: object DB intacto). No es culpa de los scripts ni
del `kill -9`.

## Alcance de la evacuación (a 2026-06-09)
- **PDFs `data/raw`: 279/324 dataless**
- **Secciones `data/interim/secciones/*.txt`: 509/578 dataless**
- **8-9 scripts `scripts/extraction/*.py` + `scripts/completar_isins.py`**
- `data/interim/idiomas.csv`, 1 caché OCR (`E089_ADEN_2023.pages.txt`), 6 `.txt` nivel-1
- INTACTOS: `secciones_manifest.csv` (289 filas), `data/external/*.csv` (salvo el borrado),
  `docs/`, la mayoría de scripts no-fase4.

## Cómo se detecta un fichero dataless
```bash
ls -lO ruta/al/fichero      # muestra el flag "dataless"
# o en python: os.path.getsize(f) > 0  pero  len(open(f,'rb').read()) == 0
```

## RECUPERACIÓN (acciones del usuario)
1. **Liberar espacio en disco** (crítico; si sigue lleno, macOS volverá a evacuar).
2. **Desactivar "Optimizar almacenamiento del Mac"**: Ajustes del Sistema → Apple ID →
   iCloud → iCloud Drive → desactivar "Optimizar almacenamiento", para que los ficheros
   se queden en local.
3. **Materializar (re-descargar) la carpeta**: en Finder, clic derecho sobre `TFG-ADE`
   (o `data/raw`) → **"Descargar ahora"**. Alternativa por terminal:
   ```bash
   find data -type f -exec cat {} > /dev/null \;   # fuerza la descarga al leerlos
   ```
   (Requiere conexión y espacio suficiente; los PDFs son varios GB.)
4. **Ficheros versionados en git** (scripts, `empresas_muestra.csv`): si quedan dataless,
   borrarlos y recrearlos —git no reescribe si el tamaño coincide—:
   ```bash
   rm -f scripts/completar_isins.py data/external/empresas_muestra.csv
   rm -f .git/index.lock
   git checkout -f HEAD -- scripts/ data/external/empresas_muestra.csv
   ```
   (Quitar `.git/index.lock` huérfano antes; cada `git` fallido lo deja.)

## Lo NO versionado (regenerable, NO perdido si iCloud descarga)
- `data/interim/secciones/*.txt`: se regeneran desde `secciones_manifest.csv` (intacto) +
  los PDFs, re-ejecutando la extracción de secciones (4C).
- `data/interim/idiomas.csv`: re-ejecutar `fase4_idioma.py` (todos los docs son `en`).
- `corpus.parquet`: NO se llegó a generar (el build 4D crasheó al leer un CSV dataless).

## Estado al interrumpir
- Bloque 4C estaba COMPLETO y verificado antes de la evacuación (289/289, ver Decisión 016).
- Bloque 4D (script `scripts/extraction/fase4_corpus.py`, Decisión 017) escrito pero
  **sin ejecutar con éxito** por la evacuación.
- `data/external/empresas_muestra.csv` quedó borrado en la recuperación; **recrear con el
  comando git de arriba** (está en HEAD).

## Siguiente paso (cuando los ficheros estén materializados y haya disco)
1. Recrear `empresas_muestra.csv` y scripts desde git (comando de arriba).
2. Regenerar secciones + idiomas si siguen dataless.
3. Ejecutar `python scripts/extraction/fase4_corpus.py` (build 4D paralelo).
