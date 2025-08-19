from qgis.core import QgsPointXY
class SegmentNode:
    def __init__(self, seg_string, coord: QgsPointXY, segment_index: int, segment_octant: int):
        self.coord = coord
        self.segment_index = segment_index
        self.seg_string = seg_string
        self.segment_octant = segment_octant
        self.is_interior = not coord.equals2D(seg_string.coordinates[segment_index])
    def is_end_point(self, max_segment_index: int) -> bool:
        if self.segment_index == 0 and not self.is_interior:
            return True
        return self.segment_index == max_segment_index
    def compare_to(self, other: 'SegmentNode') -> int:
        if self.segment_index < other.segment_index:
            return -1
        if self.segment_index > other.segment_index:
            return 1
        if self.coord.equals2D(other.coord):
            return 0
        return 1 if self.coord.x() > other.coord.x() else -1  # Упрощено