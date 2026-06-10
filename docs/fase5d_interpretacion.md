# Fase 5D — Interpretación de resultados

`scripts/nlp/fase5d_gwindex.py` (Decisión 025). Granularidad: 289 documentos `sus`
(igual que 5C). Inputs: `5c_frases.parquet` (285.509 frases) + `5c_doc_agregado.csv`.

---

## 1. Qué es el GW_index

Índice compuesto de "cheap talk" textual, siguiendo la definición operativa de
greenwashing de la Decisión 001 (especificidad, hedging, ratio cuantitativo, tono —
sin scores ESG externos).

```
GW_index = z(hedging_ratio) + z(ratio_futuro_sin_cifra) − z(ratio_cuantitativo) − z(climate_specificity_spec)
```

Componentes (medias por frase/documento, sección `sus`):

| Componente | Qué mide | Origen |
|---|---|---|
| `hedging_ratio` | `lm_uncertainty + lm_weak_modal` | 5C (Loughran-McDonald) |
| `climate_specificity_spec` | % frases climáticas específicas (ClimateBERT) | 5C |
| `ratio_cuantitativo` | % frases con cifra (excluye años sueltos `19xx`/`20xx`) | NUEVO 5D |
| `ratio_futuro` | % frases con lenguaje prospectivo (will/plan/aim/target/commit/by 20XX/ambition/pledge/goal...) | NUEVO 5D |
| `ratio_futuro_sin_cifra` | % frases prospectivas sin ninguna cifra → "promesa vaga" | NUEVO 5D |

Interpretación del signo: **GW_index alto = más cauteloso/hedged, más promesas vagas
sin cuantificar, menos cifras y menos especificidad climática** → más "cheap talk".

`finbert_tone` se reporta aparte (no entra en el índice) como variable de contraste
para la hipótesis "tono optimista sin sustancia".

---

## 2. Evolución por año (`5d_gwindex_evolucion.png`, `5d_componentes.png`)

| Año | GW_index | hedging_ratio | ratio_cuantitativo | ratio_futuro | ratio_futuro_sin_cifra | climate_specificity_spec |
|-----|----------|---------------|---------------------|--------------|------------------------|---------------------------|
| 2022 | −0.196 | 0.0102 | 0.322 | 0.192 | 0.130 | 0.281 |
| 2023 | −0.329 | 0.0115 | 0.336 | 0.188 | 0.123 | 0.288 |
| 2024 | **+0.521** | 0.0132 | 0.304 | 0.189 | 0.125 | 0.257 |

**Lectura:**
- 2022→2023: ligera mejora (GW_index baja) — más cuantificación, especificidad estable.
- 2023→2024 (transición NFRD→CSRD): **salto fuerte al alza** del GW_index, impulsado por:
  - `hedging_ratio` +29% vs 2022 (ya documentado en 5C/Dec.024: sube uncertainty + weak modal).
  - `climate_specificity_spec` −8.5% vs 2022 (ya documentado en 5C/Dec.024).
  - `ratio_cuantitativo` −5.6% vs 2023: **el único componente nuevo de 5D**, confirma que
    el crecimiento de volumen textual en 2024 (Dec.021: `sus` +111% tokens) **no** viene
    acompañado de proporcionalmente más datos cuantitativos.
  - `ratio_futuro_sin_cifra` se mantiene casi plano (0.130→0.125): las "promesas vagas"
    no aumentan en términos relativos — el deterioro viene de hedging + falta de cifras
    + falta de especificidad, no de más promesas sin cuantificar.

**Robustez (Dec.019):** excluyendo las 16 filas `densidad_baja`, la tendencia es
idéntica: −0.284 → −0.450 → +0.532.

**Significación:** test pareado 2022↔2024 sobre las 95 empresas presentes en ambos años:
Wilcoxon p=0.021 (significativo), t-test p=0.055 (marginal). El aumento de GW_index en
2024 frente a 2022 es estadísticamente robusto a nivel no paramétrico.

---

## 3. Relación con tono y sentimiento climático (`5d_gwindex_vs_tono.png`)

Correlaciones cruzadas (289 docs, todos los años):

| Variable | r con GW_index |
|---|---|
| `climate_sentiment_risk` | **+0.50** |
| `climate_sentiment_opportunity` | −0.24 |
| `climate_commitment_yes` | −0.12 |
| `finbert_tone` | +0.10 (débil) |

La correlación cruzada con `finbert_tone` es débil, pero la **relación temporal** es la
relevante para RQ4: el tono FinBERT cae 2022→2024 (Dec.024: 0.202→0.153) **a la vez que**
el GW_index sube. Es decir, el discurso se vuelve simultáneamente menos optimista y más
"cheap talk" (más hedging, menos especificidad/cuantificación) — no es el patrón clásico
"más optimismo sin sustancia", sino "menos sustancia en general" bajo CSRD, con más
discurso de riesgo (r=0.50 con GW_index) y menos de oportunidad/compromiso.

---

## 4. Para RQ3/RQ4

El GW_index cierra la triangulación de 5C: el descenso simultáneo de especificidad,
compromiso y oportunidad climática (Dec.024) **no** viene compensado por mayor
cuantificación — al contrario, `ratio_cuantitativo` también cae en 2024. El reporting
2024 es, en términos relativos, más cauteloso y menos específico/cuantificado que 2022-23,
compatible con una señal de "cheap talk" creciente bajo CSRD (RQ4). Para RQ3
(sector/país/tamaño como predictores), el `GW_index` por documento (`5d_gwindex.csv`) es
el input directo de las regresiones de 5E.

---

## 5. Tabla de salida: `5d_gwindex.csv`

289 filas (una por documento `sus`) ×: `doc_id, empresa, año, confianza,
ratio_cuantitativo, ratio_futuro, ratio_futuro_sin_cifra, lm_uncertainty, lm_weak_modal,
climate_specificity_spec, finbert_tone, climate_sentiment_opportunity,
climate_sentiment_risk, climate_commitment_yes, hedging_ratio, z_hedging,
z_futuro_sin_cifra, z_cuantitativo, z_specificity, GW_index`.

---

## 6. Para el TFG — qué reportar de 5D

| Elemento | Dónde | Capítulo TFG | RQ |
|----------|-------|--------------|-----|
| Definición y fórmula del GW_index | Decisión 025 + §1 | Metodología | RQ3 |
| Evolución GW_index 2022→2024 (+0.196→+0.521 neto) | `5d_gwindex_evolucion.png` + tabla §2 | Resultados | RQ4 |
| Componentes por año (hedging↑, cuantitativo↓, especificidad↓) | `5d_componentes.png` | Resultados | RQ3, RQ4 |
| Test pareado 2022↔2024 (Wilcoxon p=0.021) | §2 | Resultados | RQ4 |
| Correlación GW_index–riesgo climático (r=0.50) | `5d_gwindex_vs_tono.png` + tabla §3 | Resultados | RQ3 |

---

## 7. Resumen ejecutivo

- **GW_index sube netamente 2022→2024** (−0.196 → +0.521), impulsado por más hedging,
  menos especificidad climática y **menos contenido cuantitativo** (este último es el
  hallazgo nuevo de 5D, no visto en 5A-5C).
- Las "promesas vagas sin cifra" (`ratio_futuro_sin_cifra`) se mantienen estables — el
  deterioro no viene de más promesas vagas, sino de menos sustancia (cifras,
  especificidad) y más cautela (hedging).
- Robusto a la exclusión de `densidad_baja` (Dec.019) y al test no paramétrico pareado
  (Wilcoxon p=0.021).
- GW_index correlaciona con discurso de riesgo climático (r=0.50) y negativamente con
  oportunidad/compromiso — consistente con la narrativa de 5C de un reporting 2024 más
  defensivo/normativo.
- Siguiente paso: **5E** — usar `GW_index` como variable dependiente en regresiones con
  sector/país/tamaño (RQ3) y contrastar 2022↔2024 a nivel agregado (RQ4).
