#!/bin/bash
# Master submission script for barcode generation jobs
# This script submits all barcode generation jobs to the cluster

echo "=========================================="
echo "Submitting Barcode Generation Jobs"
echo "=========================================="
echo ""

JOB_DIR="/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/jobs"

cd $JOB_DIR

# Submit all barcode generation jobs
for f in job_bargen_*.pbs; do
    echo "Submitting: $f"
    qsub $f
done

echo ""
echo "=========================================="
echo "All barcode generation jobs submitted!"
echo "=========================================="
echo ""
echo "Monitor job status with: qstat -u \$USER"
echo "After all jobs complete, run: ./submit_simulation_jobs.sh"
