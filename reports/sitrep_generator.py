"""Simple PDF generator for SITREP reports."""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_sitrep_pdf(data: dict) -> str:
    """Generate a PDF file with basic SITREP information.

    Parameters
    ----------
    data: dict
        Dictionary containing keys: type, datetime, sru, zone, notes.

    Returns
    -------
    str
        Path to the generated PDF file.
    """
    try:
        filename = (
            f"SITREP_{data.get('type', 'UNKNOWN')}_"
            f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
        )
        filepath = os.path.join(os.path.expanduser("~"), "Documents", filename)

        c = canvas.Canvas(filepath, pagesize=A4)
        c.setFont("Helvetica", 12)

        c.drawString(100, 800, f"Тип: {data.get('type', '')}")
        c.drawString(100, 780, f"Дата/время: {data.get('datetime', '')}")
        c.drawString(100, 760, f"SRU: {data.get('sru', '')}")
        c.drawString(100, 740, f"Зона поиска: {data.get('zone', '')}")
        c.drawString(100, 720, f"Дополнительно: {data.get('notes', '')}")

        c.save()
        return filepath
    except Exception as e:  # pragma: no cover - simple wrapper
        raise RuntimeError(f"Ошибка при генерации PDF: {str(e)}")

