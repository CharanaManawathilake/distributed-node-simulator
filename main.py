from messages import SelfIntroductionMessage
from leaderElectionService import LeaderElectionService
from reader import loadNodes
from messageService import MessageService

nodes = []
timeline = []
timeCounter = 0

def takeStep(time=1):
    global timeCounter
    timeCounter += time
    for node in nodes:
        node.consume(time)
        node.msgQueue = node.msgBuffer
        node.msgBuffer = []

def removeDeadNodes():
    global nodes
    nodes[:] = [node for node in nodes if node.alive]

def printStatus():
    print("=========================================")
    print(f"Time: {timeCounter}")
    for node in nodes:
        status = "Leader" if node.isLeader else "Member"
        print(f"Node {node.id}: {status}, Energy: {node.energy}, Location: ({node.x}, {node.y}), Group : {node.leader.id if node.leader else 'None'}")
    print("=========================================")

def main():
    global nodes
    nodes = loadNodes("input.txt")
    messageService = MessageService(nodes)
    leaderElectionService = LeaderElectionService(nodes, messageService)

    printStatus()
    
    for node in nodes:
        messageService.broadcast(node, SelfIntroductionMessage(node))
    takeStep(1)
    printStatus()

    leaderElectionService.initializeLeader()
    takeStep(1)
    printStatus()

    while (len(nodes) > 0):
        for node in nodes:
            node.processStep(messageService, leaderElectionService)
        takeStep(1)
        removeDeadNodes()
        printStatus()

if __name__ == "__main__":    
    main()

