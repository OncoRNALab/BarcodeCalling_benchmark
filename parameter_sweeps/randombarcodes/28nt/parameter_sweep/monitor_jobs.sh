#!/bin/bash
#
# Monitor parameter sweep job progress
# Usage: ./parameter_sweep/monitor_jobs.sh
#

RESULTS_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/randombarcodes_sweep"
LOGS_DIR="./parameter_sweep/logs"

echo "=========================================="
echo "RandomBarcodes Parameter Sweep Monitor"
echo "=========================================="
echo ""

# Count jobs in queue
echo "📊 Job Queue Status:"
echo "-------------------"
queued=$(qstat -u $USER | grep "RB_" | grep " Q " | wc -l)
running=$(qstat -u $USER | grep "RB_" | grep " R " | wc -l)
total_jobs=30

echo "  Queued:  $queued"
echo "  Running: $running"
echo "  Total:   $total_jobs"
echo ""

# Count completed results
echo "✅ Completed Jobs:"
echo "-----------------"
if [ -d "$RESULTS_DIR" ]; then
    completed=$(find "$RESULTS_DIR" -name "precision_summary.csv" 2>/dev/null | wc -l)
    echo "  Completed: $completed / $total_jobs"
    
    if [ $completed -gt 0 ]; then
        completion_pct=$((completed * 100 / total_jobs))
        echo "  Progress:  $completion_pct%"
        
        # Progress bar
        filled=$((completion_pct / 2))
        empty=$((50 - filled))
        printf "  ["
        printf "%${filled}s" | tr ' ' '='
        printf "%${empty}s" | tr ' ' '-'
        printf "]\n"
    fi
else
    echo "  No results directory found yet"
fi
echo ""

# Check for errors
echo "⚠️  Error Check:"
echo "---------------"
if [ -d "$LOGS_DIR" ]; then
    error_count=$(grep -l "ERROR\|Failed\|killed" "$LOGS_DIR"/*.err 2>/dev/null | wc -l)
    if [ $error_count -gt 0 ]; then
        echo "  ⚠️  Found $error_count jobs with errors"
        echo "  Run: grep -l 'ERROR' $LOGS_DIR/*.err"
    else
        echo "  ✓ No errors detected"
    fi
else
    echo "  No logs directory found yet"
fi
echo ""

# Recent activity
echo "📝 Recent Activity:"
echo "------------------"
if [ -d "$LOGS_DIR" ]; then
    echo "  Last 5 updated log files:"
    ls -lt "$LOGS_DIR"/*.out 2>/dev/null | head -5 | awk '{print "    " $9}' | xargs -I {} basename {}
else
    echo "  No logs yet"
fi
echo ""

# Estimated completion
if [ $completed -gt 0 ] && [ $running -gt 0 ]; then
    remaining=$((total_jobs - completed))
    echo "⏱️  Estimated Completion:"
    echo "----------------------"
    echo "  Jobs remaining: $remaining"
    echo "  Jobs running:   $running"
    
    if [ $running -ge $remaining ]; then
        echo "  Status: Should complete soon!"
    else
        batches=$(((remaining + running - 1) / running))
        echo "  Status: ~$batches more batch(es) needed"
    fi
    echo ""
fi

# Quick commands
echo "💡 Quick Commands:"
echo "-----------------"
echo "  Watch queue:     watch -n 30 'qstat -u \$USER'"
echo "  View log:        tail -f $LOGS_DIR/RB_t1000_n7.out"
echo "  Check errors:    grep -l ERROR $LOGS_DIR/*.err"
echo "  Analyze results: python parameter_sweep/analyze_results.py"
echo ""

echo "=========================================="
echo "Last updated: $(date)"
echo "=========================================="


