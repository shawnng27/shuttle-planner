"""Indexed min-heap used by Dijkstra (modified from FIT1008)."""


class MinHeap:
    """
    Min-heap data structure

    Attributes:
        MIN_CAP (int): Minimum capacity (class constant)
        length (int): Current number of elements in heap
        heap_array (list): Fixed-size array storing (vertex_id, distance) tuples
        index_map (list): Maps vertex_id to position in heap_array for O(1) lookup
    """

    MIN_CAP = 1

    def __init__(self, max_size: int) -> None:
        """
        Initialize min-heap with specified maximum size.
        
        Args:
            max_size (int): Maximum number of elements the heap can hold
        
        Time Complexity: O(max_size)
        Aux Space Complexity: O(max_size)
        """
        self.length: int = 0
        self.heap_array = [None] * (max(self.MIN_CAP, max_size) + 1)
        self.index_map = [None] * (max(self.MIN_CAP, max_size) + 1)

    def __len__(self) -> int:
        """
        Get current number of elements in heap.
        
        Returns:
            int: Number of elements
        
        Time Complexity: O(1)
        Aux Space Complexity: O(1)
        """
        return self.length
    
    def is_full(self) -> bool:
        """
        Check if heap is at maximum capacity.
        
        Returns:
            bool: True if heap is full, False otherwise
        
        Time Complexity: O(1)
        Aux Space Complexity: O(1)
        """
        return self.length + 1 == len(self.heap_array)
    
    def swap(self, i: int, j: int) -> None:
        """
        Swap elements at positions i and j, and update index_map.
        Maintains the mapping from vertex_id to heap position.
        
        Args:
            i (int): First position in heap
            j (int): Second position in heap
        
        Time Complexity: O(1)
        Aux Space Complexity: O(1)
        """
        # Swap in heap array
        self.heap_array[i], self.heap_array[j] = self.heap_array[j], self.heap_array[i]
        
        # Update index_map for both vertices, index_map = (vertex_id, position in heap)
        if self.heap_array[i] is not None:
            # update i vertex
            vertex_id_i = self.heap_array[i][0]
            self.index_map[vertex_id_i] = i
        
        if self.heap_array[j] is not None:
            # update j vertex
            vertex_id_j = self.heap_array[j][0]
            self.index_map[vertex_id_j] = j

    def rise(self, k: int) -> None:
        """
        Rise the element at index k to its correct position.
        Updates index_map when swaping.
        
        Args:
            k (int): Position of element to rise
        
        Time Complexity: O(log L) where L is heap size
        Aux Space Complexity: O(1)
        """
        while k > 1 and self.heap_array[k][1] < self.heap_array[k // 2][1]:
            self.swap(k, k // 2)
            k = k // 2

    def add(self, element) -> None:
        """
        Add element to heap and restore heap property.
        
        Args:
            element (tuple): (vertex_id, distance) tuple to add
        
        Raises:
            IndexError: If heap is full
        
        Time Complexity: O(log L) where L is heap size
        Aux Space Complexity: O(1)
        """
        if self.is_full():
            raise IndexError
        
        self.length += 1
        self.heap_array[self.length] = element
        
        # Update index_map
        vertex_id = element[0]
        self.index_map[vertex_id] = self.length
        
        self.rise(self.length)

    def smallest_child(self, k: int) -> int:
        """
        Return the index of k's child with the smallest value.
        
        Args:
            k (int): Parent position
        
        Returns:
            int: Position of smallest child
        
        Time Complexity: O(1)
        Aux Space Complexity: O(1)
        """
        if 2 * k == self.length or self.heap_array[2 * k][1] < self.heap_array[2 * k + 1][1]:
            return 2 * k
        else:
            return 2 * k + 1
        
    def sink(self, k: int) -> None:
        """
        Sink element at position k to its correct position to maintain heap property.
        Updates index_map during swaps.
        Used after extracting minimum or increasing a key.
        
        Args:
            k (int): Position of element to sink
        
        Time Complexity: O(log L) where L is heap size
        Aux Space Complexity: O(1)
        """
        while 2 * k <= self.length:
            min_child = self.smallest_child(k)
            if self.heap_array[min_child][1] >= self.heap_array[k][1]:
                break
            self.swap(k, min_child)
            k = min_child

    def get_min(self):
        """
        Return and remove the minimum item in the heap.
        Moves last element to root and sinks it down.
        
        Returns:
            tuple: (vertex_id, distance) of minimum element
        
        Raises:
            IndexError: If heap is empty
        
        Time Complexity: O(log L) where L is heap size
        Aux Space Complexity: O(1)
        """
        if self.length == 0:
            raise IndexError
        
        min_element = self.heap_array[1]
        
        # Move last element to the end
        self.heap_array[1] = self.heap_array[self.length]
        self.length -= 1

        if self.length > 0:
            # Update index_map for moved element
            vertex_id = self.heap_array[1][0]
            self.index_map[vertex_id] = 1
            self.sink(1)
        
        return min_element
    
    def update(self, vertex_id: int, new_distance: int) -> None:
        """
        Update the distance of a vertex already in the heap.
        Uses index_map to find position in O(1).
        
        Args:
            vertex_id (int): The vertex ID to update
            new_distance (int): The new (typically shorter) distance
        
        Time Complexity: O(log L) where L is heap size
        Aux Space Complexity: O(1)
        """
        # Find position using index_map
        position = self.index_map[vertex_id]
        
        if position is None or position > self.length:
            # Vertex not in heap (already removed)
            return
        
        old_distance = self.heap_array[position][1]
        
        # Update distance
        self.heap_array[position] = (vertex_id, new_distance)
        
        # Restore heap property
        if new_distance < old_distance:
            self.rise(position)  # Distance smaller, rise up
        elif new_distance > old_distance:
            self.sink(position)  # Distance greater, sink down

    def contains(self, vertex_id: int):
        """
        Get the current distance of a vertex in the heap.
        
        Args:
            vertex_id (int): Vertex ID to query
        
        Returns:
            int/None: Current distance or None if not in heap
        
        Time Complexity: O(1)
        Aux Space Complexity: O(1)
        """
        position = self.index_map[vertex_id]
        return position is not None and position <= self.length
    
    def get_distance(self, vertex_id: int):
        """
        Function Description:
            Get the current distance of a vertex in the heap.
        
        Input:
            - vertex_id: Vertex ID to query
        
        Output:
            Current distance of the vertex, or None if not in heap
        
        Time Complexity: O(1)
        Time Complexity Analysis: Direct access via index_map
        
        Aux Space Complexity: O(1)
        Aux Space Complexity Analysis: No additional space used
        """
        position = self.index_map[vertex_id]
        if position is None or position > self.length:
            return None
        return self.heap_array[position][1]
