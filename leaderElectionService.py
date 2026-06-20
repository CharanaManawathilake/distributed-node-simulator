from messages import GroupAllocationMessage
from node import Node
import math

class LeaderElectionService:
    def __init__(self, nodes, messageService):
        self.nodes = nodes
        self.messageService = messageService

    def initializeLeader(self):
        for node in self.nodes:
            maxEnergy = -1
            id = -1
            tempNodes = []
            for msg in node.msgQueue:
                if msg.message_type == "SelfIntroduction":
                    energy = msg.content["energy"]
                    if energy > maxEnergy:
                        maxEnergy = energy
                        id = msg.sender_id
                    if energy == maxEnergy:
                        id = min(id, msg.sender_id)
                    tempNodes.append(Node(msg.sender_id, msg.content["location"][0], msg.content["location"][1], energy))
            if maxEnergy < node.energy or (maxEnergy == node.energy and node.id < id):
                node.setLeader()
                groups = self._calculateGroups(node, tempNodes)
                self.messageService.broadcast(node, GroupAllocationMessage(node.id, groups))

    def _calculateGroups(self, leader, tempNodes):
        remaining = tempNodes.copy()
        groups = []

        while True:
            cluster = [leader]

            members = []
            for node in remaining:
                distance = math.sqrt(
                    (leader.x - node.x) ** 2 +
                    (leader.y - node.y) ** 2
                )

                if distance <= 20:
                    cluster.append(node)
                    members.append(node)

            for node in members:
                remaining.remove(node)

            groups.append(cluster)

            # No more nodes left
            if not remaining:
                break

            leader = max(
                remaining,
                key=lambda n: (n.energy, -n.id)
            )
            remaining.remove(leader)

        return groups
