import pygame
from renderer import Renderer
from game import Game
from player import RandomPlayer, WeightedRandomPlayer
import time

def main():
    pygame.init()

    WINDOW_SIZE = (750, 910)
    start = time.time()
    discarded = 0
    tracked = 0
    completed_run_time = 0
    for _ in range(1000):
        start2 = time.time()
        players = [RandomPlayer(), RandomPlayer(), RandomPlayer(), WeightedRandomPlayer()]
        game = Game(windowSize=WINDOW_SIZE, players=players)
        dis, tra = game.play()
        discarded += dis
        tracked += tra
        if dis != 1:
            completed_run_time += (time.time() - start2)

    print(f"Run time: {time.time() - start}")
    print(f"Completed games time: {completed_run_time}")
    print(f"Tracked time: {tracked}")
    print(f"Discarded games: {discarded}")

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