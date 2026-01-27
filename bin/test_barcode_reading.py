#!/usr/bin/env python
"""
Test script to verify barcode file format auto-detection
"""
import csv
import sys

def read_barcodes(filename):
    """Read barcodes from file (auto-detect CSV or plain text format)"""
    codes = []
    with open(filename, 'r') as barcode_file:
        first_line = barcode_file.readline().strip()
        barcode_file.seek(0)  # Reset to beginning
        
        # Detect format: if first line is "cell" or contains commas, treat as CSV
        if first_line.lower() == 'cell' or ',' in first_line:
            print(f"📋 Detected format: CSV")
            # CSV format with header
            reader = csv.DictReader(barcode_file)
            for row in reader:
                # Extract barcode from 'cell' column and convert to lowercase
                codes.append(row['cell'].lower() + '\n')
        else:
            print(f"📄 Detected format: Plain text")
            # Plain text format: one barcode per line
            for line in barcode_file:
                barcode = line.strip().lower()
                if barcode:  # Skip empty lines
                    codes.append(barcode + '\n')
    
    return codes

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_barcode_reading.py <barcode_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    print(f"Testing barcode file: {filename}")
    print("=" * 60)
    
    try:
        codes = read_barcodes(filename)
        print(f"✅ Successfully read {len(codes)} barcodes")
        print(f"\nFirst 5 barcodes:")
        for i, code in enumerate(codes[:5]):
            print(f"  {i+1}. {code.strip()} (length: {len(code.strip())})")
        print(f"\nLast 3 barcodes:")
        for i, code in enumerate(codes[-3:]):
            print(f"  {len(codes)-3+i+1}. {code.strip()} (length: {len(code.strip())})")
    except Exception as e:
        print(f"❌ Error reading barcodes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

