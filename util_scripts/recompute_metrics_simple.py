#!/usr/bin/env python3
"""
Simple script to recompute metrics for barcode calling outputs
Following the notebook approach exactly.
"""

import os
import sys
import csv
import argparse
import dnaio
from numpy import genfromtxt

def main():
    parser = argparse.ArgumentParser(description='Recompute barcode calling metrics')
    parser.add_argument('--barcode-file', required=True, help='Path to barcodes file')
    parser.add_argument('--answers-file', required=True, help='Path to ground truth answers file')
    parser.add_argument('--results-dir', required=True, help='Path to results directory to scan')
    parser.add_argument('--output-csv', required=True, help='Output CSV file path')
    parser.add_argument('--tool', required=True, choices=['randombarcodes', 'quik'], help='Tool type')
    parser.add_argument('--total-reads', type=int, default=200000, help='Total number of reads (default: 200000)')
    
    args = parser.parse_args()
    
    BARCODE_FILE = args.barcode_file
    ANSWERS_FILE = args.answers_file
    RESULTS_BASE = args.results_dir
    OUTPUT_CSV = args.output_csv
    TOTAL_READS = args.total_reads
    TOOL = args.tool

    # Load ground truth data once
    print("Loading ground truth data...")
    answers = genfromtxt(ANSWERS_FILE, dtype=int)
    with open(BARCODE_FILE, 'r') as f:
        barcodes = [line.strip().upper() for line in f]

    print(f"Loaded {len(barcodes)} barcodes")
    print(f"Loaded {len(answers)} answers")

    # Find all sample directories
    print(f"\nScanning {RESULTS_BASE}...")
    samples = []
    
    if TOOL == 'randombarcodes':
        for param_dir in sorted(os.listdir(RESULTS_BASE)):
            param_path = os.path.join(RESULTS_BASE, param_dir)
            if not os.path.isdir(param_path):
                continue
            
            # Parse parameters from directory name (e.g., t100_n8)
            parts = param_dir.split('_')
            if len(parts) != 2:
                continue
            
            ntriage = parts[0][1:]  # Remove 't' prefix
            nthresh = parts[1][1:]  # Remove 'n' prefix
            
            # Find sample directory inside
            for item in os.listdir(param_path):
                item_path = os.path.join(param_path, item)
                if os.path.isdir(item_path) and item.startswith('RB'):
                    fastq_file = os.path.join(item_path, f"{item}_R1_filtered.fastq")
                    if os.path.exists(fastq_file):
                        samples.append({
                            'sample_id': f"RB_{param_dir}",
                            'ntriage': ntriage,
                            'nthresh': nthresh,
                            'rejection_threshold': '',
                            'strategy': '',
                            'fastq_file': fastq_file
                        })
    
    elif TOOL == 'quik':
        for param_dir in sorted(os.listdir(RESULTS_BASE)):
            param_path = os.path.join(RESULTS_BASE, param_dir)
            if not os.path.isdir(param_path):
                continue
            
            # Parse parameters from directory name (e.g., 4mer_r8)
            parts = param_dir.split('_')
            if len(parts) != 2:
                continue
            
            strategy = parts[0]  # e.g., "4mer"
            rejection_threshold = parts[1][1:]  # Remove 'r' prefix
            
            # Find sample directory inside
            for item in os.listdir(param_path):
                item_path = os.path.join(param_path, item)
                if os.path.isdir(item_path) and item.startswith('QUIK'):
                    fastq_file = os.path.join(item_path, f"{item}_R1_filtered.fastq")
                    if os.path.exists(fastq_file):
                        samples.append({
                            'sample_id': f"QUIK_{param_dir}",
                            'ntriage': '',
                            'nthresh': '',
                            'rejection_threshold': rejection_threshold,
                            'strategy': strategy,
                            'fastq_file': fastq_file
                        })

    print(f"Found {len(samples)} samples to process\n")

    # Process each sample
    results = []
    for sample in samples:
        sample_id = sample['sample_id']
        fastq_file = sample['fastq_file']
        
        print(f"Processing {sample_id}...")
        
        # Parse FASTQ file - handle different header formats
        # Store as dict: read_idx -> (called_idx or called_seq, true_idx)
        called_reads = {}
        with dnaio.open(fastq_file) as reader:
            for r1 in reader:
                header = r1.name.split()[0]
                parts = header.split("_")
                
                if TOOL == 'randombarcodes':
                    # RandomBarcodes format: @read_{read_num}_calledidx_{called_idx}_{barcode_seq}_barcode_{true_idx}
                    # Example: @read_1_calledidx_1381_CGATCGAAGTATTGTTTCACTGCGCACAAGCACTAA_barcode_1381
                    read_idx = int(parts[1])
                    called_idx = int(parts[3])
                    true_idx = int(parts[6])
                    called_reads[read_idx] = (called_idx, true_idx)
                elif TOOL == 'quik':
                    # QUIK format: @read_{read_num}_barcode_{true_idx}_{barcode_seq}
                    # Example: @read_1_barcode_1381_CGATCGAAGTATTGTTTCACTGCGCACAAGCACTAA
                    read_idx = int(parts[1])
                    barcode_seq = parts[4]
                    true_idx = int(parts[3])
                    called_reads[read_idx] = (barcode_seq, true_idx)
        
        # Compare with ground truth
        correct_assignments = []
        incorrect_assignments = []
        
        if TOOL == 'randombarcodes':
            # For RandomBarcodes: compare called_idx with true_idx directly
            for read_idx, (called_idx, true_idx) in called_reads.items():
                if called_idx == true_idx:
                    correct_assignments.append(read_idx)
                else:
                    incorrect_assignments.append(read_idx)
        
        elif TOOL == 'quik':
            # For QUIK: compare called sequence with true sequence
            for read_idx, (barcode_seq, true_idx) in called_reads.items():
                if true_idx < len(barcodes):  # Safety check
                    true_barcode = barcodes[true_idx]
                    if barcode_seq == true_barcode:
                        correct_assignments.append(read_idx)
                    else:
                        incorrect_assignments.append(read_idx)
        
        # Calculate metrics
        assigned = len(called_reads)
        correct = len(correct_assignments)
        incorrect = len(incorrect_assignments)
        unassigned = TOTAL_READS - assigned
        
        assignment_rate = (assigned / TOTAL_READS * 100) if TOTAL_READS > 0 else 0.0
        precision = (correct / assigned * 100) if assigned > 0 else 0.0
        recall = (correct / TOTAL_READS * 100) if TOTAL_READS > 0 else 0.0
        accuracy = recall
        f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        
        print(f"  Assigned: {assigned}, Correct: {correct}, Incorrect: {incorrect}")
        print(f"  Precision: {precision:.2f}%, Recall: {recall:.2f}%\n")
        
        # Store result
        tool_name = 'QUIK' if TOOL == 'quik' else 'RandomBarcodes'
        results.append({
            'tool': tool_name,
            'sample_id': sample_id,
            'identity_threshold': '',
            'nthresh': sample['nthresh'],
            'ntriage': sample['ntriage'],
            'rejection_threshold': sample['rejection_threshold'],
            'strategy': sample['strategy'],
            'total_reads': TOTAL_READS,
            'correct': correct,
            'incorrect': incorrect,
            'unassigned': unassigned,
            'assignment_rate': assignment_rate,
            'precision': precision,
            'recall': recall,
            'accuracy': accuracy,
            'f1_score': f1_score
        })
    # Write results to CSV
    print(f"Writing results to {OUTPUT_CSV}...")
    fieldnames = [
        'tool', 'sample_id', 'identity_threshold', 'nthresh', 'ntriage',
        'rejection_threshold', 'strategy', 'total_reads', 'correct',
        'incorrect', 'unassigned', 'assignment_rate', 'precision',
        'recall', 'accuracy', 'f1_score'
    ]

    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone! Processed {len(results)} samples")
    print(f"Results saved to: {OUTPUT_CSV}")

    # Print summary
    if results:
        avg_precision = sum(r['precision'] for r in results) / len(results)
        avg_recall = sum(r['recall'] for r in results) / len(results)
        avg_f1 = sum(r['f1_score'] for r in results) / len(results)
        
        print(f"\nAverage metrics:")
        print(f"  Precision: {avg_precision:.2f}%")
        print(f"  Recall: {avg_recall:.2f}%")
        print(f"  F1-Score: {avg_f1:.2f}")

if __name__ == '__main__':
    main()
