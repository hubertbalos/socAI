import numpy as np
from board import Board
from player import *

class Game():
    """
    Game events are run from within this class
    """
    def __init__(self, board_dimensions):
        self.board = Board(board_dimensions)

        self.development_cards = []
        self.resources = {"ORE": 19, "WHEAT": 19, "WOOD": 19, "BRICK": 19, "SHEEP": 19}

        self.ROAD_COST = [("WOOD", 1), ("BRICK", 1)]
        self.SETTLEMENT_COST = [("WOOD", 1), ("BRICK", 1), ("WHEAT", 1), ("SHEEP", 1)]
        self.CITY_COST = [("ORE", 3), ("WHEAT", 2)]
        self.DEVELOPMENT_CARD_COST = [("ORE", 1), ("WHEAT", 1), ("SHEEP", 1)]

        self.players = []
        self.currentPlayer = 0

        self.gameloop()

    def gameloop(self):
        self.initialise_players()
        self.select_starting_settlements()

    def initialise_players(self):
        colours = ["RED", "BLUE", "ORANGE", "WHITE"]
        number_of_players = 4
        for i in range(number_of_players):
            new_player = RandomPlayer("RandomPlayer" + str(i), colours[i])
            self.players.append(new_player)
        
        players = []
        for player in self.players:
            players.append(player.name)
        
        print(f"Players (Total: {len(players)}): {players}")
    
    def select_starting_settlements(self):
        for player in self.players:
            self.build_settlement(player)
            self.build_road(player)
        
        # players_reverse = self.players.reverse()
        # for player in players_reverse:
        #     self.build_settlement(player)
    
    def build_settlement(self, player):
        action_space = []
        for coord, vertex in self.board.vertices.items():
            if coord not in action_space and vertex.owner == None and all(self.board.vertices[neighbor].owner == None for neighbor in vertex.vertex_neighbors):
                action_space.append(coord)
        
        action = player.choose_action(action_space)
        print(action)
        self.board.vertices[action].owner = player.colour
        self.board.vertices[action].has_settlement = True

    def build_road(self, player):
        action_space = []

        
    def next_player(self):
        next_player =(self.currentPlayer + 1) % len(self.players)
        self.currentPlayer = next_player
    
    def roll_dice(self):
        "Returns the sum of two rolled dice"
        die_1 = np.random.randint(1, 7)
        die_2 = np.random.randint(1, 7)
        result = die_1 + die_2
        return result
    
    def get_board(self):
        return self.board
    
    """
    TURN START
    - you can play a dev card at any point in turn
    - trade (1) and build phase (3) can be combined
    1. Roll Dice
        -
    2. Trade
        - 
    3. Build or buy a dev card
    """
# -- TESTING -- 
# print("Running test for game.py")
# game = Game((750, 910))
