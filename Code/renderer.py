import pygame

class Renderer():
    """
    Renders the state of the game to the screen
    """
    def __init__(self):
        print("Renderer initialising")

        self.window_size = (750, 910)
        self.window = pygame.display.set_mode(self.window_size)

        pygame.display.set_caption("Settlers of Catan Engine")

        self.boardstate = None

        self.displayState()

    def displayState(self):
        self.window.fill((255, 255, 255))
        pygame.display.update()
