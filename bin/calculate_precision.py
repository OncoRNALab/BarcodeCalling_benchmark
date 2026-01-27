#!/usr/bin/env python3
"""
Calculate precision of barcode calling against ground truth.

This script compares barcode calling results from FASTQ files against
a ground truth file containing the correct barcode indices for each read.
Also extracts timing information from stats files when available.
"""

import argparse
import sys
import os
import re
from collections import defaultdict


def load_barcodes(barcode_file):
    """Load barcodes from file and create index-to-barcode mapping."""
    barcodes = []
    with open(barcode_file, 'r') as f:
        for line in f:
            barcode = line.strip()
            if barcode:
                barcodes.append(barcode)
    
    # Create reverse mapping: barcode -> index
    barcode_to_idx = {bc: idx for idx, bc in enumerate(barcodes)}
    
    return barcodes, barcode_to_idx


def load_ground_truth(truth_file):
    """Load ground truth barcode indices."""
    ground_truth = []
    with open(truth_file, 'r') as f:
        for line in f:
            idx = int(line.strip())
            ground_truth.append(idx)
    return ground_truth


def parse_fastq_barcodes(fastq_file, barcode_to_idx):
    """
    Parse FASTQ file to extract assigned barcodes from headers.
    
    Assumes headers are in format: @read_N_BARCODE
    Returns a dictionary mapping read_number -> barcode_index
    """
    read_assignments = {}  # read_number -> barcode_idx
    
    # Create a lowercase version of barcode mapping for case-insensitive matching
    barcode_to_idx_lower = {bc.lower(): idx for bc, idx in barcode_to_idx.items()}
    
    # Also create a mapping for partial matches (prefixes)
    # In case the header has truncated barcodes
    barcode_prefix_map = {}
    for bc_lower, idx in barcode_to_idx_lower.items():
        # Map various prefix lengths to handle truncation
        for prefix_len in range(min(26, len(bc_lower)), len(bc_lower) + 1):
            prefix = bc_lower[:prefix_len]
            if prefix not in barcode_prefix_map:
                barcode_prefix_map[prefix] = []
            barcode_prefix_map[prefix].append(idx)
    
    with open(fastq_file, 'r') as f:
        line_num = 0
        read_counter = 0  # Sequential read counter (1-based)
        for line in f:
            line_num += 1
            if line_num % 4 == 1:  # Header line
                read_counter += 1  # Increment for each read
                header = line.strip()
                # Extract read number and called barcode index from header
                # Supports multiple formats (in priority order):
                # 1. NEW: Headers with _calledidx_<INDEX> (direct index, no lookup needed)
                # 2. @read_BARCODE_N_barcode_INDEX (RandomBarcodes old format)
                # 3. @read_N_BARCODE (QUIK old format)
                
                read_num = None
                called_idx = None
                
                # PRIORITY 1: Check for _calledidx_<num> pattern (new format)
                import re
                calledidx_match = re.search(r'_calledidx_(\d+)', header)
                
                if calledidx_match:
                    # New format with direct index AND embedded truth
                    # Format: @read_calledidx_<CALLED_IDX>_<BARCODE>_<N>_barcode_<TRUE_IDX>
                    # We can extract both called and true indices from the same header!
                    called_idx = int(calledidx_match.group(1))
                    
                    # Extract true barcode index (after "barcode_" at position [6])
                    true_idx_match = re.search(r'_barcode_(\d+)', header)
                    if true_idx_match:
                        true_idx = int(true_idx_match.group(1))
                        # Store both indices for validation
                        read_num = read_counter
                        read_assignments[read_num] = (called_idx, true_idx)
                    else:
                        # Fallback: use ground truth file
                        read_num = read_counter
                        read_assignments[read_num] = called_idx
                    continue
                
                # FALLBACK: Old format - parse barcode sequence and map to index
                parts = header.split('_')
                potential_barcode = None
                
                if len(parts) >= 3:
                    # Try RandomBarcodes format: @read_BARCODE_N_barcode_INDEX
                    if len(parts) >= 5 and parts[3] == 'barcode':
                        try:
                            read_num = int(parts[2])
                            potential_barcode = parts[1].lower()
                        except ValueError:
                            pass
                    
                    # If not RandomBarcodes format, try QUIK format: @read_N_BARCODE
                    if read_num is None:
                        try:
                            read_num = int(parts[1])
                            potential_barcode = parts[-1].split()[0].lower()
                        except ValueError:
                            continue
                    
                    if read_num is not None and potential_barcode:
                        # Try exact match first
                        if potential_barcode in barcode_to_idx_lower:
                            read_assignments[read_num] = barcode_to_idx_lower[potential_barcode]
                        # Try prefix match (for truncated barcodes)
                        elif potential_barcode in barcode_prefix_map:
                            matches = barcode_prefix_map[potential_barcode]
                            if len(matches) == 1:
                                read_assignments[read_num] = matches[0]
                            # else: ambiguous, skip this read
    
    return read_assignments


def calculate_metrics(ground_truth, read_assignments, total_reads):
    """
    Calculate precision, recall, and accuracy metrics.
    
    Args:
        ground_truth: list of barcode indices (one per read, 0-based indexing)
        read_assignments: dict mapping read_number -> assigned barcode_idx OR (called_idx, true_idx) tuple
        total_reads: total number of reads in ground truth
    """
    
    # Count matches
    correct = 0
    incorrect = 0
    unassigned = 0
    
    # Create mapping for detailed analysis
    confusion_matrix = defaultdict(lambda: defaultdict(int))
    
    # Check if we have tuples (new format with embedded truth) or just indices (old format)
    sample_value = next(iter(read_assignments.values())) if read_assignments else None
    has_embedded_truth = isinstance(sample_value, tuple)
    
    if has_embedded_truth:
        # NEW FORMAT: Each entry is (called_idx, true_idx)
        # We don't need the ground_truth file - truth is embedded in headers
        for read_num, (called_idx, true_idx) in read_assignments.items():
            if called_idx == true_idx:
                correct += 1
                confusion_matrix[true_idx][called_idx] += 1
            else:
                incorrect += 1
                confusion_matrix[true_idx][called_idx] += 1
        
        # Unassigned = total - assigned
        total_assigned = len(read_assignments)
        unassigned = total_reads - total_assigned
        
    else:
        # OLD FORMAT: Use ground truth file
        # Iterate through all reads (ground truth is 0-indexed, but read numbers are 1-based)
        for read_idx in range(total_reads):
            read_num = read_idx + 1  # Convert to 1-based read number
            true_barcode_idx = ground_truth[read_idx]
            
            if read_num in read_assignments:
                # Read was assigned a barcode
                assigned_idx = read_assignments[read_num]
                
                if assigned_idx == true_barcode_idx:
                    correct += 1
                    confusion_matrix[true_barcode_idx][assigned_idx] += 1
                else:
                    incorrect += 1
                    confusion_matrix[true_barcode_idx][assigned_idx] += 1
            else:
                # Read was not assigned (rejected)
                unassigned += 1
                confusion_matrix[true_barcode_idx][-1] += 1
    
    # Calculate metrics
    total_assigned = correct + incorrect
    
    precision = (correct / total_assigned * 100) if total_assigned > 0 else 0
    recall = (correct / total_reads * 100) if total_reads > 0 else 0
    accuracy = (correct / total_reads * 100) if total_reads > 0 else 0
    assignment_rate = (total_assigned / total_reads * 100) if total_reads > 0 else 0
    
    metrics = {
        'total_reads': total_reads,
        'total_assigned': total_assigned,
        'correct': correct,
        'incorrect': incorrect,
        'unassigned': unassigned,
        'precision': precision,
        'recall': recall,
        'accuracy': accuracy,
        'assignment_rate': assignment_rate,
        'confusion_matrix': confusion_matrix
    }
    
    return metrics


def write_report(metrics, output_file, barcodes, timing=None):
    """Write detailed precision report."""
    
    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("BARCODE CALLING PRECISION REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("=== OVERALL METRICS ===\n")
        f.write(f"Total reads (ground truth): {metrics['total_reads']}\n")
        f.write(f"Reads assigned: {metrics['total_assigned']}\n")
        f.write(f"Reads unassigned/rejected: {metrics['unassigned']}\n\n")
        
        f.write("=== ACCURACY METRICS ===\n")
        f.write(f"Correct assignments: {metrics['correct']}\n")
        f.write(f"Incorrect assignments: {metrics['incorrect']}\n")
        f.write(f"Assignment rate: {metrics['assignment_rate']:.2f}%\n")
        f.write(f"Precision (correct/assigned): {metrics['precision']:.2f}%\n")
        f.write(f"Recall (correct/total): {metrics['recall']:.2f}%\n")
        f.write(f"Accuracy (correct/total): {metrics['accuracy']:.2f}%\n\n")
        
        if timing:
            f.write("=== TIMING INFORMATION ===\n")
            if timing.get('total_time_s'):
                f.write(f"Total time: {timing['total_time_s']:.3f} seconds\n")
            if timing.get('time_per_read_ms'):
                f.write(f"Time per read: {timing['time_per_read_ms']:.6f} ms\n")
            f.write("\n")
        
        # Find most common misassignments
        f.write("=== TOP MISASSIGNMENTS ===\n")
        misassignments = []
        for true_idx, assigned_dict in metrics['confusion_matrix'].items():
            for assigned_idx, count in assigned_dict.items():
                if assigned_idx != true_idx and assigned_idx != -1:
                    misassignments.append((count, true_idx, assigned_idx))
        
        misassignments.sort(reverse=True)
        
        if misassignments:
            f.write("Count | True Barcode (idx) | Assigned Barcode (idx)\n")
            f.write("-" * 80 + "\n")
            for count, true_idx, assigned_idx in misassignments[:20]:
                true_bc = barcodes[true_idx][:20] + "..." if len(barcodes[true_idx]) > 20 else barcodes[true_idx]
                assigned_bc = barcodes[assigned_idx][:20] + "..." if len(barcodes[assigned_idx]) > 20 else barcodes[assigned_idx]
                f.write(f"{count:5d} | {true_bc:20s} ({true_idx:5d}) | {assigned_bc:20s} ({assigned_idx:5d})\n")
        else:
            f.write("No misassignments found.\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")


def write_summary_csv(metrics, output_file, timing=None):
    """Write summary metrics in CSV format for easy parsing."""
    
    with open(output_file, 'w') as f:
        f.write("metric,value\n")
        f.write(f"total_reads,{metrics['total_reads']}\n")
        f.write(f"total_assigned,{metrics['total_assigned']}\n")
        f.write(f"correct_assignments,{metrics['correct']}\n")
        f.write(f"incorrect_assignments,{metrics['incorrect']}\n")
        f.write(f"unassigned_reads,{metrics['unassigned']}\n")
        f.write(f"assignment_rate_percent,{metrics['assignment_rate']:.4f}\n")
        f.write(f"precision_percent,{metrics['precision']:.4f}\n")
        f.write(f"recall_percent,{metrics['recall']:.4f}\n")
        f.write(f"accuracy_percent,{metrics['accuracy']:.4f}\n")
        
        if timing:
            if timing.get('total_time_s'):
                f.write(f"total_time_seconds,{timing['total_time_s']:.3f}\n")
            if timing.get('time_per_read_ms'):
                f.write(f"time_per_read_ms,{timing['time_per_read_ms']:.6f}\n")


def extract_timing_from_stats(stats_file):
    """
    Extract timing information from barcode_calling_stats.txt file.
    Works for QUIK, RandomBarcodes, and Columba stats files.
    """
    if not stats_file or not os.path.exists(stats_file):
        return None
    
    time_per_read_ms = None
    total_time_s = None
    
    try:
        with open(stats_file, 'r') as f:
            for line in f:
                # QUIK & Columba format: "Time per read: 0.0197177 ms"
                match_per_read = re.search(r'Time per read:\s+([\d.]+)\s+ms', line)
                if match_per_read:
                    time_per_read_ms = float(match_per_read.group(1))
                
                # QUIK format: "Barcode calling completed in 3.94354 seconds"
                match_quik_total = re.search(r'completed in\s+([\d.]+)\s+seconds', line)
                if match_quik_total:
                    total_time_s = float(match_quik_total.group(1))
                
                # RandomBarcodes format: "Barcode decoding completed in 3.456 seconds"
                match_rb_total = re.search(r'decoding completed in\s+([\d.]+)\s+seconds', line)
                if match_rb_total:
                    total_time_s = float(match_rb_total.group(1))
                
                # Columba format: "Total alignment time: 4.567 seconds"
                match_columba_total = re.search(r'Total alignment time:\s+([\d.]+)\s+seconds', line)
                if match_columba_total:
                    total_time_s = float(match_columba_total.group(1))
                
                # New unified format: "Total time (seconds): 1903.064"
                match_total_time = re.search(r'Total time \(seconds\):\s+([\d.]+)', line)
                if match_total_time:
                    total_time_s = float(match_total_time.group(1))
                
                # New unified format: "Time per read (milliseconds): 9.515321"
                match_time_per_read = re.search(r'Time per read \(milliseconds\):\s+([\d.]+)', line)
                if match_time_per_read:
                    time_per_read_ms = float(match_time_per_read.group(1))
    except Exception as e:
        print(f"Warning: Could not extract timing from {stats_file}: {e}")
        return None
    
    if time_per_read_ms or total_time_s:
        return {
            'time_per_read_ms': time_per_read_ms,
            'total_time_s': total_time_s
        }
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Calculate barcode calling precision against ground truth'
    )
    parser.add_argument('barcode_file', help='File containing barcode sequences (one per line)')
    parser.add_argument('truth_file', help='Ground truth file with barcode indices (one per line)')
    parser.add_argument('fastq_r1', help='Filtered R1 FASTQ file with assigned barcodes')
    parser.add_argument('output_report', help='Output report file')
    parser.add_argument('output_csv', help='Output CSV summary file')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    parser.add_argument('--stats-file', help='Optional stats file for timing extraction')
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Loading barcodes...")
    barcodes, barcode_to_idx = load_barcodes(args.barcode_file)
    if args.verbose:
        print(f"Loaded {len(barcodes)} barcodes")
    
    if args.verbose:
        print("Loading ground truth...")
    ground_truth = load_ground_truth(args.truth_file)
    if args.verbose:
        print(f"Loaded {len(ground_truth)} ground truth entries")
    
    if args.verbose:
        print("Parsing FASTQ file...")
    read_assignments = parse_fastq_barcodes(args.fastq_r1, barcode_to_idx)
    if args.verbose:
        print(f"Found {len(read_assignments)} assigned reads from FASTQ")
    
    total_reads = len(ground_truth)
    
    if args.verbose:
        print("Calculating metrics...")
    metrics = calculate_metrics(ground_truth, read_assignments, total_reads)
    
    # Extract timing if stats file provided
    timing = None
    if args.stats_file:
        timing = extract_timing_from_stats(args.stats_file)
        if args.verbose and timing:
            print(f"Extracted timing: {timing}")
    
    if args.verbose:
        print("Writing reports...")
    write_report(metrics, args.output_report, barcodes, timing)
    write_summary_csv(metrics, args.output_csv, timing)
    
    # Print summary to stdout
    print("\n" + "=" * 80)
    print("PRECISION CALCULATION SUMMARY")
    print("=" * 80)
    print(f"Total reads: {metrics['total_reads']}")
    print(f"Correct: {metrics['correct']}")
    print(f"Incorrect: {metrics['incorrect']}")
    print(f"Unassigned: {metrics['unassigned']}")
    print(f"Precision: {metrics['precision']:.2f}%")
    print(f"Recall: {metrics['recall']:.2f}%")
    print(f"Accuracy: {metrics['accuracy']:.2f}%")
    if timing:
        if timing.get('time_per_read_ms'):
            print(f"Time per read: {timing['time_per_read_ms']:.6f} ms")
        if timing.get('total_time_s'):
            print(f"Total time: {timing['total_time_s']:.3f} seconds")
    print("=" * 80 + "\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
