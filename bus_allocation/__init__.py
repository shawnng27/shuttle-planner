"""
Allocates people to capacity-constrained buses within walking distance, using a
circulation network with lower bounds.

Modules:
    - allocator:   assign(), the entry point
    - city_graph:  Graph, the city road network and circulation network builder
    - city:        Vertex, Edge and Bus entities
    - min_heap:    indexed MinHeap used by Dijkstra
    - circulation: CirculationFlowNetwork with lower/upper bounds
    - residual:    residual network used by Ford-Fulkerson
"""

from .allocator import assign

__all__ = ["assign"]
