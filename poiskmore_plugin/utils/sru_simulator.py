def simulate_sru_movement(start, end, steps=10):
    """
    Симуляция движения SRU по заданному маршруту.
    Args:
        start: Кортеж (x, y) начальной точки
        end: Кортеж (x, y) конечной точки
        steps: Количество шагов (по умолчанию 10)
    Yields:
        Кортеж (x, y) для каждого шага
    Raises:
        ValueError: Если steps <= 0
        TypeError: Если start или end не кортежи
    """
    if not isinstance(start, (tuple, list)) or not isinstance(end, (tuple, list)):
        raise TypeError("start и end должны быть кортежами или списками")
    if steps <= 0:
        raise ValueError("Steps must be > 0")
    x0, y0 = start
    x1, y1 = end
    for i in range(steps + 1):
        t = i / steps
        yield (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)