#!/bin/bash
# Master submission script for 1 million reads benchmark
# This script submits all benchmark jobs for RandomBarcodes, QUIK, and Columba
# across different barcode counts (21K, 42K, 85K)

JOBS_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/1million_reads/jobs"

echo "============================================"
echo "Submitting 1 Million Reads Benchmark Jobs"
echo "============================================"
echo ""

# Submit RandomBarcodes jobs
echo "Submitting RandomBarcodes jobs..."
sbatch "$JOBS_DIR/randombarcodes_21K.sh"
sbatch "$JOBS_DIR/randombarcodes_42K.sh"
sbatch "$JOBS_DIR/randombarcodes_85K.sh"
echo ""

# Submit QUIK jobs
echo "Submitting QUIK jobs..."
sbatch "$JOBS_DIR/quik_21K.sh"
sbatch "$JOBS_DIR/quik_42K.sh"
sbatch "$JOBS_DIR/quik_85K.sh"
echo ""

# Submit Columba jobs
echo "Submitting Columba jobs..."
sbatch "$JOBS_DIR/columba_21K.sh"
sbatch "$JOBS_DIR/columba_42K.sh"
sbatch "$JOBS_DIR/columba_85K.sh"
echo ""

echo "============================================"
echo "All jobs submitted!"
echo "============================================"
echo ""
echo "Check job status with: squeue -u $USER"
echo "View logs in: /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/1million_reads/logs/"
echo ""
