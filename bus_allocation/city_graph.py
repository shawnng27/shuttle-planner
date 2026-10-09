"""City road network: Dijkstra from pickups and construction of the circulation network."""

from .min_heap import MinHeap
from .city import Vertex, Edge, Bus
from .circulation import CirculationFlowNetwork


class Graph:
    """
    class Description:
        Graph representing the city road network with locations, roads, students, and buses.
   
    Attributes:
        - locations: List of Vertex objects representing city locations
    """
    def __init__(self, loacation_number: int):
        """
        Function Description:
            Initialize city graph with specified number of locations.
        
        Input:
            - loacation_number: Number of locations (vertices) in the city
        
        Output:
            None 
        
        Time Complexity: O(L) where L is number of locations
        Time Complexity Analysis: Creates L Vertex objects
        
        Aux Space Complexity: O(L)
        Aux Space Complexity Analysis: Stores L vertices in array
        """
        self.locations = [None] * loacation_number
        for i in range(loacation_number):
            self.locations[i] = Vertex(i)
    
    def reset(self):
        """
        Function Description:
            Reset all location properties to initial state.
        
        Input:
            None
        
        Output:
            None (resets vertex attributes)
        
        Time Complexity: O(L) where L is number of locations
        Time Complexity Analysis: Iterates through all vertices once
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Only modifies existing vertex attributes
        """
        for location in self.locations:
            location.discovered = False
            location.visited = False
            location.distance = 0

    def add_edges(self, edges):
        """
        Function Description:
            Add undirected (two way direction) roads to the city graph.
        
        Input:
            - edges: List of tuples (u, v, w) representing roads between locations u and v with distance w
        
        Output:
            None 
        
        Time Complexity: O(R) where R is the number of roads
        Time Complexity Analysis: Iterates through each road once and creates two edges (bidirectional)
        
        Aux Space Complexity: O(R)
        Aux Space Complexity Analysis: Creates 2R edge objects stored in vertex adjacency lists
        """
        for edge in edges:
            u = edge[0]
            v = edge[1]
            w = edge[2]

            # forward edge u -> v
            forward_edge = Edge(u,v,w)
            self.locations[u].add_edges(forward_edge)

            # forward edge u -> v
            backward_edge = Edge(v,u,w)
            self.locations[v].add_edges(backward_edge)

    def add_student_to_location(self, students):
        """
        Function Description:
            Map each student to their location in the city graph.
        
        Input:
            - students: List where students[i] is the location ID of student i
        
        Output:
            None 
        
        Time Complexity: O(S) where S is the number of students
        Time Complexity Analysis: Iterates through each student once
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Students are added to existing vertex lists (already counted in graph space)
        """
        for student_index in range(len(students)):
            location = students[student_index]
            self.locations[location].add_student(student_index)

    def add_bus_to_location(self, buses):
        """
        Add buses into the city

        Args:
            buses: List of tuples (pickup_location, min_capacity, max_capacity)
        
        Output:
            Time Complexity: O(B) where B is the number of buses
            Time Complexity Analysis: loop through the buses list and add each of them to the vertex (location)

            Aux Space Complexity: O(B), where B is the number of buses
            Aux Space Complexity Analysis:
        """
        for bus_index in range(len(buses)):
            pick_up_location = buses[bus_index][0]
            min_capacity = buses[bus_index][1]
            max_capacity = buses[bus_index][2]

            bus = Bus(bus_index, pick_up_location, min_capacity, max_capacity)

            self.locations[pick_up_location].add_bus(bus)

    def dijkstra_reset(self):
        """
        Function Description:
            reset all vertices for Dijkstra
        
        Input:
            None
        
        Output:
            None 
        
        Time Complexity: O(L) where L is the number of locations
        Time Complexity Analysis: Iterates through all vertices once
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Only modifies existing vertex attributes
        """
        for location in self.locations:
            location.visited = False
            location.discovered = False
            location.distance = float('inf')
            location.previous = None


    def dijkstra_with_max_distance(self, source, max_distance):
        """
        Function Description:
            Run Dijkstra algorithm from source but only explore locations within max_distance.
        
        Input:
            - source: ID of the source location
            - max_distance: Maximum distance threshold for exploration
        
        Output:
            None (updates distance and previous attributes in vertices)
        
        Time Complexity: O(L + R log L) where R is the number of roads and L is the number of locations
        Time Complexity Analysis: O(L) to reset vertices and allocate the heap array. Vertices are only
            pushed into the heap when first discovered (not all L upfront), so each of the 2R directed
            edges causes at most one O(log L) add/update, and each vertex is served at most once.

        Aux Space Complexity: O(L)
        Aux Space Complexity Analysis: MinHeap array and index_map of size L
        """
        # reset all vertices
        self.dijkstra_reset()
        # initialize source distance = 0
        self.locations[source].distance = 0
        # Only the source starts in the heap; other vertices are added when discovered
        discovered_minheap = MinHeap(len(self.locations))
        discovered_minheap.add((source, 0))
        self.locations[source].discovered = True

        while len(discovered_minheap) > 0:
            # serve the min element
            u_id, u_distance = discovered_minheap.get_min()

            if u_distance > max_distance:
                break

            u = self.locations[u_id]
            # finalized as visited
            u.visited = True

            # edge relaxation
            for edge in u.edges:
                v_id = edge.v
                v = self.locations[v_id]

                if v.visited == False:
                    new_distance = u_distance + edge.distance
                    # found shorter path and only update if the new distance < max distance
                    if new_distance < v.distance and new_distance <= max_distance:
                        # Update distance
                        v.distance = new_distance
                        v.previous = u_id
                        if not v.discovered:
                            # first time seen: push into heap
                            v.discovered = True
                            discovered_minheap.add((v_id, v.distance))
                        else:
                            # already in heap: decrease key using index_map
                            discovered_minheap.update(v_id, v.distance)

    def get_students_within_distance_from_pickups(self, max_walking_distance):
        """
        Function Description:
            For each pickup point, run a distance-limited Dijkstra and collect every student
            within max_walking_distance, with their walking distance. A student may appear under
            several pickups.

        Input:
            - max_walking_distance: Maximum distance D that students can walk

        Output:
            students_per_pickup, where students_per_pickup[location_id] is the list of
            (student index, walking distance) pairs within D of that pickup, or None if the
            location has no bus

        Time Complexity: O(L + R log L + S)
        Time Complexity Analysis: At most P <= 18 pickups, each costing O(L + R log L) for Dijkstra,
            O(L) for the scan, and O(S) for collecting students. P is constant.

        Aux Space Complexity: O(L + S)
        Aux Space Complexity Analysis: students_per_pickup has L slots and holds at most P*S = O(S) ids
        """
        students_per_pickup = [None] * len(self.locations)

        for vertex in self.locations:
            if len(vertex.buses) > 0:
                pickup_loc = vertex.id
                self.dijkstra_with_max_distance(pickup_loc, max_walking_distance)

                # Collect all students within D of this pickup
                reachable_students_at_pickup = []
                for v in self.locations:
                    if v.distance <= max_walking_distance:
                        for student_idx in v.students:
                            reachable_students_at_pickup.append((student_idx, v.distance))

                students_per_pickup[pickup_loc] = reachable_students_at_pickup

        return students_per_pickup
    
    def create_circulation_nodes_and_edges(self, max_walking_distance, total_students, buses):
        """
        Function Description:
            Build nodes and edges for circulation network with lower/upper bounds. Only creates nodes 
            for students who can reach at least one pickup point within max_walking_distance.
        
        Input:
            - max_walking_distance: Maximum distance D that students can walk
            - total_students: Total number of students S
            - buses: List of (pickup_loc, min_cap, max_cap) tuples for B buses
        
        Output:
            List containing [nodes_info, edges_list, metadata] where:
                - nodes_info = [x, z, students_start, pickups_start, buses_start, total_nodes]
                - edges_list = list of (u, v, lower, upper, cost) edge tuples
                - metadata = [S, P, B, pickup_locations, pickup_loc_to_node, students_per_pickup, 
                             reachable_students, student_idx_to_node]
        
        Time Complexity: O(L + R log L + S + B), where B <= T <= S after the checks in assign
        Time Complexity Analysis:
            - get_students_within_distance_from_pickups: O(L + R log L + S)
            - Finding pickups and reachable students: O(L + S)
            - Creating nodes and edges: O(P*S + B) = O(S + B) since P <= 18

        Aux Space Complexity: O(S + L + B)
        Aux Space Complexity Analysis:
            - students_per_pickup and pickup_loc_to_node: O(L + S)
            - Student mappings: O(S)
            - edges list: O(P*S + B) = O(S + B)
        """
        S = total_students
        B = len(buses)

        # Get students within walking distance of each pickup
        students_per_pickup = self.get_students_within_distance_from_pickups(max_walking_distance)

        # Find pickup locations (locations with buses)
        pickup_locations = []
        for location in range(len(self.locations)):
            if len(self.locations[location].buses) > 0:
                pickup_locations.append(location)
        P = len(pickup_locations)

        # A student is reachable if they are within D of at least one pickup
        is_reachable = [False] * S
        for pickup_loc in pickup_locations:
            for student_idx, _ in students_per_pickup[pickup_loc]:
                is_reachable[student_idx] = True
        
        # Build list of reachable students
        reachable_students = []
        for student_idx in range(S):
            if is_reachable[student_idx]:
                reachable_students.append(student_idx)
        
        S_reachable = len(reachable_students)
        
        # Create mapping: original student_idx -> node_id in flow network
        student_idx_to_node = [None] * S
        
        # Step 2: Node indexing (ONLY for reachable students)
        current_node = 0

        # x = temp source
        x = current_node
        current_node += 1
        
        # Students: [1 .. S_reachable]
        students_start = current_node
        for i in range(len(reachable_students)):
            student_idx = reachable_students[i]
            student_node = students_start + i
            student_idx_to_node[student_idx] = student_node
        current_node += S_reachable
        
        # Pickups: [S_reachable+1 .. S_reachable+P]
        pickups_start = current_node
        pickup_loc_to_node = [None] * len(self.locations)
        for idx in range(len(pickup_locations)):
            loc_id = pickup_locations[idx]
            pickup_node = pickups_start + idx
            pickup_loc_to_node[loc_id] = pickup_node
        current_node += P
        
        # Buses: [S_reachable+P+1 .. S_reachable+P+B]
        buses_start = current_node
        current_node += B
        
        # z = temp sink
        z = current_node
        current_node += 1
        
        total_nodes = current_node

        # Step 3: Build edges with lower/upper bounds
        edges = []
        
        # Edge 1: x -> Students (only reachable)
        for student_idx in reachable_students:
            student_node = student_idx_to_node[student_idx]
            edges.append((x, student_node, 0, 1, 0))
        
        # Edge 2: Students -> every pickup within D (at most P <= 18 per student),
        # costing the student's walking distance so the cheapest flow minimises total walking
        for pickup_loc in pickup_locations:
            pickup_node = pickup_loc_to_node[pickup_loc]
            for student_idx, walking_distance in students_per_pickup[pickup_loc]:
                student_node = student_idx_to_node[student_idx]
                edges.append((student_node, pickup_node, 0, 1, walking_distance))
        
        # Edge 3: Pickup -> Bus
        for bus_idx in range(B):
            bus = buses[bus_idx]
            pickup_loc = bus[0]
            bus_node = buses_start + bus_idx
            pickup_node = pickup_loc_to_node[pickup_loc]
            edges.append((pickup_node, bus_node, 0, float("inf"), 0))
        
        # Edge 4: Bus -> z
        for bus_idx in range(B):
            bus = buses[bus_idx]
            min_cap = bus[1]
            max_cap = bus[2]
            bus_node = buses_start + bus_idx
            edges.append((bus_node, z, min_cap, max_cap, 0))
        
        nodes_info = [x, z, students_start, pickups_start, buses_start, total_nodes]
        metadata = [S, P, B, pickup_locations, pickup_loc_to_node, students_per_pickup, 
                    reachable_students, student_idx_to_node]
        
        return [nodes_info, edges, metadata]
        
        
    
    # Add this method to your Graph class (after create_circulation_nodes_and_edges)
    def build_circulation_network(self, nodes_info, edges_list, T):
        """
        Function Description:
            Build CirculationFlowNetwork from nodes and edges. Adds the critical z -> x edge 
            with (lower=T, upper=T) to enforce exact student requirement.
        
        Input:
            - nodes_info: List [x, z, students_start, pickups_start, buses_start, total_nodes]
            - edges_list: List of (u, v, lower, upper, cost) edge tuples
            - T: Required number of students (exact)
        
        Output:
            CirculationFlowNetwork object ready for circulation conversion
        
        Time Complexity: O(E) where E is the number of edges
        Time Complexity Analysis: Iterates through all edges once to add them to the network
        
        Aux Space Complexity: O(V + E) where V is vertices and E is edges
        Aux Space Complexity Analysis: CirculationFlowNetwork stores V vertices and E edges
        """
        # Extract node info
        x = nodes_info[0]
        z = nodes_info[1]
        total_nodes = nodes_info[5]
        
        # Create circulation flow network
        circulation_network = CirculationFlowNetwork(total_nodes)
        
        # Add all existing edges
        for edge_tuple in edges_list:
            u, v, lower, upper, cost = edge_tuple
            circulation_network.add_edge(u, v, lower, upper, cost)
        
        # Add critical z -> x edge with (lower bound=T, upperbound=T)
        circulation_network.add_edge(z, x, T, T)
        
        return circulation_network
    

    def extract_allocation_from_circulation(self, circulation_network, nodes_info, metadata, total_students):
        """
        Function Description:
            Extract bus allocation from circulation network flows. Recovers which students ride 
            which buses by analyzing flow on edges. Handles sparse student nodes (only reachable students).
        
        Input:
            - circulation_network: CirculationFlowNetwork after successful min_cost_flow
            - nodes_info: List [x, z, students_start, pickups_start, buses_start, total_nodes]
            - metadata: List [S, P, B, pickup_locations, pickup_loc_to_node, students_per_pickup,
                        reachable_students, student_idx_to_node]
            - total_students: Total number of students S
        
        Output:
            allocation list where allocation[i] = bus_id if student i rides a bus, or -1 if not
        
        Time Complexity: O(S + B) where S is students and B is buses
        Time Complexity Analysis:
            - Finding traveling students: O(S_reachable) ≤ O(S)
            - Staging students at pickups: O(S_reachable)
            - Distributing to buses: O(B) buses * O(students per bus) = O(S) total
            Total: O(S + B)
        
        Aux Space Complexity: O(S + P)
        Aux Space Complexity Analysis:
            - traveling_students list: O(S)
            - students_at_pickup array: O(P) pickup points
            Total: O(S + P) = O(S) since P ≤ 18 is constant
        """
        # Extract node info
        x = nodes_info[0]
        z = nodes_info[1]
        students_start = nodes_info[2]
        pickups_start = nodes_info[3]
        buses_start = nodes_info[4]
        
        # Extract metadata (UPDATED indices!)
        S = metadata[0]
        P = metadata[1]
        B = metadata[2]
        pickup_locations = metadata[3]
        pickup_loc_to_node = metadata[4]
        students_per_pickup = metadata[5]
        reachable_students = metadata[6]  
        student_idx_to_node = metadata[7]  
        
        S_reachable = len(reachable_students)
        
        # Initialize allocation array 
        allocation = [-1] * total_students
        
        # Find traveling students 
        # ONLY check reachable students (unreachable students stay -1)
        traveling_students = []
        x_vertex = circulation_network.vertices[x]
        
        for edge in x_vertex.edges:
            # Check if edge goes to a student node
            if edge.v >= students_start and edge.v < students_start + S_reachable:
                real_flow = circulation_network.get_real_flow(edge)
                if real_flow > 0:
                    # Find which original student this node represents
                    node_offset = edge.v - students_start
                    student_idx = reachable_students[node_offset]
                    traveling_students.append(student_idx)
        
        # Stage students at their assigned pickups
        # students_at_pickup[pickup_idx] = list of student indices
        students_at_pickup = [None] * P
        pickup_idx = 0
        while pickup_idx < P:
            students_at_pickup[pickup_idx] = []
            pickup_idx += 1
        
        for student_idx in traveling_students:
            student_node = student_idx_to_node[student_idx]
            
            # Safety check: ensure student_node exists
            if student_node is None:
                continue
            
            student_vertex = circulation_network.vertices[student_node]
            
            # Find which pickup this student goes to (Student -> Pickup with flow = 1)
            for edge in student_vertex.edges:
                if edge.v >= pickups_start and edge.v < pickups_start + P:
                    real_flow = circulation_network.get_real_flow(edge)
                    if real_flow > 0:
                        pickup_idx = edge.v - pickups_start
                        students_at_pickup[pickup_idx].append(student_idx)
                        break
        
        # Distribute students from pickups to buses
        for pickup_idx in range(P):
            pickup_node = pickups_start + pickup_idx
            pickup_vertex = circulation_network.vertices[pickup_node]
            
            # For each bus connected to this pickup
            for edge in pickup_vertex.edges:
                if edge.v >= buses_start and edge.v < buses_start + B:
                    bus_idx = edge.v - buses_start
                    real_flow = circulation_network.get_real_flow(edge)
                    
                    # Assign 'real_flow' number of students to this bus
                    students_assigned = 0
                    while students_assigned < real_flow and len(students_at_pickup[pickup_idx]) > 0:
                        student_idx = students_at_pickup[pickup_idx].pop()
                        allocation[student_idx] = bus_idx
                        students_assigned += 1
        
        return allocation
    
    def validate_allocation(self, allocation, buses, T):
        """
        Function Description:
            Validate the final bus allocation to ensure correctness. Checks that exactly T students 
            are traveling and all bus capacity constraints are satisfied.
        
        Input:
            - allocation: List where allocation[i] = bus_id if student i rides a bus, or -1 if not
            - buses: List of (pickup_loc, min_cap, max_cap) tuples for B buses
            - T: Required number of traveling students
        
        Output:
            True if allocation is valid, False otherwise
        
        Time Complexity: O(S + B) where S is students and B is buses
        Time Complexity Analysis:
            - Counting traveling students: O(S)
            - Counting students per bus: O(S)
            - Checking bus capacities: O(B)
            Total: O(S + B)
        
        Aux Space Complexity: O(B)
        Aux Space Complexity Analysis: bus_counts array stores count for B buses
        """
        # Check 1: Count traveling students
        count_traveling = 0
        for bus_id in allocation:
            if bus_id != -1:
                count_traveling += 1
        
        if count_traveling != T:
            return False
        
        # Check 2: Verify bus capacity constraints
        bus_counts = [0] * len(buses)
        for bus_id in allocation:
            if bus_id != -1:
                bus_counts[bus_id] += 1
        
        for bus_idx in range(len(buses)):
            min_cap = buses[bus_idx][1]
            max_cap = buses[bus_idx][2]
            actual_count = bus_counts[bus_idx]
            
            if actual_count < min_cap or actual_count > max_cap:
                return False
        
        return True
