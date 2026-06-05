"""
test_compression.py — Full Unit Test Suite
============================================
Tests every DSA algorithm and integration path in the project:

  Group 1 – TestMinHeap          : Heap ordering, tie-breakers, empty edge cases
  Group 2 – TestHuffmanCoding    : Byte-level lossless compression/decompression
  Group 3 – TestFileIntegration  : File path compress_file / decompress_file
  Group 4 – TestFrequencyCount   : Linear byte frequency scanner
  Group 5 – TestSortingAlgorithms: Insertion Sort vs Merge Sort correctness
  Group 6 – TestBinarySearch     : Sorted codebook binary search
  Group 7 – TestTreeTraversals   : BFS level-order & DFS pre-order on Huffman tree
  Group 8 – TestGreedyMerge      : Step-by-step greedy merge simulation
  Group 9 – TestShannonEntropy   : Entropy formula and theoretical bounds
  Group 10– TestRunLengthEncoding: RLE encode/decode round-trip
  Group 11– TestBitPacking       : Bit string pack/unpack round-trip
"""

import unittest
import os
import tempfile

from src.heap import MinHeap
from src.node import HuffmanNode
from src.huffman import HuffmanCoding
from src.algorithms import (
    frequency_count,
    insertion_sort,
    merge_sort,
    binary_search,
    bfs_traversal,
    dfs_traversal,
    greedy_merge_steps,
    shannon_entropy,
    run_length_encode,
    run_length_decode,
    pack_bits,
    unpack_bits,
)


# ─────────────────────────────────────────────────────────────────────────────
# Group 1 — Min-Heap (Priority Queue)
# ─────────────────────────────────────────────────────────────────────────────
class TestMinHeap(unittest.TestCase):

    def test_heap_ascending_order(self):
        """Extractions must come out in strictly ascending frequency order."""
        heap = MinHeap()
        for freq in [50, 10, 25, 5, 30]:
            heap.insert(HuffmanNode(None, freq))

        extracted = [heap.extract_min().freq for _ in range(5)]
        self.assertEqual(extracted, sorted(extracted))

    def test_heap_tie_breaker_by_char(self):
        """When frequencies are equal, lower ASCII byte value wins."""
        heap = MinHeap()
        heap.insert(HuffmanNode(ord('y'), 10))
        heap.insert(HuffmanNode(ord('a'), 10))
        heap.insert(HuffmanNode(ord('m'), 10))

        # ASCII: 'a'=97 < 'm'=109 < 'y'=121
        self.assertEqual(heap.extract_min().char, ord('a'))
        self.assertEqual(heap.extract_min().char, ord('m'))
        self.assertEqual(heap.extract_min().char, ord('y'))

    def test_heap_empty_after_extractions(self):
        """Heap must report empty after all elements are extracted."""
        heap = MinHeap()
        heap.insert(HuffmanNode(ord('x'), 1))
        heap.extract_min()
        self.assertTrue(heap.is_empty())

    def test_heap_single_element(self):
        """A single-element heap must return that element and then be empty."""
        heap = MinHeap()
        node = HuffmanNode(ord('A'), 99)
        heap.insert(node)
        extracted = heap.extract_min()
        self.assertEqual(extracted.freq, 99)
        self.assertTrue(heap.is_empty())


# ─────────────────────────────────────────────────────────────────────────────
# Group 2 — Huffman Coding Core (byte-level)
# ─────────────────────────────────────────────────────────────────────────────
class TestHuffmanCoding(unittest.TestCase):

    def setUp(self):
        self.huffman = HuffmanCoding()

    def test_lossless_on_natural_text(self):
        """Compress/decompress a natural English sentence with no data loss."""
        original = b"The quick brown fox jumps over the lazy dog."
        compressed   = self.huffman.compress(original)
        decompressed = self.huffman.decompress(compressed)
        self.assertEqual(original, decompressed)

    def test_lossless_on_repeated_bytes(self):
        """Works correctly on inputs with repeated byte patterns."""
        original = b"a" * 200 + b"b" * 100 + b"c" * 50
        compressed   = self.huffman.compress(original)
        decompressed = self.huffman.decompress(compressed)
        self.assertEqual(original, decompressed)

    def test_lossless_on_full_byte_range(self):
        """Handles all 256 possible byte values — true binary file support."""
        original = bytes(range(256)) * 4
        compressed   = self.huffman.compress(original)
        decompressed = self.huffman.decompress(compressed)
        self.assertEqual(original, decompressed)

    def test_single_unique_byte_edge_case(self):
        """Only one unique byte in the stream — single-leaf tree edge case."""
        original = b"AAAAAAAAAA"
        compressed   = self.huffman.compress(original)
        decompressed = self.huffman.decompress(compressed)
        self.assertEqual(original, decompressed)

    def test_empty_input_edge_case(self):
        """Empty byte string must round-trip as empty with no error."""
        original     = b""
        compressed   = self.huffman.compress(original)
        decompressed = self.huffman.decompress(compressed)
        self.assertEqual(original, decompressed)

    def test_compressed_is_smaller_for_large_text(self):
        """For sufficiently long natural text, compressed size < original size."""
        original = (b"Huffman coding achieves lossless data compression. " * 20)
        compressed = self.huffman.compress(original)
        self.assertLess(len(compressed), len(original),
                        "Compressed payload should be smaller than original for repetitive text.")

    def test_frequent_char_has_shorter_code(self):
        """The most frequent character should receive the shortest Huffman code."""
        # 'a' appears 100×, 'z' only 1×
        original = b"a" * 100 + b"z"
        self.huffman.compress(original)
        len_a = len(self.huffman.codes[ord('a')])
        len_z = len(self.huffman.codes[ord('z')])
        self.assertLessEqual(len_a, len_z,
                             "Most frequent byte must have code length <= rarest byte's code length.")


# ─────────────────────────────────────────────────────────────────────────────
# Group 3 — File-Level Integration
# ─────────────────────────────────────────────────────────────────────────────
class TestFileIntegration(unittest.TestCase):

    def test_compress_file_and_decompress_file(self):
        """compress_file → decompress_file must restore exact bytes on disk."""
        huffman  = HuffmanCoding()
        original = b"Integration test: dynamic file compression round-trip validation."

        with tempfile.TemporaryDirectory() as tmpdir:
            src  = os.path.join(tmpdir, "source.txt")
            comp = os.path.join(tmpdir, "source.txt.huff")
            rec  = os.path.join(tmpdir, "recovered.txt")

            with open(src, "wb") as f:
                f.write(original)

            orig_size, comp_size = huffman.compress_file(src, comp)
            self.assertTrue(os.path.exists(comp))
            self.assertEqual(orig_size, len(original))

            recovered_size = huffman.decompress_file(comp, rec)
            self.assertTrue(os.path.exists(rec))
            self.assertEqual(recovered_size, len(original))

            with open(rec, "rb") as f:
                recovered = f.read()

            self.assertEqual(original, recovered,
                             "File-level decompression must be byte-for-byte identical to original.")


# ─────────────────────────────────────────────────────────────────────────────
# Group 4 — Frequency Count
# ─────────────────────────────────────────────────────────────────────────────
class TestFrequencyCount(unittest.TestCase):

    def test_correct_counts(self):
        result = frequency_count(b"ABRACADABRA")
        self.assertEqual(result[ord('A')], 5)
        self.assertEqual(result[ord('B')], 2)
        self.assertEqual(result[ord('R')], 2)
        self.assertEqual(result[ord('C')], 1)
        self.assertEqual(result[ord('D')], 1)

    def test_sorted_descending(self):
        result = frequency_count(b"ABRACADABRA")
        freqs  = list(result.values())
        self.assertEqual(freqs, sorted(freqs, reverse=True))

    def test_empty_input(self):
        self.assertEqual(frequency_count(b""), {})


# ─────────────────────────────────────────────────────────────────────────────
# Group 5 — Sorting Algorithms
# ─────────────────────────────────────────────────────────────────────────────
class TestSortingAlgorithms(unittest.TestCase):

    DATA = [(ord('z'), 1), (ord('a'), 5), (ord('m'), 3), (ord('b'), 5)]

    def test_insertion_sort_ascending(self):
        result = insertion_sort(list(self.DATA), key=lambda x: x[1])
        freqs  = [r[1] for r in result]
        self.assertEqual(freqs, sorted(freqs))

    def test_merge_sort_ascending(self):
        result = merge_sort(list(self.DATA), key=lambda x: x[1])
        freqs  = [r[1] for r in result]
        self.assertEqual(freqs, sorted(freqs))

    def test_insertion_sort_empty(self):
        self.assertEqual(insertion_sort([]), [])

    def test_merge_sort_single_element(self):
        self.assertEqual(merge_sort([(65, 10)]), [(65, 10)])

    def test_both_sorts_produce_identical_results(self):
        ins  = insertion_sort(list(self.DATA), key=lambda x: x[1])
        mrg  = merge_sort(list(self.DATA), key=lambda x: x[1])
        self.assertEqual([r[1] for r in ins], [r[1] for r in mrg])


# ─────────────────────────────────────────────────────────────────────────────
# Group 6 — Binary Search
# ─────────────────────────────────────────────────────────────────────────────
class TestBinarySearch(unittest.TestCase):

    CODEBOOK = [(65, "0"), (66, "10"), (67, "110"), (68, "1110"), (90, "1111")]

    def test_finds_existing_byte(self):
        idx = binary_search(self.CODEBOOK, 67)
        self.assertEqual(idx, 2)

    def test_first_element(self):
        self.assertEqual(binary_search(self.CODEBOOK, 65), 0)

    def test_last_element(self):
        self.assertEqual(binary_search(self.CODEBOOK, 90), 4)

    def test_missing_byte_returns_minus_one(self):
        self.assertEqual(binary_search(self.CODEBOOK, 99), -1)

    def test_empty_codebook(self):
        self.assertEqual(binary_search([], 65), -1)


# ─────────────────────────────────────────────────────────────────────────────
# Group 7 — Tree Traversals
# ─────────────────────────────────────────────────────────────────────────────
class TestTreeTraversals(unittest.TestCase):

    def _build_tree(self):
        huffman = HuffmanCoding()
        huffman.compress(b"ABRACADABRA")
        return huffman.root

    def test_bfs_visits_all_nodes(self):
        root   = self._build_tree()
        result = bfs_traversal(root)
        # All nodes visited and root is level 0
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["level"], 0)

    def test_bfs_level_order(self):
        root   = self._build_tree()
        result = bfs_traversal(root)
        levels = [r["level"] for r in result]
        # Levels must be non-decreasing
        self.assertEqual(levels, sorted(levels))

    def test_dfs_leaf_codes_match_huffman_codes(self):
        huffman = HuffmanCoding()
        huffman.compress(b"ABRACADABRA")
        result = dfs_traversal(huffman.root)

        leaf_codes = {r["char"]: r["code"] for r in result if r["is_leaf"]}
        for byte_val, code in huffman.codes.items():
            self.assertEqual(leaf_codes[byte_val], code,
                             f"DFS path for byte {byte_val} must match Huffman codebook.")

    def test_bfs_on_empty_tree(self):
        self.assertEqual(bfs_traversal(None), [])

    def test_dfs_on_empty_tree(self):
        self.assertEqual(dfs_traversal(None), [])


# ─────────────────────────────────────────────────────────────────────────────
# Group 8 — Greedy Merge Steps
# ─────────────────────────────────────────────────────────────────────────────
class TestGreedyMerge(unittest.TestCase):

    def test_step_count(self):
        """n unique symbols → n-1 merge steps to build the tree."""
        freq = {65: 5, 66: 2, 67: 1, 68: 1, 82: 2}  # 5 unique chars
        steps = greedy_merge_steps(freq)
        self.assertEqual(len(steps), len(freq) - 1)

    def test_merged_frequencies_sum(self):
        """Each result frequency must equal the sum of its two input frequencies."""
        freq  = {65: 5, 66: 3, 67: 1}
        steps = greedy_merge_steps(freq)
        for step in steps:
            expected = step["merged_a"]["freq"] + step["merged_b"]["freq"]
            self.assertEqual(step["result"]["freq"], expected)

    def test_heap_size_decreases(self):
        """Heap shrinks by 1 at each step (two removed, one inserted)."""
        freq  = {65: 5, 66: 3, 67: 2, 68: 1}
        steps = greedy_merge_steps(freq)
        sizes = [s["heap_size"] for s in steps]
        self.assertEqual(sizes, sorted(sizes, reverse=True))


# ─────────────────────────────────────────────────────────────────────────────
# Group 9 — Shannon Entropy
# ─────────────────────────────────────────────────────────────────────────────
class TestShannonEntropy(unittest.TestCase):

    def test_uniform_distribution_max_entropy(self):
        """All bytes equally likely → entropy close to log₂(k) for k symbols."""
        # 4 equally likely symbols → entropy should be close to 2.0
        data   = bytes([0, 1, 2, 3] * 100)
        result = shannon_entropy(data)
        self.assertAlmostEqual(result["entropy"], 2.0, places=4)

    def test_single_symbol_zero_entropy(self):
        """One repeated symbol → entropy is 0 (perfectly predictable)."""
        result = shannon_entropy(b"A" * 100)
        self.assertEqual(result["entropy"], 0.0)

    def test_empty_data(self):
        result = shannon_entropy(b"")
        self.assertEqual(result["entropy"], 0.0)

    def test_max_savings_between_0_and_100(self):
        result = shannon_entropy(b"Hello World! " * 50)
        self.assertGreaterEqual(result["max_savings_pct"], 0.0)
        self.assertLessEqual(result["max_savings_pct"], 100.0)


# ─────────────────────────────────────────────────────────────────────────────
# Group 10 — Run-Length Encoding
# ─────────────────────────────────────────────────────────────────────────────
class TestRunLengthEncoding(unittest.TestCase):

    def test_encode_decode_roundtrip(self):
        original  = b"AAABBBCCDDDDEE"
        encoded   = run_length_encode(original)
        recovered = run_length_decode(encoded)
        self.assertEqual(original, recovered)

    def test_rle_compresses_long_runs(self):
        """RLE should make runs of identical bytes smaller."""
        original = b"A" * 100
        encoded  = run_length_encode(original)
        self.assertLess(len(encoded), len(original))

    def test_empty_roundtrip(self):
        self.assertEqual(run_length_decode(run_length_encode(b"")), b"")


# ─────────────────────────────────────────────────────────────────────────────
# Group 11 — Bit Packing
# ─────────────────────────────────────────────────────────────────────────────
class TestBitPacking(unittest.TestCase):

    def test_pack_unpack_roundtrip(self):
        original_bits = "10110010110010110010"
        packed, padding = pack_bits(original_bits)
        recovered       = unpack_bits(packed, padding)
        self.assertEqual(original_bits, recovered)

    def test_multiple_of_8_no_padding(self):
        bits           = "10110010"  # Already 8 bits
        packed, padding = pack_bits(bits)
        self.assertEqual(padding, 0)
        self.assertEqual(len(packed), 1)

    def test_empty_bit_string(self):
        packed, padding = pack_bits("")
        self.assertEqual(packed, b"")
        self.assertEqual(padding, 0)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    unittest.main(verbosity=2)
