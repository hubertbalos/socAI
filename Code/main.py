import pygame
from renderer import Renderer

def main():
    print("Settlers of Catan now running")
    pygame.init()

    myRenderer = Renderer()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        myRenderer.displayScreen()
    
    pygame.quit()

if __name__ == "__main__":
    main()