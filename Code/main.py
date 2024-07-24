import pygame
from renderer import Renderer

def main():
    print("Settlers of Catan now running")
    pygame.init()

    renderer = Renderer()

    renderer.displayState()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Check if Enter key is pressed
                    running = False
        
        # myRenderer.displayState()
    
    pygame.quit()

if __name__ == "__main__":
    main()