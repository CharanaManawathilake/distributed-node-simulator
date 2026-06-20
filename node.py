class Node:
    def __init__(self, nodeId, x, y, energy):
        self.id = nodeId
        self.x = x
        self.y = y
        self.energy = energy

        self.alive = True
        self.isLeader = False
        self.members = []
        self.nodeCounter = 0

        self.msgQueue = []
        self.msgBuffer = []

    def consume(self, amount):
        self.energy -= amount

        if self.energy <= 0:
            self.energy = 0
            self.alive = False

    def transmitMsg(self):
        if self.energy < 2:
            return False
        self.consume(2)
        return True
    
    def setLeader(self):
        self.isLeader = True
