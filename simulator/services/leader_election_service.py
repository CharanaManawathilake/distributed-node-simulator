from simulator.messages import GroupAllocationMessage
from simulator.node import Node
import math

class LeaderElectionService:
    def __init__(self, nodes, messageService):
        self.nodes = nodes
        self.messageService = messageService

    def initializeLeader(self):
        for n in self.nodes:
            n.isLeader = False
            n.leader = None
            n.members = []

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
                    actual_node = next((n for n in self.nodes if n.id == msg.sender_id), None)
                    if actual_node:
                        tempNodes.append(actual_node)
            if maxEnergy < node.energy or (maxEnergy == node.energy and node.id < id):
                node.setLeader()
                groups = self._calculateGroups(node, tempNodes)
                node.leader = node
                node.members = [n for n in groups[0] if n.id != node.id]
                self.messageService.broadcast(node, GroupAllocationMessage(node.id, groups))

    def appointNewLeader(self, selfNode, leaderFailureMsgs, messageService):
        maxEnergy = -1
        id = -1
        tempNodes = []
        for msg in leaderFailureMsgs:
            energy = msg.content["energy"]
            if energy > maxEnergy:
                maxEnergy = energy
                id = msg.sender_id
            if energy == maxEnergy:
                id = min(id, msg.sender_id)
            actual_node = next((n for n in self.nodes if n.id == msg.sender_id), None)
            if actual_node:
                tempNodes.append(actual_node)

        self_original_energy = selfNode.energy + 3
        if maxEnergy < self_original_energy or (maxEnergy == self_original_energy and selfNode.id < id):
            selfNode.setLeader()
            groups = self._calculateGroups(selfNode, tempNodes)
            selfNode.leader = selfNode
            selfNode.members = [n for n in groups[0] if n.id != selfNode.id]
            messageService.broadcastToGroup(selfNode, GroupAllocationMessage(selfNode.id, groups), groups)

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
