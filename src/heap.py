class MinHeap:
    """
    A custom implementation of a Min-Heap (Priority Queue) from scratch.
    This is used to build the Huffman Tree by repeatedly extracting the
    two nodes with the lowest frequency.
    """
    def __init__(self):
        # The heap is represented as an array (list)
        self.heap = []

    def _parent(self, index):
        return (index - 1) // 2

    def _left_child(self, index):
        return (2 * index) + 1

    def _right_child(self, index):
        return (2 * index) + 2

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def size(self):
        """Returns the number of elements in the heap."""
        return len(self.heap)

    def is_empty(self):
        """Returns True if the heap contains no elements."""
        return len(self.heap) == 0

    def insert(self, node):
        """
        Inserts a new HuffmanNode into the heap.
        Time Complexity: O(log N)
        """
        self.heap.append(node)
        self._heapify_up(self.size() - 1)

    def extract_min(self):
        """
        Removes and returns the node with the smallest frequency from the heap.
        Time Complexity: O(log N)
        """
        if self.is_empty():
            raise IndexError("Extract from an empty MinHeap")
        
        # If there's only one element, pop it directly
        if self.size() == 1:
            return self.heap.pop()

        # Swap root with the last element, remove the last, and heapify down the root
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        
        return root

    def peek(self):
        """Returns the node with the minimum frequency without removing it."""
        if self.is_empty():
            return None
        return self.heap[0]

    def _heapify_up(self, index):
        """
        Maintains heap property by bubbling up an element.
        Moves the element up the tree until parent is smaller or root is reached.
        """
        parent_index = self._parent(index)
        while index > 0 and self.heap[index] < self.heap[parent_index]:
            self._swap(index, parent_index)
            index = parent_index
            parent_index = self._parent(index)

    def _heapify_down(self, index):
        """
        Maintains heap property by bubbling down an element.
        Compares with children and swaps with the smaller child until heap property holds.
        """
        smallest = index
        left = self._left_child(index)
        right = self._right_child(index)
        n = self.size()

        # Compare with left child
        if left < n and self.heap[left] < self.heap[smallest]:
            smallest = left

        # Compare with right child
        if right < n and self.heap[right] < self.heap[smallest]:
            smallest = right

        # If smallest is not current index, swap and continue heapifying down recursively
        if smallest != index:
            self._swap(index, smallest)
            self._heapify_down(smallest)
