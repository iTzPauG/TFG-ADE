# Fase 4B — Detección de idioma de los informes

> Generado el 2026-06-01 por `scripts/extraction/fase4_idioma.py`.
> Detección con `langdetect` por **voto de 9 ventanas** de 3000 caracteres repartidas por cada documento (robusto a portadas/secciones con fuentes corruptas).
> Corpus: **289 informes** (97 empresas × 3 años − DIA 2022 y NEM 2022 descartados).

## Distribución de idiomas

| Idioma | Código | Informes | % |
|--------|--------|---------:|----:|
| Inglés | `en` | 289 | 100.0% |

## Idiomas por país

| País | Idiomas (nº informes) |
|------|----------------------|
| Austria | en×6 |
| Belgium | en×9 |
| Denmark | en×9 |
| Finland | en×9 |
| France | en×45 |
| Germany | en×41 |
| Ireland | en×6 |
| Italy | en×15 |
| Netherlands | en×18 |
| Norway | en×12 |
| Spain | en×26 |
| Sweden | en×21 |
| Switzerland | en×27 |
| United Kingdom | en×45 |

## Informes NO en inglés (0 de 289)

_Todos los informes están en inglés._

## ⚠ Calidad de extracción: 0 informe(s) con texto corrupto

Detectados por baja densidad de palabras función reales y/o exceso de caracteres de control → fuentes con CMap rota (sin mapa ToUnicode). El idioma mostrado es el de las secciones legibles. **Requiere remediación 4A** (OCR con Tesseract o re-descarga de una copia con capa de texto correcta).

_Ninguno: todas las extracciones son legibles._

## Voto de idioma no unánime entre ventanas: 5

Fracción de ventanas que apoyan el idioma mayoritario < 1.0. Puede indicar documentos bilingües o con secciones corruptas/tabulares.

| id | ticker | año | idioma | % ventanas de acuerdo |
|----|--------|-----|--------|----------------------:|
| E005 | CABK | 2022 | `en` | 0.889 |
| E005 | CABK | 2023 | `en` | 0.889 |
| E005 | CABK | 2024 | `en` | 0.889 |
| E017 | SKA B | 2024 | `en` | 0.889 |
| E079 | ENEL | 2023 | `en` | 0.889 |

## Implicación para la decisión 4B (traducir vs. multilingüe)

- **100.0%** del corpus ya está en inglés.
- **0** informes requerirían traducción si se opta por herramientas English-only (Loughran-McDonald, FinBERT — ver Decisión 001).
- Alternativa: modelos multilingües (XLM-RoBERTa, mBERT) que evitan la traducción.

_Decisión pendiente de confirmar con el estudiante/tutor._
