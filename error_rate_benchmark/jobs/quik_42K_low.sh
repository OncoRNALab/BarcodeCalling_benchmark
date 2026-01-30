#!/bin/bash
#SBATCH -J QU_42K_36nt_low
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --clusters=joltik,accelgor
#SBATCH --time=08:00:00
#SBATCH --output=error_rate_benchmark/logs/QU_42K_36nt_low.out
#SBATCH --error=error_rate_benchmark/logs/QU_42K_36nt_low.err

# Load Nextflow module
ml Nextflow/25.04.8

# Run pipeline from project root directory
nextflow run main.nf \
    -params-file error_rate_benchmark/params/quik_42K_low.json \
    -work-dir work_error_rate/quik/42K_low \
    -profile slurm
