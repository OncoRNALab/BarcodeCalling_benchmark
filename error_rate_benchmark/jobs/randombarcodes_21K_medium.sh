#!/bin/bash
#SBATCH -J RA_21K_36nt_medium
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --clusters=joltik,accelgor
#SBATCH --time=08:00:00
#SBATCH --output=error_rate_benchmark/logs/RA_21K_36nt_medium.out
#SBATCH --error=error_rate_benchmark/logs/RA_21K_36nt_medium.err

# Load Nextflow module
ml Nextflow/25.04.8

# Run pipeline from project root directory
nextflow run main.nf \
    -params-file error_rate_benchmark/params/randombarcodes_21K_medium.json \
    -work-dir work_error_rate/randombarcodes/21K_medium \
    -profile slurm
