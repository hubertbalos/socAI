import pygame
from renderer import Renderer
from game import Game
from player import RandomPlayer, WeightedRandomPlayer
from tracker import Tracker
import time
from typing import Dict, List
from collections import defaultdict
from statistics import mean 
from tqdm import tqdm
from mcts import MCTSPlayer

def main():
    pygame.init()

    WINDOW_SIZE = (750, 910)
    start = time.time()
    discarded = 0
    completed_run_time = 0

    wins_by_colour: Dict[int] = defaultdict(int)
    game_lengths: List[int] = []

    winner_settlements_built: List[int] = []
    winner_cities_built: List[int] = []
    winner_resources_collected: List[int] = []

    losers_settlements_built: List[int] = []
    losers_cities_built: List[int] = []
    losers_resources_collected: List[int] = []

    for _ in tqdm(range(1), desc="Simulating games", unit="games/s"):
        start2 = time.time()
        players = [
            RandomPlayer(Colour="RED"), 
            RandomPlayer(Colour="WHITE"), 
            RandomPlayer(Colour="ORANGE"), 
            RandomPlayer(Colour="BLUE"),
            # MCTSPlayer(Colour="BLUE", Iterations=100)
        ]
        game = Game(windowSize=WINDOW_SIZE, players=players)
        tracker: Tracker = game.play()
        if tracker.winner is None:
            discarded += 1
        else:
            wins_by_colour[tracker.winner] += 1
            game_lengths.append(tracker.game_length)

            # winner
            winner_settlements_built.append(tracker.settlements_built[tracker.winner])
            winner_cities_built.append(tracker.cities_built[tracker.winner])
            winner_resources_collected.append(tracker.resources_collected[tracker.winner])

            # losers
            for colour, built in tracker.settlements_built.items():
                if colour != tracker.winner:
                    losers_settlements_built.append(built)

            for colour, built in tracker.cities_built.items():
                if colour != tracker.winner:
                    losers_cities_built.append(built)
            
            for colour, collected in tracker.resources_collected.items():
                if colour != tracker.winner:
                    losers_resources_collected.append(collected)

            completed_run_time += (time.time() - start2)

    print(f"AVERAGE GAME LENGTH: {mean(game_lengths)}")
    print("WINS BY COLOUR:")
    print(wins_by_colour)
    print(f"WINNER SETTLEMENTS BUILT: {mean(winner_settlements_built)}\n")
    print(f"WINNER CITIES BUILT: {mean(winner_cities_built)}\n")
    print(f"WINNER RESOURCES COLLECTED: {mean(winner_resources_collected)}\n")
    print(f"LOSERS SETTLEMENTS BUILT: {mean(losers_settlements_built)}\n")
    print(f"LOSERS CITIES BUILT: {mean(losers_cities_built)}\n")
    print(f"LOSERS RESOURCES COLLECTED: {mean(losers_resources_collected)}\n")


    print("\n")

    print(f"NET Run time: {time.time() - start}")
    print(f"Completed games time: {completed_run_time}")
    print(f"Number of discarded games: {discarded}")



    # Render loop

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

if __name__ == "__main__":
    main()