# Notas sobre la Literatura Académica — Fase 1B

> Papers fundacionales para el TFG. Organizado por bloque temático.

---

## Bloque A — Diccionarios y análisis textual financiero

### Loughran & McDonald (2011)
**Título:** "When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks"  
**Revista:** The Journal of Finance, Vol. 66, No. 1, pp. 35-65  
**DOI:** 10.1111/j.1540-6261.2010.01625.x  
**Links:**
- Wiley (oficial): https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2010.01625.x
- SSRN (preprint): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1331573
- PDF (UTS mirror): https://www.uts.edu.au/sites/default/files/ADG_Cons2015_Loughran%20McDonald%20JE%202011.pdf
- Diccionario (SRAF): https://sraf.nd.edu/loughranmcdonald-master-dictionary/

**Aportación principal:**
Los diccionarios generales de sentimiento (Harvard GI) clasifican erróneamente palabras en contexto financiero (ej. "liability", "tax", "board" son negativas en Harvard pero neutras en finanzas). LM construyeron un diccionario específico para 10-Ks de empresas cotizadas con 6 categorías:
- **Negative** (~2.355 palabras)
- **Positive** (~354 palabras)
- **Uncertainty** (~297 palabras): "approximately", "may", "might"
- **Litigious** (~903 palabras): "claimant", "deposition"
- **Strong modal** (~19 palabras): "always", "definitely", "never"
- **Weak modal** (~27 palabras): "could", "generally", "might"

**Uso en el TFG:**
- Aplicar párrafo a párrafo sobre el management report para medir tono positivo/negativo (Paso 5.11)
- Las palabras de **Uncertainty** y **Weak modal** son proxy de hedging language → indicador de vaguedad
- El diccionario está descargado en: `data/external/diccionarios/LoughranMcDonald_MasterDictionary.csv`

**Limitación relevante:** Desarrollado para textos financieros anglosajones (10-Ks de la SEC). Aplicarlo a informes ESG europeos puede generar ruido. Documentar en la sección de limitaciones del TFG.

---

## Bloque B — Impression management y legitimidad

### Hahn & Lülfs (2014)
**Título:** "Legitimizing Negative Aspects in GRI-Oriented Sustainability Reporting: A Qualitative Analysis of Corporate Disclosure Strategies"  
**Revista:** Journal of Business Ethics, Vol. 123, No. 3, pp. 401-420  
**DOI:** 10.1007/s10551-013-1801-4  
**Links:**
- Springer (oficial): https://link.springer.com/article/10.1007/s10551-013-1801-4
- SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2290167
- ResearchGate (PDF): https://www.researchgate.net/publication/249649992

**Aportación principal:**
Análisis cualitativo de cómo las empresas del DJIA y del DAX gestionan la legitimidad en sus informes GRI. Identifica **6 estrategias de legitimación** para aspectos negativos:
1. **Abstracción:** declaraciones vagas sin cuantificar
2. **Desplazamiento temporal:** "trabajaremos en ello en el futuro"
3. **Externalización:** culpar a factores externos
4. **Comparación favorable:** "mejor que el año pasado / que el sector"
5. **Negación:** negar que el impacto sea negativo
6. **Compensación:** declarar acciones compensatorias

**Hipótesis de conexión con el TFG:**
Las métricas de vaguedad (Paso 5.14) son operacionalizaciones cuantitativas de las estrategias 1 y 2 de Hahn & Lülfs. Útil para justificar teóricamente las métricas elegidas.

**Gap que deja:** Análisis cualitativo, muestra pequeña (USA + Alemania), no europeo amplio, pre-CSRD.

---

### Cho, Laine, Roberts & Rodrigue (2015)
**Título:** "Organized Hypocrisy, Organizational Façades, and Sustainability Reporting"  
**Revista:** Accounting, Organizations and Society, Vol. 40, pp. 78-94  
**DOI:** 10.1016/j.aos.2014.12.003  
**Links:**
- ScienceDirect (oficial): https://www.sciencedirect.com/science/article/pii/S0361368214000902
- Semantic Scholar: https://www.semanticscholar.org/paper/Organized-hypocrisy,-organizational-fa%C3%A7ades,-and-Cho-Laine/53cb534c2951f6e0736c30c664fd689b61c538c1
- ResearchGate (PDF): https://www.researchgate.net/publication/270517361

**Aportación principal:**
Desarrolla el concepto de **"organizational façade"** aplicado a los informes de sostenibilidad. Las empresas crean apariencias de sostenibilidad (facade) para satisfacer presiones institucionales sin cambiar sus prácticas reales. Distingue entre:
- **Hypocrisy organizada:** discurso y acción deliberadamente desacoplados
- **Façade:** presentación externa construida para legitimar la organización

**Uso en el TFG:**
Marco teórico para interpretar por qué empresas con peor ESG score podrían usar lenguaje más optimista. Respaldo al "índice de greenwashing" (Paso 5.16).

**Gap que deja:** No propone métricas cuantitativas. El TFG aporta operacionalización mediante PLN.

---

## Bloque C — Calidad del reporting CSR

### Michelon, Pilonato & Ricceri (2015)
**Título:** "CSR Reporting Practices and the Quality of Disclosure: An Empirical Analysis"  
**Revista:** Critical Perspectives on Accounting, Vol. 33, pp. 59-78  
**DOI:** 10.1016/j.cpa.2014.10.003  
**Links:**
- ScienceDirect (oficial): https://www.sciencedirect.com/science/article/abs/pii/S1045235414001051
- Semantic Scholar: https://www.semanticscholar.org/paper/CSR-reporting-practices-and-the-quality-of-An-Michelon-Pilonato/f9a827ce1f89d58f52d496f87e3f0e19949b49a8
- ResearchGate (PDF): https://www.researchgate.net/publication/268693255
- University of Bristol: https://research-information.bris.ac.uk/en/publications/csr-reporting-practices-and-the-quality-of-disclosure-an-empirica/

**Aportación principal:**
Analiza si las **prácticas de reporting** (informes standalone, verificación externa, uso de GRI) se asocian con mayor **calidad de disclosure**. Conclusión sorprendente: los informes standalone tienen menor calidad media que los integrados, y GRI y aseguramiento no garantizan mayor calidad. Los informes son más simbólicos que sustanciales.

**Dimensiones de calidad que miden:**
- Amplitud (breadth): nº de temas cubiertos
- Profundidad (depth): nivel de detalle
- Especificidad (specificity): cuantitativo vs cualitativo
- Neutralidad: inclusión de información negativa

**Uso en el TFG:**
Las dimensiones de calidad de Michelon et al. son el referente teórico para las métricas de ClimateBERT-specificity y el ratio cuantitativo/cualitativo (Paso 5.14). Citar directamente en la sección de metodología.

---

## Bloque D — Greenwashing y PLN climático

### Bingler, Kraus, Leippold & Webersinke (2022)
**Título:** "Cheap Talk and Cherry-Picking: What ClimateBert Has to Say on Corporate Climate Risk Disclosures"  
**Revista:** Finance Research Letters, Vol. 47, 102776  
**DOI:** 10.1016/j.frl.2022.102776  
**Links:**
- ScienceDirect (oficial): https://www.sciencedirect.com/science/article/pii/S1544612322000897
- SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3796152
- Oxford ORA: https://ora.ox.ac.uk/objects/uuid:b2d17f2f-7099-41e6-b7b3-91d37f313828
- Semantic Scholar (PDF): https://www.semanticscholar.org/paper/Cheap-Talk-and-Cherry-Picking:-What-ClimateBert-has-Bingler-Kraus/52ef2bea83eba1575fcfd02c82b4228f7aab0bd6

**Aportación principal:**
Primer paper en aplicar **ClimateBERT** a gran escala para analizar 1.500+ informes TCFD. Hallazgos clave:
- Las empresas que apoyan el TCFD hacen principalmente "cheap talk" (compromisos sin acción concreta)
- El "cherry-picking" implica reportar solo información climática no material (la que no cuesta nada)
- Las divulgaciones voluntarias se asocian con mayor cheap talk que las obligatorias
- El cheap talk correlaciona con mayor cobertura mediática negativa y mayor crecimiento de emisiones

**Modelos ClimateBERT disponibles en HuggingFace:**
- `climatebert/distilroberta-base-climate-detector`: detecta contenido climático
- `climatebert/distilroberta-base-climate-sentiment`: sentimiento climático
- `climatebert/distilroberta-base-climate-commitment`: compromiso concreto vs vago
- `climatebert/distilroberta-base-climate-specificity`: específico vs genérico

**Uso en el TFG:**
Referencia directa para el "índice de greenwashing" (Paso 5.16). Citar como estado del arte en PLN aplicado a sostenibilidad. Los 4 modelos se usarán en Fase 5C y 5D.

---

## Matriz de literatura

| Autor | Año | Muestra | Método | Hallazgo principal | Gap para el TFG |
|-------|-----|---------|--------|--------------------|-----------------|
| Loughran & McDonald | 2011 | 10-Ks SEC | Análisis textual, regresión | Diccionarios generales inadecuados para finanzas | No ESG, no europeo |
| Hahn & Lülfs | 2014 | DJIA + DAX | Análisis cualitativo | 6 estrategias de legitimación | No cuantitativo, muestra pequeña |
| Michelon et al. | 2015 | Empresas cotizadas | Análisis de contenido | Reporting más simbólico que sustancial | Pre-CSRD, no PLN |
| Cho et al. | 2015 | Empresas cotizadas | Análisis conceptual | Concepto de organizational façade | Sin operacionalización cuantitativa |
| Bingler et al. | 2022 | 1.500+ informes TCFD | ClimateBERT, NLP | Cheap talk y cherry-picking predominan | Solo clima, pre-CSRD |
| **Este TFG** | 2025 | STOXX 600 | BERTopic + FinBERT + ClimateBERT | **RQ1-RQ4** | Marco CSRD/ESRS completo |

**El gap del TFG:** ninguno de los papers anteriores analiza el STOXX Europe 600 bajo el marco completo CSRD/ESRS usando una combinación de topic modeling, análisis de sentimiento y detección de greenwashing en el contexto post-CSRD.

---

## Cadenas de búsqueda utilizadas (Paso 1.6)

```
("sustainability report*" OR "ESG disclosure" OR "non-financial report*") AND ("text analysis" OR "NLP" OR "content analysis")
("impression management" OR "greenwashing") AND ("corporate report*")
("CSRD" OR "ESRS") AND ("disclosure" OR "reporting")
```

**Bases de datos:** Web of Science, Scopus, Google Scholar, SSRN  
**Filtros:** 2015-2025, revistas Q1-Q2, inglés/español
