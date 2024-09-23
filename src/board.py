from typing import Tuple, Set

from hexlib import Point
from map import CatanMap
from player import Player
from map import Edge

class Board(CatanMap):
    def __init__(self, windowSize: Tuple[int, int], Game):
        super().__init__(mapDimensions=windowSize)
        self.game = Game

    def build_road(self, colour: str, edge_id: int) -> str:
        self.edges[edge_id].has_road = True
        self.edges[edge_id].owner_colour = colour

        player: Player = self.game.players[colour]
        player.owned_edges.append(edge_id)
        player.roads_left -= 1

        player.longest_road_length = self.get_longest_road(colour)
        roads_built = 15 - player.roads_left
        if roads_built >= 5:
            if self.game.longest_road_colour:
                enemy = self.game.players[self.game.longest_road_colour]
                longest_road = enemy.longest_road_length
                if  player.longest_road_length > longest_road:
                    self.game.longest_road_colour = colour
                    
                    player.victory_points += 2
                    enemy.victory_points -= 2
            else:
                self.game.longest_road_colour = colour
                player.victory_points += 2

        return f"{colour} has built a ROAD at {edge_id}"
    
    def build_settlement(self, colour: str, coord: Point) -> str:
        player: Player = self.game.players[colour]

        self.vertices[coord].building = "SETTLEMENT"
        self.vertices[coord].owner_colour = colour
        port_type = self.vertices[coord].port_type
        if port_type:
            if port_type == "3:1":
                for cost in player.trading_cost.values():
                    if cost == 4:
                        cost = 3
            else:
                player.trading_cost[port_type] = 2

        player.owned_vertices.append(coord)
        player.settlements_left -= 1
        player.victory_points += 1

        return f"{colour} has built a SETTLEMENT at {coord}"
    
    def build_city(self, colour: str, coord: Point) -> str:
        self.vertices[coord].building = "CITY"

        player: Player = self.game.players[colour]
        player.cities_left -= 1
        player.victory_points += 1

        return f"{colour} has built a CITY at {coord}"
    
    def get_longest_road(self, colour: str) -> int:
        player: Player = self.game.players[colour]
        longest_road_length: int = 0

        def dfs(vertex: Point, visited_edges: Set[int]) -> int:
            nonlocal longest_road_length
            longest_path: int = 0

            for edge_index in self.vertices[vertex].edge_neighbors:
                edge: Edge = self.edges[edge_index]

                if edge.owner_colour == colour and edge_index not in visited_edges:
                    visited_edges.add(edge_index)

                    for neighbor_vertex in edge.vertex_neighbors:
                        if neighbor_vertex != vertex:
                            owner_colour = self.vertices[neighbor_vertex].owner_colour
                            if owner_colour is None or owner_colour == colour:
                                path_length: int = dfs(neighbor_vertex, visited_edges)
                                longest_path: int = max(longest_path, 1 + path_length)

                    visited_edges.remove(edge_index)

            longest_road_length = max(longest_road_length, longest_path)
            return longest_path

        visited_edges: Set[int] = set()
        for edge_index in player.owned_edges:
            edge: Edge = self.edges[edge_index]

            for vertex in edge.vertex_neighbors:
                dfs(vertex, visited_edges)

        return longest_road_length