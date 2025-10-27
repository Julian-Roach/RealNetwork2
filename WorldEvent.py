



class WorldEvent:
    order = None

    def __init__(self, order):
        self.order = order


class AddPositionEvent(WorldEvent):

    position = None
    id = None

    def __init__(self, order, position, id):
        super().__init__(order)
        self.position = position
        self.id = id