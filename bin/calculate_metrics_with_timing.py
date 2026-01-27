#!/usr/bin/env python3
"""
Calculate precision, recall, and timing metrics for barcode calling tools.

This script extends calculate_precision.py to also extract and report timing information:
- RandomBarcodes: Not directly available in batch script, but can be measured from log timestamps
- QUIK: Reads "Time per read" from barcode_calling_stats.txt
- Columba: Parses alignment log for timing information
"""

import argparse
import sys
import re
import os
from collections import defaultdict


def load_barcodes(barcode_file):
    """Load barcodes from file and create index-to-barcode mapping."""
    barcodes = []
    with open(barcode_file, 'r') as f:
        for line in f:
            barcode = line.strip()
            if barcode:
                barcodes.append(barcode)
    
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
    Supports both old and new header formats with _calledidx_.
    """
    read_assignments = {}
    barcode_to_idx_lower = {bc.lower(): idx for bc, idx in barcode_to_idx.items()}
    
    # Prefix map for partial matches
    barcode_prefix_map = defaultdict(list)
    for bc, idx in barcode_to_idx_lower.items():
        barcode_prefix_map[bc].append(idx)
    
    with open(fastq_file, 'r') as f:
        line_num = 0
        for line in f:
            line_num += 1
            if line_num % 4 == 1:  # Header line
                header = line.strip()
                
                read_num = None
                called_idx = None
                
                # PRIORITY 1: Check for _calledidx_<num> pattern (new format)
                calledidx_match = re.search(r'_calledidx_(\d+)', header)
                
                if calledidx_match:
                    called_idx = int(calledidx_match.group(1))
                    
                    # Extract read number
                    read_match = re.match(r'^@read_(\d+)', header)
                    if read_match:
                        read_num = int(read_match.group(1))
                    else:
                        parts = header.split('_')
                        for i, part in enumerate(parts):
                            if part.isdigit() and i > 0:
                                if i > 0 and parts[i-1] not in ['calledidx', 'barcode']:
                                    read_num = int(part)
                                    break
                                elif i+1 < len(parts) and parts[i+1] == 'barcode':
                                    read_num = int(part)
                                    break
                    
                    if read_num is not None and called_idx is not None:
                        read_assignments[read_num] = called_idx
                        continue
                
                # FALLBACK: Old format - parse barcode sequence
                parts = header.split('_')
                potential_barcode = None
                
                if len(parts) >= 3:
                    if len(parts) >= 5 and parts[3] == 'barcode':
                        try:
                            read_num = int(parts[2])
                            potential_barcode = parts[1].lower()
                        except ValueError:
                            pass
                    
                    if read_num is None:
                        try:
                            read_num = int(parts[1])
                            potential_barcode = parts[-1].split()[0].lower()
                        except ValueError:
                            continue
                    
                    if read_num is not None and potential_barcode:
                        if potential_barcode in barcode_to_idx_lower:
                            read_assignments[read_num] = barcode_to_idx_lower[potential_barcode]
                        elif potential_barcode in barcode_prefix_map:
                            matches = barcode_prefix_map[potential_barcode]
                            if len(matches) == 1:
                                read_assignments[read_num] = matches[0]
    
    return read_assignments


def calculate_metrics(ground_truth, read_assignments, total_reads):
    """Calculate precision, recall, and accuracy metrics."""
    correct_assignments = 0
    incorrect_assignments = 0
    
    for read_num, called_idx in read_assignments.items():
        if read_num < len(ground_truth):
            if ground_truth[read_num] == called_idx:
                correct_assignments += 1
            else:
                incorrect_assignments += 1
    
    total_assignments = len(read_assignments)
    precision = (correct_assignments / total_assignments * 100) if total_assignments > 0 else 0.0
    recall = (total_assignments / total_reads * 100) if total_reads > 0 else 0.0
    
    if precision + recall > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0
    
    return {
        'total_reads': total_reads,
        'assigned_reads': total_assignments,
        'correct_assignments': correct_assignments,
        'incorrect_assignments': incorrect_assignments,
        'recall': recall,
        'precision': precision,
        'f1_score': f1_score
    }


def extract_quik_timing(stats_file):
    """
    Extract timing information from QUIK barcode_calling_stats.txt.
    Looks for lines like: "Time per read: 0.0197177 ms"
    """
    if not os.path.exists(stats_file):
        return None, None
    
    time_per_read_ms = None
    total_time_s = None
    total_reads = None
    
    with open(stats_file, 'r') as f:
        for line in f:
            # Time per read: 0.0197177 ms
            match_per_read = re.search(r'Time per read:\s+([\d.]+)\s+ms', line)
            if match_per_read:
                time_per_read_ms = float(match_per_read.group(1))
            
            # Barcode calling completed in 3.94354 seconds
            match_total = re.search(r'completed in\s+([\d.]+)\s+seconds', line)
            if match_total:
                total_time_s = float(match_total.group(1))
            
            # Total reads: 200000
            match_reads = re.search(r'Total reads:\s+(\d+)', line)
            if match_reads:
                total_reads = int(match_reads.group(1))
    
    return {
        'time_per_read_ms': time_per_read_ms,
        'total_time_s': total_time_s,
        'total_reads': total_reads
    }


def extract_randombarcodes_timing(work_dir, sample_id):
    """
    Extract timing for RandomBarcodes from Nextflow .command.log.
    The BarCallingPress_batch.py script doesn't output timing directly,
    but we can measure from process start/end in Nextflow logs.
    """
    # Try to find the RANDOMBARCODES process work directory
    command_log = None
    
    # Search pattern: work_dir/<hash>/<hash>/.command.log
    if os.path.exists(work_dir):
        for root, dirs, files in os.walk(work_dir):
            if '.command.log' in files:
                log_path = os.path.join(root, '.command.log')
                # Check if this is a RANDOMBARCODES process
                with open(log_path, 'r') as f:
                    content = f.read(500)
                    if 'BarCallingPress_batch.py' in content or 'Starting Demux' in content:
                        command_log = log_path
                        break
    
    if not command_log or not os.path.exists(command_log):
        return None
    
    # Parse the log for timing information
    # Look for "Starting Demux" and "DEMUX SUMMARY" timestamps
    start_time = None
    end_time = None
    reads_processed = None
    
    with open(command_log, 'r') as f:
        for line in f:
            if 'Starting Demux' in line:
                # Extract timestamp if available
                pass
            if 'Total reads processed:' in line:
                match = re.search(r'Total reads processed:\s+(\d+)', line)
                if match:
                    reads_processed = int(match.group(1))
    
    # Since timestamps aren't in the Python output, we'll return None
    # and rely on Nextflow task timing instead
    return {
        'time_per_read_ms': None,
        'total_time_s': None,
        'total_reads': reads_processed
    }


def extract_columba_timing(work_dir, sample_id):
    """
    Extract timing for Columba from .command.log.
    Columba outputs timing info to stderr/stdout which Nextflow captures.
    """
    command_out = None
    
    # Search for Columba ALIGN process
    if os.path.exists(work_dir):
        for root, dirs, files in os.walk(work_dir):
            if '.command.out' in files:
                out_path = os.path.join(root, '.command.out')
                # Check if this is a Columba align process
                with open(out_path, 'r') as f:
                    content = f.read(500)
                    if 'columba' in content.lower() or 'alignment' in content.lower():
                        command_out = out_path
                        break
    
    if not command_out or not os.path.exists(command_out):
        return None
    
    # Parse Columba output for timing
    # Columba uses a logger with format like [time] [INFO] message
    total_time_s = None
    total_reads = None
    
    with open(command_out, 'r') as f:
        lines = f.readlines()
        
        # Find first and last timestamps
        first_time = None
        last_time = None
        
        for line in lines:
            # Format: [00.123] [INFO] message
            match = re.match(r'\[(\d+\.\d+)\]', line)
            if match:
                timestamp = float(match.group(1))
                if first_time is None:
                    first_time = timestamp
                last_time = timestamp
            
            # Also look for read count
            if 'Read and concatenated' in line or 'Processed' in line:
                match_reads = re.search(r'(\d+)\s+(?:sequence|read)', line)
                if match_reads:
                    total_reads = int(match_reads.group(1))
        
        if first_time is not None and last_time is not None:
            total_time_s = last_time - first_time
    
    if total_time_s and total_reads:
        time_per_read_ms = (total_time_s / total_reads) * 1000
    else:
        time_per_read_ms = None
    
    return {
        'time_per_read_ms': time_per_read_ms,
        'total_time_s': total_time_s,
        'total_reads': total_reads
    }


def main():
    parser = argparse.ArgumentParser(
        description='Calculate barcode calling metrics with timing information'
    )
    parser.add_argument('fastq_file', help='FASTQ file with barcode calls')
    parser.add_argument('barcode_file', help='File containing barcode sequences')
    parser.add_argument('ground_truth', help='File containing ground truth barcode indices')
    parser.add_argument('output_report', help='Output text report file')
    parser.add_argument('output_summary', help='Output CSV summary file')
    parser.add_argument('--total-reads', type=int, required=True, help='Total number of input reads')
    parser.add_argument('--tool', choices=['randombarcodes', 'quik', 'columba'], required=True,
                        help='Tool used for barcode calling')
    parser.add_argument('--stats-file', help='Tool-specific stats file (e.g., QUIK stats.txt)')
    parser.add_argument('--work-dir', help='Nextflow work directory for timing extraction')
    parser.add_argument('--sample-id', help='Sample ID for timing extraction')
    
    args = parser.parse_args()
    
    # Load data
    barcodes, barcode_to_idx = load_barcodes(args.barcode_file)
    ground_truth = load_ground_truth(args.ground_truth)
    
    # Parse called barcodes
    read_assignments = parse_fastq_barcodes(args.fastq_file, barcode_to_idx)
    
    # Calculate metrics
    metrics = calculate_metrics(ground_truth, read_assignments, args.total_reads)
    
    # Extract timing based on tool
    timing_info = None
    if args.tool == 'quik' and args.stats_file:
        timing_info = extract_quik_timing(args.stats_file)
    elif args.tool == 'randombarcodes' and args.work_dir and args.sample_id:
        timing_info = extract_randombarcodes_timing(args.work_dir, args.sample_id)
    elif args.tool == 'columba' and args.work_dir and args.sample_id:
        timing_info = extract_columba_timing(args.work_dir, args.sample_id)
    
    # Write report
    with open(args.output_report, 'w') as f:
        f.write("Barcode Calling Precision Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Tool: {args.tool}\n")
        f.write(f"Total reads: {metrics['total_reads']}\n")
        f.write(f"Assigned reads: {metrics['assigned_reads']} ({metrics['recall']:.2f}%)\n")
        f.write(f"Correct assignments: {metrics['correct_assignments']}\n")
        f.write(f"Incorrect assignments: {metrics['incorrect_assignments']}\n\n")
        f.write(f"Recall: {metrics['recall']:.2f}%\n")
        f.write(f"Precision: {metrics['precision']:.2f}%\n")
        f.write(f"F1 Score: {metrics['f1_score']:.2f}%\n")
        
        if timing_info:
            f.write("\n" + "=" * 50 + "\n")
            f.write("Timing Information\n")
            f.write("=" * 50 + "\n")
            if timing_info.get('total_time_s'):
                f.write(f"Total time: {timing_info['total_time_s']:.3f} seconds\n")
            if timing_info.get('time_per_read_ms'):
                f.write(f"Time per read: {timing_info['time_per_read_ms']:.6f} ms\n")
            if timing_info.get('total_reads'):
                f.write(f"Reads processed: {timing_info['total_reads']}\n")
    
    # Write CSV summary
    with open(args.output_summary, 'w') as f:
        headers = [
            'tool', 'total_reads', 'assigned_reads', 'correct_assignments',
            'incorrect_assignments', 'recall', 'precision', 'f1_score',
            'total_time_s', 'time_per_read_ms'
        ]
        f.write(','.join(headers) + '\n')
        
        row = [
            args.tool,
            str(metrics['total_reads']),
            str(metrics['assigned_reads']),
            str(metrics['correct_assignments']),
            str(metrics['incorrect_assignments']),
            f"{metrics['recall']:.2f}",
            f"{metrics['precision']:.2f}",
            f"{metrics['f1_score']:.2f}",
            f"{timing_info.get('total_time_s', ''):.3f}" if timing_info and timing_info.get('total_time_s') else '',
            f"{timing_info.get('time_per_read_ms', ''):.6f}" if timing_info and timing_info.get('time_per_read_ms') else ''
        ]
        f.write(','.join(row) + '\n')
    
    print(f"Metrics calculated successfully")
    print(f"Recall: {metrics['recall']:.2f}%")
    print(f"Precision: {metrics['precision']:.2f}%")
    if timing_info and timing_info.get('time_per_read_ms'):
        print(f"Time per read: {timing_info['time_per_read_ms']:.6f} ms")


if __name__ == '__main__':
    main()
