import collections
import hexlib

class Hextile():
    """
    Hex board component
    """
    def __init__(self):
        self.resource = None
        self.value = None

        self.hex_neighbors = []
        self.vertex_children = []

        self.has_port = False
        self.port_type = None

        self.has_robber = False

class Vertex():
    """
    Vertex board component
    """
    def __init__(self):
        self.vertex_neighbors = []
        self.hex_parents = []
        self.edge_children = []

        self.has_port = False
        self.port_type = None

        self.owner = None
        self.has_settlement = False
        self.has_city = False

class Edge():
    """
    Edge between vertices
    """
    def __init__(self):
        self.vertex_parents = []

        self.owner = None
        self.has_road = False