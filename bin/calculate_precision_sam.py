#!/usr/bin/env python3
"""
Calculate precision and recall for Columba SAM output

This script parses Columba SAM alignment output and compares barcode calls
against ground truth to compute precision, recall, and accuracy metrics.
"""

import argparse
import csv
import re
from collections import Counter, defaultdict


def parse_sam_alignments(sam_file, identity_threshold=72):
    """
    Parse SAM file and extract barcode calls for each read.
    
    Args:
        sam_file: Path to SAM file
        identity_threshold: Minimum identity to consider alignment valid
    
    Returns:
        dict: read_id -> {barcode_idx, status ('called' or 'rejected')}
    """
    read_calls = {}
    
    with open(sam_file, 'r') as f:
        for line in f:
            if line.startswith('@'):
                # Skip header lines
                continue
            
            fields = line.strip().split('\t')
            if len(fields) < 11:
                continue
            
            read_id = fields[0]
            flag = int(fields[1])
            rname = fields[2]  # Reference name (barcode ID)
            mapq = int(fields[4])
            cigar = fields[5]
            
            # Check if read is unmapped (flag & 4)
            if flag & 4:
                read_calls[read_id] = {
                    'barcode_idx': None,
                    'status': 'rejected',
                    'reason': 'unmapped'
                }
                continue
            
            # Extract barcode index from reference name (e.g., "barcode_0" -> 0)
            match = re.match(r'barcode_(\d+)', rname)
            if not match:
                read_calls[read_id] = {
                    'barcode_idx': None,
                    'status': 'rejected',
                    'reason': 'invalid_rname'
                }
                continue
            
            barcode_idx = int(match.group(1))
            
            # Check alignment quality
            # Note: Columba's -I parameter controls filtering during alignment
            # Here we accept all mapped reads as "called"
            read_calls[read_id] = {
                'barcode_idx': barcode_idx,
                'status': 'called',
                'mapq': mapq
            }
    
    return read_calls


def load_ground_truth(ground_truth_file):
    """
    Load ground truth barcode assignments.
    
    Args:
        ground_truth_file: Path to ground truth file (one barcode index per line)
    
    Returns:
        list: List of ground truth barcode indices (0-based)
    """
    ground_truth = []
    with open(ground_truth_file, 'r') as f:
        for line in f:
            idx = line.strip()
            if idx:
                ground_truth.append(int(idx))
    return ground_truth


def load_barcode_sequences(barcode_file):
    """
    Load barcode sequences from file.
    
    Args:
        barcode_file: Path to barcode file (one barcode per line)
    
    Returns:
        list: List of barcode sequences
    """
    barcodes = []
    with open(barcode_file, 'r') as f:
        for line in f:
            barcode = line.strip()
            if barcode:
                barcodes.append(barcode)
    return barcodes


def calculate_metrics(read_calls, ground_truth, barcodes):
    """
    Calculate precision, recall, and accuracy metrics.
    
    Args:
        read_calls: dict from parse_sam_alignments
        ground_truth: list from load_ground_truth
        barcodes: list from load_barcode_sequences
    
    Returns:
        dict: Metrics dictionary
    """
    total_reads = len(ground_truth)
    
    # OPTIMIZATION: Build a fast lookup dictionary mapping read_idx -> read_id
    # This avoids O(n²) complexity from searching through all keys for each read
    read_idx_to_id = {}
    for read_id in read_calls.keys():
        # Extract read index from read_id (e.g., "read_192_barcode_20444" -> 192)
        # Handle different formats: read_<idx>, read_<idx>_barcode_<bc_idx>, etc.
        parts = read_id.split('_')
        for i, part in enumerate(parts):
            if part == 'read' and i + 1 < len(parts):
                try:
                    read_idx = int(parts[i + 1])
                    read_idx_to_id[read_idx] = read_id
                    break
                except ValueError:
                    continue
    
    # Track statistics
    correct = 0
    incorrect = 0
    unassigned = 0
    misassignments = Counter()
    
    # Process each read in ground truth
    for read_idx, true_barcode_idx in enumerate(ground_truth):
        # Fast O(1) lookup using pre-built index
        read_id = read_idx_to_id.get(read_idx)
        
        # Check if read was called or rejected
        if read_id is None or read_calls[read_id]['status'] == 'rejected':
            unassigned += 1
            continue
        
        predicted_idx = read_calls[read_id]['barcode_idx']
        
        # Compare prediction with ground truth
        if predicted_idx == true_barcode_idx:
            correct += 1
        else:
            incorrect += 1
            # Track misassignment (only store details for mismatches)
            true_bc = barcodes[true_barcode_idx] if true_barcode_idx < len(barcodes) else f"barcode_{true_barcode_idx}"
            pred_bc = barcodes[predicted_idx] if predicted_idx < len(barcodes) else f"barcode_{predicted_idx}"
            misassignments[(true_bc, true_barcode_idx, pred_bc, predicted_idx)] += 1
    
    # Calculate metrics
    assigned = correct + incorrect
    assignment_rate = (assigned / total_reads * 100) if total_reads > 0 else 0
    precision = (correct / assigned * 100) if assigned > 0 else 0
    recall = (correct / total_reads * 100) if total_reads > 0 else 0
    accuracy = recall  # Same as recall in this context
    
    return {
        'total_reads': total_reads,
        'correct': correct,
        'incorrect': incorrect,
        'unassigned': unassigned,
        'assigned': assigned,
        'assignment_rate': assignment_rate,
        'precision': precision,
        'recall': recall,
        'accuracy': accuracy,
        'misassignments': misassignments
    }


def write_report(metrics, report_file, top_n=10):
    """Write detailed text report."""
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("BARCODE CALLING PRECISION REPORT (Columba SAM output)\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("=== OVERALL METRICS ===\n")
        f.write(f"Total reads (ground truth): {metrics['total_reads']}\n")
        f.write(f"Reads processed: {metrics['total_reads']}\n")
        f.write(f"Reads assigned: {metrics['assigned']}\n")
        f.write(f"Reads unassigned/rejected: {metrics['unassigned']}\n\n")
        
        f.write("=== ACCURACY METRICS ===\n")
        f.write(f"Correct assignments: {metrics['correct']}\n")
        f.write(f"Incorrect assignments: {metrics['incorrect']}\n")
        f.write(f"Assignment rate: {metrics['assignment_rate']:.2f}%\n")
        f.write(f"Precision (correct/assigned): {metrics['precision']:.2f}%\n")
        f.write(f"Recall (correct/total): {metrics['recall']:.2f}%\n")
        f.write(f"Accuracy (correct/total): {metrics['accuracy']:.2f}%\n\n")
        
        if metrics['misassignments']:
            f.write(f"=== TOP {top_n} MISASSIGNMENTS ===\n")
            f.write(f"{'Count':<7} | {'True Barcode (idx)':<30} | {'Assigned Barcode (idx)':<30}\n")
            f.write("-" * 80 + "\n")
            
            for (true_bc, true_idx, pred_bc, pred_idx), count in metrics['misassignments'].most_common(top_n):
                true_display = f"{true_bc[:20]}... ({true_idx:>5})" if len(true_bc) > 20 else f"{true_bc} ({true_idx:>5})"
                pred_display = f"{pred_bc[:20]}... ({pred_idx:>5})" if len(pred_bc) > 20 else f"{pred_bc} ({pred_idx:>5})"
                f.write(f"{count:<7} | {true_display:<30} | {pred_display:<30}\n")


def write_summary_csv(metrics, csv_file):
    """Write summary metrics to CSV."""
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['metric', 'value'])
        writer.writerow(['total_reads', metrics['total_reads']])
        writer.writerow(['total_processed', metrics['total_reads']])
        writer.writerow(['correct_assignments', metrics['correct']])
        writer.writerow(['incorrect_assignments', metrics['incorrect']])
        writer.writerow(['unassigned_reads', metrics['unassigned']])
        writer.writerow(['assignment_rate_percent', f"{metrics['assignment_rate']:.4f}"])
        writer.writerow(['precision_percent', f"{metrics['precision']:.4f}"])
        writer.writerow(['recall_percent', f"{metrics['recall']:.4f}"])
        writer.writerow(['accuracy_percent', f"{metrics['accuracy']:.4f}"])


def main():
    parser = argparse.ArgumentParser(description='Calculate precision/recall for Columba SAM output')
    parser.add_argument('barcode_file', help='Barcode reference file (plain text)')
    parser.add_argument('ground_truth', help='Ground truth file (one index per line)')
    parser.add_argument('sam_file', help='Columba SAM alignment output')
    parser.add_argument('report_out', help='Output report file (text)')
    parser.add_argument('summary_out', help='Output summary file (CSV)')
    parser.add_argument('--identity-threshold', type=int, default=72,
                       help='Identity threshold used in Columba (default: 72)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Loading barcode sequences from {args.barcode_file}...")
    barcodes = load_barcode_sequences(args.barcode_file)
    
    if args.verbose:
        print(f"Loading ground truth from {args.ground_truth}...")
    ground_truth = load_ground_truth(args.ground_truth)
    
    if args.verbose:
        print(f"Parsing SAM alignments from {args.sam_file}...")
    read_calls = parse_sam_alignments(args.sam_file, args.identity_threshold)
    
    if args.verbose:
        print("Calculating metrics...")
    metrics = calculate_metrics(read_calls, ground_truth, barcodes)
    
    if args.verbose:
        print(f"Writing report to {args.report_out}...")
    write_report(metrics, args.report_out)
    
    if args.verbose:
        print(f"Writing summary to {args.summary_out}...")
    write_summary_csv(metrics, args.summary_out)
    
    if args.verbose:
        print("\nMetrics Summary:")
        print(f"  Precision: {metrics['precision']:.2f}%")
        print(f"  Recall: {metrics['recall']:.2f}%")
        print(f"  Assignment rate: {metrics['assignment_rate']:.2f}%")


if __name__ == '__main__':
    main()

