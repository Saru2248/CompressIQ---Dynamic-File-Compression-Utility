"""
algorithms.py — Additional DSA Algorithms used in the Compression Pipeline
============================================================================

This module implements classic DSA algorithms that underpin, support, or
complement the Huffman Coding compression system. Each function is documented
with its time complexity, space complexity, and role in the overall system.

Algorithms Implemented:
  1.  Frequency Count       – O(n)         – Build the byte frequency table
  2.  Insertion Sort        – O(n²)        – Small-list sorting baseline
  3.  Merge Sort            – O(n log n)   – Production-grade frequency sorting
  4.  Binary Search         – O(log n)     – Locate a symbol in a sorted codebook
  5.  BFS Tree Traversal    – O(n)         – Level-order Huffman tree inspection
  6.  DFS Tree Traversal    – O(n)         – Pre-order code path generation
  7.  Greedy Merge Step     – O(log n)     – Core Huffman tree construction step
  8.  Entropy Calculator    – O(n)         – Shannon entropy & theoretical bound
  9.  Run-Length Encoding   – O(n)         – Bonus lossless algorithm for comparison
  10. Bit Packing           – O(n)         – Packs a binary string into bytes
"""

import math
from collections import deque


# ─────────────────────────────────────────────────────────────────────────────
# 1. FREQUENCY COUNTER — O(n) time, O(k) space  (k = number of unique bytes)
# ─────────────────────────────────────────────────────────────────────────────

def frequency_count(data: bytes) -> dict:
    """
    Scans a byte sequence once and builds a frequency table.

    This is the very first step of the Huffman pipeline. The resulting
    dictionary drives both the Min-Heap construction and the JSON metadata
    header that is embedded in every .huff file.

    Time  Complexity: O(n)  — single linear pass
    Space Complexity: O(k)  — at most 256 unique byte values

    Args:
        data (bytes): Raw input byte sequence.

    Returns:
        dict: {byte_value (int): frequency (int)} sorted descending by frequency.

    Example:
        >>> frequency_count(b"ABRACADABRA")
        {65: 5, 66: 2, 82: 2, 67: 1, 68: 1}
    """
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    # Return sorted descending — most frequent byte first
    return dict(sorted(freq.items(), key=lambda x: -x[1]))


# ─────────────────────────────────────────────────────────────────────────────
# 2. INSERTION SORT — O(n²) time, O(1) space
# ─────────────────────────────────────────────────────────────────────────────

def insertion_sort(arr: list, key=lambda x: x) -> list:
    """
    Stable, in-place insertion sort on a list.

    Best Case  (already sorted): O(n)
    Worst Case (reverse sorted): O(n²)
    Average Case:                O(n²)
    Space Complexity:            O(1) — in-place

    Used as a baseline comparison against Merge Sort for small frequency lists.

    Args:
        arr  (list): Mutable list of items to sort.
        key  (callable): Key function to extract comparison value.

    Returns:
        list: The same list sorted ascending by key (in-place).

    Example:
        >>> insertion_sort([(65,5),(66,2),(67,1)], key=lambda x: x[1])
        [(67, 1), (66, 2), (65, 5)]
    """
    for i in range(1, len(arr)):
        current = arr[i]
        j = i - 1
        while j >= 0 and key(arr[j]) > key(current):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = current
    return arr


# ─────────────────────────────────────────────────────────────────────────────
# 3. MERGE SORT — O(n log n) time, O(n) space
# ─────────────────────────────────────────────────────────────────────────────

def merge_sort(arr: list, key=lambda x: x) -> list:
    """
    Divide-and-conquer merge sort. Returns a new sorted list.

    Time  Complexity: O(n log n) — best, average, and worst case
    Space Complexity: O(n)       — creates sub-arrays on each recursive call

    Used to sort (byte, frequency) pairs before printing the codebook table,
    and to benchmark against Insertion Sort for the same task on small lists.

    Args:
        arr  (list): List of items to sort.
        key  (callable): Key function to extract comparison value.

    Returns:
        list: New list sorted ascending by key.
    """
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left  = merge_sort(arr[:mid], key)
    right = merge_sort(arr[mid:], key)
    return _merge(left, right, key)


def _merge(left: list, right: list, key) -> list:
    """Internal merge step for merge_sort."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 4. BINARY SEARCH — O(log n) time, O(1) space
# ─────────────────────────────────────────────────────────────────────────────

def binary_search(sorted_codes: list, target_byte: int) -> int:
    """
    Searches a sorted codebook list for a given byte value.

    Time  Complexity: O(log n)
    Space Complexity: O(1)

    This is used when looking up whether a specific byte symbol exists in a
    pre-sorted codebook without scanning the whole list linearly.

    Args:
        sorted_codes (list): List of (byte_value, code_string) tuples, sorted by byte_value.
        target_byte  (int):  The byte value (0-255) to search for.

    Returns:
        int: Index of the target in sorted_codes, or -1 if not found.
    """
    low, high = 0, len(sorted_codes) - 1

    while low <= high:
        mid = (low + high) // 2
        byte_val = sorted_codes[mid][0]

        if byte_val == target_byte:
            return mid
        elif byte_val < target_byte:
            low = mid + 1
        else:
            high = mid - 1

    return -1


# ─────────────────────────────────────────────────────────────────────────────
# 5. BFS TREE TRAVERSAL — O(n) time, O(w) space  (w = max tree width)
# ─────────────────────────────────────────────────────────────────────────────

def bfs_traversal(root) -> list:
    """
    Breadth-First Search (Level-Order) traversal of the Huffman Tree.

    Visits every node level by level — root first, then children, etc.
    This is the natural way to inspect a Huffman tree visually, because
    frequent characters (shorter codes) appear on higher levels.

    Time  Complexity: O(n) — every node visited exactly once
    Space Complexity: O(w) — queue holds at most one full level at a time

    Args:
        root (HuffmanNode): The root node of the Huffman tree.

    Returns:
        list of dicts: Each dict has keys:
            - 'level'   (int):  Depth level (root = 0)
            - 'char'    (int|None): Byte value if leaf, else None
            - 'freq'    (int):  Frequency sum at this node
            - 'is_leaf' (bool): True if this is a character node
    """
    if root is None:
        return []

    result = []
    queue = deque([(root, 0)])  # (node, level)

    while queue:
        node, level = queue.popleft()
        result.append({
            "level":   level,
            "char":    node.char,
            "freq":    node.freq,
            "is_leaf": node.is_leaf()
        })
        if node.left:
            queue.append((node.left, level + 1))
        if node.right:
            queue.append((node.right, level + 1))

    return result


# ─────────────────────────────────────────────────────────────────────────────
# 6. DFS TREE TRAVERSAL (Pre-Order) — O(n) time, O(h) space  (h = tree height)
# ─────────────────────────────────────────────────────────────────────────────

def dfs_traversal(root, path="") -> list:
    """
    Depth-First Search (Pre-Order) traversal of the Huffman Tree.

    Visits Root → Left → Right. This mirrors the exact recursive path used
    during code generation. Every leaf node's path from root IS the Huffman code
    for that character ('0' for left, '1' for right).

    Time  Complexity: O(n) — every node visited exactly once
    Space Complexity: O(h) — call stack depth equals tree height

    Args:
        root (HuffmanNode): The root node of the Huffman tree.
        path (str):         Binary path string accumulated so far (default "").

    Returns:
        list of dicts: Each dict has keys:
            - 'char'    (int|None): Byte value for leaf nodes, None for internal
            - 'freq'    (int):      Node frequency
            - 'code'    (str):      Binary path from root to this node
            - 'is_leaf' (bool):     True if this is a character node
    """
    if root is None:
        return []

    result = [{
        "char":    root.char,
        "freq":    root.freq,
        "code":    path,
        "is_leaf": root.is_leaf()
    }]

    result += dfs_traversal(root.left, path + "0")
    result += dfs_traversal(root.right, path + "1")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 7. GREEDY MERGE STEP — O(log n) per step, O(n log n) total
# ─────────────────────────────────────────────────────────────────────────────

def greedy_merge_steps(freq_table: dict) -> list:
    """
    Simulates the Greedy Huffman tree construction step-by-step.

    At each step, extracts the two minimum-frequency nodes, merges them into
    a parent, and records the state. This lets the dashboard animate each
    individual merge operation interactively.

    Time  Complexity: O(n log n) total — each of n steps costs O(log n) for heap ops
    Space Complexity: O(n)

    Args:
        freq_table (dict): {byte_value: frequency} mapping.

    Returns:
        list of dicts: One dict per merge step, containing:
            - 'step'     (int):   Step number (1-indexed)
            - 'merged_a' (dict):  First extracted node info
            - 'merged_b' (dict):  Second extracted node info
            - 'result'   (dict):  New parent node info
            - 'heap_size'(int):   Remaining heap size after merge
    """
    import heapq

    # Use (freq, tiebreaker_id, char_or_none) tuples for Python's heapq
    counter = 0
    heap = []
    for byte_val, freq in freq_table.items():
        heapq.heappush(heap, (freq, counter, byte_val, "leaf"))
        counter += 1

    steps = []
    step_num = 1

    while len(heap) > 1:
        freq_a, _, char_a, type_a = heapq.heappop(heap)
        freq_b, _, char_b, type_b = heapq.heappop(heap)

        merged_freq = freq_a + freq_b
        heapq.heappush(heap, (merged_freq, counter, None, "internal"))
        counter += 1

        steps.append({
            "step":      step_num,
            "merged_a":  {"char": char_a, "freq": freq_a, "type": type_a},
            "merged_b":  {"char": char_b, "freq": freq_b, "type": type_b},
            "result":    {"char": None,   "freq": merged_freq, "type": "internal"},
            "heap_size": len(heap)
        })
        step_num += 1

    return steps


# ─────────────────────────────────────────────────────────────────────────────
# 8. SHANNON ENTROPY CALCULATOR — O(n) time, O(k) space
# ─────────────────────────────────────────────────────────────────────────────

def shannon_entropy(data: bytes) -> dict:
    """
    Calculates the Shannon entropy of a byte sequence.

    Shannon entropy defines the theoretical minimum average bits-per-symbol
    needed to encode data without loss. Huffman coding achieves within 1 bit
    of this theoretical bound.

        H(X) = -Σ P(x) * log₂(P(x))

    Time  Complexity: O(n)
    Space Complexity: O(k) — k unique symbols

    Args:
        data (bytes): Raw input bytes.

    Returns:
        dict with keys:
            - 'entropy'        (float): Shannon entropy in bits/symbol
            - 'theoretical_min'(float): Minimum bits needed to represent all data
            - 'current_bits'   (int):   Bits used by uncompressed data (8 * n)
            - 'max_savings_pct'(float): Theoretical maximum compression %
    """
    if not data:
        return {"entropy": 0.0, "theoretical_min": 0, "current_bits": 0, "max_savings_pct": 0.0}

    freq = frequency_count(data)
    n = len(data)

    entropy = 0.0
    for count in freq.values():
        p = count / n
        if p > 0:
            entropy -= p * math.log2(p)

    theoretical_min = entropy * n
    current_bits    = n * 8
    max_savings_pct = ((current_bits - theoretical_min) / current_bits) * 100

    return {
        "entropy":         round(entropy, 4),
        "theoretical_min": round(theoretical_min, 2),
        "current_bits":    current_bits,
        "max_savings_pct": round(max_savings_pct, 2)
    }


# ─────────────────────────────────────────────────────────────────────────────
# 9. RUN-LENGTH ENCODING (RLE) — O(n) time, O(n) space
# ─────────────────────────────────────────────────────────────────────────────

def run_length_encode(data: bytes) -> bytes:
    """
    Run-Length Encoding — a simple lossless compression baseline.

    Consecutive identical bytes are replaced with (count, byte) pairs.
    This algorithm is very fast but only effective on data with long runs
    of repeated values (e.g., BMP images, certain binary formats).

    Huffman coding consistently outperforms RLE on natural language text.

    Time  Complexity: O(n)
    Space Complexity: O(n) in worst case (no repetition)

    Args:
        data (bytes): Raw input bytes.

    Returns:
        bytes: RLE-encoded payload.
    """
    if not data:
        return b""

    encoded = bytearray()
    i = 0
    while i < len(data):
        current_byte = data[i]
        count = 1
        while i + count < len(data) and data[i + count] == current_byte and count < 255:
            count += 1
        encoded.append(count)
        encoded.append(current_byte)
        i += count

    return bytes(encoded)


def run_length_decode(encoded: bytes) -> bytes:
    """
    Decodes a Run-Length Encoded byte stream back to original data.

    Time  Complexity: O(n)
    Space Complexity: O(n)

    Args:
        encoded (bytes): RLE-encoded bytes from run_length_encode().

    Returns:
        bytes: Original decoded byte sequence.
    """
    if not encoded:
        return b""

    decoded = bytearray()
    for i in range(0, len(encoded), 2):
        count = encoded[i]
        byte  = encoded[i + 1]
        decoded.extend([byte] * count)

    return bytes(decoded)


# ─────────────────────────────────────────────────────────────────────────────
# 10. BIT PACKING — O(n) time, O(n/8) space
# ─────────────────────────────────────────────────────────────────────────────

def pack_bits(bit_string: str) -> tuple:
    """
    Converts a binary string (e.g. "10110010") into a compact byte array.

    This is the final step of the Huffman compression pipeline — converting
    the long string of '0's and '1's into actual physical bytes so that
    compressed files are genuinely smaller on disk.

    Without this step, writing '0' and '1' as characters would actually
    INCREASE file size by 8× vs. the original.

    Time  Complexity: O(n) — one pass over the bit string
    Space Complexity: O(n/8) — output is 8× smaller than input string

    Args:
        bit_string (str): A string containing only '0' and '1' characters.

    Returns:
        tuple: (packed_bytes: bytes, padding: int)
            - packed_bytes: The byte-packed binary data.
            - padding: Number of '0' bits appended to reach a multiple of 8.
    """
    # Calculate how many padding bits are needed
    padding = (8 - len(bit_string) % 8) % 8
    bit_string += "0" * padding

    packed = bytearray()
    for i in range(0, len(bit_string), 8):
        byte_val = int(bit_string[i:i+8], 2)
        packed.append(byte_val)

    return bytes(packed), padding


def unpack_bits(packed_bytes: bytes, padding: int) -> str:
    """
    Converts a packed byte array back to its original bit string.

    Time  Complexity: O(n)
    Space Complexity: O(8n) — output is 8× larger than input

    Args:
        packed_bytes (bytes): Byte array from pack_bits().
        padding      (int):   Number of padding bits to strip from the end.

    Returns:
        str: The original binary string without padding.
    """
    bit_string = "".join(f"{byte:08b}" for byte in packed_bytes)
    if padding > 0:
        bit_string = bit_string[:-padding]
    return bit_string
