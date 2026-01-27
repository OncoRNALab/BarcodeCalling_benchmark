#!/usr/bin/env python3
"""
Fast Columba metrics calculator

Optimized for speed - only parses what's needed from SAM file.
The read ID contains the ground truth: read_N_barcode_TRUE_INDEX
The reference field contains the call: barcode_CALLED_INDEX
"""

import sys
import csv
import re
from collections import Counter

def parse_sam_fast(sam_file):
    """
    Fast SAM parser - extracts only what we need.
    
    Returns:
        correct: number of correct assignments
        incorrect: number of incorrect assignments  
        unmapped: number of unmapped reads
        total_reads: total number of reads processed
    """
    correct = 0
    incorrect = 0
    unmapped = 0
    total_reads = 0
    
    read_pattern = re.compile(r'read_(\d+)_barcode_(\d+)')
    ref_pattern = re.compile(r'barcode_(\d+)')
    
    seen_reads = set()
    
    with open(sam_file, 'r') as f:
        for line in f:
            # Skip headers
            if line.startswith('@'):
                continue
            
            # Parse only the fields we need
            parts = line.split('\t', 4)  # Only need first 3 columns
            if len(parts) < 3:
                continue
            
            read_id = parts[0]
            flag = int(parts[1])
            ref_name = parts[2]
            
            # Extract read number and true barcode from read ID
            match = read_pattern.match(read_id)
            if not match:
                continue
            
            read_num = int(match.group(1))
            true_barcode = int(match.group(2))
            
            # Skip secondary alignments (flag & 256)
            # We only want the best/primary alignment
            if flag & 256:
                continue
            
            # Only count each read once (in case of duplicates)
            if read_num in seen_reads:
                continue
            seen_reads.add(read_num)
            
            total_reads += 1
            
            # Check if unmapped (flag & 4) or ref is *
            if (flag & 4) or ref_name == '*':
                unmapped += 1
            else:
                # Extract called barcode from reference name
                ref_match = ref_pattern.match(ref_name)
                if ref_match:
                    called_barcode = int(ref_match.group(1))
                    
                    if called_barcode == true_barcode:
                        correct += 1
                    else:
                        incorrect += 1
                else:
                    # Invalid reference name
                    unmapped += 1
    
    return correct, incorrect, unmapped, total_reads


def write_report(metrics, output_file):
    """Write detailed report"""
    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("COLUMBA BARCODE CALLING PRECISION REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total reads: {metrics['total_reads']}\n")
        f.write(f"Mapped reads: {metrics['assigned']} ({metrics['assignment_rate']:.2f}%)\n")
        f.write(f"Unmapped reads: {metrics['unmapped']}\n\n")
        
        f.write(f"Correct assignments: {metrics['correct']}\n")
        f.write(f"Incorrect assignments: {metrics['incorrect']}\n\n")
        
        f.write(f"Precision: {metrics['precision']:.2f}%\n")
        f.write(f"Recall: {metrics['recall']:.2f}%\n")
        f.write(f"Accuracy: {metrics['accuracy']:.2f}%\n")


def write_csv(metrics, output_file):
    """Write CSV summary"""
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['metric', 'value'])
        writer.writerow(['total_reads', metrics['total_reads']])
        writer.writerow(['total_processed', metrics['total_reads']])
        writer.writerow(['correct_assignments', metrics['correct']])
        writer.writerow(['incorrect_assignments', metrics['incorrect']])
        writer.writerow(['unassigned_reads', metrics['unmapped']])
        writer.writerow(['assignment_rate_percent', f"{metrics['assignment_rate']:.4f}"])
        writer.writerow(['precision_percent', f"{metrics['precision']:.4f}"])
        writer.writerow(['recall_percent', f"{metrics['recall']:.4f}"])
        writer.writerow(['accuracy_percent', f"{metrics['accuracy']:.4f}"])


def main():
    if len(sys.argv) < 4:
        print("Usage: calculate_columba_metrics_fast.py <sam_file> <output_report> <output_csv>")
        sys.exit(1)
    
    sam_file = sys.argv[1]
    output_report = sys.argv[2]
    output_csv = sys.argv[3]
    
    print(f"Processing {sam_file}...")
    
    # Parse SAM file
    correct, incorrect, unmapped, total_reads = parse_sam_fast(sam_file)
    
    # Calculate metrics
    assigned = correct + incorrect
    assignment_rate = (assigned / total_reads * 100) if total_reads > 0 else 0
    precision = (correct / assigned * 100) if assigned > 0 else 0
    recall = (correct / total_reads * 100) if total_reads > 0 else 0
    accuracy = recall  # Same as recall for this task
    
    metrics = {
        'total_reads': total_reads,
        'correct': correct,
        'incorrect': incorrect,
        'unmapped': unmapped,
        'assigned': assigned,
        'assignment_rate': assignment_rate,
        'precision': precision,
        'recall': recall,
        'accuracy': accuracy
    }
    
    # Write outputs
    write_report(metrics, output_report)
    write_csv(metrics, output_csv)
    
    # Print summary
    print("\n" + "=" * 80)
    print("COLUMBA METRICS SUMMARY")
    print("=" * 80)
    print(f"Total reads: {total_reads}")
    print(f"Correct: {correct}")
    print(f"Incorrect: {incorrect}")
    print(f"Unmapped: {unmapped}")
    print(f"Precision: {precision:.2f}%")
    print(f"Recall: {recall:.2f}%")
    print("=" * 80)


if __name__ == '__main__':
    main()
