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