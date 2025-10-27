

import pygame


RADIUS_POSITION = 10
COLOR_BLACK = (0,0,0)
COLOR_GREEN = (255,0,0)

class Renderer:

    screen = None
    world = None

    def __init__(self, screen, world):
        self.screen = screen
        self.world = world


    def render(self):

        self.screen.fill(COLOR_BLACK)
        for position in self.world.positions:
            pygame.draw.circle(self.screen, color=COLOR_GREEN, center=(position.x, position.y), radius=RADIUS_POSITION)

        pygame.display.update()