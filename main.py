from simulator.messages import SelfIntroductionMessage
from simulator.services.leader_election_service import LeaderElectionService
from simulator.reader import loadNodes
from simulator.services.message_service import MessageService
import copy
import sys

import argparse
import os
import filecmp

nodes = []
timeline = {}
timeCounter = 0
output_file = None

def saveTimeline():
    global timeline
    timeline[timeCounter] = copy.deepcopy(nodes)

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
    saveTimeline()

    lines = [f"Time: {timeCounter}"]

    for node in nodes:
        status = "Leader" if node.isLeader else "Member"
        lines.append(
            f"Node {node.id}: {status}, Energy: {node.energy}, "
            f"Location: ({node.x}, {node.y}), "
            f"Group: {node.leader.id if node.leader else 'None'}"
        )

    lines.append("=" * 90)

    output = "\n".join(lines)

    print(output)

    output_file.write(output + "\n")

def run_simulation(input_file, output_file_name="output.txt"):
    global nodes, output_file, timeCounter, timeline

    # Reset globals
    nodes = []
    timeline = {}
    timeCounter = 0

    output_file = open(output_file_name, "w")

    nodes = loadNodes(input_file)
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

    while len(nodes) > 0:
        for node in nodes:
            node.processStep(messageService, leaderElectionService)
        takeStep(1)
        removeDeadNodes()
        printStatus()

    output_file.close()

def run_tests():
    input_dir = "tests/input"
    expected_dir = "tests/expected"
    actual_dir = "tests/actual"

    os.makedirs(actual_dir, exist_ok=True)

    passed = 0
    total = 0

    for filename in os.listdir(input_dir):
        if not filename.endswith(".txt"):
            continue

        total += 1

        input_file = os.path.join(input_dir, filename)
        expected_output = os.path.join(expected_dir, filename)
        actual_output = os.path.join(actual_dir, filename)

        run_simulation(input_file, actual_output)

        if filecmp.cmp(actual_output, expected_output, shallow=False):
            print(f"[PASS] {filename}")
            passed += 1
        else:
            print(f"[FAIL] {filename}")

    print(f"\n{passed}/{total} tests passed.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file",
        nargs="?",
        default="input.txt",
        help="Input file"
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Run test suite"
    )

    args = parser.parse_args()

    if args.test:
        run_tests()
    else:
        run_simulation(args.input_file)

if __name__ == "__main__":
    main()
