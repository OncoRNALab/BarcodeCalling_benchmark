#!/bin/bash
#SBATCH -J CO_85K_36nt_low
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=error_rate_benchmark/logs/CO_85K_36nt_low.out
#SBATCH --error=error_rate_benchmark/logs/CO_85K_36nt_low.err

# Load Nextflow module
ml Nextflow/25.04.8

# Run pipeline from project root directory
nextflow run main.nf \
    -params-file error_rate_benchmark/params/columba_85K_low.json \
    -work-dir work_error_rate/columba/85K_low \
    -profile slurm
