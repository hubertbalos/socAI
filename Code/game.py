import numpy as np

class Game():
    """
    Game events are run from within this class
    """
    def __init__(self):
        self.developmentCards = []
        self.resources = {"ORE": 19, "WHEAT": 19, "WOOD": 19, "BRICK": 19, "SHEEP": 19}

        self.ROAD_COST = [("WOOD", 1), ("BRICK", 1)]
        self.SETTLEMENT_COST = [("WOOD", 1), ("BRICK", 1), ("WHEAT", 1), ("SHEEP", 1)]
        self.CITY_COST = [("ORE", 3), ("WHEAT", 2)]
        self.DEVELOPMENT_CARD_COST = [("ORE", 1), ("WHEAT", 1), ("SHEEP", 1)]
    
    def rollDice(self):
        "Returns the sum of two rolled dice"
        die1 = np.random.randint(0, 7)
        die2 = np.random.randint(0, 7)
        result = die1 + die2
        return result
