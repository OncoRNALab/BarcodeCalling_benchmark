#!/usr/bin/env python3
"""
Test script for calculate_barcode_stats.py

Creates minimal test data and runs the statistics calculation.
"""

import os
import sys
import tempfile
import subprocess

def create_test_barcode_file(path, num_barcodes=100):
    """Create a test barcode file."""
    with open(path, 'w') as f:
        for i in range(num_barcodes):
            # Create simple barcodes
            barcode = f"ACGT{'A' * (32 - len(str(i)))}{i:04d}"[:36]
            f.write(f"{barcode}\n")

def create_test_fastq(path, assignments):
    """Create a test FASTQ file with barcode assignments in headers."""
    with open(path, 'w') as f:
        for read_num, bc_idx in enumerate(assignments, 1):
            # Use the new _calledidx_ format
            f.write(f"@read_calledidx_{bc_idx}_{read_num}\n")
            f.write("ACGTACGTACGTACGTACGTACGTACGTACGTACGT\n")
            f.write("+\n")
            f.write("IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII\n")

def main():
    """Run test."""
    print("Testing calculate_barcode_stats.py...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        barcode_file = os.path.join(tmpdir, "barcodes.txt")
        fastq_file = os.path.join(tmpdir, "test_R1.fastq")
        report_file = os.path.join(tmpdir, "report.txt")
        summary_file = os.path.join(tmpdir, "summary.csv")
        per_barcode_file = os.path.join(tmpdir, "per_barcode.csv")
        
        num_barcodes = 100
        
        print(f"Creating test barcode file with {num_barcodes} barcodes...")
        create_test_barcode_file(barcode_file, num_barcodes)
        
        # Create test assignments
        # 500 reads: 400 assigned, 100 will be "unassigned" (not in FASTQ)
        assignments = []
        for i in range(400):
            bc_idx = i % 80  # Use 80 out of 100 barcodes
            assignments.append(bc_idx)
        
        print(f"Creating test FASTQ with {len(assignments)} reads...")
        create_test_fastq(fastq_file, assignments)
        
        # Run the script
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "bin",
            "calculate_barcode_stats.py"
        )
        
        print(f"Running {script_path}...")
        cmd = [
            "python3",
            script_path,
            barcode_file,
            fastq_file,
            report_file,
            summary_file,
            per_barcode_file,
            "--verbose"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("ERROR: Script failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            sys.exit(1)
        
        print("\nScript output:")
        print(result.stdout)
        
        # Verify outputs exist
        print("\nVerifying outputs...")
        for filename, path in [
            ("Report", report_file),
            ("Summary CSV", summary_file),
            ("Per-barcode CSV", per_barcode_file)
        ]:
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"✓ {filename}: {path} ({size} bytes)")
            else:
                print(f"✗ {filename} not found: {path}")
                sys.exit(1)
        
        # Display summary
        print("\nSummary CSV contents:")
        with open(summary_file) as f:
            print(f.read())
        
        print("\n" + "="*80)
        print("TEST PASSED!")
        print("="*80)

if __name__ == '__main__':
    main()
