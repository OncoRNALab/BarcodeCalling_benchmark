# RandomBarcodes Parameter Sweep

## Overview

Testing 5 × 6 = 30 parameter combinations

**Parameters:**
- `ntriage`: [100, 1000, 2000, 5000, 10000]
- `nthresh`: [5, 6, 7, 8, 9, 10]

**Test Data:**
- Barcodes: 21,504 (28 nt)
- Reads: Low coverage dataset

## Usage

1. **Generate all files:**
   ```bash
   python parameter_sweep/generate_sweep.py
   ```

2. **Submit all jobs:**
   ```bash
   ./parameter_sweep/submit_all.sh
   ```

3. **Monitor jobs:**
   ```bash
   squeue -u $USER
   watch -n 30 'squeue -u $USER'
   ```

4. **Analyze results:**
   ```bash
   python parameter_sweep/analyze_results.py
   ```

## Directory Structure

```
parameter_sweep/
├── params/           # Parameter files (JSON)
│   ├── params_t100_n5.json
│   ├── params_t100_n6.json
│   └── ...
├── jobs/             # Job scripts (Slurm)
│   ├── job_t100_n5.sh
│   ├── job_t100_n6.sh
│   └── ...
├── logs/             # Job output/error logs
│   ├── RB_t100_n5.out
│   ├── RB_t100_n5.err
│   └── ...
├── generate_sweep.py # This script
├── submit_all.sh     # Submit all jobs
├── analyze_results.py # Analyze results
└── README.md         # This file
```

## Results Location

All results will be stored in:
```
/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/randombarcodes_sweep/
├── t100_n5/
│   └── RB_t100_n5/
│       ├── precision_summary.csv
│       └── ...
├── t100_n6/
└── ...
```

## Expected Runtime

- Per job: ~30 minutes to 2 hours (depends on parameters)
- Total: ~30 jobs
- Wall time per job: 4 hours (with buffer)

## Tips

- Each job uses a unique work directory to avoid lock conflicts
- Check `parameter_sweep/logs/` for job-specific output
- Use `analyze_results.py` to get comprehensive comparison
