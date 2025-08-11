from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
def export_to_pdf(filepath, content):
c = canvas.Canvas(filepath, pagesize=letter)
c.drawString(100, 750, content)
c.save()