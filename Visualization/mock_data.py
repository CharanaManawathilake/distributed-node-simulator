import random
import copy

class Node:
    def __init__(self, nodeId, x, y, energy):
        self.id = nodeId
        self.x = x
        self.y = y
        self.energy = energy
        self.alive = True
        self.isLeader = False
        self.members = []  # List of nodeIds or node objects belonging to this CH/leader
        self.nodeCounter = 0
        self.msgQueue = []
        self.msgBuffer = []

def generate_mock_data():
    """
    Generates a sample timeline array with 8 nodes over 5 time steps.
    """
    num_steps = 5
    timeline = []
    
    # ----------------------------------------------------
    # Time Step 0: Initial State
    # ----------------------------------------------------
    
    # Group 1 (Leader is Node 0)
    n0 = Node(0, 50, 50, 100)
    n0.isLeader = True
    n0.members = [1, 2]
    
    n1 = Node(1, 40, 60, 100)
    n2 = Node(2, 60, 40, 100)
    
    # Group 2 (Leader is Node 3)
    n3 = Node(3, 140, 140, 100)
    n3.isLeader = True
    n3.members = [4, 5, 6]
    
    n4 = Node(4, 130, 150, 100)
    n5 = Node(5, 150, 130, 100)
    n6 = Node(6, 145, 155, 100)
    
    # Unaffiliated node
    n7 = Node(7, 100, 100, 100)
    
    initial_nodes = [n0, n1, n2, n3, n4, n5, n6, n7]
    timeline.append(copy.deepcopy(initial_nodes))
    
    # ----------------------------------------------------
    # Time Steps 1 to N: Energy depletion and movement
    # ----------------------------------------------------
    for t in range(1, num_steps):
        # Deepcopy the previous state to create the new time step state
        current_state = copy.deepcopy(timeline[-1])
        
        for node in current_state:
            # Simulate energy consumption
            if node.isLeader:
                # Leaders consume more energy
                node.energy -= random.uniform(5.0, 15.0)
            else:
                # Members consume less energy
                node.energy -= random.uniform(1.0, 5.0)
                
            # Cap energy at 0 and update status
            if node.energy <= 0:
                node.energy = 0
                node.alive = False
        
        timeline.append(current_state)
        
    return timeline

if __name__ == "__main__":
    # Test generation
    data = generate_mock_data()
    print(f"Generated timeline with {len(data)} time steps.")
    print(f"Initial nodes: {len(data[0])}")
    print(f"Energy of node 0 at t=0: {data[0][0].energy:.2f}")
    print(f"Energy of node 0 at t=4: {data[4][0].energy:.2f}")
