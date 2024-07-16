class player():
    def __init__(self, playerName, playerColour):
        self.name = playerName
        self.colour = playerColour

        # --
        self.victoryPoints = 0
        
        # --
        self.settlements = 0
        self.roads = 0
        self.cities = 0
        self.resources = {'ORE': 0, 'WHEAT': 0, }
