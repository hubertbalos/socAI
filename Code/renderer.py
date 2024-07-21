import pygame
from game import Game
from hexlib import *
import numpy as np

class Renderer():
    """
    Renders the state of the game to the screen
    """
    def __init__(self):
        print("Renderer initialising")

        pygame.display.set_caption("Settlers of Catan Engine")

        self.WINDOW_SIZE = (750, 910)
        self.window = pygame.display.set_mode(self.WINDOW_SIZE)
        self.game = Game(self.WINDOW_SIZE)
        self.board = self.game.get_board()

        self.RESOURCE_COLOUR_DICT = {
            "ORE":(160,160,160), 
            "WHEAT":(255,255,0), 
            "WOOD":(0,102,0), 
            "BRICK":(153,0,0), 
            "SHEEP":(204,255,153), 
            "DESERT":(255,229,204),
            "SEA":(153,204,255),
            "3:1":(0,0,0)
        }

        self.PLAYER_COLOUR_DICT = {
            "RED":(255,0,0),
            "WHITE":(255,255,255),
            "ORANGE":(255,128,0),
            "BLUE":(0,0,255)
        }
        
        self.PIP_NUMBER_DICT = {2:1, 3:2, 4:3, 5:4, 6:5, 8:5, 9:4, 10:3, 11:2, 12:1}
        
        self.font = pygame.font.SysFont(None, 40)

        self.displayState()

    def displayState(self):
        # background colour
        self.window.fill((102, 178, 255))
        # drawing hexes
        for coord, hextile in self.board.hexes.items():
            corners = polygon_corners(self.board.layout, coord)
            center = hex_to_pixel(self.board.layout, coord)
            hextile_colour = self.RESOURCE_COLOUR_DICT[hextile.resource]
            r = hextile_colour[0]
            g = hextile_colour[1]
            b = hextile_colour[2]
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

                hextilePips = self.font.render(str(self.PIP_NUMBER_DICT[hextile.value] * "."), True, (0, 0, 0))
                text_rect = hextilePips.get_rect()
                text_rect.center = (center.x + 1, center.y + 8)
                self.window.blit(hextilePips, text_rect)

            if hextile.has_robber:
                pygame.draw.circle(self.window, (70, 70, 70), center, 20)
                text_surface = self.font.render(str("R"), True, (255, 255, 255))
                text_rect = text_surface.get_rect()
                text_rect.center = (center.x, center.y)
                self.window.blit(text_surface, text_rect)

        self.drawPorts()
        self.drawPlayerRoads()
        self.drawPlayerBuildings()
        
        pygame.display.update()     
    
    def drawPorts(self):
        for coord, hextile in self.board.hexes.items():
            center = hex_to_pixel(self.board.layout, coord)
            if hextile.has_port:
                Colour = self.RESOURCE_COLOUR_DICT[hextile.port_type]
                r = Colour[0]
                g = Colour[1]
                b = Colour[2]
                for vertex in hextile.vertex_children:
                    if self.board.vertices[vertex].has_port:
                        pygame.draw.line(self.window, (102, 51, 0), center, vertex, 5)
                pygame.draw.circle(self.window, (r, g, b), center, 10)
    
    def drawPlayerRoads(self):
        for id, edge in self.board.edges.items():
            if edge.has_road:
                Colour = self.PLAYER_COLOUR_DICT[edge.owner]
                r = Colour[0]
                g = Colour[1]
                b = Colour[2]
                pygame.draw.line(self.window, (r, g, b), edge.vertex_parents[0], edge.vertex_parents[1], 8)
    
    def drawPlayerBuildings(self):
        for coord, vertex in self.board.vertices.items():
            if vertex.has_settlement:
                Colour = self.PLAYER_COLOUR_DICT[vertex.owner]
                r = Colour[0]
                g = Colour[1]
                b = Colour[2]
                pygame.draw.circle(self.window, (r, g, b), coord, 13)
