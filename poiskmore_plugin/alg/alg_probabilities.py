python import numpy as np import math
def compute_probability_map(lkp, radius, resolution, wind_speed, wind_dir, current_speed, current_dir, time_hours): drift_x, drift_y = calculate_drift(0, 0, wind_speed, wind_dir, current_speed, current_dir, time_hours) size = int((radius * 2) / resolution) center = size // 2 matrix = np.zeros((size, size))
for i in range(size): for j in range(size): dx = (j - center) * resolution - drift_x dy = (i - center) * resolution - drift_y distance = math.sqrt(dx2 + dy2) matrix[i][j] = max(0, 1 - (distance / radius))
return matrix
