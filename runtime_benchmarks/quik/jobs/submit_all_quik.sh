#!/bin/bash
#SBATCH -J QUIK_runtime_bench
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=08:00:00
#SBATCH --mem=32G
#SBATCH --output=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/runtime_benchmarks/quik/logs/quik_runtime_bench.out
#SBATCH --error=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/runtime_benchmarks/quik/logs/quik_runtime_bench.err

# Environment setup
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
BASE_WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_runtime_quik"

echo "========================================="
echo "QUIK Runtime Benchmarking - All Configs"
echo "Started: $(date)"
echo "========================================="

# Array of parameter files
PARAMS=(
    "params_4mer_1gpu.json"
    "params_4mer_2gpu.json"
    "params_4mer_4gpu.json"
    "params_4_7mer_1gpu.json"
    "params_4_7mer_2gpu.json"
    "params_4_7mer_4gpu.json"
)

# Loop through each parameter file
for PARAM_FILE in "${PARAMS[@]}"; do
    CONFIG_NAME="${PARAM_FILE%.json}"
    WORK_DIR="${BASE_WORK_DIR}/${CONFIG_NAME}"
    PARAMS_PATH="${PROJECT_DIR}/runtime_benchmarks/quik/params/${PARAM_FILE}"
    
    echo ""
    echo "========================================="
    echo "Running: ${CONFIG_NAME}"
    echo "Param file: ${PARAM_FILE}"
    echo "Work dir: ${WORK_DIR}"
    echo "Started: $(date)"
    echo "========================================="
    
    # Create and move to unique work directory
    mkdir -p "$WORK_DIR"
    cd "$WORK_DIR"
    
    # Run pipeline
    nextflow run "$PROJECT_DIR/main.nf" \
        -c "$PROJECT_DIR/nextflow.config" \
        -profile slurm \
        -params-file "$PARAMS_PATH" \
        -work-dir "$WORK_DIR" \
        -resume
    
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✓ ${CONFIG_NAME} completed successfully"
    else
        echo "✗ ${CONFIG_NAME} failed with exit code ${EXIT_CODE}"
    fi
    
    echo "Finished: $(date)"
    echo "========================================="
done

echo ""
echo "========================================="
echo "All QUIK runtime benchmarks completed"
echo "Finished: $(date)"
echo "========================================="
