import xml.etree.ElementTree as ET
import os
class SerializationHelper:
@staticmethod
def deserialize_file(file_type, path):
if os.path.exists(path):
tree = ET.parse(path)
return tree.getroot()
return None