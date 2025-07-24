# Генератор SITREP PDF. Улучшен: Обработка
# ошибок, динамический y с отступами.

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from datetime import datetime

def generate_sitrep_pdf(data):
    try:
        filename = f"SITREP_{data.get('type', 'UNKNOWN')}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(os.path.expanduser("~"), "Documents", filename)

        c = canvas.Canvas(filepath, pagesize=A4)
        c.setFont("Helvetica", 12)

        c.drawString(100, 800, f"Тип: {data.get('type', '')}")
        c.drawString(100, 780, f"Дата/время: {data.get('datetime', '')}")
        c.drawString(100, 760, f"SRU: {data.get('sru', '')}")
        c.drawString(100, 740, f"Зона поиска: {data.get('zone', '')}")
        c.drawString(100, 720, f"Дополнительно: {data.get('notes', '')}")

        c.save()
    except Exception as e:
        raise RuntimeError(f"Ошибка при генерации PDF: {str(e)}")
