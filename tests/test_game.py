import unittest
from unittest.mock import MagicMock

from src.game import Game
from src.player import Player
from src.board import Board
from src.tracker import Tracker
from src.hexlib import Point

class TestGame(unittest.TestCase):
    
    def setUp(self):
        """Set up a default game with mock players for testing"""
        self.window_size = (800, 600)
        self.players = [
            Player("RED", "TestPlayer"),
            Player("WHITE", "TestPlayer"),
            Player("ORANGE", "TestPlayer"),
            Player("BLUE", "TestPlayer")
        ]
        self.gamelog = False
        self._debug = False
        self.savegame = False
        self.game = Game(self.window_size, self.players, self.gamelog, self._debug, self.savegame)

    def test_initialise_players(self):
        """Test player initialization and order randomization"""
        self.game.initialise_players(self.players)
        self.assertEqual(len(self.game.players), 4)
        self.assertEqual(len(self.game.player_order), 4)
        self.assertTrue(set(self.game.players.keys()).issubset({"RED", "BLUE", "WHITE", "ORANGE"}))

    def test_game_over_win(self):
        """Test game_over method when a player wins by reaching 10 victory points"""
        player = self.game.players["RED"]
        player.victory_points = 10
        self.assertTrue(self.game.game_over())
        self.assertEqual(self.game.tracker.winner, "RED")

    def test_game_over_turn_limit(self):
        """Test game_over when turn limit is reached"""
        self.game.turn = 1000
        self.assertTrue(self.game.game_over())
    
    def test_robber_movement(self):
        """Test moving the robber and robbing a player"""
        self.game.board.robber_coord = Point(0, 0)  # Mock initial robber location
        self.game.board.hexes[Point(1, 1)] = MagicMock()  # Mock hex tile
        log = self.game.move_robber_and_rob("RED", (Point(1, 1), "BLUE"))
        self.assertIn("RED has moved ROBBER", log)
        self.assertIn("RED stole", log)

    def test_buy_devcard(self):
        """Test buying a development card and updating resources"""
        player = self.game.players["RED"]
        player.resources = {"WHEAT": 1, "ORE": 1, "SHEEP": 1}
        log = self.game.buy_devcard("RED")
        self.assertIn("RED has bought a DEVCARD", log)
        self.assertEqual(player.resources["WHEAT"], 0)
        self.assertEqual(player.resources["ORE"], 0)
        self.assertEqual(player.resources["SHEEP"], 0)

    def test_roll_dice(self):
        """Test rolling dice returns a tuple of values between 1 and 6"""
        roll = self.game.roll_dice()
        self.assertIsInstance(roll, tuple)
        self.assertEqual(len(roll), 2)
        self.assertTrue(1 <= roll[0] <= 6)
        self.assertTrue(1 <= roll[1] <= 6)
    
    def test_step_end_turn(self):
        """Test the END_TURN action"""
        current_turn = self.game.turn
        current_player = self.game.current_player
        self.game.step("RED", MagicMock(type="END_TURN", value=None))
        self.assertEqual(self.game.turn, current_turn + 1)
        self.assertNotEqual(self.game.current_player, current_player)
    
    def test_distribute_resources(self):
        """Test resource distribution after a valid roll"""
        self.game.board.hexes[Point(1, 1)] = MagicMock()
        self.game.board.vertices[Point(0, 0)] = MagicMock(owner_colour="RED", building="SETTLEMENT")
        log = self.game.distribute_resources(total_roll=8)
        self.assertIn("RED has received", log)

    def test_trade_with_bank(self):
        """Test trading with the bank"""
        player = self.game.players["RED"]
        player.resources = {"WOOD": 4}
        log = self.game.trade_with_bank("RED", ("WOOD", 4, "BRICK"))
        self.assertIn("RED traded 4 WOOD for 1 BRICK", log)
        self.assertEqual(player.resources["WOOD"], 0)
        self.assertEqual(player.resources["BRICK"], 1)

    def test_save_and_load_game(self):
        """Test saving and loading a game"""
        self.game.save_game('test_save.pkl')
        loaded_game = Game.load_game('test_save.pkl')
        self.assertIsInstance(loaded_game, Game)

    def test_initial_settlement_phase(self):
        """Test the initial settlement phase logic"""
        self.game.initial_settlement_phase()
        self.assertEqual(self.game.turn, 3)  # Ensure both forward and backward phases completed

    def tearDown(self):
        """Clean up files after tests."""
        import os
        if os.path.exists('test_save.pkl'):
            os.remove('test_save.pkl')

if __name__ == '__main__':
    unittest.main()