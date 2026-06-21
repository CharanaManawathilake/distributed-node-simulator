from messages import HeartbeatMessage, LeaderFailureMessage

class Node:
    def __init__(self, nodeId, x, y, energy):
        self.id = nodeId
        self.x = x
        self.y = y
        self.energy = energy

        self.alive = True
        self.isLeader = False
        self.members = []
        self.leader = None
        self.nodeCounter = 0

        self.msgQueue = []
        self.msgBuffer = []

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

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

    def processStep(self, messageService, leaderElectionService):
        leaderFailureMsgs = []
        for msg in self.msgQueue:
            if msg.message_type == "LeaderFailure":
                leaderFailureMsgs.append(msg)
        if len(leaderFailureMsgs) > 0:
            leaderElectionService.initializeLeader("LeaderFailure")
            return

        containedHeartbeat = False
        for msg in self.msgQueue:
            if msg.message_type == "GroupAllocation":
                for group in msg.content:
                    if self in group:
                        self.members = [node for node in group if node.id != self.id]
                        if self == group[0]:
                            self.isLeader = True
                            self.leader = self
                        else:
                            self.leader = group[0]
            elif msg.message_type == "Heartbeat":
                containedHeartbeat = True

        if not containedHeartbeat and not self.isLeader:
            self.nodeCounter += 1
        else:
            self.nodeCounter = 0

        if self.nodeCounter >= 5 and not self.isLeader:
            messageService.broadcastToGroup(self, LeaderFailureMessage(self))
            self.nodeCounter = 2

        if self.isLeader:
            messageService.broadcastToGroup(self, HeartbeatMessage(self.id))
