import numpy as np
def generate_probability_grid(area, resolution):
x = np.linspace(area.xMinimum(), area.xMaximum(), resolution)
y = np.linspace(area.yMinimum(), area.yMaximum(), resolution)
grid = np.meshgrid(x, y)
return grid