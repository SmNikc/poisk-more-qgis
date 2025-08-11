class Coverage:
def __init__(self, east=0.0, north=0.0, south=0.0, west=0.0):
self.east = east
self.north = north
self.south = south
self.west = west
class CoverageEqualityComparer:
def __eq__(self, other):
if isinstance(other, Coverage):
return (self.east == other.east and
self.north == other.north and
self.south == other.south and
self.west == other.west)
return False
def __hash__(self):
return hash((self.east, self.north, self.south, self.west))