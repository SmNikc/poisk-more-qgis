Загрузка XML. Улучшен: Добавлена try-
except, проверка на наличие элементов.
import xml.etree.ElementTree as ET
def load_incidents_from_xml(path):
try:
tree = ET.parse(path)
root = tree.getroot()
incidents = []
for item in root.findall(".//incident"):
inc = {
"id": item.findtext("id", ""),
"datetime": item.findtext("datetime", ""),
"description": item.findtext("description", "")
}
if all(inc.values()):  # Проверка на полноту
incidents.append(inc)
return incidents
except ET.ParseError as e:
print(f"Ошибка парсинга XML: {e}")
return []
