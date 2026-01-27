#!/bin/bash
# Master submission script for error rate benchmark
# This script submits all 27 jobs (3 tools × 3 barcode counts × 3 error rates)

BENCHMARK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/error_rate_benchmark"
JOBS_DIR="${BENCHMARK_DIR}/jobs"

echo "=========================================="
echo "Error Rate Benchmark - Job Submission"
echo "=========================================="
echo ""

# Array of all job scripts
TOOLS=("randombarcodes" "quik" "columba")
SIZES=("85K" "42K" "21K")
ERRORS=("low" "medium" "high")

total_jobs=0
submitted_jobs=0

for tool in "${TOOLS[@]}"; do
    echo "Submitting ${tool} jobs..."
    for size in "${SIZES[@]}"; do
        for error in "${ERRORS[@]}"; do
            job_script="${JOBS_DIR}/${tool}_${size}_${error}.sh"
            if [ -f "$job_script" ]; then
                echo "  - Submitting: ${tool}_${size}_${error}"
                sbatch "$job_script"
                if [ $? -eq 0 ]; then
                    ((submitted_jobs++))
                else
                    echo "    ERROR: Failed to submit ${tool}_${size}_${error}"
                fi
                ((total_jobs++))
                # Small delay to avoid overwhelming the scheduler
                sleep 0.5
            else
                echo "    WARNING: Job script not found: $job_script"
            fi
        done
    done
    echo ""
done

echo "=========================================="
echo "Submission Summary"
echo "=========================================="
echo "Total jobs: ${total_jobs}"
echo "Successfully submitted: ${submitted_jobs}"
echo ""
echo "To check job status, run: squeue -u $USER"
echo "Results will be saved in: ${BENCHMARK_DIR}/results/"
echo "=========================================="
