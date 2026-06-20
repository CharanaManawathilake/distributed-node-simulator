class MessageService:
    def __init__(self, nodes):
        self.nodes = nodes

    def broadcast(self, sender, msg):
        if not sender.transmitMsg():
            return
        
        for node in self.nodes:
            if node.id != sender.id:
                node.msgBuffer.append(msg)
