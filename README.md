# TFG-ADE

**Comunicación corporativa y estrategias de gestión en los informes de sostenibilidad de
las empresas europeas: un análisis de contenido mediante técnicas de inteligencia
artificial.**

TFG (ADE, Universidad de Valencia). Análisis con técnicas de PLN (FinBERT, ClimateBERT,
diccionario Loughran-McDonald, diccionario ESRS propio) de las secciones de sostenibilidad
de 97 empresas del STOXX Europe 600 (2022-2024), bajo el marco normativo CSRD/ESRS.

Contexto completo del proyecto, decisiones metodológicas y estado del pipeline en
[`CLAUDE.md`](CLAUDE.md), [`GUÍA.MD`](GUÍA.MD) y [`docs/decisiones.md`](docs/decisiones.md).

## Estado del pipeline

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1-4 | Marco teórico, muestra, recolección, extracción/limpieza | ✅ |
| 5 | Análisis PLN (descriptivos, topics, sentimiento, GW_index, estadística) | ✅ |
| 6 | Dashboard Streamlit + reproducibilidad | 🔄 |
| 7 | Redacción del TFG | ⬜ |

## Entorno

```bash
conda env create -f environment.yml
conda activate tfg-ade
```

(o `conda run -n tfg-ade <comando>`)

## Dashboard (Fase 6)

El dashboard explora los resultados de la Fase 5 (5A-5E) sobre el panel de 289 documentos
(secciones de sostenibilidad, 97 empresas × 3 años).

```bash
conda run -n tfg-ade streamlit run app/Home.py
```

Páginas:
- **Overview** — descriptivos del corpus, distribución de tokens, cobertura ESRS
- **Explorador de empresa** — evolución de tono, especificidad, GW_index y tópicos por empresa
- **Topics** — modelos LDA (K=15) y BERTopic (339 tópicos)
- **Comparador** — comparación de métricas clave entre empresas
- **Resultados RQ** — hallazgos por pregunta de investigación (RQ1-RQ4)

Antes de lanzar el dashboard, regenera las tablas precalculadas si cambian los resultados
de Fase 5:

```bash
conda run -n tfg-ade python scripts/viz/preparar_dashboard.py
```

## Estructura del repositorio

```
data/
├── external/        # datos versionados (muestra, diccionarios, normativa)
├── raw/              # PDFs originales (no versionado)
├── interim/          # textos extraídos y secciones (no versionado)
└── processed/        # corpus.parquet (no versionado, regenerable)
scripts/
├── fase2_*.py         # construcción de la muestra
├── fase3_*.py         # descarga/registro de informes
├── extraction/         # pipeline Fase 4 (extracción y limpieza)
├── nlp/                 # pipeline Fase 5 (PLN)
└── viz/                  # precálculo para el dashboard (Fase 6)
app/
├── Home.py             # punto de entrada del dashboard Streamlit
├── pages/                # páginas del dashboard
└── utils/                # carga de datos cacheada
results/
├── tables/              # tablas de resultados (Fase 5)
├── figures/              # figuras (Fase 5)
└── models/                # modelos LDA/BERTopic
docs/                    # decisiones metodológicas e interpretación de resultados
```

## ⚠️ Ficheros "dataless" (iCloud)

El repo está en `~/Documents` y se sincroniza con iCloud. Algunos ficheros pueden
evacuarse a iCloud y leer 0 bytes (no es corrupción). Ver `CLAUDE.md` §3 y
`docs/retomar_fase5.md` para el procedimiento de recuperación con `brctl download`.
