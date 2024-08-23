from game import Game
from player import RandomPlayer, WeightedRandomPlayer
from tracker import Tracker
import time
from statistics import mean 
from tqdm import tqdm
from mcts import MCTSPlayer
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

WINDOW_SIZE = (750, 910)
USE_MULTIPROCESSING = True
TOTAL_GAMES = 1000

def simulate_game(i):
    players = [
        RandomPlayer(Colour="RED"), 
        RandomPlayer(Colour="WHITE"), 
        RandomPlayer(Colour="ORANGE"), 
        RandomPlayer(Colour="BLUE"),

        # WeightedRandomPlayer(Colour="RED"),
        # WeightedRandomPlayer(Colour="WHITE"),
        # WeightedRandomPlayer(Colour="ORANGE"),
        # WeightedRandomPlayer(Colour="BLUE"),

        # MCTSPlayer(Colour="RED", Iterations=1000, Pruning=False, Reward=False),
        # MCTSPlayer(Colour="WHITE", Iterations=1000, Pruning=False, Reward=True),
        # MCTSPlayer(Colour="ORANGE", Iterations=1000, Pruning=True, Reward=False),
        # MCTSPlayer(Colour="BLUE", Iterations=1000, Pruning=True, Reward=True),
    ]
    
    game = Game(windowSize=WINDOW_SIZE, players=players)
    tracker: Tracker = game.play()
    
    result = {
        'winner': tracker.winner,
        'game_length': tracker.game_length,
        'ticks': tracker.ticks,
        'first_building_turn_built': tracker.first_building_turn_built,
        'winner_settlements_built': tracker.settlements_built[tracker.winner] if tracker.winner else None,
        'winner_cities_built': tracker.cities_built[tracker.winner] if tracker.winner else None,
        'winner_resources_collected': tracker.resources_collected[tracker.winner] if tracker.winner else None,
        'losers_settlements_built': {colour: built for colour, built in tracker.settlements_built.items() if colour != tracker.winner},
        'losers_cities_built': {colour: built for colour, built in tracker.cities_built.items() if colour != tracker.winner},
        'losers_resources_collected': {colour: collected for colour, collected in tracker.resources_collected.items() if colour != tracker.winner},
    }
    
    return result, game

def main(use_multiprocessing=False):

    total_games = TOTAL_GAMES

    discarded = 0
    wins_by_colour = {colour: 0 for colour in ["RED", "WHITE", "ORANGE", "BLUE"]}
    game_lengths = []
    ticks = []
    first_building_turn_built = []
    winner_settlements_built = []
    winner_cities_built = []
    winner_resources_collected = []
    losers_settlements_built = []
    losers_cities_built = []
    losers_resources_collected = []

    start = time.time()
    if use_multiprocessing:
        print(f"CPU cores: {multiprocessing.cpu_count()}")
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            futures = [executor.submit(simulate_game, i) for i in range(total_games)]

            try:
                for future in tqdm(as_completed(futures), total=total_games, desc="Simulating games", unit="games"):
                    result, game = future.result()

                    if result['winner'] is None:
                        discarded += 1
                    else:
                        wins_by_colour[result['winner']] += 1
                        game_lengths.append(result['game_length'])
                        ticks.append(result['ticks'])

                        first_building_turn_built.append(result['first_building_turn_built'])

                        winner_settlements_built.append(result['winner_settlements_built'])
                        winner_cities_built.append(result['winner_cities_built'])
                        winner_resources_collected.append(result['winner_resources_collected'])

                        losers_settlements_built.extend(result['losers_settlements_built'].values())
                        losers_cities_built.extend(result['losers_cities_built'].values())
                        losers_resources_collected.extend(result['losers_resources_collected'].values())

            except KeyboardInterrupt:
                print("Received KeyboardInterrupt, terminating all processes...")
                for proc in multiprocessing.active_children():
                    print(f"Terminating process {proc.pid}")
                    proc.terminate()  # Forcefully terminate the process
                executor.shutdown(wait=False)
                raise
    else:
        # Run simulations sequentially
        for i in tqdm(range(total_games), desc="Simulating games", unit="games/s"):
            result, game = simulate_game(i)

            if result['winner'] is None:
                discarded += 1
            else:
                wins_by_colour[result['winner']] += 1
                game_lengths.append(result['game_length'])
                ticks.append(result['ticks'])

                first_building_turn_built.append(result['first_building_turn_built'])

                winner_settlements_built.append(result['winner_settlements_built'])
                winner_cities_built.append(result['winner_cities_built'])
                winner_resources_collected.append(result['winner_resources_collected'])

                losers_settlements_built.extend(result['losers_settlements_built'].values())
                losers_cities_built.extend(result['losers_cities_built'].values())
                losers_resources_collected.extend(result['losers_resources_collected'].values())

    run_time = time.time() - start

    print("\n")

    print(f"AVERAGE GAME LENGTH: {mean(game_lengths):.2f} turns")
    print(f"AVERAGE TICKS: {mean(ticks):.2f} ticks\n")
    print("WINS BY COLOUR:")
    print(f"{wins_by_colour}\n")
    print(f"TURN FIRST BUILDING BUILT: {mean(first_building_turn_built):.2f}\n")
    print(f"WINNER SETTLEMENTS BUILT: {mean(winner_settlements_built):.2f}\n")
    print(f"WINNER CITIES BUILT: {mean(winner_cities_built):.2f}\n")
    print(f"WINNER RESOURCES COLLECTED: {mean(winner_resources_collected):.2f}\n")
    print(f"LOSERS SETTLEMENTS BUILT: {mean(losers_settlements_built):.2f}\n")
    print(f"LOSERS CITIES BUILT: {mean(losers_cities_built):.2f}\n")
    print(f"LOSERS RESOURCES COLLECTED: {mean(losers_resources_collected):.2f}\n")

    print("\n")

    print(f"Run time: {run_time:.2f} seconds")
    print(f"Number of discarded games: {discarded}")

    print("\n")

    return game

if __name__ == "__main__":
    game = main(use_multiprocessing=USE_MULTIPROCESSING)
    import pygame
    from renderer import Renderer
    # Render loop

    pygame.init()
    renderer = Renderer(windowSize=WINDOW_SIZE, game=game)

    renderer.display()
    lower_limit = 1
    upper_limit = game.turn-1

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game.savegame:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if game.turn > lower_limit:
                            game.turn -= 1
                            new_game = Game.load_game(f"saves/turn_{game.turn}")
                            renderer.display_game = new_game
                            renderer.display()
                    elif event.key == pygame.K_RIGHT:
                        if game.turn < upper_limit:
                            game.turn += 1
                            new_game = Game.load_game(f"saves/turn_{game.turn}")
                            renderer.display_game = new_game
                            renderer.display()
    
    pygame.quit()