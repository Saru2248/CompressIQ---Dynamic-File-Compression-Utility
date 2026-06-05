/**
 * Dynamic File Compression Utility - JavaScript Frontend Engine
 * Implements Huffman Coding with a Custom Min-Heap.
 * Maintains full binary compatibility with the Python CLI backend.
 */

// --- DATA STRUCTURES (DSA IMPLEMENTATION) ---

class HuffmanNode {
    constructor(char, freq) {
        this.char = char;   // Integer byte value (0-255) or null for internal nodes
        this.freq = freq;   // Frequency count
        this.left = null;   // Left child reference
        this.right = null;  // Right child reference
    }

    isLeaf() {
        return this.left === null && this.right === null;
    }
}

class MinHeap {
    constructor() {
        this.heap = [];
    }

    parent(i) { return Math.floor((i - 1) / 2); }
    leftChild(i) { return 2 * i + 1; }
    rightChild(i) { return 2 * i + 2; }

    swap(i, j) {
        const temp = this.heap[i];
        this.heap[i] = this.heap[j];
        this.heap[j] = temp;
    }

    size() {
        return this.heap.length;
    }

    isEmpty() {
        return this.heap.length === 0;
    }

    insert(node) {
        this.heap.push(node);
        this.heapifyUp(this.heap.length - 1);
    }

    extractMin() {
        if (this.isEmpty()) return null;
        if (this.heap.length === 1) return this.heap.pop();

        const min = this.heap[0];
        this.heap[0] = this.heap.pop();
        this.heapifyDown(0);
        return min;
    }

    heapifyUp(i) {
        let parentIdx = this.parent(i);
        while (i > 0 && this.compare(this.heap[i], this.heap[parentIdx]) < 0) {
            this.swap(i, parentIdx);
            i = parentIdx;
            parentIdx = this.parent(i);
        }
    }

    heapifyDown(i) {
        let smallest = i;
        const left = this.leftChild(i);
        const right = this.rightChild(i);
        const n = this.heap.length;

        if (left < n && this.compare(this.heap[left], this.heap[smallest]) < 0) {
            smallest = left;
        }
        if (right < n && this.compare(this.heap[right], this.heap[smallest]) < 0) {
            smallest = right;
        }

        if (smallest !== i) {
            this.swap(i, smallest);
            this.heapifyDown(smallest);
        }
    }

    /**
     * Node comparator. Compares node frequencies.
     * Tie-breaker: compares byte values. Leaf nodes take priority over internal nodes.
     */
    compare(nodeA, nodeB) {
        if (nodeA.freq !== nodeB.freq) {
            return nodeA.freq - nodeB.freq;
        }
        // Tie-breaker
        if (nodeA.char !== null && nodeB.char !== null) {
            return nodeA.char - nodeB.char;
        }
        if (nodeA.char !== null) return -1; // Leaf node comes first
        if (nodeB.char !== null) return 1;
        return 0;
    }
}

// --- HUFFMAN CODING ENGINE ---

class HuffmanCoding {
    constructor() {
        this.freqTable = {};
        this.codes = {};
        this.root = null;
    }

    buildFrequencyTable(uint8Array) {
        const freq = {};
        for (let i = 0; i < uint8Array.length; i++) {
            const byte = uint8Array[i];
            freq[byte] = (freq[byte] || 0) + 1;
        }
        return freq;
    }

    buildHuffmanTree(freqTable) {
        const heap = new MinHeap();
        
        for (const [byteStr, count] of Object.entries(freqTable)) {
            const node = new HuffmanNode(parseInt(byteStr), count);
            heap.insert(node);
        }

        if (heap.size() === 0) return null;

        // Edge case: single unique byte
        if (heap.size() === 1) {
            const left = heap.extractMin();
            const parent = new HuffmanNode(null, left.freq);
            parent.left = left;
            heap.insert(parent);
        }

        while (heap.size() > 1) {
            const node1 = heap.extractMin();
            const node2 = heap.extractMin();

            const parent = new HuffmanNode(null, node1.freq + node2.freq);
            parent.left = node1;
            parent.right = node2;
            heap.insert(parent);
        }

        return heap.extractMin();
    }

    generateCodes(node, currentCode = "") {
        if (!node) return;

        if (node.isLeaf()) {
            this.codes[node.char] = currentCode;
            return;
        }

        this.generateCodes(node.left, currentCode + "0");
        this.generateCodes(node.right, currentCode + "1");
    }

    /**
     * Compresses bytes and returns a binary-compatible Uint8Array payload.
     * Binary Format:
     * - [Header Size (4 Bytes, Big Endian)]
     * - [JSON Metadata String]
     * - [Padded packed bits]
     */
    compress(uint8Array) {
        if (uint8Array.length === 0) return new Uint8Array(0);

        // 1. Calculate Frequencies
        this.freqTable = this.buildFrequencyTable(uint8Array);

        // 2. Build Huffman Tree
        this.root = this.buildHuffmanTree(this.freqTable);

        // 3. Generate Codes
        this.codes = {};
        this.generateCodes(this.root, "");

        // 4. Create Bit String
        let bitString = "";
        for (let i = 0; i < uint8Array.length; i++) {
            bitString += this.codes[uint8Array[i]];
        }

        // 5. Pad Bit String to multiple of 8
        const padding = (8 - (bitString.length % 8)) % 8;
        bitString += "0".repeat(padding);

        // 6. Convert bit string to packed byte array
        const packedBytes = new Uint8Array(bitString.length / 8);
        for (let i = 0; i < bitString.length; i += 8) {
            packedBytes[i / 8] = parseInt(bitString.slice(i, i + 8), 2);
        }

        // 7. Prepare JSON Metadata Header
        const metadata = {
            freq: {},
            padding: padding
        };
        for (const [k, v] of Object.entries(this.freqTable)) {
            metadata.freq[k] = v;
        }

        const encoder = new TextEncoder();
        const metadataBytes = encoder.encode(JSON.stringify(metadata));
        const metadataLen = metadataBytes.length;

        // 8. Assemble combined buffer: [4-Byte Header Len] + [Header] + [Data]
        const combined = new Uint8Array(4 + metadataLen + packedBytes.length);
        const view = new DataView(combined.buffer);
        
        // Write 4-byte length in big endian
        view.setUint32(0, metadataLen, false);
        
        // Copy JSON bytes
        combined.set(metadataBytes, 4);
        
        // Copy packed data bytes
        combined.set(packedBytes, 4 + metadataLen);

        return combined;
    }

    /**
     * Decompresses raw compressed bytes back to original Uint8Array.
     */
    decompress(compressedBytes) {
        if (compressedBytes.length < 4) return new Uint8Array(0);

        const view = new DataView(compressedBytes.buffer, compressedBytes.byteOffset, compressedBytes.byteLength);
        const metadataLen = view.getUint32(0, false);

        // Extract metadata bytes and decode
        const metadataBytes = compressedBytes.slice(4, 4 + metadataLen);
        const decoder = new TextDecoder();
        const metadata = JSON.parse(decoder.decode(metadataBytes));

        const freqTable = {};
        for (const [k, v] of Object.entries(metadata.freq)) {
            freqTable[parseInt(k)] = v;
        }
        const padding = metadata.padding;

        // Rebuild Tree
        this.root = this.buildHuffmanTree(freqTable);
        if (!this.root) return new Uint8Array(0);

        // Extract bit stream
        const bitData = compressedBytes.slice(4 + metadataLen);
        let bitString = "";
        for (let i = 0; i < bitData.length; i++) {
            // Convert byte to 8-character binary representation
            bitString += bitData[i].toString(2).padStart(8, '0');
        }

        // Strip padding bits
        if (padding > 0) {
            bitString = bitString.slice(0, -padding);
        }

        // Decode bit stream using Tree Traversal
        const decodedBytes = [];
        let currNode = this.root;
        for (let i = 0; i < bitString.length; i++) {
            const bit = bitString[i];
            currNode = bit === '0' ? currNode.left : currNode.right;

            if (currNode.isLeaf()) {
                decodedBytes.push(currNode.char);
                currNode = this.root;
            }
        }

        return new Uint8Array(decodedBytes);
    }
}

// --- INTERACTIVE DASHBOARD SYSTEM CONTROLLER ---

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const navButtons = document.querySelectorAll(".nav-btn");
    const tabPanels = document.querySelectorAll(".tab-panel");
    const currentTabTitle = document.getElementById("current-tab-title");
    const currentTabDesc = document.getElementById("current-tab-desc");

    const btnInputText = document.getElementById("btn-input-text");
    const btnInputFile = document.getElementById("btn-input-file");
    const groupText = document.getElementById("group-text");
    const groupFile = document.getElementById("group-file");
    
    const textInput = document.getElementById("text-input");
    const compressDropzone = document.getElementById("compress-dropzone");
    const compressFileInput = document.getElementById("compress-file-input");
    const compressFileDetails = document.getElementById("compress-file-details");
    const cFileName = document.getElementById("c-file-name");
    const cFileSize = document.getElementById("c-file-size");
    const btnClearCompress = document.getElementById("btn-clear-compress");

    const btnCompressAction = document.getElementById("btn-compress-action");

    // Metrics Elements
    const metricOrigSize = document.getElementById("metric-orig-size");
    const metricCompSize = document.getElementById("metric-comp-size");
    const metricSaved = document.getElementById("metric-saved");
    const compressionProgress = document.getElementById("compression-progress");
    const progressDesc = document.getElementById("progress-desc");
    const metricRatio = document.getElementById("metric-ratio");
    
    const uniqueCharCount = document.getElementById("unique-char-count");
    const codebookTableBody = document.querySelector("#codebook-table tbody");

    // Decompress Tab Elements
    const decompressDropzone = document.getElementById("decompress-dropzone");
    const decompressFileInput = document.getElementById("decompress-file-input");
    const decompressFileDetails = document.getElementById("decompress-file-details");
    const dFileName = document.getElementById("d-file-name");
    const dFileSize = document.getElementById("d-file-size");
    const btnClearDecompress = document.getElementById("btn-clear-decompress");
    const btnDecompressAction = document.getElementById("btn-decompress-action");

    const decompressResultBox = document.getElementById("decompress-result-box");
    const decompressPreview = document.getElementById("decompress-preview");
    const btnDownloadRecovered = document.getElementById("btn-download-recovered");

    // Tree SVG Elements — now controlled exclusively by the Multi-Tree Visualizer IIFE

    // Global states
    let activeInputType = "text"; // "text" or "file"
    let rawInputBytes = new Uint8Array(0);
    let originalFileName = "compressed_output.txt";
    let compressedPayload = null; // Uint8Array
    let uploadedCompressedBytes = null; // Uint8Array
    let decompressedPayload = null; // Uint8Array
    let huffmanCoder = new HuffmanCoding();

    // Tab Navigation
    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            navButtons.forEach(b => b.classList.remove("active"));
            tabPanels.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const tabId = btn.getAttribute("data-tab");
            document.getElementById(`${tabId}-tab`).classList.add("active");

            // Update header info dynamically
            switch(tabId) {
                case "compress":
                    currentTabTitle.innerText = "Compression Dashboard";
                    currentTabDesc.innerText = "Analyze and compress text streams or local files";
                    break;
                case "decompress":
                    currentTabTitle.innerText = "Decompression Portal";
                    currentTabDesc.innerText = "Unpack and restore original files from binary .huff archives";
                    break;
                case "visualizer":
                    currentTabTitle.innerText = "DSA Tree Structure Explorer";
                    currentTabDesc.innerText = "Visualize 5 fundamental tree data structures live";
                    break;
                case "algorithms":
                    currentTabTitle.innerText = "DSA Algorithm Explorer";
                    currentTabDesc.innerText = "Run all 10 algorithms live on any input text and inspect their outputs";
                    break;
                case "workbook":
                    currentTabTitle.innerText = "Concept Guide & Handbook";
                    currentTabDesc.innerText = "Learn the computer science theory and binary design behind file encoding";
                    break;
            }
        });
    });

    // Input Source Toggle
    btnInputText.addEventListener("click", () => {
        btnInputText.classList.add("active");
        btnInputFile.classList.remove("active");
        groupText.classList.add("active");
        groupFile.classList.remove("active");
        activeInputType = "text";
        processTextAnalysis();
    });

    btnInputFile.addEventListener("click", () => {
        btnInputFile.classList.add("active");
        btnInputText.classList.remove("active");
        groupFile.classList.add("active");
        groupText.classList.remove("active");
        activeInputType = "file";
        clearTextAnalysis();
    });

    // --- COMPRESSION PIPELINE INPUT LISTENERS ---

    // Real-time Textarea Analysis
    textInput.addEventListener("input", () => {
        if (activeInputType === "text") {
            processTextAnalysis();
        }
    });

    function processTextAnalysis() {
        const text = textInput.value;
        const encoder = new TextEncoder();
        rawInputBytes = encoder.encode(text);
        originalFileName = "compressed.txt";
        updateLiveAnalysis();
    }

    function clearTextAnalysis() {
        rawInputBytes = new Uint8Array(0);
        updateLiveAnalysis();
    }

    // Drag-and-Drop Dropzone
    setupDragDrop(compressDropzone, compressFileInput, (file) => {
        originalFileName = file.name;
        const reader = new FileReader();
        reader.onload = (e) => {
            rawInputBytes = new Uint8Array(e.target.result);
            
            // Show details Card
            compressDropzone.style.display = "none";
            compressFileDetails.style.display = "flex";
            cFileName.innerText = file.name;
            cFileSize.innerText = formatSize(rawInputBytes.length);
            
            updateLiveAnalysis();
        };
        reader.readAsArrayBuffer(file);
    });

    btnClearCompress.addEventListener("click", () => {
        compressFileInput.value = "";
        compressFileDetails.style.display = "none";
        compressDropzone.style.display = "flex";
        rawInputBytes = new Uint8Array(0);
        updateLiveAnalysis();
    });

    // --- COMPRESSION MATH & UI UPDATER ---

    function updateLiveAnalysis() {
        if (rawInputBytes.length === 0) {
            resetMetrics();
            return;
        }

        // 1. Run quick compression in memory to show stats
        const tempCoder = new HuffmanCoding();
        const compressed = tempCoder.compress(rawInputBytes);
        
        const origSize = rawInputBytes.length;
        const compSize = compressed.length;
        const ratio = origSize / compSize;
        const savings = ((origSize - compSize) / origSize) * 100;

        // 2. Render Metrics Cards
        metricOrigSize.innerText = formatSize(origSize);
        metricCompSize.innerText = formatSize(compSize);
        
        if (savings >= 0) {
            metricSaved.innerText = `${savings.toFixed(1)}%`;
            metricSaved.className = "metric-val highlight";
            compressionProgress.style.width = `${savings}%`;
            progressDesc.innerText = `Compression saves ${formatSize(origSize - compSize)} of space`;
        } else {
            // Negative savings (for extremely small files due to header overhead)
            metricSaved.innerText = `${savings.toFixed(1)}%`;
            metricSaved.className = "metric-val highlight text-warning";
            compressionProgress.style.width = "0%";
            progressDesc.innerText = "Header metadata overhead exceeds data savings.";
        }

        metricRatio.innerText = `${ratio.toFixed(2)}:1 Ratio`;

        // 3. Render Table
        const sortedFreq = Object.entries(tempCoder.freqTable).sort((a, b) => b[1] - a[1]);
        uniqueCharCount.innerText = `${sortedFreq.length} Unique Bytes`;
        
        codebookTableBody.innerHTML = "";
        sortedFreq.forEach(([byteStr, freq]) => {
            const byteVal = parseInt(byteStr);
            const charDesc = formatChar(byteVal);
            const code = tempCoder.codes[byteVal] || "";
            
            const origBits = freq * 8;
            const newBits = freq * code.length;
            const savingsPercent = ((origBits - newBits) / origBits) * 100;

            const row = document.createElement("tr");
            row.innerHTML = `
                <td><strong>${charDesc}</strong></td>
                <td>${freq}</td>
                <td><code class="binary-code">${code}</code></td>
                <td class="${savingsPercent >= 0 ? 'text-success' : 'text-danger'}">${savingsPercent.toFixed(0)}%</td>
            `;
            codebookTableBody.appendChild(row);
        });

        // Save reference for final download/tree visualization
        huffmanCoder = tempCoder;
        compressedPayload = compressed;

    }

    function resetMetrics() {
        metricOrigSize.innerText = "0 B";
        metricCompSize.innerText = "0 B";
        metricSaved.innerText = "0.0%";
        metricSaved.className = "metric-val highlight";
        compressionProgress.style.width = "0%";
        progressDesc.innerText = "No data compressed yet";
        metricRatio.innerText = "0.00:1 Ratio";
        uniqueCharCount.innerText = "0 Unique Bytes";
        codebookTableBody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-table">Enter text on the left to generate codebook</td>
            </td>
        `;
    }

    // Download compressed file button
    btnCompressAction.addEventListener("click", () => {
        if (rawInputBytes.length === 0) {
            alert("Please input some text or upload a file first!");
            return;
        }

        // Make sure we have the latest compression payload
        const coder = new HuffmanCoding();
        const payload = coder.compress(rawInputBytes);
        
        // Trigger download
        const blob = new Blob([payload], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = originalFileName + ".huff";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // --- DECOMPRESSION PORTAL PIPELINE ---

    setupDragDrop(decompressDropzone, decompressFileInput, (file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedCompressedBytes = new Uint8Array(e.target.result);
            
            // Show details card
            decompressDropzone.style.display = "none";
            decompressFileDetails.style.display = "flex";
            dFileName.innerText = file.name;
            dFileSize.innerText = formatSize(uploadedCompressedBytes.length);

            // Enable extraction
            btnDecompressAction.disabled = false;
        };
        reader.readAsArrayBuffer(file);
    });

    btnClearDecompress.addEventListener("click", () => {
        decompressFileInput.value = "";
        decompressFileDetails.style.display = "none";
        decompressDropzone.style.display = "flex";
        uploadedCompressedBytes = null;
        btnDecompressAction.disabled = true;
        decompressResultBox.style.display = "none";
    });

    btnDecompressAction.addEventListener("click", () => {
        if (!uploadedCompressedBytes) return;

        try {
            const decompressor = new HuffmanCoding();
            decompressedPayload = decompressor.decompress(uploadedCompressedBytes);

            // Show preview (attempt UTF-8 text translation)
            const decoder = new TextDecoder("utf-8", { fatal: false });
            const previewText = decoder.decode(decompressedPayload);

            decompressPreview.innerText = previewText.slice(0, 1500) + (previewText.length > 1500 ? "\n\n... [Truncated preview]" : "");
            decompressResultBox.style.display = "block";
            
            // Scroll to preview
            decompressResultBox.scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            console.error(error);
            alert("Failed to decompress file. Ensure this is a valid .huff compressed binary package.");
        }
    });

    btnDownloadRecovered.addEventListener("click", () => {
        if (!decompressedPayload) return;

        // Strip ".huff" from file name
        let targetName = dFileName.innerText;
        if (targetName.endsWith(".huff")) {
            targetName = targetName.slice(0, -5);
        } else {
            targetName = "recovered_" + targetName;
        }

        const blob = new Blob([decompressedPayload], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = targetName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // --- HELPER FUNCTION UTILITIES ---

    function setupDragDrop(zone, input, fileCallback) {
        zone.addEventListener("click", () => input.click());

        input.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                fileCallback(e.target.files[0]);
            }
        });

        zone.addEventListener("dragover", (e) => {
            e.preventDefault();
            zone.classList.add("dragover");
        });

        zone.addEventListener("dragleave", () => {
            zone.classList.remove("dragover");
        });

        zone.addEventListener("drop", (e) => {
            e.preventDefault();
            zone.classList.remove("dragover");
            if (e.dataTransfer.files.length > 0) {
                fileCallback(e.dataTransfer.files[0]);
            }
        });
    }

    function formatSize(bytes) {
        if (bytes === 0) return "0 B";
        const k = 1024;
        const sizes = ["B", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    }

    function formatChar(byteVal) {
        if (byteVal === 32) return "[Space]";
        if (byteVal === 10) return "[Newline]";
        if (byteVal === 9) return "[Tab]";
        if (byteVal >= 33 && byteVal <= 126) return String.fromCharCode(byteVal);
        return `0x${byteVal.toString(16).toUpperCase().padStart(2, '0')}`;
    }

    // Old SVG Tree drawing engine removed — replaced by the Multi-Tree Visualizer IIFE below.
});

// ─── ALGORITHMS TAB — Interactive Demo Engine ─────────────────────────────
// All 10 DSA algorithms re-implemented in vanilla JS and wired to the UI cards.

// ── Utilities ────────────────────────────────────────────────────────────────
function _fmtChar(byteVal) {
    if (byteVal === 32) return '[Space]';
    if (byteVal === 10) return '[NL]';
    if (byteVal >= 33 && byteVal <= 126) return String.fromCharCode(byteVal);
    return `0x${byteVal.toString(16).toUpperCase().padStart(2,'0')}`;
}

function _setOutput(id, html, pulse = true) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = html;
    el.classList.add('has-result');
    if (pulse) {
        const card = el.closest('.algo-card');
        if (card) {
            card.classList.remove('running');
            void card.offsetWidth;          // force reflow for re-animation
            card.classList.add('running');
        }
    }
}

// ── 1. Frequency Count — O(n) ────────────────────────────────────────────────
function demoFrequency(bytes) {
    const freq = {};
    for (const b of bytes) freq[b] = (freq[b] || 0) + 1;
    const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1]);
    const lines = sorted.slice(0, 8).map(([b, f]) =>
        `<span class="key">${_fmtChar(Number(b)).padEnd(8)}</span>` +
        `→ <span class="val">${f}</span>`);
    if (sorted.length > 8) lines.push(`<span class="label">...and ${sorted.length - 8} more</span>`);
    _setOutput('output-freq',
        `<span class="label">Unique bytes:</span> <span class="val">${sorted.length}</span>\n` +
        lines.join('\n'));
}

// ── 2. Insertion Sort — O(n²) ────────────────────────────────────────────────
function demoInsertionSort(bytes) {
    const freq = {};
    for (const b of bytes) freq[b] = (freq[b] || 0) + 1;
    const arr = Object.entries(freq).map(([b, f]) => [Number(b), f]);

    // Insertion sort by frequency ascending
    for (let i = 1; i < arr.length; i++) {
        const cur = arr[i];
        let j = i - 1;
        while (j >= 0 && arr[j][1] > cur[1]) { arr[j + 1] = arr[j]; j--; }
        arr[j + 1] = cur;
    }
    const preview = arr.slice(0, 6)
        .map(([b, f]) => `<span class="key">${_fmtChar(b)}</span>:${f}`)
        .join('  ');
    _setOutput('output-insertion',
        `<span class="label">Sorted ascending by freq (first 6):</span>\n${preview}\n` +
        `<span class="label">Swaps:</span> O(n²) worst-case`);
}

// ── 3. Merge Sort — O(n log n) ───────────────────────────────────────────────
function _merge(left, right) {
    const out = []; let i = 0, j = 0;
    while (i < left.length && j < right.length)
        out.push(left[i][1] <= right[j][1] ? left[i++] : right[j++]);
    return out.concat(left.slice(i)).concat(right.slice(j));
}
function _mergeSort(arr) {
    if (arr.length <= 1) return arr;
    const m = arr.length >> 1;
    return _merge(_mergeSort(arr.slice(0, m)), _mergeSort(arr.slice(m)));
}
function demoMergeSort(bytes) {
    const freq = {};
    for (const b of bytes) freq[b] = (freq[b] || 0) + 1;
    const arr  = Object.entries(freq).map(([b, f]) => [Number(b), f]);
    const sorted = _mergeSort([...arr]);
    const preview = sorted.slice(0, 6)
        .map(([b, f]) => `<span class="key">${_fmtChar(b)}</span>:${f}`)
        .join('  ');
    const steps = Math.ceil(Math.log2(arr.length || 1));
    _setOutput('output-merge',
        `<span class="label">Sorted ascending (first 6):</span>\n${preview}\n` +
        `<span class="label">Recursion depth:</span> <span class="val">${steps}</span> levels  ` +
        `<span class="label">n·log₂n ≈</span> <span class="val">${(arr.length * steps).toFixed(0)}</span> comparisons`);
}

// ── 4. Binary Search — O(log n) ──────────────────────────────────────────────
function demoBinarySearch(bytes) {
    const freq = {};
    for (const b of bytes) freq[b] = (freq[b] || 0) + 1;
    // Build sorted array of [byteVal, code_placeholder]
    const sorted = Object.keys(freq).map(Number).sort((a, b) => a - b);
    // Search for most frequent character
    const target = Number(Object.entries(freq).sort((a, b) => b[1] - a[1])[0]?.[0] ?? 65);

    let low = 0, high = sorted.length - 1, steps = 0, found = -1;
    while (low <= high) {
        const mid = (low + high) >> 1;
        steps++;
        if (sorted[mid] === target) { found = mid; break; }
        else if (sorted[mid] < target) low = mid + 1;
        else high = mid - 1;
    }
    _setOutput('output-bsearch',
        `<span class="label">Target:</span> <span class="key">${_fmtChar(target)}</span> ` +
        `(most frequent, freq=${freq[target]})\n` +
        `<span class="label">Found at index:</span> <span class="val">${found}</span>  ` +
        `<span class="label">Steps taken:</span> <span class="val">${steps}</span> ` +
        `<span class="label">(log₂${sorted.length} ≈ ${Math.ceil(Math.log2(sorted.length || 1))})</span>`);
}

// ── 5. Min-Heap — O(log n) per op ────────────────────────────────────────────
function demoHeap(bytes) {
    const freq = {};
    for (const b of bytes) freq[b] = (freq[b] || 0) + 1;
    // Show heap array state after inserting all nodes
    const heap = new MinHeap();
    for (const [b, f] of Object.entries(freq))
        heap.insert(new HuffmanNode(Number(b), f));

    const top3 = [];
    const snapshot = [...heap.heap].slice(0, 6)
        .map(n => `<span class="key">${_fmtChar(n.char??-1)}</span>:${n.freq}`);
    // Extract 3 minimums to show ordering
    for (let i = 0; i < 3 && !heap.isEmpty(); i++)
        top3.push(heap.extractMin());

    _setOutput('output-heap',
        `<span class="label">Heap array (first 6 slots):</span>\n[${snapshot.join(', ')}]\n` +
        `<span class="label">Min extractions:</span> ` +
        top3.map(n => `<span class="val">${_fmtChar(n.char)}:${n.freq}</span>`).join(' → '));
}

// ── 6. Greedy Tree Build — O(n log n) ────────────────────────────────────────
function demoGreedy(bytes) {
    const freq = {};
    for (const b of bytes) freq[b] = (freq[b] || 0) + 1;
    const n = Object.keys(freq).length;
    if (n < 2) {
        _setOutput('output-greedy', '<span class="label">Need ≥2 unique bytes to merge.</span>');
        return;
    }
    // Simulate greedy merge steps
    const coder = new HuffmanCoding();
    coder.freqTable = Object.fromEntries(Object.entries(freq).map(([k,v])=>[Number(k),v]));
    coder.root = coder.buildHuffmanTree(coder.freqTable);
    coder.codes = {};
    coder.generateCodes(coder.root);

    const steps = n - 1;
    const codeLens = Object.values(coder.codes).map(c => c.length);
    const avgLen = (codeLens.reduce((s,l)=>s+l,0)/codeLens.length).toFixed(2);
    _setOutput('output-greedy',
        `<span class="label">Unique symbols:</span> <span class="val">${n}</span>  ` +
        `<span class="label">Merge steps:</span> <span class="val">${steps}</span> (= n-1)\n` +
        `<span class="label">Avg code length:</span> <span class="val">${avgLen}</span> bits  ` +
        `<span class="label">vs fixed 8-bit → saves </span>` +
        `<span class="val">${((1 - avgLen/8)*100).toFixed(1)}%</span> avg/symbol`);
}

// ── 7. BFS Traversal — O(n) ──────────────────────────────────────────────────
function demoBFS(bytes) {
    const freq = {};
    for (const b of bytes) freq[b] = (freq[b] || 0) + 1;
    if (Object.keys(freq).length < 2) {
        _setOutput('output-bfs', '<span class="label">Need ≥2 unique bytes.</span>'); return;
    }
    const coder = new HuffmanCoding();
    coder.root = coder.buildHuffmanTree(
        Object.fromEntries(Object.entries(freq).map(([k,v])=>[Number(k),v])));

    // BFS level-order using a queue
    const levels = {};
    const queue = [[coder.root, 0]];
    let totalNodes = 0;
    while (queue.length) {
        const [node, lvl] = queue.shift();
        if (!node) continue;
        totalNodes++;
        if (!levels[lvl]) levels[lvl] = [];
        levels[lvl].push(node.char !== null ? _fmtChar(node.char) : '●');
        if (node.left)  queue.push([node.left,  lvl + 1]);
        if (node.right) queue.push([node.right, lvl + 1]);
    }
    const preview = Object.entries(levels).slice(0, 4)
        .map(([l, ns]) => `<span class="label">L${l}:</span> ${ns.join('  ')}`)
        .join('\n');
    _setOutput('output-bfs',
        `<span class="label">Total nodes visited:</span> <span class="val">${totalNodes}</span> ` +
        `(${Object.keys(freq).length} leaves + ${totalNodes - Object.keys(freq).length} internal)\n` + preview);
}

// ── 8. DFS Traversal — O(n) ──────────────────────────────────────────────────
function demoDFS(bytes) {
    const freq = {};
    for (const b of bytes) freq[b] = (freq[b] || 0) + 1;
    if (Object.keys(freq).length < 2) {
        _setOutput('output-dfs', '<span class="label">Need ≥2 unique bytes.</span>'); return;
    }
    const coder = new HuffmanCoding();
    coder.root = coder.buildHuffmanTree(
        Object.fromEntries(Object.entries(freq).map(([k,v])=>[Number(k),v])));
    coder.codes = {};
    coder.generateCodes(coder.root);

    // Show first 5 leaf paths discovered by DFS
    const leaves = Object.entries(coder.codes)
        .sort((a, b) => a[1].length - b[1].length)
        .slice(0, 5);
    const lines = leaves.map(([b, code]) =>
        `<span class="key">${_fmtChar(Number(b)).padEnd(7)}</span>` +
        `path: <span class="val">${code}</span>  (depth ${code.length})`);
    _setOutput('output-dfs',
        `<span class="label">Pre-order DFS — leaf codes (shallowest first):</span>\n` +
        lines.join('\n'));
}

// ── 9. Shannon Entropy — O(n) ────────────────────────────────────────────────
function demoEntropy(bytes) {
    if (!bytes.length) {
        _setOutput('output-entropy', '<span class="label">No input.</span>'); return;
    }
    const freq = {};
    for (const b of bytes) freq[b] = (freq[b] || 0) + 1;
    const n = bytes.length;
    let H = 0;
    for (const count of Object.values(freq)) {
        const p = count / n;
        if (p > 0) H -= p * Math.log2(p);
    }
    const theoreticalMin = H * n;
    const currentBits   = n * 8;
    const maxSavings    = ((currentBits - theoreticalMin) / currentBits * 100);
    _setOutput('output-entropy',
        `<span class="label">H(X) =</span> <span class="val">${H.toFixed(4)}</span> bits/symbol\n` +
        `<span class="label">Theoretical min bits:</span> <span class="val">${theoreticalMin.toFixed(1)}</span>  ` +
        `<span class="label">Current bits:</span> <span class="val">${currentBits}</span>\n` +
        `<span class="label">Max possible savings:</span> <span class="val">${maxSavings.toFixed(1)}%</span>`);
}

// ── 10. Bit Packing — O(n) ───────────────────────────────────────────────────
function demoBitPack(bytes) {
    if (!bytes.length) {
        _setOutput('output-bitpack', '<span class="label">No input.</span>'); return;
    }
    const coder = new HuffmanCoding();
    const compressed = coder.compress(bytes);
    // Build a sample bit string from first 3 bytes
    const sample = bytes.slice(0, 3);
    coder.freqTable = Object.fromEntries(
        Object.entries(coder.freqTable).map(([k,v])=>[Number(k),v]));
    let sampleBits = '';
    for (const b of sample) {
        const code = coder.codes[b];
        if (code) sampleBits += code;
    }
    const padding = (8 - (sampleBits.length % 8)) % 8;
    const packed  = sampleBits.padEnd(sampleBits.length + padding, '0');
    _setOutput('output-bitpack',
        `<span class="label">Sample (first 3 chars) bit string:</span>\n<span class="val">${sampleBits}</span>\n` +
        `<span class="label">Padded to 8-boundary:</span> <span class="val">${packed}</span> (+${padding} pad bits)\n` +
        `<span class="label">Full file:</span> <span class="val">${bytes.length * 8}</span> bits → packed into ` +
        `<span class="val">${compressed.length}</span> bytes`);
}

// ── Master Run Controller ─────────────────────────────────────────────────────
function runAllAlgorithms() {
    const text  = document.getElementById('algo-input')?.value || 'ABRACADABRA';
    const bytes = new TextEncoder().encode(text);

    demoFrequency(bytes);
    demoInsertionSort(bytes);
    demoMergeSort(bytes);
    demoBinarySearch(bytes);
    demoHeap(bytes);
    demoGreedy(bytes);
    demoBFS(bytes);
    demoDFS(bytes);
    demoEntropy(bytes);
    demoBitPack(bytes);
}

// Auto-run on input change and on button click
const algoInput  = document.getElementById('algo-input');
const btnRunAlgo = document.getElementById('btn-run-algos');
if (algoInput)  algoInput.addEventListener('input', runAllAlgorithms);
if (btnRunAlgo) btnRunAlgo.addEventListener('click', runAllAlgorithms);

// Run once on page load with the default value
runAllAlgorithms();


// ═══════════════════════════════════════════════════════════════════
//  MULTI-TREE VISUALIZER ENGINE
//  Supports: BST · AVL · Min-Heap · Red-Black Tree · Trie
// ═══════════════════════════════════════════════════════════════════

(function () {

    // ── DOM refs ────────────────────────────────────────────────────
    const treeInput     = document.getElementById('tree-text-input');
    const charCount     = document.getElementById('tree-char-count');
    const typeBtns      = document.querySelectorAll('.tree-type-btn');
    const svg           = document.getElementById('tree-svg');
    const emptyMsg      = document.getElementById('tree-empty-message');
    const tibTitle      = document.getElementById('tib-title');
    const tibDesc       = document.getElementById('tib-desc');
    const cmpRows       = { bst:'cmp-bst', avl:'cmp-avl', minheap:'cmp-minheap', rbt:'cmp-rbt', trie:'cmp-trie' };

    let currentType = 'bst';

    const INFO = {
        bst:     { title:'Binary Search Tree (BST)',      desc:'Characters inserted by ASCII value. Left < Parent < Right. May become unbalanced.' },
        avl:     { title:'AVL Tree (Height-Balanced BST)', desc:'Self-balancing BST. After each insert, rotations (LL, RR, LR, RL) keep |height(L)−height(R)| ≤ 1.' },
        minheap: { title:'Min-Heap (Array-based)',         desc:'Complete binary tree. Each parent ≤ children. Array indices: parent=(i-1)//2, left=2i+1, right=2i+2.' },
        rbt:     { title:'Red-Black Tree',                 desc:'BST with colour rules: root=Black, red nodes have black children, all paths have equal black-height.' },
        trie:    { title:'Trie (Prefix Tree)',              desc:'Each character of the input string is a node. Shared prefixes merge into the same path from root.' },
    };

    // ── Wire up tabs ────────────────────────────────────────────────
    typeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            typeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentType = btn.dataset.tree;
            updateInfoBar();
            highlightCmpRow();
            renderTree();
        });
    });

    if (treeInput) {
        treeInput.addEventListener('input', () => {
            charCount.textContent = treeInput.value.length + ' chars';
            renderTree();
        });
        // Set initial char count but skip render — tab is hidden, SVG has 0 width
        charCount.textContent = treeInput.value.length + ' chars';
    }

    function updateInfoBar() {
        const info = INFO[currentType];
        if (tibTitle) tibTitle.textContent = info.title;
        if (tibDesc)  tibDesc.textContent  = info.desc;
    }
    function highlightCmpRow() {
        Object.values(cmpRows).forEach(id => {
            const r = document.getElementById(id);
            if (r) r.classList.remove('active-tree-row');
        });
        const active = document.getElementById(cmpRows[currentType]);
        if (active) active.classList.add('active-tree-row');
    }
    updateInfoBar();
    highlightCmpRow();

    // ── Master render dispatcher ────────────────────────────────────
    function renderTree() {
        if (!svg) return;
        svg.innerHTML = '';
        const text = treeInput ? treeInput.value : '';
        if (!text) { showEmpty(); return; }

        hideEmpty();
        const chars = [...new Set(text.toUpperCase().split('').filter(c => c.trim()))];

        switch (currentType) {
            case 'bst':     drawBST(chars);     break;
            case 'avl':     drawAVL(chars);     break;
            case 'minheap': drawMinHeapTree(text); break;
            case 'rbt':     drawRBT(chars);     break;
            case 'trie':    drawTrie(text);     break;
        }
    }

    function showEmpty() { if (emptyMsg) emptyMsg.style.display = 'flex'; }
    function hideEmpty() { if (emptyMsg) emptyMsg.style.display = 'none'; }

    // ── SVG LAYOUT ENGINE ───────────────────────────────────────────
    // Shared by BST / AVL / MinHeap / RBT
    // Node shape: { val, left, right, color? }

    const NODE_R   = 20;
    const V_GAP    = 72;
    const SVG_PAD  = 40;

    function layoutTree(root) {
        // Assign x by in-order index, y by depth
        let counter = 0;
        function inorder(n, depth) {
            if (!n) return;
            inorder(n.left, depth + 1);
            n._x = counter++;
            n._y = depth;
            inorder(n.right, depth + 1);
        }
        inorder(root, 0);
        return counter; // total nodes
    }

    function paintTree(root, totalNodes) {
        const W = svg.clientWidth || 900;
        const cellW = Math.max((W - SVG_PAD * 2) / Math.max(totalNodes, 1), 38);
        const svgH  = (getDepth(root) + 1) * V_GAP + SVG_PAD * 2;

        svg.setAttribute('viewBox', `0 0 ${W} ${svgH}`);
        svg.setAttribute('height', svgH);

        function paintEdgesFirst(n) {
            if (!n) return;
            if (n.left)  drawEdge(cx(n, cellW), cy(n), cx(n.left,  cellW), cy(n.left));
            if (n.right) drawEdge(cx(n, cellW), cy(n), cx(n.right, cellW), cy(n.right));
            paintEdgesFirst(n.left);
            paintEdgesFirst(n.right);
        }
        function paintNodes(n) {
            if (!n) return;
            paintNodes(n.left);
            paintNodes(n.right);
            drawGenericNode(n, cx(n, cellW), cy(n));
        }

        paintEdgesFirst(root);
        paintNodes(root);
    }

    function cx(n, cellW) { return SVG_PAD + n._x * cellW + cellW / 2; }
    function cy(n)        { return SVG_PAD + n._y * V_GAP + NODE_R; }

    function getDepth(n) {
        if (!n) return 0;
        return 1 + Math.max(getDepth(n.left), getDepth(n.right));
    }

    function drawEdge(x1, y1, x2, y2) {
        const line = _svgEl('line');
        line.setAttribute('x1', x1); line.setAttribute('y1', y1);
        line.setAttribute('x2', x2); line.setAttribute('y2', y2);
        line.setAttribute('stroke', 'rgba(255,255,255,0.12)');
        line.setAttribute('stroke-width', '2');
        svg.appendChild(line);
    }

    function drawGenericNode(n, x, y) {
        const isLeaf  = !n.left && !n.right;
        // Glow
        if (isLeaf) {
            const glow = _svgEl('circle');
            glow.setAttribute('cx', x); glow.setAttribute('cy', y);
            glow.setAttribute('r', NODE_R + 5);
            glow.setAttribute('fill', 'rgba(6,182,212,0.15)');
            glow.setAttribute('filter', 'blur(5px)');
            svg.appendChild(glow);
        }
        // Determine fill & stroke based on tree type / node colour
        let fill = 'var(--bg-dark)', stroke = 'var(--secondary)';
        if (n.color === 'red')   { fill = '#7f1d1d'; stroke = '#ef4444'; }
        if (n.color === 'black') { fill = '#1e293b'; stroke = '#64748b'; }
        if (isLeaf && !n.color) { fill = 'var(--primary)'; stroke = 'var(--primary)'; }

        const circle = _svgEl('circle');
        circle.setAttribute('cx', x); circle.setAttribute('cy', y);
        circle.setAttribute('r',  NODE_R);
        circle.setAttribute('fill', fill);
        circle.setAttribute('stroke', stroke);
        circle.setAttribute('stroke-width', '2');
        circle.style.cursor = 'pointer';
        svg.appendChild(circle);

        // Label
        const label = _svgEl('text');
        label.setAttribute('x', x); label.setAttribute('y', y + 5);
        label.setAttribute('text-anchor', 'middle');
        label.setAttribute('fill', '#f8fafc');
        label.setAttribute('font-size', '13');
        label.setAttribute('font-family', 'Outfit, sans-serif');
        label.setAttribute('font-weight', '600');
        label.setAttribute('pointer-events', 'none');
        label.textContent = n.val;
        svg.appendChild(label);

        // Height badge for AVL
        if (n.height !== undefined) {
            const hBadge = _svgEl('text');
            hBadge.setAttribute('x', x + NODE_R + 2);
            hBadge.setAttribute('y', y - NODE_R + 4);
            hBadge.setAttribute('text-anchor', 'start');
            hBadge.setAttribute('fill', 'var(--warning)');
            hBadge.setAttribute('font-size', '9');
            hBadge.setAttribute('font-family', 'Space Grotesk, monospace');
            hBadge.setAttribute('pointer-events', 'none');
            hBadge.textContent = 'h' + n.height;
            svg.appendChild(hBadge);
        }
    }

    function _svgEl(tag) {
        return document.createElementNS('http://www.w3.org/2000/svg', tag);
    }

    // ════════════════════════════════════════════════════════════════
    //  1. BINARY SEARCH TREE
    // ════════════════════════════════════════════════════════════════
    function bstInsert(root, val) {
        if (!root) return { val, left: null, right: null };
        if (val < root.val) root.left  = bstInsert(root.left,  val);
        else if (val > root.val) root.right = bstInsert(root.right, val);
        return root;
    }

    function drawBST(chars) {
        let root = null;
        chars.sort().forEach(c => { root = bstInsert(root, c); });
        const total = layoutTree(root);
        paintTree(root, total);
    }

    // ════════════════════════════════════════════════════════════════
    //  2. AVL TREE
    // ════════════════════════════════════════════════════════════════
    function avlHeight(n) { return n ? n.height : 0; }
    function avlBF(n)     { return n ? avlHeight(n.left) - avlHeight(n.right) : 0; }
    function avlUpdate(n) { n.height = 1 + Math.max(avlHeight(n.left), avlHeight(n.right)); }

    function rotateRight(y) {
        const x = y.left, T2 = x.right;
        x.right = y; y.left = T2;
        avlUpdate(y); avlUpdate(x);
        return x;
    }
    function rotateLeft(x) {
        const y = x.right, T2 = y.left;
        y.left = x; x.right = T2;
        avlUpdate(x); avlUpdate(y);
        return y;
    }
    function avlInsert(root, val) {
        if (!root) return { val, left: null, right: null, height: 1 };
        if (val < root.val) root.left  = avlInsert(root.left,  val);
        else if (val > root.val) root.right = avlInsert(root.right, val);
        else return root;

        avlUpdate(root);
        const bf = avlBF(root);

        if (bf > 1 && val < root.left.val)  return rotateRight(root);
        if (bf < -1 && val > root.right.val) return rotateLeft(root);
        if (bf > 1 && val > root.left.val)  { root.left  = rotateLeft(root.left);  return rotateRight(root); }
        if (bf < -1 && val < root.right.val){ root.right = rotateRight(root.right); return rotateLeft(root);  }
        return root;
    }

    function drawAVL(chars) {
        let root = null;
        chars.sort().forEach(c => { root = avlInsert(root, c); });
        const total = layoutTree(root);
        paintTree(root, total);
    }

    // ════════════════════════════════════════════════════════════════
    //  3. MIN-HEAP (array-based → rendered as binary tree)
    // ════════════════════════════════════════════════════════════════
    function drawMinHeapTree(text) {
        // Build frequency heap from all characters
        const freq = {};
        for (const c of text.toUpperCase()) {
            if (c.trim()) freq[c] = (freq[c] || 0) + 1;
        }
        // Insert into array min-heap
        const heap = [];
        function heapInsert(val) {
            heap.push(val);
            let i = heap.length - 1;
            while (i > 0) {
                const p = Math.floor((i - 1) / 2);
                if (heap[p] > heap[i]) { [heap[p], heap[i]] = [heap[i], heap[p]]; i = p; }
                else break;
            }
        }
        // Insert char + freq pairs, keyed by frequency then char
        const pairs = Object.entries(freq).sort((a,b)=>a[1]-b[1]||a[0].localeCompare(b[0]));
        pairs.forEach(([c, f]) => heapInsert(c + ':' + f));

        // Convert array to linked tree for layout
        function buildFromArray(arr, i) {
            if (i >= arr.length) return null;
            return {
                val: arr[i],
                left:  buildFromArray(arr, 2*i+1),
                right: buildFromArray(arr, 2*i+2),
            };
        }
        const root = buildFromArray(heap, 0);
        const total = layoutTree(root);
        paintTree(root, total);
    }

    // ════════════════════════════════════════════════════════════════
    //  4. RED-BLACK TREE
    // ════════════════════════════════════════════════════════════════
    const R = 'red', B = 'black';

    function rbtNode(val) { return { val, color: R, left: null, right: null }; }
    function isRed(n)     { return n && n.color === R; }

    function rbtRotateLeft(h)  { const x=h.right; h.right=x.left; x.left=h; x.color=h.color; h.color=R; return x; }
    function rbtRotateRight(h) { const x=h.left;  h.left=x.right; x.right=h; x.color=h.color; h.color=R; return x; }
    function rbtFlip(h)        { h.color=R; h.left.color=B; h.right.color=B; }

    function rbtInsert(h, val) {
        if (!h) return rbtNode(val);
        if      (val < h.val) h.left  = rbtInsert(h.left,  val);
        else if (val > h.val) h.right = rbtInsert(h.right, val);

        if (isRed(h.right) && !isRed(h.left))      h = rbtRotateLeft(h);
        if (isRed(h.left)  && isRed(h.left.left))  h = rbtRotateRight(h);
        if (isRed(h.left)  && isRed(h.right))       rbtFlip(h);

        return h;
    }

    function drawRBT(chars) {
        let root = null;
        chars.sort().forEach(c => { root = rbtInsert(root, c); });
        if (root) root.color = B; // root always black
        const total = layoutTree(root);
        paintTree(root, total);
    }

    // ════════════════════════════════════════════════════════════════
    //  5. TRIE (Prefix Tree)
    // ════════════════════════════════════════════════════════════════
    function buildTrie(text) {
        // Keep only first 30 chars to avoid huge trees
        const words = text.toUpperCase().replace(/[^A-Z ]/g,'').split(' ').filter(Boolean).slice(0,6);
        const trieRoot = { val: '★', children: {}, isEnd: false };

        function insert(word) {
            let node = trieRoot;
            for (const ch of word.slice(0, 8)) {
                if (!node.children[ch]) node.children[ch] = { val: ch, children: {}, isEnd: false };
                node = node.children[ch];
            }
            node.isEnd = true;
        }
        words.forEach(w => insert(w));
        return trieRoot;
    }

    function trieToLinked(tNode) {
        const children = Object.values(tNode.children).sort((a,b)=>a.val.localeCompare(b.val));
        return {
            val: tNode.isEnd ? tNode.val + '●' : tNode.val,
            left:  children[0] ? trieToLinked(children[0]) : null,
            right: children[1] ? buildTrieChain(children.slice(1)) : null,
        };
    }
    function buildTrieChain(siblings) {
        if (!siblings.length) return null;
        const node = trieToLinked(siblings[0]);
        node.right = buildTrieChain(siblings.slice(1));
        return node;
    }

    function drawTrie(text) {
        const trieRoot = buildTrie(text);
        const linkedRoot = trieToLinked(trieRoot);
        const total = layoutTree(linkedRoot);
        paintTree(linkedRoot, total);
    }

    // Render tree when visualizer tab opens (tab must be visible for SVG sizing)
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.dataset.tab === 'visualizer') {
                // Staggered renders to guarantee the tab is fully visible
                setTimeout(renderTree, 100);
                setTimeout(renderTree, 400);
            }
        });
    });

})(); // end IIFE
