# 🚀 CompressIQ - Dynamic File Compression Utility

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)]
[![DSA](https://img.shields.io/badge/Data%20Structures-MinHeap-green.svg)]
[![Algorithm](https://img.shields.io/badge/Algorithm-HuffmanCoding-orange.svg)]
[![Compression](https://img.shields.io/badge/Compression-Lossless-red.svg)]

A production-grade file compression and decompression utility built using **Huffman Coding**, **Custom Min Heap**, **Binary Trees**, **Bit-Level Serialization**, and **Greedy Algorithms**.

Designed as a Data Structures & Algorithms portfolio project demonstrating real-world applications of trees, heaps, greedy optimization, file systems, binary data processing, and lossless compression techniques.

---

# 📌 Project Overview

**CompressIQ** is an industrial-grade, byte-level file compression and decompression utility built from scratch using Huffman Coding.

The system compresses files by assigning shorter binary codes to frequently occurring bytes and longer codes to less frequent bytes, significantly reducing storage requirements while preserving complete data integrity.

Unlike lossy compression techniques, CompressIQ guarantees that every byte of the original file can be perfectly reconstructed after decompression.

---

# ❓ Problem Statement

Modern applications generate large volumes of data that consume significant storage and bandwidth.

Traditional file storage uses fixed-length encoding where every character occupies the same amount of memory regardless of its frequency.

This results in:

* Increased storage requirements
* Higher bandwidth consumption
* Slower file transfers
* Reduced system efficiency

CompressIQ solves these challenges through Huffman Coding, which dynamically generates optimal binary representations based on symbol frequency.

---

# 🚀 Why File Compression Matters

## Storage Optimization

Reduce disk space usage for files, logs, backups, and archives.

## Faster Data Transfer

Smaller files require less network bandwidth.

## Better Performance

Applications can process and transmit compressed data more efficiently.

## Real-World Applications

* ZIP Utilities
* Cloud Storage Systems
* Database Compression
* Backup Solutions
* Operating Systems
* File Archiving Software
* Data Transmission Protocols

---

# ✨ Key Features

✅ Lossless File Compression

✅ File Decompression

✅ Supports Text Files

✅ Supports Binary Files

✅ Supports PDFs

✅ Supports Images

✅ Huffman Coding Implementation from Scratch

✅ Custom Min Heap (Priority Queue)

✅ Binary Tree Construction

✅ Bit-Level Data Packing

✅ Serialization & Deserialization

✅ Compression Statistics Dashboard

✅ Compression Ratio Calculation

✅ File Integrity Verification

✅ Command Line Interface

✅ GitHub Portfolio Ready

✅ Interview Ready Project

---

# 🏗️ System Architecture

## Compression Pipeline

```text
Input File
      │
      ▼
Frequency Analysis
      │
      ▼
Custom Min Heap
      │
      ▼
Huffman Tree Builder
      │
      ▼
Code Generator
      │
      ▼
Bit Stream Encoder
      │
      ▼
Binary Serializer
      │
      ▼
Compressed Output (.huff)
```

## Decompression Pipeline

```text
Compressed File
      │
      ▼
Header Parser
      │
      ▼
Tree Reconstruction
      │
      ▼
Bit Stream Decoder
      │
      ▼
Original File Recovery
```

---

# 🔄 Workflow

```text
Input File
      │
      ▼
Frequency Calculation
      │
      ▼
Min Heap Construction
      │
      ▼
Huffman Tree Creation
      │
      ▼
Binary Code Generation
      │
      ▼
File Compression
      │
      ▼
Compressed Output
      │
      ▼
File Decompression
      │
      ▼
Original File Recovery
```

---

# 🧠 DSA Concepts Implemented

## Data Structures

### Custom Min Heap

Used as a Priority Queue to efficiently retrieve the two lowest-frequency nodes during Huffman Tree construction.

### Binary Tree

Huffman Tree is represented as a binary tree where leaf nodes store symbols and internal nodes store combined frequencies.

### Hash Maps (Dictionary)

Used for:

* Frequency Mapping
* Codebook Generation
* Fast Encoding Lookup
* Fast Decoding Lookup

---

## Algorithms

### Huffman Coding

A lossless compression algorithm that generates variable-length binary codes.

### Greedy Algorithm

Repeatedly selects the two lowest-frequency nodes to build an optimal Huffman Tree.

### Tree Traversal

Used for:

* Huffman Code Generation
* Decoding Compressed Data

---

# 📂 Repository Structure

```text
CompressIQ/
│
├── input_files/
│   └── sample.txt
│
├── compressed_files/
│   └── sample.huff
│
├── decompressed_files/
│   └── recovered_sample.txt
│
├── outputs/
│   └── simulation_summary.txt
│
├── src/
│   ├── __init__.py
│   ├── node.py
│   ├── heap.py
│   └── huffman.py
│
├── images/
│   └── screenshots
│
├── docs/
│   └── project_report.pdf
│
├── README.md
├── requirements.txt
├── .gitignore
└── main.py
```

---

# ⚙️ Installation Guide

## Prerequisites

* Python 3.8+
* Git

---

## Clone Repository

```bash
git clone https://github.com/yourusername/CompressIQ.git

cd CompressIQ
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Verify Python Installation

```bash
python --version
```

Expected Output:

```text
Python 3.8+
```

---

# ▶️ Running the Project

## Run Demo Simulation

```bash
python main.py --demo
```

---

## Compress File

```bash
python main.py -c input_files/document.txt -s
```

Output:

```text
compressed_files/document.txt.huff
```

---

## Decompress File

```bash
python main.py -d compressed_files/document.txt.huff
```

Output:

```text
decompressed_files/recovered_document.txt
```

---

# 📊 Sample Output

```text
=========================================
--- STARTING END-TO-END SIMULATION ---
=========================================

Reading input file...

Compression completed successfully.

Original Size:      4110 bytes
Compressed Size:    2568 bytes

Compression Ratio:  1.60 : 1

Space Savings:      37.52%

Decompression completed successfully.

Integrity Check Passed.

Recovered file is identical to original file.
```

---

# ⚡ Complexity Analysis

| Operation             | Time Complexity |
| --------------------- | --------------- |
| Frequency Counting    | O(n)            |
| Heap Construction     | O(k log k)      |
| Huffman Tree Creation | O(k log k)      |
| Code Generation       | O(k)            |
| Compression           | O(n)            |
| Decompression         | O(n)            |

Where:

* n = Total file size
* k = Unique symbols

---

# 📈 Learning Outcomes

Through this project, developers gain hands-on experience with:

* Huffman Coding
* Greedy Algorithms
* Binary Trees
* Min Heap Implementation
* Priority Queues
* Hash Maps
* Binary Data Processing
* Serialization
* Deserialization
* File Handling
* Memory Optimization
* Compression Algorithms
* System Programming
* Software Engineering Practices

---

# 🎯 Skills Demonstrated

## Data Structures

* Binary Trees
* Min Heaps
* Priority Queues
* Hash Maps

## Algorithms

* Huffman Coding
* Greedy Algorithms
* Tree Traversal

## Software Engineering

* Modular Architecture
* CLI Development
* File Processing
* Error Handling

## System Programming

* Bit Manipulation
* Binary Serialization
* Compression Techniques
* Memory Optimization

## Developer Tools

* Python
* Git
* GitHub

---

# 🧪 Project Simulation

## Step 1

Create sample file:

```text
DATA STRUCTURES AND ALGORITHMS
```

## Step 2

Calculate frequency table.

## Step 3

Generate Huffman codes.

Example:

```text
A = 10
T = 111
D = 00
```

## Step 4

Compress file.

## Step 5

Calculate compression ratio.

## Step 6

Decompress file.

## Step 7

Verify:

```text
Original File == Recovered File
```

Result:

```text
TRUE
```

---

# 📸 Screenshots to Include

### Project Structure

```text
images/project_structure.png
```

### Input File

```text
images/input_file.png
```

### Frequency Table

```text
images/frequency_table.png
```

### Huffman Codebook

```text
images/huffman_codes.png
```

### Compression Output

```text
images/compression_output.png
```

### Compression Statistics

```text
images/compression_ratio.png
```

### Decompression Verification

```text
images/decompression_verification.png
```

### GitHub Repository Preview

```text
images/github_preview.png
```

---

# 🚀 Future Enhancements

* GUI Version using Tkinter
* Drag & Drop Compression
* Folder Compression
* Parallel Compression
* LZW Compression Support
* Arithmetic Coding Support
* File Encryption Layer
* Cloud Storage Integration
* Web Dashboard
* Performance Benchmarking Suite

---

# 💼 Why This Project Matters

CompressIQ is not just a DSA assignment.

It demonstrates practical implementation of:

* Compression Algorithms
* Memory Optimization
* File Systems
* Binary Data Processing
* Greedy Algorithm Design
* Priority Queue Operations
* Tree-Based Encoding Systems

The project combines algorithm design, data structures, system programming, and software engineering into a complete end-to-end application suitable for:

* Software Developer Roles
* Backend Developer Roles
* System Programming Roles
* DSA Interviews
* Coding Assessments
* Academic Projects
* Open Source Portfolios

---

# 🏆 Resume Highlights

### Implemented

* Huffman Coding from Scratch
* Custom Min Heap
* Binary Tree Encoding
* Lossless Compression Engine
* Bit-Level Serialization

### Achieved

* Reduced file storage requirements
* Preserved 100% data integrity
* Built complete compression/decompression workflow
* Demonstrated advanced DSA concepts

---

# 👨‍💻 Author

**Sarthak Dhumal**

Computer Engineering Student

Interested In:

* Data Structures & Algorithms
* Software Development
* Backend Engineering
* System Design
* Problem Solving
* Open Source Development

---



---

## ⭐ If you found this project useful, consider giving it a star and sharing it with others.
#   C o m p r e s s I Q - - - D y n a m i c - F i l e - C o m p r e s s i o n - U t i l i t y  
 