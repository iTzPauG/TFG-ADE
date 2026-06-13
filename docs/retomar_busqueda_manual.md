# Búsqueda/descarga manual de informes faltantes (ampliación 196) — COMPLETADO

Estado a fecha 2026-06-12. Sesión cerrada: se completó la integración de los 156 PDFs
pendientes de los lotes 1-5 (`data/raw/_staging_ampliacion/`, ya eliminada) a su
ubicación definitiva `data/raw/<País>/<TICKER>/<TICKER>_<año>_integrated.pdf` y se
actualizó `data/external/tracking_descargas.csv` (script
`scripts/fase3_integrar_ampliacion.py`).

## Resultado final (588 filas = 196 empresas × 3 años)

- `descargado`: 572
- `descartado`: 2 (DIA 2022, NEM 2022 — Decisión 010, sin contenido ESG analizable)
- `problema`: 14 — de las 99 empresas nuevas (E098-E196), quedan **8 informes
  pendientes** (ver tabla abajo). Las otras 6 filas `problema` corresponden a la
  muestra original (97 empresas) y son anteriores a esta ampliación.

## Pendientes — requieren acción del usuario o reintento posterior

| Empresa | Ticker | Año | Motivo | URL conocida |
|---|---|---|---|---|
| Saint-Gobain | SGO | 2023 | Cloudflare bloquea curl (403 cf-mitigated) | https://www.saint-gobain.com/sites/saint-gobain.com/files/media/document/2023%20-%20URD%20%20SAINT-GOBAIN%20-%20ENG_accessible.pdf |
| Saint-Gobain | SGO | 2024 | Cloudflare bloquea curl (403 cf-mitigated) | https://www.saint-gobain.com/sites/saint-gobain.com/files/media/document/Saint-Gobain_2024_DEU_VA-.pdf |
| Moncler | MONC | 2022/2023/2024 | monclergroup.com en mantenimiento completo — reintentar más adelante | — |
| Haleon | HLI | 2024 | haleon.com bloquea curl (403/404 AWS WAF) | https://www.haleon.com/content/dam/haleon/corporate/documents/investors/oar-2024/haleon-annual-report-and-form-20F-2024.pdf.downloadasset.pdf |
| Delivery Hero | DASH | 2022 | sin URL fiable encontrada (IR solo desde 2024, sustainabilityreports.com 403) — requiere búsqueda adicional | — |
| Severn Trent | SVT | 2024 | severntrent.com bloquea curl (403 AWS WAF) | https://www.severntrent.com/content/dam/stw-plc/shareholder-resources/2024-reports/severn-trent-ara-2024-bookmarked-web-full-report.pdf |

Para Saint-Gobain, Haleon y Severn Trent las URLs son correctas y verificadas — solo
falta descargarlas a mano desde un navegador (el WAF no bloquea sesiones de
navegador real) y guardarlas como `data/raw/<País>/<TICKER>/<TICKER>_<año>_integrated.pdf`,
luego marcar `estado=descargado` en `tracking_descargas.csv`.

## Siguiente paso

Con 196/196 empresas (588 filas, 580 descargado + 2 descartado = 582 utilizables,
8 pendientes), valorar si pasar a Fase 4 (extracción/segmentación) para las 99
empresas nuevas con lo ya descargado, o esperar a resolver los 8 pendientes
primero. CLAUDE.md y GUÍA.MD aún describen el estado anterior a la ampliación
(97 empresas/291 filas) — actualizar cuando se decida cómo proceder con Fase 4/5
sobre el corpus ampliado.
