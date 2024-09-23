from board import Board
from typing import Tuple, Dict, List, Set
from player import Player, Action
from collections import defaultdict
from map import Vertex, Hextile
import random
from hexlib import Point, Hex
from itertools import combinations
import pickle
from tracker import Tracker

class Game():
    def __init__(self, windowSize: Tuple[int, int], players: List[Player]):
        self.gamelog: bool = False
        self.debug: bool = False
        self.savegame: bool = False
        self.reward: bool = False
        self.turn_limit: int = 20
        self.turn: int = 1

        self.board = Board(windowSize, self)
        self.starting_settlement_phase: bool = True
        self.last_settlement_coord: Point = None

        self.robber_active: bool = False

        self.players: Dict[str, Player] = {}
        self.player_order: List[str] = []
        self.current_player: int = 0

        self.bank_resources = {"WOOD": 19, "BRICK": 19, "SHEEP": 19, "WHEAT": 19, "ORE": 19}
        self.bank_devcards = {
            "KNIGHT": 14, "YEAR_OF_PLENTY": 2, "ROAD_BUILDING": 2, "MONOPOLY": 2, "VICTORY_POINT": 5}
        
        self.devcard_played: bool = False
        self.devs_just_purchased: List[str] = []

        self.player_trade_limit: int = 1
        self.current_trades: int = 0

        self.largest_army_colour: str = None
        self.longest_road_colour: str = None

        self.mcts_reward: int = 0
        self.tracker: Tracker = Tracker()

        # player setup
        self.initialise_players(players)
    
    def save_game(self, filepath: str):
        with open(filepath, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load_game(filepath: str):
        with open(filepath, 'rb') as file:
            game = pickle.load(file)
        return game
    
    def initialise_players(self, players: List[Player]):
        NUMBER_OF_PLAYERS = len(players)

        for _ in range(NUMBER_OF_PLAYERS):
            new_player = players.pop(0)
            self.player_order.append(new_player.colour)
            self.players[new_player.colour] = new_player
        
        self.player_order = random.sample(self.player_order, NUMBER_OF_PLAYERS)

        return
    
    def evaluate(self, runner_colour: str) -> int:
        while not self.game_over():
            current_colour = self.player_order[self.current_player]
            current_player = self.players[current_colour]
            possible_actions = self.get_possible_actions(current_colour)
            chosen_action = current_player.choose_action(possible_actions)
            self.step(current_colour, chosen_action)
        
        winner_colour = self.tracker.winner
        reward = 0
        if self.reward: reward += self.mcts_reward * 0.5

        if not winner_colour:
            return 0 # draw
        elif winner_colour == runner_colour:
            return reward +1 # win
        else:
            return -1 # loss

    def play(self):
        current_colour = self.player_order[self.current_player]
        if self.gamelog: 
            print("-"*55)
            print(f"TURN[{self.turn}] {current_colour} to play")
            print("-"*55)
        
        while not self.game_over():
            # get possible actions
            current_colour = self.player_order[self.current_player]
            possible_actions: List[Action] = self.get_possible_actions(current_colour)
            # decide and carry out possible action
            player: Player = self.players[current_colour]
            if self.starting_settlement_phase and player.type == "MCTSPlayer":
                chosen_action: Action = player.choose_action(possible_actions, game=self)
            else:
                chosen_action: Action = player.choose_action(possible_actions)
            self.step(current_colour, chosen_action)
            self.tracker.ticks += 1

        if self.gamelog:
            print("-"*55)
            print(f"Longest Road: {self.longest_road_colour}, Largest Army: {self.largest_army_colour}\n")
            for player in self.players.values():
                name = player.type
                colour = player.colour
                knights = player.knights_played
                longest = player.longest_road_length
                total_vp = player.victory_points
                vp_cards = player.development_cards["VICTORY_POINT"]

                print(
                    f"{name} ({colour}) TOTAL VPS: {total_vp}, knights played: {knights}, longest road: {longest}, vp cards: {vp_cards}\n"
                    )
        
        for colour, player in self.players.items():
                settlements = 5 - player.settlements_left
                cities = 4 - player.cities_left

                self.tracker.settlements_built[colour] = settlements + cities
                self.tracker.cities_built[colour] = cities

        return self.tracker

    def game_over(self) -> bool:
        for player in self.players.values():
            if player.victory_points >= 10:
                self.tracker.winner = player.colour
                self.tracker.game_length = self.turn
                return True

        if self.turn >= self.turn_limit:
            return True
        
        return False  
    
    def initial_settlement_phase(self):
        order_forward = self.player_order
        order_backward = list(reversed(self.player_order))

        if self.gamelog: 
            print("-"*55)
            print(f"TURN[{self.turn}]")
            print("-"*55)
        self.initial_builds(order_forward, distribute=False)
        if self.savegame: self.save_game(f"saves/turn_{self.turn}")
        self.turn += 1

        if self.gamelog: 
            print("-"*55)
            print(f"TURN[{self.turn}]")
            print("-"*55)
        self.initial_builds(order_backward, distribute=True)
        if self.savegame: self.save_game(f"saves/turn_{self.turn}")
        self.turn += 1

    def initial_builds(self, player_order: List[str], distribute: bool):
        for colour in player_order:
            player: Player = self.players[colour]
            # build settlement
            action_space = self.get_possible_settlements(colour, initial=True)
            chosen_action: Action = player.choose_action(action_space)
            coord: Point = chosen_action.value
            log = self.board.build_settlement(colour, coord)
            if self.gamelog: print(log)

            if distribute:
                # give resources
                log = self.distribute_resources(coord=coord)
                if self.gamelog: print(log)

            # build adjacent road
            action_space = self.get_possible_roads(colour, coord)
            chosen_action: Action = player.choose_action(action_space)
            edge_id: int = chosen_action.value
            log = self.board.build_road(colour, edge_id)
            if self.gamelog: print(log)
        
    def roll_dice(self) -> Tuple[int, int]:
        return (random.randint(1, 6), random.randint(1, 6))
    
    def buy_devcard(self, colour: str) -> str:
        log: str
        available_devcards: List[str] = []
        player: Player = self.players[colour]

        for devcard, amount in self.bank_devcards.items():
            if amount > 0:
                available_devcards.append(devcard)
        
        gained_devcard = random.choice(available_devcards)
        player.development_cards[gained_devcard] += 1
        self.bank_devcards[gained_devcard] -= 1

        card: str = ""
        if self.debug: card = gained_devcard
        log = f"{colour} has bought a DEVCARD"
        if gained_devcard != "VICTORY_POINT":
            self.devs_just_purchased.append(gained_devcard)
        
        return log
    
    def move_robber_and_rob(self, colour: str, value: Tuple[Hex, str]) -> str:
        log: str = ""
        player: Player = self.players[colour]

        coord, loser_colour = value

        # moving the robber
        self.board.hexes[self.board.robber_coord].has_robber = False
        self.board.robber_coord = coord
        self.board.hexes[coord].has_robber = True
        log += f"{colour} has moved ROBBER to {coord}\n"

        # selecting player to rob
        if loser_colour:
            loser: Player = self.players[loser_colour]

            resources_available: List[str] = []
            for resource, value in loser.resources.items():
                if value > 0:
                    resources_available.extend([resource] * value)
            random_resource = random.choice(resources_available)

            player.resources[random_resource] += 1
            loser.resources[random_resource] -= 1
            log += f"{colour} stole 1 {random_resource} from {loser_colour}"
        else:
            log += f"No valid players to rob"

        return log

    def play_monopoly(self, colour: str, resource: str) -> str:
        stolen: int = 0

        for col, player in self.players.items():
            if col != colour:
                available = player.resources[resource]
                stolen += available
                player.resources[resource] -= available
        
        player: Player = self.players[colour]
        player.resources[resource] += stolen

        return f"{colour} has stolen {stolen} {resource}"
    
    def play_year_of_plenty(self, colour: str, res_tup: Tuple[str, str]) -> str:
        player: Player = self.players[colour]

        for res in res_tup:
            if res != "":
                player.resources[res] += 1
                self.bank_resources[res] -= 1
                log = f"{colour} has received {res}\n"

        return log

    def trade_with_bank(self, colour: str, trade: Tuple[str, int, str]) -> str:
        player: Player = self.players[colour]

        give: str = trade[0]
        give_amount: int = trade[1]
        get: str = trade[2]

        player.resources[give] -= give_amount
        self.bank_resources[give] += give_amount

        player.resources[get] += 1
        self.bank_resources[get] -= 1

        return f"{colour} traded {give_amount} {give} for 1 {get} with BANK"

    def trade_with_players(self, colour: str, trade: Tuple[str, str]) -> str:
        player: Player = self.players[colour]
        other_players: List[Player] = [p for p in self.players.values() if p != player]
        log: str = ""
        possible_trades: List[Action] = []
        for other in other_players:
            result = self.propose_trade(other, trade)
            if result == "ACCEPT_TRADE":
                possible_trades.append(Action("CONFIRMED_TRADE", other.colour))

        if possible_trades:
            selected_trade = player.choose_action(possible_trades)
            acceptee: Player = self.players[selected_trade.value]

            # Update resources for the trade
            player.resources[trade[1]] += 1
            acceptee.resources[trade[1]] -= 1

            player.resources[trade[0]] -=1
            acceptee.resources[trade[0]] += 1


            log += f"{colour} gave {trade[0]} to {acceptee.colour} and got {trade[1]}\n"
        
        return log
    
    def propose_trade(self, receiver: Player, trade: Tuple[str, str]) -> bool:
        possible_actions: List[Action] = [Action("DECLINE_TRADE", trade)]

        needed_resourcee: str = trade[1]
        if receiver.resources[needed_resourcee] >= 1:
            possible_actions.append(Action("ACCEPT_TRADE", trade))

        chosen = receiver.choose_action(possible_actions)

        return chosen.type

    def discard_resources(self) -> str:
        log: str = ""
        # owner_colour : resource : value]
        discarders_dict: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        for colour, player in self.players.items():
            if sum(player.resources.values()) >= 7:

                player_resources: List[str] = []
                for resource, value in player.resources.items():
                    player_resources.extend([resource] * value)

                to_discard = sum(player.resources.values()) // 2
                while to_discard != 0:
                    chosen: str = random.choice(player_resources)
                    player.resources[chosen] -= 1
                    self.bank_resources[chosen] += 1
                    discarders_dict[colour][chosen] += 1
                    player_resources.remove(chosen)
                    to_discard -= 1

        for colour, resource_dict in discarders_dict.items():
            for resource, value in resource_dict.items():
                log += f"{colour} discarded {value} {resource}\n"
        
        return log     

    def distribute_resources(self, total_roll: int=None, coord: Point=None) -> str:
        # resource : [owner_colour : value]
        receivers_dict: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        if coord:
            vertex: Vertex = self.board.vertices[coord]
            hex_neighbors: List[Hex] = vertex.hex_neighbors
            for hexcoord in hex_neighbors:
                resource: str = self.board.hexes[hexcoord].resource
                if resource != "DESERT":
                    receivers_dict[resource][vertex.owner_colour] += 1
        
        elif total_roll:
            assert total_roll != 7
            rolled_hexcoords = self.board.values_dict[total_roll]

            for hexcoord in rolled_hexcoords:
                hextile: Hextile = self.board.hexes[hexcoord]
                if not hextile.has_robber:
                    resource: str = self.board.hexes[hexcoord].resource
                    for neighbor_vertex in self.board.hexes[hexcoord].vertex_neighbors:
                        vertex: Vertex = self.board.vertices[neighbor_vertex]
                        if vertex.owner_colour:
                            if vertex.building == "SETTLEMENT":
                                receivers_dict[resource][vertex.owner_colour] += 1
                            elif vertex.building == "CITY":
                                receivers_dict[resource][vertex.owner_colour] += 2
                            else:
                                raise ValueError("Invalid vertex building")

        else:
            raise ValueError("Nothing passed to distribute resources")

        log: str = ""
        for resource, owner_dict in receivers_dict.items():
            needed_resources = sum(owner_dict.values())
            if needed_resources > self.bank_resources[resource]:
                log += f"Not enough {resource} to distribute\n"
            else:
                for owner_colour, value in owner_dict.items():
                    player: Player = self.players[owner_colour]
                    self.bank_resources[resource] -= value
                    player.resources[resource] += value
                    log += f"{owner_colour} has received {value} {resource}\n"
                    
                    # tracking resources
                    self.tracker.resources_collected[owner_colour] += value
        
        return log

    def get_possible_actions(self, colour: str) -> List[Action]:
        possible_actions: List[Action] = [Action("END_TURN", None)]
        player: Player = self.players[colour]

        if self.starting_settlement_phase:
            if (self.turn % 2) == 1:
                return self.get_possible_settlements(colour, initial=True)
            else:
                return self.get_possible_roads(colour, self.last_settlement_coord)

        if self.robber_active:
            return self.get_robber_possibilities(colour)

        possible_actions.extend(self.get_possible_bank_trades(colour))
        if self.current_trades < self.player_trade_limit:
            player_resources: List[str] = []
            for resource, value in player.resources.items():
                if value > 0:
                    player_resources.extend([resource] * value)
            if player_resources:
                possible_actions.extend(self.get_possible_player_trades(player_resources))

        can_afford: bool = ( # ROAD
            player.resources["WOOD"] >= 1 and player.resources["BRICK"] >= 1
        )
        if player.roads_left > 0 and can_afford:
            possible_actions.extend(self.get_possible_roads(colour))

        can_afford = ( # SETTLEMENT
            player.resources["WOOD"] >= 1 and player.resources["BRICK"] >= 1 and
            player.resources["SHEEP"] >= 1 and player.resources["WHEAT"] >= 1
        )
        if player.settlements_left > 0 and can_afford:
            possible_actions.extend(self.get_possible_settlements(colour))

        can_afford = ( # CITY
            player.resources["WHEAT"] >= 2 and player.resources["ORE"] >= 3
        )
        if player.cities_left > 0 and can_afford:
            possible_actions.extend(self.get_possible_cities(colour))
        
        can_afford = ( # DEVCARD
            player.resources["WHEAT"] >= 1 and player.resources["ORE"] >= 1 and
            player.resources["SHEEP"] >= 1
        )
        if sum(self.bank_devcards.values()) > 0 and can_afford:
            possible_actions.append(Action("BUY_DEVCARD", None))
        
        if not self.devcard_played:
            available_devcards: List[str] = []
            for devcard, amount in player.development_cards.items():
                if amount > 0 and devcard != "VICTORY_POINT":
                    available_devcards.extend([devcard] * amount)
            if self.devs_just_purchased:
                for card in self.devs_just_purchased:
                    available_devcards.remove(card)
            if available_devcards:
                possible_actions.extend(self.get_possible_devcards_plays(colour, available_devcards))

        return possible_actions

    def get_possible_roads(self, colour: str, coord: Point=None) -> List[Action]:
        action_type: str = "BUILD_ROAD"
        possible_actions: List[Action] = []

        # only used for initial placement
        if coord:
            vertex: Vertex = self.board.vertices[coord]
            for edge_id in vertex.edge_neighbors:
                possible_actions.append(Action(action_type, edge_id))
        # default
        else:
            player: Player = self.players[colour]
            explored_vertex_coords: List[Point] = []
            owned_edges_ids = player.owned_edges
            vertex_coords: Set[Point] = set()
            for edge_id in owned_edges_ids:
                vertex_coords.update(self.board.edges[edge_id].vertex_neighbors)
            for i in range(len(vertex_coords)):
                coord = vertex_coords.pop()
                vertex: Vertex = self.board.vertices[coord]
                explored_vertex_coords.append(coord)
                if vertex.owner_colour == colour or vertex.owner_colour is None:
                    potential_edge_id = vertex.edge_neighbors
                    for id in potential_edge_id:
                        if not self.board.edges[id].has_road:
                            possible_actions.append(Action(action_type, id))
            
        return possible_actions
    
    def get_possible_settlements(self, colour: str, initial: bool=False) -> List[Action]:
        action_type: str = "BUILD_SETTLEMENT"
        possible_actions: List[Action] = []

        # only used for initial placement
        if initial:
            for coord, vertex in self.board.vertices.items():
                if vertex.owner_colour == None:
                    all_neighbors_unowned = all(
                        self.board.vertices[neighbor].owner_colour == None for neighbor in vertex.vertex_neighbors
                        )
                    if all_neighbors_unowned:
                        possible_actions.append(Action(action_type, coord))
                else:
                    continue
        # default
        else:
            player: Player = self.players[colour]
            owned_edges_indexes: List[int] = player.owned_edges
            possible_vertex_coords: Set[Point] = set()
            for index in owned_edges_indexes:
                possible_vertex_coords.update(self.board.edges[index].vertex_neighbors)
            for coord in possible_vertex_coords:
                vertex: Vertex = self.board.vertices[coord]
                all_neighbors_unowned = all(
                    self.board.vertices[neighbor].owner_colour == None for neighbor in vertex.vertex_neighbors
                    )
                if vertex.owner_colour == None and all_neighbors_unowned:
                    possible_actions.append(Action(action_type, coord))

        return possible_actions

    def get_possible_cities(self, colour: str) -> List[Action]:
        action_type: str = "BUILD_CITY"
        possible_actions: List[Action] = []
        player: Player = self.players[colour]

        for vertex_coord in player.owned_vertices:
            vertex: Vertex = self.board.vertices[vertex_coord]
            if vertex.building == "SETTLEMENT":
                possible_actions.append(Action(action_type, vertex_coord))

        return possible_actions
    
    def get_possible_devcards_plays(self, colour: str, available_devcards: List[str]) -> List[Action]:
        action_type: str
        player: Player = self.players[colour]
        possible_actions: List[Action] = []
        
        # Deal with devcards as composite actions?
        if "ROAD_BUILDING" in available_devcards and player.roads_left >= 2:
            action_type = "PLAY_ROAD_BUILDING"
            possible_actions.append(Action(action_type, None))
        if "KNIGHT" in available_devcards:
            action_type = "PLAY_KNIGHT"
            # robber_locations = self.get_possible_robber_locations()
            # for location in robber_locations:
            #     possible_actions.append(Action(action_type, location))
            possible_actions.append(Action(action_type, None))
        if "YEAR_OF_PLENTY" in available_devcards and sum(self.bank_resources.values()) > 0:
            action_type = "PLAY_YEAR_OF_PLENTY"
            combinations = self.get_year_of_plenty_combinations()
            for comb in combinations:
                possible_actions.append(Action(action_type, comb))
        if "MONOPOLY" in available_devcards:
            action_type = "PLAY_MONOPOLY"
            for resource in self.bank_resources.keys():
                possible_actions.append(Action(action_type, resource))
        
        return possible_actions
    
    def get_year_of_plenty_combinations(self) -> Tuple[str, str]:
        resource_list: List[str] = [""]
        for resource, amount in self.bank_resources.items():
            if amount == 1: 
                resource_list.extend([resource] * amount)
            elif amount > 1:
                resource_list.extend([resource] * 2)

        return set(combinations(resource_list, 2))

    def get_robber_possibilities(self, colour) -> List[Action]:
        action_type: str = "MOVE_ROBBER_AND_ROB"
        possible_actions: List[Action] = []

        # Robber locations
        possible_robber_coords = []
        # can optimise by splitting sea and land hexes by dict
        for coord, hextile in self.board.hexes.items():
            if hextile.resource != "SEA" and not hextile.has_robber:
                possible_robber_coords.append(coord)
        
        for coord in possible_robber_coords:
            added: bool = False
            hextile: Hextile = self.board.hexes[coord]
            vertex_neighbor_coords: List[Point] = hextile.vertex_neighbors
            for neighbor_vertex in vertex_neighbor_coords:
                vertex: Vertex = self.board.vertices[neighbor_vertex]
                # not unowned and not their own vertex
                if vertex.owner_colour != None and vertex.owner_colour != colour:
                    # if player has resources to rob
                    if sum(self.players[vertex.owner_colour].resources.values()) > 0:
                        value = (coord, vertex.owner_colour)
                        possible_actions.append(Action(action_type, value))
                        added: bool = True
            if not added:
                value = (coord, None)
                possible_actions.append(Action(action_type, value))
        
        return possible_actions
    
    def get_possible_robber_locations(self) -> List[Action]:
        action_type: str = "MOVE_ROBBER"
        possible_actions: List[Action] = []

        # can optimise by splitting sea and land hexes by dict
        for coord, hextile in self.board.hexes.items():
            if hextile.resource != "SEA" and not hextile.has_robber:
                possible_actions.append(Action(action_type, coord))
        
        return possible_actions

    def get_possible_players_to_rob(self, colour: str, coord: Hex) -> List[Action]:
        action_type: str = "ROB"
        possible_actions: List[Action] = []

        hextile: Hextile = self.board.hexes[coord]
        vertex_neighbor_coords: List[Point] = hextile.vertex_neighbors
        for neighbor_vertex in vertex_neighbor_coords:
            vertex: Vertex = self.board.vertices[neighbor_vertex]
            # not unowned and not their own vertex
            if vertex.owner_colour != None and vertex.owner_colour != colour:
                # if player has resources to rob
                if sum(self.players[vertex.owner_colour].resources.values()) > 0:
                    possible_actions.append(Action(action_type, vertex.owner_colour))

        return possible_actions
    
    def get_possible_bank_trades(self, colour: str) -> List[Action]:
        action_type: str = "TRADE_WITH_BANK"
        possible_actions: List[Action] = []
        player: Player = self.players[colour]
        # first 4 give, last 1 receive
        trade: Tuple[str, int, str]

        available_bank_resources: List[str] = [
            resource for resource, value in self.bank_resources.items() if value > 0
        ]

        for give, amount in player.resources.items():
            cost = player.trading_cost[give]
            if amount >= cost:
                for want in available_bank_resources:
                    if want != give:
                        trade = (give, cost, want)
                        possible_actions.append(Action(action_type, trade))
        
        return possible_actions
    
    def get_possible_player_trades(self, all_possible_offering: List[str]) -> List[Action]:
        action_type: str = "TRADE_WITH_PLAYER"
        possible_actions: List[Action] = []

        resources = list(self.bank_resources.keys())

        for offer in all_possible_offering:
            other_resources = [r for r in resources if r != offer]
            for receive in other_resources:
                trade = (offer, receive)
                possible_actions.append(Action(action_type, trade))
        
        return possible_actions
    
    def end_turn(self):
        if self.savegame: self.save_game(f"saves/turn_{self.turn}")
        if self.turn <= 16:
            # on odd turns ie settlements, don't change player
            if (self.turn % 2) == 1:
                pass
            # first settlement phase go forward in player order
            elif self.turn <= 6:
                self.current_player = (self.current_player + 1)
            # on end of both phases don't change current player
            elif self.turn == 8 or self.turn == 16:
                pass
            # second settlement phase go backward in player order
            else:
                self.current_player = (self.current_player - 1)
        else:
            self.current_player = (self.current_player + 1) % len(self.player_order)
        
        self.turn += 1
        self.devs_just_purchased.clear()
        self.devcard_played = 0
        self.current_trades = 0

        current_colour = self.player_order[self.current_player]

        if self.gamelog: 
            print("\n")
            print("-"*55)
            print(f"TURN[{self.turn}] {current_colour} to play")
            print("-"*55)
        
        if self.turn == 17:
            self.starting_settlement_phase = False
        
        if not self.starting_settlement_phase:
            dice_roll: Tuple[int, int] = self.roll_dice()
            if self.gamelog: print(f"{current_colour} has rolled {dice_roll}")
            total_roll: int = dice_roll[0] + dice_roll[1]
            if total_roll == 7:
                self.robber_active = True
                log = self.discard_resources()
            else:
                log = self.distribute_resources(total_roll)
            if self.gamelog: print(log)
    
    def step(self, colour: str, chosen_action: Action):
        player: Player = self.players[colour]
        # need to check vps for any action that can change them indirectly
        # direct: build settlement, build city, get vp
        # indirect: build road, play knight
        action_type = chosen_action.type 
        value = chosen_action.value

        if action_type == "END_TURN":
            log = "END_TURN"
            if self.gamelog: print(log)
            self.end_turn()
        
        elif action_type == "MOVE_ROBBER_AND_ROB":
            log = self.move_robber_and_rob(colour, value)
            self.robber_active = False
            if self.gamelog: print(log)

        elif action_type == "BUILD_ROAD":
            log = self.board.build_road(colour, value)
            if self.gamelog: print(log)
            if self.starting_settlement_phase:
                self.end_turn()
            else:
                player.resources["WOOD"] -= 1
                player.resources["BRICK"] -= 1
                self.bank_resources["WOOD"] += 1
                self.bank_resources["BRICK"] += 1

        elif action_type == "BUILD_SETTLEMENT":
            log = self.board.build_settlement(colour, value)
            if self.gamelog: print(log)
            if self.starting_settlement_phase:
                if self.turn <= 8:
                    self.last_settlement_coord = value
                else:
                    self.last_settlement_coord = value
                    log += self.distribute_resources(coord=self.last_settlement_coord)
                self.end_turn()
            else:
                if not self.tracker.first_building_turn_built:
                    self.tracker.first_building_turn_built = self.turn
                if self.reward:
                    if self.turn <= 24 and self.mcts_reward == 0:
                        # print(f"MCTS rewarded for *Settlement*")
                        self.mcts_reward += 1
                player.resources["WOOD"] -= 1
                player.resources["BRICK"] -= 1
                player.resources["SHEEP"] -= 1
                player.resources["WHEAT"] -= 1
                self.bank_resources["WOOD"] += 1
                self.bank_resources["BRICK"] += 1
                self.bank_resources["SHEEP"] += 1
                self.bank_resources["WHEAT"] += 1

        elif action_type == "BUILD_CITY":
            log = self.board.build_city(colour, value)
            if self.gamelog: print(log)
            if not self.tracker.first_building_turn_built:
                    self.tracker.first_building_turn_built = self.turn
            if self.reward:
                if self.turn <= 24 and self.mcts_reward == 0:
                    # print(f"MCTS rewarded for *City*")
                    self.mcts_reward += 1
            player.resources["WHEAT"] -= 2
            player.resources["ORE"] -= 3
            self.bank_resources["WHEAT"] += 2
            self.bank_resources["ORE"] += 3

        elif action_type == "BUY_DEVCARD":
            log = self.buy_devcard(colour)
            if self.gamelog: print(log)
            self.tracker.dev_cards_purchased[colour] += 1
            player.resources["WHEAT"] -= 1
            player.resources["ORE"] -= 1
            player.resources["SHEEP"] -= 1
            self.bank_resources["WHEAT"] += 1
            self.bank_resources["ORE"] += 1
            self.bank_resources["SHEEP"] += 1

        elif action_type == "PLAY_ROAD_BUILDING":
            self.devcard_played = True
            log = f"{colour} has played ROAD_BUILDING"
            locations = self.get_possible_roads(colour)
            if locations:
                action = player.choose_action(locations)
                log += self.board.build_road(colour, action.value)
                log += "\n"
            locations = self.get_possible_roads(colour)
            if locations:
                action = player.choose_action(locations)
                log += self.board.build_road(colour, action.value)
            if self.gamelog: print(log)

        elif action_type == "PLAY_KNIGHT":
            self.devcard_played = True
            self.robber_active = True
            log = f"{colour} has played KNIGHT\n"
            player.development_cards["KNIGHT"] -= 1
            player.knights_played += 1
            if player.knights_played >= 3:
                if self.largest_army_colour:
                    enemy = self.players[self.largest_army_colour]
                    largest_army = enemy.knights_played
                    if player.knights_played > largest_army:
                        self.largest_army_colour = colour
                        player.victory_points += 2
                        enemy.victory_points -= 2
                else:
                    self.largest_army_colour = colour
                    player.victory_points += 2
            if self.gamelog: print(log)
        
        elif action_type == "PLAY_MONOPOLY":
            self.devcard_played = True
            log = f"{colour} has played MONOPOLY\n"
            log += self.play_monopoly(colour, value)
            player.development_cards["MONOPOLY"] -= 1
            if self.gamelog: print(log)

        elif action_type == "PLAY_YEAR_OF_PLENTY":
            self.devcard_played = True
            log = f"{colour} has played YEAR_OF_PLENTY\n"
            log += self.play_year_of_plenty(colour, value)
            player.development_cards["YEAR_OF_PLENTY"] -= 1
            if self.gamelog: print(log)

        elif action_type == "TRADE_WITH_BANK":
            log = self.trade_with_bank(colour, value)
            if self.gamelog and log != "": print(log)

        elif action_type == "TRADE_WITH_PLAYER":
            self.current_trades += 1
            log = self.trade_with_players(colour, value)
            if self.gamelog and log != "": print(log)

        else:
            print(action_type)
            raise ValueError("Invalid action type")