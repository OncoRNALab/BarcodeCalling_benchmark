#!/bin/bash
#
# Temporary script to extract RandomBarcodes runtime metrics from existing runs
# Location: /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark
#

RESULTS_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_runtime/randombarcodes"
WORK_BASE="/kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/work_runtime_rb"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "   RandomBarcodes Runtime Extraction - Temporary Analysis Script"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Check if results directory exists
if [ ! -d "$RESULTS_DIR" ]; then
    echo "ERROR: Results directory not found: $RESULTS_DIR"
    exit 1
fi

# Function to extract timing from GPU logs
extract_timing() {
    local sample_id="$1"
    local work_dir="$2"
    
    echo "─────────────────────────────────────────────────────────────────────────"
    echo "Sample: $sample_id"
    echo "─────────────────────────────────────────────────────────────────────────"
    
    # Find GPU log files in work directory
    local gpu_logs=$(find "$work_dir" -name "gpu_*.log" 2>/dev/null)
    
    if [ -z "$gpu_logs" ]; then
        echo "  ⚠️  No GPU logs found in work directory"
        echo ""
        return
    fi
    
    local total_time=0
    local total_reads=0
    local gpu_count=0
    
    # Parse each GPU log
    for gpu_log in $gpu_logs; do
        gpu_num=$(basename "$gpu_log" .log | sed 's/gpu_//')
        
        # Extract timing
        time_sec=$(grep "Barcode decoding completed in" "$gpu_log" | grep -oP '[0-9]+\.[0-9]+' | head -1)
        reads_proc=$(grep "Total reads processed:" "$gpu_log" | grep -oP '[0-9]+' | head -1)
        time_per_read=$(grep "Time per read:" "$gpu_log" | grep -oP '[0-9]+\.[0-9]+' | head -1)
        
        if [ -n "$time_sec" ] && [ -n "$reads_proc" ]; then
            echo "  GPU $gpu_num:"
            echo "    - Reads processed: $reads_proc"
            echo "    - Total time: $time_sec seconds"
            echo "    - Time per read: $time_per_read ms"
            
            # Aggregate
            total_time=$(awk "BEGIN {print $total_time + $time_sec}")
            total_reads=$((total_reads + reads_proc))
            gpu_count=$((gpu_count + 1))
        fi
    done
    
    # Calculate overall metrics
    if [ $gpu_count -gt 0 ]; then
        echo ""
        echo "  AGGREGATED METRICS:"
        echo "    - Total GPUs: $gpu_count"
        echo "    - Total reads: $total_reads"
        echo "    - Total compute time: $total_time seconds"
        
        if [ $total_reads -gt 0 ]; then
            avg_time_per_read=$(awk "BEGIN {printf \"%.6f\", ($total_time / $total_reads) * 1000}")
            echo "    - Average time per read: $avg_time_per_read ms"
        fi
        
        # Calculate speedup if multi-GPU
        if [ $gpu_count -gt 1 ]; then
            # Estimate single-GPU time (sum of all GPU times / number of GPUs gives baseline)
            single_gpu_estimate=$(awk "BEGIN {print $total_time}")
            echo ""
            echo "  PARALLELISM ANALYSIS:"
            echo "    - Total compute time: $total_time seconds"
            echo "    - Expected wall-clock time: ~$(awk "BEGIN {printf \"%.1f\", $total_time / $gpu_count}") seconds"
            echo "    - Theoretical speedup: ${gpu_count}x"
        fi
    else
        echo "  ⚠️  No valid timing data found in GPU logs"
    fi
    
    echo ""
}

# Main processing
echo "Scanning for completed samples..."
echo ""

# Find all sample directories
for sample_dir in "$RESULTS_DIR"/runtime_*; do
    if [ -d "$sample_dir" ]; then
        sample_id=$(basename "$sample_dir")
        
        # Determine work directory based on sample ID
        # runtime_t100_1gpu -> t100_1gpu
        work_subdir=$(echo "$sample_id" | sed 's/runtime_//')
        work_dir="$WORK_BASE/$work_subdir"
        
        if [ -d "$work_dir" ]; then
            extract_timing "$sample_id" "$work_dir"
        else
            echo "─────────────────────────────────────────────────────────────────────────"
            echo "Sample: $sample_id"
            echo "  ⚠️  Work directory not found: $work_dir"
            echo ""
        fi
    fi
done

echo "═══════════════════════════════════════════════════════════════════════════"
echo "                            EXTRACTION COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════════"
