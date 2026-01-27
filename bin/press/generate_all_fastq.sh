#!/bin/bash
# Batch script to generate FASTQ pairs for all simulations
# Usage: ./generate_all_fastq.sh

echo "========================================================================"
echo "FASTQ PAIR GENERATION FOR ALL SIMULATIONS"
echo "========================================================================"
echo ""

# Load required module
module load PyTorch/2.6.0-foss-2024a

SCRIPT="/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/scripts/3_Generate_FASTQ_pairs.py"
CONFIG_DIR="/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/config_files"

# Counter
total=0
success=0
failed=0

# Process all simulation configs
for config in ${CONFIG_DIR}/config_benchmark_*_sim_*.yaml; do
    total=$((total + 1))
    config_name=$(basename "$config")
    
    echo "[$total] Processing: $config_name"
    
    if python "$SCRIPT" --config "$config" --min-qual 20 --max-qual 40; then
        success=$((success + 1))
        echo "  ✓ Success"
    else
        failed=$((failed + 1))
        echo "  ✗ Failed"
    fi
    
    echo ""
done

echo "========================================================================"
echo "SUMMARY"
echo "========================================================================"
echo "Total configs processed: $total"
echo "Successful:              $success"
echo "Failed:                  $failed"
echo "========================================================================"
