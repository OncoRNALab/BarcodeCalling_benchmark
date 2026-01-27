#!/bin/bash
#
# Script to extract RandomBarcodes runtime metrics from GPU logs and update stats files
# Location: /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark
#

RESULTS_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_runtime/randombarcodes"
WORK_BASE="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_runtime_rb"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "   RandomBarcodes Runtime Stats Update - Fix Missing Metrics"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Check if results directory exists
if [ ! -d "$RESULTS_DIR" ]; then
    echo "ERROR: Results directory not found: $RESULTS_DIR"
    exit 1
fi

# Function to extract timing and update stats file
update_stats_file() {
    local sample_id="$1"
    local work_dir="$2"
    local stats_file="$3"
    
    echo "─────────────────────────────────────────────────────────────────────────"
    echo "Sample: $sample_id"
    echo "─────────────────────────────────────────────────────────────────────────"
    
    # Check if stats file exists
    if [ ! -f "$stats_file" ]; then
        echo "  ⚠️  Stats file not found: $stats_file"
        echo ""
        return 1
    fi
    
    # Check if runtime metrics already exist
    if grep -q "Runtime metrics:" "$stats_file" && grep -q "Total time (seconds):" "$stats_file"; then
        echo "  ✓  Runtime metrics already present in stats file"
        echo ""
        return 0
    fi
    
    # Find GPU log files in work directory
    local gpu_logs=$(find "$work_dir" -name "gpu_*.log" 2>/dev/null | sort)
    
    if [ -z "$gpu_logs" ]; then
        echo "  ⚠️  No GPU logs found in work directory"
        echo ""
        return 1
    fi
    
    local total_time=0
    local total_reads=0
    local gpu_count=0
    
    echo "  Extracting timing from GPU logs..."
    
    # Parse each GPU log
    for gpu_log in $gpu_logs; do
        gpu_num=$(basename "$gpu_log" .log | sed 's/gpu_//')
        
        # Extract timing (escape brackets for grep -P)
        time_sec=$(grep "Barcode decoding completed in" "$gpu_log" | grep -oP '\d+\.\d+' | head -1)
        reads_proc=$(grep "Total reads processed:" "$gpu_log" | grep -oP '\d+' | head -1)
        
        if [ -n "$time_sec" ] && [ -n "$reads_proc" ]; then
            echo "    GPU $gpu_num: $time_sec seconds, $reads_proc reads"
            
            # Aggregate
            total_time=$(awk "BEGIN {print $total_time + $time_sec}")
            total_reads=$((total_reads + reads_proc))
            gpu_count=$((gpu_count + 1))
        fi
    done
    
    # Calculate overall metrics and update stats file
    if [ $gpu_count -gt 0 ] && [ $total_reads -gt 0 ]; then
        # For wall clock time, use the maximum GPU time (they run in parallel)
        # Not the sum of all GPU times
        wallclock_time=$(awk "BEGIN {print $total_time / $gpu_count}")
        avg_time_per_read=$(awk "BEGIN {printf \"%.6f\", ($total_time / $total_reads) * 1000}")
        
        echo ""
        echo "  📊 Aggregated Metrics:"
        echo "    - Total compute time: $total_time seconds"
        echo "    - Wall clock time: $wallclock_time seconds (max GPU time)"
        echo "    - Total reads: $total_reads"
        echo "    - Avg time per read: $avg_time_per_read ms"
        echo ""
        
        # Append runtime metrics to stats file
        echo "  ✏️  Updating stats file..."
        
        cat >> "$stats_file" <<EOF
Runtime metrics:
  Wall clock time (seconds): $wallclock_time
  Total compute time (seconds): $total_time
  Time per read (milliseconds): $avg_time_per_read
EOF
        
        echo "  ✓  Stats file updated successfully"
        echo ""
        return 0
    else
        echo "  ⚠️  No valid timing data found in GPU logs"
        echo ""
        return 1
    fi
}

# Main processing
echo "Scanning for samples with missing runtime metrics..."
echo ""

updated_count=0
skipped_count=0
error_count=0

# Find all sample directories
for sample_dir in "$RESULTS_DIR"/runtime_*; do
    if [ -d "$sample_dir" ]; then
        sample_id=$(basename "$sample_dir")
        
        # Determine work directory based on sample ID
        # runtime_t100_1gpu -> t100_1gpu
        work_subdir=$(echo "$sample_id" | sed 's/runtime_//')
        work_dir="$WORK_BASE/$work_subdir"
        
        # Stats file path
        stats_file="$sample_dir/${sample_id}_barcode_calling_stats.txt"
        
        if [ -d "$work_dir" ]; then
            if update_stats_file "$sample_id" "$work_dir" "$stats_file"; then
                updated_count=$((updated_count + 1))
            else
                error_count=$((error_count + 1))
            fi
        else
            echo "─────────────────────────────────────────────────────────────────────────"
            echo "Sample: $sample_id"
            echo "  ⚠️  Work directory not found: $work_dir"
            echo ""
            error_count=$((error_count + 1))
        fi
    fi
done

echo "═══════════════════════════════════════════════════════════════════════════"
echo "                            UPDATE COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Summary:"
echo "  ✓ Updated: $updated_count files"
echo "  ⚠️ Errors:  $error_count files"
echo ""
echo "Updated stats files can be found in:"
echo "  $RESULTS_DIR"
echo ""
