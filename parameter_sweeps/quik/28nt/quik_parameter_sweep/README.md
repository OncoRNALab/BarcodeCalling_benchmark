# QUIK Parameter Sweep

## Overview

Testing 3 strategies × 6 rejection thresholds = 18 parameter combinations

**Parameters:**
- `strategy`: ['4_mer_gpu_v4', '4_7_mer_gpu_v1', '7_7_mer_gpu_v1']
  - `4_mer_gpu_v4`: 4-mer filtering
  - `4_7_mer_gpu_v1`: 4-mer then 7-mer refinement (default)
  - `7_7_mer_gpu_v1`: 7-mer only
- `rejection_threshold`: [5, 6, 7, 8, 9, 10]

**Test Data:**
- Barcodes: 21,000+ (28 nt)
- Reads: Low coverage dataset
- Distance measure: SEQUENCE_LEVENSHTEIN
- Barcode start: 0

## Usage

1. **Generate all files:**
   ```bash
   python quik_parameter_sweep/generate_sweep.py
   ```

2. **Submit all jobs:**
   ```bash
   ./quik_parameter_sweep/submit_all.sh
   ```

3. **Monitor jobs:**
   ```bash
   squeue -u $USER
   watch -n 30 'squeue -u $USER'
   ```

4. **Analyze results:**
   ```bash
   python quik_parameter_sweep/analyze_results.py
   ```

## Directory Structure

```
quik_parameter_sweep/
├── params/           # Parameter files (JSON)
│   ├── params_4mer_r5.json
│   ├── params_4mer_r6.json
│   ├── params_47mer_r5.json
│   ├── params_77mer_r5.json
│   └── ...
├── jobs/             # Job scripts (Slurm)
│   ├── job_4mer_r5.sh
│   ├── job_4mer_r6.sh
│   └── ...
├── logs/             # Job output/error logs
│   ├── QUIK_4mer_r5.out
│   ├── QUIK_4mer_r5.err
│   └── ...
├── generate_sweep.py # This script
├── submit_all.sh     # Submit all jobs
├── analyze_results.py # Analyze results
└── README.md         # This file
```

## Results Location

All results will be stored in:
```
/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/quik_sweep/
├── 4mer_r5/
│   └── QUIK_4mer_r5/
│       ├── precision_summary.csv
│       └── ...
├── 4mer_r6/
├── 47mer_r5/
├── 77mer_r5/
└── ...
```

## Expected Runtime

- Per job: ~30 minutes to 2 hours (depends on parameters)
- Total: ~18 jobs
- Wall time per job: 5 hours (with buffer)

## Comparison with RandomBarcodes

This sweep uses the same rejection thresholds (5-10) as the RandomBarcodes sweep for fair comparison:
- RandomBarcodes: `nthresh` parameter
- QUIK: `rejection_threshold` parameter

Both represent maximum edit distance for barcode assignment.

## Tips

- Each job uses a unique work directory to avoid lock conflicts
- Check `quik_parameter_sweep/logs/` for job-specific output
- Use `analyze_results.py` to get comprehensive comparison
- GPU required for all QUIK strategies
