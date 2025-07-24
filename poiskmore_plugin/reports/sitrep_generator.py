Генератор SITREP PDF. Улучшен: Обработка
ошибок, динамический y с отступами.
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from datetime import datetime
def generate_sitrep_pdf(data):
try:
filename = f"SITREP_{data.get('type', 
'UNKNOWN')}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
filepath = os.path.join(os.path.expanduser("~"), "Documents", filename)
c = canvas.Canvas(filepath, pagesize=A4)
c.setFont("Helvetica", 12)
y = 800
for label in ["type", "datetime", "sru", "coords", "weather", "situation", "actions", 
"attachment"]:
value = data.get(label, "N/A")
c.drawString(100, y, f"{label.capitalize()}: {value}")
y -= 20
if y < 100:
c.showPage()
y = 800
c.save()
return filepath
except Exception as e:
print(f"Ошибка генерации PDF: {e}")
return None
