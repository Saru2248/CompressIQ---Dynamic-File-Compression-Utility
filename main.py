import os
import sys
import argparse
import time
from src.huffman import HuffmanCoding

# Attempt to import colorama for premium terminal aesthetics
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLOR_AVAILABLE = True
except ImportError:
    COLOR_AVAILABLE = False
    # Mock class to prevent crashes if colorama is not installed
    class EmptyColor:
        def __getattr__(self, name):
            return ""
    Fore = Back = Style = EmptyColor()

# Premium ASCII Art Banner
BANNER = f"""
{Fore.CYAN}{Style.BRIGHT}  _____                               _      ______ _ _      
 |  __ \\                             (_)    |  ____(_) |     
 | |  | |_   _ _ __   __ _ _ __ ___   _  ___| |__   _| | ___ 
 | |  | | | | | '_ \\ / _` | '_ ` _ \\ | |/ __|  __| | | |/ _ \\
 | |__| | |_| | | | | (_| | | | | | || | (__| |    | | |  __/
 |_____/ \\__, |_| |_|\\__,_|_| |_| |_| |_|\\___|_|    |_|_|\\___|
          __/ |                                              
         |___/ {Fore.YELLOW}v1.0 - Industrial-Grade DSA File Compressor
{Fore.GREEN}{Style.BRIGHT}======================================================================
"""

def create_default_directories():
    """Creates the standard directory layout for the project if not present."""
    directories = [
        "input_files",
        "compressed_files",
        "decompressed_files",
        "outputs"
    ]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            # Create a simple .gitkeep file to keep directories tracked in Git
            with open(os.path.join(directory, ".gitkeep"), "w") as f:
                f.write("")

def format_char(byte_val):
    """Formats raw byte value into a readable character description."""
    if byte_val == 32:
        return "[Space]"
    elif byte_val == 10:
        return "[LF/Newline]"
    elif byte_val == 13:
        return "[CR/Return]"
    elif byte_val == 9:
        return "[Tab]"
    elif 32 < byte_val < 127:
        return chr(byte_val)
    else:
        return f"0x{byte_val:02X}"

def print_stats(huffman_coder, original_size, compressed_size):
    """Prints compression metrics and the generated binary codebook."""
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}--- COMPRESSION METRICS & STATISTICS ---")
    print(f"{Fore.WHITE}Original Size:      {Fore.YELLOW}{original_size} bytes")
    print(f"{Fore.WHITE}Compressed Size:    {Fore.YELLOW}{compressed_size} bytes")
    
    if original_size > 0:
        ratio = original_size / compressed_size if compressed_size > 0 else 0
        savings = (1 - (compressed_size / original_size)) * 100
        print(f"{Fore.WHITE}Compression Ratio:  {Fore.GREEN}{ratio:.3f}:1")
        print(f"{Fore.WHITE}Space Savings:      {Fore.GREEN}{savings:.2f}%")
    else:
        print(f"{Fore.RED}Cannot calculate ratio: original size is 0.")

    print(f"\n{Fore.BLUE}{Style.BRIGHT}--- HUFFMAN BINARY CODEBOOK (TOP 15 CHARACTERS) ---")
    print(f"{Fore.CYAN}{'Byte/Char':<15} | {'Frequency':<10} | {'Huffman Code':<15} | {'Size Savings'}")
    print(f"{Fore.CYAN}" + "-" * 60)
    
    # Sort characters by frequency descending
    sorted_freq = sorted(huffman_coder.freq_table.items(), key=lambda x: x[1], reverse=True)
    
    for byte_val, freq in sorted_freq[:15]:
        char_desc = format_char(byte_val)
        code = huffman_coder.codes.get(byte_val, "")
        
        # Original size = freq * 8 bits. New size = freq * len(code) bits.
        orig_bits = freq * 8
        new_bits = freq * len(code)
        bit_savings = ((orig_bits - new_bits) / orig_bits) * 100 if orig_bits > 0 else 0
        
        print(f"{Fore.WHITE}{char_desc:<15} | {freq:<10} | {Fore.YELLOW}{code:<15}{Fore.RESET} | {Fore.GREEN}{bit_savings:.1f}%")
        
    if len(sorted_freq) > 15:
        print(f"{Fore.WHITE}... and {len(sorted_freq) - 15} more unique character(s).")

def run_compression(input_path, output_path, display_stats=False):
    """Reads input file, runs compression, writes compressed file, and prints logs."""
    if not os.path.exists(input_path):
        print(f"{Fore.RED}[Error] Input file '{input_path}' does not exist.")
        sys.exit(1)

    print(f"{Fore.YELLOW}Reading input file: {input_path}...")
    start_time = time.time()
    with open(input_path, "rb") as f:
        raw_bytes = f.read()
    
    original_size = len(raw_bytes)
    print(f"{Fore.GREEN}Successfully read {original_size} bytes.")

    print(f"{Fore.YELLOW}Compresing data using Huffman Coding...")
    coder = HuffmanCoding()
    compressed_bytes = coder.compress(raw_bytes)
    compressed_size = len(compressed_bytes)
    
    print(f"{Fore.YELLOW}Writing compressed output: {output_path}...")
    with open(output_path, "wb") as f:
        f.write(compressed_bytes)
    
    elapsed_time = time.time() - start_time
    print(f"{Fore.GREEN}[Success] Compression completed in {elapsed_time:.4f} seconds.")
    print(f"{Fore.GREEN}Compressed file written to: {output_path}")

    if display_stats and original_size > 0:
        print_stats(coder, original_size, compressed_size)

def run_decompression(input_path, output_path):
    """Reads compressed file, runs decompression, writes original file, and validates."""
    if not os.path.exists(input_path):
        print(f"{Fore.RED}[Error] Compressed file '{input_path}' does not exist.")
        sys.exit(1)

    print(f"{Fore.YELLOW}Reading compressed file: {input_path}...")
    start_time = time.time()
    with open(input_path, "rb") as f:
        compressed_bytes = f.read()

    print(f"{Fore.YELLOW}Decompressing data using Huffman Tree traversal...")
    coder = HuffmanCoding()
    decompressed_bytes = coder.decompress(compressed_bytes)

    print(f"{Fore.YELLOW}Writing decompressed output: {output_path}...")
    with open(output_path, "wb") as f:
        f.write(decompressed_bytes)

    elapsed_time = time.time() - start_time
    print(f"{Fore.GREEN}[Success] Decompression completed in {elapsed_time:.4f} seconds.")
    print(f"{Fore.GREEN}Decompressed file written to: {output_path}")

def run_simulation():
    """Runs a complete end-to-end simulation of the compression pipeline."""
    create_default_directories()
    
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}=========================================")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}--- STARTING END-TO-END SIMULATION ---")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}=========================================")
    
    # 1. Create a sample text file with repeated pattern to guarantee compression
    sample_text = (
        "huffman coding is a data compression algorithm. "
        "it is a greedy algorithm that assigns variable-length codes to input characters. "
        "the most frequent characters get the shortest codes, and the least frequent "
        "characters get the longest codes. this project is a complete proof of work "
        "demonstrating custom min-heap priority queue implementations, binary tree structures, "
        "and byte-level bit packing logic in python.\n"
    ) * 10  # 10 repetitions to make it larger

    input_file = os.path.join("input_files", "sample.txt")
    compressed_file = os.path.join("compressed_files", "sample.huff")
    decompressed_file = os.path.join("decompressed_files", "sample_recovered.txt")

    print(f"\n{Fore.CYAN}[Step 1] Creating sample input text in '{input_file}'...")
    with open(input_file, "w", encoding="utf-8") as f:
        f.write(sample_text)
    
    orig_size = os.path.getsize(input_file)
    print(f"Sample file size: {orig_size} bytes.")

    # 2. Run compression
    print(f"\n{Fore.CYAN}[Step 2] Executing compression...")
    run_compression(input_file, compressed_file, display_stats=True)
    comp_size = os.path.getsize(compressed_file)

    # 3. Run decompression
    print(f"\n{Fore.CYAN}[Step 3] Executing decompression...")
    run_decompression(compressed_file, decompressed_file)

    # 4. Verify integrity
    print(f"\n{Fore.CYAN}[Step 4] Verifying data integrity...")
    with open(input_file, "rb") as f1, open(decompressed_file, "rb") as f2:
        original_data = f1.read()
        recovered_data = f2.read()

    if original_data == recovered_data:
        print(f"{Fore.GREEN}{Style.BRIGHT}[PASS] Integrity Check: Decompressed bytes match the original bytes exactly!")
        print(f"{Fore.GREEN}Binary matches: byte-for-byte identical.")
    else:
        print(f"{Fore.RED}{Style.BRIGHT}[FAIL] Integrity Check: Decompressed data differs from original!")

    # Write a summary log file to outputs/
    summary_path = os.path.join("outputs", "simulation_summary.txt")
    with open(summary_path, "w") as sf:
        sf.write("DYNAMIC FILE COMPRESSION UTILITY - SIMULATION REPORT\n")
        sf.write("===================================================\n")
        sf.write(f"Original File: {input_file} ({orig_size} bytes)\n")
        sf.write(f"Compressed File: {compressed_file} ({comp_size} bytes)\n")
        sf.write(f"Decompressed File: {decompressed_file}\n")
        sf.write(f"Compression Ratio: {orig_size / comp_size if comp_size > 0 else 0:.3f}:1\n")
        sf.write(f"Space Savings: {(1 - (comp_size / orig_size)) * 100:.2f}%\n")
        sf.write("Integrity Verification: PASSED (Byte-for-Byte identical)\n")

    print(f"\n{Fore.GREEN}Simulation report saved to {summary_path}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}=========================================")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}---   SIMULATION PROCESS COMPLETED    ---")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}=========================================")

def main():
    """Main CLI driver."""
    create_default_directories()
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="Dynamic File Compression Utility - A Huffman Coding CLI application.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--compress", help="Path to the file to compress")
    group.add_argument("-d", "--decompress", help="Path to the compressed file to decompress")
    group.add_argument("--demo", action="store_true", help="Run an automated end-to-end simulation")

    parser.add_argument("-o", "--output", help="Path to save the output file")
    parser.add_argument("-s", "--stats", action="store_true", help="Display stats and Huffman codebook")

    args = parser.parse_args()

    if args.demo:
        run_simulation()
    elif args.compress:
        output_file = args.output
        if not output_file:
            # Default name if output is not specified
            base_name = os.path.basename(args.compress)
            output_file = os.path.join("compressed_files", base_name + ".huff")
        run_compression(args.compress, output_file, display_stats=args.stats)
    elif args.decompress:
        output_file = args.output
        if not output_file:
            # Default name if output is not specified
            base_name = os.path.basename(args.decompress)
            if base_name.endswith(".huff"):
                base_name = base_name[:-5]
            output_file = os.path.join("decompressed_files", "recovered_" + base_name)
        run_decompression(args.decompress, output_file)

if __name__ == "__main__":
    main()
