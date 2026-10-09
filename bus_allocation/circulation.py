"""Flow network with lower and upper bounds, reduced to max-flow via a super source/sink."""

from .residual import CirculationResidualNetwork, CirculationForwardEdge, CirculationBackwardEdge


class CirculationFlowNetwork:
    """
    Flow network supporting edges with lower and upper bounds.
    Implements circulation with lower bounds algorithm for bus allocation.
    
    Attributes:
        vertices (list): Fixed-size array of CirculationVertex objects
        edges_list (list): List of all CirculationEdge objects
    """
    
    def __init__(self, num_vertices):
        """
        Function Description:
            Initialize circulation flow network with specified number of vertices.
        
        Input:
            - num_vertices: Number of vertices in the network
        
        Output:
            None 
        
        Time Complexity: O(V) where V is num_vertices
        Time Complexity Analysis: Creates V CirculationVertex objects
        
        Aux Space Complexity: O(V)
        Aux Space Complexity Analysis: Stores V vertices in fixed-size array
        """
        self.vertices = [None] * num_vertices
        for i in range(num_vertices):
            self.vertices[i] = CirculationVertex(i)
        self.edges_list = []
    
    def add_edge(self, u, v, lower, upper):
        """
        Function Description:
            Add edge with lower and upper flow bounds to the network.
        
        Input:
            - u: Source vertex ID
            - v: Destination vertex ID
            - lower: Lower bound (minimum required flow)
            - upper: Upper bound (maximum allowed flow), can be float('inf')
        
        Output:
            None 
        
        Time Complexity: O(1)
        Time Complexity Analysis: Create one edge and adds to vertex's edge list
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Created one CirculationEdge objsct
        """
        edge = CirculationEdge(u, v, lower, upper)
        self.vertices[u].add_edge(edge)
        self.edges_list.append(edge)
    
    def get_real_flow(self, edge):
        """
        Function Description:
            Calculate real flow on edge as flow + lower_bound. 
        
        Input:
            - edge: CirculationEdge object
        
        Output:
            Real flow value (flow + lower_bound)
        
        Time Complexity: O(1)
        Time Complexity Analysis: Simple addition operation
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: No additional space used
        """
        return edge.flow + edge.lower
    
    def convert_to_circulation(self):
        """
        Function Description:
            Convert circulation network with lower bounds to standard max-flow problem by adding 
            super-source (SS) and super-sink (TT). Removes lower bounds from edges and balances flow.
        
        Approach Description:
            1. For each edge with lower > 0: update capacity to (upper - lower), adjust vertex balances
            2. Add super-source SS and super-sink TT vertices
            3. For vertices with positive balance (supply): add edge SS -> vertex
            4. For vertices with negative balance (demand): add edge vertex -> TT
        
        Input:
            None
        
        Output:
            List [SS, TT, total_positive_balance] where:
                - SS: Super-source vertex ID
                - TT: Super-sink vertex ID  
                - total_positive_balance: Required flow from SS to TT for valid circulation
        
        Time Complexity: O(V + E) where V is vertices and E is edges
        Time Complexity Analysis:
            - Computing balances: O(E) to iterate through all edges
            - Adding SS and TT: O(1)
            - Connecting balanced vertices: O(V) to check all vertices
            Total: O(V + E)
        
        Aux Space Complexity: O(V)
        Aux Space Complexity Analysis: balance array stores V vertex balances
        """
        n = len(self.vertices)  # Store original number of vertices before adding SS/TT
        balance = [0] * n  # Fixed-size array initialize balance with 0
        
        # Update capacity and compute balances
        for edge in self.edges_list:
            if edge.lower > 0:
                # update capacity
                edge.capacity = edge.upper - edge.lower
                # Update balances
                balance[edge.u] -= edge.lower
                balance[edge.v] += edge.lower
            else:
                edge.capacity = edge.upper
        
        # Add SS and TT
        SS = len(self.vertices)
        TT = SS + 1
        self.vertices.append(CirculationVertex(SS))
        self.vertices.append(CirculationVertex(TT))
        
        # Connect nodes with non-zero balance and nly loop through original n vertices, not SS/TT
        total_positive_balance = 0
        for i in range(n):  
            if balance[i] > 0:
                # Positive balance = supply, connect from SS
                self.add_edge(SS, i, 0, balance[i])
                total_positive_balance += balance[i]
            elif balance[i] < 0:
                # Negative balance = demand, connect to TT
                self.add_edge(i, TT, 0, -balance[i])
        
        return [SS, TT, total_positive_balance]
    
    def create_residual_network(self, source, sink):
        """
        Function Description:
            Create residual network for Ford-Fulkerson max-flow algorithm.
        
        Input:
            - source: Source vertex ID
            - sink: Sink vertex ID
        
        Output:
            CirculationResidualNetwork object
        
        Time Complexity: O(V + E) where V is vertices and E is edges
        Time Complexity Analysis: Creates residual network with V vertices and processes E edges
        
        Aux Space Complexity: O(V + E)
        Aux Space Complexity Analysis: Residual network stores V vertices and 2E residual edges (forward + backward)
        """
        residual = CirculationResidualNetwork(len(self.vertices), source, sink)
        
        for vertex in self.vertices:
            for edge in vertex.edges:
                u_id = vertex.id
                v_id = edge.v
                
                # Forward edge (remaining capacity)
                forward = CirculationForwardEdge(edge, v_id)
                residual.vertices[u_id].add_edge(forward)
                
                # Backward edge (reverse flow)
                backward = CirculationBackwardEdge(edge, u_id)
                residual.vertices[v_id].add_edge(backward)
        
        return residual
    
    def ford_fulkerson(self, source, sink):
        """
        Function Description:
            Run Edmonds-Karp (BFS-based Ford-Fulkerson) to get maximum flow.
        
        Input:
            - source: Source vertex ID (SS)
            - sink: Sink vertex ID (TT)
        
        Output:
            Maximum flow value from source to sink
        
        Time Complexity: O(max_flow · (V + E)) for unit capacity networks, which is O(T · (S + B)) in our case
        Time Complexity Analysis:
            - For unit capacity networks, there are at most max_flow augmenting paths
            - Each BFS takes O(V + E) time
            - In our network: max_flow = T, V = O(S + B), E = O(S + B)
            Total: O(T · (S + B))
        
        Aux Space Complexity: O(V + E)
        Aux Space Complexity Analysis: Residual network stores V vertices and 2E residual edges
        """
        total_flow = 0
        residual = self.create_residual_network(source, sink)
        
        while residual.has_AugmentingPath():
            path = residual.get_AugmentingPath()
            if len(path) == 0:
                break
            
            # Find bottleneck
            bottleneck = min(edge.weight for edge in path)
            
            # Augment flow
            for edge in path:
                edge.augment(bottleneck)
            
            total_flow += bottleneck
        
        return total_flow


class CirculationVertex:
    """
    class Description:
        Vertex in circulation flow network.
    
    Attributes:
        - id: Vertex id
        - edges: List of outgoing CirculationEdge objects
    """
    
    def __init__(self, vertex_id):
        """
        Function Description:
            Initialize circulation vertex.
        
        Input:
            - vertex_id: Vertex identifier
        
        Output:
            None (creates CirculationVertex object)
        
        Time Complexity: O(1)
        Time Complexity Analysis: Simple attribute initialization
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: attributes stored
        """
        self.id = vertex_id
        self.edges = []
    
    def add_edge(self, edge):
        """
        Function Description:
            Add outgoing edge to this vertex.
        
        Input:
            - edge: CirculationEdge object
        
        Output:
            None 
        
        Time Complexity: O(1)
        Time Complexity Analysis: List append is amortized O(1)
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Single edge reference added
        """
        self.edges.append(edge)


class CirculationEdge:
    """
    Class Description:
        Edge in circulation flow network with lower and upper flow bounds.
    
    Attributes:
        - u: Source vertex id
        - v: Destination vertex id
        - lower: Lower bound (minimum required flow)
        - upper: Upper bound (maximum allowed flow), can be float('inf')
        - capacity: Available capacity (upper - lower after conversion)
        - flow: Current flow on this edge
    """
    
    def __init__(self, u, v, lower, upper):
        """
        Function Description:
            Initialize edge with flow bounds.
        
        Input:
            - u: Source vertex id
            - v: Destination vertex id
            - lower: Lower bound (minimum flow)
            - upper: Upper bound (maximum capacity), can be float('inf')
        
        Output:
            None (creates CirculationEdge object)
        
        Time Complexity: O(1)
        Time Complexity Analysis: Simple attribute initialization
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Six attributes stored
        """
        self.u = u
        self.v = v
        self.lower = lower
        self.upper = upper
        self.capacity = upper  # will be adjusted during conversion
        self.flow = 0
