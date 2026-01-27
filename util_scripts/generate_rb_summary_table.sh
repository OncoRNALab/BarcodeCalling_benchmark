#!/bin/bash
#
# Script to generate RandomBarcodes runtime summary table
# Location: /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark
#

RESULTS_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_runtime/randombarcodes"
OUTPUT_FILE="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/randombarcodes_runtime_summary.txt"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "   RandomBarcodes Runtime Summary Table Generator"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Check if results directory exists
if [ ! -d "$RESULTS_DIR" ]; then
    echo "ERROR: Results directory not found: $RESULTS_DIR"
    exit 1
fi

# Arrays to store data
declare -A data_config
declare -A data_gpus
declare -A data_ntriage
declare -A data_wallclock
declare -A data_timeperread

# Extract data from all stats files
echo "Extracting runtime data from stats files..."
for statsfile in "$RESULTS_DIR"/runtime_*/runtime_*_barcode_calling_stats.txt; do
    if [ -f "$statsfile" ]; then
        config=$(basename "$(dirname "$statsfile")")
        
        # Extract metrics
        gpus=$(grep "GPUs used:" "$statsfile" | awk '{print $NF}')
        ntriage=$(grep "Triage size (Ntriage):" "$statsfile" | awk '{print $NF}')
        
        # Try to get wall clock time first, fall back to total time
        wallclock=$(grep "Wall clock time (seconds):" "$statsfile" | awk '{print $NF}')
        if [ -z "$wallclock" ]; then
            # Old format: use total time divided by GPU count for wall clock
            total_time=$(grep "Total time (seconds):" "$statsfile" | awk '{print $NF}')
            if [ -n "$total_time" ] && [ -n "$gpus" ]; then
                wallclock=$(awk "BEGIN {print $total_time / $gpus}")
            fi
        fi
        
        timeperread=$(grep "Time per read (milliseconds):" "$statsfile" | awk '{print $NF}')
        
        if [ -n "$gpus" ] && [ -n "$wallclock" ]; then
            data_config["$config"]="$config"
            data_gpus["$config"]="$gpus"
            data_ntriage["$config"]="$ntriage"
            data_wallclock["$config"]="$wallclock"
            data_timeperread["$config"]="$timeperread"
            echo "  ✓ $config"
        fi
    fi
done

echo ""
echo "Generating summary table..."
echo ""

# Function to generate table for a specific ntriage value
generate_table() {
    local ntriage_val="$1"
    local table_title="$2"
    
    # Collect data for this ntriage value
    local -a configs
    for config in "${!data_ntriage[@]}"; do
        if [ "${data_ntriage[$config]}" = "$ntriage_val" ]; then
            configs+=("$config")
        fi
    done
    
    # Sort configs by GPU count
    IFS=$'\n' sorted=($(for config in "${configs[@]}"; do
        echo "${data_gpus[$config]} $config"
    done | sort -n))
    unset IFS
    
    # Find baseline (1 GPU) for speedup calculation
    local baseline_time=""
    for item in "${sorted[@]}"; do
        gpus=$(echo "$item" | awk '{print $1}')
        config=$(echo "$item" | awk '{$1=""; print $0}' | xargs)
        if [ "$gpus" = "1" ]; then
            baseline_time="${data_wallclock[$config]}"
            break
        fi
    done
    
    # Generate table header
    echo "$table_title"
    echo "════════════════════════════════════════════════════════════════════"
    printf "%-10s %-20s %-15s %-10s\n" "GPUs" "Wall Clock (s)" "Time/Read (ms)" "Speedup"
    echo "────────────────────────────────────────────────────────────────────"
    
    # Generate table rows
    for item in "${sorted[@]}"; do
        gpus=$(echo "$item" | awk '{print $1}')
        config=$(echo "$item" | awk '{$1=""; print $0}' | xargs)
        
        wallclock="${data_wallclock[$config]}"
        timeperread="${data_timeperread[$config]}"
        
        # Calculate speedup
        if [ -n "$baseline_time" ] && [ -n "$wallclock" ]; then
            speedup=$(awk "BEGIN {printf \"%.2f\", $baseline_time / $wallclock}")
        else
            speedup="-"
        fi
        
        printf "%-10s %-20s %-15s %-10s\n" "$gpus" "$wallclock" "$timeperread" "${speedup}x"
    done
    
    echo "════════════════════════════════════════════════════════════════════"
    echo ""
}

# Generate output file
{
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "                    RandomBarcodes Runtime Summary"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Generated: $(date)"
    echo "Dataset: 200,000 reads, 21,000 barcodes (36nt)"
    echo ""
    
    # Generate tables for each ntriage configuration
    generate_table "100" "Configuration: Ntriage = 100"
    generate_table "5000" "Configuration: Ntriage = 5000"
    
    echo ""
    echo "Notes:"
    echo "  - Wall Clock: Actual elapsed time (max GPU time for parallel execution)"
    echo "  - Time/Read: Average time per read (total compute time / total reads)"
    echo "  - Speedup: Relative to single GPU configuration (wall clock basis)"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    
} | tee "$OUTPUT_FILE"

echo ""
echo "✓ Summary table saved to: $OUTPUT_FILE"
echo ""
