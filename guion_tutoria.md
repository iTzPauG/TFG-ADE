# Guion de tutoría — Entender y explicar el TFG de palabra

> Documento de estudio para preparar la llamada con el tutor. Escrito para explicarlo
> hablando, sin tecnicismos de informática. Todas las cifras son las reales del proyecto.
> Léelo de arriba abajo una vez; luego usa los apartados 11–13 como "chuleta" final.

---

## 0. La idea del trabajo en una sola frase

> **"Uso técnicas de inteligencia artificial que leen texto para analizar CÓMO las grandes
> empresas europeas hablan de sostenibilidad en sus informes, y busco señales de que ese
> discurso sea más 'humo' que sustancia (greenwashing), especialmente ahora que ha entrado
> en vigor la nueva ley europea (CSRD)."**

Si solo te quedas con una frase, es esa. Todo lo demás la desarrolla.

---

## 1. El problema de fondo (el "por qué" del trabajo)

Dos cosas están pasando a la vez en Europa:

1. **Greenwashing.** Muchas empresas comunican que son muy sostenibles, pero a veces ese
   mensaje es vago, optimista y sin datos que lo respalden. Es lo que la literatura llama
   *"cheap talk"* (hablar barato): promesas que no cuestan nada porque no se concretan.

2. **Una ley nueva muy potente: la CSRD.** Hasta 2023 las empresas reportaban su
   sostenibilidad bajo una norma antigua y "blanda" (la **NFRD**): cada empresa elegía
   qué contar y cómo, sin obligación de detalle. Desde el ejercicio **2024**, las grandes
   empresas están obligadas por la **CSRD** a reportar de forma mucho más estricta,
   estandarizada (con los estándares **ESRS**) y auditada.

**Mi trabajo conecta las dos cosas:** mido, con el texto de los informes, si el discurso
de sostenibilidad cambia con la llegada de la CSRD y si hay señales textuales de
greenwashing. La pregunta de fondo es: *¿la nueva ley hace que las empresas comuniquen
mejor (más concreto, más datos), o simplemente escriben más sin decir más?*

**Referente académico** (por si lo pregunta): me baso en **Bingler et al. (2022),
"Cheap talk and cherry-picking"**, que hicieron algo parecido con divulgaciones climáticas
usando un modelo llamado ClimateBERT. Mi marco teórico también usa a Loughran & McDonald
(2011), Hahn & Lülfs (2014) y Michelon et al. (2015).

---

## 2. Las 4 preguntas de investigación (RQ), en cristiano

El trabajo gira en torno a 4 preguntas. Apréndete estas versiones "de andar por casa":

| Nº | Pregunta formal | Traducción de andar por casa |
|----|-----------------|------------------------------|
| **RQ1** | ¿Qué temas predominan en los informes? | *"¿De qué hablan exactamente cuando hablan de sostenibilidad?"* |
| **RQ2** | ¿Hay diferencias por sector y país? | *"¿Habla igual un banco que una eléctrica? ¿Una empresa alemana que una británica?"* |
| **RQ3** | ¿Qué factores predicen más concreción / qué relación hay entre tono y concreción? | *"¿Las empresas más grandes son más concretas? ¿Las que suenan más optimistas son menos concretas (señal de greenwashing)?"* |
| **RQ4** | ¿Cómo cambia el reporting de NFRD (2022-23) a CSRD (2024)? | *"¿Qué cambia en la forma de comunicar cuando entra la nueva ley?"* |

RQ4 es probablemente la más vistosa porque captura un cambio real de régimen legal que está
ocurriendo *ahora mismo* — y tengo datos antes (2022-23) y después (2024).

---

## 3. ⭐ Por qué ANNUAL REPORTS y no informes de sostenibilidad (la pregunta clave)

Esta es la pregunta que más probablemente te haga el tutor. Tienes **cuatro argumentos**,
y el primero es el más fuerte. Apréndetelos en orden.

### Argumento 1 — El legal (el definitivo)

> **"Porque, por ley, la información de sostenibilidad NO es un documento aparte: es una
> parte obligatoria del informe de gestión (el management report), que va dentro del informe
> anual."**

Tanto la antigua NFRD como la nueva CSRD (artículos **19a y 29a** de la Directiva contable)
obligan a meter el "estado de información no financiera" / "estado de sostenibilidad"
**dentro del informe de gestión**, que es parte del informe anual integrado. Es decir: el
sitio donde la regulación realmente "muerde" es el informe anual, no el folleto de
sostenibilidad. Si quiero estudiar el efecto de la ley, tengo que ir a donde la ley aplica.

### Argumento 2 — El de comparabilidad

> **"El informe anual es obligatorio y homogéneo; el informe de sostenibilidad separado es
> voluntario y cada empresa lo hace como quiere."**

- El **informe de sostenibilidad standalone** es voluntario: unas empresas lo publican,
  otras no, y cambia de un año a otro. No puedo comparar bien algo que a veces existe y a
  veces no.
- El **informe anual** existe siempre, para todas, todos los años. Eso me permite comparar
  empresa con empresa y, sobre todo, **2022 con 2024** (el corazón de RQ4). Sin esa base
  común, RQ4 sería imposible.

### Argumento 3 — El anti-greenwashing (muy elegante para tu tema)

> **"El folleto de sostenibilidad separado es justo donde es MÁS fácil hacer greenwashing:
> es marketing, va con fotos bonitas y lenguaje promocional. El estado de sostenibilidad
> dentro del informe anual está regulado y auditado, así que es la prueba más exigente."**

Si yo busco "humo", buscarlo en el documento de marketing sería hacer trampa (ahí siempre lo
hay). Buscarlo en el documento legalmente regulado y auditado es mucho más riguroso: si ahí
también aparece falta de concreción, el hallazgo tiene mucho más valor.

### Argumento 4 — El práctico

> **"Las grandes del STOXX 600 publican mayoritariamente UN único documento integrado que
> ya une lo financiero y lo no financiero. Descargar dos documentos por empresa duplicaría
> el trabajo y obligaría a fusionar secciones a mano."** (Es la Decisión 008 del proyecto.)

### Matiz importante que debes saber decir

No analizo el informe anual entero a lo bruto. **Dentro** de cada informe anual, mi programa
**aísla dos trozos**:
- **`mr`** = el informe de gestión SIN la parte de sostenibilidad (la narrativa de
  negocio/estrategia/gobernanza).
- **`sus`** = la subsección de sostenibilidad aislada.

Y casi todo el análisis fino de greenwashing (RQ3) lo hago sobre **`sus`**, la parte de
sostenibilidad. Pero esa parte la extraigo *de dentro del informe anual*, que es lo correcto
legalmente. Resumen de una frase para el tutor:

> *"Uso el informe anual porque ahí es donde la ley obliga a meter la sostenibilidad, pero
> dentro de él aíslo quirúrgicamente la sección de sostenibilidad para analizarla."*

---

## 4. La otra gran decisión: SOLO texto, CERO ratings ESG de terceros

Otra pregunta típica: *"¿por qué no usas las notas ESG de MSCI o Sustainalytics?"*

> **"Porque eso sería un argumento circular. Esas notas (MSCI, Sustainalytics, Refinitiv) ya
> son la opinión de una agencia sobre si la empresa es sostenible. Si yo las usara para
> 'validar' el texto, estaría midiendo el texto contra otra opinión, no contra la realidad.
> Mi aportación es construir señales DIRECTAMENTE desde el texto, de forma transparente y
> reproducible."**

Todo lo que mido sale del propio lenguaje de los informes: diccionarios de palabras y
modelos de lenguaje. Nada de notas externas. (Es la Decisión 001, la regla número 1 del
proyecto.)

---

## 5. Qué hace cada "técnica de IA" (explicado para ADE)

No necesitas saber programar para explicar esto. Cada herramienta es como un "empleado
especialista" que lee los informes y te devuelve un dato. Aquí está el equipo:

| Herramienta | Qué es, en cristiano | Qué me da |
|-------------|----------------------|-----------|
| **Diccionario ESRS** (propio) | Una lista de palabras clave por cada tema de la ley (clima, agua, empleados…). Cuento cuántas aparecen. | Cuánto "cubre" cada empresa cada pilar de la normativa ESRS. |
| **Diccionario Loughran-McDonald** | Un diccionario clásico de finanzas que clasifica palabras en "positivas", "negativas", "de incertidumbre", "de matiz/condicionales"… | El **tono** y, sobre todo, el **hedging** (cuánto se cubre las espaldas con "podría", "quizá"). |
| **TF-IDF** | Una fórmula que detecta las palabras "características" de un texto (las que aparecen mucho aquí pero poco en el resto). | Las palabras y frases que mejor distinguen un grupo (p. ej. el bigrama estrella de 2024). |
| **LDA** | Un método estadístico que agrupa los párrafos en "temas" automáticamente, por las palabras que suelen ir juntas. | Los **temas** de los informes (RQ1). Encontré 15 temas. |
| **BERTopic** | Lo mismo que LDA pero más moderno: agrupa por *significado*, no solo por palabras. | Una segunda lista de temas, más fina (339), para **confirmar** los de LDA. |
| **FinBERT** | Un modelo entrenado con textos financieros que dice si una frase suena positiva, negativa o neutra. | El **tono financiero** general. |
| **ClimateBERT** | Un modelo especializado en clima. Detecta si una frase es climática y, si lo es, si habla de riesgo u oportunidad, si es un compromiso, y si es específica (con cifras/fechas). | El análisis fino del discurso climático: **especificidad, compromiso, riesgo/oportunidad**. |
| **FinBERT-ESG-9** | Otro modelo que clasifica cada frase en 9 categorías ESG. | Una tercera fuente para triangular de qué temas se habla. |

**Idea clave que mola decir:** uso **varios modelos independientes** para lo mismo, y cuando
todos apuntan en la misma dirección, el hallazgo es robusto. Eso se llama **triangulación**
y es uno de los puntos fuertes metodológicos del trabajo.

### El GW_index (mi "índice de greenwashing") — explícalo bien

Es mi indicador estrella. Lo construí yo combinando 4 señales del texto (Decisión 025).
La fórmula, en palabras:

> **GW_index = (cuánto se cubre las espaldas) + (promesas a futuro sin ninguna cifra)
> − (frases con datos cuantitativos) − (especificidad climática)**

Es decir, el índice **sube** cuando una empresa usa mucho lenguaje vago y de cobertura, hace
promesas sin números, y baja en datos concretos y especificidad. **GW_index alto = más
"humo", menos sustancia.** Es una forma transparente de operacionalizar el "cheap talk" sin
recurrir a notas externas.

---

## 6. El recorrido del trabajo (las 7 fases)

Para que entiendas el orden lógico de lo que hiciste:

1. **Fase 1 — Marco teórico y normativo.** Estudiar greenwashing, CSRD/ESRS/Taxonomía, y la
   literatura. Definir las 4 RQ.
2. **Fase 2 — La muestra.** Elegir 97 empresas del STOXX 600 de forma estratificada (ver §7).
3. **Fase 3 — Recolección.** Descargar los 291 informes anuales (97 × 3 años).
4. **Fase 4 — Extracción y limpieza.** Sacar el texto de los PDF, traducir/sustituir los no
   ingleses por su versión oficial inglesa, y aislar `mr` y `sus`. Resultado: el "corpus".
5. **Fase 5 — Análisis con IA (el grueso).** Cinco bloques, 5A a 5E (ver §8). **Está completa.**
6. **Fase 6 — Dashboard.** Una página web (HTML) interactiva para explorar todos los
   resultados. **Lista.**
7. **Fase 7 — Redacción del TFG.** Pendiente. Es lo que viene ahora.

**Dónde estás:** análisis terminado, dashboard hecho, toca escribir la memoria.

---

## 7. La muestra (los datos)

- **97 empresas** del **STOXX Europe 600** (las grandes cotizadas europeas), × **3 años**
  (2022, 2023, 2024) = **291 informes**. Tras quitar 2 que no tenían contenido de
  sostenibilidad analizable, el corpus de análisis son **289 documentos** de sostenibilidad.
- **14 países**, todos los grandes sectores (clasificación ICB).
- **Muestreo estratificado por sector** (~5 empresas por sector) con un **tope de 15 por
  país** para que no domine Reino Unido (que de forma natural pesa un 32%). Semilla aleatoria
  fija (`random_state=42`) para que sea **reproducible**.
- Todos los informes se homogeneizaron a **inglés** (los modelos están entrenados en inglés).
  Los 27 que estaban en francés/español se **sustituyeron por la versión oficial en inglés
  publicada por la propia empresa** — nunca traducción automática (rompería los modelos).

**Por qué 2024 es tan importante:** es el **primer ejercicio obligatorio de CSRD** para las
grandes empresas. Tener 2022-23 (régimen viejo NFRD) y 2024 (régimen nuevo CSRD) es lo que
permite responder RQ4 con un "antes y después" real.

---

## 8. Resultados y hallazgos por pregunta (lo importante)

Aquí están los outcomes reales. Para cada bloque te doy el dato y la frase para decirlo.

### Fase 5A — Descriptivos + cobertura ESRS

- **Hallazgo estrella:** la sección de sostenibilidad **más que se duplica** en dos años:
  pasa de **10.947 a 23.068 palabras de media (+111%)** entre 2022 y 2024. La parte de
  negocio (`mr`) se queda **estable** (~37.000). → *El crecimiento es específico de
  sostenibilidad, justo lo que predice la llegada de la CSRD.*
- **Cobertura ESRS:** todas las categorías de la ley crecen 2022→2024. Las más cubiertas son
  **E1 (clima)** y **S1 (plantilla propia)**; la menos, **E2 (contaminación)** — porque
  contaminar/medir contaminación solo es "material" para las industriales.
- **Dato lingüístico bonito:** la expresión *"sustainability statement"* pasa de ser
  irrelevante en 2022 a ser **la nº 1 en 2024**. Es la huella léxica del cambio de la NFRD
  ("non-financial statement") a la CSRD ("sustainability statement").

### Fase 5B — Temas (RQ1)

- **LDA** encontró **15 temas** coherentes, que mapeé a las categorías de la ley: clima (E1),
  agua/biodiversidad/contaminación (E2-E4), economía circular (E5), plantilla (S1), cadena de
  valor (S2-S3), gobernanza (G1), y varios temas de marco CSRD.
- **BERTopic** encontró 339 temas más finos que **confirman** los de LDA (triangulación).
- **Hallazgo estrella RQ4:** el tema **"doble materialidad / IROs" se multiplica por 8,2**
  (de 104 a 865 párrafos de 2022 a 2024). Es la señal textual más fuerte de todo el trabajo
  del cambio de ley. (La Taxonomía UE crece ×1,8; el riesgo climático físico ×1,7.)

> #### ¿Qué es la "doble materialidad"? (apréndete esto bien)
>
> Es **el principio estrella que introduce la CSRD** y que **no existía bajo la NFRD**.
> "Materialidad" en contabilidad significa *"lo que es relevante / importante y por tanto hay
> que reportar"*. La CSRD dice que la sostenibilidad hay que mirarla desde **dos direcciones a
> la vez** (por eso "doble"):
>
> 1. **Materialidad de impacto — "de dentro hacia fuera".** Cómo la empresa **afecta** al
>    mundo: sus emisiones, su consumo de agua, sus condiciones laborales, su impacto en
>    comunidades… Es la mirada clásica de sostenibilidad: *"¿qué daño o bien hace la empresa
>    al planeta y a la sociedad?"*
>
> 2. **Materialidad financiera — "de fuera hacia dentro".** Cómo la sostenibilidad **afecta al
>    negocio y al dinero** de la empresa: riesgos y oportunidades. Por ejemplo, una sequía que
>    encarece su materia prima, una nueva ley que la obliga a invertir, o un producto verde que
>    le abre un mercado. Es la mirada del inversor: *"¿cómo influye el clima/lo social en los
>    resultados y el valor de la empresa?"*
>
> **Ejemplo concreto para explicarlo de palabra (una eléctrica):**
> - *Impacto (dentro→fuera):* la central de carbón **emite CO₂** que contribuye al cambio
>   climático. → La empresa daña al entorno.
> - *Financiera (fuera→dentro):* ese mismo cambio climático trae **nuevos impuestos al CO₂ y
>   olas de calor** que disparan la demanda y rompen la red. → El entorno daña (o beneficia) a
>   la empresa.
>
> La CSRD obliga a reportar **las dos**. La NFRD, en la práctica, solo empujaba la primera. Por
> eso, cuando en 2024 aparece de golpe muchísimo texto sobre "doble materialidad", "IROs"
> (Impacts, Risks & Opportunities = impactos, riesgos y oportunidades) y "evaluación de
> materialidad", **es la huella lingüística directa de que las empresas están aplicando la
> CSRD**: están escribiendo justo el lenguaje que la nueva ley exige y la antigua no pedía.
> Que ese tema se multiplique por 8 en dos años es, por tanto, la prueba textual más limpia de
> RQ4 (el cambio de régimen NFRD→CSRD).

### Fase 5C — Tono y sentimiento

- Analicé **285.509 frases**. El **41%** son climáticas (estable los 3 años).
- **El tono se vuelve MENOS optimista con el tiempo**, y lo confirman **tres modelos
  distintos a la vez**:
  - FinBERT (tono general): **0,202 → 0,153** (−24%).
  - Loughran-McDonald: bajan las palabras positivas, suben las de incertidumbre y riesgo.
  - ClimateBERT (clima): el discurso de **oportunidad baja (21,5%→16,2%)** y el de **riesgo
    sube (10,4%→17,2%)**. Los **compromisos explícitos bajan (34,5%→27,5%)** y la
    **especificidad baja ligeramente (28,1%→25,7%)**.

### Fase 5D — El GW_index (greenwashing)

- El **GW_index sube claramente: −0,196 (2022) → +0,521 (2024)**. Es decir, en agregado el
  discurso 2024 tiene **más señales de "cheap talk"** que el de 2022.
- ¿Por qué sube? Por **más hedging** (cubrirse las espaldas), **menos especificidad** y —el
  hallazgo nuevo— **menos proporción de frases con cifras**. O sea: *escriben mucho más
  (+111% palabras) pero NO proporcionalmente más datos.*
- Es **estadísticamente significativo** (test de Wilcoxon, p = 0,021).

### Fase 5E — Estadística (RQ2, RQ3, RQ4)

- **RQ2 (sector/país):** hay diferencias **significativas** (p < 0,001). **Tecnología y
  bancos** tienen el GW_index más alto (más humo, menos concreción climática); **inmobiliarias
  (Real Estate)** son las más específicas. Por geografía, la **Europa central** (Francia,
  Italia) es más concreta que los **nórdicos y UK**.
- **RQ3 (regresiones):** dos hallazgos potentes:
  1. **Las empresas más grandes tienen MENOS greenwashing** (coef. −0,268, p = 0,024). A más
     tamaño, menos "cheap talk".
  2. La relación **especificidad → tono es POSITIVA** (p = 0,003). Esto es importante: la
     hipótesis ingenua de greenwashing diría "más optimismo = menos concreción". Pues **no se
     cumple así**: las empresas que hablan de clima de forma concreta tienden a tener tono más
     positivo (porque la concreción suele acompañar a logros reales que se cuentan en positivo).
     **Matizar esto te da nota: significa que el greenwashing no es tan simple como suena.**
- **RQ4 (test pareado 2022 vs 2024):** confirma con significación formal que en 2024, frente
  a 2022: **más extensión, menos tono optimista, más riesgo climático, menos oportunidad, y
  GW_index más alto** (todos p < 0,05). La caída de especificidad es la única señal "marginal"
  (p ≈ 0,09).

---

## 9. Hallazgos SORPRENDENTES (los que lucen en la tutoría)

Estos son los que debes destacar porque van contra la intuición:

1. **El discurso se vuelve menos optimista, no más.** Lo intuitivo sería "con la presión de
   la sostenibilidad, las empresas se ponen más triunfalistas". Pues al revés: **tres modelos
   independientes coinciden** en que el tono baja 2022→2024. La CSRD parece empujar a un
   lenguaje más cauto, de riesgos y cumplimiento.

2. **Más texto, pero no más datos.** El volumen de la sección de sostenibilidad sube +111%,
   pero la **proporción de frases con cifras BAJA**. Es la prueba más directa de que parte
   del crecimiento es "relleno normativo" (definiciones, metodología, gobernanza del proceso)
   más que nuevos compromisos cuantificados. **Este es probablemente tu hallazgo más fino.**

3. **El "efecto CSRD" del GW_index es en parte composición, no magia.** El subidón del
   GW_index en 2024 deja de ser significativo cuando controlo por sector, tamaño y región.
   Traducción: parte del cambio agregado se explica por **qué tipo de empresas** hay en la
   muestra, no por un efecto uniforme de la ley sobre todas. Es un matiz honesto que da
   credibilidad.

4. **La hipótesis simple del greenwashing no se sostiene tal cual.** Como decía en RQ3,
   "optimista = vago" no se cumple empresa a empresa. El greenwashing real es más sutil:
   no es tono, es **falta de cifras y exceso de cobertura ("hedging")**.

5. **Cuanto más grande la empresa, menos humo.** Las grandes (más capitalización) tienen
   menor GW_index. Probablemente porque tienen más recursos para reportar bien y más
   escrutinio público.

6. **La "doble materialidad" se multiplica por 8.** Una huella textual clarísima de que la
   CSRD está cambiando de verdad el contenido, no solo la forma.

---

## 10. Limitaciones (para que no te pillen desprevenido)

Decir las limitaciones tú mismo te hace quedar bien. Las principales:

- **La cobertura ESRS mide vocabulario, no cumplimiento legal.** Que una empresa "puntúe
  bajo" en E3 (agua) puede ser porque el agua no es material para ella, no porque incumpla.
  El indicador es **conservador**: cuenta palabras exactas de mi diccionario.
- **El GW_index es una *proxy* (señal indirecta) de greenwashing, no una prueba.** Mido
  patrones de lenguaje compatibles con "cheap talk", no demuestro intención de engañar.
- **Algunos países tienen muy pocas empresas** (Austria 2, Irlanda 2…), así que el análisis
  por país es exploratorio; por eso agrupo en 4 regiones para las regresiones.
- **Solo 3 años** y solo el primer año de CSRD (2024); la tendencia habrá que confirmarla con
  más ejercicios.
- **Modelos en inglés:** homogeneicé el corpus a inglés, lo que es correcto pero implica
  sustituir informes originales por su versión inglesa oficial.

---

## 11. Tu "elevator pitch" de 90 segundos (memorízalo)

> *"Mi TFG analiza cómo comunican sostenibilidad las grandes empresas europeas, usando
> inteligencia artificial que lee texto. Trabajo con 97 empresas del STOXX 600 a lo largo de
> 2022, 2023 y 2024, justo el periodo en que entra en vigor la nueva directiva europea, la
> CSRD. Analizo el informe anual porque es donde la ley obliga a meter la sostenibilidad, y
> dentro de él aíslo la sección de sostenibilidad. Sobre 285.000 frases aplico varios modelos
> de lenguaje —FinBERT, ClimateBERT— y diccionarios financieros para medir el tono, la
> concreción y las señales de greenwashing, sin usar ninguna nota ESG externa. Construyo un
> índice propio de greenwashing y respondo a cuatro preguntas: de qué hablan, si difieren por
> sector y país, qué empresas son más concretas, y cómo cambia todo con la CSRD. El hallazgo
> central es que con la CSRD los informes crecen muchísimo en extensión pero no en datos
> concretos, el tono se vuelve menos optimista y más de riesgo, y el concepto de 'doble
> materialidad' que introduce la ley se multiplica por ocho. Es decir: la ley cambia el qué y
> el cómo se comunica, pero el aumento de volumen no se traduce automáticamente en más
> transparencia cuantitativa."*

---

## 12. Preguntas que te puede hacer el tutor (y cómo responder)

**P: ¿Por qué informes anuales y no informes de sostenibilidad?**
R: Ver §3. Empieza por el legal: *"la ley obliga a meter la sostenibilidad dentro del informe
de gestión, que va en el informe anual"*, y remata con comparabilidad + anti-greenwashing.

**P: ¿Por qué no usas ratings ESG (MSCI, Sustainalytics)?**
R: §4. *"Sería circular: validaría texto contra otra opinión. Mi aportación es medir desde el
texto, de forma transparente."*

**P: ¿Qué es exactamente el greenwashing que mides?**
R: *"No mido intención de engañar; mido patrones de lenguaje de 'cheap talk': mucho lenguaje
vago y de cobertura, promesas sin cifras, poca especificidad. Lo resumo en un índice propio,
el GW_index."*

**P: ¿Cómo sé que tus modelos no se inventan los resultados?**
R: *"Por triangulación: uso modelos independientes (FinBERT, ClimateBERT, diccionario LM) y
dos métodos de temas (LDA y BERTopic), y todos apuntan en la misma dirección."*

**P: ¿Tu hallazgo demuestra que hay más greenwashing con la CSRD?**
R: *"Hay más señales agregadas de 'cheap talk' (más hedging, menos cifras), pero matizo dos
cosas: el tono se vuelve más cauto, no más triunfalista; y al controlar por sector y tamaño,
el efecto temporal se diluye, así que es en parte composicional. Por eso lo presento como una
señal a vigilar, no como prueba."*

**P: ¿Por qué 97 empresas y no las 600?**
R: *"Muestreo estratificado por sector con tope por país para equilibrar, y por viabilidad de
descarga y procesamiento manual de PDFs. La muestra es representativa de sectores y países."*

**P: ¿Qué es la doble materialidad?**
R: *"El principio estrella de la CSRD: la empresa debe reportar tanto su impacto sobre el
entorno (materialidad de impacto) como cómo la sostenibilidad afecta a su negocio
(materialidad financiera). No existía bajo la NFRD; por eso su explosión textual (×8,2) es la
huella más clara del cambio de ley."*

**P: ¿Qué diferencia LDA de BERTopic?**
R: *"LDA agrupa temas por qué palabras aparecen juntas; BERTopic agrupa por significado, así
que es más fino. Uso LDA para los grandes temas y BERTopic para confirmarlos y afinar."*

**P: ¿Cuál es tu aportación original?**
R: *"Tres cosas: (1) un diccionario ESRS propio validado contra el corpus; (2) un índice de
greenwashing construido solo desde el texto, sin ratings externos; (3) un diseño 'antes/después'
de la CSRD sobre una muestra grande y comparable del STOXX 600."*

---

## 13. Glosario rápido (por si te trabas con una palabra)

- **STOXX Europe 600:** índice de las 600 grandes cotizadas europeas. Mi universo de partida.
- **NFRD:** directiva antigua (2014) de información no financiera. Blanda, voluntaria en el
  detalle. Régimen de 2022-23 en mi estudio.
- **CSRD:** directiva nueva (2022, aplica desde ejercicio 2024). Estricta, estandarizada,
  auditada. Régimen de 2024.
- **ESRS:** los estándares concretos que desarrollan la CSRD (qué reportar exactamente). 12
  estándares: E1-E5 (ambiental), S1-S4 (social), G1 (gobernanza), ESRS1-2 (transversales).
- **Taxonomía UE:** sistema de la UE para clasificar qué actividades económicas son
  "verdes". Las empresas reportan qué % de su negocio está alineado.
- **Management report (informe de gestión):** la parte narrativa del informe anual (negocio,
  estrategia, riesgos, gobernanza) donde, por ley, va la sostenibilidad.
- **Greenwashing / "cheap talk":** comunicar más sostenibilidad de la que sustancialmente se
  respalda con datos y acciones concretas.
- **Hedging:** lenguaje de cobertura/cautela ("podría", "esperamos", "en la medida de…").
- **Especificidad:** que una frase tenga cifras, fechas o metas concretas (lo contrario de
  vago).
- **GW_index:** mi índice propio de señales de greenwashing textual.
- **Corpus:** el conjunto total de textos analizados (los 289 documentos).
- **Token:** una palabra (unidad de conteo del texto).
- **Triangulación:** confirmar un hallazgo con varios métodos independientes.
- **Test de Wilcoxon / regresión OLS:** pruebas estadísticas. Wilcoxon compara 2022 vs 2024
  por parejas (misma empresa); OLS estima qué factores (tamaño, sector…) explican el GW_index.
- **p < 0,05:** convención de que un resultado es estadísticamente significativo (poco
  probable que sea casualidad).

---

### Última recomendación

Si solo tienes 5 minutos antes de la llamada, repasa: **§0 (la frase), §3 (annual reports),
§9 (hallazgos sorprendentes) y §11 (el pitch).** Con eso llevas el 80% de la conversación.
