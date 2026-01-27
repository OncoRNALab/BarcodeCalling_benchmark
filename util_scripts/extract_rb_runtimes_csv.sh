#!/bin/bash
#
# Extract RandomBarcodes runtime metrics to CSV format
#

RESULTS_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_runtime/randombarcodes"
WORK_BASE="/kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/work_runtime_rb"
OUTPUT_CSV="randombarcodes_runtime_summary.csv"

# Create CSV header
echo "sample_id,ntriage,gpus,total_reads,total_compute_time_sec,wall_clock_time_sec,time_per_read_ms,speedup_vs_1gpu" > "$OUTPUT_CSV"

# Function to extract timing from GPU logs
extract_timing_csv() {
    local sample_id="$1"
    local work_dir="$2"
    
    # Extract parameters from sample ID
    # runtime_t100_1gpu -> ntriage=100, gpus=1
    # runtime_t5000_2gpu -> ntriage=5000, gpus=2
    local ntriage=$(echo "$sample_id" | grep -oP 't\K[0-9]+')
    local gpus=$(echo "$sample_id" | grep -oP '[0-9]+gpu' | grep -oP '[0-9]+')
    
    # Find GPU log files
    local gpu_logs=$(find "$work_dir" -name "gpu_*.log" 2>/dev/null)
    
    if [ -z "$gpu_logs" ]; then
        return
    fi
    
    local total_time=0
    local total_reads=0
    local gpu_count=0
    local max_time=0
    
    # Parse each GPU log
    for gpu_log in $gpu_logs; do
        time_sec=$(grep "Barcode decoding completed in" "$gpu_log" | grep -oP '[0-9]+\.[0-9]+' | head -1)
        reads_proc=$(grep "Total reads processed:" "$gpu_log" | grep -oP '[0-9]+' | head -1)
        
        if [ -n "$time_sec" ] && [ -n "$reads_proc" ]; then
            total_time=$(awk "BEGIN {print $total_time + $time_sec}")
            total_reads=$((total_reads + reads_proc))
            gpu_count=$((gpu_count + 1))
            
            # Track max time (wall clock for parallel execution)
            if (( $(awk "BEGIN {print ($time_sec > $max_time)}") )); then
                max_time=$time_sec
            fi
        fi
    done
    
    # Calculate metrics
    if [ $gpu_count -gt 0 ] && [ $total_reads -gt 0 ]; then
        avg_time_per_read=$(awk "BEGIN {printf \"%.6f\", ($total_time / $total_reads) * 1000}")
        
        # Wall clock time is max of all GPU times (they run in parallel)
        wall_clock=$max_time
        
        # Speedup calculation will be done later in post-processing
        speedup="N/A"
        
        # Write to CSV
        echo "$sample_id,$ntriage,$gpus,$total_reads,$total_time,$wall_clock,$avg_time_per_read,$speedup" >> "$OUTPUT_CSV"
    fi
}

# Main processing
echo "Extracting runtime metrics to CSV..."

# Process all sample directories
for sample_dir in "$RESULTS_DIR"/runtime_*; do
    if [ -d "$sample_dir" ]; then
        sample_id=$(basename "$sample_dir")
        work_subdir=$(echo "$sample_id" | sed 's/runtime_//')
        work_dir="$WORK_BASE/$work_subdir"
        
        if [ -d "$work_dir" ]; then
            extract_timing_csv "$sample_id" "$work_dir"
        fi
    fi
done

# Post-process to calculate speedup
# Read baseline (1 GPU) times for each ntriage value
t100_1gpu_time=$(grep "runtime_t100_1gpu" "$OUTPUT_CSV" | cut -d',' -f6)
t5000_1gpu_time=$(grep "runtime_t5000_1gpu" "$OUTPUT_CSV" | cut -d',' -f6)

# Create temporary file for updated CSV
TMP_CSV="${OUTPUT_CSV}.tmp"
head -1 "$OUTPUT_CSV" > "$TMP_CSV"

# Calculate speedup for each row
tail -n +2 "$OUTPUT_CSV" | while IFS=',' read -r sample_id ntriage gpus total_reads total_compute wall_clock time_per_read speedup; do
    # Determine baseline
    if [ "$ntriage" = "100" ]; then
        baseline=$t100_1gpu_time
    elif [ "$ntriage" = "5000" ]; then
        baseline=$t5000_1gpu_time
    else
        baseline=""
    fi
    
    # Calculate speedup
    if [ -n "$baseline" ] && [ -n "$wall_clock" ] && (( $(awk "BEGIN {print ($baseline > 0 && $wall_clock > 0)}") )); then
        speedup=$(awk "BEGIN {printf \"%.2f\", $baseline / $wall_clock}")
    else
        speedup="N/A"
    fi
    
    echo "$sample_id,$ntriage,$gpus,$total_reads,$total_compute,$wall_clock,$time_per_read,$speedup" >> "$TMP_CSV"
done

mv "$TMP_CSV" "$OUTPUT_CSV"

echo "✓ CSV created: $OUTPUT_CSV"
echo ""
echo "Summary:"
column -t -s',' "$OUTPUT_CSV"
