#!/bin/bash
# Master submission script for read simulation jobs
# This script submits all simulation jobs to the cluster
# IMPORTANT: Only run this after all barcode generation jobs have completed!

echo "=========================================="
echo "Submitting Read Simulation Jobs"
echo "=========================================="
echo ""

JOB_DIR="/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/jobs"

cd $JOB_DIR

# Submit all simulation jobs
for f in job_simgen_*.pbs; do
    echo "Submitting: $f"
    qsub $f
done

echo ""
echo "=========================================="
echo "All simulation jobs submitted!"
echo "=========================================="
echo ""
echo "Monitor job status with: qstat -u \$USER"
