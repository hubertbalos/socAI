class Player():
    """
    Player for Settlers of Catan
    """
    def __init__(self, playerName, playerColour):
        self.name = playerName
        self.colour = playerColour

        self.victoryPoints = 0
        
        self.resources = {"ORE": 0, "WHEAT": 0, "WOOD": 0, "BRICK": 0, "SHEEP": 0}
        self.settlements = 5
        self.roads = 15
        self.cities = 4

        self.longestRoad = False
        self.largestArmy = False