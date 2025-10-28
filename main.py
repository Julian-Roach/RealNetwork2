

# TODO: Why is it spamming through the network? That's weird... it must not flush some list probably.
# TODO: ^^^ the server especially, perhaps only.

# TODO: The server doesn't consider the event but the client seems to receive the nothingness ... and then not receive server events?

import pygame

import World
import EventManager
import Renderer
import WorldEvent

import random

pygame.init()

import macros as M


def main():

    running = True

    screen = pygame.display.set_mode(M.SCREEN_SIZE)

    world = World.World()
    renderer = Renderer.Renderer(screen, world)

    event_manager = None

    print("\n" * 30)
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
                    event_manager.add_local_event(WorldEvent.AddPositionEvent(1, (random.randrange(0,M.SCREEN_SIZE[0]),random.randrange(0,M.SCREEN_SIZE[1])),len(world.positions)))

                if event.key == pygame.K_F1:
                    event_manager.manipulator.revert(event_manager.history[-1])

        event_manager.update()
        renderer.render()

main()

