

import json
from turtle import position


# When sent accross a network, world events have a particular 
# serialization convention. They're processed with the help of JSON

# Specifically, the JSON object always has the following keys:
# "ETYPE" the type of the event
# "ORDER" the requested order of the event (is often altered)
# "ARGS" a nested JSON object that specifies the particular arguments


JTAG_EVENT_TYPE = "ETYPE"
JTAG_EVENT_ORDER = "ORDER"
JTAG_EVENT_ARGUMENTS = "ARGS"

JTAG_EVENT_FLOAT2 = "FLOAT2" # Can refer to a list in practice
JTAG_EVENT_INT = "INT" # Can refer to a list in practice

JKEY_EVENT_TYPE_ADDPOSITION = "ADD_POSITION"

class WorldEvent:
    order = None

    def __init__(self, order):
        self.order = order

    def serialize(self) -> str:
        pass


class AddPositionEvent(WorldEvent):

    position = None
    id = None

    def __init__(self, order, position, id):
        super().__init__(order)
        self.position = position
        self.id = id

    def serialize(self):
        serialized_arguments = json.dumps({JTAG_EVENT_FLOAT2 : self.position, JTAG_EVENT_INT : self.id})
        print("I serialzied an event", serialized_arguments)
        return json.dumps({ JTAG_EVENT_TYPE : JKEY_EVENT_TYPE_ADDPOSITION, JTAG_EVENT_ORDER : self.order, JTAG_EVENT_ARGUMENTS : serialized_arguments })


def compose_world_event(world_event_json):

    print("I received as event", world_event_json)
    event_type = world_event_json.get(JTAG_EVENT_TYPE)
    event_order = world_event_json.get(JTAG_EVENT_ORDER)
    event_arguments = world_event_json.get(JTAG_EVENT_ARGUMENTS)

    if event_type and event_order:

        if True: #temproary TODO
        #try: # Assuming everything goes right
            match event_type:
                case str(JKEY_EVENT_TYPE_ADDPOSITION):
                    position = event_arguments.get(JTAG_EVENT_FLOAT2)
                    id = event_arguments
                    return AddPositionEvent(event_order, position, id)

                case _:
                    print("Could not figure out the type of that event!!!")
        """ TODO
         except:
            print("The event was parsed weirdly. What? It literally caused an error")
            return False
        """

    else:
        print("No event type or event order")
    return False