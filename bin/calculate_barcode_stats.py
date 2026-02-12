#!/usr/bin/env python3
"""
Calculate barcode assignment statistics without requiring ground truth.

This script analyzes barcode calling results from FASTQ files and generates
comprehensive statistics useful for quality control of real sequencing data.
"""

import argparse
import sys
import os
import gzip
from collections import defaultdict, Counter
import csv
import json


def open_file(filename):
    """Open regular or gzipped file."""
    if filename.endswith('.gz'):
        return gzip.open(filename, 'rt', encoding='utf-8', errors='replace')
    return open(filename, 'r', encoding='utf-8', errors='replace')


def count_fastq_reads(fastq_file):
    """Count total number of reads in a FASTQ file."""
    read_count = 0
    with open_file(fastq_file) as f:
        for line_num, line in enumerate(f, 1):
            if line_num % 4 == 1:  # Header line
                read_count += 1
    return read_count


def load_barcodes(barcode_file):
    """Load barcodes from file."""
    barcodes = []
    with open(barcode_file, 'r') as f:
        for line in f:
            barcode = line.strip()
            if barcode:
                barcodes.append(barcode)
    return barcodes


def parse_fastq_assignments(fastq_file, barcodes):
    """
    Parse FASTQ file to extract barcode assignments.
    
    Supports multiple header formats:
    - @read_calledidx_<INDEX>_...  (direct index)
    - @read_<N>_<BARCODE>         (barcode sequence)
    """
    import re
    
    barcode_to_idx = {bc: idx for idx, bc in enumerate(barcodes)}
    barcode_to_idx_lower = {bc.lower(): idx for bc, idx in barcode_to_idx.items()}
    
    assignments = []  # List of (read_num, barcode_idx)
    read_counter = 0
    
    with open_file(fastq_file) as f:
        line_num = 0
        for line in f:
            line_num += 1
            if line_num % 4 == 1:  # Header line
                read_counter += 1
                header = line.strip()
                
                # Try format 1: _calledidx_<INDEX>
                calledidx_match = re.search(r'_calledidx_(\d+)', header)
                if calledidx_match:
                    barcode_idx = int(calledidx_match.group(1))
                    assignments.append((read_counter, barcode_idx))
                    continue
                
                # Try format 2: Extract barcode sequence from header
                # Format: @read_<N>_<BARCODE> or similar
                parts = header.split('_')
                for i, part in enumerate(parts):
                    # Check if this part matches a known barcode
                    if part.lower() in barcode_to_idx_lower:
                        barcode_idx = barcode_to_idx_lower[part.lower()]
                        assignments.append((read_counter, barcode_idx))
                        break
    
    return assignments, read_counter


def calculate_statistics(assignments, total_reads, num_barcodes):
    """Calculate comprehensive barcode statistics."""
    
    # Basic counts
    num_assigned = len(assignments)
    num_unassigned = total_reads - num_assigned
    assignment_rate = (num_assigned / total_reads * 100) if total_reads > 0 else 0
    
    # Per-barcode counts
    barcode_counts = Counter(bc_idx for _, bc_idx in assignments)
    
    # Distribution statistics
    counts = list(barcode_counts.values())
    if counts:
        mean_reads_per_bc = sum(counts) / len(counts)
        median_reads_per_bc = sorted(counts)[len(counts) // 2]
        min_reads_per_bc = min(counts)
        max_reads_per_bc = max(counts)
        
        # Coefficient of variation (measure of uniformity)
        import math
        if mean_reads_per_bc > 0:
            std_dev = math.sqrt(sum((x - mean_reads_per_bc) ** 2 for x in counts) / len(counts))
            cv = std_dev / mean_reads_per_bc
        else:
            cv = 0
    else:
        mean_reads_per_bc = 0
        median_reads_per_bc = 0
        min_reads_per_bc = 0
        max_reads_per_bc = 0
        cv = 0
    
    # Barcode coverage
    num_barcodes_detected = len(barcode_counts)
    num_barcodes_zero = num_barcodes - num_barcodes_detected
    barcode_detection_rate = (num_barcodes_detected / num_barcodes * 100) if num_barcodes > 0 else 0
    
    # Singleton barcodes (assigned only once)
    singletons = sum(1 for count in counts if count == 1)
    
    # Low coverage barcodes (< 10 reads)
    low_coverage = sum(1 for count in counts if count < 10)
    
    stats = {
        # Assignment metrics
        'total_reads': total_reads,
        'reads_assigned': num_assigned,
        'reads_unassigned': num_unassigned,
        'assignment_rate_percent': assignment_rate,
        
        # Distribution metrics
        'num_barcodes_in_library': num_barcodes,
        'num_barcodes_detected': num_barcodes_detected,
        'num_barcodes_zero_coverage': num_barcodes_zero,
        'barcode_detection_rate_percent': barcode_detection_rate,
        
        # Read distribution
        'mean_reads_per_barcode': mean_reads_per_bc,
        'median_reads_per_barcode': median_reads_per_bc,
        'min_reads_per_barcode': min_reads_per_bc,
        'max_reads_per_barcode': max_reads_per_bc,
        'coefficient_of_variation': cv,
        
        # Quality flags
        'singleton_barcodes': singletons,
        'low_coverage_barcodes': low_coverage,
    }
    
    return stats, barcode_counts


def write_summary_csv(stats, output_file):
    """Write summary statistics to CSV."""
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['metric', 'value'])
        for key, value in stats.items():
            writer.writerow([key, value])


def write_detailed_report(stats, barcode_counts, num_barcodes, output_file):
    """Write detailed text report."""
    with open(output_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("BARCODE ASSIGNMENT STATISTICS (Real Data - No Ground Truth)\n")
        f.write("="*80 + "\n\n")
        
        f.write("ASSIGNMENT SUMMARY\n")
        f.write("-"*80 + "\n")
        f.write(f"Total reads processed:        {stats['total_reads']:,}\n")
        f.write(f"Reads assigned to barcodes:   {stats['reads_assigned']:,}\n")
        f.write(f"Reads unassigned/rejected:    {stats['reads_unassigned']:,}\n")
        f.write(f"Assignment rate:              {stats['assignment_rate_percent']:.2f}%\n\n")
        
        f.write("BARCODE COVERAGE\n")
        f.write("-"*80 + "\n")
        f.write(f"Total barcodes in library:    {stats['num_barcodes_in_library']:,}\n")
        f.write(f"Barcodes detected (>0 reads): {stats['num_barcodes_detected']:,}\n")
        f.write(f"Barcodes not detected:        {stats['num_barcodes_zero_coverage']:,}\n")
        f.write(f"Detection rate:               {stats['barcode_detection_rate_percent']:.2f}%\n\n")
        
        f.write("READ DISTRIBUTION PER BARCODE\n")
        f.write("-"*80 + "\n")
        f.write(f"Mean reads per barcode:       {stats['mean_reads_per_barcode']:.2f}\n")
        f.write(f"Median reads per barcode:     {stats['median_reads_per_barcode']:.0f}\n")
        f.write(f"Min reads per barcode:        {stats['min_reads_per_barcode']:,}\n")
        f.write(f"Max reads per barcode:        {stats['max_reads_per_barcode']:,}\n")
        f.write(f"Coefficient of variation:     {stats['coefficient_of_variation']:.4f}\n\n")
        
        f.write("QUALITY INDICATORS\n")
        f.write("-"*80 + "\n")
        f.write(f"Singleton barcodes (1 read):  {stats['singleton_barcodes']:,}\n")
        f.write(f"Low coverage barcodes (<10):  {stats['low_coverage_barcodes']:,}\n\n")
        
        # Distribution uniformity interpretation
        cv = stats['coefficient_of_variation']
        f.write("DISTRIBUTION UNIFORMITY ASSESSMENT\n")
        f.write("-"*80 + "\n")
        if cv < 0.3:
            assessment = "EXCELLENT - Very uniform distribution"
        elif cv < 0.5:
            assessment = "GOOD - Reasonably uniform distribution"
        elif cv < 0.8:
            assessment = "FAIR - Moderate variation in coverage"
        else:
            assessment = "POOR - High variation in coverage"
        f.write(f"CV = {cv:.4f}: {assessment}\n\n")
        
        # Top 10 most abundant barcodes
        if barcode_counts:
            f.write("TOP 10 MOST ABUNDANT BARCODES\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Rank':<6} {'Barcode Index':<15} {'Read Count':<15} {'Percentage':<10}\n")
            f.write("-"*80 + "\n")
            
            total_assigned = stats['reads_assigned']
            for rank, (bc_idx, count) in enumerate(barcode_counts.most_common(10), 1):
                percentage = (count / total_assigned * 100) if total_assigned > 0 else 0
                f.write(f"{rank:<6} {bc_idx:<15} {count:<15,} {percentage:<10.2f}%\n")
            f.write("\n")
        
        f.write("="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")


def write_per_barcode_csv(barcode_counts, num_barcodes, output_file):
    """Write per-barcode statistics to CSV."""
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode_index', 'read_count'])
        
        # Write all barcodes (including zero counts)
        for bc_idx in range(num_barcodes):
            count = barcode_counts.get(bc_idx, 0)
            writer.writerow([bc_idx, count])


def main():
    parser = argparse.ArgumentParser(
        description='Calculate barcode assignment statistics without ground truth'
    )
    parser.add_argument('barcode_file', help='File containing barcode sequences')
    parser.add_argument('fastq_r1', help='Filtered R1 FASTQ file with barcode assignments')
    parser.add_argument('output_report', help='Output text report file')
    parser.add_argument('output_summary', help='Output summary CSV file')
    parser.add_argument('output_per_barcode', help='Output per-barcode CSV file')
    parser.add_argument('--original-fastq', help='Original input FASTQ file (for accurate total read count)')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    
    args = parser.parse_args()
    
    # Load barcodes
    if args.verbose:
        print(f"Loading barcodes from {args.barcode_file}...")
    barcodes = load_barcodes(args.barcode_file)
    num_barcodes = len(barcodes)
    if args.verbose:
        print(f"  Loaded {num_barcodes} barcodes")
    
    # Parse FASTQ assignments
    if args.verbose:
        print(f"Parsing barcode assignments from {args.fastq_r1}...")
    assignments, filtered_read_count = parse_fastq_assignments(args.fastq_r1, barcodes)
    
    # Count total reads from original FASTQ if provided, otherwise use filtered count
    if args.original_fastq:
        if args.verbose:
            print(f"Counting total reads from original FASTQ: {args.original_fastq}...")
        total_reads = count_fastq_reads(args.original_fastq)
    else:
        # Fall back to using filtered read count (may give 100% assignment rate)
        total_reads = filtered_read_count
    
    if args.verbose:
        print(f"  Total reads (input): {total_reads}")
        print(f"  Assigned reads (output): {len(assignments)}")
    
    # Calculate statistics
    if args.verbose:
        print("Calculating statistics...")
    stats, barcode_counts = calculate_statistics(assignments, total_reads, num_barcodes)
    
    # Write outputs
    if args.verbose:
        print(f"Writing summary to {args.output_summary}...")
    write_summary_csv(stats, args.output_summary)
    
    if args.verbose:
        print(f"Writing detailed report to {args.output_report}...")
    write_detailed_report(stats, barcode_counts, num_barcodes, args.output_report)
    
    if args.verbose:
        print(f"Writing per-barcode statistics to {args.output_per_barcode}...")
    write_per_barcode_csv(barcode_counts, num_barcodes, args.output_per_barcode)
    
    if args.verbose:
        print("Done!")
    
    # Print key metrics to stdout
    print(f"\nBarcode Assignment Statistics:")
    print(f"  Total reads: {stats['total_reads']:,}")
    print(f"  Assignment rate: {stats['assignment_rate_percent']:.2f}%")
    print(f"  Barcodes detected: {stats['num_barcodes_detected']}/{stats['num_barcodes_in_library']}")
    print(f"  Mean reads/barcode: {stats['mean_reads_per_barcode']:.2f}")
    print(f"  CV (uniformity): {stats['coefficient_of_variation']:.4f}")


if __name__ == '__main__':
    main()
