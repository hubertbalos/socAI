import random

class Player():
    """
    Player for Settlers of Catan
    """
    def __init__(self, player_name, player_colour):
        self.name = player_name
        self.colour = player_colour

        self.victory_points = 0
        
        self.resources = {"ORE": 0, "WHEAT": 0, "WOOD": 0, "BRICK": 0, "SHEEP": 0}
        self.development_cards = {"KNIGHT": 0, "YEAR_OF_PLENTY": 0, "ROAD_BUILDING": 0, "MONOPOLY": 0, "VICTORY_POINTS": 0}
        self.settlements_left = 5
        self.roads_left = 15
        self.cities_left = 4

        self.longest_road = False
        self.largest_army = False

class RandomPlayer(Player):
    """
    Player that makes random choices
    """
    def choose_action(self, possible_actions):
        random_action = random.choice(possible_actions)
        return random_action