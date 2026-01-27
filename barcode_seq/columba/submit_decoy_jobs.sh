#!/bin/bash
# Submit all Columba decoy jobs

echo "Submitting Columba decoy jobs..."

qsub jobs/job_21k_I76_decoy.sh
echo "Submitted 21k I76 decoy job"

qsub jobs/job_21k_I77_decoy.sh
echo "Submitted 21k I77 decoy job"

qsub jobs/job_42k_I76_decoy.sh
echo "Submitted 42k I76 decoy job"

qsub jobs/job_42k_I77_decoy.sh
echo "Submitted 42k I77 decoy job"

qsub jobs/job_85k_I76_decoy.sh
echo "Submitted 85k I76 decoy job"

qsub jobs/job_85k_I77_decoy.sh
echo "Submitted 85k I77 decoy job"

echo "All Columba decoy jobs submitted!"
