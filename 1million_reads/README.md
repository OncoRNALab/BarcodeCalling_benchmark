# 1 Million Reads Benchmark

This directory contains job submission scripts and parameter files for benchmarking barcode calling tools on 1 million read datasets.

## Overview

This benchmark compares three barcode calling tools:
- **RandomBarcodes** - GPU-based barcode calling
- **QUIK** - GPU-based barcode calling with k-mer strategies
- **Columba** - CPU-based alignment-based barcode calling

Each tool is tested on three datasets with different barcode counts:
- **21K barcodes** - 21,000 unique barcodes
- **42K barcodes** - 42,000 unique barcodes
- **85K barcodes** - 85,000 unique barcodes

All datasets contain **1 million reads** (36nt barcodes) with medium error rate.

## Directory Structure

```
1million_reads/
├── jobs/               # SLURM job submission scripts
│   ├── randombarcodes_21K.sh
│   ├── randombarcodes_42K.sh
│   ├── randombarcodes_85K.sh
│   ├── quik_21K.sh
│   ├── quik_42K.sh
│   ├── quik_85K.sh
│   ├── columba_21K.sh
│   ├── columba_42K.sh
│   └── columba_85K.sh
├── params/            # Parameter JSON files for each run
│   ├── randombarcodes_21K.json
│   ├── randombarcodes_42K.json
│   ├── randombarcodes_85K.json
│   ├── quik_21K.json
│   ├── quik_42K.json
│   ├── quik_85K.json
│   ├── columba_21K.json
│   ├── columba_42K.json
│   └── columba_85K.json
├── logs/              # Job output and error logs
├── submit_all_1M_benchmarks.sh  # Master submission script
└── README.md          # This file
```

## Parameters

### RandomBarcodes
- `nthresh`: 9
- `ntriage`: 100
- `gpus`: 1
- Memory: 16G
- Time: 12 hours

### QUIK
- `strategy`: 4_mer_gpu_v4
- `rejection_threshold`: 8
- `gpus`: 1
- Memory: 16G
- Time: 24 hours

### Columba
- `identity_threshold`: 80
- `barcode_window`: 0-36
- `cpus`: 16
- Memory: 64G
- Time: 12 hours

## Input Data

All input datasets are located in:
```
/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/
```

Each dataset contains:
- `reads_*_R1.fastq` - Forward reads
- `reads_*_R2.fastq` - Reverse reads
- `barcodes_*` - Barcode reference file
- `answers_*` - Ground truth barcode assignments

## Output Data

Results will be saved to:
```
/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_1million_reads/
```

Each run will have its own subdirectory:
- `randombarcodes_21K/`
- `randombarcodes_42K/`
- `randombarcodes_85K/`
- `quik_21K/`
- `quik_42K/`
- `quik_85K/`
- `columba_21K/`
- `columba_42K/`
- `columba_85K/`

## Usage

### Submit All Jobs

To submit all 9 benchmark jobs at once:

```bash
bash submit_all_1M_benchmarks.sh
```

### Submit Individual Jobs

To submit a specific job:

```bash
sbatch jobs/randombarcodes_42K.sh
sbatch jobs/quik_42K.sh
sbatch jobs/columba_42K.sh
```

### Monitor Jobs

Check job status:
```bash
squeue -u $USER
```

View live logs:
```bash
tail -f logs/RB_42K_1M.out
tail -f logs/QK_42K_1M.out
tail -f logs/CB_42K_1M.out
```

### Check Results

After jobs complete, check the output directories for:
- Filtered FASTQ files (RandomBarcodes, QUIK)
- SAM alignment files (Columba)
- Precision/recall reports
- Summary CSV files with metrics

## Expected Runtime

Based on 200K read benchmarks (scaled to 1M reads):

- **RandomBarcodes**: ~4-8 hours
- **QUIK**: ~10-20 hours
- **Columba**: ~6-10 hours

Times may vary depending on system load and barcode count.

## Notes

- All jobs use unique work directories to avoid Nextflow lock conflicts
- Jobs can be resumed with `-resume` flag if interrupted
- GPU allocation is handled by Nextflow based on tool requirements
- No manual GPU allocation in SLURM directives (as per specifications)

## Troubleshooting

If a job fails:

1. Check the error log in `logs/`
2. Review the Nextflow work directory for detailed process logs
3. Resume the job with the same submission script (uses `-resume`)
4. Contact the administrator if issues persist

## Contact

For questions or issues, refer to the main BarCall_benchmark README or contact the project maintainer.
