import numpy as np
from board import Board
from player import *

class Game():
    """
    Game events are run from within this class
    """
    def __init__(self, board_dimensions):
        self.board = Board(board_dimensions)

        self.development_cards = {"KNIGHT": 14, "YEAR_OF_PLENTY": 2, "ROAD_BUILDING": 2, "MONOPOLY": 2, "VICTORY_POINTS": 5}
        self.resources = {"ORE": 19, "WHEAT": 19, "WOOD": 19, "BRICK": 19, "SHEEP": 19}

        self.ROAD_COST = [("WOOD", 1), ("BRICK", 1)]
        self.SETTLEMENT_COST = [("WOOD", 1), ("BRICK", 1), ("WHEAT", 1), ("SHEEP", 1)]
        self.CITY_COST = [("ORE", 3), ("WHEAT", 2)]
        self.DEVELOPMENT_CARD_COST = [("ORE", 1), ("WHEAT", 1), ("SHEEP", 1)]

        self.players = []
        self.current_player_index = 0

        self.turn = 0

        self.gameloop()

    def gameloop(self):
        self.initialise_players()

        print("-" * 55)
        print("Players choosing starting builds\n")
        self.board.choose_starting_builds(self.players)

        while self.turn < 50:
            print("-" * 55)
            current_player = self.players[self.current_player_index]
            dice_roll = self.roll_dice()
            print(f"{current_player.name} ({current_player.colour}) has rolled a {dice_roll}\n")
            if dice_roll == 7:
                self.move_robber_and_rob(self.players)
            self.distribute_resources(dice_roll)

            # choose action

            self.turn += 1
            self.next_player()
        
        print("*** GAME FINISHED ***")

    def initialise_players(self):
        colours = np.random.permutation(["RED", "BLUE", "ORANGE", "WHITE"])
        number_of_players = 4
        for i in range(number_of_players):
            new_player = RandomPlayer("RandomPlayer" + str(i), colours[i])
            self.players.append(new_player)
        
        players = []
        for player in self.players:
            players.append(player.name)
        
        print(f"Total Players: {len(players)}")
        for player in self.players:
            print(f"{player.name} ({player.colour})")
        
    def next_player(self):
        next_player = (self.current_player_index + 1) % len(self.players)
        self.current_player_index = next_player
    
    def distribute_resources(self, dice_roll):
        rolled_hexes = []
        for coord, hextile in self.board.hexes.items():
            if hextile.value == dice_roll:
                rolled_hexes.append(coord)

        for hexcoord in rolled_hexes:
            hextile = self.board.hexes[hexcoord]
            resource = hextile.resource

            recievers = []
            for coord in hextile.vertex_children:
                vertex = self.board.vertices[coord]
                owner = vertex.owner
                if owner != None:
                    recievers.append(owner)
            
            if len(recievers) > self.resources[resource]:
                print(f"Not enough {resource} to distribute")
            else:
                for reciever in recievers:
                    for player in self.players:
                        if reciever == player.colour:
                            self.resources[resource] -= 1
                            player.resources[resource] += 1
                            print(f"{player.name} ({player.colour}) has recieved 1 {resource}")
            
    def move_robber_and_rob(self, player):
        None
    
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
