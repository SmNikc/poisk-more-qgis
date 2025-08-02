python from reportlab.lib.pagesizes import A4 from reportlab.pdfgen import canvas import tempfile
def generate_plan_pdf(prob_matrix): temp_path = tempfile.mktemp(suffix=".pdf") c = canvas.Canvas(temp_path, pagesize=A4) c.drawString(100, 800, "Карта вероятности")
# max_val = max(map(max, prob_matrix)) step = 500 / len(prob_matrix) for i, row in enumerate(prob_matrix): for j, val in enumerate(row): shade = int(255 * (1 - val / max_val)) c.setFillGray(shade / 255.0) c.rect(50 + j * step, 300 + i * step, step, step, fill=True, stroke=False)
c.save() return temp_path
