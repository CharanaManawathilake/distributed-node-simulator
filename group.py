class Group:
    def __init__(self, groupId, leader):
        self.id = groupId
        self.leader = leader
        self.members = [leader]
