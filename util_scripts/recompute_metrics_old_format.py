#!/usr/bin/env python3
"""
Script to recompute metrics for OLD RandomBarcodes header format.
Old format: @read_calledidx_{called_idx}_{barcode_seq}_{read_num}_barcode_{true_idx}
Example: @read_calledidx_1381_CGATCGAAGTATTGTTTCACTGCGCACAAGCACTAA_1_barcode_1381
"""

import os
import sys
import csv
import argparse
import dnaio

def main():
    parser = argparse.ArgumentParser(description='Recompute barcode calling metrics for old RandomBarcodes format')
    parser.add_argument('--results-dir', required=True, help='Path to results directory to scan')
    parser.add_argument('--output-csv', required=True, help='Output CSV file path')
    parser.add_argument('--total-reads', type=int, default=200000, help='Total number of reads (default: 200000)')
    
    args = parser.parse_args()
    
    RESULTS_BASE = args.results_dir
    OUTPUT_CSV = args.output_csv
    TOTAL_READS = args.total_reads

    # Find all sample directories
    print(f"\nScanning {RESULTS_BASE}...")
    samples = []
    
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
                        'fastq_file': fastq_file
                    })

    print(f"Found {len(samples)} samples to process\n")

    # Process each sample
    results = []
    for sample in samples:
        sample_id = sample['sample_id']
        fastq_file = sample['fastq_file']
        
        print(f"Processing {sample_id}...")
        
        # Parse FASTQ file - OLD format
        # @read_calledidx_{called_idx}_{barcode_seq}_{read_num}_barcode_{true_idx}
        called_reads = {}
        with dnaio.open(fastq_file) as reader:
            for r1 in reader:
                header = r1.name.split()[0]
                parts = header.split("_")
                
                # Parts: ['@read', 'calledidx', called_idx, barcode_seq, read_num, 'barcode', true_idx]
                read_idx = int(parts[4])
                called_idx = int(parts[2])
                true_idx = int(parts[6])
                
                called_reads[read_idx] = (called_idx, true_idx)
        
        # Compare called_idx with true_idx
        correct_assignments = []
        incorrect_assignments = []
        
        for read_idx, (called_idx, true_idx) in called_reads.items():
            if called_idx == true_idx:
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
        results.append({
            'tool': 'RandomBarcodes',
            'sample_id': sample_id,
            'identity_threshold': '',
            'nthresh': sample['nthresh'],
            'ntriage': sample['ntriage'],
            'rejection_threshold': '',
            'strategy': '',
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
