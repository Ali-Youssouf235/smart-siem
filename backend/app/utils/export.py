"""
Utilitaire d'export CSV / Excel (XLSX) partagé par les logs et les alertes.

Exigence 4.5 du cahier des charges : permettre à un profil "Auditeur"
d'extraire les données brutes pour preuve/analyse hors du SIEM, dans un
format tableur exploitable (et non uniquement en PDF de synthèse).
"""
import csv
import io
from typing import List, Dict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from fastapi.responses import StreamingResponse


def _flatten_rows(rows: List[Dict]) -> List[Dict]:
    """Aplati les valeurs non scalaires (listes/dicts) en texte pour un tableur lisible."""
    flat = []
    for row in rows:
        flat_row = {}
        for k, v in row.items():
            if isinstance(v, (list, dict)):
                flat_row[k] = str(v)
            else:
                flat_row[k] = v
        flat.append(flat_row)
    return flat


def export_to_csv(rows: List[Dict], filename: str) -> StreamingResponse:
    rows = _flatten_rows(rows)
    columns = sorted({k for row in rows for k in row.keys()}) if rows else []

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

    buffer.seek(0)
    byte_buffer = io.BytesIO(buffer.getvalue().encode("utf-8-sig"))  # BOM pour Excel/accents FR
    return StreamingResponse(
        byte_buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def export_to_excel(rows: List[Dict], filename: str, sheet_title: str = "Export") -> StreamingResponse:
    rows = _flatten_rows(rows)
    columns = sorted({k for row in rows for k in row.keys()}) if rows else []

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_title[:31]  # Limite Excel

    header_fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)

    ws.append(columns)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font

    for row in rows:
        ws.append([row.get(c, "") for c in columns])

    for i, col in enumerate(columns, start=1):
        max_len = max([len(str(col))] + [len(str(r.get(col, ""))) for r in rows]) if rows else len(str(col))
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = min(max_len + 3, 50)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
