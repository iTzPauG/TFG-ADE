"""
Registra manualmente una descarga completada en el tracking CSV.

Uso (tras descargar el PDF a mano):
  python scripts/fase3_registrar.py \\
      --id E001 --año 2023 \\
      --url https://www.stellantis.com/.../annual_report_2023.pdf \\
      --paginas 320 --idioma en --notas "descargado manualmente desde web IR"

Si ya tienes el PDF en data/raw y quieres marcarlo sin url:
  python scripts/fase3_registrar.py --id E005 --año 2022 --estado descargado
"""

import argparse
from datetime import date
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
TRACKING_PATH = BASE_DIR / "data" / "external" / "tracking_descargas.csv"


def main():
    p = argparse.ArgumentParser(description="Registra descarga manual en tracking")
    p.add_argument("--id", required=True, help="ID empresa (ej. E001)")
    p.add_argument("--año", required=True, type=int)
    p.add_argument("--url", default="", help="URL de donde se descargó")
    p.add_argument("--paginas", default="", help="Número de páginas del PDF")
    p.add_argument("--idioma", default="", help="Idioma del documento (en, es, de, fr, it...)")
    p.add_argument("--estado", default="descargado",
                   choices=["descargado", "problema", "descartado", "pendiente"])
    p.add_argument("--notas", default="", help="Notas adicionales")
    args = p.parse_args()

    df = pd.read_csv(TRACKING_PATH, dtype=str).fillna("")
    mask = (df["id_empresa"] == args.id) & (df["año"] == str(args.año))

    if not mask.any():
        print(f"[error] No existe la combinación id={args.id} año={args.año}")
        return

    df.loc[mask, "estado"] = args.estado
    df.loc[mask, "tipo_informe"] = "integrated"
    df.loc[mask, "url_fuente"] = args.url
    df.loc[mask, "fecha_descarga"] = str(date.today())
    df.loc[mask, "n_paginas"] = args.paginas
    df.loc[mask, "idioma"] = args.idioma
    df.loc[mask, "notas"] = args.notas

    df.to_csv(TRACKING_PATH, index=False)
    empresa = df.loc[mask, "empresa"].iloc[0]
    print(f"[OK] {empresa} — {args.año} → {args.estado}")


if __name__ == "__main__":
    main()
