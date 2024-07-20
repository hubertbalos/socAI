from components import Hextile, Vertex, Edge
from hexlib import *
import numpy as np
import random

class Board():
    """
    Contains the board state
    """
    def __init__(self, board_dimensions):
        # board is made of hexagonal hexes and their vertices
        self.hexes = {}
        self.vertices = {}
        self.edges = {}

        self.width, self.height = board_dimensions
        self.hex_size = 50
        self.layout = Layout(layout_flat, Point(self.hex_size, self.hex_size), Point(self.width/2, self.height/2))

        self.generate_random_board()
    
    def generate_random_board(self):
        land_hexes = self.generate_land_hexes()
        sea_hexes = self.generate_sea_hexes(land_hexes)
        vertices = self.generate_vertices(land_hexes, sea_hexes)
        edges = self.generate_edges(vertices)

        self.assign_ports(sea_hexes, vertices)

        self.hexes.update(land_hexes)
        self.hexes.update(sea_hexes)
        self.vertices.update(vertices)
        self.edges.update(edges)
    
    def generate_edges(self, vertices):
        "Returns a dictionary containing the hexgrid edges"

        new_edges = {}
        traversed_vertices = []
        id = 0
        for coord, vertex in vertices.items():
            for neighbor in vertex.vertex_neighbors:
                if neighbor not in traversed_vertices:
                    new_edge = Edge()
                    new_edge.vertex_parents.append(coord)
                    new_edge.vertex_parents.append(neighbor)
                    new_edges[id] = new_edge
                    id += 1
            traversed_vertices.append(coord)
        
        print(f"TOTAL EDGES: {len(new_edges)}")

        return new_edges
    
    def generate_vertices(self, land_hexes, sea_hexes):
        "Returns a dictionary containing the hexgrid vertices"

        # adding all vertices
        new_vertices = {}
        for coord, hextile in land_hexes.items():
            corners = polygon_corners(self.layout, coord)
            for vertex in corners:
                hextile.vertex_children.append(vertex)
                if vertex not in new_vertices:
                    new_vertex = Vertex()
                    new_vertices[vertex] = new_vertex
        
        # adding vertex children and hex parents
        for coord, hextile in land_hexes.items():
            corners = polygon_corners(self.layout, coord)
            for vertex in corners:
                new_vertices[vertex].hex_parents.append(hextile)
        
        for coord, hextile in sea_hexes.items():
            corners = polygon_corners(self.layout, coord)
            for vertex in corners:
                if vertex in new_vertices:
                    hextile.vertex_children.append(vertex)
                    new_vertices[vertex].hex_parents.append(hextile)
        
        # computing vertex neighbors
        keys = list(new_vertices.keys())
        radius = math.sqrt((keys[1].x - keys[0].x)**2 + (keys[1].y - keys[0].y)**2) * 1.01
        for current_vertex in new_vertices:
            for other_vertex in new_vertices:
                if other_vertex != current_vertex:
                    distance = math.sqrt((other_vertex.x - current_vertex.x)**2 + (other_vertex.y - current_vertex.y)**2)
                    if distance <= radius:
                        new_vertices[current_vertex].vertex_neighbors.append(other_vertex)

        # for vertex in new_vertices:
        #     print(len(new_vertices[vertex].vertex_neighbors))
        
        return new_vertices

    def generate_land_hexes(self):
        "Returns a dictionary containing the land hexgrid"
        land_hexes = {}
        while not self.is_valid_land_hex_placement(land_hexes) or len(land_hexes) == 0:
            land_hexes.clear()
            resource_list = self.get_random_resource_list()
            # adding the first hex at the origin
            new_hextile = Hextile()
            new_hextile.resource, new_hextile.value = resource_list.pop()
            if new_hextile.resource == "DESERT":
                new_hextile.has_robber = True
            land_hexes[Hex(0, 0, 0)] = new_hextile

            # building the remaining hexes around the origin
            for n in range(2):
                new_land_hexes = {}
                for coord, hextile in land_hexes.items():
                    for direction in range(6):
                        neighbor = hex_neighbor(coord, direction)
                        if all(neighbor != coord for coord in land_hexes) and all(neighbor != coord for coord in new_land_hexes): 
                            new_hextile = Hextile()
                            new_hextile.resource, new_hextile.value = resource_list.pop()
                            if new_hextile.resource == "DESERT":
                                new_hextile.has_robber = True
                            new_land_hexes[neighbor] = new_hextile
                land_hexes.update(new_land_hexes)
            
            # adding hextile neighbors
            for coord, hextile in land_hexes.items():
                for direction in range(6):
                    neighbor = hex_neighbor(coord, direction)
                    hextile.hex_neighbors.append(neighbor)
            

        return land_hexes
    
    def is_valid_land_hex_placement(self, land_hexes):
        for coord, hextile in land_hexes.items():
            if hextile.value == 6 or hextile.value == 8:
                for neighbor in hextile.hex_neighbors:
                    if abs(neighbor.q) != 3 and abs(neighbor.r) != 3 and abs(neighbor.s) != 3:
                        if land_hexes[neighbor].value == 6 or land_hexes[neighbor].value == 8:
                            return False
        return True

    
    def generate_sea_hexes(self, land_hexes):
        "Returns a dictionary containg the sea hexgrid"
        # building the sea hexes surrounding the current land hexgrid
        sea_hexes = {}
        for coord, hextile in land_hexes.items():
            for direction in  range(6):
                neighbor = hex_neighbor(coord, direction)
                if all(neighbor != coord for coord in land_hexes):
                    new_hextile = Hextile()
                    new_hextile.resource = "SEA"
                    sea_hexes[neighbor] = new_hextile

        # adding hextile neighbors
        for coord, hextile in sea_hexes.items():
            for direction in range(6):
                    neighbor = hex_neighbor(coord, direction)
                    if neighbor in land_hexes or neighbor in sea_hexes:
                        hextile.hex_neighbors.append(neighbor)
        
        assert(len(sea_hexes) == 18)

        return sea_hexes

    def get_random_resource_list(self):
        "Returns a random list of resource type and value pairs"
        # Resource = collections.namedtuple("Resource", ["type", "value"])

        resource_tiles = np.random.permutation([
            "ORE", "ORE", "ORE", 
            "WHEAT", "WHEAT", "WHEAT", "WHEAT", 
            "WOOD", "WOOD", "WOOD", "WOOD", 
            "BRICK", "BRICK", "BRICK",
            "SHEEP", "SHEEP", "SHEEP", "SHEEP"])
        
        tiles_values = np.random.permutation([
            2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12])

        resource_list = []
        for i in range(len(resource_tiles)):
                resource_list.append((resource_tiles[i], tiles_values[i]))
        
        resource_list.insert(np.random.randint(0, len(resource_list)), ("DESERT", None))

        return resource_list
    
    def assign_ports(self, sea_hexes, vertices):
        port_types = list(np.random.permutation([
            "ORE", "WHEAT", "WOOD", "BRICK", "SHEEP", "3:1", "3:1", "3:1", "3:1" ]))
        sea_hexesList = list(sea_hexes.keys())
        coord = random.choice(sea_hexesList)
        sea_hexes[coord].has_port = True
        sea_hexes[coord].port_type = port_types.pop()
        self.make_two_vertices_ports(sea_hexes[coord], vertices)
        ports = 1
        traversed_sea_tiles = [coord]
        while ports < 9:
            for neighbor in sea_hexes[coord].hex_neighbors:
                if neighbor in sea_hexes and neighbor not in traversed_sea_tiles:
                    if len(traversed_sea_tiles) % 2 == 0:
                        sea_hexes[neighbor].has_port = True
                        sea_hexes[neighbor].port_type = port_types.pop()
                        self.make_two_vertices_ports(sea_hexes[neighbor], vertices)
                        ports += 1
                    traversed_sea_tiles.append(coord)
                    coord = neighbor
                    break
    
    def make_two_vertices_ports(self, seaHex, vertices):
        coord = random.choice(seaHex.vertex_children)
        vertices[coord].has_port = True
        vertices[coord].port_type = seaHex.port_type
        already_selected_coord = coord
        while coord not in vertices[already_selected_coord].vertex_neighbors:
            coord = random.choice(seaHex.vertex_children)
        vertices[coord].has_port = True
        vertices[coord].port_type = seaHex.port_type
        
        





            
            

        

