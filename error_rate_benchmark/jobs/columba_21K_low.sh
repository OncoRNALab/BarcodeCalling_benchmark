#!/bin/bash
#SBATCH -J CO_21K_36nt_low
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=error_rate_benchmark/logs/CO_21K_36nt_low.out
#SBATCH --error=error_rate_benchmark/logs/CO_21K_36nt_low.err

# Load Nextflow module
ml Nextflow/25.04.8

# Set Apptainer/Singularity cache directories to scratch (avoid home disk quota)
SCRATCH_DIR="${VSC_SCRATCH_VO_USER:-${VSC_SCRATCH:-$HOME/scratch}}"
export APPTAINER_TMPDIR="$SCRATCH_DIR/.apptainer/tmp"
export APPTAINER_CACHEDIR="$SCRATCH_DIR/.apptainer/cache"
export SINGULARITY_CACHEDIR="$SCRATCH_DIR/singularity"
export NXF_SINGULARITY_CACHEDIR="$SCRATCH_DIR/.apptainer/cache"

# Create cache directories if they don't exist
mkdir -p "$APPTAINER_TMPDIR" "$APPTAINER_CACHEDIR" "$SINGULARITY_CACHEDIR"

# Run pipeline from project root directory
nextflow run main.nf \
    -params-file error_rate_benchmark/params/columba_21K_low.json \
    -work-dir work_error_rate/columba/21K_low \
    -profile slurm

nextflow run main.nf \
    -params-file error_rate_benchmark/params/columba_21K_low.json \
    -work-dir work_error_rate/columba/21K_low \
    -profile local,singularity
