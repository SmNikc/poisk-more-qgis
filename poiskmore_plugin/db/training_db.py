import sqlite3
def create_training_db(db_path):
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS training (id INTEGER PRIMARY KEY, exercise TEXT)')
cursor.execute('INSERT INTO training (exercise) VALUES (?)', ("Test exercise",))
conn.commit()
conn.close()