class MessageService:
    def __init__(self, nodes):
        self.nodes = nodes

    def broadcast(self, sender, msg):
        if not sender.transmitMsg():
            return
        
        for node in self.nodes:
            if node.id != sender.id:
                node.msgBuffer.append(msg)

    def broadcastToGroup(self, sender, msg, groups):
        if not sender.transmitMsg():
            return
        
        for i in groups:
            for node in i:
                if node.id != sender.id:
                    node.msgBuffer.append(msg)

    def broadcastToMembers(self, sender, msg):
        if not sender.transmitMsg():
            return
        
        for node in sender.members:
            if node.id != sender.id:
                node.msgBuffer.append(msg)
