from components import Hextile, Vertex, Edge
from hexlib import *
import numpy as np
import random

class Board():
    """
    Contains the board state
    """
    def __init__(self, board_dimensions):
        # board is made of hexagonal hexes and their vertices and edges
        self.hexes = {} # hexcoord , hextileClass
        self.vertices = {} # coord , vertexClass
        self.edges = {} # index, edgeClass

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
        
        for id, edge in new_edges.items():
            for parent in edge.vertex_parents:
                vertices[parent].edge_children.append(id)

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
                new_vertices[vertex].hex_parents.append(coord)
        
        for coord, hextile in sea_hexes.items():
            corners = polygon_corners(self.layout, coord)
            for vertex in corners:
                if vertex in new_vertices:
                    hextile.vertex_children.append(vertex)
                    #new_vertices[vertex].hex_parents.append(coord)
        
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
            added_hexes = [Hex(0, 0, 0)]
            for n in range(2):
                new_land_hexes = {}
                for coord, hextile in land_hexes.items():
                    for direction in range(6):
                        neighbor = hex_neighbor(coord, direction)
                        if neighbor not in added_hexes:
                            added_hexes.append(neighbor) 
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
    
    def choose_starting_builds(self, players, player_order):
        reversed_players = list(reversed(player_order))
        for player_index in player_order:
            _ = self.build_starting_builds(players[player_index])
        
        # track location of second settlement for starting resources
        last_settlement_coords = []
        for player_index in reversed_players:
            settlement_coord = self.build_starting_builds(players[player_index])
            last_settlement_coords.append(settlement_coord)
        
        return last_settlement_coords
    
    def build_starting_builds(self, player):
        # building settlement
        possible_settlment_coords = []
        for coord, vertex in self.vertices.items():
            all_neighbors_unowned = all(self.vertices[neighbor].owner == None for neighbor in vertex.vertex_neighbors)
            if coord not in possible_settlment_coords and vertex.owner == None and all_neighbors_unowned:
                possible_settlment_coords.append(coord)
        settlement_coord = player.choose_action(possible_settlment_coords)
        self.vertices[settlement_coord].owner = player.colour
        self.vertices[settlement_coord].has_settlement = True
        player.owned_settlements.append(settlement_coord)
        print(f"{player.name} ({player.colour}) has built a SETTLEMENET")

        # building adjacent road
        possible_road_edges = []
        for child in self.vertices[settlement_coord].edge_children:
            possible_road_edges.append(child)
        road_edge = player.choose_action(possible_road_edges)
        self.edges[road_edge].owner = player.colour
        self.edges[road_edge].has_road = True
        player.owned_roads.append(road_edge)
        print(f"{player.name} ({player.colour}) has built a ROAD")

        return settlement_coord

    def build_settlement(self, player):
        owned_edges_indexes = player.owned_roads
        possible_settlment_coords = []
        for edge_index in owned_edges_indexes:
            possible_vertex_coords = self.edges[edge_index].vertex_parents
            for coord in possible_vertex_coords:
                vertex = self.vertices[coord]
                all_neighbors_unowned = all(self.vertices[neighbor].owner == None for neighbor in vertex.vertex_neighbors)
                if coord not in possible_settlment_coords and vertex.owner == None and all_neighbors_unowned:
                    possible_settlment_coords.append(coord)
        settlement_coord = player.choose_action(possible_settlment_coords)
        self.vertices[settlement_coord].owner = player.colour
        self.vertices[settlement_coord].has_settlement = True
        player.owned_settlements.append(settlement_coord)
        player.settlements_left -=1
        print(f"{player.name} ({player.colour}) has built a SETTLEMENET")

    def build_road(self, player):
        possible_road_edges = []
        explored_vertex_coords = []
        owned_edges_indexes = player.owned_roads
        for owned_edge_index in owned_edges_indexes:
            vertex_coords = self.edges[owned_edge_index].vertex_parents
            for coord in vertex_coords:
                if coord not in explored_vertex_coords:
                    vertex = self.vertices[coord]
                    explored_vertex_coords.append(coord)
                    edge_indexes = vertex.edge_children
                    for index in edge_indexes:
                        if not self.edges[index].has_road:
                            possible_road_edges.append(index)

        road_edge = player.choose_action(possible_road_edges)
        self.edges[road_edge].owner = player.colour
        self.edges[road_edge].has_road = True
        player.owned_roads.append(road_edge)
        player.roads_left -= 1
        print(f"{player.name} ({player.colour}) has built a ROAD")
    
    def build_city(self, player):
        possible_city_coords = []
        for settlement_coord in player.owned_settlements:
            if not self.vertices[settlement_coord].has_city:
                possible_city_coords.append(settlement_coord)
        
        city_coord = player.choose_action(possible_city_coords)
        self.vertices[city_coord].has_city = True
        self.vertices[city_coord].has_settlement = False
        player.cities_left -= 1
        player.settlements_left += 1
        print(f"{player.name} ({player.colour}) has built a CITY")
    
    def get_longest_road(self, player):
        longest_road_length = 0

        def dfs(vertex, visited_edges):
            nonlocal longest_road_length
            longest_path = 0

            for edge_index in self.vertices[vertex].edge_children:
                edge = self.edges[edge_index]

                if edge.owner == player.colour and edge_index not in visited_edges:
                    visited_edges.add(edge_index)

                    for neighbor_vertex in edge.vertex_parents:
                        if neighbor_vertex != vertex:
                            if self.vertices[neighbor_vertex].owner is None or self.vertices[neighbor_vertex].owner == player.colour:
                                path_length = dfs(neighbor_vertex, visited_edges)
                                longest_path = max(longest_path, 1 + path_length)

                    visited_edges.remove(edge_index)

            longest_road_length = max(longest_road_length, longest_path)
            return longest_path

        visited_edges = set()
        for edge_index in player.owned_roads:
            edge = self.edges[edge_index]

            for vertex in edge.vertex_parents:
                dfs(vertex, visited_edges)

        return longest_road_length