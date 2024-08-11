import numpy as np
import random
import time
from player import Player, Action
from game import Game
from typing import List

class PlacementState():
    def __init__(self, game, current_player, settlements_placed=0, roads_placed=0):
        self.game = game
        self.current_player = current_player
        self.settlements_placed = settlements_placed
        self.roads_placed = roads_placed
        self.placements = []  # Track placements (settlements and roads)

    def clone(self):
        # Return a deep copy of the state
        return PlacementState(self.game.clone(), self.current_player, self.settlements_placed, self.roads_placed)

    def get_possible_actions(self):
        if self.settlements_placed < 2:
            return self.game.get_possible_settlements(self.current_player, initial=True)
        else:
            last_settlement = self.placements[-2]
            return self.game.get_possible_roads(self.current_player, last_settlement)

    def perform_action(self, action):
        new_state = self.clone()
        new_state.placements.append(action.value)
        if new_state.settlements_placed < 2:
            new_state.settlements_placed += 1
        else:
            new_state.roads_placed += 1
        return new_state

    def evaluate(self):
        # Simulate a full game and return the result
        return self.simulate_full_game()

    def simulate_full_game(self):
        current_game = self.game.clone()
        while not current_game.game_over():
            current_player_colour = current_game.start_turn()
            possible_actions = current_game.get_possible_actions(current_player_colour)
            random_action = random.choice(possible_actions)
            current_game.decide(current_player_colour, [random_action])
            current_game.finish_turn()
        winner = max(current_game.players.values(), key=lambda p: p.victory_points)
        return 1 if winner.colour == self.current_player else -1

class Node():
    def __init__(self, state, parent=None, action=None):
        self.state: Game = state
        self.parent: Node = parent
        self.children: List[Node] = []
        self.action: Action = action
        self.untried_actions: List[Action] = self.get_untried_actions()
        self.visits: int = 0
        self.value: int = 0

    def get_untried_actions(self):
        current_colour = self.state.player_order[self.state.current_player]
        return self.state.get_possible_actions(current_colour)
    
    def is_fully_expanded(self):
        "Are all possible children initiated?"
        return len(self.untried_actions) == 0
    
    def is_terminal(self):
        return self.state.is_game_over()

    def best_child(self, exploration_param=1.4):
        choices_weights = [
            (child.value / child.visits) + exploration_param * np.sqrt(np.log(self.visits) / child.visits)
            for child in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def most_visited_child(self):
        return max(self.children, key=lambda child: child.visits)

    def add_child(self, child_state, action):
        child_node = Node(child_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node

class MCTSPlayer(Player):
    """
    Monte carlo tree search player 
    """
    type = "MCTSPlayer"

    def __init__(self, Colour, Iterations: int=1000):
        super().__init__(Colour)
        self.iterations = Iterations

    def choose_action(self, possible_actions, game: Game=None):
        # If only one action then just return it
        if len(possible_actions) == 1:
            return possible_actions[0]
        # If game was not passed play like RandomPlayer
        if not game:
            return random.choice(possible_actions)
        
        # MCTS
        start = time.time()

        root = Node(game)
        for _ in range(self.iterations):
            node = self.select(root)
            if not node.is_terminal():
                node = self.expand(node)
            reward = self.simulate(node.state)
            self.backpropagate(node, reward)

        print(f"MCTS completed in {time.time() - start}")
        return root.best_child(exploration_param=0).action

    def select(self, node: Node):
        "Select leaf of tree"
        while not node.is_terminal():
            if not node.is_fully_expanded():
                return node
            else:
                node = node.best_child()
        return node

    def expand(self, node: Node):
        "Choose an untried action from the node and create child"
        action = node.untried_actions.pop()
        game_clone = node.state.clone()
        new_state = game_clone.step(action)
        return node.add_child(new_state, action)

    def simulate(self, state: Game):
        "Rollout the rest of the game from this state and get result"
        return state.evaluate()

    def backpropagate(self, node: Node, reward):
        "Move up the tree and increment vists and adjust reward"
        node.visits += 1
        node.value += reward
        if node.parent:
            self.backpropagate(node.parent, reward)