#!/bin/bash
# Submit all Columba real data jobs

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Submitting Columba jobs for real sequencing data..."

# Submit 21k jobs (both thresholds)
JOB1=$(sbatch "$SCRIPT_DIR/jobs/job_21k_I76.sh" | awk '{print $4}')
echo "Submitted 21k I76 job: $JOB1"

JOB2=$(sbatch "$SCRIPT_DIR/jobs/job_21k_I77.sh" | awk '{print $4}')
echo "Submitted 21k I77 job: $JOB2"

# Submit 42k jobs (both thresholds)
JOB3=$(sbatch "$SCRIPT_DIR/jobs/job_42k_I76.sh" | awk '{print $4}')
echo "Submitted 42k I76 job: $JOB3"

JOB4=$(sbatch "$SCRIPT_DIR/jobs/job_42k_I77.sh" | awk '{print $4}')
echo "Submitted 42k I77 job: $JOB4"

# Submit 85k jobs (both thresholds)
JOB5=$(sbatch "$SCRIPT_DIR/jobs/job_85k_I76.sh" | awk '{print $4}')
echo "Submitted 85k I76 job: $JOB5"

JOB6=$(sbatch "$SCRIPT_DIR/jobs/job_85k_I77.sh" | awk '{print $4}')
echo "Submitted 85k I77 job: $JOB6"

echo ""
echo "All Columba jobs submitted!"
echo "Job IDs: $JOB1, $JOB2, $JOB3, $JOB4, $JOB5, $JOB6"
echo ""
echo "Monitor with: squeue -u $USER"
echo "Check logs in: $SCRIPT_DIR/logs/"
