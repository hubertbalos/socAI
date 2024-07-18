from components import Hextile, Vertex
from hexlib import *
import numpy as np

class Board():
    """
    Contains the board state
    """
    def __init__(self, boardDimensions):
        # board is made of hexagonal hexes and their vertices
        self.hexes = {}
        self.vertices = {}

        self.width, self.height = boardDimensions
        self.hexSize = 50
        self.layout = Layout(layout_flat, Point(self.hexSize, self.hexSize), Point(self.width/2, self.height/2))

        self.generateBoard()
    
    def generateBoard(self):
        resourceList = self.getRandomResourceList()
        landHexes = self.getLandHexes(resourceList)
        seaHexes = self.getSeaHexes(landHexes)
        vertices = self.getVertices(landHexes, seaHexes)

        self.hexes.update(landHexes)
        self.hexes.update(seaHexes)
        self.vertices.update(vertices)
    
    def getVertices(self, landHexes, seaHexes):
        "Return a dictionary containing the hexgrid vertices"

        # adding all vertices
        newVertices = {}
        for coord, hextile in landHexes.items():
            corners = polygon_corners(self.layout, coord)
            for vertex in corners:
                hextile.vertexChildren.append(vertex)
                if vertex not in newVertices:
                    newVertex = Vertex()
                    newVertices[vertex] = newVertex
        
        # adding vertex children and hex parents
        for coord, hextile in landHexes.items():
            corners = polygon_corners(self.layout, coord)
            for vertex in corners:
                newVertices[vertex].hexParents.append(hextile)
        
        for coord, hextile in seaHexes.items():
            corners = polygon_corners(self.layout, coord)
            for vertex in corners:
                if vertex in newVertices:
                    hextile.vertexChildren.append(vertex)
                    newVertices[vertex].hexParents.append(hextile)
        
        return newVertices

    def getLandHexes(self, resourceList):
        "Returns a dictionary containing the land hexgrid"
        # adding the first hex at the origin
        landHexes = {}
        newHextile = Hextile()
        newHextile.resource, newHextile.value = resourceList.pop()
        landHexes[Hex(0, 0, 0)] = newHextile

        # building the remaining hexes around the origin
        for n in range(2):
            newLandHexes = {}
            for coord, hextile in landHexes.items():
                for direction in range(6):
                    neighbor = hex_neighbor(coord, direction)
                    if neighbor not in hextile.hexNeighbors:
                        hextile.hexNeighbors.append(neighbor)
                    if all(neighbor != coord for coord in landHexes) and all(neighbor != coord for coord in newLandHexes): 
                        newHextile = Hextile()
                        newHextile.resource, newHextile.value = resourceList.pop()
                        newLandHexes[neighbor] = newHextile
            landHexes.update(newLandHexes)

        return landHexes

    
    def getSeaHexes(self, landHexes):
        "Returns a dictionary containg the sea hexgrid"
        # building the sea hexes surrounding the current land hexgrid
        seaHexes = {}
        for coord, hextile in landHexes.items():
            for direction in  range(6):
                neighbor = hex_neighbor(coord, direction)
                if all(neighbor != coord for coord in landHexes):
                    newHextile = Hextile()
                    newHextile.resource = "SEA"
                    seaHexes[neighbor] = newHextile

        for coord, hextile in seaHexes.items():
            for direction in range(6):
                    neighbor = hex_neighbor(coord, direction)
                    if neighbor in landHexes or neighbor in seaHexes:
                        seaHexes[coord].hexNeighbors.append(neighbor)
        
        assert(len(seaHexes) == 18)

        return seaHexes

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
    
    def assignPorts(self, seaHexes):
        None






