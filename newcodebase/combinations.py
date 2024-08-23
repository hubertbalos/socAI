from itertools import combinations_with_replacement, combinations
from typing import List, Tuple
import time

# Function to generate unique trades
def generate_unique_trades(player_resources: List[str], resources):
    card_limit = 1
    unique_trades = set()
    
    player_resources = player_resources + [""] * (card_limit - 1)
    all_possible_offering = combinations(player_resources, card_limit)

    # For each combination of the first set of 3 resources
    for offer in all_possible_offering:
        # Generate all unique combinations of 3 resources from the complete resource list with replacement
        other_resources = [r for r in resources if r not in offer] + [""]
        # other_resources = resources + [""]
        all_possible_receiving = combinations_with_replacement(other_resources, card_limit)
        
        # For each combination, add the valid trade to the set
        for receive in all_possible_receiving:
            if all(element == "" for element in receive):
                continue
            intersection = set(offer).intersection(set(receive))
            if intersection == {""} or len(intersection) == 0:
                trade_pair = (tuple(offer), tuple(receive))
                unique_trades.add(trade_pair)
                print(len(unique_trades))
    
    return list(unique_trades)

# Define the resources
resources = ["WOOD", "BRICK", "SHEEP", "WHEAT", "ORE"]

# Define the player's resources
player_resources = [
    "WOOD", "WOOD", "WOOD",
    "BRICK", "BRICK", "BRICK",
    "SHEEP", "SHEEP", "SHEEP",
    "WHEAT", "WHEAT", "WHEAT",
    "ORE", "ORE", "ORE",
]

# Define player possibilities
player_possibilities = [
    ["p2"], ["p3"], ["p4"], 
    ["p2", "p3"], ["p2", "p4"], ["p3", "p4"],
    ["p2", "p3", "p4"],
]

start_time = time.time()

unique_trades = generate_unique_trades(player_resources, resources)

end_time = time.time()
elapsed_time = end_time - start_time

for trade in sorted(unique_trades):
    print(trade)

print(f"Number of unique trades: {len(unique_trades) * len(player_possibilities)}")
print(f"Execution time: {elapsed_time} seconds")

# def propose_trade(self, receiver: Player, trade: Tuple[Tuple[str, str], Tuple[str, str]]) -> bool:
#         possible_actions: List[Action] = [Action("DECLINE_TRADE", False)]

#         needed_resources: List[str] = []
#         if trade[1][0] != "":
#             needed_resources.append(trade[1][0])
#         if trade[1][1] != "":
#             needed_resources.append(trade[1][1])

#         needed_dict: Dict[str, int] = defaultdict(int)
#         for resource in needed_resources:
#             needed_dict[resource] += 1

#         can_trade = True
#         for resource, amount in needed_dict.items():
#             if receiver.resources[resource] < amount:
#                 can_trade = False
#                 break
#         if can_trade:
#             possible_actions.append(Action("ACCEPT_TRADE", True))

#         chosen = receiver.choose_action(possible_actions)

#         return chosen.value

# def get_possible_player_trades(self, player_resources: List[str]) -> List[Action]:
#         action_type: str = "TRADE_WITH_PLAYER"
#         possible_actions: List[Action] = []

#         card_limit = 1
#         resources = list(self.bank_resources.keys())
#         unique_trades = set()

#         player_resources = player_resources + [""] * (card_limit - 1)
#         all_possible_offering = list(combinations(player_resources, card_limit))

#         # For each combination of the first set of resources
#         # start = time.time()
#         for offer in all_possible_offering:
#             offer_set = set(offer)
            
#             # Generate all unique combinations of resources from the complete resource list with replacement
#             other_resources = [r for r in resources if r not in offer_set] + [""]
            
#             all_possible_receiving = list(combinations_with_replacement(other_resources, card_limit))
            
#             # For each combination, add the valid trade to the set
#             for receive in all_possible_receiving:
#                 if receive == ("", ""):
#                     continue
                
#                 receive_set = set(receive)
#                 if not offer_set.intersection(receive_set) or (offer_set == {""} and receive_set != {""}):
#                     unique_trades.add((tuple(offer), tuple(receive)))
#         # self.tracker += (time.time() - start)
        
#         for trade in unique_trades:
#             possible_actions.append(Action(action_type, trade))
        
#         return possible_actions







# WINDOW_SIZE = (750, 910)
    # start = time.time()
    # discarded = 0
    # completed_run_time = 0

    # wins_by_colour: Dict[int] = defaultdict(int)
    # game_lengths: List[int] = []
    # ticks: List[int] = []

    # winner_settlements_built: List[int] = []
    # winner_cities_built: List[int] = []
    # winner_resources_collected: List[int] = []

    # losers_settlements_built: List[int] = []
    # losers_cities_built: List[int] = []
    # losers_resources_collected: List[int] = []

    # for _ in tqdm(range(100), desc="Simulating games", unit="games/s"):
    #     start2 = time.time()
    #     players = [
    #         # RandomPlayer(Colour="RED"), 
    #         # RandomPlayer(Colour="WHITE"), 
    #         # RandomPlayer(Colour="ORANGE"), 
    #         # RandomPlayer(Colour="BLUE"),

    #         # WeightedRandomPlayer(Colour="RED"),
    #         # WeightedRandomPlayer(Colour="WHITE"),
    #         # WeightedRandomPlayer(Colour="ORANGE"),

    #         MCTSPlayer(Colour="RED", Iterations=100, Pruning=False, Reward=False),
    #         MCTSPlayer(Colour="WHITE", Iterations=100, Pruning=False, Reward=True),
    #         MCTSPlayer(Colour="ORANGE", Iterations=100, Pruning=True, Reward=False),

    #         MCTSPlayer(Colour="BLUE", Iterations=100, Pruning=True, Reward=True),
    #     ]
    #     game = Game(windowSize=WINDOW_SIZE, players=players)
    #     tracker: Tracker = game.play()
    #     if tracker.winner is None:
    #         discarded += 1
    #     else:
    #         wins_by_colour[tracker.winner] += 1
    #         game_lengths.append(tracker.game_length)
    #         ticks.append(tracker.ticks)

    #         # winner
    #         winner_settlements_built.append(tracker.settlements_built[tracker.winner])
    #         winner_cities_built.append(tracker.cities_built[tracker.winner])
    #         winner_resources_collected.append(tracker.resources_collected[tracker.winner])

    #         # losers
    #         for colour, built in tracker.settlements_built.items():
    #             if colour != tracker.winner:
    #                 losers_settlements_built.append(built)

    #         for colour, built in tracker.cities_built.items():
    #             if colour != tracker.winner:
    #                 losers_cities_built.append(built)
            
    #         for colour, collected in tracker.resources_collected.items():
    #             if colour != tracker.winner:
    #                 losers_resources_collected.append(collected)

    #         completed_run_time += (time.time() - start2)