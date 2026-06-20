from messages import SelfIntroductionMessage
from leaderElectionService import LeaderElectionService
from reader import loadNodes
from messageService import MessageService

nodes = []

def takeStep(time=1):
    for node in nodes:
        node.consume(time)

def main():
    nodes = loadNodes("input.txt")
    messageService = MessageService(nodes)
    leaderElectionService = LeaderElectionService(nodes, messageService)
    
    for node in nodes:
        messageService.broadcast(node, SelfIntroductionMessage(node))
    takeStep(1)

    leaderElectionService.initializeLeader()
    takeStep(1)

    while (len(nodes) > 0):
        pass
        takeStep(1)

    # First appointed leader (max energy guy) broadcasts what nodes are clustered and who their leaders are.
    # message : Initialize System : [[leader1, member1-1,member1-2], [leader2, member2-1, member2-2], ...]

    # Leaders sends a heartbeat every x seconds.
    # Leader knows who's alive and who's dead.
    # If the leader dies after all of it's children : do nothing,
    # Else : calculate the suitable leader(s) and broadcast a suitable message.

if __name__ == "__main__":    
    main()

