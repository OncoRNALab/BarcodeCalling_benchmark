#!/bin/bash
#SBATCH -J CO_21K_36nt_high
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=error_rate_benchmark/logs/CO_21K_36nt_high.out
#SBATCH --error=error_rate_benchmark/logs/CO_21K_36nt_high.err

# Load Nextflow module
ml Nextflow/25.04.8

# Run pipeline from project root directory
nextflow run main.nf \
    -params-file error_rate_benchmark/params/columba_21K_high.json \
    -work-dir work_error_rate/columba/21K_high \
    -profile slurm
