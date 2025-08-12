from PyQt5.QtWidgets import QMessageBox


def generate_report(data):
    """Generate a simple report and display it."""
    report = f"Отчет: {data}"
    QMessageBox.information(None, "Отчет", report)
    return report
