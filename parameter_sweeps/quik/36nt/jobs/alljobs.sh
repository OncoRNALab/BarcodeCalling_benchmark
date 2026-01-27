#!/bin/bash
#SBATCH -J QUIK36_sweep
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --clusters=accelgor,joltik
#SBATCH --output=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/quik/36nt/logs/QUIK36_all.out
#SBATCH --error=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/quik/36nt/logs/QUIK36_all.err

# Environment setup
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
PARAMS_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/quik/36nt/params"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_sweep_36nt/quik/all"

# Create and change to work directory
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "======================================================================"
echo "Starting QUIK 36nt Parameter Sweep - All configurations in one job"
echo "======================================================================"
echo "Start time: $(date)"
echo ""

# Counter for completed jobs
completed=0
total=18

# 4mer strategy (6 rejection thresholds)
echo ">>> Running 4mer strategy (6 configurations)..."
for r in 5 6 7 8 9 10; do
    echo "  [$(date +%H:%M:%S)] Running 4mer r=${r}..."
    nextflow run "$PROJECT_DIR/main.nf" \
        -c "$PROJECT_DIR/nextflow.config" \
        -profile singularity,local \
        -params-file "$PARAMS_DIR/params_4mer_r${r}.json" \
        -work-dir "$WORK_DIR/4mer_r${r}"
    
    if [ $? -eq 0 ]; then
        ((completed++))
        echo "  ✓ 4mer r=${r} completed successfully ($completed/$total)"
    else
        echo "  ✗ 4mer r=${r} failed!"
    fi
    echo ""
done

# 47mer strategy (6 rejection thresholds)
echo ">>> Running 47mer strategy (6 configurations)..."
for r in 5 6 7 8 9 10; do
    echo "  [$(date +%H:%M:%S)] Running 47mer r=${r}..."
    nextflow run "$PROJECT_DIR/main.nf" \
        -c "$PROJECT_DIR/nextflow.config" \
        -profile singularity,local \
        -params-file "$PARAMS_DIR/params_47mer_r${r}.json" \
        -work-dir "$WORK_DIR/47mer_r${r}"
    
    if [ $? -eq 0 ]; then
        ((completed++))
        echo "  ✓ 47mer r=${r} completed successfully ($completed/$total)"
    else
        echo "  ✗ 47mer r=${r} failed!"
    fi
    echo ""
done

# 77mer strategy (6 rejection thresholds)
echo ">>> Running 77mer strategy (6 configurations)..."
for r in 5 6 7 8 9 10; do
    echo "  [$(date +%H:%M:%S)] Running 77mer r=${r}..."
    nextflow run "$PROJECT_DIR/main.nf" \
        -c "$PROJECT_DIR/nextflow.config" \
        -profile singularity,local \
        -params-file "$PARAMS_DIR/params_77mer_r${r}.json" \
        -work-dir "$WORK_DIR/77mer_r${r}"
    
    if [ $? -eq 0 ]; then
        ((completed++))
        echo "  ✓ 77mer r=${r} completed successfully ($completed/$total)"
    else
        echo "  ✗ 77mer r=${r} failed!"
    fi
    echo ""
done

echo "======================================================================"
echo "QUIK 36nt Parameter Sweep Completed"
echo "======================================================================"
echo "End time: $(date)"
echo "Completed: $completed / $total configurations"
echo "======================================================================"
