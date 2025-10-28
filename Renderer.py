

import pygame

import macros as M

class Renderer:

    screen = None
    world = None

    def __init__(self, screen, world):
        self.screen = screen
        self.world = world


    def render(self):

        self.screen.fill(M.COLOR_BLACK)
        for position in self.world.positions:
            pygame.draw.circle(self.screen, color=M.COLOR_GREEN, center=(position.x, position.y), radius=M.RADIUS_POSITION)

        pygame.display.update()