import pygame
from board import Board
from hexlib import *
import numpy as np

class Renderer():
    """
    Renders the state of the game to the screen
    """
    def __init__(self):
        print("Renderer initialising")

        pygame.display.set_caption("Settlers of Catan Engine")

        self.window_size = (750, 910)
        self.window = pygame.display.set_mode(self.window_size)
        self.board = Board(self.window_size)

        self.hexColourDict = {"ORE":(160,160,160), 
                              "WHEAT":(255,255,0), 
                              "WOOD":(0,102,0), 
                              "BRICK":(153,0,0), 
                              "SHEEP":(204,255,153), 
                              "DESERT":(255,229,204),
                              "SEA":(153,204,255)}
        
        self.font = pygame.font.SysFont(None, 40)

        self.displayState()

    def displayState(self):
        # background colour
        self.window.fill((255, 255, 255))

        # drawing hexes
        for hextile in self.board.hexes:
            corners = polygon_corners(self.board.layout, hextile.hexCoordinate)
            center = hex_to_pixel(self.board.layout, hextile.hexCoordinate)
            # print(f"corners: {corners}\n")
            hextileColour = self.hexColourDict[hextile.resource]
            r = hextileColour[0]
            g = hextileColour[1]
            b = hextileColour[2]
            pygame.draw.polygon(self.window, (r, g, b), corners, width=0)
            if hextile.resource != "DESERT":
                if hextile.value == 6 or hextile.value == 8:
                    text_surface = self.font.render(str(hextile.value), True, (255, 0, 0))
                else:
                    text_surface = self.font.render(str(hextile.value), True, (0, 0, 0))
                self.window.blit(text_surface, (center.x -11, center.y -9))
        
        pygame.display.update()
