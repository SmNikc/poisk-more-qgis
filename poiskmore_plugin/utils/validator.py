class Validator:
def validate_input(self, data, required_fields):
errors = []
for field in required_fields:
if not data.get(field):
errors.append(f"Поле '{field}' обязательно")
return errors
def validate_incident(self, data):
errors = []
if not data.get('name'):
errors.append("Не указано название объекта")
if not data.get('coords'):
errors.append("Не указаны координаты")
if not data.get('type'):
errors.append("Не указан тип инцидента")
return errors
def validate_search_params(self, params):
errors = []
if params.get('radius', 0) <= 0:
errors.append("Радиус должен быть положительным")
if not params.get('mode'):
errors.append("Режим поиска не указан")
return errors