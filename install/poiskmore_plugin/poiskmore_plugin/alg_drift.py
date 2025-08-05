pythonimport math
from qgis.core import QgsPointXY

def calculate_asw(wind_data):
    sum_x = 0
    sum_y = 0
    n = len(wind_data)
    for d, v in wind_data:
        rad = math.radians(d)
        sum_x += v * math.cos(rad)
        sum_y += v * math.sin(rad)
    if n > 0:
        avg_x = sum_x / n
        avg_y = sum_y / n
        asw_speed_knots = math.sqrt(avg_x**2 + avg_y**2) * 1.94384
        asw_dir = (math.degrees(math.atan2(avg_y, avg_x)) + 360) % 360
        return asw_speed_knots, asw_dir
    return 0, 0

def calculate_twc(current_data):
    sum_x = 0
    sum_y = 0
    n = len(current_data)
    for d, v in current_data:
        rad = math.radians(d)
        sum_x += v * math.cos(rad)
        sum_y += v * math.sin(rad)
    if n > 0:
        avg_x = sum_x / n
        avg_y = sum_y / n
        twc_speed_knots = math.sqrt(avg_x**2 + avg_y**2)
        twc_dir = (math.degrees(math.atan2(avg_y, avg_x)) + 360) % 360
        return twc_speed_knots, twc_dir
    return 0, 0

def calculate_drift(lat, lon, asw_speed, asw_dir, twc_speed, twc_dir, time_hours):
    asw_rad = math.radians(asw_dir)
    twc_rad = math.radians(twc_dir)
    dx = (asw_speed * 0.03 * math.sin(asw_rad) + twc_speed * math.sin(twc_rad)) * time_hours
    dy = (asw_speed * 0.03 * math.cos(asw_rad) + twc_speed * math.cos(twc_rad)) * time_hours
    delta_lat = dy / 60
    delta_lon = dx / (60 * math.cos(math.radians(lat)))
    new_lat = lat + delta_lat
    new_lon = lon + delta_lon
    return QgsPointXY(new_lon, new_lat)