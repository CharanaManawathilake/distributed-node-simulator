from math import sqrt

def euclideanDistance(node1, node2):
    return sqrt(
        (node1.x - node2.x) ** 2 +
        (node1.y - node2.y) ** 2
    )
