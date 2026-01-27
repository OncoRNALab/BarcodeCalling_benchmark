#!/bin/bash
# Quick Reference: Submit all runtime benchmarking jobs
# Location: /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/runtime_benchmarks
# 
# Usage: bash SUBMIT_ALL_JOBS.sh
#
# Note: This script submits all 17 jobs. Review README.md before running!

set -e  # Exit on error

echo "========================================="
echo "Runtime Benchmarking Job Submission"
echo "Starting: $(date)"
echo "========================================="
echo ""

# Navigate to base directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Track submitted jobs
SUBMITTED_JOBS=()

# ============================================
# QUIK - Single submission (6 configs)
# ============================================
echo "Submitting QUIK jobs (all 6 configs in one job)..."
cd quik/jobs
JOB_ID=$(sbatch submit_all_quik.sh | grep -oP '\d+')
SUBMITTED_JOBS+=("QUIK_all:$JOB_ID")
echo "  ✓ Submitted: Job ID $JOB_ID"
cd "$SCRIPT_DIR"
echo ""

# ============================================
# RandomBarcodes - Individual submissions
# ============================================
echo "Submitting RandomBarcodes jobs (6 individual jobs)..."
cd randombarcodes/jobs
for JOB_SCRIPT in job_*.sh; do
    CONFIG=$(basename "$JOB_SCRIPT" .sh | sed 's/job_//')
    JOB_ID=$(sbatch "$JOB_SCRIPT" | grep -oP '\d+')
    SUBMITTED_JOBS+=("RB_$CONFIG:$JOB_ID")
    echo "  ✓ Submitted $CONFIG: Job ID $JOB_ID"
done
cd "$SCRIPT_DIR"
echo ""

# ============================================
# Columba - Individual submissions
# ============================================
echo "Submitting Columba jobs (3 individual jobs)..."
cd columba/jobs
for JOB_SCRIPT in job_*.sh; do
    CONFIG=$(basename "$JOB_SCRIPT" .sh | sed 's/job_//')
    JOB_ID=$(sbatch "$JOB_SCRIPT" | grep -oP '\d+')
    SUBMITTED_JOBS+=("Columba_$CONFIG:$JOB_ID")
    echo "  ✓ Submitted $CONFIG: Job ID $JOB_ID"
done
cd "$SCRIPT_DIR"
echo ""

# ============================================
# Summary
# ============================================
echo "========================================="
echo "All jobs submitted successfully!"
echo "========================================="
echo ""
echo "Total jobs: ${#SUBMITTED_JOBS[@]}"
echo ""
echo "Job IDs:"
for JOB in "${SUBMITTED_JOBS[@]}"; do
    echo "  - $JOB"
done
echo ""
echo "Monitor jobs:"
echo "  squeue -u \$USER"
echo ""
echo "Check logs:"
echo "  tail -f quik/logs/quik_runtime_bench.out"
echo "  tail -f randombarcodes/logs/RB_t100_1gpu.out"
echo "  tail -f columba/logs/Columba_1cpu.out"
echo ""
echo "Results will be in:"
echo "  /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_runtime/"
echo ""
echo "========================================="
echo "Finished: $(date)"
echo "========================================="
