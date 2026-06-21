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
        self.inElection = False

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
        leaderFailureMsgs = [msg for msg in self.msgQueue if msg.message_type == "LeaderFailure"]
        groupAllocationMsgs = [msg for msg in self.msgQueue if msg.message_type == "GroupAllocation"]
        heartbeatMsgs = [msg for msg in self.msgQueue if msg.message_type == "Heartbeat"]
        
        if self.inElection:
            if len(leaderFailureMsgs) == 0:
                self.inElection = False
                self.isLeader = True
                self.leader = self
                self.members = []
                self.nodeCounter = 0
                return
            else:
                leaderElectionService.appointNewLeader(self, leaderFailureMsgs, messageService)
                self.inElection = False
                return

        containedHeartbeat = len(heartbeatMsgs) > 0

        for msg in groupAllocationMsgs:
            for group in msg.content:
                if self in group:
                    self.members = [node for node in group if node.id != self.id]
                    if self == group[0]:
                        self.isLeader = True
                        self.leader = self
                    else:
                        self.leader = group[0]

        if not self.isLeader:
            if not containedHeartbeat:
                self.nodeCounter += 1
            else:
                self.nodeCounter = 0
        else:
            self.nodeCounter += 1

        if self.nodeCounter >= 5 and not self.isLeader:
            self.leader = None
            self.inElection = True
            messageService.broadcastToMembers(self, LeaderFailureMessage(self))
            self.nodeCounter = 2

        if self.isLeader and self.nodeCounter >= 4:
            self.nodeCounter = 0
            messageService.broadcastToMembers(self, HeartbeatMessage(self.id))
