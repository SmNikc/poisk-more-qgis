import sqlite3
def init_schema(db_path):
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS schema_table (id INTEGER PRIMARY KEY, name TEXT)')
conn.commit()
conn.close()