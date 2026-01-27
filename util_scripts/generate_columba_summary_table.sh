#!/bin/bash
#
# Script to generate Columba runtime summary table
# Location: /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark
#

RESULTS_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_runtime/columba"
OUTPUT_FILE="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/columba_runtime_summary.txt"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "   Columba Runtime Summary Table Generator"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Check if results directory exists
if [ ! -d "$RESULTS_DIR" ]; then
    echo "ERROR: Results directory not found: $RESULTS_DIR"
    exit 1
fi

# Arrays to store data
declare -A data_config
declare -A data_cpus
declare -A data_wallclock
declare -A data_timeperread
declare -A data_total_reads
declare -A data_mapped_reads
declare -A data_mapping_rate

# Extract data from all stats files
echo "Extracting runtime data from stats files..."
for statsfile in "$RESULTS_DIR"/runtime_*/runtime_*_barcode_calling_stats.txt; do
    if [ -f "$statsfile" ]; then
        config=$(basename "$(dirname "$statsfile")")
        
        # Extract CPU count from config name (runtime_8cpu -> 8)
        cpus=$(echo "$config" | grep -oE '[0-9]+')
        
        # Extract metrics
        wallclock=$(grep "Total alignment time:" "$statsfile" | awk '{print $4}')
        timeperread=$(grep "Time per read:" "$statsfile" | awk '{print $4}')
        total_reads=$(grep "Total reads:" "$statsfile" | awk '{print $3}')
        mapped_reads=$(grep "Mapped reads:" "$statsfile" | awk '{print $3}')
        mapping_rate=$(grep "Mapping rate:" "$statsfile" | awk '{print $3}')
        
        if [ -n "$cpus" ] && [ -n "$wallclock" ]; then
            data_config["$config"]="$config"
            data_cpus["$config"]="$cpus"
            data_wallclock["$config"]="$wallclock"
            data_timeperread["$config"]="$timeperread"
            data_total_reads["$config"]="$total_reads"
            data_mapped_reads["$config"]="$mapped_reads"
            data_mapping_rate["$config"]="$mapping_rate"
            echo "  ✓ $config"
        fi
    fi
done

echo ""
echo "Generating summary table..."
echo ""

# Collect and sort configs by CPU count
declare -a configs
for config in "${!data_cpus[@]}"; do
    configs+=("$config")
done

# Sort configs by CPU count
IFS=$'\n' sorted=($(for config in "${configs[@]}"; do
    echo "${data_cpus[$config]} $config"
done | sort -n))
unset IFS

# Find baseline (1 CPU) for speedup calculation
baseline_time=""
for item in "${sorted[@]}"; do
    cpus=$(echo "$item" | awk '{print $1}')
    config=$(echo "$item" | awk '{$1=""; print $0}' | xargs)
    if [ "$cpus" = "1" ]; then
        baseline_time="${data_wallclock[$config]}"
        break
    fi
done

# Generate output file
{
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "                      Columba Runtime Summary"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Generated: $(date)"
    echo "Dataset: ${data_total_reads[${sorted[0]##* }]} reads, 21,000 barcodes (36nt)"
    echo "Identity threshold: 77%"
    echo ""
    echo "════════════════════════════════════════════════════════════════════"
    printf "%-10s %-20s %-15s %-10s %-15s\n" "CPUs" "Wall Clock (s)" "Time/Read (ms)" "Speedup" "Mapping Rate"
    echo "────────────────────────────────────────────────────────────────────"
    
    # Generate table rows
    for item in "${sorted[@]}"; do
        cpus=$(echo "$item" | awk '{print $1}')
        config=$(echo "$item" | awk '{$1=""; print $0}' | xargs)
        
        wallclock="${data_wallclock[$config]}"
        timeperread="${data_timeperread[$config]}"
        mapping_rate="${data_mapping_rate[$config]}"
        
        # Calculate speedup
        if [ -n "$baseline_time" ] && [ -n "$wallclock" ]; then
            speedup=$(awk "BEGIN {printf \"%.2f\", $baseline_time / $wallclock}")
        else
            speedup="-"
        fi
        
        printf "%-10s %-20s %-15s %-10s %-15s\n" "$cpus" "$wallclock" "$timeperread" "${speedup}x" "$mapping_rate"
    done
    
    echo "════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Notes:"
    echo "  - Wall Clock: Total alignment time (actual elapsed time)"
    echo "  - Time/Read: Average time per read"
    echo "  - Speedup: Relative to single CPU configuration"
    echo "  - Mapping Rate: Percentage of reads successfully mapped to barcodes"
    echo ""
    echo "Performance Analysis:"
    if [ -n "$baseline_time" ]; then
        echo "  Baseline (1 CPU): $baseline_time seconds"
        for item in "${sorted[@]}"; do
            cpus=$(echo "$item" | awk '{print $1}')
            config=$(echo "$item" | awk '{$1=""; print $0}' | xargs)
            if [ "$cpus" != "1" ]; then
                wallclock="${data_wallclock[$config]}"
                speedup=$(awk "BEGIN {printf \"%.2f\", $baseline_time / $wallclock}")
                efficiency=$(awk "BEGIN {printf \"%.1f\", ($speedup / $cpus) * 100}")
                echo "  ${cpus} CPUs: ${wallclock}s (${speedup}x speedup, ${efficiency}% parallel efficiency)"
            fi
        done
    fi
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    
} | tee "$OUTPUT_FILE"

echo ""
echo "✓ Summary table saved to: $OUTPUT_FILE"
echo ""
