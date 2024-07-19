import collections
import hexlib

class Hextile():
    """
    xxx
    """
    def __init__(self):
        self.resource = None
        self.value = None

        self.hexNeighbors = []
        self.vertexChildren = []

        self.hasPort = False
        self.portType = None

        self.hasRobber = False

class Vertex():
    """
    xxx
    """
    def __init__(self):
        self.vertexNeighbors = []
        self.hexParents = []

        self.hasPort = False
        self.portType = None
