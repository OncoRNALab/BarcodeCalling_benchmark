#!/bin/bash
#SBATCH -J RB_t100_2gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --output=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/runtime_benchmarks/randombarcodes/logs/RB_t100_2gpu.out
#SBATCH --error=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/runtime_benchmarks/randombarcodes/logs/RB_t100_2gpu.err

# Environment setup
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_runtime_rb/t100_2gpu"
PARAMS_FILE="${PROJECT_DIR}/runtime_benchmarks/randombarcodes/params/params_t100_2gpu.json"

echo "========================================="
echo "RandomBarcodes Runtime Benchmark"
echo "Config: ntriage=100, gpus=2"
echo "Started: $(date)"
echo "========================================="

# Create and move to unique work directory
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Run pipeline
nextflow run "$PROJECT_DIR/main.nf" \
    -c "$PROJECT_DIR/nextflow.config" \
    -profile slurm \
    -params-file "$PARAMS_FILE" \
    -work-dir "$WORK_DIR" \
    -resume

EXIT_CODE=$?

echo "========================================="
echo "Finished: $(date)"
echo "Exit code: ${EXIT_CODE}"
echo "========================================="

exit $EXIT_CODE
