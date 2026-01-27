#!/bin/bash
#SBATCH -J CB_21K_1M
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=12:00:00
#SBATCH --mem=64G
#SBATCH --output=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/1million_reads/logs/CB_21K_1M.out
#SBATCH --error=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/1million_reads/logs/CB_21K_1M.err

# Load Nextflow module
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_1million_reads/columba/21K"

# Create and move to unique work directory for this job to avoid lock conflicts
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Run pipeline
nextflow run "$PROJECT_DIR/main.nf" \
    -c "$PROJECT_DIR/nextflow.config" \
    -profile slurm \
    -params-file /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/1million_reads/params/columba_21K.json \
    -work-dir "$WORK_DIR" \
    -resume

echo "Job completed for COLUMBA - 21K 36nt 1M reads"
