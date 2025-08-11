import json
class ConfigLoader:
def load(self, file_path):
with open(file_path, 'r') as f:
return json.load(f)