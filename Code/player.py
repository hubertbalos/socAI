import random

class Player():
    """
    Player for Settlers of Catan
    """
    def __init__(self, player_name, player_colour):
        self.name = player_name
        self.colour = player_colour

        self.victory_points = 2 # player starts with 2 settlements
        
        self.resources = {"ORE": 0, "WHEAT": 0, "WOOD": 0, "BRICK": 0, "SHEEP": 0}
        self.development_cards = {"KNIGHT": 0, "YEAR_OF_PLENTY": 0, "ROAD_BUILDING": 0, "MONOPOLY": 0, "VICTORY_POINT": 0}
        self.owned_roads = [] # list of edge indexes
        self.owned_settlements = [] # list of vertex coords
        self.settlements_left = 3 # 5 but setup settlements already subtracted
        self.roads_left = 13 # 15 but setup roads already subtracted
        self.cities_left = 4

        self.knights_played = 0
        self.longest_road_length = 1

        self.longest_road = False
        self.largest_army = False
    
    def get_victory_points(self):
        cities = (4 - self.cities_left) * 2
        settlements = (5 - self.settlements_left)
        dev_cards = self.development_cards["VICTORY_POINT"]

        road = 0
        if self.longest_road:
            road = 2
        army = 0
        if self.largest_army:
            army = 2

        vps = cities + settlements + dev_cards + road + army
        self.victory_points = vps
        return vps

class RandomPlayer(Player):
    """
    Player that makes random choices
    """
    def choose_action(self, possible_actions):
        random_action = random.choice(possible_actions)
        return random_action