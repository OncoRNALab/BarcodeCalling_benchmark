# Parameter Sweeps Directory

This directory contains organized parameter sweeps for all three barcode calling tools, tested with both 28nt and 36nt barcodes.

## Directory Structure

```
parameter_sweeps/
├── randombarcodes/
│   ├── 28nt/              # 28-nucleotide barcode parameter sweep
│   │   └── parameter_sweep/
│   │       ├── params/    # Parameter JSON files
│   │       ├── jobs/      # SLURM job scripts
│   │       ├── logs/      # Job output logs
│   │       ├── generate_sweep.py
│   │       └── submit_all.sh
│   └── 36nt/              # 36-nucleotide barcode parameter sweep
│       ├── params/
│       ├── jobs/
│       ├── logs/
│       ├── generate_sweep.py
│       └── submit_all.sh
├── quik/
│   ├── 28nt/
│   │   └── quik_parameter_sweep/
│   │       ├── params/
│   │       ├── jobs/
│   │       ├── logs/
│   │       ├── generate_sweep.py
│   │       └── submit_all.sh
│   └── 36nt/
│       ├── params/
│       ├── jobs/
│       ├── logs/
│       ├── generate_sweep.py
│       └── submit_all.sh
└── columba/
    ├── 28nt/
    │   └── columba_parameter_sweep/
    │       ├── params/
    │       ├── jobs/
    │       ├── logs/
    │       ├── generate_sweep.py
    │       └── submit_all.sh
    └── 36nt/
        ├── params/
        ├── jobs/
        ├── logs/
        ├── generate_sweep.py
        └── submit_all.sh
```

## Parameter Sweep Configurations

### RandomBarcodes
- **28nt:** 30 configurations (5 ntriage × 6 nthresh)
  - ntriage: [100, 1000, 2000, 5000, 10000]
  - nthresh: [5, 6, 7, 8, 9, 10]
- **36nt:** 30 configurations (same parameters)

### QUIK
- **28nt:** 18 configurations (3 strategies × 6 rejection thresholds)
  - strategies: [4mer, 47mer, 77mer]
  - rejection_threshold: [5, 6, 7, 8, 9, 10]
- **36nt:** 18 configurations (same parameters)

### Columba
- **28nt:** 5 configurations
  - identity_threshold: [72, 75, 77, 80, 83]
- **36nt:** 5 configurations (same parameters)

**Total: 106 configurations** (53 for 28nt + 53 for 36nt)

## Dataset Information

### 28nt Barcodes
- **Location:** `/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_28nt/`
- **Reads:** 200,000
- **Barcodes:** 21,000
- **Length:** 28 nucleotides

### 36nt Barcodes
- **Location:** `/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_36nt/`
- **Reads:** 200,000
- **Barcodes:** 21,000
- **Length:** 36 nucleotides

## Usage

### To submit all jobs for a specific tool and barcode length:

```bash
# RandomBarcodes 28nt
cd parameter_sweeps/randombarcodes/28nt/parameter_sweep
./submit_all.sh

# RandomBarcodes 36nt
cd parameter_sweeps/randombarcodes/36nt
./submit_all.sh

# QUIK 28nt
cd parameter_sweeps/quik/28nt/quik_parameter_sweep
./submit_all.sh

# QUIK 36nt
cd parameter_sweeps/quik/36nt
./submit_all.sh

# Columba 28nt
cd parameter_sweeps/columba/28nt/columba_parameter_sweep
./submit_all.sh

# Columba 36nt
cd parameter_sweeps/columba/36nt
./submit_all.sh
```

### To submit individual jobs:

```bash
# Navigate to the jobs directory
cd parameter_sweeps/<tool>/<barcode_length>/jobs/

# Submit specific job
sbatch job_<parameters>.sh
```

### To monitor jobs:

```bash
squeue -u $USER
```

## Results Organization

Results are organized by barcode length:

- **28nt results:** `/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/`
  - `randombarcodes_sweep/`
  - `quik_sweep/`
  - `columba_sweep/`

- **36nt results:** `/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_36nt/`
  - `randombarcodes_sweep/`
  - `quik_sweep/`
  - `columba_sweep/`

## Work Directories

Temporary work directories are isolated per job to avoid Nextflow session conflicts:

- **28nt:** `/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_sweep/`
- **36nt:** `/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_sweep_36nt/`

## Notes

1. **Job Isolation:** Each job runs in its own work directory to prevent Nextflow session lock conflicts
2. **Resume Support:** All jobs use `-resume` flag to allow restarting from checkpoints
3. **Resource Allocation:** 
   - RandomBarcodes & QUIK: 1 CPU, 8GB RAM, 24h walltime
   - Columba: 16 CPUs, 32GB RAM, 24h walltime
4. **Scheduler:** All jobs use Slurm (`-profile slurm`)

## Regenerating Sweep Files

If you need to modify parameters and regenerate:

```bash
cd parameter_sweeps/<tool>/<barcode_length>/
python generate_sweep.py
```

This will recreate all parameter files, job scripts, and submission scripts.
