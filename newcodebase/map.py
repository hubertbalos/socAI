from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from hexlib import *
import time
import random
import math

@dataclass
class Hextile():
    "Hex coordinate contained within Hextile Dict"
    resource: str = None
    value: str = None

    hex_neighbors: List[Hex] = field(default_factory=list)
    vertex_neighbors: List[Point] = field(default_factory=list)

    port_type: str = None
    has_robber: bool = False

@dataclass
class Vertex():
    "Pixel coordinate contained within Vertex Dict"
    vertex_neighbors: List[Hex] = field(default_factory=list) # list of vertex coords
    hex_neighbors: List[Point] = field(default_factory=list) # list of hex coords
    edge_neighbors: List[int] = field(default_factory=list) # list of edge indexes

    port_type: str = None
    owner_colour: str = None
    building: str = None

@dataclass
class Edge():
    "Index contained within Edge Dict"
    vertex_neighbors: List[Point] = field(default_factory=list) # list of vertex coords

    owner_colour: str = None
    has_road: bool = False

class CatanMap():
    "By default initialises a random Catan map"

    def __init__(self, mapDimensions: Tuple[int, int], firstRun: bool, randomMap: bool=True):
        self.gamelog = False

        self.first_run = firstRun

        self.hexes: Dict[Hex, Hextile] = {}
        self.vertices: Dict[Point, Vertex] = {}
        self.edges: Dict[int, Edge] = {}

        # useful for quickly finding specific tiles from their values
        self.values_dict: Dict[int, List[Hex]] = {}

        self.robber_coord: Hex = None

        width, height = mapDimensions
        hex_size = 50
        self.layout = Layout(layout_flat, Point(hex_size, hex_size), Point(width/2, height/2))

        if randomMap: 
            if self.gamelog: start = time.time()
            self.generate_random_map()
            if self.gamelog: print(f"## MAP GENERATION TIME ##: {time.time() - start}")
    
    def generate_random_map(self):
        if self.gamelog: start = time.time()
        land_hexes = self.generate_land_hexes()
        if self.gamelog: print(f"Land Hex generation time: {time.time() - start}")

        if self.gamelog: start = time.time()
        sea_hexes = self.generate_sea_hexes(land_hexes)
        if self.gamelog: print(f"Sea Hex generation time: {time.time() - start}")

        if self.gamelog: start = time.time()
        vertices = self.generate_vertices(land_hexes, sea_hexes)
        if self.gamelog: print(f"Vertex generation time: {time.time() - start}")

        if self.gamelog: start = time.time()
        edges = self.generate_edges(vertices)
        if self.gamelog: print(f"Edge generation time: {time.time() - start}")

        if self.gamelog: start = time.time()
        self.assign_ports(sea_hexes, vertices)
        if self.gamelog: print(f"Port assignment time: {time.time() - start}")

        self.hexes.update(land_hexes)
        self.hexes.update(sea_hexes)
        self.vertices.update(vertices)
        self.edges.update(edges)

        return 1

    def generate_land_hexes(self) -> Dict[Hex, Hextile]:
        land_hexes: Dict[Hex, Hextile] = {}
        added_hexcoords: List[Hex] = []

        # adding the first hex at the origin
        new_hextile = Hextile()
        land_hexes[Hex(0, 0, 0)] = new_hextile
        added_hexcoords.append(Hex(0, 0, 0))

        # building the remaining hexes around the origin
        for _ in range(2):
            new_land_hexes = {}
            for coord, hextile in land_hexes.items():
                for direction in range(6):
                    neighbor: Hex = hex_neighbor(coord, direction)
                    if neighbor not in added_hexcoords:
                        added_hexcoords.append(neighbor)
                        new_hextile = Hextile()
                        new_land_hexes[neighbor] = new_hextile
            land_hexes.update(new_land_hexes)
            
        # adding hex neighbors
        for coord, hextile in land_hexes.items():
            for direction in range(6):
                neighbor = hex_neighbor(coord, direction)
                hextile.hex_neighbors.append(neighbor)
        
        # initialising hex resources and values
        while not self.is_valid_land_hex_placement(land_hexes):
            self.values_dict.clear()
            resource_list = self.get_random_resource_list()

            for coord, hextile in land_hexes.items():
                resource, value = resource_list.pop()
                hextile.resource = resource
                hextile.value = value

                if value is None: # ie is DESERT
                    robber_coord = coord
                    self.robber_coord = coord
                else:
                    if value not in self.values_dict:
                        self.values_dict[value] = []
                    self.values_dict[value].append(coord)
        
        land_hexes[robber_coord].has_robber = True

        return land_hexes

    def is_valid_land_hex_placement(self, land_hexes) -> bool:
        if len(self.values_dict) == 0:
            return False
        
        six_coords = self.values_dict[6]
        eight_coords = self.values_dict[8]
        coords = six_coords + eight_coords

        for coord in coords:
            hextile = land_hexes[coord]
            for neighbor in hextile.hex_neighbors:
                if neighbor in coords:
                    return False
        return True

    def get_random_resource_list(self) -> List[Tuple[str, int]]:
        "Returns a random list of tuples (resource type, value)"

        resource_tiles = [
            "ORE", "ORE", "ORE", 
            "WHEAT", "WHEAT", "WHEAT", "WHEAT", 
            "WOOD", "WOOD", "WOOD", "WOOD", 
            "BRICK", "BRICK", "BRICK",
            "SHEEP", "SHEEP", "SHEEP", "SHEEP"
            ]
        
        tiles_values = [
            2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12
            ]
        
        # random.sample is significantly faster than random.shuffle
        shuffled_resource_tiles = random.sample(resource_tiles, len(resource_tiles))
        shuffled_tiles_values = random.sample(tiles_values, len(tiles_values))

        resource_list = list(zip(shuffled_resource_tiles, shuffled_tiles_values))
        resource_list.insert(random.randint(0, len(resource_list)), ("DESERT", None))

        return resource_list
    
    def generate_sea_hexes(self, land_hexes: Dict[Hex, Hextile]) -> Dict[Hex, Hextile]:
        # building the sea hexes surrounding the current land hexgrid
        sea_hexes: Dict[Hex, Hextile] = {}

        for coord, hextile in land_hexes.items():
            for direction in  range(6):
                neighbor: Hex = hex_neighbor(coord, direction)
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

        return sea_hexes
    
    def generate_vertices(self, land_hexes, sea_hexes) -> Dict[Point, Vertex]:
        new_vertices: Dict[Point, Vertex] = {}

        # adding all vertices
        for coord, hextile in land_hexes.items():
            corners = polygon_corners(self.layout, coord)
            for vertex in corners:
                # adding landhex vertex neighbors
                hextile.vertex_neighbors.append(vertex)
                if vertex not in new_vertices:
                    new_vertex = Vertex()
                    new_vertices[vertex] = new_vertex
        
        # adding land hex neighbors
        for coord, hextile in land_hexes.items():
            corners = polygon_corners(self.layout, coord)
            for vertex in corners:
                new_vertices[vertex].hex_neighbors.append(coord)
        
        # adding seahex vertex neighbors
        for coord, hextile in sea_hexes.items():
            corners = polygon_corners(self.layout, coord)
            for vertex in corners:
                if vertex in new_vertices:
                    hextile.vertex_neighbors.append(vertex)
        
        # computing vertex neighbors
        keys = list(new_vertices.keys())
        radius = math.sqrt((keys[1].x - keys[0].x)**2 + (keys[1].y - keys[0].y)**2) * 1.01
        for current_vertex in new_vertices:
            for other_vertex in new_vertices:
                if other_vertex != current_vertex:
                    distance = math.sqrt((other_vertex.x - current_vertex.x)**2 + (other_vertex.y - current_vertex.y)**2)
                    if distance <= radius:
                        new_vertices[current_vertex].vertex_neighbors.append(other_vertex)
        
        return new_vertices
    
    def generate_edges(self, vertices) -> Dict[int, Edge]:
        new_edges: Dict[int, Edge] = {}
        traversed_vertices: List[Point] = []

        id = 0
        for coord, vertex in vertices.items():
            for neighbor in vertex.vertex_neighbors:
                if neighbor not in traversed_vertices:
                    new_edge = Edge()
                    new_edge.vertex_neighbors.append(coord)
                    new_edge.vertex_neighbors.append(neighbor)
                    new_edges[id] = new_edge
                    id += 1
            traversed_vertices.append(coord)
        
        for id, edge in new_edges.items():
            for neighbor in edge.vertex_neighbors:
                vertices[neighbor].edge_neighbors.append(id)

        return new_edges
    
    def assign_ports(self, sea_hexes, vertices):
        "Randomly assigns 9 sea hexes as ports"
        port_types = [
            "ORE", "WHEAT", "WOOD", "BRICK", "SHEEP", "3:1", "3:1", "3:1", "3:1" 
            ]
        port_types = random.sample(port_types, len(port_types))
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
        "For sea hex with port chooses two random hex vertex children as port vertices"
        coord = random.choice(seaHex.vertex_neighbors)
        vertices[coord].has_port = True
        vertices[coord].port_type = seaHex.port_type
        already_selected_coord = coord
        while coord not in vertices[already_selected_coord].vertex_neighbors:
            coord = random.choice(seaHex.vertex_neighbors)
        vertices[coord].has_port = True
        vertices[coord].port_type = seaHex.port_type

# def TESTING():
#     print(f"-- Initial RUN --")
#     catanmap = CatanMap(mapDimensions=(750, 910), firstRun=True)
#     print(f"-- Secondary RUN --")
#     catanmap = CatanMap(mapDimensions=(750, 910), firstRun=False)

# TESTING()