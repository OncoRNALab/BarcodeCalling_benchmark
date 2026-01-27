#!/bin/bash
#
# Run metric recomputation for all RandomBarcodes and QUIK outputs
# This script processes 28nt dataset results for both tools
#

set -e  # Exit on error

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RECOMPUTE_SCRIPT="${SCRIPT_DIR}/recompute_metrics_simple.py"

# 28nt dataset files
BARCODE_FILE_28NT="/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_28nt/barcodes_21K_28_subset1"
ANSWERS_FILE_28NT="/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_28nt/answers_21K_28_low"
TOTAL_READS=200000

# Results directories
RANDOMBARCODES_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/randombarcodes_sweep"
QUIK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/quik_sweep"

# Output files
RANDOMBARCODES_OUTPUT="${SCRIPT_DIR}/randombarcodes_28nt_corrected_metrics.csv"
QUIK_OUTPUT="${SCRIPT_DIR}/quik_28nt_corrected_metrics.csv"
COMBINED_OUTPUT="${SCRIPT_DIR}/all_tools_28nt_corrected_metrics.csv"

# Check if script exists
if [[ ! -f "$RECOMPUTE_SCRIPT" ]]; then
    echo "ERROR: Recompute script not found: $RECOMPUTE_SCRIPT"
    exit 1
fi

echo "================================================================================"
echo "Recomputing Metrics for All Tools - 28nt Dataset"
echo "================================================================================"
echo ""
echo "Configuration:"
echo "  Barcode file:  $BARCODE_FILE_28NT"
echo "  Answers file:  $ANSWERS_FILE_28NT"
echo "  Total reads:   $TOTAL_READS"
echo ""
echo "================================================================================"
echo ""

# Process RandomBarcodes
if [[ -d "$RANDOMBARCODES_DIR" ]]; then
    echo "▶ Processing RandomBarcodes..."
    echo "  Results dir: $RANDOMBARCODES_DIR"
    echo "  Output CSV:  $RANDOMBARCODES_OUTPUT"
    echo ""
    
    python3 "$RECOMPUTE_SCRIPT" \
        --barcode-file "$BARCODE_FILE_28NT" \
        --answers-file "$ANSWERS_FILE_28NT" \
        --results-dir "$RANDOMBARCODES_DIR" \
        --output-csv "$RANDOMBARCODES_OUTPUT" \
        --tool randombarcodes \
        --total-reads "$TOTAL_READS"
    
    echo ""
    echo "✓ RandomBarcodes processing complete!"
    echo ""
else
    echo "⚠ WARNING: RandomBarcodes directory not found: $RANDOMBARCODES_DIR"
    echo ""
fi

echo "================================================================================"
echo ""

# Process QUIK
if [[ -d "$QUIK_DIR" ]]; then
    echo "▶ Processing QUIK..."
    echo "  Results dir: $QUIK_DIR"
    echo "  Output CSV:  $QUIK_OUTPUT"
    echo ""
    
    python3 "$RECOMPUTE_SCRIPT" \
        --barcode-file "$BARCODE_FILE_28NT" \
        --answers-file "$ANSWERS_FILE_28NT" \
        --results-dir "$QUIK_DIR" \
        --output-csv "$QUIK_OUTPUT" \
        --tool quik \
        --total-reads "$TOTAL_READS"
    
    echo ""
    echo "✓ QUIK processing complete!"
    echo ""
else
    echo "⚠ WARNING: QUIK directory not found: $QUIK_DIR"
    echo ""
fi

echo "================================================================================"
echo ""

# Combine results
if [[ -f "$RANDOMBARCODES_OUTPUT" && -f "$QUIK_OUTPUT" ]]; then
    echo "▶ Combining results..."
    
    # Write header from first file
    head -n 1 "$RANDOMBARCODES_OUTPUT" > "$COMBINED_OUTPUT"
    
    # Append data from both files (skip headers)
    tail -n +2 "$RANDOMBARCODES_OUTPUT" >> "$COMBINED_OUTPUT"
    tail -n +2 "$QUIK_OUTPUT" >> "$COMBINED_OUTPUT"
    
    echo "✓ Combined results saved to: $COMBINED_OUTPUT"
    echo ""
    
    # Show summary
    TOTAL_SAMPLES=$(tail -n +2 "$COMBINED_OUTPUT" | wc -l)
    RB_SAMPLES=$(tail -n +2 "$RANDOMBARCODES_OUTPUT" | wc -l)
    QUIK_SAMPLES=$(tail -n +2 "$QUIK_OUTPUT" | wc -l)
    
    echo "Summary:"
    echo "  RandomBarcodes samples: $RB_SAMPLES"
    echo "  QUIK samples:           $QUIK_SAMPLES"
    echo "  Total samples:          $TOTAL_SAMPLES"
    echo ""
fi

echo "================================================================================"
echo "All Processing Complete!"
echo "================================================================================"
echo ""
echo "Output files:"
echo "  RandomBarcodes: $RANDOMBARCODES_OUTPUT"
echo "  QUIK:           $QUIK_OUTPUT"
echo "  Combined:       $COMBINED_OUTPUT"
echo ""
echo "Compare with original results in:"
echo "  ${SCRIPT_DIR}/benchmark_results_summary.csv"
echo ""
    "QUIK" \
    "$RESULTS_DIR/quik_sweep" \
    "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_28nt/barcodes_21K_28_subset1" \
    "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_28nt/answers_21K_28_low"

# Columba sweep
echo "=== Columba Sweep ==="
recompute_sam_metrics \
    "$RESULTS_DIR/columba_sweep" \
    "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/barcodes_21K_28_subset1" \
    "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/answers_21K_28_low"

echo "=========================================="
echo "Metrics Recomputation Complete!"
echo "=========================================="
