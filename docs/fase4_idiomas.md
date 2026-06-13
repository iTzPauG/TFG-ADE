# Fase 4B — Detección de idioma de los informes

> Generado el 2026-06-13 por `scripts/extraction/fase4_idioma.py`.
> Detección con `langdetect` por **voto de 9 ventanas** de 3000 caracteres repartidas por cada documento (robusto a portadas/secciones con fuentes corruptas).
> Corpus: **586 informes** (196 empresas × 3 años − DIA 2022 y NEM 2022 descartados).

## Distribución de idiomas

| Idioma | Código | Informes | % |
|--------|--------|---------:|----:|
| Inglés | `en` | 586 | 100.0% |

## Idiomas por país

| País | Idiomas (nº informes) |
|------|----------------------|
| Austria | en×12 |
| Belgium | en×21 |
| Denmark | en×9 |
| Finland | en×15 |
| France | en×84 |
| Germany | en×86 |
| Ireland | en×6 |
| Israel | en×3 |
| Italy | en×42 |
| Luxembourg | en×3 |
| Netherlands | en×45 |
| Norway | en×24 |
| Portugal | en×6 |
| Spain | en×50 |
| Sweden | en×33 |
| Switzerland | en×57 |
| United Kingdom | en×90 |

## Informes NO en inglés (0 de 586)

_Todos los informes están en inglés._

## ⚠ Calidad de extracción: 0 informe(s) con texto corrupto

Detectados por baja densidad de palabras función reales y/o exceso de caracteres de control → fuentes con CMap rota (sin mapa ToUnicode). El idioma mostrado es el de las secciones legibles. **Requiere remediación 4A** (OCR con Tesseract o re-descarga de una copia con capa de texto correcta).

_Ninguno: todas las extracciones son legibles._

## Voto de idioma no unánime entre ventanas: 7

Fracción de ventanas que apoyan el idioma mayoritario < 1.0. Puede indicar documentos bilingües o con secciones corruptas/tabulares.

| id | ticker | año | idioma | % ventanas de acuerdo |
|----|--------|-----|--------|----------------------:|
| E005 | CABK | 2022 | `en` | 0.889 |
| E005 | CABK | 2023 | `en` | 0.889 |
| E005 | CABK | 2024 | `en` | 0.889 |
| E017 | SKA B | 2024 | `en` | 0.889 |
| E155 | VNA | 2022 | `en` | 0.889 |
| E155 | VNA | 2023 | `en` | 0.889 |
| E184 | SPSN | 2022 | `en` | 0.889 |

## Implicación para la decisión 4B (traducir vs. multilingüe)

- **100.0%** del corpus ya está en inglés.
- **0** informes requerirían traducción si se opta por herramientas English-only (Loughran-McDonald, FinBERT — ver Decisión 001).
- Alternativa: modelos multilingües (XLM-RoBERTa, mBERT) que evitan la traducción.

_Decisión pendiente de confirmar con el estudiante/tutor._
