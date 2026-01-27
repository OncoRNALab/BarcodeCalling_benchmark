#!/bin/bash
#SBATCH -J CB_85K_36nt_high
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --output=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/error_rate_benchmark/logs/CB_85K_36nt_high.out
#SBATCH --error=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/error_rate_benchmark/logs/CB_85K_36nt_high.err

# Load Nextflow module
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_error_rate/columba/85K_high"

# Create and move to unique work directory for this job to avoid lock conflicts
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Run pipeline
nextflow run "$PROJECT_DIR/main.nf" \
    -c "$PROJECT_DIR/nextflow.config" \
    -profile slurm \
    -params-file /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/error_rate_benchmark/params/columba_85K_high.json \
    -work-dir "$WORK_DIR" \
    -resume

echo "Job completed for COLUMBA - 85K 36nt high error"
