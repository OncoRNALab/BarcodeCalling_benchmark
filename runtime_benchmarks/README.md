# Runtime Benchmarking Setup

This directory contains parameter files and job scripts for benchmarking the runtime performance of three barcode calling tools (QUIK, RandomBarcodes, and Columba) with different resource configurations.

## Overview

**Goal**: Compare runtime performance and GPU/CPU overhead for each tool with varying resource allocations.

**Dataset**: 36nt barcodes, 21K barcode library, low error rate reads
- Barcode file: `/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_36nt/barcodes_21K_36_subset1`
- Input reads: `reads_21K_36_low_R1.fastq` and `reads_21K_36_low_R2.fastq`
- Ground truth: `answers_21K_36_low`

**Total Jobs**: 17
- QUIK: 6 jobs (2 strategies × 3 GPU configs)
- RandomBarcodes: 6 jobs (2 ntriage values × 3 GPU configs)
- Columba: 3 jobs (1 config × 3 CPU counts)

## Directory Structure

```
runtime_benchmarks/
├── quik/
│   ├── params/           # Parameter JSON files
│   ├── jobs/             # Job submission scripts
│   └── logs/             # Job output and error logs
├── randombarcodes/
│   ├── params/
│   ├── jobs/
│   └── logs/
└── columba/
    ├── params/
    ├── jobs/
    └── logs/
```

## Tool Configurations

### QUIK (GPU-accelerated)
**Fixed parameters**:
- `rejection_threshold`: 8
- `distance_measure`: SEQUENCE_LEVENSHTEIN
- `barcode_start`: 0
- `barcode_length`: 36

**Variable parameters**:
| Strategy         | GPUs | Sample ID            | Job File              |
|------------------|------|----------------------|-----------------------|
| 4_mer_gpu_v4     | 1    | runtime_4mer_1gpu    | submit_all_quik.sh    |
| 4_mer_gpu_v4     | 2    | runtime_4mer_2gpu    | submit_all_quik.sh    |
| 4_mer_gpu_v4     | 4    | runtime_4mer_4gpu    | submit_all_quik.sh    |
| 4_7_mer_gpu_v1   | 1    | runtime_4_7mer_1gpu  | submit_all_quik.sh    |
| 4_7_mer_gpu_v1   | 2    | runtime_4_7mer_2gpu  | submit_all_quik.sh    |
| 4_7_mer_gpu_v1   | 4    | runtime_4_7mer_4gpu  | submit_all_quik.sh    |

**Purpose**: Test GPU overhead (QUIK doesn't parallelize across GPUs, so 2 and 4 GPU jobs should show overhead/no benefit)

### RandomBarcodes (GPU-accelerated)
**Fixed parameters**:
- `nthresh`: 9
- `barcode_length`: 36

**Variable parameters**:
| ntriage | GPUs | Sample ID           | Job File              |
|---------|------|---------------------|-----------------------|
| 100     | 1    | runtime_t100_1gpu   | job_t100_1gpu.sh      |
| 100     | 2    | runtime_t100_2gpu   | job_t100_2gpu.sh      |
| 100     | 4    | runtime_t100_4gpu   | job_t100_4gpu.sh      |
| 5000    | 1    | runtime_t5000_1gpu  | job_t5000_1gpu.sh     |
| 5000    | 2    | runtime_t5000_2gpu  | job_t5000_2gpu.sh     |
| 5000    | 4    | runtime_t5000_4gpu  | job_t5000_4gpu.sh     |

**Purpose**: Test task-level parallelism (multiple GPU chunks) and impact of triage size on runtime

### Columba (CPU-only)
**Fixed parameters**:
- `identity_threshold`: 77
- `barcode_window`: 0-36
- `barcode_length`: 36

**Variable parameters**:
| CPUs | Sample ID       | Job File         |
|------|-----------------|------------------|
| 1    | runtime_1cpu    | job_1cpu.sh      |
| 2    | runtime_2cpu    | job_2cpu.sh      |
| 4    | runtime_4cpu    | job_4cpu.sh      |

**Purpose**: Test CPU thread scalability for alignment-based approach

## Resource Allocation

All jobs use:
- **Memory**: 32GB (increased from 16GB to prevent OOM)
- **Walltime**: 
  - QUIK: 48 hours (all jobs in one submission)
  - RandomBarcodes: 24 hours per job
  - Columba: 48 hours per job (alignment is slower)

## Submission Instructions

### QUIK - Single Submission
All QUIK jobs run sequentially in one Slurm job:

```bash
cd runtime_benchmarks/quik/jobs
sbatch submit_all_quik.sh
```

### RandomBarcodes - Individual Submissions
Submit each configuration separately:

```bash
cd runtime_benchmarks/randombarcodes/jobs

# Submit all at once
for job in job_*.sh; do
    sbatch "$job"
done

# Or submit individually
sbatch job_t100_1gpu.sh
sbatch job_t100_2gpu.sh
# ... etc
```

### Columba - Individual Submissions
Submit each configuration separately:

```bash
cd runtime_benchmarks/columba/jobs

# Submit all at once
for job in job_*.sh; do
    sbatch "$job"
done

# Or submit individually
sbatch job_1cpu.sh
sbatch job_2cpu.sh
sbatch job_4cpu.sh
```

## Output Locations

Results are written to tool-specific directories:

```
/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_runtime/
├── quik/
│   ├── runtime_4mer_1gpu/
│   ├── runtime_4mer_2gpu/
│   ├── runtime_4_7mer_1gpu/
│   └── ...
├── randombarcodes/
│   ├── runtime_t100_1gpu/
│   ├── runtime_t5000_1gpu/
│   └── ...
└── columba/
    ├── runtime_1cpu/
    ├── runtime_2cpu/
    └── runtime_4cpu/
```

Each sample directory contains:
- Output files (FASTQ or SAM)
- `*_barcode_calling_stats.txt` - Runtime metrics
- `*_report.txt` - Precision/recall/F1 metrics
- `*_summary.csv` - CSV metrics with timing
- `trace.txt` - Nextflow trace with peak memory usage
- `report.html` - Nextflow execution report
- `timeline.html` - Nextflow timeline visualization

## Performance Metrics Captured

### Automatically Captured by Pipeline
1. **Total Runtime** (seconds) - Total barcode calling time
2. **Time per Read** (milliseconds) - Average time to process one read
3. **Peak Memory Usage** (from Nextflow trace):
   - `peak_rss` - Peak resident set size (RAM)
   - `peak_vmem` - Peak virtual memory
4. **Precision, Recall, F1** - Accuracy metrics

### How Timing is Measured

**RandomBarcodes**: 
- Measures decoding loop time (triage + Levenshtein distance calculation)
- Reported in `*_barcode_calling_stats.txt`

**QUIK**:
- Built-in timing from C++/CUDA code
- Measures GPU barcode calling kernel time
- Reported in `*_barcode_calling_stats.txt`

**Columba**:
- Shell wrapper timing around `./columba` execution
- Measures total alignment time
- Appended to `*_barcode_calling_stats.txt`

## Monitoring Jobs

### Check job status
```bash
squeue -u $USER
```

### View logs (while running or after completion)
```bash
# QUIK
tail -f runtime_benchmarks/quik/logs/quik_runtime_bench.out

# RandomBarcodes
tail -f runtime_benchmarks/randombarcodes/logs/RB_t100_1gpu.out

# Columba
tail -f runtime_benchmarks/columba/logs/Columba_1cpu.out
```

### Cancel jobs
```bash
scancel <JOB_ID>

# Cancel all your jobs
scancel -u $USER
```

## Expected Results

### QUIK
- **1 GPU**: Baseline performance
- **2 GPUs**: Similar runtime to 1 GPU (no parallelization, overhead from multiple GPU allocation)
- **4 GPUs**: Similar or slower than 1 GPU (more overhead)
- **4_7_mer vs 4_mer**: 4_7_mer should be slightly slower but potentially more accurate

### RandomBarcodes
- **1 GPU**: Baseline performance
- **2 GPUs**: ~2× speedup (task-level parallelism via chunking)
- **4 GPUs**: ~4× speedup (task-level parallelism via chunking)
- **ntriage=100 vs 5000**: Smaller triage = faster but potentially less accurate

### Columba
- **1 CPU**: Baseline performance
- **2 CPUs**: ~1.5-2× speedup (alignment threading)
- **4 CPUs**: ~2-3× speedup (alignment threading with overhead)

## Analyzing Results

After all jobs complete, analyze the results using:

```bash
cd /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark

# Aggregate all runtime benchmark results
python bin/aggregate_runtime_results.py \
    results_runtime/ \
    runtime_benchmark_summary.csv
```

This will create a summary CSV with:
- Tool, configuration, resources
- Precision, recall, F1
- Total time, time per read
- Peak memory usage
- Speedup factor (compared to baseline)

## Troubleshooting

### Job fails with "Out of Memory"
- Increase `--mem` in job script (currently 32G)
- Check Nextflow trace to see actual peak memory

### Job times out
- Increase `--time` in job script
- Check if pipeline is actually running (not stuck in queue)

### QUIK compilation errors
- Check CUDA module is loaded correctly
- Verify `cmake` and `nvcc` are available in job logs

### Columba alignment errors
- Verify `columba_repo` path exists: `/user/gent/446/vsc44685/ScratchVO_dir/columba`
- Check that Columba was built correctly in the repository

### Nextflow session locks
- Each job uses isolated work directories to prevent conflicts
- If lock errors occur, check that `WORK_DIR` paths are unique

## Notes

- **QUIK Compilation**: QUIK is compiled from source each time (takes ~1-2 minutes per run)
- **Nextflow Caching**: `-resume` flag enables caching, but each job uses isolated work directories
- **Memory Reporting**: Peak memory is automatically captured in `trace.txt` by Nextflow
- **GPU Visibility**: Slurm `--gres=gpu:N` ensures proper GPU isolation
- **CPU Threading**: Columba uses `-t` parameter (set via `cpus` in params file)

## Questions or Issues?

Contact: Franco Alexander Poma Soto
Project: Barcode Calling Benchmarking Pipeline
Location: `/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark`
