#!/bin/bash
#SBATCH -J RB_t1000_n8
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=24:00:00
#SBATCH --mem=8G
#SBATCH --output=/kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/parameter_sweep/logs/RB_t1000_n8.out
#SBATCH --error=/kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/parameter_sweep/logs/RB_t1000_n8.err

# Environment setup
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_sweep/t1000_n8"

# Create and move to unique work directory for this job to avoid lock conflicts
# This ensures each run has its own .nextflow metadata folder
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Run pipeline
nextflow run "$PROJECT_DIR/main.nf" \
    -c "$PROJECT_DIR/nextflow.config" \
    -profile slurm \
    -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/parameter_sweep/params/params_t1000_n8.json \
    -work-dir "$WORK_DIR" \

echo "Job completed for ntriage=1000, nthresh=8"
