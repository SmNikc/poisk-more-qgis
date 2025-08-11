from qgis.core import QgsPointXY
from math import cos, sin, radians
def calculate_drift(start_point, wind_speed, wind_dir, current_speed, current_dir, time_hours):
wind_drift_x = wind_speed * cos(radians(wind_dir)) * time_hours
wind_drift_y = wind_speed * sin(radians(wind_dir)) * time_hours
current_drift_x = current_speed * cos(radians(current_dir)) * time_hours
current_drift_y = current_speed * sin(radians(current_dir)) * time_hours
total_drift_x = wind_drift_x + current_drift_x
total_drift_y = wind_drift_y + current_drift_y
end_point = QgsPointXY(start_point.x() + total_drift_x, start_point.y() + total_drift_y)
return end_point