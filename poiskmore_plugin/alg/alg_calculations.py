from math import sqrt


def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two QgsPointXY points."""
    dx = point2.x() - point1.x()
    dy = point2.y() - point1.y()
    return sqrt(dx ** 2 + dy ** 2)


def calculate_area(size):
    """Calculate area of a square with given side length."""
    return size * size
