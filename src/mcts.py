import numpy as np
import random
import time
from player import Player, Action
from game import Game
from typing import List
from copy import deepcopy
from statistics import median
from concurrent.futures import ProcessPoolExecutor, as_completed

USE_ENSEMBLE = False
EXPLORATION_PARAM = 0.75

class Node():
    def __init__(self, state, parent=None, action=None, pruning=None):
        self.state: Game = state
        self.parent: Node = parent
        self.pruning: bool = pruning
        self.children: List[Node] = []
        self.action: Action = action
        self.untried_actions: List[Action] = self.get_untried_actions()
        self.visits: int = 0
        self.value: int = 0

    def get_untried_actions(self):
        current_colour = self.state.player_order[self.state.current_player]
        possible_actions = self.state.get_possible_actions(current_colour)
        if self.pruning:
            if self.parent is None and (self.state.turn % 2) == 1:
                possible_actions = self.placement_prune_actions(possible_actions)
        return possible_actions
    
    def is_fully_expanded(self):
        "Are all possible children initiated?"
        return len(self.untried_actions) == 0
    
    def is_terminal(self):
        return self.state.game_over()

    def best_child(self, exploration_param=EXPLORATION_PARAM):
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
    
    def placement_prune_actions(self, possible_actions: List[Action]):
        PIP_NUMBER_DICT = {2:1, 3:2, 4:3, 5:4, 6:5, 8:5, 9:4, 10:3, 11:2, 12:1}

        pip_dict: List[int] = {}
        for action in possible_actions:
            point = action.value
            vertex = self.state.board.vertices[point]

            total_pips: int = 0
            for coord in vertex.hex_neighbors:
                hextile = self.state.board.hexes[coord]
                if hextile.value:
                    total_pips += PIP_NUMBER_DICT[hextile.value]
            pip_dict[point] = total_pips
        
        med = median(pip_dict.values())
        pruned_actions = [action for action in possible_actions if pip_dict[action.value] > med]
        return pruned_actions

WEIGHTS_BY_ACTION_TYPE = {
    "BUILD_CITY": 10000,
    "BUILD_SETTLEMENT": 1000,
    "BUY_DEVCARD": 100,
}

class MCTSPlayer(Player):
    """
    Monte carlo tree search player 
    """
    type = "MCTSPlayer"

    def __init__(self, Colour, Iterations: int=1000, Pruning: bool=True, Reward: bool=True):
        super().__init__(Colour)
        self.iterations = Iterations
        self.colour = Colour
        self.pruning = Pruning
        self.reward = Reward
        self.max_workers = 10

    def choose_action(self, possible_actions, game: Game=None):
        # If only one action then just return it
        if len(possible_actions) == 1:
            return possible_actions[0]
        # If game was not passed play like RandomPlayer
        # if not game:
        #     return random.choice(possible_actions)
        # If game was not passed play like WeightedPlayer
        if not game:
            bloated_actions = []
            for action in possible_actions:
                weight = WEIGHTS_BY_ACTION_TYPE.get(action.type, 1)
                bloated_actions.extend([action] * weight)
            return random.choice(bloated_actions)
        
        # MCTS
        start = time.time()

        root = Node(game, pruning=self.pruning)
        if not USE_ENSEMBLE:
            for _ in range(self.iterations):
                node = self.select(root)
                if not node.is_terminal():
                    node = self.expand(node)
                reward = self.simulate(deepcopy(node.state))
                self.backpropagate(node, reward)
        else:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self.run_mcts, deepcopy(root)) for _ in range(self.max_workers)]
                for future in as_completed(futures):
                    result_node = future.result()
                    if not root.children:
                        root = result_node
                    else:
                        self.merge_trees(root, result_node)

        print(f"MCTS completed in {time.time() - start:.2f}")
        return root.best_child(exploration_param=0).action
    
    def run_mcts(self, root):
        for _ in range(self.iterations):
            node = self.select(root)
            if not node.is_terminal():
                node = self.expand(node)
            reward = self.simulate(deepcopy(node.state))
            self.backpropagate(node, reward)
        return root
    
    def merge_trees(self, root: Node, other_root: Node):
        for other_child in other_root.children:
            match = False
            for root_child in root.children:
                if root_child.action == other_child.action:
                    root_child.visits += other_child.visits
                    root_child.value += other_child.value
                    match = True
                    break
            if not match:
                root.children.append(other_child)

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
        new_state = deepcopy(node.state)
        # ------------ game settings --------------
        new_state.gamelog = False
        new_state.debug = False
        new_state.savegame = False
        new_state.reward = self.reward
        new_state.turn_limit = 1000
        # -----------------------------------------
        current_colour = new_state.player_order[new_state.current_player]
        new_state.step(current_colour, action)
        return node.add_child(new_state, action)

    def simulate(self, state: Game):
        "Rollout the rest of the game from this state and get result"
        return state.evaluate(self.colour)

    def backpropagate(self, node: Node, reward):
        "Move up the tree and increment vists and adjust reward"
        node.visits += 1
        node.value += reward
        if node.parent:
            self.backpropagate(node.parent, reward)