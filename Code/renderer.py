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

        self.ColourDict = {"ORE":(160,160,160), 
                           "WHEAT":(255,255,0), 
                           "WOOD":(0,102,0), 
                           "BRICK":(153,0,0), 
                           "SHEEP":(204,255,153), 
                           "DESERT":(255,229,204),
                           "SEA":(153,204,255),
                           "3:1":(0,0,0)}
        
        self.pipNumberDict = {2:1, 3:2, 4:3, 5:4, 6:5, 8:5, 9:4, 10:3, 11:2, 12:1}
        
        self.font = pygame.font.SysFont(None, 40)

        self.displayState()

    def displayState(self):
        # background colour
        self.window.fill((102, 178, 255))
        # drawing hexes
        for coord, hextile in self.board.hexes.items():
            corners = polygon_corners(self.board.layout, coord)
            center = hex_to_pixel(self.board.layout, coord)
            hextileColour = self.ColourDict[hextile.resource]
            r = hextileColour[0]
            g = hextileColour[1]
            b = hextileColour[2]
            # actual hexagon
            pygame.draw.polygon(self.window, (r, g, b), corners, width=0)
            # number inside hexagon
            if hextile.resource != "DESERT" and hextile.resource != "SEA":
                if hextile.value == 6 or hextile.value == 8:
                    colour = (255, 0, 0)
                else:
                    colour = (0, 0, 0)
                text_surface = self.font.render(str(hextile.value), True, colour)
                text_rect = text_surface.get_rect()
                text_rect.center = (center.x, center.y)
                self.window.blit(text_surface, text_rect)

                hextilePips = self.font.render(str(self.pipNumberDict[hextile.value] * "."), True, (0, 0, 0))
                text_rect = hextilePips.get_rect()
                text_rect.center = (center.x + 1, center.y + 8)
                self.window.blit(hextilePips, text_rect)

            if hextile.hasRobber:
                pygame.draw.circle(self.window, (70, 70, 70), center, 20)
                text_surface = self.font.render(str("R"), True, (255, 255, 255))
                text_rect = text_surface.get_rect()
                text_rect.center = (center.x, center.y)
                self.window.blit(text_surface, text_rect)
            # if hextile.resource == "SEA" and hextile.hasPort == True:
            #     pygame.draw.circle(self.window, (0, 0, 255), center, 5)
        
            # if hextile.resource == "SEA":
            #     text_surface = self.font.render(str(len(hextile.vertexChildren)), True, (0, 0, 0))
            #     self.window.blit(text_surface, (center.x -11, center.y -11))
        self.drawPorts()
                
        # drawing vertices
        # for coord, vertex in self.board.vertices.items():
        #     if vertex.hasPort == True:
        #         pygame.draw.circle(self.window, (0, 0, 255), coord, 5)
        #     else:
        #         pygame.draw.circle(self.window, (0, 0, 0), coord, 5)
        
        pygame.display.update()     
    
    def drawPorts(self):
        for coord, hextile in self.board.hexes.items():
            center = hex_to_pixel(self.board.layout, coord)
            if hextile.hasPort == True:
                Colour = self.ColourDict[hextile.portType]
                r = Colour[0]
                g = Colour[1]
                b = Colour[2]
                for vertex in hextile.vertexChildren:
                    if self.board.vertices[vertex].hasPort == True:
                        pygame.draw.line(self.window, (102, 51, 0), center, vertex, 5)
                pygame.draw.circle(self.window, (r, g, b), center, 10)
                

                
