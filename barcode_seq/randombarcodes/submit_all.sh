#!/bin/bash
# Submit all RandomBarcodes real data jobs

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Submitting RandomBarcodes jobs for real sequencing data..."

# Submit 21k job
JOB1=$(sbatch "$SCRIPT_DIR/jobs/job_21k.sh" | awk '{print $4}')
echo "Submitted 21k job: $JOB1"

# Submit 42k job
JOB2=$(sbatch "$SCRIPT_DIR/jobs/job_42k.sh" | awk '{print $4}')
echo "Submitted 42k job: $JOB2"

# Submit 85k job
JOB3=$(sbatch "$SCRIPT_DIR/jobs/job_85k.sh" | awk '{print $4}')
echo "Submitted 85k job: $JOB3"

echo ""
echo "All RandomBarcodes jobs submitted!"
echo "Job IDs: $JOB1, $JOB2, $JOB3"
echo ""
echo "Monitor with: squeue -u $USER"
echo "Check logs in: $SCRIPT_DIR/logs/"
