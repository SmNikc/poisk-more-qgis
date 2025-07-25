# Утилиты координат. Улучшен: Try-except
# для парсинга.
def parse_coords(coord_str):
# try:
# lat, lon = map(float, coord_str.strip().split(","))
# return lat, lon
# except ValueError:
# return None, None
def format_coords(lat, lon):
# return f"{lat:.4f}, {lon:.4f}"