#!/bin/bash
#SBATCH -J Columba_1cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=48:00:00
#SBATCH --mem=32G
#SBATCH --output=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/runtime_benchmarks/columba/logs/Columba_1cpu.out
#SBATCH --error=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/runtime_benchmarks/columba/logs/Columba_1cpu.err

# Environment setup
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_runtime_columba/1cpu"
PARAMS_FILE="${PROJECT_DIR}/runtime_benchmarks/columba/params/params_1cpu.json"

echo "========================================="
echo "Columba Runtime Benchmark"
echo "Config: identity_threshold=77, cpus=1"
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
