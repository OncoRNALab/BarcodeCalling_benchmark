#!/bin/bash
#SBATCH -J RB32_t100_n9
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=24:00:00
#SBATCH --mem=8G
#SBATCH --gres=gpu:1
#SBATCH --output=/kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/32nt/logs/RB32_t100_n9.out
#SBATCH --error=/kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/32nt/logs/RB32_t100_n9.err

# Load Nextflow module
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_sweep_32nt/randombarcodes/t100_n9"

# Create and move to unique work directory for this job to avoid lock conflicts
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Run pipeline
nextflow run "$PROJECT_DIR/main.nf" \
    -c "$PROJECT_DIR/nextflow.config" \
    -profile slurm \
    -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/32nt/params/params_t100_n9.json \
    -work-dir "$WORK_DIR" \
    -resume

echo "Job completed for ntriage=100, nthresh=9"
