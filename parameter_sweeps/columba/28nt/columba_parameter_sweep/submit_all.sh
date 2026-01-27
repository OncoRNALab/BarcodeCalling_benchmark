#!/bin/bash
# Submit all Columba parameter sweep jobs

echo 'Submitting 5 jobs...'

echo 'Submitting job_I72.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/columba_parameter_sweep/jobs/job_I72.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_I75.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/columba_parameter_sweep/jobs/job_I75.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_I77.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/columba_parameter_sweep/jobs/job_I77.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_I80.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/columba_parameter_sweep/jobs/job_I80.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_I83.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/columba_parameter_sweep/jobs/job_I83.sh
sleep 1  # Avoid overwhelming scheduler

echo 'All jobs submitted!'
echo 'Monitor with: squeue -u $USER'
