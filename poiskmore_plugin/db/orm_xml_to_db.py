import xml.etree.ElementTree as ET
import sqlite3
def orm_xml_to_db(xml_path, db_path):
tree = ET.parse(xml_path)
root = tree.getroot()
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS xml_data (tag TEXT, text TEXT)')
for elem in root:
cursor.execute('INSERT INTO xml_data (tag, text) VALUES (?, ?)', (elem.tag, elem.text))
conn.commit()
conn.close()