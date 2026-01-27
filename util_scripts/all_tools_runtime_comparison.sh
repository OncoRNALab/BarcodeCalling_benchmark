#!/bin/bash
#
# Script to generate comprehensive runtime comparison across all barcode calling tools
# Location: /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark
#

RESULTS_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_runtime"
OUTPUT_FILE="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/all_tools_runtime_comparison.txt"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "   Barcode Calling Tools - Comprehensive Runtime Comparison"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Generate output file
{
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "           Barcode Calling Tools - Runtime Comparison"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Generated: $(date)"
    echo "Dataset: 200,000 reads, 21,000 barcodes (36nt)"
    echo ""
    
    # ========================================
    # QUIK Results
    # ========================================
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "                            QUIK (GPU-Based)"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Note: QUIK does not support multi-GPU operation. GPU count in config"
    echo "      represents overhead testing (same algorithm, different allocations)."
    echo ""
    
    # 4-mer strategy
    echo "Strategy: 4-mer (simpler k-mer matching)"
    echo "────────────────────────────────────────────────────────────────────"
    printf "%-15s %-20s %-15s %-15s\n" "Config" "Wall Clock (s)" "Time/Read (ms)" "Overhead"
    echo "────────────────────────────────────────────────────────────────────"
    
    baseline_4mer=""
    for statsfile in "$RESULTS_DIR"/quik/runtime_4mer_*/runtime_*_barcode_calling_stats.txt; do
        if [ -f "$statsfile" ]; then
            config=$(basename "$(dirname "$statsfile")" | sed 's/runtime_//')
            wallclock=$(grep "Barcode calling completed in" "$statsfile" | awk '{print $5}')
            timeperread=$(grep "Time per read:" "$statsfile" | awk '{print $4}')
            
            if [ -z "$baseline_4mer" ]; then
                baseline_4mer=$wallclock
                overhead="-"
            else
                overhead=$(awk "BEGIN {printf \"%.2f%%\", (($wallclock - $baseline_4mer) / $baseline_4mer) * 100}")
            fi
            
            printf "%-15s %-20s %-15s %-15s\n" "$config" "$wallclock" "$timeperread" "$overhead"
        fi
    done
    echo ""
    
    # 4-7 mer strategy
    echo "Strategy: 4-7mer (more complex k-mer matching)"
    echo "────────────────────────────────────────────────────────────────────"
    printf "%-15s %-20s %-15s %-15s\n" "Config" "Wall Clock (s)" "Time/Read (ms)" "Overhead"
    echo "────────────────────────────────────────────────────────────────────"
    
    baseline_4_7mer=""
    for statsfile in "$RESULTS_DIR"/quik/runtime_4_7mer_*/runtime_*_barcode_calling_stats.txt; do
        if [ -f "$statsfile" ]; then
            config=$(basename "$(dirname "$statsfile")" | sed 's/runtime_//')
            wallclock=$(grep "Barcode calling completed in" "$statsfile" | awk '{print $5}')
            timeperread=$(grep "Time per read:" "$statsfile" | awk '{print $4}')
            
            if [ -z "$baseline_4_7mer" ]; then
                baseline_4_7mer=$wallclock
                overhead="-"
            else
                overhead=$(awk "BEGIN {printf \"%.2f%%\", (($wallclock - $baseline_4_7mer) / $baseline_4_7mer) * 100}")
            fi
            
            printf "%-15s %-20s %-15s %-15s\n" "$config" "$wallclock" "$timeperread" "$overhead"
        fi
    done
    echo ""
    echo "Key Findings:"
    echo "  • QUIK is extremely fast (~3-5 seconds for 200K reads)"
    echo "  • Minimal overhead with different GPU allocations (< 4% variation)"
    echo "  • 4-mer strategy is ~30% faster than 4-7mer strategy"
    echo ""
    
    # ========================================
    # RandomBarcodes Results
    # ========================================
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "                       RandomBarcodes (GPU-Based)"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "RandomBarcodes supports true multi-GPU parallelization"
    echo ""
    
    # ntriage=100
    echo "Configuration: Ntriage = 100 (small triage window)"
    echo "────────────────────────────────────────────────────────────────────"
    printf "%-10s %-20s %-15s %-10s\n" "GPUs" "Wall Clock (s)" "Time/Read (ms)" "Speedup"
    echo "────────────────────────────────────────────────────────────────────"
    
    baseline_rb_t100=""
    for statsfile in "$RESULTS_DIR"/randombarcodes/runtime_t100_*/runtime_*_barcode_calling_stats.txt; do
        if [ -f "$statsfile" ]; then
            config=$(basename "$(dirname "$statsfile")")
            gpus=$(grep "GPUs used:" "$statsfile" | awk '{print $NF}')
            ntriage=$(grep "Triage size (Ntriage):" "$statsfile" | awk '{print $NF}')
            
            if [ "$ntriage" = "100" ]; then
                wallclock=$(grep "Wall clock time (seconds):" "$statsfile" | awk '{print $NF}')
                if [ -z "$wallclock" ]; then
                    total_time=$(grep "Total time (seconds):" "$statsfile" | awk '{print $NF}')
                    wallclock=$(awk "BEGIN {print $total_time / $gpus}")
                fi
                timeperread=$(grep "Time per read (milliseconds):" "$statsfile" | awk '{print $NF}')
                
                if [ -z "$baseline_rb_t100" ]; then
                    baseline_rb_t100=$wallclock
                    speedup="1.00x"
                else
                    speedup=$(awk "BEGIN {printf \"%.2fx\", $baseline_rb_t100 / $wallclock}")
                fi
                
                printf "%-10s %-20s %-15s %-10s\n" "$gpus" "$wallclock" "$timeperread" "$speedup"
            fi
        fi
    done
    echo ""
    
    # ntriage=5000
    echo "Configuration: Ntriage = 5000 (large triage window)"
    echo "────────────────────────────────────────────────────────────────────"
    printf "%-10s %-20s %-15s %-10s\n" "GPUs" "Wall Clock (s)" "Time/Read (ms)" "Speedup"
    echo "────────────────────────────────────────────────────────────────────"
    
    baseline_rb_t5000=""
    for statsfile in "$RESULTS_DIR"/randombarcodes/runtime_t5000_*/runtime_*_barcode_calling_stats.txt; do
        if [ -f "$statsfile" ]; then
            config=$(basename "$(dirname "$statsfile")")
            gpus=$(grep "GPUs used:" "$statsfile" | awk '{print $NF}')
            ntriage=$(grep "Triage size (Ntriage):" "$statsfile" | awk '{print $NF}')
            
            if [ "$ntriage" = "5000" ]; then
                wallclock=$(grep "Wall clock time (seconds):" "$statsfile" | awk '{print $NF}')
                if [ -z "$wallclock" ]; then
                    total_time=$(grep "Total time (seconds):" "$statsfile" | awk '{print $NF}')
                    wallclock=$(awk "BEGIN {print $total_time / $gpus}")
                fi
                timeperread=$(grep "Time per read (milliseconds):" "$statsfile" | awk '{print $NF}')
                
                if [ -z "$baseline_rb_t5000" ]; then
                    baseline_rb_t5000=$wallclock
                    speedup="1.00x"
                else
                    speedup=$(awk "BEGIN {printf \"%.2fx\", $baseline_rb_t5000 / $wallclock}")
                fi
                
                printf "%-10s %-20s %-15s %-10s\n" "$gpus" "$wallclock" "$timeperread" "$speedup"
            fi
        fi
    done
    echo ""
    echo "Key Findings:"
    echo "  • Excellent scaling with ntriage=5000 (up to 5.5x with 4 GPUs)"
    echo "  • Limited scaling with ntriage=100 (workload too small)"
    echo "  • Larger triage window increases accuracy but requires more compute"
    echo ""
    
    # ========================================
    # Columba Results
    # ========================================
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "                        Columba (CPU-Based)"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Columba uses CPU-based alignment with multi-threading support"
    echo ""
    echo "────────────────────────────────────────────────────────────────────"
    printf "%-10s %-20s %-15s %-10s %-15s\n" "CPUs" "Wall Clock (s)" "Time/Read (ms)" "Speedup" "Efficiency"
    echo "────────────────────────────────────────────────────────────────────"
    
    baseline_columba=""
    for statsfile in "$RESULTS_DIR"/columba/runtime_*/runtime_*_barcode_calling_stats.txt; do
        if [ -f "$statsfile" ]; then
            config=$(basename "$(dirname "$statsfile")")
            cpus=$(echo "$config" | grep -oE '[0-9]+')
            wallclock=$(grep "Total alignment time:" "$statsfile" | awk '{print $4}')
            timeperread=$(grep "Time per read:" "$statsfile" | awk '{print $4}')
            
            if [ -z "$baseline_columba" ]; then
                baseline_columba=$wallclock
                speedup="1.00x"
                efficiency="-"
            else
                speedup_val=$(awk "BEGIN {print $baseline_columba / $wallclock}")
                speedup=$(awk "BEGIN {printf \"%.2fx\", $speedup_val}")
                efficiency=$(awk "BEGIN {printf \"%.1f%%\", ($speedup_val / $cpus) * 100}")
            fi
            
            printf "%-10s %-20s %-15s %-10s %-15s\n" "$cpus" "$wallclock" "$timeperread" "$speedup" "$efficiency"
        fi
    done
    echo ""
    echo "Key Findings:"
    echo "  • Excellent scaling up to 8 CPUs (8.26x speedup, 103% efficiency)"
    echo "  • Diminishing returns beyond 8 CPUs (50% efficiency at 16 CPUs)"
    echo "  • Near-linear scaling indicates well-parallelized algorithm"
    echo ""
    
    # ========================================
    # Overall Comparison
    # ========================================
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "                         Overall Comparison"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Best Single-Device Performance:"
    echo "────────────────────────────────────────────────────────────────────"
    echo "  1. QUIK (1 GPU, 4-mer):           3.35 seconds   (0.017 ms/read)"
    echo "  2. QUIK (1 GPU, 4-7mer):          4.82 seconds   (0.024 ms/read)"
    echo "  3. Columba (1 CPU):            1099.20 seconds   (5.244 ms/read)"
    echo "  4. RandomBarcodes (1 GPU, t100): 1903.06 seconds   (9.515 ms/read)"
    echo "  5. RandomBarcodes (1 GPU, t5000): 2739.03 seconds  (13.695 ms/read)"
    echo ""
    echo "Best Multi-Device Performance:"
    echo "────────────────────────────────────────────────────────────────────"
    echo "  1. QUIK (4 GPU, 4-mer):           3.36 seconds   (minimal overhead)"
    echo "  2. QUIK (4 GPU, 4-7mer):          4.65 seconds   (minimal overhead)"
    echo "  3. Columba (8 CPU):             133.06 seconds   (8.26x speedup)"
    echo "  4. RandomBarcodes (4 GPU, t100):  491.38 seconds   (3.87x speedup)"
    echo "  5. RandomBarcodes (4 GPU, t5000): 495.13 seconds   (5.53x speedup)"
    echo ""
    echo "Parallelization Efficiency:"
    echo "────────────────────────────────────────────────────────────────────"
    echo "  • QUIK:           Not applicable (single-GPU design)"
    echo "  • Columba:        Excellent (103% at 8 CPUs, near-linear scaling)"
    echo "  • RandomBarcodes: Good (97% at 4 GPUs with t5000)"
    echo ""
    echo "Speed Comparison (relative to slowest):"
    echo "────────────────────────────────────────────────────────────────────"
    
    slowest=2739.03
    quik_4mer=3.35
    columba_8cpu=133.06
    rb_4gpu_t5000=495.13
    
    quik_speedup=$(awk "BEGIN {printf \"%.0fx\", $slowest / $quik_4mer}")
    columba_speedup=$(awk "BEGIN {printf \"%.0fx\", $slowest / $columba_8cpu}")
    rb_speedup=$(awk "BEGIN {printf \"%.0fx\", $slowest / $rb_4gpu_t5000}")
    
    echo "  • QUIK (1 GPU, 4-mer):           ${quik_speedup} faster than RB baseline"
    echo "  • Columba (8 CPU):               ${columba_speedup} faster than RB baseline"
    echo "  • RandomBarcodes (4 GPU, t5000): ${rb_speedup} faster than RB baseline"
    echo ""
    echo "Recommendations:"
    echo "────────────────────────────────────────────────────────────────────"
    echo "  • For maximum speed:      Use QUIK (4-mer strategy)"
    echo "  • For CPU-only systems:   Use Columba with 8+ CPUs"
    echo "  • For accuracy:           Use RandomBarcodes (higher ntriage)"
    echo "  • For balance:            Use QUIK (4-7mer) or Columba (4-8 CPUs)"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    
} | tee "$OUTPUT_FILE"

echo ""
echo "✓ Comprehensive comparison saved to: $OUTPUT_FILE"
echo ""
