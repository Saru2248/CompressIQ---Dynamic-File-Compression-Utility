import json
import struct
from src.node import HuffmanNode
from src.heap import MinHeap

class HuffmanCoding:
    """
    Main controller class for Huffman encoding and decoding.
    Operates at the byte level (0-255) to compress and decompress any file format.
    """
    def __init__(self):
        self.freq_table = {}
        self.codes = {}
        self.reverse_codes = {}
        self.root = None

    def build_frequency_table(self, raw_bytes):
        """
        Scans raw bytes to calculate the frequency of each byte value (0-255).
        Returns a dictionary mapping byte values to frequencies.
        """
        freq = {}
        for byte in raw_bytes:
            freq[byte] = freq.get(byte, 0) + 1
        return freq

    def build_huffman_tree(self, freq_table):
        """
        Builds the Huffman tree using a priority queue (MinHeap).
        Returns the root node of the tree.
        """
        heap = MinHeap()
        
        # 1. Create a leaf node for each unique byte and insert it into the min-heap
        for byte, count in freq_table.items():
            node = HuffmanNode(byte, count)
            heap.insert(node)

        # Edge case: Empty file
        if heap.size() == 0:
            return None
        
        # Edge case: Only one unique character in the file
        if heap.size() == 1:
            left_child = heap.extract_min()
            parent = HuffmanNode(None, left_child.freq)
            parent.left = left_child
            heap.insert(parent)

        # 2. Iterate until there is only one node left in the heap (the root)
        while heap.size() > 1:
            # Extract the two nodes with the lowest frequencies
            node1 = heap.extract_min()
            node2 = heap.extract_min()

            # Create a new internal node with a frequency equal to the sum of the two nodes' frequencies
            parent = HuffmanNode(None, node1.freq + node2.freq)
            parent.left = node1
            parent.right = node2
            
            # Insert the new parent node back into the min-heap
            heap.insert(parent)

        # The remaining node is the root of the Huffman tree
        return heap.extract_min()

    def _generate_codes_helper(self, node, current_code):
        """Recursive helper function to traverse the tree and assign binary paths."""
        if node is None:
            return

        # Leaf node contains a character: store its generated binary code
        if node.is_leaf():
            self.codes[node.char] = current_code
            self.reverse_codes[current_code] = node.char
            return

        # Traverse left (assign '0') and right (assign '1')
        self._generate_codes_helper(node.left, current_code + "0")
        self._generate_codes_helper(node.right, current_code + "1")

    def generate_codes(self, root):
        """
        Triggers binary code generation by traversing the Huffman tree.
        Returns a dictionary mapping byte values to their binary string representation.
        """
        self.codes = {}
        self.reverse_codes = {}
        self._generate_codes_helper(root, "")
        return self.codes

    def compress(self, raw_bytes):
        """
        Compresses a sequence of raw bytes using Huffman Coding.
        Returns a binary sequence (bytes) consisting of:
        - 4-byte integer: Length of metadata header (L)
        - L-byte JSON: Frequency table and padding info
        - Remaining bytes: The compressed bit stream packed into bytes
        """
        if not raw_bytes:
            return b""

        # 1. Build frequency table
        self.freq_table = self.build_frequency_table(raw_bytes)

        # 2. Build Huffman Tree
        self.root = self.build_huffman_tree(self.freq_table)

        # 3. Generate Codes
        self.generate_codes(self.root)

        # 4. Convert input bytes to encoded bit string
        bit_string_list = [self.codes[byte] for byte in raw_bytes]
        encoded_bits = "".join(bit_string_list)

        # 5. Pad the bit string so its length is a multiple of 8
        # Since files are byte-oriented, we must write complete bytes
        padding = 8 - (len(encoded_bits) % 8)
        if padding == 8:
            padding = 0
        else:
            encoded_bits += "0" * padding

        # 6. Convert the bit string into actual bytes
        byte_arr = bytearray()
        for i in range(0, len(encoded_bits), 8):
            byte_val = int(encoded_bits[i:i+8], 2)
            byte_arr.append(byte_val)

        # 7. Serialize metadata as JSON to store in the file header
        # JSON keys must be strings, so we convert integer byte values to string keys
        metadata = {
            "freq": {str(k): v for k, v in self.freq_table.items()},
            "padding": padding
        }
        metadata_bytes = json.dumps(metadata).encode('utf-8')
        metadata_len = len(metadata_bytes)

        # 8. Assemble final compressed payload:
        # [Header Size (4 bytes)][Header Metadata (JSON string)][Compressed Bits]
        header_len_bytes = struct.pack(">I", metadata_len) # 32-bit unsigned integer (big-endian)
        
        return header_len_bytes + metadata_bytes + bytes(byte_arr)

    def decompress(self, compressed_data):
        """
        Decompresses the Huffman encoded binary data.
        Returns the original uncompressed byte sequence.
        """
        if len(compressed_data) < 4:
            return b""

        # 1. Extract metadata size (first 4 bytes)
        metadata_len = struct.unpack(">I", compressed_data[:4])[0]
        
        # 2. Extract and decode metadata
        metadata_bytes = compressed_data[4:4+metadata_len]
        metadata = json.loads(metadata_bytes.decode('utf-8'))
        
        freq_table_raw = metadata["freq"]
        padding = metadata["padding"]
        
        # Convert JSON string keys back to integer byte keys
        freq_table = {int(k): v for k, v in freq_table_raw.items()}
        
        # 3. Rebuild Huffman Tree
        self.root = self.build_huffman_tree(freq_table)
        if self.root is None:
            return b""

        # 4. Extract padded bit stream and convert bytes back to a bit string
        bit_data = compressed_data[4+metadata_len:]
        bit_string_list = [f"{byte:08b}" for byte in bit_data]
        encoded_bits = "".join(bit_string_list)
        
        # Remove padding bits
        if padding > 0:
            encoded_bits = encoded_bits[:-padding]

        # 5. Decode the bit string using tree traversal
        decoded_bytes = bytearray()
        current_node = self.root
        
        for bit in encoded_bits:
            if bit == '0':
                current_node = current_node.left
            else:
                current_node = current_node.right
                
            # If leaf node is reached, record the byte value and return to the root
            if current_node.is_leaf():
                decoded_bytes.append(current_node.char)
                current_node = self.root
                
        return bytes(decoded_bytes)

    def compress_file(self, input_path, output_path):
        """
        Reads a file from disk, compresses it using Huffman Coding, and writes
        the compressed binary payload to the output path.

        Args:
            input_path  (str): Path to the source file to compress.
            output_path (str): Path where the .huff file will be written.

        Returns:
            tuple: (original_size, compressed_size) in bytes.
        """
        with open(input_path, "rb") as f:
            raw_bytes = f.read()

        compressed_data = self.compress(raw_bytes)

        with open(output_path, "wb") as f:
            f.write(compressed_data)

        return len(raw_bytes), len(compressed_data)

    def decompress_file(self, input_path, output_path):
        """
        Reads a .huff compressed file from disk, decompresses it using Huffman
        tree reconstruction, and writes the restored bytes to the output path.

        Args:
            input_path  (str): Path to the compressed .huff file.
            output_path (str): Path where the restored original file will be written.

        Returns:
            int: Number of bytes written (size of decompressed file).
        """
        with open(input_path, "rb") as f:
            compressed_data = f.read()

        decompressed_bytes = self.decompress(compressed_data)

        with open(output_path, "wb") as f:
            f.write(decompressed_bytes)

        return len(decompressed_bytes)
