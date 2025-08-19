from typing import List
from qgis.core import QgsFeature, QgsVectorLayer  # Для хранения графов в слоях
class PlanarGraph:
    def __init__(self):
        self.nodes = []  # Список узлов
class Subgraph:
    def __init__(self, parent_graph: PlanarGraph):
        self.parent_graph = parent_graph
        self.edges = set()
        self.dir_edges = []
        self.node_map = {}  # Словарь узлов
    def add(self, edge):
        if edge in self.edges:
            return
        self.edges.add(edge)
        self.dir_edges.extend([edge.dir_edge0, edge.dir_edge1])  # Предполагаем, что edge имеет dir_edges
        self.node_map[edge.from_node] = edge.from_node
        self.node_map[edge.to_node] = edge.to_node
    def get_dir_edges(self) -> List:
        return self.dir_edges
    def contains(self, edge) -> bool:
        return edge in self.edges