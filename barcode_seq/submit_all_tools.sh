#!/bin/bash
# Submit ALL real sequencing data jobs for all tools

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=========================================="
echo "Submitting ALL real sequencing data jobs"
echo "=========================================="
echo ""

# Submit RandomBarcodes jobs
echo "1. Submitting RandomBarcodes jobs..."
cd "$BASE_DIR/randombarcodes"
bash submit_all.sh
echo ""

# Submit QUIK jobs
echo "2. Submitting QUIK jobs..."
cd "$BASE_DIR/quik"
bash submit_all.sh
echo ""

# Submit Columba jobs
echo "3. Submitting Columba jobs..."
cd "$BASE_DIR/columba"
bash submit_all.sh
echo ""

echo "=========================================="
echo "All jobs submitted successfully!"
echo "=========================================="
echo ""
echo "Total jobs: 12 (3 RandomBarcodes + 3 QUIK + 6 Columba)"
echo ""
echo "Monitor all jobs: squeue -u $USER"
echo "Cancel all jobs: scancel -u $USER"
