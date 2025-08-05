"""Генерация простого PDF‑отчёта SITREP."""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_sitrep_pdf(data: dict) -> str:
    """Создаёт PDF с основной информацией SITREP.

    Параметры
    ----------
    data : dict
        Словарь с ключами: type, datetime, sru, zone, notes.

    Возвращает
    ----------
    str
        Путь к созданному PDF файлу.
    """

    try:
        filename = (
            f"SITREP_{data.get('type', 'UNKNOWN')}_"
            f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
        )
        filepath = os.path.join(os.path.expanduser("~"), "Documents", filename)

        c = canvas.Canvas(filepath, pagesize=A4)
        c.setFont("Helvetica", 12)
        c.drawString(100, 780, f"Тип: {data.get('type', '')}")
        c.drawString(100, 760, f"Дата/время: {data.get('datetime', '')}")
        c.drawString(100, 740, f"SRU: {data.get('sru', '')}")
        c.drawString(100, 720, f"Зона поиска: {data.get('zone', '')}")
        c.drawString(100, 700, f"Дополнительно: {data.get('notes', '')}")
        c.save()
        return filepath

    except Exception as e:  # pragma: no cover - простая обёртка
        raise RuntimeError(f"Ошибка при генерации PDF: {str(e)}")

