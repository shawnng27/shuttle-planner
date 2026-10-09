"""City entities: locations (vertices), roads (edges) and buses."""


class Vertex:
    """
    Function Description:
        Vertex representing a location in the city graph.
    
    Attributes:
        - id: Location identifier
        - edges: List of Edge objects (roads from this location)
        - visited: Dijkstra visited flag
        - discovered: Dijkstra discovered flag
        - buses: List of Bus objects at this location
        - students: List of student indices at this location
        - distance: Distance from source in Dijkstra
        - previous: Previous vertex ID in shortest path
    """
    def __init__(self, location_id):
        """
        Function Description:
            Initialize vertex for a city location.
        
        Input:
            - location_id: Unique location id
        
        Output:
            None
        
        Time Complexity: O(1)
        Time Complexity Analysis: Simple attribute initialization
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Fixed number of attributes
        """
        self.id = location_id
        self.edges = []
        self.visited = False
        self.discovered = False
        self.buses = []
        self.students = []
        self.distance = float('inf')
        self.previous = None

    def add_edges(self, edge):
        """
        Function Description:
            Add road edge from this location.
        
        Input:
            - edge: Edge object representing a road
        
        Output:
            None (appends edge to edges list)
        
        Time Complexity: O(1)
        Time Complexity Analysis: List append is O(1)
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Single edge add
        """
        self.edges.append(edge)

    def add_student(self, student_idex: int):
        """
        Function Description:
            Add student to this location.
        
        Input:
            - student_idx: Student identifier
        
        Output:
            None (appends student to students list)
        
        Time Complexity: O(1)
        Time Complexity Analysis: List append is amortized O(1)
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Single student index added
        """
        self.students.append(student_idex)

    def add_bus(self, bus_location: int):
        """
        Function Description:
            Add bus to this pickup location.
        
        Input:
            - bus_location: Bus object
        
        Output:
            None
        
        Time Complexity: O(1)
        Time Complexity Analysis: List append is amortized O(1)
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Single bus reference added
        """
        self.buses.append(bus_location)
        

class Edge:
    """
    Class Description:
        Edge representing a bidirectional road between two locations.
    
    Attributes:
        - u: Source vertex id
        - v: Destination vertex id
        - distance: Road distance/weight
    """
    def __init__(self, u: Vertex, v: Vertex, distance: int = 0):
        """
        Function Description:
            Initialize road edge between two locations.
        
        Input:
            - u: Source vertex id
            - v: Destination vertex id
            - distance: Road distance (default 0)
        
        Output:
            None (creates Edge object)
        
        Time Complexity: O(1)
        Time Complexity Analysis: Only assigning atribute
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: store three attributes 
        """
        self.u = u
        self.v = v
        self.distance = distance


class Bus:
    """
    Class Description:
        Bus object with capacity constraints and pickup location.
    
    Attributes:
        - id: Bus id
        - pickup_location: Location id where bus picks up students
        - min_capacity: Minimum number of students required
        - max_capacity: Maximum number of students allowed
        - assigned_student: List of assigned student indices
    """
    def __init__(self, bus_id, pick_up_location, min_capacity, max_capacity):
        """
        Function Description:
            Initialize bus with capacity constraints.
        
        Input:
            - bus_id: Unique bus identifier
            - pick_up_location: Location ID for pickup
            - min_capacity: Minimum students required
            - max_capacity: Maximum students allowed
        
        Output:
            None (creates Bus object)
        
        Time Complexity: O(1)
        Time Complexity Analysis: Simple attribute initialization
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: Fixed number of attributes
        """
        self.id = bus_id
        self.pickup_location = pick_up_location
        self.min_capacity = min_capacity
        self.max_capacity = max_capacity
        self.assigned_student = []
