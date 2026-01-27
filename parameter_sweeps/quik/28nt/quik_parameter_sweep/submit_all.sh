#!/bin/bash
# Submit all QUIK parameter sweep jobs

echo 'Submitting 18 jobs...'

echo 'Submitting job_47mer_r10.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_47mer_r10.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_47mer_r5.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_47mer_r5.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_47mer_r6.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_47mer_r6.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_47mer_r7.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_47mer_r7.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_47mer_r8.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_47mer_r8.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_47mer_r9.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_47mer_r9.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_4mer_r10.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_4mer_r10.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_4mer_r5.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_4mer_r5.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_4mer_r6.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_4mer_r6.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_4mer_r7.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_4mer_r7.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_4mer_r8.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_4mer_r8.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_4mer_r9.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_4mer_r9.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_77mer_r10.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_77mer_r10.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_77mer_r5.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_77mer_r5.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_77mer_r6.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_77mer_r6.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_77mer_r7.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_77mer_r7.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_77mer_r8.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_77mer_r8.sh
sleep 1  # Avoid overwhelming scheduler

echo 'Submitting job_77mer_r9.sh'
sbatch /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/jobs/job_77mer_r9.sh
sleep 1  # Avoid overwhelming scheduler

echo 'All jobs submitted!'
echo 'Monitor with: squeue -u $USER'
