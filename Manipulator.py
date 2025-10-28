
import WorldEvent
import World


# Manipulates the world via world events

class Manipulator:

    world = None

    def __init__(self, world):
        self.world = world

    def incorporate(self, event):
        
        match type(event):

            case WorldEvent.AddPositionEvent:
                self.world.add_position(World.Position(*event.position, event.id))
                return

            case _:
                print("Cannot incorporate the event of type", type(event))
                return

    def revert(self, event):

        match type(event):

            case WorldEvent.AddPositionEvent:
                self.world.remove_position_id(event.id)
                return

            case _:
                print("Cannot revert the event of type", type(event))
                return

    