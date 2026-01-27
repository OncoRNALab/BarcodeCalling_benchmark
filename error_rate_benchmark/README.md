# Error Rate Benchmark

This directory contains the setup for benchmarking the 3 barcode calling tools (RandomBarcodes, QUIK, Columba) across different error rates.

## Experiment Design

- **Tools**: RandomBarcodes, QUIK, Columba
- **Barcode Counts**: 85K, 42K, 21K
- **Barcode Length**: 36nt
- **Error Rates**: low, medium, high
- **Total Experiments**: 27 (3 tools × 3 barcode counts × 3 error rates)

## Directory Structure

```
error_rate_benchmark/
├── params/              # Parameter JSON files for each experiment
│   ├── randombarcodes_85K_low.json
│   ├── randombarcodes_85K_medium.json
│   ├── randombarcodes_85K_high.json
│   ├── randombarcodes_42K_low.json
│   ├── randombarcodes_42K_medium.json
│   ├── randombarcodes_42K_high.json
│   ├── randombarcodes_21K_low.json
│   ├── randombarcodes_21K_medium.json
│   ├── randombarcodes_21K_high.json
│   ├── quik_85K_low.json
│   ├── quik_85K_medium.json
│   ├── quik_85K_high.json
│   ├── quik_42K_low.json
│   ├── quik_42K_medium.json
│   ├── quik_42K_high.json
│   ├── quik_21K_low.json
│   ├── quik_21K_medium.json
│   ├── quik_21K_high.json
│   ├── columba_85K_low.json
│   ├── columba_85K_medium.json
│   ├── columba_85K_high.json
│   ├── columba_42K_low.json
│   ├── columba_42K_medium.json
│   ├── columba_42K_high.json
│   ├── columba_21K_low.json
│   ├── columba_21K_medium.json
│   └── columba_21K_high.json
├── jobs/                # PBS job submission scripts
│   ├── randombarcodes_*.sh (9 files)
│   ├── quik_*.sh (9 files)
│   └── columba_*.sh (9 files)
├── results/             # Output directory (created by jobs)
├── submit_all_error_rate_benchmarks.sh  # Master submission script
└── README.md            # This file
```

## Tool Parameters

### RandomBarcodes
- Threshold (nthresh): 9
- Ntriage: 100
- GPUs: 2

### QUIK
- Strategy: 4_mer_gpu_v4
- Rejection threshold: 8
- GPUs: 1

### Columba
- Identity threshold: 80%
- CPUs: 16
- No GPU required

## Dataset Information

All datasets use 36nt barcodes with the following barcode counts:
- **85K**: 85,000 barcodes
- **42K**: 42,000 barcodes  
- **21K**: 21,000 barcodes

Error rates (low, medium, high) reflect different sequencing error profiles in the simulated data.

## Usage

### Submit All Jobs
To submit all 27 benchmark jobs at once:

```bash
cd /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/error_rate_benchmark
./submit_all_error_rate_benchmarks.sh
```

### Submit Individual Jobs
To submit a specific job:

```bash
cd /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/error_rate_benchmark
sbatch jobs/randombarcodes_85K_low.sh
```

### Check Job Status
```bash
squeue -u $USER
```

### Monitor Results
Results will be saved in subdirectories under `results/`:
- `results/randombarcodes_85K_36nt_low/`
- `results/quik_42K_36nt_medium/`
- `results/columba_21K_36nt_high/`
- etc.

Each result directory will contain:
- Barcode calling results
- Performance metrics (precision, recall, F1)
- Runtime information
- Log files

Logs for each job are saved in `logs/`:
- `logs/RB_85K_36nt_low.out` / `logs/RB_85K_36nt_low.err`
- `logs/QK_42K_36nt_medium.out` / `logs/QK_42K_36nt_medium.err`
- `logs/CB_21K_36nt_high.out` / `logs/CB_21K_36nt_high.err`
- etc.

## Data Locations

### Input Datasets
- 85K barcodes: `/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_36nt/`
- 42K barcodes: `/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_36nt/`
- 21K barcodes: `/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_36nt/`

### Ground Truth Files
- Located in the same directories as input datasets
- Named as `answers_{size}_{length}_{error}`

## Notes

- Jobs use **SBATCH** (Slurm) job submission system
- Jobs use the **slurm** profile for Nextflow execution
- GPUs are not requested in SBATCH headers; Nextflow handles GPU allocation automatically based on tool parameters
- Each job has a unique work directory to avoid lock conflicts: `/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_error_rate/{tool}/{size}_{error}/`
- Resource allocations per tool:
  - **RandomBarcodes**: 1 CPU, 8GB memory
  - **QUIK**: 1 CPU, 8GB memory
  - **Columba**: 16 CPUs, 32GB memory
- All jobs request 10 hours walltime
- Log files (stdout/stderr) are written to `logs/` directory

## Expected Outputs

Each experiment will generate:
1. **Precision/Recall metrics**: Comparison against ground truth
2. **Runtime statistics**: Execution time for each tool
3. **Resource usage**: Memory and GPU utilization
4. **Quality metrics**: F1 score, accuracy, etc.

This data will be used to analyze how each tool performs under different error conditions.
