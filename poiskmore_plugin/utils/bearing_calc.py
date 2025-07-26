import math

def calculate_bearing(lat1, lon1, lat2, lon2):
    if math.isnan(lat1) or math.isnan(lon1) or math.isnan(lat2) or math.isnan(lon2):
        return 0.0  # Нулевой азимут при некорректных данных
    if lat1 == lat2 and lon1 == lon2:
        return 0.0  # Нулевая дистанция
    d_lon = math.radians(lon2 - lon1)
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    x = math.sin(d_lon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(d_lon)
    bearing = math.atan2(x, y)  # Формула вычисления азимута по координатам
    return (math.degrees(bearing) + 360) % 360