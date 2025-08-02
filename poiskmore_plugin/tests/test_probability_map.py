python import pytest from alg.alg_probabilities import compute_probability_map
def test_probability_map_shape(): matrix = compute_probability_map((60, 30), 50, 5, 10, 45, 2, 90, 3) assert matrix.shape == (20, 20)
