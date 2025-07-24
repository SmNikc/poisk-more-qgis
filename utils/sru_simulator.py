Симулятор движения SRU. Улучшен:
Проверка steps, yield без sleep для тестов.
def simulate_sru_movement(start, end, steps=10):
if steps <= 0:
raise ValueError("Steps must be > 0")
x0, y0 = start
x1, y1 = end
for i in range(steps + 1):
t = i / steps
yield (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
