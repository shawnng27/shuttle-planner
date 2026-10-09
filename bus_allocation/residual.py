"""Residual network and BFS augmenting paths for Ford-Fulkerson (Edmonds-Karp)."""

from collections import deque


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
        Residual network for Ford-Fulkerson algorithm on circulation flow network.
    
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
            Reset all vertices to prepare for new BFS search.
        
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
    
    def has_AugmentingPath(self):
        """
        Function Description:
            Use BFS to check if augmenting path exists from source to destination.
        
        Input:
            None
        
        Output:
            True if augmenting path exists, False otherwise
        
        Time Complexity: O(V + E) where V is vertices and E is residual edges
        Time Complexity Analysis: Standard BFS traversal
        
        Aux Space Complexity: O(V)
        Aux Space Complexity Analysis: BFS queue can hold up to V vertices
        """
        self.reset()
        discovered = deque()
        source = self.vertices[self.source]

        discovered.append(source)
        source.discovered = True

        while len(discovered) > 0:
            u = discovered.popleft()
            u.visited = True
            # If we reached the destination, return True
            if u.id == self.destination:
                return True
            
            for edge in u.edges:
                v = self.vertices[edge.v]
                # only traverse when edge > 0 and not discovered:
                if edge.weight > 0 and not v.discovered:
                    v.discovered = True
                    v.previous = (u.id, edge)
                    discovered.append(v)

        return False

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
        Vertex in residual network for Ford-Fulkerson algorithm.
    
    Attributes:
        - id: Vertex identifier
        - edges: List of residual edges (forward/backward)
        - visited: visited flag
        - discovered: discovered flag
        - previous: Tuple (previous_vertex_id, edge) for path reconstruction
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
