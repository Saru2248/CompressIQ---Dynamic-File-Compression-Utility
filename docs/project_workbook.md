# CompressIQ — Dynamic File Compression Utility: Student Project Workbook

This workbook is a comprehensive guide to building, understanding, documenting, and presenting **CompressIQ** as a standout project for your software engineering portfolio.

---

## 1️⃣ PROJECT EXPLANATION

### 👶 Simple Explanation (The Shorthand Analogy)
Imagine you and a friend communicate using a limited set of words. Writing out long words takes time and paper. If you use the word "the" 100 times and the word "xylophone" once, it makes sense to write "t" for "the" and keep "xylophone" as it is. 
This is what **Huffman Coding** does for files. Instead of using 8 bits (1 byte) for every character (whether it is a common space or a rare character like 'z'), it analyzes the file, finds out which characters appear most frequently, and gives them the shortest possible shorthand codes (like `0` or `10`), while giving rare characters longer codes (like `11101`).

### ⚙️ Technical Explanation (Lossless Data Compression)
The utility is a **lossless data compression** application. "Lossless" means that the decompressed file is a byte-for-byte exact replica of the original, with zero data degradation.
It operates on **Greedy Huffman Coding**, which builds an optimal prefix-free code tree. A **prefix-free code** (or prefix code) is a code in which no code word is a prefix of another (e.g., if 'E' is `01`, no other character code starts with `01`). This feature is crucial because it allows the decoder to read a continuous stream of bits and uniquely identify characters without separator markers.

```text
WORKFLOW:
[Input File] ──► [Frequency Analysis] ──► [Min-Heap Initialization] ──► [Huffman Tree Assembly]
                                                                                │
[Decompressed File] ◄── [Bit Decoding] ◄── [Header Deserialization] ◄── [Bitwise Packing] ◄─┘
```

---

## 2️⃣ TECH STACK OPTIONS

When building this project, three distinct approaches can be taken:

| Category | Option A: Easy | Option B: Intermediate (Selected) | Option C: Advanced |
| :--- | :--- | :--- | :--- |
| **Language** | Python | **Python** | C++ |
| **Core DSA** | Standard `heapq` module | **Custom Min-Heap + Huffman Tree** | Custom Heap, Bitwise Buffer, Tree |
| **Bit Packing**| Zeros and Ones as Text (`"0101"`) | **Actual Bit-to-Byte packing** | Byte-level file streams (`std::fstream`) |
| **Header** | No header (hardcoded table) | **JSON Metadata Header (4-byte length)** | Custom binary tree serialization |
| **Interface** | Basic script | **Interactive CLI with colorama** | Performance benchmark CLI |

### 🏆 Selected Option for Students: Option B
**Option B** is chosen because:
1. **Academic Integrity**: Writing a **custom Min-Heap** demonstrates core DSA concepts directly to recruiters.
2. **Actual Utility**: It performs *real physical file compression* by packing bits into bytes rather than just writing `"0"` and `"1"` as text characters.
3. **Cross-Platform CLI**: Easy to run on Windows, macOS, or Linux with minimal setup.

---

## 3️⃣ PROJECT ARCHITECTURE

### 🗺️ System Architecture Diagram
```text
==========================================================================================
                                  COMPRESSION PHASE
==========================================================================================
[Input Stream] ──────► [Calculate Frequencies] ──────► [Populate Min-Heap]
                                                             │
[Pack Bits to Bytes] ◄─── [Generate Codebook] ◄─── [Build Huffman Tree]
         │
         ▼
[Assemble File Payload] ( [4-Byte Header Size] + [JSON Metadata Header] + [Packed Byte Stream] )
         │
         ▼
[Write to .huff File]

==========================================================================================
                                 DECOMPRESSION PHASE
==========================================================================================
[Read .huff File] ───► [Extract 4-Byte Size] ───► [Extract & Parse JSON Metadata]
                                                             │
[Write Original Bytes] ◄── [Traverse Tree] ◄──── [Rebuild Huffman Tree]
```

### 🗃️ Key Data Structures Used
1. **Min-Heap (Priority Queue)**: An array representation of a binary tree where the parent node `i` is always smaller than or equal to its children `2i + 1` and `2i + 2`. Used to fetch the two lowest frequency elements in $O(\log N)$ time.
2. **Huffman Tree (Binary Tree)**: A structural binary tree. Leaves store character values, and internal nodes store frequency sums. Left child traversals represent `0`, right child traversals represent `1`.
3. **Hash Map (Python Dictionary)**: Used to store character frequencies and mapping codes (`char -> binary_string`) for fast $O(1)$ lookups during encoding.

---

## 4️⃣ IMPLEMENTATION PLAN

### Phase 1: Setup & Environment
* **Action**: Configure workspace, setup virtual environment, write `.gitignore` and `requirements.txt`.
* **Why**: Ensures reproducible runtimes and clean git commits.
* **Beginner Mistake**: Committing `venv/` or temporary log directories to GitHub.

### Phase 2: File Reading (Byte-Level)
* **Action**: Implement reading files in binary mode (`rb`).
* **Why**: Text editors decode bytes dynamically; read raw bytes directly to ensure compatibility with non-text files.
* **Beginner Mistake**: Reading files as text (`r`), which corrupts files that contain non-UTF-8 binary data.

### Phase 3: Frequency Table Creation
* **Action**: Map each byte value (0-255) to its occurrence count.
* **Why**: Frequency determines the tree structure and resulting code lengths.
* **Beginner Mistake**: Storing character frequencies only for standard alphabets, omitting symbols, spaces, and formatting characters.

### Phase 4: Custom Min-Heap Implementation
* **Action**: Code parent/child pointer arithmetic, bubble-up, bubble-down, insertion, and extract-min.
* **Why**: Proves understanding of priority queues without relying on built-in libraries.
* **Beginner Mistake**: Off-by-one errors in index conversions: `parent = (i-1)//2`, `left = 2i+1`, `right = 2i+2`.

### Phase 5: Huffman Tree Construction
* **Action**: Pop two nodes from the heap, merge them under a new parent, and push the parent back until one node remains.
* **Why**: Places low-frequency items further down the tree, resulting in longer paths/codes.
* **Beginner Mistake**: Forgetting node comparisons (`__lt__`) will trigger errors when comparing two nodes with identical frequencies.

### Phase 6: Code Generation (DFS Traversal)
* **Action**: Traverse the tree from root to leaf, appending '0' for left paths and '1' for right paths.
* **Why**: Constructs the codebook map for compression.
* **Beginner Mistake**: Creating prefix codes that overlap, resulting in ambiguous decompressions.

### Phase 7: File Compression & Bit Packing
* **Action**: Convert source bytes to a bit string, pad it to a multiple of 8, pack bits into bytes, and write the header metadata.
* **Why**: Essential for physical size reduction; writing bits as string characters increases file size.
* **Beginner Mistake**: Forgetting to record padding bits, leading to extra trailing characters during decompression.

### Phase 8: File Decompression & Tree Rebuilding
* **Action**: Extract header metadata, reconstruct the Huffman tree, unpack byte arrays back to bits, and traverse the tree to extract characters.
* **Why**: Restores the original binary payload.
* **Beginner Mistake**: Rebuilding a new tree from decompressed file frequencies, which changes leaf arrangements and scrambles the output.

### Phase 9: Compression Ratio Calculations
* **Action**: Calculate original vs. compressed file size, ratio, and space savings percentage.
* **Why**: Quantifies performance to prove efficiency.
* **Beginner Mistake**: Calculating savings on small files (< 100 bytes) where header overhead makes the compressed file larger.

### Phase 10: GitHub Upload
* **Action**: Write documentation, capture execution results, commit phases, and push to GitHub.
* **Why**: Presents code as a clean portfolio project.
* **Beginner Mistake**: Committing the entire project in a single "Initial Commit".

---

## 5️⃣ FOLDER STRUCTURE

The repository uses the following organization:
* `input_files/`: Store test files (e.g., text, code, logs).
* `compressed_files/`: Holds output `.huff` binaries.
* `decompressed_files/`: Holds restored files to verify integrity.
* `src/`: Houses modularized python files (`node.py`, `heap.py`, `huffman.py`).
* `outputs/`: Keeps generated simulation reports.
* `images/`: Save console screenshots for the README.
* `docs/`: Stores this workbook and other references.

---

## 6️⃣ INSTALLATION & SETUP GUIDE

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/yourusername/Dynamic-File-Compression-Utility.git
   cd Dynamic-File-Compression-Utility
   ```
2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Running the Utility**:
   * Windows: `python main.py --demo`
   * Mac/Linux: `python3 main.py --demo`

---

## 7️⃣ FULL PROJECT CODE

Here is the complete source code for the project, organized as implemented in your workspace:

### 📄 File: `src/node.py`
```python
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
```

### 📄 File: `src/heap.py`
```python
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
```

### 📄 File: `src/huffman.py`
```python
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
```

---

## 8️⃣ VIRTUAL SIMULATION WORKFLOW

You can demonstrate the utility step-by-step through a virtual walkthrough:

1. **Initialize Simulation**:
   ```bash
   python main.py --demo
   ```
2. **Step 1: File Generation**: The script writes a synthetic text file `input_files/sample.txt` populated with regular patterns of words to guarantee compression.
3. **Step 2: Frequency Mapping & Codebook Display**: The terminal prints the frequencies and shows characters with the highest occurrence mapped to the shortest code paths.
4. **Step 3: Size Comparison**: The terminal compares file sizes to calculate space savings.
5. **Step 4: Decompression Verification**: The compressed file is parsed, decompressed to `decompressed_files/sample_recovered.txt`, and compared byte-for-byte to confirm matches.

---

## 9️⃣ HOW TO RUN THE PROJECT (MANUAL ROUTE)

If you wish to test custom inputs instead of the demo:

1. Place your target file (e.g., `essay.txt`) in `input_files/`.
2. **Compress**:
   ```bash
   python main.py -c input_files/essay.txt -s
   ```
   *Expected Output*: Displays compression statistics and outputs `compressed_files/essay.txt.huff`.
3. **Decompress**:
   ```bash
   python main.py -d compressed_files/essay.txt.huff
   ```
   *Expected Output*: Restores `decompressed_files/recovered_essay.txt`.

---

## 🔟 GITHUB UPLOAD STEPS

Follow these steps to upload your repository:

### 1. Initialize Git Local Repository
```bash
git init
git add .
git commit -m "feat: initial project setup and structure"
```

### 2. Create the GitHub Repository
Go to GitHub, create a repository named: `CompressIQ`.
* **Description**: CompressIQ — An intelligent, byte-level file compression tool implementing Huffman Coding and a custom Min-Heap from scratch in Python.
* **Tags**: `data-structures`, `algorithms`, `huffman-coding`, `greedy-algorithm`, `file-compression`, `python`, `systems-programming`, `min-heap`

### 3. Add Remote and Push Code
```bash
git remote add origin https://github.com/YOUR_USERNAME/CompressIQ.git
git branch -M main
git push -u origin main
```

---

## 1️⃣1️⃣ README.md REFERENCE
*(See the root [README.md](file:///e:/NEW%20IIP/DSA/Dynamic%20File%20Compression%20Utility/README.md) file written in the directory.)*

---

## 1️⃣2️⃣ PROOF-BUILDING STRATEGY (DAY-BY-DAY PLAN)

A structured approach to commit changes systematically:

* **Day 1: Setup & Data Representation**
  * Create `node.py`, `.gitignore`, and `requirements.txt`.
  * *Commit*: `git commit -m "docs: establish workspace and huffman tree nodes"`
* **Day 2: Priority Queue Mechanics**
  * Write `heap.py` with custom array bubble logics. Write tests to verify min extraction.
  * *Commit*: `git commit -m "feat: implement custom min-heap priority queue"`
* **Day 3: Tree Building & Coding**
  * Build Huffman tree logic and the recursive code generator in `huffman.py`.
  * *Commit*: `git commit -m "feat: construct huffman tree builder and codebook generator"`
* **Day 4: Bitwise Packing Pipeline**
  * Implement bit-to-byte packing and add header serialization using `struct`.
  * *Commit*: `git commit -m "feat: complete bit packer and payload serializer"`
* **Day 5: Decompression Pipeline**
  * Write decompression extraction, binary unpacking, and tree traversal decoder.
  * *Commit*: `git commit -m "feat: build decompression and data integrity validator"`
* **Day 6: CLI & Portfolio Documentation**
  * Create `main.py`, run tests, and write the project `README.md`.
  * *Commit*: `git commit -m "docs: build command-line interface and add portfolio documentation"`

---

## 1️⃣3️⃣ SCREENSHOT / OUTPUT CHECKLIST

Capture these items to enrich your GitHub repository:
1. **Directory Tree**: Screenshot of the project layout in your IDE.
2. **Terminal Output**: Capture the output of `python main.py --demo` showing the colorful metrics table.
3. **Hex Editor View**: Open the compressed `.huff` file in a hex editor or code preview to show the JSON metadata followed by binary markers.
4. **Directory File Size List**: A screenshot showing sizes side-by-side: `sample.txt` (large) vs. `sample.huff` (small).

---

## 1️⃣4️⃣ INTERVIEW PREPARATION (10 KEY QUESTIONS)

### Q1: Can you explain your project?
* **Elevator Pitch**: "I built CompressIQ — an intelligent file compression utility that achieves lossless compression using Huffman Coding. It parses file streams at the byte level, calculates character frequencies, builds a Huffman tree using a custom Min-Heap, and writes packed bits into a binary file. It includes a custom metadata header containing the frequencies to enable self-contained decompression."
* **DSA Focus**: Mention implementing the Min-Heap priority queue from scratch using array representation, highlighting bubble-up and bubble-down operations.
* **Systems Focus**: Explain bit-packing logic where dynamic bit lengths are grouped into 8-bit bytes to reduce physical file size, and the header format that prepends metadata size.

---

### Q2: Why did you implement a custom Min-Heap instead of using Python's built-in `heapq` module?
* **Technical Answer**: "I wanted to demonstrate a deep understanding of heap structures. Using library imports abstracts the underlying logic. By coding the Min-Heap, I showed how pointer math behaves in a flat array (`parent = (index-1)//2`) and how we maintain the heap property in $O(\log N)$ time through recursive bubble-down operations."
* **HR Answer**: "It shows that I don't just rely on high-level abstractions. In systems engineering, you often build custom memory allocators or specialized queues. Coding it from scratch shows I understand how these tools work under the hood."

---

### Q3: What is a prefix-free code, and why is it essential for Huffman Decompression?
* **Technical Answer**: "A prefix-free code ensures that no character's binary representation matches the beginning of another character's code. For example, if 'A' is `0` and 'B' is `01`, it is *not* prefix-free because 'A' is a prefix of 'B'. If we read `01`, we wouldn't know if it means 'A' followed by something else, or just 'B'. Huffman codes are prefix-free because characters only reside on the leaf nodes of the tree, ensuring there is a unique path from the root to each character."
* **HR Answer**: "Prefix-free coding removes ambiguity from stream reading. It is what allows us to read compressed files as a continuous stream of bits without using separator characters, saving significant file space."

---

### Q4: How does your utility handle the decompression of a file? How does it know how to reconstruct the tree?
* **Technical Answer**: "The compressed file contains a 4-byte header specifying the size of the serialized metadata. Following that is a JSON block containing the character frequency table. During decompression, we parse the JSON table and pass it to the tree building algorithm, which reconstructs the identical Huffman tree. We then read the bitstream and navigate down the tree (left on `0`, right on `1`) until we hit a leaf, which yields the original byte."
* **HR Answer**: "A compressed file must be self-contained. Prepending the frequency table as a header ensures the decompressor can rebuild the tree and restore the file without requiring external tables."

---

### Q5: How do you handle tie-breaking when two nodes have identical frequencies in the Min-Heap?
* **Technical Answer**: "In Python, comparing classes without a custom operator throws an error if they share equal keys. To solve this, I overrode the `__lt__` operator in the `HuffmanNode` class. If the frequencies are equal, we fall back to comparing the raw byte values. If one node is an internal node (no character) and the other is a leaf, we prioritize the leaf node to keep leaf paths shorter."
* **HR Answer**: "This demonstrates attention to edge cases. It prevents application crashes during heap sorting operations when different characters appear with the exact same frequency."

---

### Q6: Why could a compressed file occasionally become larger than the original file?
* **Technical Answer**: "This occurs in two scenarios: extremely small files or files with high entropy (like JPEG images or encrypted files). For small files, the metadata header containing the frequency table adds more bytes of overhead than the bit savings can recover. For high-entropy files, character distributions are uniform, meaning all characters get roughly 8-bit codes, resulting in no savings while still adding the header overhead."
* **HR Answer**: "It highlights the trade-offs of compression algorithms. Huffman coding relies on non-uniform character distribution. Knowing these limitations helps us decide when to apply compression."

---

### Q7: What are the time and space complexities of your compression algorithm?
* **Technical Answer**: "Let $N$ be the number of bytes in the file, and $U$ be the number of unique bytes (max 256 for a byte-level stream).
  * **Time Complexity**:
    * Frequency map calculation: $O(N)$
    * Heap creation: $O(U \log U)$
    * Tree construction: $O(U \log U)$
    * Codebook generation: $O(U)$
    * Bitstream encoding: $O(N)$
    * Total Time Complexity: $O(N + U \log U)$. Since $U \le 256$, the complexity is linear, $O(N)$.
  * **Space Complexity**:
    * Storing frequencies and codes: $O(U)$
    * Huffman tree storage: $O(U)$ nodes
    * Total Space Complexity: $O(U) \approx O(1)$ auxiliary space, excluding input/output buffers."
* **HR Answer**: "It is highly optimized. Because the alphabet size is bounded at 256 bytes, the tree building overhead is constant, and the performance scales linearly with the input file size."

---

### Q8: How did you pack the dynamic-length bits into bytes in Python?
* **Technical Answer**: "Since computer systems write data in bytes (groups of 8 bits), we cannot write individual bits directly to disk. I accumulated the generated Huffman bit strings into a long text string. I calculated the number of bits needed to pad the string to a multiple of 8. I then looped through this string in steps of 8, converted each 8-character block into an integer using `int(block, 2)`, and appended it to a `bytearray`. The padding count is saved in the header so we can discard the extra bits during decompression."
* **HR Answer**: "This shows system-level programming skills. It bridges the gap between high-level algorithms and low-level physical byte representation on disk."

---

### Q9: How would you scale this utility to compress files larger than the system's RAM (e.g., a 10 GB file)?
* **Technical Answer**: "Our current implementation loads the entire file into RAM, which will fail for files larger than memory. To scale this, we must process the file in chunks. We would first scan the file sequentially to count byte frequencies (requiring only $O(1)$ memory for the 256-byte counter). After building the tree, we would read the input file in streams, encode chunk by chunk, and write the output bit stream directly to disk using a buffered binary writer."
* **HR Answer**: "This shows system design thinking. A real-world application must handle resource constraints, and streaming buffers are key to processing large datasets efficiently."

---

### Q10: What are the differences between Huffman Coding and other algorithms like LZW (used in ZIP files)?
* **Technical Answer**: "Huffman coding is an entropy-encoding algorithm that replaces single characters with variable-length codes based on frequency. LZW (Lempel-Ziv-Welch) is a dictionary-based algorithm. It scans for repeated sequences of characters (e.g., 'the') and replaces them with a single index marker. LZW does not require storing a frequency table header, as the dictionary is built dynamically during decompression."
* **HR Answer**: "Huffman is excellent for character-frequency compression, whereas dictionary-based algorithms are better for files with repeating words and phrases. In modern ZIP tools, these algorithms are often combined (e.g., DEFLATE combines LZ77 and Huffman coding) to achieve maximum compression."
