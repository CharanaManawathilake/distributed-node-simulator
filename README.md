# Distributed Node Simulator

A distributed node simulation framework implementing energy-aware clustering and leader election strategies to maximize network longevity. 

## Features

- **Energy-Aware Leader Election**: Automatically coordinates leader node selections using energy levels and node IDs to optimize resource utilization.
- **Dynamic Distance-Based Clustering**: Clusters node structures into group allocations based on Euclidean distance boundaries (within range of 20 units).
- **Heartbeat & Failover Recovery**: Simulates node health monitoring via heartbeats, triggering automated reelection processes if leader nodes run out of energy.
- **Automated Test Runner**: Built-in comparison test suite comparing simulated outcomes with expected trace logs.

---

## File System Layout

The codebase is organized into a clean, modular structure:

```
distributed-node-simulator/
├── main.py                     # Entry point runner script supporting simulation and test flags
├── input.txt                   # Default simulation input configuration file
├── output.txt                  # Output execution logs
├── simulator/                  # Main simulator package
│   ├── __init__.py
│   ├── messages.py             # Message definitions (Heartbeats, Leader Failures, Allocations)
│   ├── node.py                 # Node state, execution steps, and energy consumption logic
│   ├── reader.py               # Input parser mapping config coordinates to active Node instances
│   └── services/               # System service layer
│       ├── __init__.py
│       ├── leader_election_service.py # Leader election and distance clustering algorithms
│       └── message_service.py         # Network routing and broadcast dispatch handlers
└── tests/                      # Verification suite
    ├── input/                  # Test input scenarios
    ├── expected/               # Ground truth simulator outputs
    └── actual/                 # Generated outputs from the current run
```

---

## Getting Started

### Prerequisites
- Python 3.6+ 
- `matplotlib` (Required for the real-time node visualizer)

To install the necessary dependencies, run:
```bash
pip install matplotlib
```

### Running a Simulation

To run a simulation using the default `input.txt`:
```bash
python main.py
```

To run a simulation using a specific input file:
```bash
python main.py path/to/your/input.txt
```

The simulator prints execution timelines to stdout and logs the complete historical state traces to `output.txt` (or custom generated output files inside `tests/actual/` when testing).

### Running Tests

To run the custom validation test suite built natively into `main.py` (no external test framework required):
```bash
python main.py -t
```
This runs the simulation against all test scripts located in `tests/input/`, comparing the generated logs against `tests/expected/`.

---

## Simulation Mechanics

1. **Self-Introduction Phase**: Nodes broadcast their presence along with location coordinates `(x, y)` and current energy.
2. **Initial Leader Election**: The node with the highest energy (using lowest ID as a tiebreaker) appoints itself as leader and computes clustering.
3. **Clustering Algorithm**:
   - The leader groups all nodes within a 20-unit Euclidean distance.
   - For any unassigned nodes, the node with the highest energy and lowest ID is appointed leader of the next cluster, recursively grouping its neighbors.
   - Group allocations are broadcasted to all nodes.
4. **Heartbeat Protocol**: Leaders consume energy to send heartbeat signals every 4 steps. Member nodes expect heartbeats; if no heartbeat is received within 5 steps, members initiate leader-failover elections.
