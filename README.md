# Shuttle Planner

Assigns people to shuttle buses on a real road network, where:

- each person walks at most `D` metres to a pickup point,
- each bus must carry between its minimum and maximum number of riders, and every bus is used,
- exactly `T` people travel in total.

The allocation is found by modelling the problem as a **flow network with lower bounds**
(circulation with demands) and solving it with a from-scratch Dijkstra and Edmonds-Karp
implementation. A demo runs it on real OpenStreetMap data and draws the result on an
interactive map.

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Real map around Bandar Sunway, Malaysia: 300 people, 5 real bus stops, 10 buses
.venv/bin/python -m shuttle_planner.demo

# Any other area and scenario
.venv/bin/python -m shuttle_planner.demo --lat 3.139 --lon 101.687 --students 1000 --stops 8 --walk 800
```

The demo prints how many riders each bus gets and saves `shuttle_map.html`. Open it in a
browser to see each stop with its walking radius, people coloured by the bus they board, and
people who don't travel in grey.

## Using the solver directly

```python
from bus_allocation import assign

L = 4                                        # locations 0..L-1
roads = [(1, 2, 1), (2, 0, 1), (3, 0, 2)]    # (u, v, length), bidirectional
students = [3, 0, 0]                         # location of each person
buses = [(2, 1, 4), (0, 1, 4)]               # (pickup location, min riders, max riders)

assign(L, roads, students, buses, D=3, T=3)  # [1, 0, 1]
```

`assign` returns a list where entry `i` is the bus person `i` boards (`-1` if they don't
travel), or `None` if no valid allocation exists. `bus_allocation` uses only the Python standard
library.

## How it works

1. **Early checks.** Return `None` straight away if `T > S`, `B > T` (every bus needs at least
   one rider), any bus has `min > max`, or `T` lies outside `[sum of mins, sum of maxes]`.
2. **Reachability.** Run a distance-limited Dijkstra from each pickup point with an indexed
   min-heap. Vertices enter the heap only when first reached, so each run costs
   `O(L + R log L)` even on large or disconnected maps.
3. **Circulation network.** Each edge has bounds `[lower, upper]`:

   ```
   x ──[0,1]──▶ person ──[0,1]──▶ pickup ──[0,∞]──▶ bus ──[min,max]──▶ z
   ▲                                                                   │
   └─────────────────────────────[T,T]─────────────────────────────────┘
   ```

   Each person is linked to **every** pickup within `D`, not just the nearest one. A farther
   bus may need that person to reach its minimum.
4. **Remove lower bounds.** Each lower bound becomes a demand at its endpoints. A super source
   and super sink connect to the vertices with surplus and deficit.
5. **Max-flow.** Edmonds-Karp (BFS Ford-Fulkerson). A valid allocation exists iff the flow
   saturates every demand.
6. **Extract.** Read each traveller's pickup and bus from the edges carrying flow.

### Complexity

With `S` people, `T` travellers, `L` locations, `R` roads, `B ≤ T ≤ S` buses and a constant
number of pickup points:

| Step | Time |
| --- | --- |
| Early checks | `O(S)` |
| Dijkstra from each pickup | `O(L + R log L)` |
| Build flow network (`O(S)` vertices and edges) | `O(S)` |
| Edmonds-Karp (≤ `T` augmenting paths × `O(S)` BFS) | `O(S·T)` |
| **Total** | **`O(S·T + L + R log L)`** |

Auxiliary space is `O(S + L + R)`.

### Performance on real data

Walking network within 1.5 km of Bandar Sunway (2,583 intersections, 3,549 roads):

| People | Buses | Travellers `T` | `assign` time |
| --- | --- | --- | --- |
| 300 | 10 | 153 | 0.01 s |
| 1,000 | 16 | 222 | 0.06 s |
| 3,000 | 24 | 370 | 0.32 s |

## Project structure

```
bus_allocation/        the solver (standard library only)
├── allocator.py       assign(), the entry point
├── city_graph.py      city graph, Dijkstra, building and reading the flow network
├── city.py            Vertex, Edge, Bus
├── min_heap.py        indexed min-heap with decrease-key
├── circulation.py     flow network with lower and upper bounds
└── residual.py        residual network and BFS augmenting paths
shuttle_planner/       real-map demo
├── osm_loader.py      downloads an OpenStreetMap walking network and converts it
└── demo.py            builds a scenario, runs assign, draws the map
tests/
└── test_assign.py     hand-written cases plus a brute-force comparison
```

## Tests

```bash
.venv/bin/python -m pytest
```

Besides hand-written edge cases, the suite checks `assign` against an exhaustive brute-force
solver on 1,500 random small instances. Every returned allocation must be valid, and `None`
is only accepted when no allocation exists.

## Notes

- The people and bus capacities in the demo are randomly generated; roads and bus stops are
  real OpenStreetMap data. 70% of people are placed within walking distance of a stop, as
  riders along a real route would be.
- The solver started as a university algorithms assignment and was later refactored into
  modules, extended to real map data, and given a test suite.

Map data © OpenStreetMap contributors, available under the Open Database License.
