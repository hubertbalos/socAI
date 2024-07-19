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
        landHexes = self.getLandHexes()
        seaHexes = self.getSeaHexes(landHexes)
        vertices = self.getVertices(landHexes, seaHexes)

        self.hexes.update(landHexes)
        self.assignPorts(seaHexes, vertices)
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
        
        # computing vertex neighbors
        keys = list(newVertices.keys())
        radius = math.sqrt((keys[1].x - keys[0].x)**2 + (keys[1].y - keys[0].y)**2) * 1.01
        for currentVertex in newVertices:
            for otherVertex in newVertices:
                if otherVertex != currentVertex:
                    distance = math.sqrt((otherVertex.x - currentVertex.x)**2 + (otherVertex.y - currentVertex.y)**2)
                    if distance <= radius:
                        newVertices[currentVertex].vertexNeighbors.append(otherVertex)

        # for vertex in newVertices:
        #     print(len(newVertices[vertex].vertexNeighbors))
        
        return newVertices

    def getLandHexes(self):
        "Returns a dictionary containing the land hexgrid"
        landHexes = {}
        while not self.isValidLandHexPlacement(landHexes) or len(landHexes) == 0:
            landHexes.clear()
            resourceList = self.getRandomResourceList()
            # adding the first hex at the origin
            newHextile = Hextile()
            newHextile.resource, newHextile.value = resourceList.pop()
            landHexes[Hex(0, 0, 0)] = newHextile

            # building the remaining hexes around the origin
            for n in range(2):
                newLandHexes = {}
                for coord, hextile in landHexes.items():
                    for direction in range(6):
                        neighbor = hex_neighbor(coord, direction)
                        if all(neighbor != coord for coord in landHexes) and all(neighbor != coord for coord in newLandHexes): 
                            newHextile = Hextile()
                            newHextile.resource, newHextile.value = resourceList.pop()
                            newLandHexes[neighbor] = newHextile
                landHexes.update(newLandHexes)
            
            # adding hextile neighbors
            for coord, hextile in landHexes.items():
                for direction in range(6):
                    neighbor = hex_neighbor(coord, direction)
                    hextile.hexNeighbors.append(neighbor)

        return landHexes
    
    def isValidLandHexPlacement(self, landHexes):
        for coord, hextile in landHexes.items():
            if hextile.value == 6 or hextile.value == 8:
                for neighbor in hextile.hexNeighbors:
                    if abs(neighbor.q) != 3 and abs(neighbor.r) != 3 and abs(neighbor.s) != 3:
                        if landHexes[neighbor].value == 6 or landHexes[neighbor].value == 8:
                            return False
        return True

    
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

        # adding hextile neighbors
        for coord, hextile in seaHexes.items():
            for direction in range(6):
                    neighbor = hex_neighbor(coord, direction)
                    if neighbor in landHexes or neighbor in seaHexes:
                        hextile.hexNeighbors.append(neighbor)
        
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
    
    def assignPorts(self, seaHexes, vertices):
        portTypes = list(np.random.permutation([
            "ORE", "WHEAT", "WOOD", "BRICK", "SHEEP", "3:1", "3:1", "3:1", "3:1" ]))
        seaHexesList = list(seaHexes.keys())
        randomCoord = np.random.randint(0, len(seaHexesList))
        coord = seaHexesList.pop(randomCoord)
        seaHexes[coord].hasPort = True
        seaHexes[coord].portType = portTypes.pop()
        self.makeTwoVerticesPorts(seaHexes[coord], vertices)
        ports = 1
        traversedSeaTiles = [coord]
        while ports < 9:
            for neighbor in seaHexes[coord].hexNeighbors:
                if neighbor in seaHexes and neighbor not in traversedSeaTiles:
                    if len(traversedSeaTiles) % 2 == 0:
                        seaHexes[neighbor].hasPort = True
                        seaHexes[neighbor].portType = portTypes.pop()
                        self.makeTwoVerticesPorts(seaHexes[neighbor], vertices)
                        ports += 1
                    traversedSeaTiles.append(coord)
                    coord = neighbor
                    break
    
    def makeTwoVerticesPorts(self, seaHex, vertices):
        randomIndex = np.random.randint(0, len(seaHex.vertexChildren))
        coord = seaHex.vertexChildren[randomIndex]
        vertices[coord].hasPort = True
        vertices[coord].portType = seaHex.portType
        alreadySelectedIndex = randomIndex
        alreadySelectedCoord = coord
        while alreadySelectedIndex == randomIndex or coord not in vertices[alreadySelectedCoord].vertexNeighbors:
            randomIndex = np.random.randint(0, len(seaHex.vertexChildren))
            coord = seaHex.vertexChildren[randomIndex]
        vertices[coord].hasPort = True
        vertices[coord].portType = seaHex.portType
        
        





            
            

        

