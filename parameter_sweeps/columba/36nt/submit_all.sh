#!/bin/bash
# Submit all Columba 36nt parameter sweep jobs

echo 'Submitting 5 jobs...'

for job_file in $(ls -v /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/36nt/jobs/job_*.sh); do
    echo "Submitting $(basename "$job_file")"
    sbatch "$job_file"
    sleep 1  # Avoid overwhelming scheduler
done

echo 'All jobs submitted!'
echo 'Monitor with: squeue -u $USER'
