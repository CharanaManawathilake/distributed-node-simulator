class Message:
    def __init__(self, sender_id, message_type, content):
        self.sender_id = sender_id
        self.message_type = message_type
        self.content = content


class SelfIntroductionMessage(Message):
    def __init__(self, node):
        super().__init__(node.id,
                         "SelfIntroduction",
                         {"energy": node.energy, "location": (node.x, node.y)})


class GroupAllocationMessage(Message):
    def __init__(self, leader_id, groups):
        super().__init__(leader_id,
                         "GroupAllocation",
                         groups)

class TransferLeadershipMessage(Message):
    def __init__(self, sender_id, newLeaderId):
        super().__init__(sender_id,
                         "TransferLeadership",
                         {"newLeader": newLeaderId})
