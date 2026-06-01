# Notas sobre el Marco Normativo Europeo

> Documentos descargados en `data/external/normativa/`. Usados en Fase 5 para evaluar cumplimiento.

---

## 1. NFRD — Directiva 2014/95/UE (antecedente)

**Archivo:** `data/external/normativa/NFRD/NFRD_Directiva_2014_95_ES.pdf`  
**EUR-Lex:** https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=CELEX:32014L0095

### Qué regula
Primera directiva de reporting no financiero en Europa. Obligaba a empresas de más de 500 empleados a incluir en su informe anual información sobre:
- Medio ambiente
- Asuntos sociales y laborales
- Respeto de los derechos humanos
- Lucha contra la corrupción y el soborno
- Diversidad en órganos de administración

### Limitaciones (por qué nació la CSRD)
- Sin formato estandarizado → informes muy heterogéneos
- Sin obligación de aseguramiento externo
- Sin principio de doble materialidad
- Alcance limitado (solo ~11.000 empresas en la UE)
- Verificación externa no requerida

### Relevancia para el TFG
Los informes de 2022 aún caen bajo NFRD. Sirven como **baseline pre-CSRD** para la comparativa temporal (RQ4).

---

## 2. CSRD — Directiva 2022/2464/UE

**Archivo:** `data/external/normativa/CSRD/CSRD_Directiva_2022_2464_ES.pdf`  
**EUR-Lex:** https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=CELEX:32022L2464

### Qué regula
Refunde y amplía la NFRD. Principales novedades:
- **Doble materialidad:** las empresas deben reportar tanto impactos sobre la sociedad/medioambiente (materialidad de impacto) como riesgos y oportunidades que la sostenibilidad supone para la empresa (materialidad financiera)
- **Estandarización obligatoria** mediante los ESRS
- **Aseguramiento externo** con garantía limitada (y en el futuro razonable)
- **Etiquetado digital** (XBRL/iXBRL) para facilitar comparabilidad automática
- **Ampliación de alcance:** ~50.000 empresas en la UE

### Calendario de implementación
| Ejercicio | Empresas afectadas |
|-----------|-------------------|
| 2024 | Grandes empresas ya bajo NFRD (>500 empleados) |
| 2025 | Grandes empresas no cubiertas antes (>250 empleados o >40M€ facturación) |
| 2026 | PYMES cotizadas |
| 2028 | Empresas no-UE con actividad significativa en la UE |

### Artículos clave para el TFG
- **Art. 19a y 29a:** obligación de estado de información no financiera
- **Art. 8:** principio de doble materialidad
- **Anexo I y II:** referencia a los ESRS como estándares de reporting

---

## 3. ESRS — Reglamento Delegado (UE) 2023/2772

**Archivos:**
- `data/external/normativa/ESRS/ESRS_Set1_Reglamento_Delegado_2023_2772_EN.pdf` (5.8 MB — para modelos)
- `data/external/normativa/ESRS/ESRS_Set1_Reglamento_Delegado_2023_2772_ES.pdf` (6.0 MB)

**EUR-Lex (consolidado):** https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02023R2772-20231222  
**PDF oficial:** https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202302772

### Los 12 estándares ESRS

#### Transversales (siempre obligatorios)

| Estándar | Nombre completo | Contenido principal |
|----------|-----------------|---------------------|
| **ESRS 1** | General Requirements | Arquitectura del sistema, concepto de doble materialidad, due diligence, horizontes temporales, información comparativa |
| **ESRS 2** | General Disclosures | Gobierno (GOV), Estrategia (SBM), Gestión de riesgos (IRO), Métricas y objetivos (MT) — siempre obligatorio |

#### Medioambientales (sujetos a materialidad)

| Estándar | Nombre completo | Disclosure Requirements clave |
|----------|-----------------|-------------------------------|
| **E1** | Climate Change | Scope 1/2/3 GHG, plan de transición, análisis de escenarios climáticos, energías renovables, riesgos climáticos |
| **E2** | Pollution | Emisiones al aire/agua/suelo, sustancias peligrosas, microplásticos, umbrales regulatorios |
| **E3** | Water and Marine Resources | Consumo y extracción de agua, descarga, áreas con estrés hídrico, recursos marinos |
| **E4** | Biodiversity and Ecosystems | Pérdida de hábitat, conversión de suelo, servicios ecosistémicos, restauración *(suspendido temporalmente para Wave 1 2025-2026)* |
| **E5** | Resource Use & Circular Economy | Consumo de materiales, residuos, diseño para circularidad, eficiencia en cadena de suministro |

#### Sociales (sujetos a materialidad)

| Estándar | Nombre completo | Disclosure Requirements clave |
|----------|-----------------|-------------------------------|
| **S1** | Own Workforce | Condiciones laborales, salarios, libertad de asociación, diálogo social, igualdad |
| **S2** | Workers in the Value Chain | Prácticas laborales en proveedores, trabajo infantil/forzado, mecanismos de queja *(temporalmente no aplicable Wave 1)* |
| **S3** | Affected Communities | Consulta comunitaria, derechos sobre la tierra, debida diligencia en DDHH *(suspendido Wave 1)* |
| **S4** | Consumers and End Users | Seguridad de producto, privacidad de datos, marketing responsable *(suspendido Wave 1)* |

#### Gobernanza

| Estándar | Nombre completo | Disclosure Requirements clave |
|----------|-----------------|-------------------------------|
| **G1** | Business Conduct | Anticorrupción, cumplimiento fiscal, competencia leal, protección de whistleblowers |

### Uso en el TFG
- El diccionario ESRS de keywords (Paso 5.2) se construye a partir de los **Disclosure Requirements** de cada estándar
- El PDF en inglés (`_EN.pdf`) es el que se pasará a los modelos para evaluar cobertura y cumplimiento
- La cobertura real de cada empresa se medirá contra estos DRs

---

## 4. Taxonomía UE — Reglamento 2020/852

**Archivo:** `data/external/normativa/Taxonomia_UE/Taxonomia_UE_Reglamento_2020_852_ES.pdf`  
**EUR-Lex:** https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=CELEX:32020R0852

### Qué regula
Sistema de clasificación de actividades económicas **sostenibles** para redirigir inversión privada hacia la transición verde.

### Los 6 objetivos medioambientales
1. Mitigación del cambio climático
2. Adaptación al cambio climático
3. Uso sostenible y protección de recursos hídricos y marinos
4. Transición hacia una economía circular
5. Prevención y control de la contaminación
6. Protección y restauración de la biodiversidad y los ecosistemas

### Criterios clave
- **Contribución sustancial:** la actividad debe contribuir significativamente a al menos un objetivo
- **DNSH (Do No Significant Harm):** no debe dañar significativamente ninguno de los otros objetivos
- **Salvaguardas mínimas:** cumplimiento con estándares sociales mínimos (OCDE, ONU)

### Relevancia para el TFG
Las empresas del STOXX 600 publican el **% de ventas/capex/opex "alineados con la Taxonomía"**. Este dato puede usarse como variable de control en las regresiones (Paso 5.18).

---

## 5. SFDR — Reglamento 2019/2088

**Archivo:** `data/external/normativa/SFDR/SFDR_Reglamento_2019_2088_ES.pdf`  
**EUR-Lex:** https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=CELEX:32019R2088

### Qué regula
Obligaciones de transparencia en sostenibilidad para **participantes en mercados financieros** (gestoras, aseguradoras, fondos de pensiones). No aplica directamente a empresas no financieras, pero condiciona su reporting porque los inversores institucionales deben rendir cuentas sobre las empresas de su cartera.

### Clasificación de productos financieros
| Artículo | Tipo | Descripción |
|----------|------|-------------|
| **Art. 6** | Sin integración de sostenibilidad | El producto no promueve características medioambientales o sociales |
| **Art. 8** | Promueve características de sostenibilidad | El producto promueve características medioambientales o sociales |
| **Art. 9** | Objetivo de inversión sostenible | El producto tiene la inversión sostenible como objetivo explícito |

### Relevancia para el TFG
Contextualiza por qué las grandes corporaciones tienen incentivo para mejorar su reporting de sostenibilidad: los fondos Art. 8 y 9 presionan a las empresas en cartera para obtener datos de mayor calidad.

---

## Tabla comparativa NFRD vs CSRD

| Dimensión | NFRD (2014/95) | CSRD (2022/2464) |
|-----------|----------------|------------------|
| Alcance | ~11.000 empresas | ~50.000 empresas |
| Estándares | Sin formato único | ESRS obligatorios |
| Doble materialidad | No | Sí |
| Aseguramiento | No requerido | Garantía limitada obligatoria |
| Formato digital | No | XBRL/iXBRL obligatorio |
| Auditoría externa | No | Sí (limitada) |
| Información cadena de valor | Mínima | Extensa |
| Objetivos climáticos | No específicos | Alineados con Acuerdo de París |
