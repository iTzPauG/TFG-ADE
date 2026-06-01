# Guía de correcciones — PDFs problemáticos

> Generado: 2026-05-29 | Actualizado: 2026-05-30 (v3)

De los 10 documentos problemáticos detectados, **8 ya están resueltos**. Quedan **2 pendientes** (decisiones metodológicas).

---

## ✅ Resueltos

| PDF | Problema original | Solución aplicada | Resultado |
|-----|-------------------|-------------------|-----------|
| UMG 2022 | Era Form 10-K de Focus Universal Inc. (151pp) | Reemplazado por Annual Report UMG N.V. | Cat E → **Cat B** (337pp, 30pp ESG) |
| UMG 2023 | Era Form 10-K de Focus Universal Inc. (110pp) | Reemplazado por Annual Report UMG N.V. | Cat E → **Cat B** (355pp, 40pp ESG) |
| CPG 2022 | Era informe de Compass Diversified Holdings CODI (244pp) | Reemplazado por Annual Report Compass Group plc | Cat D → **Cat B** (226pp, 40pp ESG) |

---

## 🔴 Pendiente — Tipo 2: Documento resumido (empresa correcta, informe incorrecto)

Tenemos la versión "highlights" o "essentials" en lugar del informe completo.

---

### OR 2023 y OR 2024 — L'Oréal

**Problema:** Los archivos son el "Rapport annuel — L'essentiel" / "The Essentials", resúmenes ejecutivos de 17-19 páginas. No son el informe completo.

```
OR_2023_integrated.pdf → "Rapport annuel 2023, L'essentiel" (17pp) — Cat E, 0pp ESG
OR_2024_integrated.pdf → "2024 Annual Report — The Essentials" (19pp) — Cat C, 6pp ESG
OR_2022_integrated.pdf → URD completo ✅ (400pp, Cat A, 113pp ESG)
```

**Solución:** Descargar el Document d'enregistrement universel (URD) completo.

- `loreal-finance.com/en/annual-reports` (puede requerir aceptar cookies en el navegador)
- También en AMF: `amf-france.org` → Recherche de documents → L'Oréal
- El URD 2023 y 2024 deberían tener ~400pp (similar al 2022)

**Pasos:**
1. Descarga el URD 2023 completo (buscar "Document d'enregistrement universel 2023", no el "essentiel")
2. Descarga el URD 2024 completo
3. Reemplaza en `data/raw/France/OR/`:
   - `OR_2023_integrated.pdf`
   - `OR_2024_integrated.pdf`
4. Registra en tracking:
```bash
python scripts/fase3_registrar.py --id E094 --año 2023 \
  --url "URL_URD_2023" --paginas XXX --idioma fr \
  --notas "reemplaza resumen 'essentiel' 17pp por URD completo"

python scripts/fase3_registrar.py --id E094 --año 2024 \
  --url "URL_URD_2024" --paginas XXX --idioma fr \
  --notas "reemplaza resumen 'essentials' 19pp por URD completo"
```

---

### SAF 2022 y SAF 2023 — Safran

**Problema:** Los archivos son folletos de indicadores clave (27 y 35pp). El propio SAF 2022 referencia "section 2.1.1 of the 2022 Universal Registration Document", confirmando que es un extracto.

```
SAF_2022_integrated.pdf → Folleto "key indicators" (27pp) — Cat C, 10pp ESG
SAF_2023_integrated.pdf → Folleto "key indicators" (35pp) — Cat C, 13pp ESG
SAF_2024_integrated.pdf → URD completo ✅ (546pp, Cat C, 63pp ESG)
```

**Solución:** Descargar el URD completo de Safran.

- `safran-group.com/finance/publications/annual-reports`
- También en AMF: `amf-france.org` → Recherche de documents → Safran
- El URD 2022 y 2023 deberían tener ~400-500pp como el 2024

**Pasos:**
1. Descarga el URD 2022 completo de Safran
2. Descarga el URD 2023 completo
3. Reemplaza en `data/raw/France/SAF/`
4. Registra en tracking:
```bash
python scripts/fase3_registrar.py --id E??? --año 2022 \
  --url "URL_URD_2022" --paginas XXX --idioma fr \
  --notas "reemplaza folleto indicadores 27pp por URD completo"

python scripts/fase3_registrar.py --id E??? --año 2023 \
  --url "URL_URD_2023" --paginas XXX --idioma fr \
  --notas "reemplaza folleto indicadores 35pp por URD completo"
```

Para consultar el ID de SAF:
```bash
conda run -n tfg-ade python -c "
import pandas as pd; df = pd.read_csv('data/external/tracking_descargas.csv')
print(df[df.ticker=='SAF'][['id_empresa','año']].to_string())"
```

---

### LONN 2022 — Lonza

**Problema:** El archivo contiene únicamente los estados financieros consolidados (Balance Sheet, Income Statement, Cash Flow), sin la parte narrativa ni contenido de sostenibilidad.

```
LONN_2022_integrated.pdf → Solo estados financieros (112pp) — Cat D, 1pp ESG
LONN_2023_integrated.pdf → Informe completo ✅ (112pp, Cat B, 6pp ESG)
LONN_2024_integrated.pdf → Informe completo ✅ (112pp, Cat B, 9pp ESG)
```

**Nota:** Lonza publica dos PDFs separados — "Annual Report" (narrativo) y "Financial Statements". Los de 2023 y 2024 son correctos y compactos por diseño.

**Solución:** Descargar el Annual Report 2022 narrativo.

- `lonza.com/investor-relations/reports`
- Buscar "Annual Report 2022" (no "Financial Statements 2022")
- Alternativamente buscar en Wayback Machine: `web.archive.org/web/2023*/lonza.com/*annual-report*2022*`

**Pasos:**
1. Descarga el Annual Report 2022 narrativo de Lonza
2. Reemplaza `data/raw/Switzerland/LONN/LONN_2022_integrated.pdf`
3. Registra en tracking:
```bash
python scripts/fase3_registrar.py --id E??? --año 2022 \
  --url "URL_AR_2022" --paginas XXX --idioma en \
  --notas "reemplaza financial statements por annual report narrativo completo"
```

---

## 🟡 Pendiente — Tipo 3: Documento correcto con ESG muy escaso

Documentos válidos de la empresa correcta pero con contenido ESG mínimo. Requieren una **decisión metodológica**, no una descarga nueva.

---

### NEM 2022 — Nemetschek

```
NEM_2022_integrated.pdf → Geschäftsbericht 2022 (178pp) — Cat D, 1pp ESG
NEM_2023_integrated.pdf → Cat B ✅ (180pp, 13pp ESG)
NEM_2024_integrated.pdf → Cat A ✅ (228pp, 51pp ESG)
```

**Contexto:** Nemetschek es una empresa de software alemana. En 2022 el reporting ESG era incipiente. El Konzern-Lagebericht está presente pero con contenido de sostenibilidad mínimo.

**Opciones:**

| Opción | Acción | Consecuencia |
|--------|--------|--------------|
| A *(recomendada)* | Excluir NEM 2022 del análisis NLP | Pierde 1 obs.; la evolución 2022→2024 es un hallazgo en sí mismo |
| B | Buscar Nachhaltigkeitsbericht separado de 2022 | Puede no existir |
| C | Incluir anotando bajo contenido en metadatos | Introduce ruido en análisis de 2022 |

---

### DIA 2022 — Distribuidora Internacional de Alimentación

```
DIA_2022_integrated.pdf → Informe financiero + auditoría (207pp) — Cat E, 0pp ESG
DIA_2023_integrated.pdf → Cat B ✅ (211pp, 31pp ESG)
DIA_2024_integrated.pdf → Cat C ✅ (100pp, 5pp ESG)
```

**Contexto:** Dia estaba en plena reestructuración en 2022. El documento es el informe de auditoría + estados financieros consolidados; la información no financiera puede estar en un EINF separado o ser mínima.

**Opciones:**

| Opción | Acción | Consecuencia |
|--------|--------|--------------|
| A | Buscar el EINF 2022 de Dia en CNMV (`cnmv.es`) | Puede existir como documento separado |
| B *(recomendada)* | Excluir DIA 2022 del análisis NLP con nota | Empresa en crisis = dato interesante como caso extremo |
| C | Incluir anotando ausencia de ESG | Válido si se trata como variable (ESG score = 0) |

---

## Resumen de estado

| PDF | Estado | Categoría actual | Pendiente |
|-----|--------|-----------------|-----------|
| UMG 2022 | ✅ Resuelto | Cat B (337pp, 30pp ESG) | — |
| UMG 2023 | ✅ Resuelto | Cat B (355pp, 40pp ESG) | — |
| CPG 2022 | ✅ Resuelto | Cat B (226pp, 40pp ESG) | — |
| OR 2023 | ✅ Resuelto | URD completo (450pp) | — |
| OR 2024 | ✅ Resuelto | URD completo (448pp) | — |
| SAF 2022 | ✅ Resuelto | URD completo (536pp) | — |
| SAF 2023 | ✅ Resuelto | URD completo (542pp) | — |
| LONN 2022 | ✅ Resuelto | Annual Report narrativo (234pp) | — |
| NEM 2022 | 🟡 Decisión | Cat D (178pp, 1pp ESG) | Excluir del análisis NLP |
| DIA 2022 | 🟡 Decisión | Cat E (207pp, 0pp ESG) | Excluir o anotar |

---

## Después de resolver los pendientes

Vuelve a ejecutar la auditoría completa:

```bash
/opt/homebrew/Caskroom/miniconda/base/envs/tfg-ade/bin/python /tmp/audit_fast.py
```

Y regenera el documento de auditoría ejecutando el script de generación del markdown.
