#!/bin/bash
#SBATCH -J RA_85K_36nt_high
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --clusters=joltik,accelgor
#SBATCH --time=08:00:00
#SBATCH --output=error_rate_benchmark/logs/RA_85K_36nt_high.out
#SBATCH --error=error_rate_benchmark/logs/RA_85K_36nt_high.err

# Load Nextflow module
ml Nextflow/25.04.8

# Run pipeline from project root directory
nextflow run main.nf \
    -params-file error_rate_benchmark/params/randombarcodes_85K_high.json \
    -work-dir work_error_rate/randombarcodes/85K_high \
    -profile slurm
