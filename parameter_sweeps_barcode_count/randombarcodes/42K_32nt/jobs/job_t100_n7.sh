#!/bin/bash
#SBATCH -J RB_42K_32nt_n7
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=04:00:00
#SBATCH --mem=8G
#SBATCH --output=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/randombarcodes/42K_32nt/logs/RB_42K_32nt_n7.out
#SBATCH --error=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/randombarcodes/42K_32nt/logs/RB_42K_32nt_n7.err

# Load Nextflow module
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_barcode_count/randombarcodes/42K_32nt/t100_n7"

# Create and move to unique work directory for this job to avoid lock conflicts
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Run pipeline
nextflow run "$PROJECT_DIR/main.nf" \
    -c "$PROJECT_DIR/nextflow.config" \
    -profile slurm \
    -params-file /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/randombarcodes/42K_32nt/params/params_t100_n7.json \
    -work-dir "$WORK_DIR" \
    -resume

echo "Job completed for RandomBarcodes - 42K 32nt threshold=7"
