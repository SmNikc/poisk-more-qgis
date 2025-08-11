from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
class PlanSearchManager:
def generate_plan_pdf(self, data):
filepath = "plan.pdf"
c = canvas.Canvas(filepath, pagesize=letter)
c.drawString(100, 750, str(data))
c.save()
return filepath