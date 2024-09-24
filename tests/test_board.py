import unittest
from unittest.mock import MagicMock

from src.board import Board
from src.map import CatanMap, Vertex, Edge
from src.player import Player
from src.hexlib import Point, Hex

class TestBoard(unittest.TestCase):

    def setUp(self):
        """Set up the Board with mock Game and Players for testing"""
        self.window_size = (800, 600)
        self.mock_game = MagicMock()
        self.mock_game.longest_road_colour = None
        self.mock_game.players = {
            "RED": Player("RED", "TestPlayer"),
            "BLUE": Player("BLUE", "TestPlayer"),
        }
        self.board = Board(self.window_size, self.mock_game)

    def test_build_road(self):
        """Test building a road and updating the player's state"""
        self.board.edges[0] = Edge(vertex_neighbors=[Point(0, 0), Point(1, 1)])

        log = self.board.build_road("RED", 0)
        self.assertIn("RED has built a ROAD", log)
        self.assertTrue(self.board.edges[0].has_road)
        self.assertEqual(self.board.edges[0].owner_colour, "RED")

        player = self.mock_game.players["RED"]
        self.assertIn(0, player.owned_edges)
        self.assertEqual(player.roads_left, 14)

    def test_build_settlement(self):
        """Test building a settlement and updating the player's state"""
        coord = Point(0, 0)
        self.board.vertices[coord] = Vertex()

        log = self.board.build_settlement("RED", coord)
        self.assertIn("RED has built a SETTLEMENT", log)
        self.assertEqual(self.board.vertices[coord].owner_colour, "RED")
        self.assertEqual(self.board.vertices[coord].building, "SETTLEMENT")

        player = self.mock_game.players["RED"]
        self.assertIn(coord, player.owned_vertices)
        self.assertEqual(player.settlements_left, 4)
        self.assertEqual(player.victory_points, 1)

    def test_build_city(self):
        """Test building a city and updating the player's state"""
        coord = Point(0, 0)
        self.board.vertices[coord] = Vertex(owner_colour="RED", building="SETTLEMENT")

        log = self.board.build_city("RED", coord)
        self.assertIn("RED has built a CITY", log)
        self.assertEqual(self.board.vertices[coord].building, "CITY")

        player = self.mock_game.players["RED"]
        self.assertEqual(player.cities_left, 3)
        self.assertEqual(player.victory_points, 2)

    def test_get_longest_road(self):
        """Test calculating the longest road for a player"""
        player = self.mock_game.players["RED"]
        # Mock road network for the player
        self.board.vertices[Point(0, 0)] = Vertex(edge_neighbors=[0, 1])
        self.board.vertices[Point(1, 1)] = Vertex(edge_neighbors=[0, 2])
        self.board.vertices[Point(2, 2)] = Vertex(edge_neighbors=[1, 3])
        self.board.edges[0] = Edge(vertex_neighbors=[Point(0, 0), Point(1, 1)], owner_colour="RED", has_road=True)
        self.board.edges[1] = Edge(vertex_neighbors=[Point(1, 1), Point(2, 2)], owner_colour="RED", has_road=True)
        self.board.edges[2] = Edge(vertex_neighbors=[Point(2, 2), Point(3, 3)], owner_colour="RED", has_road=True)

        player.owned_edges = [0, 1, 2]
        longest_road = self.board.get_longest_road("RED")
        self.assertEqual(longest_road, 3)


class TestCatanMap(unittest.TestCase):

    def setUp(self):
        """Set up a default CatanMap for testing."""
        self.map_dimensions = (800, 600)
        self.catan_map = CatanMap(mapDimensions=self.map_dimensions)

    def test_generate_land_hexes(self):
        """Test generating land hexes and validate resources/values."""
        land_hexes = self.catan_map.generate_land_hexes()
        self.assertGreater(len(land_hexes), 0)
        self.assertTrue(any(hex.resource for hex in land_hexes.values()))
        self.assertTrue(any(hex.value is not None for hex in land_hexes.values() if hex.resource != "DESERT"))

    def test_generate_sea_hexes(self):
        """Test generating sea hexes surrounding land hexes."""
        land_hexes = self.catan_map.generate_land_hexes()
        sea_hexes = self.catan_map.generate_sea_hexes(land_hexes)
        self.assertGreater(len(sea_hexes), 0)
        self.assertTrue(all(hextile.resource == "SEA" for hextile in sea_hexes.values()))

    def test_generate_vertices(self):
        """Test generating vertices for land and sea hexes."""
        land_hexes = self.catan_map.generate_land_hexes()
        sea_hexes = self.catan_map.generate_sea_hexes(land_hexes)
        vertices = self.catan_map.generate_vertices(land_hexes, sea_hexes)
        self.assertGreater(len(vertices), 0)
        for hextile in land_hexes.values():
            self.assertTrue(hextile.vertex_neighbors)

    def test_generate_edges(self):
        """Test generating edges based on vertices."""
        land_hexes = self.catan_map.generate_land_hexes()
        sea_hexes = self.catan_map.generate_sea_hexes(land_hexes)
        vertices = self.catan_map.generate_vertices(land_hexes, sea_hexes)
        edges = self.catan_map.generate_edges(vertices)
        self.assertGreater(len(edges), 0)
        for vertex in vertices.values():
            self.assertTrue(vertex.edge_neighbors)

    def test_assign_ports(self):
        """Test assigning ports to random sea hexes."""
        land_hexes = self.catan_map.generate_land_hexes()
        sea_hexes = self.catan_map.generate_sea_hexes(land_hexes)
        vertices = self.catan_map.generate_vertices(land_hexes, sea_hexes)
        self.catan_map.assign_ports(sea_hexes, vertices)
        ports = [hex for hex in sea_hexes.values() if hex.port_type]
        self.assertEqual(len(ports), 9)

if __name__ == '__main__':
    unittest.main()
