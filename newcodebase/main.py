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
    for _ in range(1):
        players = [RandomPlayer(), RandomPlayer(), RandomPlayer(), WeightedRandomPlayer()]
        game = Game(windowSize=WINDOW_SIZE, players=players)
        dis, tra = game.play()
        discarded += dis
        tracked += tra

    print(f"Run time: {time.time() - start}")
    print(f"Tracked time: {tracked}")
    print(f"Discarded games: {discarded}")

    renderer = Renderer(windowSize=WINDOW_SIZE, game=game)

    renderer.display()

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # elif event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_RETURN:  # Check if Enter key is pressed
            #         running = False
        
        #turn = input("Enter Turn:")
        #renderer.updateGame(turn)
        
    
    pygame.quit()

if __name__ == "__main__":
    main()