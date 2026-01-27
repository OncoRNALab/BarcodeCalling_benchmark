#!/bin/bash
#
# Submit all parameter sweep jobs for RandomBarcodes optimization
# This script submits 30 jobs (5 ntriage × 6 nthresh combinations)
#

set -e  # Exit on error

# Configuration
JOBS_DIR="parameter_sweep/jobs"
LOG_FILE="parameter_sweep/submission_log_$(date +%Y%m%d_%H%M%S).txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo ""
echo "======================================================================="
echo "  RandomBarcodes Parameter Sweep - Job Submission"
echo "======================================================================="
echo ""

# Check if jobs directory exists
if [ ! -d "$JOBS_DIR" ]; then
    echo -e "${RED}ERROR: Jobs directory not found: $JOBS_DIR${NC}"
    echo "Please run: python parameter_sweep/generate_sweep.py"
    exit 1
fi

# Count job files
JOB_COUNT=$(ls $JOBS_DIR/job_*.sh 2>/dev/null | wc -l)

if [ $JOB_COUNT -eq 0 ]; then
    echo -e "${RED}ERROR: No job files found in $JOBS_DIR${NC}"
    echo "Please run: python parameter_sweep/generate_sweep.py"
    exit 1
fi

echo -e "${GREEN}Found $JOB_COUNT job scripts${NC}"
echo ""

# Confirmation prompt
echo -e "${YELLOW}About to submit $JOB_COUNT jobs to the PBS queue.${NC}"
echo ""
echo "Job details:"
echo "  - Wall time: 10 hours per job"
echo "  - Resources: 1 CPU, 8GB RAM (wrapper)"
echo "  - Sub-jobs will request: 2 CPUs, 32GB RAM, 1 GPU (RandomBarcodes)"
echo ""
read -p "Do you want to continue? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Submission cancelled.${NC}"
    exit 0
fi

# Initialize counters
submitted=0
failed=0

# Create log file
echo "Parameter Sweep Submission Log" > "$LOG_FILE"
echo "Date: $(date)" >> "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Submit jobs
echo -e "${BLUE}Submitting jobs...${NC}"
echo ""

for job_file in $(ls $JOBS_DIR/job_*.sh | sort); do
    job_name=$(basename "$job_file" .sh)
    
    # Extract parameters from filename (e.g., job_t1000_n7.sh)
    params=$(echo "$job_name" | sed 's/job_//')
    
    echo -n "  Submitting $params ... "
    
    # Submit job and capture job ID
    if job_id=$(qsub "$job_file" 2>&1); then
        echo -e "${GREEN}✓${NC} Job ID: $job_id"
        echo "$params: $job_id" >> "$LOG_FILE"
        ((submitted++))
        
        # Small delay to avoid overwhelming the scheduler
        sleep 0.5
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "$params: FAILED - $job_id" >> "$LOG_FILE"
        ((failed++))
    fi
done

echo ""
echo "======================================================================="
echo "  Submission Summary"
echo "======================================================================="
echo ""
echo -e "  ${GREEN}Successfully submitted: $submitted jobs${NC}"
if [ $failed -gt 0 ]; then
    echo -e "  ${RED}Failed submissions:     $failed jobs${NC}"
fi
echo ""
echo "  Log file: $LOG_FILE"
echo ""

# Show queue status
echo "======================================================================="
echo "  Current Queue Status"
echo "======================================================================="
echo ""
qstat -u $USER | grep "RB_" || echo "No jobs found in queue yet (may take a moment to appear)"
echo ""

# Monitoring instructions
echo "======================================================================="
echo "  Monitoring Instructions"
echo "======================================================================="
echo ""
echo "Check job status:"
echo "  qstat -u \$USER"
echo ""
echo "Watch queue (updates every 30 seconds):"
echo "  watch -n 30 'qstat -u \$USER'"
echo ""
echo "Monitor sweep progress:"
echo "  ./parameter_sweep/monitor_jobs.sh"
echo ""
echo "View specific job log:"
echo "  tail -f parameter_sweep/logs/RB_t1000_n7.out"
echo ""
echo "Check for errors:"
echo "  grep -l ERROR parameter_sweep/logs/*.err"
echo ""

# Analysis instructions
echo "======================================================================="
echo "  After Completion"
echo "======================================================================="
echo ""
echo "Analyze results:"
echo "  python parameter_sweep/analyze_results.py"
echo ""
echo "Generate visualizations:"
echo "  python parameter_sweep/visualize_results.py"
echo ""
echo "======================================================================="
echo ""

exit 0


