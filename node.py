class Node:
    def __init__(self, nodeId, x, y, energy):
        self.id = nodeId
        self.x = x
        self.y = y
        self.energy = energy

        self.alive = True
        self.isLeader = False
        self.groupId = None

    def consume(self, amount):
        self.energy -= amount

        if self.energy <= 0:
            self.energy = 0
            self.alive = False
