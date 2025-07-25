# Генератор простых отчетов PDF. Улучшен:
# Добавлена try-except для ошибок файла,
# динамический y.
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
def generate_simple_report(title, lines, filename="report.pdf"):
# try:
# output_path = os.path.join(os.path.expanduser("~"), "Documents", filename)
# c = canvas.Canvas(output_path, pagesize=A4)
# c.setFont("Helvetica", 12)
# y = 800
# c.drawString(100, y, f"Report: {title}")
# y -= 30
# for line in lines:
# c.drawString(100, y, line)
# y -= 20
# if y < 100:
# c.showPage()
# y = 800
# c.save()
# return output_path
# except Exception as e:
# print(f"Ошибка генерации PDF: {e}")
# return None