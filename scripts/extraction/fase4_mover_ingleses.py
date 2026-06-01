"""
Fase 4 (remediación idioma) — coloca las versiones EN descargadas a mano en data/raw.

Sustituye los informes no-ingleses por su versión oficial en inglés (URD/Integrated
Management Report del propio emisor). Hace copia de seguridad del original
francés/español en data/raw/_reemplazados_originales/ antes de sobrescribir.

Solo mueve los ficheros del MAPA que existan en ~/Downloads; informa de los que falten.

Uso:
  python scripts/extraction/fase4_mover_ingleses.py            # mueve
  python scripts/extraction/fase4_mover_ingleses.py --dry-run  # solo informa
"""

import argparse
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
DOWNLOADS = Path.home() / "Downloads"
BACKUP = RAW_DIR / "_reemplazados_originales"

# (fichero en Downloads, país, ticker, año)
MAPA = [
    ("karing2022.pdf", "France", "KER", "2022"),
    ("kering2023.pdf", "France", "KER", "2023"),
    ("karing2024.pdf", "France", "KER", "2024"),
    ("2022-universal-registration-document.pdf", "France", "EN", "2022"),  # Bouygues 2022 (verificado)
    ("deu_bouygues_2023-va-2903.pdf", "France", "EN", "2023"),
    ("bouygues_deu_2024_uk.pdf", "France", "EN", "2024"),
    ("orange2023.pdf", "France", "ORAN", "2023"),
    ("orange2024.pdf", "France", "ORAN", "2024"),
    ("valeo_2022-urd_uk.pdf", "France", "FR", "2022"),
    ("valeo_2023-universal-registration-document.pdf", "France", "FR", "2023"),
    ("gecina_-_universal_registration_document_urd_2022.pdf", "France", "GFC", "2022"),
    ("gecina_universal_registration_document_2023_e-accessible.pdf", "France", "GFC", "2023"),
    ("gecina_universal_registration_document_urd_2024.pdf", "France", "GFC", "2024"),
    ("wendel2022.pdf", "France", "WEND", "2022"),
    ("repsol2022.pdf", "Spain", "REP", "2022"),
    ("repsol2023.pdf", "Spain", "REP", "2023"),
    ("EIFFAGE_DEU2022_GB.pdf", "France", "EFGI", "2022"),
    # --- 2ª tanda (descargada por el usuario) ---
    ("0428_boll22t023_urd_gb_2022.pdf", "France", "BOL", "2022"),
    ("0502_boll23t029_urd_gb_2023_mel.pdf", "France", "BOL", "2023"),
    ("0520_boll24t035_urd_gb_2024_mel.pdf", "France", "BOL", "2024"),
    ("vinci-2022-universal-registration-document.pdf", "France", "DG", "2022"),
    ("vinci-2023-universal-registration-document.pdf", "France", "DG", "2023"),
    ("vinci-2024-universal-registration-document.pdf", "France", "DG", "2024"),
    ("2024-safran-universal-registration-document.pdf", "France", "SAF", "2024"),
    ("Universal Registration Document 2023_VUK pdf..pdf", "France", "PERP", "2023"),
    ("wendel-2023-urd-en-april2024.pdf", "France", "WEND", "2023"),
    ("wen-2024-urd-en-v-mel-25-04-04.pdf", "France", "WEND", "2024"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    BACKUP.mkdir(parents=True, exist_ok=True)

    movidos, faltan = [], []
    for fichero, pais, ticker, año in MAPA:
        src = DOWNLOADS / fichero
        dst = RAW_DIR / pais / ticker / f"{ticker}_{año}_integrated.pdf"
        if not src.exists():
            faltan.append((fichero, ticker, año))
            print(f"[FALTA] {ticker} {año}: no está {fichero} en Downloads")
            continue
        accion = "DRY" if args.dry_run else "OK"
        if not args.dry_run:
            bak = BACKUP / f"{ticker}_{año}_orig.pdf"
            if dst.exists() and not bak.exists():
                shutil.copy2(dst, bak)  # backup original (solo la 1ª vez; no pisar backups previos)
            shutil.copy2(src, dst)
        movidos.append((ticker, año))
        print(f"[{accion}] {fichero}  ->  {dst.relative_to(BASE_DIR)}")

    print(f"\nMovidos: {len(movidos)} | Faltan en Downloads: {len(faltan)}")
    print("Re-extraer:", " ".join(f"{t}:{a}" for t, a in movidos))


if __name__ == "__main__":
    main()
