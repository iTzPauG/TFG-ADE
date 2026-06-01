# Fase 4 — Versiones en inglés de los informes no-ingleses

> Objetivo: sustituir los 27 informes no-ingleses (25 fr + 2 es) por su versión oficial en inglés
> para mantener la Decisión 001 (FinBERT/ClimateBERT/LM, English-only) sin traducción automática.
> Verificado con `curl` (HEAD/range): `200/206 application/pdf` = PDF válido descargable.

## ✅ Encontrados con enlace directo confirmado (12 informes)

| id | empresa | año | URL inglesa (verificada) |
|----|---------|-----|--------------------------|
| E045 | Bolloré | 2022 | https://www.bollore.com/wp-content/uploads/2023/04/0428_boll22t023_urd_gb_2022.pdf |
| E045 | Bolloré | 2023 | https://www.bollore.com/wp-content/uploads/2024/05/0502_boll23t029_urd_gb_2023_mel.pdf |
| E045 | Bolloré | 2024 | https://www.bollore.com/wp-content/uploads/2025/05/0520_boll24t035_urd_gb_2024_mel.pdf |
| E018 | Vinci | 2022 | https://www.vinci.com/publi/vinci/vinci-2022-universal-registration-document.pdf |
| E018 | Vinci | 2023 | https://www.vinci.com/publi/vinci/vinci-2023-universal-registration-document.pdf |
| E018 | Vinci | 2024 | https://www.vinci.com/publi/vinci/vinci-2024-universal-registration-document.pdf |
| E047 | Safran | 2024 | https://www.safran-group.com/sites/default/files/2025-04/2024-safran-universal-registration-document.pdf |
| E060 | Gecina | 2022 | https://www.gecina.fr/sites/default/files/2023-03/gecina_urd_2022_universal_registration_document_en_e-accessible.pdf |
| E060 | Gecina | 2024 | https://www.gecina.fr/sites/default/files/2025-02/gecina_universal_registration_document_urd_2024.pdf |
| E033 | Wendel | 2023 | https://www.wendelgroup.com/wp-content/uploads/2024/04/wendel-2023-urd-en-april2024.pdf |
| E033 | Wendel | 2024 | https://www.wendelgroup.com/wp-content/uploads/2025/04/wen-2024-urd-en-v-mel-25-04-04.pdf |
| E037 | Pernod Ricard | 2023 | https://www.pernod-ricard.com/sites/default/files/inline-files/Universal%20Registration%20Document%202023_VUK%20pdf..pdf (FY22/23) |

## ⚠ Versión inglesa CONFIRMADA que existe, pero requiere localizar el fichero exacto (búsqueda manual)

Para estos, la empresa publica el documento en inglés, pero no obtuve un enlace directo
descargable (página IR sin PDF directo, descarga bloqueada con 403, o año ambiguo).

| id | empresa | año(s) | Dónde buscarlo | Nota |
|----|---------|--------|----------------|------|
| E024 | Kering | 2022, 2023, 2024 | kering.com → Finance / Regulated Information (EN) | publica URD en inglés y francés |
| E019 | Bouygues | 2022, 2023, 2024 | bouygues.com/en/regulated-information | descarga directa bloqueada (403); sufijo `-va` = version anglaise |
| E073 | Orange | 2023, 2024 | orange.com/en/regulated-information | URD en inglés disponible |
| E004 | Valeo | 2022, 2023 | valeo.com → Regulated Information (sufijo `_uk`) | 2022 también en Euronext |
| E060 | Gecina | 2023 | gecina.fr → Investors / Financial reports | (2022 y 2024 ya encontrados) |
| E033 | Wendel | 2022 | wendelgroup.com → archivo URD | (2023 y 2024 ya encontrados) |
| E026 | Repsol | 2022, 2023 | repsol.com/en → Annual reports / Integrated Management Report | versión inglesa = "Integrated Management Report" |
| E020 | Eiffage | 2022 | eiffage.com/en/finance/universal-registration-document | confirmar que el fichero es el de 2022 (patrón `Eiffage_URD_2022_EN.pdf`) |

## Resumen

- **Todas las 12 empresas publican versión oficial en inglés** de todos los años → ningún informe queda sin alternativa inglesa.
- 12 informes con enlace directo verificado (descargables ya).
- 15 informes: versión inglesa existe, falta capturar el PDF exacto (lista de arriba para búsqueda manual).
