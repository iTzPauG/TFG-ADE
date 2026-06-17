# LaTeX incremental para Overleaf

Carpeta pensada para subir a Overleaf un proyecto pequeño que compile rápido
(sin el paywall de "compile más rápido" que aparece con el TFG completo).

## Cómo funciona

`main.tex` es una copia de `TFG.tex` pero cada `\input{capX_...}` está
envuelto en `\IfFileExists{...}{...}{}`. Si el fichero del capítulo **no
existe** en esta carpeta, simplemente se omite — no da error de compilación.
Lo mismo para `resumen.tex` y `anexos.tex`.

De momento solo está copiado **`cap1_introduccion.tex`** (+ `resumen.tex`,
`references.bib` y la carpeta `figures/` con todas las imágenes, por si las
necesita algún capítulo).

## Cómo añadir el siguiente capítulo

1. Copia el `.tex` actualizado desde `../latex/` a esta carpeta, p.ej.:
   ```bash
   cp ../latex/cap2_marco.tex .
   ```
2. Comprime esta carpeta (`incremental_latex/`) en un .zip.
3. Sube el .zip a Overleaf (Nuevo proyecto → Subir proyecto) o reemplaza los
   ficheros del proyecto existente.
4. Compila (pdflatex → biber → pdflatex → pdflatex, o simplemente "Recompile"
   varias veces).

Repite el proceso capítulo a capítulo: `cap2_marco.tex`, `cap3_metodologia.tex`,
`cap4_resultados.tex`, `cap5_propuestas.tex`, `cap6_conclusiones.tex`, y por
último `anexos.tex`.

## Notas

- `cap4_resultados.tex` es el que usa imágenes (`figures/*.png`); ya están
  todas incluidas en esta carpeta.
- Las referencias cruzadas (`\ref{}`) a secciones de capítulos que todavía no
  están presentes aparecerán como `??` y darán warnings — no son errores, no
  rompen la compilación.
- Cuando quieras volver a generar el documento completo, usa `../latex/TFG.tex`
  como siempre.
