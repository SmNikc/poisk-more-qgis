"""Расчёт вероятностной карты поиска."""

import math
import numpy as np

from .alg_drift import calculate_drift


def compute_probability_map(
    lkp,
    radius,
    resolution,
    wind_speed,
    wind_dir,
    current_speed,
    current_dir,
    time_hours,
):
    """Возвращает матрицу вероятностей вокруг LKP."""

    drift_x, drift_y = calculate_drift(
        0, 0, wind_speed, wind_dir, current_speed, current_dir, time_hours
    )

    size = int((radius * 2) / resolution)
    center = size // 2
    matrix = np.zeros((size, size))

    for i in range(size):
        for j in range(size):
            dx = (j - center) * resolution - drift_x
            dy = (i - center) * resolution - drift_y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            matrix[i][j] = max(0, 1 - (distance / radius))

    return matrix

