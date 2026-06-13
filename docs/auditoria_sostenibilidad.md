# Auditoría de contenido de sostenibilidad — 291 PDFs

> **⚠ Foto previa a la ampliación — 291 PDFs / 97 empresas.** Esta auditoría de contenido cubre los **291 PDFs de la muestra original de 97 empresas**. Tras la ampliación a 196 empresas (588 PDFs, Decisiones 027-035) debe extenderse a las 99 nuevas; las cifras de cobertura recogidas aquí son las de las 97 originales.

> Actualizado: 2026-05-30 (v3 — tras corrección OR 2023/2024, SAF 2022/2023, LONN 2022)
> Método: pymupdf + regex multilingüe | 8 workers paralelos | ~3 min ejecución

## Resumen ejecutivo

| Categoría | N | Descripción | Estrategia de extracción |
|-----------|---|-------------|--------------------------|
| **A** | 114 | Sección explícita en índice (≥2 hits TOC + ≥10 pp ESG) | Extracción por rango de páginas desde TOC |
| **B** | 106 | Sección identificable (1 hit TOC + ≥5 pp ESG) | Localizar cabecera + extraer bloque |
| **C** | 69 | Contenido disperso sin sección explícita | Extracción completa + filtrado por párrafos ESG |
| **D** | 1 | Solo menciones genéricas (≤1 pp ESG específico) | Revisión manual — ESG muy incipiente |
| **E** | 1 | Sin contenido ESG detectado | Requieren acción (ver sección final) |

**Cobertura útil (A+B+C): 289/291 (99.3%)**

### Estadísticas por categoría

| Cat | N | Páginas promedio | Páginas ESG promedio | % ESG promedio |
|-----|---|-----------------|---------------------|----------------|
| A | 114 | 293 | 77.5 | 25.1% |
| B | 106 | 294 | 52.3 | 17.4% |
| C | 69 | 307 | 38.3 | 13.6% |
| D | 1 | 178 | 1.0 | 0.6% |
| E | 1 | 207 | 0.0 | 0.0% |

### Evolución por año (NFRD → CSRD)

| Año  | Cat A | Cat B | Cat C | Cat D+E | Cobertura útil |
|------|------:|------:|------:|--------:|---------------:|
| 2022 |    32 |    30 |    33 |       2 | 95/97 (98%) |
| 2023 |    34 |    42 |    21 |       0 | 97/97 (100%) |
| 2024 |    48 |    34 |    15 |       0 | 97/97 (100%) |

**Tendencia clara:** migración de C → A/B entre 2022 y 2024, consistente con la implantación gradual de CSRD.

---

## Categoría A — Sección explícita bien delimitada

**Criterio:** ≥2 menciones de cabecera de sostenibilidad en las primeras 15 páginas + ≥10 páginas con contenido ESG.
**Extracción:** cortar el PDF directamente entre `p_ini` y `p_fin` con `fitz`. Alta fiabilidad.

| Ticker   | Año  | País            | Total | ESG (%)          | Rango páginas       |
|----------|------|:----------------|------:|:-----------------|:--------------------|
| RBI      | 2022 | Austria         |  282 |  10 ( 3.5%) | p.   5 – p.198 |
| RBI      | 2024 | Austria         |  632 | 209 (33.1%) | p.   5 – p.613 |
| COLR     | 2022 | Belgium         |  280 |  31 (11.1%) | p.   5 – p.272 |
| MELE     | 2024 | Belgium         |  191 |  49 (25.7%) | p.   2 – p.173 |
| ONT      | 2022 | Belgium         |  249 |  44 (17.7%) | p.   2 – p.241 |
| ONT      | 2023 | Belgium         |  258 |  60 (23.3%) | p.   2 – p.252 |
| ONT      | 2024 | Belgium         |  254 |  64 (25.2%) | p.   2 – p.237 |
| NOVO B   | 2024 | Denmark         |  152 |  41 (27.0%) | p.   2 – p.141 |
| TRYG     | 2024 | Denmark         |  221 |  51 (23.1%) | p.   2 – p.133 |
| VESTAS   | 2022 | Denmark         |  154 |  39 (25.3%) | p.   8 – p.152 |
| VESTAS   | 2023 | Denmark         |  131 |  24 (18.3%) | p.   2 – p.129 |
| VESTAS   | 2024 | Denmark         |  221 |  88 (39.8%) | p.   2 – p.219 |
| NSN      | 2022 | Finland         |  262 |  99 (37.8%) | p.   2 – p.239 |
| STER     | 2023 | Finland         |  212 |  95 (44.8%) | p.   2 – p.165 |
| STER     | 2024 | Finland         |  223 |  90 (40.4%) | p.   2 – p.220 |
| UPM      | 2024 | Finland         |  182 | 104 (57.1%) | p.   2 – p.180 |
| FR       | 2024 | France          |  502 | 198 (39.4%) | p.   2 – p.497 |
| OR       | 2022 | France          |  400 | 113 (28.2%) | p.   3 – p.397 |
| SAF      | 2022 | France          |  536 | 253 (47.2%) | p.   2 – p.533 |
| SAF      | 2023 | France          |  542 | 269 (49.6%) | p.   2 – p.539 |
| OR       | 2023 | France          |  450 | 274 (60.9%) | p.   2 – p.447 |
| OR       | 2024 | France          |  448 | 270 (60.3%) | p.   2 – p.445 |
| 1COV     | 2024 | Germany         |  360 | 149 (41.4%) | p.   2 – p.336 |
| ADS      | 2022 | Germany         |  317 |  31 ( 9.8%) | p.   5 – p.309 |
| ADS      | 2024 | Germany         |  492 | 116 (23.6%) | p.   4 – p.485 |
| BNR      | 2022 | Germany         |  292 |  34 (11.6%) | p.  10 – p.210 |
| BNR      | 2023 | Germany         |  296 |  41 (13.9%) | p.  10 – p.207 |
| DHER     | 2022 | Germany         |  226 |  19 ( 8.4%) | p.   2 – p.223 |
| DHER     | 2023 | Germany         |  231 |  23 (10.0%) | p.   2 – p.228 |
| DHER     | 2024 | Germany         |  249 |  33 (13.3%) | p.   2 – p.245 |
| EVK      | 2024 | Germany         |  326 | 130 (39.9%) | p.   2 – p.293 |
| FNTN     | 2022 | Germany         |  211 |  24 (11.4%) | p.  11 – p.208 |
| FNTN     | 2023 | Germany         |  210 |  27 (12.9%) | p.   7 – p.205 |
| FNTN     | 2024 | Germany         |  247 |  59 (23.9%) | p.   7 – p.243 |
| MBG      | 2023 | Germany         |  353 |  51 (14.4%) | p.  10 – p.352 |
| MBG      | 2024 | Germany         |  453 |  97 (21.4%) | p.  10 – p.451 |
| NEM      | 2024 | Germany         |  228 |  51 (22.4%) | p.  14 – p.145 |
| P911     | 2023 | Germany         |  239 |  50 (20.9%) | p.   3 – p.237 |
| P911     | 2024 | Germany         |  257 |  86 (33.5%) | p.   3 – p.257 |
| TLX      | 2022 | Germany         |  276 |  24 ( 8.7%) | p.   5 – p.249 |
| TLX      | 2023 | Germany         |  344 |  26 ( 7.6%) | p.   5 – p.204 |
| TLX      | 2024 | Germany         |  410 |  75 (18.3%) | p.   5 – p.276 |
| BRNW     | 2024 | Italy           |  324 |  72 (22.2%) | p.   3 – p.324 |
| CPR      | 2024 | Italy           |  413 | 111 (26.9%) | p.   3 – p.411 |
| ENEL     | 2022 | Italy           |  571 | 163 (28.5%) | p.  14 – p.564 |
| ENEL     | 2024 | Italy           |  698 | 471 (67.5%) | p.   4 – p.695 |
| LDO      | 2022 | Italy           |  432 |  78 (18.1%) | p.   2 – p.431 |
| LDO      | 2023 | Italy           |  437 |  91 (20.8%) | p.   2 – p.435 |
| LDO      | 2024 | Italy           |  424 | 105 (24.8%) | p.   2 – p.423 |
| QIA      | 2024 | Netherlands     |  397 |  59 (14.9%) | p.   2 – p.146 |
| STLAM    | 2022 | Netherlands     |  421 |  58 (13.8%) | p.   2 – p.412 |
| STMPA    | 2024 | Netherlands     |  442 | 120 (27.1%) | p.   3 – p.440 |
| WKL      | 2023 | Netherlands     |  229 |  50 (21.8%) | p.   3 – p.151 |
| WKL      | 2024 | Netherlands     |  243 |  60 (24.7%) | p.   2 – p.235 |
| AKERBP   | 2023 | Norway          |  239 |  79 (33.1%) | p.   2 – p.238 |
| ORK      | 2024 | Norway          |  324 | 105 (32.4%) | p.   7 – p.246 |
| TGS      | 2022 | Norway          |  156 |  20 (12.8%) | p.   2 – p.153 |
| TGS      | 2023 | Norway          |  169 |  25 (14.8%) | p.   2 – p.167 |
| YAR      | 2023 | Norway          |  354 | 100 (28.2%) | p.   3 – p.349 |
| YAR      | 2024 | Norway          |  345 | 119 (34.5%) | p.   2 – p.335 |
| AENA     | 2022 | Spain           |  364 | 106 (29.1%) | p.   3 – p.355 |
| AENA     | 2023 | Spain           |  413 | 137 (33.2%) | p.   3 – p.413 |
| AENA     | 2024 | Spain           |  309 | 297 (96.1%) | p.   3 – p.302 |
| ALLFG    | 2023 | Spain           |  224 |  23 (10.3%) | p.   2 – p.125 |
| ALLFG    | 2024 | Spain           |  224 |  35 (15.6%) | p.   2 – p.146 |
| ANE      | 2023 | Spain           |  316 | 129 (40.8%) | p.   2 – p.315 |
| ANE      | 2024 | Spain           |   59 |  21 (35.6%) | p.   6 – p.54 |
| CABK     | 2024 | Spain           | 1456 | 296 (20.3%) | p.   2 – p.1427 |
| ENG      | 2022 | Spain           |  345 | 183 (53.0%) | p.   4 – p.345 |
| ENG      | 2024 | Spain           |  358 | 105 (29.3%) | p.   2 – p.356 |
| REP      | 2024 | Spain           |  552 | 199 (36.1%) | p.   2 – p.540 |
| BOL      | 2022 | Sweden          |  136 |  30 (22.1%) | p.   2 – p.130 |
| BOL      | 2023 | Sweden          |  144 |  38 (26.4%) | p.   2 – p.141 |
| BOL      | 2024 | Sweden          |  192 |  94 (49.0%) | p.   2 – p.188 |
| CAST     | 2022 | Sweden          |  184 |  49 (26.6%) | p.   2 – p.120 |
| HMB      | 2022 | Sweden          |  152 |  42 (27.6%) | p.   2 – p.118 |
| HMB      | 2023 | Sweden          |   75 |  33 (44.0%) | p.   3 – p.72 |
| HMB      | 2024 | Sweden          |   87 |  37 (42.5%) | p.   3 – p.84 |
| SEB      | 2022 | Sweden          |  240 |  47 (19.6%) | p.   3 – p.234 |
| SEB      | 2023 | Sweden          |  252 |  71 (28.2%) | p.   2 – p.249 |
| SKA B    | 2022 | Sweden          |  224 |  35 (15.6%) | p.   3 – p.216 |
| SKA B    | 2023 | Sweden          |  226 |  46 (20.4%) | p.   2 – p.216 |
| SKA B    | 2024 | Sweden          |  232 |  42 (18.1%) | p.   3 – p.226 |
| VPLAY B  | 2022 | Sweden          |  153 |  31 (20.3%) | p.   2 – p.143 |
| VPLAY B  | 2023 | Sweden          |  146 |  23 (15.8%) | p.   2 – p.134 |
| VPLAY B  | 2024 | Sweden          |  136 |  26 (19.1%) | p.   2 – p.124 |
| WIHL     | 2022 | Sweden          |  164 |  25 (15.2%) | p.   3 – p.150 |
| WIHL     | 2023 | Sweden          |  168 |  28 (16.7%) | p.   3 – p.154 |
| WIHL     | 2024 | Sweden          |  172 |  32 (18.6%) | p.   3 – p.159 |
| ADEN     | 2024 | Switzerland     |  188 |  15 ( 8.0%) | p.   2 – p.110 |
| BARN     | 2022 | Switzerland     |  177 |  11 ( 6.2%) | p.  13 – p.42 |
| BARN     | 2023 | Switzerland     |  190 |  15 ( 7.9%) | p.  12 – p.52 |
| CFR      | 2022 | Switzerland     |  164 |  11 ( 6.7%) | p.   5 – p.87 |
| SCMN     | 2023 | Switzerland     |  212 |  23 (10.8%) | p.   2 – p.207 |
| SGSN     | 2022 | Switzerland     |  240 |  53 (22.1%) | p.   2 – p.237 |
| SGSN     | 2023 | Switzerland     |  208 |  44 (21.2%) | p.   3 – p.201 |
| SGSN     | 2024 | Switzerland     |  204 |  43 (21.1%) | p.   2 – p.200 |
| UBSG     | 2022 | Switzerland     |  390 |  29 ( 7.4%) | p.   2 – p.387 |
| UBSG     | 2023 | Switzerland     |  430 |  32 ( 7.4%) | p.   2 – p.427 |
| UBSG     | 2024 | Switzerland     |  395 |  20 ( 5.1%) | p.   2 – p.392 |
| ZURN     | 2023 | Switzerland     |  440 |  83 (18.9%) | p.   2 – p.267 |
| ZURN     | 2024 | Switzerland     |  434 |  87 (20.0%) | p.   2 – p.429 |
| AV       | 2022 | United Kingdom  |  345 |  42 (12.2%) | p.   2 – p.343 |
| CPG      | 2023 | United Kingdom  |  236 |  46 (19.5%) | p.   2 – p.235 |
| CPG      | 2024 | United Kingdom  |  236 |  45 (19.1%) | p.   2 – p.235 |
| CTEC     | 2022 | United Kingdom  |  126 |  34 (27.0%) | p.   2 – p.124 |
| CTEC     | 2023 | United Kingdom  |  112 |  32 (28.6%) | p.   2 – p.110 |
| CTEC     | 2024 | United Kingdom  |  109 |  31 (28.4%) | p.   2 – p.108 |
| MKS      | 2023 | United Kingdom  |  236 |  32 (13.6%) | p.   3 – p.181 |
| MKS      | 2024 | United Kingdom  |  111 |  26 (23.4%) | p.   2 – p.84 |
| SGRO     | 2024 | United Kingdom  |  200 |  36 (18.0%) | p.   2 – p.177 |
| SSE      | 2023 | United Kingdom  |  352 | 148 (42.0%) | p.   3 – p.349 |
| ULVR     | 2024 | United Kingdom  |  305 |  89 (29.2%) | p.   4 – p.303 |

---

## Categoría B — Sección identificable

**Criterio:** 1 hit en TOC + ≥5 páginas con contenido ESG.
**Extracción:** localizar primera aparición de cabecera de sección y extraer hasta la siguiente sección mayor. Fiabilidad media-alta.

| Ticker   | Año  | País            | Total | ESG (%)          | Rango páginas       |
|----------|------|:----------------|------:|:-----------------|:--------------------|
| RBI      | 2023 | Austria         |  273 |   7 ( 2.6%) | p.   5 – p.194 |
| VOE      | 2024 | Austria         |  508 | 138 (27.2%) | p.   3 – p.472 |
| COLR     | 2023 | Belgium         |  300 |  51 (17.0%) | p.  22 – p.234 |
| COLR     | 2024 | Belgium         |  264 |  52 (19.7%) | p.  93 – p.242 |
| MELE     | 2022 | Belgium         |  159 |  13 ( 8.2%) | p.   2 – p.150 |
| MELE     | 2023 | Belgium         |  166 |  18 (10.8%) | p.   2 – p.155 |
| NOVO B   | 2022 | Denmark         |  110 |  17 (15.5%) | p.  12 – p.101 |
| NOVO B   | 2023 | Denmark         |  112 |  15 (13.4%) | p.  12 – p.104 |
| TRYG     | 2023 | Denmark         |  190 |  28 (14.7%) | p.   2 – p.90 |
| NSN      | 2024 | Finland         |  246 |  98 (39.8%) | p.   2 – p.245 |
| STER     | 2022 | Finland         |  221 |  92 (41.6%) | p.   2 – p.191 |
| UPM      | 2023 | Finland         |  127 |  59 (46.5%) | p.   2 – p.92 |
| AF       | 2022 | France          |  464 |  92 (19.8%) | p.   2 – p.455 |
| AF       | 2023 | France          |  488 | 106 (21.7%) | p.   2 – p.483 |
| AF       | 2024 | France          |  532 | 134 (25.2%) | p.   2 – p.525 |
| BOL      | 2024 | France          |  364 |  36 ( 9.9%) | p.   3 – p.243 |
| CS       | 2023 | France          |  559 |  91 (16.3%) | p.   2 – p.548 |
| CS       | 2024 | France          |  565 | 128 (22.7%) | p.   2 – p.503 |
| EFGI     | 2024 | France          |  424 | 162 (38.2%) | p.   2 – p.404 |
| EN       | 2023 | France          |  476 |  47 ( 9.9%) | p.   7 – p.451 |
| FR       | 2023 | France          |  468 |  43 ( 9.2%) | p.   9 – p.315 |
| 1COV     | 2022 | Germany         |  338 | 108 (32.0%) | p.   3 – p.333 |
| 1COV     | 2023 | Germany         |  331 | 103 (31.1%) | p.   3 – p.326 |
| ADS      | 2023 | Germany         |   69 |  22 (31.9%) | p.   1 – p.69 |
| BOSS     | 2022 | Germany         |  298 |  15 ( 5.0%) | p.  10 – p.276 |
| BOSS     | 2023 | Germany         |  311 |  20 ( 6.4%) | p.   9 – p.306 |
| BOSS     | 2024 | Germany         |  343 |  45 (13.1%) | p.   9 – p.322 |
| CON      | 2022 | Germany         |  227 |  17 ( 7.5%) | p.   5 – p.224 |
| CON      | 2023 | Germany         |  231 |  14 ( 6.1%) | p.   5 – p.196 |
| CON      | 2024 | Germany         |  340 |  87 (25.6%) | p.   6 – p.305 |
| EVK      | 2022 | Germany         |  232 |  41 (17.7%) | p.   3 – p.229 |
| EVK      | 2023 | Germany         |  244 |  44 (18.0%) | p.  15 – p.241 |
| P911     | 2022 | Germany         |  222 |  43 (19.4%) | p.   4 – p.220 |
| SY1      | 2023 | Germany         |  152 |  40 (26.3%) | p.   5 – p.132 |
| SY1      | 2024 | Germany         |  314 |  78 (24.8%) | p.   5 – p.310 |
| TUI      | 2022 | Germany         |  270 |  25 ( 9.3%) | p.   3 – p.268 |
| TUI      | 2023 | Germany         |  297 |  57 (19.2%) | p.   3 – p.295 |
| TUI      | 2024 | Germany         |  286 | 116 (40.6%) | p.  11 – p.284 |
| GLB      | 2023 | Ireland         |  268 |  57 (21.3%) | p.   3 – p.218 |
| GLB      | 2024 | Ireland         |  256 |  55 (21.5%) | p.  13 – p.205 |
| BRNW     | 2023 | Italy           |  180 |   5 ( 2.8%) | p.   3 – p.77 |
| ENEL     | 2023 | Italy           |  428 | 123 (28.7%) | p.  12 – p.426 |
| TIT      | 2022 | Italy           |  498 |  13 ( 2.6%) | p.   8 – p.484 |
| TIT      | 2023 | Italy           |  451 |  11 ( 2.4%) | p.   7 – p.438 |
| TIT      | 2024 | Italy           |  595 | 112 (18.8%) | p.   5 – p.581 |
| EXO      | 2022 | Netherlands     |  351 |  34 ( 9.7%) | p.   2 – p.342 |
| EXO      | 2023 | Netherlands     |  355 |  35 ( 9.9%) | p.   2 – p.223 |
| EXO      | 2024 | Netherlands     |  278 |  47 (16.9%) | p.   2 – p.277 |
| QIA      | 2023 | Netherlands     |  372 |  32 ( 8.6%) | p.   2 – p.372 |
| STLAM    | 2023 | Netherlands     |  428 |  66 (15.4%) | p.   2 – p.422 |
| STLAM    | 2024 | Netherlands     |  442 |  91 (20.6%) | p.   2 – p.436 |
| STMPA    | 2022 | Netherlands     |  227 |  25 (11.0%) | p.   2 – p.217 |
| STMPA    | 2023 | Netherlands     |  254 |  33 (13.0%) | p.   3 – p.244 |
| UMG      | 2022 | Netherlands     |  337 |  36 (10.7%) | p.   2 – p.327 |
| UMG      | 2023 | Netherlands     |  355 |  48 (13.5%) | p.   3 – p.345 |
| UMG      | 2024 | Netherlands     |  284 |  39 (13.7%) | p.   2 – p.269 |
| WKL      | 2022 | Netherlands     |  237 |  21 ( 8.9%) | p.   6 – p.85 |
| AKERBP   | 2024 | Norway          |  235 |  85 (36.2%) | p.   2 – p.234 |
| YAR      | 2022 | Norway          |  278 |  58 (20.9%) | p.   5 – p.264 |
| ACX      | 2022 | Spain           |  301 |  60 (19.9%) | p.   5 – p.301 |
| ACX      | 2024 | Spain           |  191 |  80 (41.9%) | p.   2 – p.182 |
| ALLFG    | 2022 | Spain           |  182 |  14 ( 7.7%) | p.   7 – p.89 |
| CABK     | 2023 | Spain           | 1206 | 224 (18.6%) | p.  10 – p.1027 |
| DIA      | 2023 | Spain           |  211 |  31 (14.7%) | p.   4 – p.207 |
| MRL      | 2023 | Spain           |  142 |  23 (16.2%) | p.   8 – p.103 |
| CAST     | 2023 | Sweden          |  164 |  41 (25.0%) | p.   2 – p.146 |
| CAST     | 2024 | Sweden          |  175 |  44 (25.1%) | p.   2 – p.154 |
| SEB      | 2024 | Sweden          |  307 | 100 (32.6%) | p.   3 – p.305 |
| ADEN     | 2022 | Switzerland     |  198 |  10 ( 5.1%) | p.   4 – p.181 |
| ADEN     | 2023 | Switzerland     |  180 |   9 ( 5.0%) | p.   2 – p.57 |
| ALC      | 2023 | Switzerland     |  276 |   6 ( 2.2%) | p.   4 – p.144 |
| BARN     | 2024 | Switzerland     |  150 |   6 ( 4.0%) | p.  11 – p.22 |
| CFR      | 2023 | Switzerland     |  160 |   6 ( 3.8%) | p.   5 – p.86 |
| CFR      | 2024 | Switzerland     |  164 |   6 ( 3.7%) | p.   6 – p.60 |
| LONN     | 2022 | Switzerland     |  234 |  40 (17.1%) | p.   3 – p.231 |
| LONN     | 2023 | Switzerland     |  112 |   6 ( 5.4%) | p.  12 – p.91 |
| LONN     | 2024 | Switzerland     |  112 |   9 ( 8.0%) | p.  13 – p.101 |
| SCMN     | 2022 | Switzerland     |  186 |   5 ( 2.7%) | p.   2 – p.90 |
| SCMN     | 2024 | Switzerland     |  230 |  27 (11.7%) | p.   2 – p.225 |
| AV       | 2023 | United Kingdom  |  372 |  52 (14.0%) | p.   3 – p.371 |
| AV       | 2024 | United Kingdom  |  332 |  43 (13.0%) | p.   3 – p.330 |
| BBY      | 2022 | United Kingdom  |  260 |  44 (16.9%) | p.   3 – p.189 |
| BBY      | 2023 | United Kingdom  |  262 |  51 (19.5%) | p.   3 – p.191 |
| BBY      | 2024 | United Kingdom  |  284 |  49 (17.3%) | p.   3 – p.200 |
| CPG      | 2022 | United Kingdom  |  226 |  46 (20.4%) | p.   2 – p.225 |
| HSBA     | 2022 | United Kingdom  |  432 | 104 (24.1%) | p.   2 – p.430 |
| HSBA     | 2023 | United Kingdom  |  450 | 106 (23.6%) | p.   2 – p.447 |
| HSBA     | 2024 | United Kingdom  |  460 |  86 (18.7%) | p.   2 – p.457 |
| III      | 2024 | United Kingdom  |  226 |  45 (19.9%) | p.  12 – p.207 |
| JD       | 2024 | United Kingdom  |  264 |  37 (14.0%) | p.   3 – p.156 |
| LSEG     | 2022 | United Kingdom  |  256 |  31 (12.1%) | p.   7 – p.255 |
| LSEG     | 2023 | United Kingdom  |  264 |  27 (10.2%) | p.  13 – p.263 |
| LSEG     | 2024 | United Kingdom  |  260 |  30 (11.5%) | p.  11 – p.256 |
| MKS      | 2022 | United Kingdom  |  216 |  28 (13.0%) | p.   3 – p.140 |
| SGE      | 2022 | United Kingdom  |  296 |  44 (14.9%) | p.   5 – p.295 |
| SGE      | 2023 | United Kingdom  |  276 |  38 (13.8%) | p.   2 – p.275 |
| SGE      | 2024 | United Kingdom  |  268 |  33 (12.3%) | p.   2 – p.267 |
| SGRO     | 2022 | United Kingdom  |  220 |  43 (19.5%) | p.   2 – p.218 |
| SGRO     | 2023 | United Kingdom  |  202 |  38 (18.8%) | p.   2 – p.178 |
| SSE      | 2022 | United Kingdom  |  360 | 156 (43.3%) | p.   2 – p.342 |
| SSE      | 2024 | United Kingdom  |  347 | 138 (39.8%) | p.   2 – p.344 |
| TPK      | 2022 | United Kingdom  |  192 |  43 (22.4%) | p.   3 – p.187 |
| TPK      | 2023 | United Kingdom  |  211 |  38 (18.0%) | p.   2 – p.208 |
| TPK      | 2024 | United Kingdom  |  192 |  37 (19.3%) | p.   3 – p.188 |
| VOD      | 2022 | United Kingdom  |  260 |  36 (13.8%) | p.   2 – p.256 |
| VOD      | 2023 | United Kingdom  |  252 |  43 (17.1%) | p.   2 – p.251 |
| VOD      | 2024 | United Kingdom  |  272 |  46 (16.9%) | p.   2 – p.268 |

---

## Categoría C — Contenido disperso (sin sección etiquetada)

**Criterio:** 0 hits en TOC, pero ≥3 páginas con contenido ESG.
**Patrón predominante:** documentos franceses (URDs AMF), algunos holandeses y españoles donde la sostenibilidad está integrada transversalmente.
**Extracción:** dos opciones:
1. Documento completo (más sencillo, introduce algo de ruido financiero)
2. Filtrado por párrafos con densidad ESG ≥ 2 keywords (más limpio, riesgo de perder contexto)

| Ticker   | Año  | País            | Total | ESG (%)          | p_ini detectada     |
|----------|------|:----------------|------:|:-----------------|:--------------------|
| VOE      | 2022 | Austria         |  240 |  18 ( 7.5%) | p.38 |
| VOE      | 2023 | Austria         |  256 |  27 (10.5%) | p.38 |
| TRYG     | 2022 | Denmark         |  132 |   8 ( 6.1%) | p.19 |
| NSN      | 2023 | Finland         |  263 | 128 (48.7%) | p.31 |
| UPM      | 2022 | Finland         |  125 |  55 (44.0%) | p.59 |
| BOL      | 2022 | France          |  372 |  19 ( 5.1%) | p.— |
| BOL      | 2023 | France          |  356 |  18 ( 5.1%) | p.56 |
| CS       | 2022 | France          |  530 |  68 (12.8%) | p.36 |
| DG       | 2022 | France          |  217 |  31 (14.3%) | p.— |
| DG       | 2023 | France          |  223 |  31 (13.9%) | p.105 |
| DG       | 2024 | France          |  456 |  53 (11.6%) | p.48 |
| EFGI     | 2022 | France          |  177 |  20 (11.3%) | p.87 |
| EFGI     | 2023 | France          |  400 | 131 (32.8%) | p.23 |
| EN       | 2022 | France          |  448 |  33 ( 7.4%) | p.130 |
| EN       | 2024 | France          |  640 | 142 (22.2%) | p.77 |
| ENGIE    | 2022 | France          |  186 |  18 ( 9.7%) | p.45 |
| ENGIE    | 2023 | France          |  170 |  21 (12.4%) | p.39 |
| ENGIE    | 2024 | France          |  169 |  20 (11.8%) | p.39 |
| FR       | 2022 | France          |  505 |  38 ( 7.5%) | p.— |
| GFC      | 2022 | France          |  346 |  30 ( 8.7%) | p.— |
| GFC      | 2023 | France          |  373 |  27 ( 7.2%) | p.— |
| GFC      | 2024 | France          |  358 |  21 ( 5.9%) | p.180 |
| KER      | 2022 | France          |  454 |  32 ( 7.0%) | p.172 |
| KER      | 2023 | France          |  448 |  36 ( 8.0%) | p.183 |
| KER      | 2024 | France          |  445 |  43 ( 9.7%) | p.89 |
| ORAN     | 2022 | France          |   71 |  22 (31.0%) | p.24 |
| ORAN     | 2023 | France          |  496 |  43 ( 8.7%) | p.21 |
| ORAN     | 2024 | France          |  558 |  66 (11.8%) | p.23 |
| PERP     | 2022 | France          |   67 |  11 (16.4%) | p.— |
| PERP     | 2023 | France          |  124 |   3 ( 2.4%) | p.— |
| PERP     | 2024 | France          |  126 |  17 (13.5%) | p.81 |
| SAF      | 2024 | France          |  546 |  63 (11.5%) | p.152 |
| WEND     | 2022 | France          |  492 |  47 ( 9.6%) | p.— |
| WEND     | 2023 | France          |  404 |  33 ( 8.2%) | p.86 |
| WEND     | 2024 | France          |  432 |  58 (13.4%) | p.63 |
| BNR      | 2024 | Germany         |  296 |  59 (19.9%) | p.21 |
| MBG      | 2022 | Germany         |  363 |  37 (10.2%) | p.84 |
| NEM      | 2023 | Germany         |  180 |  13 ( 7.2%) | p.17 |
| SY1      | 2022 | Germany         |  188 |   6 ( 3.2%) | p.16 |
| FLTR     | 2022 | Ireland         |  304 |  33 (10.9%) | p.73 |
| FLTR     | 2023 | Ireland         |  365 |  23 ( 6.3%) | p.20 |
| FLTR     | 2024 | Ireland         |  189 |   4 ( 2.1%) | p.6 |
| GLB      | 2022 | Ireland         |  264 |  51 (19.3%) | p.52 |
| BRNW     | 2022 | Italy           |  185 |   4 ( 2.2%) | p.3 |
| CPR      | 2022 | Italy           |  321 |  37 (11.5%) | p.56 |
| CPR      | 2023 | Italy           |  308 |  37 (12.0%) | p.57 |
| QIA      | 2022 | Netherlands     |  246 |  12 ( 4.9%) | p.84 |
| AKERBP   | 2022 | Norway          |  129 |  12 ( 9.3%) | p.21 |
| ORK      | 2022 | Norway          |  358 |  49 (13.7%) | p.42 |
| ORK      | 2023 | Norway          |  323 |  82 (25.4%) | p.37 |
| TGS      | 2024 | Norway          |  217 |  46 (21.2%) | p.31 |
| ACX      | 2023 | Spain           |  148 |  35 (23.6%) | p.43 |
| ANE      | 2022 | Spain           |   34 |  18 (52.9%) | p.22 |
| CABK     | 2022 | Spain           |  844 | 114 (13.5%) | p.70 |
| DIA      | 2024 | Spain           |  100 |   5 ( 5.0%) | p.— |
| ENG      | 2023 | Spain           |  316 |  96 (30.4%) | p.35 |
| MRL      | 2022 | Spain           |  144 |  27 (18.8%) | p.83 |
| MRL      | 2024 | Spain           |  138 |  23 (16.7%) | p.77 |
| REP      | 2022 | Spain           |  565 |  35 ( 6.2%) | p.203 |
| REP      | 2023 | Spain           |  611 |  29 ( 4.7%) | p.399 |
| ALC      | 2022 | Switzerland     |  266 |   7 ( 2.6%) | p.— |
| ALC      | 2024 | Switzerland     |  274 |   4 ( 1.5%) | p.65 |
| ZURN     | 2022 | Switzerland     |  392 |  72 (18.4%) | p.51 |
| III      | 2022 | United Kingdom  |  222 |  34 (15.3%) | p.45 |
| III      | 2023 | United Kingdom  |  238 |  45 (18.9%) | p.26 |
| JD       | 2022 | United Kingdom  |  240 |  30 (12.5%) | p.31 |
| JD       | 2023 | United Kingdom  |  276 |  37 (13.4%) | p.66 |
| ULVR     | 2022 | United Kingdom  |  241 |  49 (20.3%) | p.35 |
| ULVR     | 2023 | United Kingdom  |  261 |  43 (16.5%) | p.49 |

---

## Categoría D — ESG muy incipiente (n=2)

Documentos válidos de la empresa correcta pero con contenido ESG prácticamente nulo. Decisión metodológica requerida.

| Ticker | Año  | Total | ESG pp | Contexto | Recomendación |
|--------|------|------:|-------:|----------|---------------|
| NEM    | 2022 |  178  |   1    | Nemetschek (software): ESG muy incipiente en 2022 | Excluir del análisis NLP; documentar como limitación |

---

## Categoría E — Sin contenido ESG detectado (n=2)

Requieren acción antes de la Fase 5.

| Ticker | Año  | Total | Problema | Acción |
|--------|------|------:|----------|--------|
| DIA    | 2022 |  207  | Informe financiero-contable; Dia en reestructuración, ESG mínimo | Buscar EINF 2022 separado o excluir con nota metodológica |

---

## Patrones por país

| País | Docs | Cat A | Cat B | Cat C | Cat D+E | % útil |
|------|-----:|------:|------:|------:|--------:|-------:|
| Austria         |    6 |     2 |     2 |     2 |       0 | 100% |
| Belgium         |    9 |     5 |     4 |     0 |       0 | 100% |
| Denmark         |    9 |     5 |     3 |     1 |       0 | 100% |
| Finland         |    9 |     4 |     3 |     2 |       0 | 100% |
| France          |   45 |     6 |     9 |    30 |       0 | 100% |
| Germany         |   42 |    20 |    17 |     4 |       1 | 98% |
| Ireland         |    6 |     0 |     2 |     4 |       0 | 100% |
| Italy           |   15 |     7 |     5 |     3 |       0 | 100% |
| Netherlands     |   18 |     5 |    12 |     1 |       0 | 100% |
| Norway          |   12 |     6 |     2 |     4 |       0 | 100% |
| Spain           |   27 |    11 |     6 |     9 |       1 | 96% |
| Sweden          |   21 |    18 |     3 |     0 |       0 | 100% |
| Switzerland     |   27 |    14 |    10 |     3 |       0 | 100% |
| United Kingdom  |   45 |    11 |    28 |     6 |       0 | 100% |

---

## Flujo de extracción recomendado para Fase 4

```python
# Para cada PDF en el corpus:
def clasificar_y_extraer(pdf_path, cat, p_ini, p_fin):

    if cat == 'A':
        # Extracción directa por rango de páginas del TOC
        return extraer_paginas(pdf_path, p_ini, p_fin)

    elif cat == 'B':
        # Localizar cabecera en cuerpo y extraer hasta siguiente sección
        p_start = localizar_cabecera_sostenibilidad(pdf_path)
        p_end   = localizar_siguiente_seccion_mayor(pdf_path, p_start)
        return extraer_paginas(pdf_path, p_start, p_end)

    elif cat == 'C':
        # Documento completo + filtrado por densidad ESG
        texto_completo = extraer_todo(pdf_path)
        return filtrar_parrafos_esg(texto_completo, min_keywords=2)

    elif cat in ('D', 'E'):
        # Marcar para revisión manual — no procesar automáticamente
        return None
```

### Keywords de cabecera por idioma

```python
CABECERAS = {
    'en': ['Sustainability Statement', 'Non-Financial Statement',
           'Sustainability Report', 'Sustainability Review', 'ESG Report'],
    'de': ['Nachhaltigkeitsbericht', 'Nichtfinanzielle Erklärung',
           'Nachhaltigkeitserklärung', 'Nichtfinanzieller Bericht'],
    'fr': ['Rapport de durabilité', 'Informations non financières',
           'Déclaration de performance extra-financière'],
    'it': ['Relazione di Sostenibilità', 'Dichiarazione non finanziaria'],
    'es': ['Informe de Sostenibilidad', 'Estado de Información No Financiera', 'EINF'],
    'nl': ['Duurzaamheidsverklaring', 'Niet-financiële verklaring'],
}
```

---

## Pendientes antes de Fase 4

| Ticker | Año | Problema | Acción | Prioridad |
|--------|-----|----------|--------|-----------|
| DIA | 2022 | Sin ESG (reestructuración) | Buscar EINF en CNMV o excluir con nota metodológica | 🟡 Baja |
| NEM | 2022 | ESG incipiente (1pp) | Excluir del análisis NLP; documentar como limitación | 🟡 Baja |

> OR 2023/2024, SAF 2022/2023 y LONN 2022 ya fueron corregidos (v3). Solo quedan decisiones metodológicas.

Ver instrucciones detalladas en `docs/guia_correcciones_pdfs.md`.

---

*Script: `/tmp/audit_fast.py` — pymupdf + multiprocessing (8 workers) | ~3 min para 291 PDFs*
*Para regenerar: `/opt/homebrew/Caskroom/miniconda/base/envs/tfg-ade/bin/python /tmp/audit_fast.py`*
