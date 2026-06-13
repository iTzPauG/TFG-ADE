"""
Fase 4C — Recálculo fiable del límite de fin del management report y acotado de la
sostenibilidad. SUPERSEDE el recorte del bloque C de `fase4_sanear_secciones.py`, que
cortaba el MR con un marcador de estados financieros tras un 30% arbitrario del documento
y producía cortes prematuros (mr_fin antes del capítulo de sostenibilidad).

Principio: los ESTADOS FINANCIEROS van DESPUÉS de la narrativa, y la sostenibilidad es
parte de la narrativa. Por tanto:
  - `mr_fin` = primer epígrafe de estados financieros (en cabecera de página) en página
    POSTERIOR a `sus_fin`; si no hay → documento entero (sin corte falso).
  - En los informes SOBRE-EXTRAÍDOS (la sostenibilidad abarca ≥55% del documento porque la
    heurística de índice no halló su cierre), se re-acota `sus_fin` al primer epígrafe de
    estados financieros POSTERIOR a `sus_ini`.
  - Siempre `sus_fin ≤ mr_fin`.
Los informes con la sostenibilidad arrancando en la página 1 (portada) o sin corte fiable
se marcan `revisar` en `sus_confianza` (revisión manual, no se adivina).

Lee el texto limpio por página (caché OCR para los docs corruptos; nativo el resto).
Por defecto DRY-RUN; con --apply hace backup en `secciones/_bak_limites/` y actualiza el
manifiesto. Idempotente.

Uso:
  python scripts/extraction/fase4_recalcular_limites.py            # dry-run
  python scripts/extraction/fase4_recalcular_limites.py --apply
"""

import argparse
import shutil
import warnings
from pathlib import Path

import fitz  # PyMuPDF
import pandas as pd

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
INTERIM_DIR = BASE_DIR / "data" / "interim"
SEC_DIR = INTERIM_DIR / "secciones"
BAK_DIR = SEC_DIR / "_bak_limites"
CACHE_DIR = INTERIM_DIR / "_paginas_ocr"
MANIFEST_PATH = INTERIM_DIR / "secciones_manifest.csv"

FIN_MARKERS = [
    "consolidated financial statements", "financial statements",
    "parent company financial statements", "company financial statements",
    "statutory accounts", "annual accounts", "company accounts",
]
SOBRE_EXTR = 0.55  # sus que abarca ≥55% del doc = sobre-extraído (cierre no detectado)


def localizar_pdf(pais, ticker, año):
    p = RAW_DIR / pais / ticker / f"{ticker}_{año}_integrated.pdf"
    if p.exists():
        return p
    m = list(RAW_DIR.glob(f"**/{ticker}_{año}_*.pdf"))
    return m[0] if m else None


def cargar_paginas(idd, ticker, año, pais):
    c = CACHE_DIR / f"{idd}_{ticker}_{año}.pages.txt"
    if c.exists():
        return c.read_text(encoding="utf-8").split("\f")
    pdf = localizar_pdf(pais, ticker, año)
    if not pdf:
        return None
    doc = fitz.open(pdf)
    pags = [p.get_text() for p in doc]
    doc.close()
    return pags


def fin_tras(pags, desde):
    """Primer epígrafe de estados financieros (en cabecera de página, primeros 200 chars)
    en página 1-based > `desde`. Si el marcador aparece en >40% de páginas es un running
    header (no un límite) → None."""
    n = len(pags)
    hits = [i for i in range(n) if any(m in pags[i][:200].lower() for m in FIN_MARKERS)]
    if not hits or len(hits) > 0.4 * n:
        return None
    after = [i for i in hits if i + 1 > desde]
    return (after[0] + 1) if after else None


def f(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def escribir(path, texto, apply):
    if not apply:
        return
    BAK_DIR.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, BAK_DIR / path.name)
    path.write_text(texto, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--nuevos", action="store_true",
                    help="Solo procesar las 99 empresas de la ampliación (E098-E196).")
    args = ap.parse_args()

    man = pd.read_csv(MANIFEST_PATH, dtype=str).fillna("")
    tr = pd.read_csv(BASE_DIR / "data" / "external" / "tracking_descargas.csv", dtype=str).fillna("")

    cambios_mr, cambios_sus, marcados = [], [], []
    for r in man.itertuples():
        if args.nuevos and int(r.id_empresa[1:]) < 98:
            continue
        idd, tk, an = r.id_empresa, r.ticker, r.año
        npp = int(f(r.npaginas))
        mr_ini = int(f(r.mr_ini)) or 1
        sus_ini, sus_fin = int(f(r.sus_ini)), int(f(r.sus_fin))
        mr_fin = int(f(r.mr_fin))
        if not (npp and sus_ini and sus_fin):
            continue
        row = tr[(tr.id_empresa == idd) & (tr.año == str(an))]
        pais = row.iloc[0]["pais"] if not row.empty else ""

        pags = None

        def get():
            nonlocal pags
            if pags is None:
                pags = cargar_paginas(idd, tk, an, pais)
            return pags

        base = f"{idd}_{tk}_{an}"
        sobre = (sus_fin - sus_ini) >= SOBRE_EXTR * npp
        marca = ""

        # 1) Sostenibilidad sobre-extraída: re-acotar sus_fin al primer epígrafe de estados
        #    financieros tras sus_ini, SOLO si reduce de verdad (corte < sus_fin) y el bloque
        #    resultante baja del 55% del doc. Si no se puede acotar con fiabilidad → 'revisar'
        #    (sin tocar el _sus: no se adivina).
        new_sus_fin = sus_fin
        if sobre:
            corte = None
            if sus_ini > 1:
                p = get()
                corte = fin_tras(p, sus_ini) if p else None
            if corte and sus_ini + 3 < corte < sus_fin and (corte - sus_ini) < SOBRE_EXTR * npp:
                new_sus_fin = corte
            else:
                marca = "revisar"

        # 2) Invariante mr_fin >= sus_fin (la sostenibilidad ⊂ narrativa = MR). NO se intenta
        #    localizar los estados financieros para todos (heurístico poco fiable que rompía
        #    detecciones correctas): solo se EXTIENDE mr_fin hasta cubrir la sostenibilidad
        #    cuando había quedado por debajo (corte prematuro). Nunca se acorta el MR aquí.
        new_mr_fin = max(mr_fin, new_sus_fin)
        new_sus_fin = min(new_sus_fin, new_mr_fin)

        # Aplicar cambios. El PDF SOLO se carga si hay que reescribir un fichero (perezoso);
        # en dry-run no se carga nada salvo lo ya cargado para los sobre-extraídos.
        if new_mr_fin != mr_fin:
            if args.apply:
                pp = get()
                escribir(SEC_DIR / f"{base}_mr.txt", "\n".join(pp[mr_ini - 1:new_mr_fin]), True)
            man.loc[r.Index, ["mr_fin", "mr_pp"]] = [str(new_mr_fin), str(new_mr_fin - mr_ini)]
            cambios_mr.append(f"{base}: mr_fin {mr_fin}→{new_mr_fin} (npp={npp})")
        if new_sus_fin != sus_fin:
            if args.apply:
                pp = get()
                escribir(SEC_DIR / f"{base}_sus.txt", "\n".join(pp[sus_ini - 1:new_sus_fin]), True)
            man.loc[r.Index, ["sus_fin", "sus_pp"]] = [str(new_sus_fin), str(new_sus_fin - sus_ini)]
            cambios_sus.append(f"{base}: sus {sus_ini}-{sus_fin}→{sus_ini}-{new_sus_fin} ({sus_fin-new_sus_fin}pp menos)")
        if marca:
            man.loc[r.Index, "sus_confianza"] = marca
            marcados.append(f"{base}: sus {sus_ini}-{sus_fin} ({sus_fin-sus_ini}pp, {100*(sus_fin-sus_ini)//npp}% del doc) → REVISAR")

    print(f"=== MR re-acotados: {len(cambios_mr)} ===")
    for c in cambios_mr:
        print("  " + c)
    print(f"\n=== SUS sobre-extraídos re-acotados: {len(cambios_sus)} ===")
    for c in cambios_sus:
        print("  " + c)
    print(f"\n=== SUS marcados 'revisar' (manual): {len(marcados)} ===")
    for c in marcados:
        print("  " + c)

    if args.apply:
        man.to_csv(MANIFEST_PATH, index=False)
        print(f"\n[APLICADO] backups en {BAK_DIR.relative_to(BASE_DIR)}, manifiesto actualizado.")
    else:
        print(f"\n[DRY-RUN] {len(cambios_mr)+len(cambios_sus)} cambios + {len(marcados)} marcados. Usa --apply.")


if __name__ == "__main__":
    main()
