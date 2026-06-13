"""
Fase 4 — QA del corpus final (`data/processed/corpus.parquet`).

Comprueba, sobre las 1172 filas (586 docs x 2 secciones, 196 empresas):
  - Integridad estructural: columnas, duplicados (id, seccion), nulos/vacíos.
  - Consistencia n_chars/n_tokens vs longitud real de clean_text/tokens.
  - Caracteres de control, mojibake (Ã©, â€™, Â, ...), carácter de sustitución \\ufffd.
  - idioma == 'en' en todas las filas (Decisión 012).
  - Ratio de caracteres no-ASCII anómalo (posible texto en otro idioma / OCR roto).
  - Cabeceras/pies repetidos no eliminados (líneas muy frecuentes dentro de un doc).
  - tokens: deben ser lemas en minúscula, alfabéticos, len>2 (spaCy, sin stopwords).
  - Distribución de n_tokens/n_chars por sección y confianza (outliers).

Uso:
  python scripts/extraction/fase4_qa_corpus.py
  python scripts/extraction/fase4_qa_corpus.py --muestra 50   # imprime ejemplos de problemas
"""

import argparse
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
CORPUS = BASE_DIR / "data" / "processed" / "corpus.parquet"

CTRL_RX = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MOJIBAKE_RX = re.compile(r"Ã[\x80-\xbf]|â€[\x80-\x9f]|Â[\xa0-\xbf]")
REPL_CHAR = "�"
NON_ASCII_RX = re.compile(r"[^\x00-\x7f]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--muestra", type=int, default=10, help="nº de ejemplos a imprimir por problema")
    args = ap.parse_args()

    print("Cargando corpus.parquet...", flush=True)
    df = pd.read_parquet(CORPUS)
    n = len(df)
    print(f"Filas: {n} | columnas: {list(df.columns)}\n")

    problemas = defaultdict(list)
    stats_chars = defaultdict(list)
    stats_tokens = defaultdict(list)

    t0 = time.time()
    for i, r in enumerate(df.itertuples(), 1):
        clave = f"{r.id}|{r.seccion}"

        # 1. nulos / vacíos
        if not isinstance(r.clean_text, str) or not r.clean_text.strip():
            problemas["clean_text_vacio"].append(clave)
            continue
        if r.tokens is None or len(r.tokens) == 0:
            problemas["tokens_vacio"].append(clave)

        texto = r.clean_text

        # 2. consistencia n_chars / n_tokens
        if abs(len(texto) - int(r.n_chars)) > 0:
            problemas["n_chars_inconsistente"].append(f"{clave} (real={len(texto)}, declarado={r.n_chars})")
        if r.tokens is not None and abs(len(r.tokens) - int(r.n_tokens)) > 0:
            problemas["n_tokens_inconsistente"].append(f"{clave} (real={len(r.tokens)}, declarado={r.n_tokens})")

        # 3. caracteres de control
        ctrl = CTRL_RX.findall(texto)
        if ctrl:
            problemas["caracteres_control"].append(f"{clave} (n={len(ctrl)}, ej={ctrl[:3]!r})")

        # 4. carácter de sustitución (encoding roto)
        if REPL_CHAR in texto:
            problemas["caracter_sustitucion_ufffd"].append(f"{clave} (n={texto.count(REPL_CHAR)})")

        # 5. mojibake (UTF-8 mal decodificado como Latin-1 y similares)
        moji = MOJIBAKE_RX.findall(texto)
        if moji:
            problemas["mojibake"].append(f"{clave} (n={len(moji)}, ej={moji[:5]!r})")

        # 6. idioma
        if r.idioma != "en":
            problemas["idioma_no_en"].append(f"{clave} (idioma={r.idioma})")

        # 7. ratio no-ASCII anómalo (>5% del texto)
        non_ascii = len(NON_ASCII_RX.findall(texto))
        ratio = non_ascii / len(texto)
        if ratio > 0.05:
            problemas["ratio_no_ascii_alto"].append(f"{clave} (ratio={ratio:.1%})")

        # 8. cabeceras/pies repetidos no eliminados: línea no trivial que se repite
        #    más de 1 vez por cada ~3 páginas estimadas (250 palabras/pág aprox.)
        lineas = [l.strip() for l in texto.split("\n") if len(l.strip()) >= 8]
        if lineas:
            freq = Counter(lineas)
            npag_est = max(len(texto.split()) / 250, 1)
            umbral = max(int(npag_est / 2), 3)
            repetidas = [(l, c) for l, c in freq.items() if c >= umbral and c >= 5]
            if repetidas:
                repetidas.sort(key=lambda x: -x[1])
                top = repetidas[0]
                problemas["lineas_repetidas_sospechosas"].append(f"{clave} ('{top[0][:60]}' x{top[1]})")

        # 9. tokens: deben ser lemas alfabéticos en minúscula, len>2
        if r.tokens is not None and len(r.tokens) > 0:
            malos = [t for t in r.tokens[:2000] if not (t.isalpha() and t.islower() and len(t) > 2)]
            if malos:
                problemas["tokens_invalidos"].append(f"{clave} (n_muestra_mala={len(malos)}, ej={malos[:5]!r})")

        # estadísticas
        stats_chars[(r.seccion, r.confianza)].append(r.n_chars)
        stats_tokens[(r.seccion, r.confianza)].append(r.n_tokens)

        if i % 50 == 0 or i == n:
            pct = int(100 * i / n)
            el = time.time() - t0
            bar = "#" * (pct // 4) + "-" * (25 - pct // 4)
            sys.stdout.write(f"\r  [{bar}] {pct:3d}%  fila {i}/{n}  {el:5.1f}s   ")
            sys.stdout.flush()

    print("\n")

    # 10. duplicados (id, seccion)
    dups = df.groupby(["id", "seccion"]).size()
    dups = dups[dups > 1]
    if len(dups):
        problemas["duplicados_id_seccion"] = [f"{i}|{s} x{c}" for (i, s), c in dups.items()]

    # 11. seccion / confianza fuera de esquema esperado
    secciones_validas = {"mr", "sus"}
    conf_validas = {"alta", "densidad", "densidad_baja", "media", "aceptado_sin_financieros",
                     "mr", "mr_con_financieros"}
    bad_sec = sorted(set(df.seccion) - secciones_validas)
    bad_conf = sorted(set(df.confianza) - conf_validas)
    if bad_sec:
        problemas["seccion_desconocida"] = bad_sec
    if bad_conf:
        problemas["confianza_desconocida"] = bad_conf

    # 12. outliers de tamaño (docs sospechosamente cortos)
    cortos = df[(df.seccion == "sus") & (df.n_tokens < 50)]
    if len(cortos):
        problemas["sus_muy_corto_(<50_tokens)"] = [
            f"{r.id} (n_tokens={r.n_tokens}, confianza={r.confianza})" for r in cortos.itertuples()
        ]
    cortos_mr = df[(df.seccion == "mr") & (df.n_tokens < 200)]
    if len(cortos_mr):
        problemas["mr_muy_corto_(<200_tokens)"] = [
            f"{r.id} (n_tokens={r.n_tokens}, confianza={r.confianza})" for r in cortos_mr.itertuples()
        ]

    # === informe ===
    print("=" * 70)
    print("RESUMEN QA corpus.parquet")
    print("=" * 70)
    print(f"Filas totales: {n}")
    print("Por sección:", dict(df.seccion.value_counts()))
    print("Por confianza:", dict(df.confianza.value_counts()))
    print("Por idioma:", dict(df.idioma.value_counts()))
    print()

    if not problemas:
        print("✅ SIN PROBLEMAS DETECTADOS.")
    else:
        print(f"⚠️  {len(problemas)} tipo(s) de problema detectados:\n")
        for tipo, items in problemas.items():
            print(f"- {tipo}: {len(items)} caso(s)")
            for ej in items[:args.muestra]:
                print(f"    · {ej}")
            if len(items) > args.muestra:
                print(f"    ... y {len(items) - args.muestra} más")
        print()

    print("Distribución n_tokens por (sección, confianza):")
    for clave, vals in sorted(stats_tokens.items()):
        s = pd.Series(vals)
        print(f"  {clave}: n={len(s)} mediana={int(s.median())} min={int(s.min())} max={int(s.max())}")


if __name__ == "__main__":
    main()
