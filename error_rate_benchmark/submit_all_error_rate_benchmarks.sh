#!/bin/bash
# Submit all error-rate benchmark jobs

cd error_rate_benchmark/jobs

for job in *.sh; do
    echo "Submitting $job..."
    sbatch "$job"
done

echo "All error-rate benchmark jobs submitted."
