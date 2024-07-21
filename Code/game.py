import numpy as np
from board import Board
from player import *
import random

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

        self.players = {} # colour , PlayerClass
        self.player_order = [] # indexes
        self.current_player_index = 0

        self.turn = 0
        self.max_turns = 10

        self.highest_VPs = 0
        self.current_leader = None

        self.gameloop()

    def gameloop(self):
        self.initialise_players()

        print("-" * 55)
        print("Players choosing starting builds\n")
        start_settlement_coords = self.board.choose_starting_builds(self.players, self.player_order)
        self.give_starting_resources(start_settlement_coords)

        print("\n Bank resources")
        print(self.resources)
        print("\n End phase player resources")
        for player in self.players.values():
            print(player.resources)

        while self.turn < self.max_turns or self.highest_VPs >= 10:
            print("-" * 55)
            current_player = self.players[self.player_order[self.current_player_index]]
            dice_roll = self.roll_dice()
            print(f"{current_player.name} ({current_player.colour}) has rolled a {dice_roll}\n")
            if dice_roll == 7:
                self.move_robber_and_rob(current_player)
            self.distribute_resources(dice_roll)

            # choose action

            self.turn += 1
            self.next_player()

            print("\n Bank resources")
            print(self.resources)
            print("\n End turn player resources")
            for player in self.players.values():
                print(player.resources)
            
        print("*** GAME FINISHED ***")
    
    def give_starting_resources(self, start_settlement_coords):
        for coord in start_settlement_coords:
            owner = self.board.vertices[coord].owner
            player = self.players[owner]
            hexcoords = self.board.vertices[coord].hex_parents
            gained_resources = []
            for hexcoord in hexcoords:
                hextile = self.board.hexes[hexcoord]
                if hextile.resource != "DESERT":
                    gained_resources.append(str(hextile.resource))
                    self.resources[hextile.resource] -= 1
                    player.resources[hextile.resource] += 1
            print(f"\n {player.name} ({player.colour}) has received {gained_resources}")

    
    def perform_actions(self, current_player):
        possible_actions = ["END_TURN"] #  "BUY_DEVELOPMENT_CARD", "PLAY_DEVELOPMENT_CARD"
        if self.can_build_settlement(current_player):
            possible_actions.append("BUILD_ROAD")
        if all(current_player.resources[resource] >= cost for (resource, cost) in self.SETTLEMENT_COST):
            possible_actions.append("BUILD_SETTLEMENT")
        if all(current_player.resources[resource] >= cost for (resource, cost) in self.CITY_COST):
            possible_actions.append("BUILD_CITY")
        
        action = current_player.choose_action(possible_actions)
        if action == "END_TURN":
            return # do nothing
        elif action == "BUILD_ROAD":
            self.board.build_road(current_player)
        elif action == "BUILD_SETTLMENT":
            self.board.build_settlement(current_player)
        elif action == "BUILD_CITY":
            self.board.build_city(current_player)
    
    def can_build_settlement(self, current_player):
        # does the player have enough resources?
        if all(current_player.resources[resource] < cost for (resource, cost) in self.ROAD_COST):
            return False
        # does the player have any settlements in hand?
        if current_player.settlements_left == 0:
            return False
        # is there a valid place to build the settlement?


    def initialise_players(self):
        colours = np.random.permutation(["RED", "BLUE", "ORANGE", "WHITE"])
        number_of_players = 4
        for i in range(number_of_players):
            new_player = RandomPlayer("RandomPlayer" + str(i), colours[i])
            self.players[colours[i]] = new_player
            self.player_order.append(colours[i])
        
        players = []
        for player in self.players.values():
            players.append(player.name)
        
        print(f"Total Players: {len(players)}")
        for player in self.players.values():
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
                    if vertex.has_settlement:
                        recievers.append((owner, 1))
                    elif vertex.has_city:
                        recievers.append((owner, 2))
                    else:
                        raise Exception("Invalid bool for vertex state")
                    
            needed_resources = 0
            for _ , gain in recievers:
                needed_resources += gain
            if needed_resources > self.resources[resource]:
                print(f"Not enough {resource} to distribute")
            else:
                for reciever, gain in recievers:
                    self.resources[resource] -= gain
                    player = self.players[reciever]
                    player.resources[resource] += gain
                    print(f"{player.name} ({player.colour}) has received {gain} {resource}")
            
    def move_robber_and_rob(self, player):
        possible_robber_coords = []
        for coord, hextile in self.board.hexes.items():
            if hextile.resource != "SEA":
                if hextile.has_robber:
                    self.board.hexes[coord].has_robber = False
                else:
                    possible_robber_coords.append(coord)
        robber_coord = player.choose_action(possible_robber_coords)
        self.board.hexes[robber_coord].has_robber = True
        print(f"{player.name} ({player.colour}) has moved the ROBBER")

        possible_players_to_rob = []
        vertex_children = self.board.hexes[robber_coord].vertex_children
        for coord in vertex_children:
            vertex = self.board.vertices[coord]
            if vertex.owner != player.colour and vertex.owner != None:
                if self.player_has_resources(vertex.owner):
                    possible_players_to_rob.append(vertex.owner)
        
        if possible_players_to_rob:
            player_to_rob_colour = player.choose_action(possible_players_to_rob)
            player_to_rob = self.players[player_to_rob_colour]
            self.steal_random_resource(player, player_to_rob)
        else:
            print(f"No valid players to rob")
         
    def player_has_resources(self, player):
        player_resource_values = self.players[player].resources.values()
        net = 0
        for value in player_resource_values:
            net += value
        if net > 0:
            return True
        else:
            return False
    
    def steal_random_resource(self, robber, player_to_rob):
        resource_names = list(player_to_rob.resources.keys())
        resource_counts = list(player_to_rob.resources.values())
        selected_resource = random.choices(resource_names, weights=resource_counts, k=1)[0]

        robber.resources[selected_resource] += 1
        player_to_rob.resources[selected_resource] -= 1
        print(f"{robber.name} ({robber.colour}) has stolen 1 {selected_resource} from {player_to_rob.name} ({(player_to_rob.colour)})")

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
