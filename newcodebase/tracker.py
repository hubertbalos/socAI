from typing import Dict
from collections import defaultdict

class Tracker():
    def __init__(self):
        self.winner: str = None
        self.game_length: int = 0
        self.ticks: int = 0

        self.victory_points: Dict[int] = defaultdict(int)
        self.resources_collected: Dict[int] = defaultdict(int)

        # At turn 25
        self.settlements_built: Dict[int] = defaultdict(int)
        self.cities_built: Dict[int] = defaultdict(int)
