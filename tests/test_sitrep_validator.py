Тест валидатора SITREP. Улучшен:
Добавлен import pytest, тест на пустые
поля.
import pytest
def test_sitrep_data_complete():
data = {
"type": "INITIAL",
"datetime": "2025-07-23 13:00:00",
"sru": "Vessel-Alpha",
"coords": "60.0, 30.0",
"weather": "Clear",
"situation": "Test situation",
"actions": "Rescue started",
"attachment": ""
}
required_fields = ["type", "datetime", "sru", "coords", "weather", "situation", "actions"]
for field in required_fields:
assert data[field] != "", f"Поле {field} должно быть заполнено"
@pytest.mark.parametrize("missing", ["type", "datetime"])
def test_missing_field(missing):
data = {"type": "INITIAL", "datetime": "2025-07-23"}
del data[missing]
with pytest.raises(KeyError):
data[missing]
