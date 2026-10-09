"""Entry point for the bus allocation problem."""

from .city_graph import Graph


def assign(L, roads, students, buses, D, T):
    """
    Function Description:
        Allocates students to buses so that exactly T students travel, every bus carries between
        its minimum and maximum capacity, and every travelling student is within distance D of
        their bus's pickup point. Among all such allocations, returns one with the least total
        walking distance from travelling students to their pickup points.

    Approach Description:
        Reject impossible inputs early: T > S, B > T (every bus needs at least one student, and
        this bounds B <= T <= S), any min > max, or T outside [sum of mins, sum of maxes].
        Run a distance-limited Dijkstra from each of the P <= 18 pickup points to find which
        students are within D of each pickup.
        Build a circulation network with lower bounds:
            x -> student [0, 1], student -> every pickup within D [0, 1],
            pickup -> bus [0, inf], bus -> z [min, max], z -> x [T, T].
        Each student -> pickup edge costs the student's walking distance; all others cost 0.
        Remove lower bounds by converting them into vertex demands, connect a super source and
        super sink, and run min-cost max-flow (successive shortest paths with Dijkstra and
        potentials). A feasible allocation exists iff the max flow saturates every demand, and
        the cheapest such flow minimises total walking; each student's bus is then read from the
        edges carrying flow.

    Input:
        - L: number of locations
        - roads: list of (u, v, w) bidirectional roads of length w
        - students: students[i] is the location of student i
        - buses: list of (pickup location, min capacity, max capacity)
        - D: maximum distance a student will travel to a pickup point
        - T: exact number of students that must travel

    Output:
        A list of length S where entry i is student i's bus ID, or -1 if they do not travel;
        None if no valid allocation exists.

    Time Complexity: O(T * S log S + L + R log L)
    Time Complexity Analysis:
        - Early checks: O(1) for T > S and B > T, then O(B) = O(S)
        - Building the city graph: O(L + R + S + B) = O(L + R + S)
        - P <= 18 Dijkstra runs, each O(L + R log L) since vertices only enter the heap when
          discovered: O(L + R log L)
        - Flow network: V = O(S + B) = O(S), E = O(P*S + B) = O(S)
        - Min-cost max-flow: total demand is T, so at most T augmentations, each a Dijkstra of
          O((V + E) log V) = O(S log S): O(T * S log S)
        - Extracting and validating the allocation: O(S)

    Aux Space Complexity: O(S + L + R)
    Aux Space Complexity Analysis:
        City graph O(L + R + S + B), Dijkstra heap O(L), flow and residual networks O(S + B),
        allocation O(S); B <= S after the early checks.
    """
    S = len(students)
    B = len(buses)
    
    # Step 0: Pre-checking
    # Every bus must carry >= 1 student, so B > T is infeasible. Checking this (and T > S) first,
    # in O(1), bounds B <= T <= S for everything below; otherwise any O(B) loop is unbounded.
    if T > S or B > T:
        return None

    sum_min = 0
    sum_max = 0
    for bus in buses:
        sum_min += bus[1]
        sum_max += bus[2]
    
    # Check feasibility conditions
    # min > max
    for bus in buses:
        if bus[1] > bus[2]:  
            return None
    
    if T < sum_min or T > sum_max:
        return None
    
    # Build city graph
    city = Graph(L)
    city.add_edges(roads)
    city.add_student_to_location(students)
    city.add_bus_to_location(buses)
    
    # Steps 1-3: Build circulation network
    result = city.create_circulation_nodes_and_edges(D, S, buses)
    nodes_info = result[0]
    edges_list = result[1]
    metadata = result[2]
    
    # Step 3 (continued): Add z -> x edge and create network
    circulation_network = city.build_circulation_network(nodes_info, edges_list, T)
    
    # Steps 4 & 5: Convert to circulation and add SS/TT
    circulation_result = circulation_network.convert_to_circulation()
    SS = circulation_result[0]
    TT = circulation_result[1]
    total_positive_balance = circulation_result[2]
    
    # Step 5: Run min-cost max-flow from SS to TT
    max_flow = circulation_network.min_cost_flow(SS, TT)
    
    # Check if circulation is feasible
    if max_flow != total_positive_balance:
        return None
    
    # Step 6: Extract allocation from real flows
    allocation = city.extract_allocation_from_circulation(circulation_network, nodes_info, metadata, S)
    
    # Step 7: Final checking
    if not city.validate_allocation(allocation, buses, T):
        return None
    
    return allocation
