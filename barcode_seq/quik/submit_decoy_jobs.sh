#!/bin/bash
# Submit all QUIK decoy jobs

echo "Submitting QUIK decoy jobs..."

qsub jobs/job_21k_decoy.sh
echo "Submitted 21k decoy job"

qsub jobs/job_42k_decoy.sh
echo "Submitted 42k decoy job"

qsub jobs/job_85k_decoy.sh
echo "Submitted 85k decoy job"

echo "All QUIK decoy jobs submitted!"
