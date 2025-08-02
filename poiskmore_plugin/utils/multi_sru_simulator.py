# (Доработка: реальная логика intersect) python def intersect(route1, route2):
# Простая проверка на пересечение линий (можно расширить)
for p1 in route1: for p2 in route2: if p1 == p2: return True return False
def simulate_multi_sru(routes): collisions = [] for i, route1 in enumerate(routes): for j, route2 in enumerate(routes[i+1:], start=i+1): if intersect(route1, route2): collisions.append((i, j)) return collisions
