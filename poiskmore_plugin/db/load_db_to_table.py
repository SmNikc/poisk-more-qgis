from PyQt5.QtWidgets import QTableWidget
import sqlite3
def load_db_to_table(db_path, table_widget):
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT * FROM incidents')
rows = cursor.fetchall()
table_widget.setRowCount(len(rows))
for row_num, row_data in enumerate(rows):
for col_num, data in enumerate(row_data):
table_widget.setItem(row_num, col_num, QTableWidgetItem(str(data)))
conn.close()