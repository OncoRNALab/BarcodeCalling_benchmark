#!/bin/bash
#SBATCH -J RB36_sweep
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=06:00:00
#SBATCH --mem=32G
#SBATCH --clusters=accelgor,joltik
#SBATCH --output=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/36nt/logs/RB36_all.out
#SBATCH --error=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/36nt/logs/RB36_all.err

# Environment setup
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
PARAMS_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/36nt/params"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_sweep_36nt/randombarcodes/all"

# Create and change to work directory
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "======================================================================"
echo "Starting RandomBarcodes 36nt Parameter Sweep - All configurations"
echo "======================================================================"
echo "Start time: $(date)"
echo ""

# Counter for completed jobs
completed=0
total=30

# Run all combinations of ntriage and nthresh
for ntriage in 100 1000 2000 5000 10000; do
    echo ">>> Running ntriage=${ntriage} (6 configurations)..."
    for nthresh in 5 6 7 8 9 10; do
        echo "  [$(date +%H:%M:%S)] Running t${ntriage}_n${nthresh}..."
        nextflow run "$PROJECT_DIR/main.nf" \
            -c "$PROJECT_DIR/nextflow.config" \
            -profile singularity,local \
            -params-file "$PARAMS_DIR/params_t${ntriage}_n${nthresh}.json" \
            -work-dir "$WORK_DIR/t${ntriage}_n${nthresh}"
        
        if [ $? -eq 0 ]; then
            ((completed++))
            echo "  ✓ t${ntriage}_n${nthresh} completed successfully ($completed/$total)"
        else
            echo "  ✗ t${ntriage}_n${nthresh} failed!"
        fi
        echo ""
    done
done

echo "======================================================================"
echo "RandomBarcodes 36nt Parameter Sweep Completed"
echo "======================================================================"
echo "End time: $(date)"
echo "Completed: $completed / $total configurations"
echo "======================================================================"
