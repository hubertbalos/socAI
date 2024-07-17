from components import Hextile, Vertex
from hexlib import *
import numpy as np

class Board():
    """
    Contains the board state
    """
    def __init__(self, boardDimensions):
        # board is made of hexagonal hexes and their vertices
        self.hexes = []
        self.vertices = []

        self.width, self.height = boardDimensions
        self.hexSize = 50
        self.layout = Layout(layout_flat, Point(self.hexSize, self.hexSize), Point(self.width/2, self.height/2))

        self.generateBoard()
    
    def generateBoard(self):
        resourceList = self.getRandomResourceList()

        newHextile = Hextile()
        newHextile.hexCoordinate = Hex(0, 0, 0)
        newHextile.resource, newHextile.value = resourceList[0]
        self.hexes.append(newHextile)
        index = 1

        # adding land hexes
        for n in range(2):
            landHexes = []
            for hextile in self.hexes:
                for direction in range(6):
                    neighbor = hex_neighbor(hextile.hexCoordinate, direction)
                    if all(neighbor != h.hexCoordinate for h in self.hexes) and all(neighbor != h.hexCoordinate for h in landHexes):
                        if index < len(resourceList):
                            newHextile = Hextile()
                            newHextile.hexCoordinate = neighbor
                            newHextile.resource, newHextile.value = resourceList[index]
                            landHexes.append(newHextile)
                            index += 1
            self.hexes.extend(landHexes)
        
        # adding sea hexes
        seaHexes = []
        for hextile in self.hexes:
            for direction in  range(6):
                neighbor = hex_neighbor(hextile.hexCoordinate, direction)
                if all(neighbor != h.hexCoordinate for h in self.hexes):
                    newHextile = Hextile()
                    newHextile.hexCoordinate = neighbor
                    newHextile.resource = "SEA"
                    seaHexes.append(newHextile)
        self.hexes.extend(seaHexes)

        # adding all vertices
        newVertices = []
        for hextile in self.hexes:
            if hextile.resource != "SEA":
                corners = polygon_corners(self.layout, hextile.hexCoordinate)
                for point in corners:
                    if all(point != v.coordinates for v in self.vertices):
                        newVertex = Vertex()
                        newVertex.coordinates = point
                        newVertices.append(newVertex)
        self.vertices.extend(newVertices)

    def getRandomResourceList(self):
        "Returns a random list of resource type and value pairs"
        # Resource = collections.namedtuple("Resource", ["type", "value"])

        resourceTiles = np.random.permutation([
            "ORE", "ORE", "ORE", 
            "WHEAT", "WHEAT", "WHEAT", "WHEAT", 
            "WOOD", "WOOD", "WOOD", "WOOD", 
            "BRICK", "BRICK", "BRICK",
            "SHEEP", "SHEEP", "SHEEP", "SHEEP"])
        tileValues = np.random.permutation([
            2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12])

        resourceList = []
        for i in range(len(resourceTiles)):
                resourceList.append((resourceTiles[i], tileValues[i]))
        
        resourceList.insert(np.random.randint(0, len(resourceList)), ("DESERT", None))

        return resourceList





