# Fase 3 — Guía para completar manualmente

> Estado a 2026-05-29: **291/291 PDFs descargados (100%)**
> Colección completa. Ningún pendiente.

---

## Resumen de sesiones

### Sesión 2026-05-28 (automática)
Se descargaron automáticamente 4 nuevos PDFs corrigiendo URLs caducadas (Enel 2022/2024, Vodafone 2022, Nemetschek 2024).

### Sesión 2026-05-28/29 (automática + manual)

**Descargados automáticamente vía Wayback CDX:**

| Empresa | Año | Solución |
|---------|-----|---------|
| Air France-KLM | 2024 | URL en CDX: `airfranceklm.com/sites/default/files/2025-04/2024_urd_ven_04032025.pdf` |
| STMicroelectronics | 2023 | UUID `632e1a9a` vía Wayback → Form 6-K FY2023 DAR |
| STMicroelectronics | 2024 | UUID `ea3b0c4d` vía Wayback → DAR 2024 (442 pp) |

**Descargados manualmente por el usuario:**

| Empresa | Ticker | Año | Páginas | Fuente |
|---------|--------|-----|---------|--------|
| Allfunds Group | ALLFG | 2023 | 224 | allfunds.com IR — `REDUX_ANNUAL_REPORT_1cbf35d7ea.pdf` |
| Compass Group | CPG | 2023 | 236 | compassgroupplc.com IR |
| Compass Group | CPG | 2024 | 236 | compassgroupplc.com IR |
| Colruyt | COLR | 2022 | 280 | colruytgroup.com — FY2021/22 |
| Unilever | ULVR | 2024 | 305 | unilever.com (descarga manual) |
| Mercedes-Benz Group | MBG | 2024 | 453 | mercedes-benz-group.com IR |
| Stellantis | STLAM | 2024 | 442 | stellantis.com IR |
| UBS Group | UBSG | 2022 | 390 | ubs.com IR |
| UBS Group | UBSG | 2023 | 430 | ubs.com IR |
| UBS Group | UBSG | 2024 | 395 | ubs.com IR |
| STMicroelectronics | STMPA | 2022 | 227 | investors.st.com — DAR 2022 |
| STMicroelectronics | STMPA | 2023 | 254 | investors.st.com — DAR 2023 (reemplaza copia Wayback) |

---

## Estado actual

```bash
conda run -n tfg-ade python -c "
import pandas as pd
df = pd.read_csv('data/external/tracking_descargas.csv')
print(df.estado.value_counts())
print(f'{(df.estado==\"descargado\").sum()}/{len(df)}')"
```

---

## Última sesión completada (2026-05-29)

| Empresa | Ticker | Año | Páginas | Fuente |
|---------|--------|-----|---------|--------|
| Unilever | ULVR | 2022 | 241 | unilever.com (descarga manual) |
| Swisscom | SCMN | 2022 | 186 | swisscom.ch — geschaeftsbericht 2022 en |
| Swisscom | SCMN | 2023 | 212 | swisscom.ch — geschaeftsbericht 2023 en |
| Swisscom | SCMN | 2024 | 230 | swisscom.ch — geschaeftsbericht 2024 en |

---

## Comandos útiles

```bash
# Ver estado actual
conda run -n tfg-ade python -c "
import pandas as pd; df = pd.read_csv('data/external/tracking_descargas.csv')
print(df.estado.value_counts()); print(f'{(df.estado==\"descargado\").sum()}/{len(df)}')"

# Contar PDFs físicos
find data/raw -name "*.pdf" | wc -l
```

---

## Notas técnicas del pipeline

- Script principal: `scripts/fase3_descarga.py`
- Script registro manual: `scripts/fase3_registrar.py`
- Tracking: `data/external/tracking_descargas.csv`
- PDFs: `data/raw/[País]/[TICKER]/`
- Convención nombre: `[TICKER]_[AÑO]_integrated.pdf`
- annualreports.com: caído en mayo 2026 (connection refused)
- Wayback Machine: usar sufijo `if_` en el timestamp para obtener PDF crudo (sin toolbar HTML)
- STMPA: UUID `ea3b0c4d` = DAR 2024; UUID `632e1a9a` = Form 6-K FY2023
- ALLFG: informes en `app.allfunds.com/docs/cms/` con hash en el nombre (REDUX = Annual Report 2023)
- Colruyt: FY termina en marzo — FY2021/22 = año tracking 2022; informes en colruytgroup.com
- Enel: ruta correcta `/investitori/` (italiano) no `/investors/`
- Nemetschek 2024: URL correcta en `ir.nemetschek.com`
- Vodafone 2022: URL correcta en `~/media/Files/V/Vodafone-IR/...`
