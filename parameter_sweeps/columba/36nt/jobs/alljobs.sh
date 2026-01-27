#!/bin/bash
#SBATCH -J Columba36_sweep
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=08:00:00
#SBATCH --mem=64G
#SBATCH --clusters=accelgor,joltik
#SBATCH --output=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/36nt/logs/Columba36_all.out
#SBATCH --error=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/36nt/logs/Columba36_all.err

# Environment setup
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
PARAMS_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/36nt/params"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_sweep_36nt/columba/all"

# Create and change to work directory
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "======================================================================"
echo "Starting Columba 36nt Parameter Sweep - All configurations"
echo "======================================================================"
echo "Start time: $(date)"
echo ""

# Counter for completed jobs
completed=0
total=5

# Run all identity thresholds
echo ">>> Running Columba with different identity thresholds..."
for identity in 72 75 77 80 83; do
    echo "  [$(date +%H:%M:%S)] Running I${identity}..."
    nextflow run "$PROJECT_DIR/main.nf" \
        -c "$PROJECT_DIR/nextflow.config" \
        -profile singularity,local \
        -params-file "$PARAMS_DIR/params_I${identity}.json" \
        -work-dir "$WORK_DIR/I${identity}"
    
    if [ $? -eq 0 ]; then
        ((completed++))
        echo "  ✓ I${identity} completed successfully ($completed/$total)"
    else
        echo "  ✗ I${identity} failed!"
    fi
    echo ""
done

echo "======================================================================"
echo "Columba 36nt Parameter Sweep Completed"
echo "======================================================================"
echo "End time: $(date)"
echo "Completed: $completed / $total configurations"
echo "======================================================================"
