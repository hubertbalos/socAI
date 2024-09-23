import random
from typing import List
from collections import namedtuple

from hexlib import Point

Action = namedtuple("Action", ["type", "value"])

class Player():
    """
    Player class skeleton
    """
    def __init__(self, Colour: str):
        self.colour: str = Colour

        self.victory_points: int = 0 
        self.owned_edges: List[int] = []
        self.owned_vertices: List[Point] = []
        
        self.trading_cost = {"WOOD": 4, "BRICK": 4, "SHEEP": 4, "WHEAT": 4, "ORE": 4}
        self.resources = {"WOOD": 0, "BRICK": 0, "SHEEP": 0, "WHEAT": 0, "ORE": 0}
        self.development_cards = {
            "KNIGHT": 0, "YEAR_OF_PLENTY": 0, "ROAD_BUILDING": 0, "MONOPOLY": 0, "VICTORY_POINT": 0}

        self.roads_left: int = 15 
        self.settlements_left: int = 5
        self.cities_left: int = 4

        self.knights_played: int = 0
        self.longest_road_length: int = 0
    
    def choose_action(self, possible_actions: List[Action]) -> Action:
        raise NotImplementedError("This method should be overridden in subclasses")

class RandomPlayer(Player):
    """
    Player that makes random choices
    """
    type = "RandomPlayer"

    def choose_action(self, possible_actions: List[Action]) -> Action:
        return random.choice(possible_actions)

WEIGHTS_BY_ACTION_TYPE = {
    "BUILD_CITY": 10000,
    "BUILD_SETTLEMENT": 1000,
    "BUY_DEVCARD": 100,
}
class WeightedRandomPlayer(Player):
    """
    Player that decides at random, but skews distribution
    to actions that are likely better (cities > settlements > dev cards).
    """
    type = "WeightedRandomPlayer"

    def choose_action(self, possible_actions: List[Action]) -> Action:
        bloated_actions = []
        for action in possible_actions:
            weight = WEIGHTS_BY_ACTION_TYPE.get(action.type, 1)
            bloated_actions.extend([action] * weight)
        return random.choice(bloated_actions)