

# TODO: Why is it spamming through the network? That's weird... it must not flush some list probably.

import pygame

import World
import EventManager
import Renderer
import WorldEvent

import random

pygame.init()


SCREEN_SIZE = (800,400)

def main():

    running = True

    screen = pygame.display.set_mode(SCREEN_SIZE)

    world = World.World()
    renderer = Renderer.Renderer(screen, world)

    event_manager = None

    mode = input("s for 'server'; 'c' for client; 'o' for offline >> ").lower()

    if mode == "s":
        event_manager = EventManager.EventManager(world, authoritative=True, serving=True)
    if mode == "c":
        event_manager = EventManager.EventManager(world, authoritative=False, serving=False)
    if mode == "o":
        event_manager = EventManager.EventManager(world)

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print(event_manager.history)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    event_manager.add_local_event(WorldEvent.AddPositionEvent(0, (random.randrange(0,SCREEN_SIZE[0]),random.randrange(0,SCREEN_SIZE[1])),len(world.positions)))

                if event.key == pygame.K_F1:
                    event_manager.manipulator.revert(event_manager.history[-1])

        event_manager.update()
        renderer.render()

main()

