class HuffmanNode:
    """
    Represents a node in the Huffman Tree.
    Each node stores a character and its frequency.
    For internal nodes, the character is None.
    """
    def __init__(self, char, freq):
        self.char = char        # The character (None for internal nodes)
        self.freq = freq        # Frequency of the character (or sum of child frequencies)
        self.left = None        # Left child reference
        self.right = None       # Right child reference

    def is_leaf(self):
        """Returns True if the node is a leaf node (has no children)."""
        return self.left is None and self.right is None

    def __lt__(self, other):
        """
        Less-than operator for comparing nodes.
        This is crucial for the Min Heap / Priority Queue to maintain heap property.
        If frequencies are equal, we compare characters as a tie-breaker.
        """
        if not isinstance(other, HuffmanNode):
            return NotImplemented
        
        if self.freq != other.freq:
            return self.freq < other.freq
        
        # Tie-breaking logic for nodes with identical frequencies
        if self.char is not None and other.char is not None:
            return self.char < other.char
        
        # Leaf nodes take priority over internal nodes for shorter paths if frequencies match
        if self.char is not None:
            return True
        return False

    def __repr__(self):
        char_display = repr(self.char) if self.char is not None else "Internal"
        return f"HuffmanNode(char={char_display}, freq={self.freq})"
