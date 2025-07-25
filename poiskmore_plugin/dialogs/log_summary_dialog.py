# Диалог суммарного лога. Исправлено:
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
import os
from ..reports.log_summary_generator import generate_log_summary
class LogSummaryDialog(QDialog):
def init(self):
# super().init()
# self.setWindowTitle("Сводка по логам оператора")
# layout = QVBoxLayout()
# self.text = QTextEdit()
# self.text.setReadOnly(True)
# layout.addWidget(self.text)
# self.button = QPushButton("Обновить сводку")
# self.button.clicked.connect(self.update)
# layout.addWidget(self.button)
# self.setLayout(layout)
# self.update()
def update(self):
# generate_log_summary()
# summary_path = "log_summary.txt"
# if os.path.exists(summary_path):
# with open(summary_path, "r", encoding="utf-8") as f:
# self.text.setText(f.read())
# else:
# self.text.setText("Сводка не найдена. Проверьте генератор.")
 Лента публикации полного кода проекта "Поиск-Море" для QGIS (итоговый 
# вариант) — Фрагмент 15/16 (третья группа файлов, продолжение)
# Комментарий к фрагменту: Продолжение. orm_xml_to_db.py: Добавлена try-
# orm_xml_to_db.py вызывается для импорта; operator_log_dialog.py показывает 
# логи; probability_dialog.py генерирует параметры.
# CopyEdit