from typing import List, Collection
from qgis.core import QgsPointXY
class Node:
    def __init__(self, pt: QgsPointXY):
        self.pt = pt
class NodeMap(dict):
    def find(self, pt: QgsPointXY) -> Node:
        return self.get(pt, None)
class PlanarGraph:
    def __init__(self):
        self.edges = []
        self.dir_edges = []
        self.node_map = NodeMap()
    def find_node(self, pt: QgsPointXY) -> Node:
        return self.node_map.find(pt)
    def add_node(self, node: Node):
        self.node_map[node.pt] = node
    def add_edge(self, edge):
        self.edges.append(edge)
        self.dir_edges.extend([edge.dir_edge0, edge.dir_edge1])
    def get_nodes(self) -> Collection[Node]:
        return self.node_map.values()