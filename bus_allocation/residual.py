"""Residual network and shortest (min-cost) augmenting paths for successive shortest paths."""

from .min_heap import MinHeap


class CirculationForwardEdge:
    """
    class Description:
        Forward residual edge representing remaining capacity in original edge direction.
    
    Attributes:
        - edge: Reference to original CirculationEdge
        - v: Destination vertex id
    """
    
    def __init__(self, edge, v):
        """
        Function Description:
            Initialize forward residual edge.
        
        Input:
            - edge: Original CirculationEdge
            - v: Destination vertex ID
        
        Output:
            None (creates CirculationForwardEdge object)
        
        Time Complexity: O(1)
        Time Complexity Analysis: Simple attribute assignment
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Two references stored
        """
        self.edge = edge
        self.v = v

    @property
    def weight(self):
        """
        Function Description:
            Get remaining capacity on forward edge (capacity - flow).
            Uses @property to allow attribute-like access (edge.weight) while dynamically 
            computing the current value, ensuring it updates after each augmentation.
        
        Returns:
            int/float: Available capacity
        
        Time Complexity: O(1)
        Time Complexity Analysis: Simple subtraction
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: No additional space
        """
        return self.edge.capacity - self.edge.flow

    @property
    def cost(self):
        """
        Function Description:
            Get the cost per unit of flow pushed along the original edge.

        Output:
            Cost of the original edge

        Time Complexity: O(1)
        Time Complexity Analysis: Simple attribute access

        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: No additional space
        """
        return self.edge.cost

    def augment(self, flow_amount):
        """
        Function Description:
            Augment flow in forward direction by increasing edge flow.
        
        Input:
            - flow_amount: Amount of flow to add
        
        Output:
            None (modifies edge.flow)
        
        Time Complexity: O(1)
        Time Complexity Analysis: Simple addition
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: No additional space
        """
        self.edge.flow += flow_amount


class CirculationBackwardEdge:
    """
    Class Description:
        Backward residual edge representing flow that can be reversed (pushed back).
    
    Attributes:
        - edge: Reference to original CirculationEdge
        - v: Destination vertex id (in reverse direction)
    """
    
    def __init__(self, edge, v):
        """
        Function Description:
            Initialize backward residual edge.
        
        Input:
            - edge: Original CirculationEdge
            - v: Destination vertex ID in reverse direction
        
        Output:
            None (creates CirculationBackwardEdge object)
        
        Time Complexity: O(1)
        Time Complexity Analysis: Simple attribute assignment
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Two references stored
        """
        self.edge = edge
        self.v = v

    @property
    def weight(self):
        """
        Function Description:
            Get available flow to push back (current flow on edge).
            Uses @property to allow attribute-like access (edge.weight) while dynamically 
            computing the current value, ensuring it updates after each augmentation.
        
        Input:
            None
        
        Output:
            Current flow that can be reversed
        
        Time Complexity: O(1)
        Time Complexity Analysis: Simple attribute access
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: No additional space
        """
        return self.edge.flow

    @property
    def cost(self):
        """
        Function Description:
            Get the cost per unit of flow pushed back, which refunds the original edge's cost.

        Output:
            Negated cost of the original edge

        Time Complexity: O(1)
        Time Complexity Analysis: Simple negation

        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: No additional space
        """
        return -self.edge.cost

    def augment(self, flow_amount):
        """
        Function Description:
            Augment flow in backward direction by decreasing edge flow (reverse flow).
        
        Input:
            - flow_amount: Amount of flow to push back
        
        Output:
            None (modifies edge.flow)
        
        Time Complexity: O(1)
        Time Complexity Analysis: Simple subtraction
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: No additional space
        """
        self.edge.flow -= flow_amount


class CirculationResidualNetwork:
    """
    Class Description:
        Residual network for successive shortest paths on the circulation flow network.
    
    Attributes:
        - vertices: List of ResidualVertex objects
        - source: Source vertex ID (SS)
        - destination: Sink vertex ID (TT)
    """
    
    def __init__(self, num_vertices, source, destination):
        """
        Function Description:
            Initialize residual network with specified vertices.
        
        Input:
            - num_vertices: Number of vertices in network
            - source: Source vertex ID
            - destination: Destination vertex ID
        
        Output:
            None (creates CirculationResidualNetwork object)
        
        Time Complexity: O(V) where V is num_vertices
        Time Complexity Analysis: Creates V ResidualVertex objects
        
        Aux Space Complexity: O(V)
        Aux Space Complexity Analysis: Stores V vertices in array
        """
        self.vertices = [None] * num_vertices 
        self.source = source
        self.destination = destination
        for i in range(num_vertices):
            self.vertices[i] = ResidualVertex(i)
    
    def reset(self):
        """
        Function Description:
            Reset all vertices to prepare for a new Dijkstra search. Potentials are kept.
        
        Input:
            None
        
        Output:
            None (resets vertex attributes)
        
        Time Complexity: O(V) where V is number of vertices
        Time Complexity Analysis: Iterates through all vertices once
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Only modifies existing vertex attributes
        """
        for vertex in self.vertices:
            vertex.discovered = False
            vertex.visited = False
            vertex.previous = None
            vertex.distance = float('inf')
    
    def has_AugmentingPath(self):
        """
        Function Description:
            Find a cheapest augmenting path from source to destination, then update the vertex
            potentials so every residual edge keeps a non-negative reduced cost.

        Approach Description:
            Run Dijkstra on reduced costs, cost(u, v) + potential(u) - potential(v), which are
            non-negative while potentials are valid (all zero at the start, since every original
            edge cost is non-negative). Stop once the destination is served, then add
            min(distance, destination distance) to every potential. This keeps all reduced
            costs non-negative and makes every edge on the shortest path cost 0 reduced, so the
            reverse edges created by augmenting along it are non-negative too.
        
        Input:
            None
        
        Output:
            True if augmenting path exists, False otherwise
        
        Time Complexity: O((V + E) log V) where V is vertices and E is residual edges
        Time Complexity Analysis: Dijkstra with an indexed min-heap; each edge causes at most
            one O(log V) add or decrease-key, plus an O(V) reset and potential update
        
        Aux Space Complexity: O(V)
        Aux Space Complexity Analysis: MinHeap array and index_map of size V
        """
        self.reset()
        source = self.vertices[self.source]
        source.distance = 0
        source.discovered = True
        discovered_minheap = MinHeap(len(self.vertices))
        discovered_minheap.add((source.id, 0))

        while len(discovered_minheap) > 0:
            u_id, u_distance = discovered_minheap.get_min()
            u = self.vertices[u_id]
            u.visited = True
            # Distances past the destination are not needed for this path
            if u_id == self.destination:
                break

            for edge in u.edges:
                v = self.vertices[edge.v]
                # only traverse edges with remaining capacity to unfinalized vertices
                if edge.weight > 0 and not v.visited:
                    new_distance = u_distance + edge.cost + u.potential - v.potential
                    if new_distance < v.distance:
                        v.distance = new_distance
                        v.previous = (u_id, edge)
                        if not v.discovered:
                            v.discovered = True
                            discovered_minheap.add((v.id, new_distance))
                        else:
                            discovered_minheap.update(v.id, new_distance)

        destination = self.vertices[self.destination]
        if not destination.visited:
            return False

        # Unserved vertices are at least as far as the destination, so cap their shift there
        for vertex in self.vertices:
            vertex.potential += min(vertex.distance, destination.distance)
        return True

    def get_AugmentingPath(self):
        """
        Function Description:
            Reconstruct augmenting path from source to destination using previous pointers.
        
        Input:
            None
        
        Output:
            List of edges forming the path (empty if no path exists)
        
        Time Complexity: O(V) where V is number of vertices
        Time Complexity Analysis: Traces back path from destination to source
        
        Aux Space Complexity: O(V)
        Aux Space Complexity Analysis: Path can contain up to V edges
        """
        if self.vertices[self.destination].previous is None:
            return []
        
        path = []
        node = self.vertices[self.destination]

        while node.previous is not None:
            parent_id, residual_edge = node.previous
            path.append(residual_edge)
            node = self.vertices[parent_id]

        path.reverse()
        return path


class ResidualVertex:
    """
    Function Description:
        Vertex in residual network for successive shortest paths.
    
    Attributes:
        - id: Vertex identifier
        - edges: List of residual edges (forward/backward)
        - visited: visited flag
        - discovered: discovered flag
        - previous: Tuple (previous_vertex_id, edge) for path reconstruction
        - distance: Reduced-cost distance from the source in the current search
        - potential: Johnson potential that keeps reduced edge costs non-negative
    """
    def __init__(self, id):
        """
        Function Description:
            Initialize residual vertex.
        
        Input:
            - id: Vertex identifier
        
        Output:
            None 
        
        Time Complexity: O(1)
        Time Complexity Analysis: Simple attribute initialization
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Fixed number of attributes
        """
        self.id = id
        self.edges = []
        self.visited = False
        self.discovered = False
        self.previous = None
        self.distance = float('inf')
        self.potential = 0

    def add_edge(self, edge):
        """
        Function Description:
            Add residual edge to this vertex.
        
        Input:
            - edge: CirculationForwardEdge or CirculationBackwardEdge
        
        Output:
            None 
        
        Time Complexity: O(1)
        Time Complexity Analysis: List append is amortized O(1)
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Single edge reference added
        """
        self.edges.append(edge)
