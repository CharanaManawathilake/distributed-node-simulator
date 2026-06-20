import messageService


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

    def processStep(self):
        containedHeartbeat = False
        for msg in self.msgQueue:
            if msg.message_type == "GroupAllocation":
                for group in msg.content:
                    if self in group:
                        self.members = [node for node in group if node.id != self.id]
            elif msg.message_type == "Heartbeat":
                containedHeartbeat = True

        if not containedHeartbeat and not self.isLeader:
            self.nodeCounter += 1
        else:
            self.nodeCounter = 0

        if self.nodeCounter >= 5 and not self.isLeader:
            messageService.broadcastToGroup(self)
            self.nodeCounter = 2

        
