from reader import loadNodes

def main():
    nodes = loadNodes("input.txt")
    nodes[0].isLeader = True
    
    for node in nodes:
        print(f"Node {node.id}: ({node.x}, {node.y}), Energy: {node.energy}")

if __name__ == "__main__":    
    main()
