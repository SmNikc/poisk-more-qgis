python from utils.multi_sru_simulator import simulate_multi_sru
def test_simulate_no_collision(): routes = [[(0,0), (1,1)], [(2,2), (3,3)]] collisions = simulate_multi_sru(routes) assert len(collisions) == 0
def test_simulate_with_collision(): routes = [[(0,0), (1,1)], [(1,1), (2,2)]] collisions = simulate_multi_sru(routes) assert len(collisions) == 1
