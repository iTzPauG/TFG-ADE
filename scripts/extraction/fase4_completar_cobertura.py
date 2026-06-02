"""
Fase 4C — completar cobertura al 100% SOLO en los informes a los que les falta el .txt.
NO regenera ni toca los ficheros ya existentes.

- Falta `_mr.txt` (6 informes sin índice ni estructura de fuente): fallback de management
  report = [1, primera página de 'financial statements'] (búsqueda de texto), o doc entero.
- Falta `_sus.txt` (16 con ESG disperso): densidad ESG RELAJADA = mayor ventana contigua por
  encima de un umbral relativo (garantiza bloque). Marca de calidad densidad / densidad_baja.

Uso: python scripts/extraction/fase4_completar_cobertura.py
"""

import re
import warnings
from pathlib import Path

import fitz
import pandas as pd

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
SEC_DIR = BASE_DIR / "data" / "interim" / "secciones"
TRACKING_PATH = BASE_DIR / "data" / "external" / "tracking_descargas.csv"
MANIFEST_PATH = BASE_DIR / "data" / "interim" / "secciones_manifest.csv"

FIN_MARKERS = ["consolidated financial statements", "financial statements"]

ESG_TERMS = [
    "climat", "emission", "greenhouse", "ghg", "scope 1", "scope 2", "scope 3", "carbon",
    "decarboni", "net zero", "net-zero", "renewable", "biodivers", "ecosystem", "circular",
    "pollution", "environmental", "sustainab", "esg", "csr", "materiality", "esrs", "taxonomy",
    "stakeholder", "diversity", "inclusion", "gender", "human rights", "supply chain",
    "governance", "ethic", "occupational", "community", "science-based", "sbti", "tcfd",
    "paris agreement", "due diligence", "waste", "water", "social responsib", "workforce",
    "employe", "health and safety", "non-financial",
]
RX = re.compile("|".join(re.escape(t) for t in ESG_TERMS))


def localizar_pdf(pais, ticker, año):
    p = RAW_DIR / pais / ticker / f"{ticker}_{año}_integrated.pdf"
    if p.exists():
        return p
    m = list(RAW_DIR.glob(f"**/{ticker}_{año}_*.pdf"))
    return m[0] if m else None


def mr_fallback(doc):
    """MR = [1, inicio de los estados financieros]. Localiza por encabezado de página.
    Si 'financial statements' aparece en >40% de páginas es un running header (no un
    límite) → MR = documento entero. El corte debe estar en la mitad final del documento."""
    n = doc.page_count
    fs = [i for i in range(n) if any(m in doc[i].get_text()[:200].lower() for m in FIN_MARKERS)]
    if len(fs) > 0.4 * n:          # running header → sin límite fiable
        return 1, n
    after = [i for i in fs if i + 1 >= 0.30 * n]   # corte en la mitad final
    return (1, after[0] + 1) if after else (1, n)


def densidad(doc):
    out = []
    for p in doc:
        t = p.get_text().lower()
        out.append(len(RX.findall(t)) / max(len(t.split()), 1) * 100)
    return out


def bloque_relajado(dn):
    """Garantiza una ventana: umbral relativo = max(1.0, 0.35*pico), huecos<=3, min 3pp.
    Devuelve (ini, fin, calidad)."""
    pico = max(dn) if dn else 0
    umb = max(1.0, 0.35 * pico)
    runs, i, n = [], 0, len(dn)
    while i < n:
        if dn[i] >= umb:
            last, k = i, i + 1
            while k < n:
                if dn[k] >= umb:
                    last = k
                elif k - last > 3:
                    break
                k += 1
            runs.append((i, last + 1))
            i = last + 1
        else:
            i += 1
    runs = [r for r in runs if r[1] - r[0] >= 3]
    if not runs:  # último recurso: ±2 páginas alrededor del pico
        pk = dn.index(pico)
        return max(1, pk - 1), min(n, pk + 3), "densidad_baja"
    ini, fin = max(runs, key=lambda r: sum(dn[r[0]:r[1]]))
    media = sum(dn[ini:fin]) / (fin - ini)
    calidad = "densidad" if (media >= 2.5 and fin - ini >= 5) else "densidad_baja"
    return ini + 1, fin, calidad


def main():
    man = pd.read_csv(MANIFEST_PATH, dtype=str)
    tr = pd.read_csv(TRACKING_PATH, dtype=str).fillna("")
    for c in ["mr_ini", "mr_fin", "mr_pp", "sus_ini", "sus_fin", "sus_pp", "sus_ok", "sus_confianza"]:
        if c not in man.columns:
            man[c] = ""

    n_mr = n_sus = 0
    for r in man.itertuples():
        row = tr[(tr.id_empresa == r.id_empresa) & (tr.año == r.año)]
        pais = row.iloc[0]["pais"] if not row.empty else ""
        base = f"{r.id_empresa}_{r.ticker}_{r.año}"
        falta_mr = not (SEC_DIR / f"{base}_mr.txt").exists()
        falta_sus = not (SEC_DIR / f"{base}_sus.txt").exists()
        if not (falta_mr or falta_sus):
            continue
        pdf = localizar_pdf(pais, r.ticker, r.año)
        if not pdf:
            continue
        doc = fitz.open(pdf)
        idx = man.index[(man.id_empresa == r.id_empresa) & (man.año == r.año)]

        if falta_mr:
            ini, fin = mr_fallback(doc)
            (SEC_DIR / f"{base}_mr.txt").write_text(
                "\n".join(doc[i].get_text() for i in range(ini - 1, fin)), encoding="utf-8")
            man.loc[idx, ["mr_ini", "mr_fin", "mr_pp"]] = [str(ini), str(fin), str(fin - ini)]
            n_mr += 1
            print(f"[MR ] {base}: páginas {ini}-{fin}")

        if falta_sus:
            dn = densidad(doc)
            ini, fin, calidad = bloque_relajado(dn)
            (SEC_DIR / f"{base}_sus.txt").write_text(
                "\n".join(doc[i].get_text() for i in range(ini - 1, fin)), encoding="utf-8")
            man.loc[idx, ["sus_ini", "sus_fin", "sus_pp", "sus_ok", "sus_confianza"]] = \
                [str(ini), str(fin), str(fin - ini), "True", calidad]
            n_sus += 1
            print(f"[SUS] {base}: páginas {ini}-{fin} [{calidad}]")
        doc.close()

    man.to_csv(MANIFEST_PATH, index=False)
    mr_tot = sum((SEC_DIR / f"{r.id_empresa}_{r.ticker}_{r.año}_mr.txt").exists() for r in man.itertuples())
    sus_tot = sum((SEC_DIR / f"{r.id_empresa}_{r.ticker}_{r.año}_sus.txt").exists() for r in man.itertuples())
    print(f"\nGenerados ahora: {n_mr} _mr.txt, {n_sus} _sus.txt")
    print(f"COBERTURA: _mr.txt {mr_tot}/{len(man)} | _sus.txt {sus_tot}/{len(man)}")


if __name__ == "__main__":
    main()
