import xml.etree.ElementTree as ET
def load_xml(xml_path):
tree = ET.parse(xml_path)
root = tree.getroot()
data = {}
for child in root:
data[child.tag] = child.text
return data