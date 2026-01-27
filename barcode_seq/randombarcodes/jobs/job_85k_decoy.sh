#!/bin/bash
#SBATCH -J RB_decoy_85k
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --output=/kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/barcode_seq/randombarcodes/logs/RB_decoy_85k.out
#SBATCH --error=/kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/barcode_seq/randombarcodes/logs/RB_decoy_85k.err

# Load Nextflow module
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_realdata/randombarcodes/85k_decoy"

# Create and move to unique work directory for this job to avoid lock conflicts
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Run pipeline
nextflow run "$PROJECT_DIR/main.nf" \
    -c "$PROJECT_DIR/nextflow.config" \
    -profile slurm \
    -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/barcode_seq/randombarcodes/params/params_85k_decoy.json \
    -work-dir "$WORK_DIR" \
    -resume

echo "Job completed for RandomBarcodes on 85k decoy data"
