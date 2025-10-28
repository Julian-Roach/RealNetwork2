

import json


# When sent accross a network, world events have a particular 
# serialization convention. They're processed with the help of JSON

# Specifically, the JSON object always has the following keys:
# "ETYPE" the type of the event
# "ORDER" the requested order of the event (is often altered)
# "ARGS" a nested JSON object that specifies the particular arguments

import macros as M

class WorldEvent:
    order = None

    def __init__(self, order):
        self.order = order

    def decompose(self):
        raise NotImplementedError("This world event does not have a decomposition method yet.")


class AddPositionEvent(WorldEvent):

    position = None
    id = None

    def __init__(self, order, position, id):
        super().__init__(order)
        self.position = position
        self.id = id

    def decompose(self):
        serialized_arguments = {M.JTAG_EVENT_FLOAT2 : self.position, M.JTAG_EVENT_INT : self.id}
        return { M.JTAG_EVENT_TYPE : M.JKEY_EVENT_TYPE_ADDPOSITION, M.JTAG_EVENT_ORDER : self.order, M.JTAG_EVENT_ARGUMENTS : serialized_arguments }


def compose_world_event(world_event_json):

    event_type = world_event_json.get(M.JTAG_EVENT_TYPE)
    event_order = world_event_json.get(M.JTAG_EVENT_ORDER)
    event_arguments = world_event_json.get(M.JTAG_EVENT_ARGUMENTS)

    if event_type and event_order:

        try: # Assuming everything goes right
            match event_type:
                case M.JKEY_EVENT_TYPE_ADDPOSITION:

                    position = event_arguments.get(M.JTAG_EVENT_FLOAT2)
                    id = event_arguments
                    return AddPositionEvent(event_order, position, id)

                case _:
                    print("Uknown event type.")
        except:
            print("Could not interpret the world event; an error was thrown.")
            return False

    else:
        print("No event type or event order given.")
    return False