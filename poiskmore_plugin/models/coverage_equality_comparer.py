from typing import Any
from qgis.core import QgsRectangle
class Coverage:
    def __init__(self, east: float = 0.0, north: float = 0.0, south: float = 0.0, west: float = 0.0):
        self.east = east
        self.north = north
        self.south = south
        self.west = west
    def to_qgs_rectangle(self) -> QgsRectangle:
        return QgsRectangle(self.west, self.south, self.east, self.north)
class CoverageEqualityComparer:
    def equals(self, x: Coverage, y: Coverage) -> bool:
        if x is y:
            return True
        return x.east == y.east and x.north == y.north and x.south == y.south and x.west == y.west
    def get_hash_code(self, obj: Coverage) -> int:
        if obj is None:
            raise ValueError("obj cannot be None")
        return hash((obj.east, obj.north, obj.south, obj.west))