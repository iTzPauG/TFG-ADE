"""
Genera data/external/busqueda_manual.html — página con links directos a las
búsquedas de Google/RR.com para todas las empresas con estado 'problema' o 'pendiente'.
Abre el HTML en el navegador, haz clic en cada empresa, descarga el PDF y
luego corre fase3_registrar.py para marcarla como descargada en el tracking.

Uso:
  python scripts/fase3_helper_manual.py
  open data/external/busqueda_manual.html
"""

from pathlib import Path
import pandas as pd
import urllib.parse

BASE_DIR = Path(__file__).resolve().parents[1]
TRACKING_PATH = BASE_DIR / "data" / "external" / "tracking_descargas.csv"
OUT_PATH = BASE_DIR / "data" / "external" / "busqueda_manual.html"


def google_link(empresa: str, año: int) -> str:
    q = urllib.parse.quote_plus(f'"{empresa}" annual report {año} filetype:pdf')
    return f"https://www.google.com/search?q={q}"


def rr_link(empresa: str) -> str:
    q = urllib.parse.quote_plus(empresa)
    return f"https://www.responsibilityreports.com/Search/?q={q}"


def main():
    df = pd.read_csv(TRACKING_PATH, dtype=str).fillna("")
    pendientes = df[df["estado"].isin(["pendiente", "problema"])].copy()

    rows_html = []
    for _, row in pendientes.iterrows():
        empresa = row["empresa"]
        ticker = row["ticker"]
        pais = row["pais"]
        año = row["año"]
        estado = row["estado"]
        notas = row.get("notas", "")

        color = "#fff3cd" if estado == "problema" else "#f8f9fa"
        g_url = google_link(empresa, int(año))
        rr_url = rr_link(empresa)

        rows_html.append(f"""
        <tr style="background:{color}">
          <td>{row['id_empresa']}</td>
          <td><b>{empresa}</b></td>
          <td>{ticker}</td>
          <td>{pais}</td>
          <td>{año}</td>
          <td><span style="color:{'#856404' if estado=='problema' else '#0d6efd'}">{estado}</span></td>
          <td>
            <a href="{g_url}" target="_blank">Google</a> |
            <a href="{rr_url}" target="_blank">RR.com</a>
          </td>
          <td style="font-size:0.85em;color:#666">{notas}</td>
        </tr>""")

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Fase 3 — Búsqueda manual de informes</title>
  <style>
    body {{ font-family: sans-serif; font-size: 14px; margin: 20px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #dee2e6; padding: 6px 10px; text-align: left; }}
    th {{ background: #343a40; color: white; }}
    a {{ color: #0d6efd; }}
  </style>
</head>
<body>
  <h2>Fase 3 — Búsqueda manual de informes ({len(pendientes)} entradas)</h2>
  <p>Para cada empresa: descarga el PDF del informe anual integrado, guárdalo en
     <code>data/raw/[país]/[ticker]/[TICKER]_[AÑO]_integrated.pdf</code>
     y actualiza el tracking con <code>python scripts/fase3_registrar.py --empresa [id] --año [año] --url [url]</code>
  </p>
  <table>
    <thead>
      <tr>
        <th>ID</th><th>Empresa</th><th>Ticker</th><th>País</th>
        <th>Año</th><th>Estado</th><th>Búsqueda</th><th>Notas</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows_html)}
    </tbody>
  </table>
</body>
</html>"""

    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"Generado: {OUT_PATH}")
    print(f"  {len(pendientes)} entradas ({(pendientes['estado']=='problema').sum()} con problema)")


if __name__ == "__main__":
    main()
