import sqlite3
class IncidentStorage:
def __init__(self, db_path):
self.conn = sqlite3.connect(db_path)
self.cursor = self.conn.cursor()
self.cursor.execute('CREATE TABLE IF NOT EXISTS incidents (id INTEGER PRIMARY KEY, data TEXT)')
def store_incident(self, data):
self.cursor.execute('INSERT INTO incidents (data) VALUES (?)', (str(data),))
self.conn.commit()
def __del__(self):
self.conn.close()