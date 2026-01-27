#!/bin/bash
# Master submission script for error rate benchmark with MODIFIED parameters
# This script submits all 27 modified benchmark jobs

JOBS_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/error_rate_benchmark/jobs_modified"

echo "============================================"
echo "Submitting Modified Error Rate Benchmark Jobs"
echo "============================================"
echo ""
echo "Modified Parameters:"
echo "- RandomBarcodes: nthresh = 8 (was 9)"
echo "- QUIK: rejection_threshold = 7 (was 8)"
echo "- Columba: identity_threshold = 83 (was 80)"
echo ""
echo "Total jobs to submit: 27"
echo ""

# Submit RandomBarcodes jobs
echo "Submitting RandomBarcodes jobs..."
for bc in 21K 42K 85K; do
    for err in low medium high; do
        sbatch "$JOBS_DIR/randombarcodes_${bc}_${err}.sh"
    done
done
echo ""

# Submit QUIK jobs
echo "Submitting QUIK jobs..."
for bc in 21K 42K 85K; do
    for err in low medium high; do
        sbatch "$JOBS_DIR/quik_${bc}_${err}.sh"
    done
done
echo ""

# Submit Columba jobs
echo "Submitting Columba jobs..."
for bc in 21K 42K 85K; do
    for err in low medium high; do
        sbatch "$JOBS_DIR/columba_${bc}_${err}.sh"
    done
done
echo ""

echo "============================================"
echo "All 27 modified jobs submitted!"
echo "============================================"
echo ""
echo "Check job status with: squeue -u $USER"
echo "View logs in: error_rate_benchmark/logs_modified/"
echo "Results will be saved to: error_rate_benchmark/results_modified/"
echo ""
