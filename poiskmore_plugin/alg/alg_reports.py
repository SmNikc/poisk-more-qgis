from PyQt5.QtWidgets import QMessageBox
def generate_report(data):
report = f"Отчет: {data}"
QMessageBox.information(None, "Отчет", report)
return report