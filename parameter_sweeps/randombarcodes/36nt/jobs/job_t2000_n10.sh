#!/bin/bash
#SBATCH -J RB36_t2000_n10
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=24:00:00
#SBATCH --mem=8G
#SBATCH --output=/kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/36nt/logs/RB36_t2000_n10.out
#SBATCH --error=/kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/36nt/logs/RB36_t2000_n10.err

# Load Nextflow module
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_sweep_36nt/randombarcodes/t2000_n10"

# Create and move to unique work directory for this job to avoid lock conflicts
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Run pipeline
nextflow run "$PROJECT_DIR/main.nf" \
    -c "$PROJECT_DIR/nextflow.config" \
    -profile slurm \
    -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/36nt/params/params_t2000_n10.json \
    -work-dir "$WORK_DIR" \
    -resume

echo "Job completed for ntriage=2000, nthresh=10"
