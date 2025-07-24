Валидация GeoJSON. Улучшен: Строгая
проверка структуры, try-except.
import json
def validate_geojson(path):
try:
with open(path, "r", encoding="utf-8") as f:
data = json.load(f)
assert data.get("type") == "FeatureCollection"
assert "features" in data and isinstance(data["features"], list)
for feature in data["features"]:
assert feature.get("type") == "Feature"
assert "geometry" in feature
return True
except (json.JSONDecodeError, AssertionError):
return False
