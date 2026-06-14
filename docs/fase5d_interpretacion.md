# Fase 5D — Interpretación de resultados

> **Corpus ampliado — 196 empresas / 586 documentos `sus` (Decisión 036).**
> Re-ejecutado desde cero sobre `5c_frases.parquet` (539.993 frases) +
> `5c_doc_agregado.csv` (586 docs). La metodología (fórmula del GW_index) no
> cambia respecto a la versión original (97 empresas / 289 docs, Decisión 025);
> solo los números, que **confirman y amplifican** los hallazgos previos.

`scripts/nlp/fase5d_gwindex.py` (Decisión 025/036). Granularidad: 586 documentos `sus`
(igual que 5C). Inputs: `5c_frases.parquet` (539.993 frases) + `5c_doc_agregado.csv`.

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
| `ratio_cuantitativo` | % frases con cifra (excluye años sueltos `19xx`/`20xx`) | 5D |
| `ratio_futuro` | % frases con lenguaje prospectivo (will/plan/aim/target/commit/by 20XX/ambition/pledge/goal...) | 5D |
| `ratio_futuro_sin_cifra` | % frases prospectivas sin ninguna cifra → "promesa vaga" | 5D |

Interpretación del signo: **GW_index alto = más cauteloso/hedged, más promesas vagas
sin cuantificar, menos cifras y menos especificidad climática** → más "cheap talk".

`finbert_tone` se reporta aparte (no entra en el índice) como variable de contraste
para la hipótesis "tono optimista sin sustancia".

---

## 2. Evolución por año (`5d_gwindex_evolucion.png`, `5d_componentes.png`)

| Año | GW_index | hedging_ratio | ratio_cuantitativo | ratio_futuro | ratio_futuro_sin_cifra | climate_specificity_spec |
|-----|----------|---------------|---------------------|--------------|------------------------|---------------------------|
| 2022 | −0.2026 | 0.0112 | 0.3234 | 0.1861 | 0.1241 | 0.2621 |
| 2023 | −0.1677 | 0.0124 | 0.3235 | 0.1888 | 0.1238 | 0.2707 |
| 2024 | **+0.3705** | 0.0146 | 0.3049 | 0.1831 | 0.1226 | 0.2413 |

**Lectura (mismo patrón cualitativo que la muestra original, magnitud algo menor en el
salto absoluto del índice pero igualmente clara):**
- 2022→2023: el GW_index mejora ligeramente (−0.2026→−0.1677) — `ratio_cuantitativo` se
  mantiene prácticamente plano (0.3234→0.3235) y `climate_specificity_spec` sube
  (0.2621→0.2707). Igual que en la muestra original, el deterioro no es lineal: ocurre
  sobre todo en la transición a 2024.
- 2023→2024 (transición NFRD→CSRD): **salto fuerte al alza** del GW_index (−0.1677→+0.3705,
  Δ=+0.548 en el año de transición CSRD), impulsado por:
  - `hedging_ratio` +17.7% vs 2023 (+30% vs 2022) — confirma 5C/Dec.036 (↑uncertainty +
    weak modal).
  - `climate_specificity_spec` −10.9% vs 2023 (y −7.9% vs 2022) — confirma 5C/Dec.036.
  - `ratio_cuantitativo` −5.7% vs 2023: **se reproduce el hallazgo nuevo de 5D** (Decisión
    025) — el crecimiento de volumen textual en 2024 (5A: `sus` mediana +147% 2022→2024) no
    viene acompañado de proporcionalmente más datos cuantitativos; al contrario, decae.
  - `ratio_futuro_sin_cifra` se mantiene casi plano (0.1241→0.1226): igual que en la
    muestra original, las "promesas vagas" no aumentan en términos relativos — el
    deterioro viene de hedging + falta de cifras + falta de especificidad, no de más
    promesas sin cuantificar.

**Robustez (Dec.019):** excluyendo las 46 filas `densidad_baja`, la tendencia es
idéntica e incluso algo más marcada: −0.3355 → −0.3399 → +0.3396 (Δ22→24 = +0.675).

**Significación:** test pareado 2022↔2024 sobre las **194 empresas** presentes en ambos
años (Decisión 036): Δ=+0.547, **Wilcoxon p=0.0051** (significativo, mejora respecto al
p=0.021 de la muestra de 95 empresas — más potencia estadística con el doble de casos). El
aumento de GW_index en 2024 frente a 2022 es estadísticamente robusto a nivel no
paramétrico, ahora con mayor solidez.

---

## 3. Relación con tono y sentimiento climático (`5d_gwindex_vs_tono.png`)

Correlaciones cruzadas (586 docs, todos los años):

| Variable | r con GW_index |
|---|---|
| `climate_sentiment_risk` | **+0.46** |
| `climate_sentiment_opportunity` | −0.19 |
| `climate_commitment_yes` | −0.09 |
| `finbert_tone` | +0.04 (prácticamente nula) |

Las correlaciones cruzadas se mantienen en la misma dirección que en la muestra original
(r=0.50/−0.24/−0.12/+0.10), con magnitudes algo menores pero el mismo patrón. La
correlación cruzada con `finbert_tone` sigue siendo muy débil, pero la **relación
temporal** es la relevante para RQ4: el tono FinBERT cae 2022→2024 (5C/Dec.036:
0.1885→0.1405) **a la vez que** el GW_index sube (−0.2026→+0.3705). Es decir, el discurso
se vuelve simultáneamente menos optimista y más "cheap talk" (más hedging, menos
especificidad/cuantificación) — confirma a 196 empresas que no es el patrón clásico "más
optimismo sin sustancia", sino "menos sustancia en general" bajo CSRD, con más discurso de
riesgo (r=0.46 con GW_index) y menos de oportunidad/compromiso.

---

## 4. Para RQ3/RQ4

El GW_index cierra la triangulación de 5C: el descenso simultáneo de especificidad,
compromiso y oportunidad climática (5C/Dec.036) **no** viene compensado por mayor
cuantificación — al contrario, `ratio_cuantitativo` también cae en 2024 (−5.7% vs 2023).
El reporting 2024 es, en términos relativos, más cauteloso y menos específico/cuantificado
que 2022-23, compatible con una señal de "cheap talk" creciente bajo CSRD (RQ4), ahora
confirmada con significación estadística reforzada (Wilcoxon p=0.0051 sobre 194 empresas).
Para RQ3 (sector/país/tamaño como predictores), el `GW_index` por documento
(`5d_gwindex.csv`) es el input directo de las regresiones de 5E.

---

## 5. Tabla de salida: `5d_gwindex.csv`

**586 filas** (una por documento `sus`) ×: `doc_id, empresa, año, confianza,
ratio_cuantitativo, ratio_futuro, ratio_futuro_sin_cifra, lm_uncertainty, lm_weak_modal,
climate_specificity_spec, finbert_tone, climate_sentiment_opportunity,
climate_sentiment_risk, climate_commitment_yes, hedging_ratio, z_hedging,
z_futuro_sin_cifra, z_cuantitativo, z_specificity, GW_index`.

---

## 6. Para el TFG — qué reportar de 5D

| Elemento | Dónde | Capítulo TFG | RQ |
|----------|-------|--------------|-----|
| Definición y fórmula del GW_index | Decisión 025 + §1 | Metodología | RQ3 |
| Evolución GW_index 2022→2024 (−0.2026→+0.3705 neto) | `5d_gwindex_evolucion.png` + tabla §2 | Resultados | RQ4 |
| Componentes por año (hedging↑, cuantitativo↓, especificidad↓) | `5d_componentes.png` | Resultados | RQ3, RQ4 |
| Test pareado 2022↔2024, 194 empresas (Wilcoxon p=0.0051) | §2 | Resultados | RQ4 |
| Correlación GW_index–riesgo climático (r=0.46) | `5d_gwindex_vs_tono.png` + tabla §3 | Resultados | RQ3 |
| Robustez a 196 empresas vs muestra original 97 | §2/§3 (todo el documento) | Metodología (reproducibilidad) | — |

---

## 7. Resumen ejecutivo

- **GW_index sube netamente 2022→2024** (−0.2026 → +0.3705), impulsado por más hedging,
  menos especificidad climática y **menos contenido cuantitativo** — el mismo patrón que
  en la muestra de 97 empresas (Decisión 025), ahora replicado sobre 196.
- Las "promesas vagas sin cifra" (`ratio_futuro_sin_cifra`) se mantienen estables
  (0.1241→0.1226) — el deterioro no viene de más promesas vagas, sino de menos sustancia
  (cifras, especificidad) y más cautela (hedging).
- Robusto a la exclusión de `densidad_baja` (Dec.019: −0.3355→−0.3399→+0.3396) y al test no
  paramétrico pareado, ahora con **mayor significación** (Wilcoxon p=0.0051 sobre 194
  empresas, vs p=0.021 sobre 95 en la muestra original).
- GW_index correlaciona con discurso de riesgo climático (r=0.46) y negativamente con
  oportunidad/compromiso — consistente con la narrativa de 5C de un reporting 2024 más
  defensivo/normativo, ahora confirmada a escala del STOXX 600 muestreado.
- Siguiente paso: **5E** — usar `GW_index` como variable dependiente en regresiones con
  sector/país/tamaño (RQ3) y contrastar 2022↔2024 a nivel agregado (RQ4).
