



class Position:

    x = None
    y = None
    id = None

    def __init__(self, x,y,id):
        self.x = x
        self.y = y
        self.id = id

        


class World:

    positions = []


    def add_position(self, position):
        self.positions.append(position)

    def remove_position_id(self, id):
        for position in self.positions:
            if position.id == id:
                self.positions.remove(position)
