from simulator.node import Node
import re

def loadNodes(filename="input.txt"):
    nodes = []

    with open(filename, "r") as f:
        content = f.read()

    matches = re.findall(r"\((\d+),(\d+),(\d+)\)", content)

    for i, (x, y, energy) in enumerate(matches):
        nodes.append(
            Node(
                i,
                int(x),
                int(y),
                int(energy)
            )
        )

    return nodes
