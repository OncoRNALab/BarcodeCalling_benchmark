#!/usr/bin/env python3
"""
Generate parameter sweep for RandomBarcodes optimization
Creates parameter files and job scripts for all combinations of ntriage and nthresh
"""

import json
import os
from pathlib import Path
from itertools import product

# Configuration
BASE_CONFIG = {
    "barcode_file": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/barcodes_21K_28_subset1",
    "r1_fastq": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/reads_21K_28_low_R1.fastq",
    "r2_fastq": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/reads_21K_28_low_R2.fastq",
    "ground_truth": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/answers_21K_28_low",
    "barcode_length": 28,
    "n_barcodes": 21000,
    "gpus": 4,  # Number of GPUs to use
    "tool": "randombarcodes"
}

# Parameter ranges
NTRIAGE_VALUES = [100, 1000, 2000, 5000, 10000]
NTHRESH_VALUES = [5, 6, 7, 8, 9, 10]

# Directories
OUTPUT_BASE = "/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/randombarcodes_sweep"
PARAMS_DIR = Path("./parameter_sweep/params")
JOBS_DIR = Path("./parameter_sweep/jobs")

# Job template
# Note: This wrapper job runs Nextflow, which submits separate Slurm jobs for each process.
# GPU resources are requested by the RANDOMBARCODES process via clusterOptions in slurm.config.
# This wrapper only needs minimal resources to orchestrate the pipeline.
JOB_TEMPLATE = """#!/bin/bash
#SBATCH -J RB_t{ntriage}_n{nthresh}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=24:00:00
#SBATCH --mem=8G
#SBATCH --output={log_dir}/RB_t{ntriage}_n{nthresh}.out
#SBATCH --error={log_dir}/RB_t{ntriage}_n{nthresh}.err

# Environment setup
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_sweep/t{ntriage}_n{nthresh}"

# Create and move to unique work directory for this job to avoid lock conflicts
# This ensures each run has its own .nextflow metadata folder
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Run pipeline
nextflow run "$PROJECT_DIR/main.nf" \\
    -c "$PROJECT_DIR/nextflow.config" \\
    -profile slurm \\
    -params-file {params_file} \\
    -work-dir "$WORK_DIR" \\
    -resume

echo "Job completed for ntriage={ntriage}, nthresh={nthresh}"
"""


def create_directories():
    """Create output directories"""
    PARAMS_DIR.mkdir(parents=True, exist_ok=True)
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    
    log_dir = Path("./parameter_sweep/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    return log_dir


def generate_param_file(ntriage, nthresh, output_dir):
    """Generate a parameter JSON file for a specific combination"""
    params = BASE_CONFIG.copy()
    params["ntriage"] = ntriage
    params["nthresh"] = nthresh
    params["sample_id"] = f"RB_t{ntriage}_n{nthresh}"
    params["outdir"] = f"{output_dir}/t{ntriage}_n{nthresh}"
    
    filename = PARAMS_DIR / f"params_t{ntriage}_n{nthresh}.json"
    with open(filename, 'w') as f:
        json.dump(params, f, indent=2)
    
    return filename


def generate_job_script(ntriage, nthresh, params_file, log_dir):
    """Generate a Slurm job script for a specific combination"""
    job_content = JOB_TEMPLATE.format(
        ntriage=ntriage,
        nthresh=nthresh,
        params_file=params_file.absolute(),
        log_dir=log_dir.absolute()
    )
    
    job_file = JOBS_DIR / f"job_t{ntriage}_n{nthresh}.sh"
    with open(job_file, 'w') as f:
        f.write(job_content)
    
    # Make executable
    job_file.chmod(0o755)
    
    return job_file


def generate_submission_script(job_files):
    """Generate a master script to submit all jobs"""
    submit_script = Path("./parameter_sweep/submit_all.sh")
    
    with open(submit_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Submit all parameter sweep jobs\n\n")
        f.write("echo 'Submitting {} jobs...'\n\n".format(len(job_files)))
        
        for job_file in sorted(job_files):
            f.write(f"echo 'Submitting {job_file.name}'\n")
            f.write(f"sbatch {job_file.absolute()}\n")
            f.write("sleep 1  # Avoid overwhelming scheduler\n\n")
        
        f.write("echo 'All jobs submitted!'\n")
        f.write("echo 'Monitor with: squeue -u $USER'\n")
    
    submit_script.chmod(0o755)
    return submit_script


def generate_analysis_script():
    """Generate a script to analyze results from all runs"""
    analysis_script = Path("./parameter_sweep/analyze_results.py")
    
    analysis_code = """#!/usr/bin/env python3
\"\"\"
Analyze results from RandomBarcodes parameter sweep
Collects precision/recall metrics from all runs
\"\"\"

import pandas as pd
import json
from pathlib import Path
import re

# Configuration
RESULTS_BASE = "{output_base}"

def extract_metrics(result_dir):
    \"\"\"Extract metrics from a single run\"\"\"
    summary_file = result_dir / "precision_summary.csv"
    
    if not summary_file.exists():
        return None
    
    df = pd.read_csv(summary_file)
    return df.iloc[0].to_dict()

def parse_run_name(dirname):
    \"\"\"Extract ntriage and nthresh from directory name\"\"\"
    match = re.search(r't(\\d+)_n(\\d+)', dirname)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def main():
    results_path = Path(RESULTS_BASE)
    
    if not results_path.exists():
        print(f"Results directory not found: {{results_path}}")
        return
    
    all_results = []
    
    # Iterate through all result directories
    for run_dir in results_path.iterdir():
        if not run_dir.is_dir():
            continue
        
        ntriage, nthresh = parse_run_name(run_dir.name)
        if ntriage is None:
            continue
        
        # Look for precision summary in subdirectory
        sample_dirs = list(run_dir.glob("RB_t*_n*"))
        if not sample_dirs:
            continue
        
        sample_dir = sample_dirs[0]
        metrics = extract_metrics(sample_dir)
        
        if metrics:
            metrics['ntriage'] = ntriage
            metrics['nthresh'] = nthresh
            all_results.append(metrics)
    
    if not all_results:
        print("No results found!")
        return
    
    # Create DataFrame
    df = pd.DataFrame(all_results)
    
    # Sort by ntriage and nthresh
    df = df.sort_values(['ntriage', 'nthresh'])
    
    # Save to CSV
    output_file = Path("./parameter_sweep/sweep_results.csv")
    df.to_csv(output_file, index=False)
    print(f"Results saved to: {{output_file}}")
    
    # Print summary
    print("\\n" + "="*80)
    print("PARAMETER SWEEP RESULTS")
    print("="*80)
    print(df.to_string(index=False))
    
    # Find best parameters
    print("\\n" + "="*80)
    print("BEST PARAMETERS")
    print("="*80)
    
    if 'precision' in df.columns:
        best_precision = df.loc[df['precision'].idxmax()]
        print(f"\\nBest Precision: {{best_precision['precision']:.4f}}")
        print(f"  ntriage: {{int(best_precision['ntriage'])}}")
        print(f"  nthresh: {{int(best_precision['nthresh'])}}")
    
    if 'recall' in df.columns:
        best_recall = df.loc[df['recall'].idxmax()]
        print(f"\\nBest Recall: {{best_recall['recall']:.4f}}")
        print(f"  ntriage: {{int(best_recall['ntriage'])}}")
        print(f"  nthresh: {{int(best_recall['nthresh'])}}")
    
    if 'f1_score' in df.columns:
        best_f1 = df.loc[df['f1_score'].idxmax()]
        print(f"\\nBest F1 Score: {{best_f1['f1_score']:.4f}}")
        print(f"  ntriage: {{int(best_f1['ntriage'])}}")
        print(f"  nthresh: {{int(best_f1['nthresh'])}}")
    
    print("\\n" + "="*80)

if __name__ == "__main__":
    main()
""".format(output_base=OUTPUT_BASE)
    
    with open(analysis_script, 'w') as f:
        f.write(analysis_code)
    
    analysis_script.chmod(0o755)
    return analysis_script


def generate_summary_table():
    """Generate a template for results summary"""
    readme = Path("./parameter_sweep/README.md")
    
    readme_content = f"""# RandomBarcodes Parameter Sweep

## Overview

Testing {len(NTRIAGE_VALUES)} × {len(NTHRESH_VALUES)} = {len(NTRIAGE_VALUES) * len(NTHRESH_VALUES)} parameter combinations

**Parameters:**
- `ntriage`: {NTRIAGE_VALUES}
- `nthresh`: {NTHRESH_VALUES}

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
{OUTPUT_BASE}/
├── t100_n5/
│   └── RB_t100_n5/
│       ├── precision_summary.csv
│       └── ...
├── t100_n6/
└── ...
```

## Expected Runtime

- Per job: ~30 minutes to 2 hours (depends on parameters)
- Total: ~{len(NTRIAGE_VALUES) * len(NTHRESH_VALUES)} jobs
- Wall time per job: 4 hours (with buffer)

## Tips

- Each job uses a unique work directory to avoid lock conflicts
- Check `parameter_sweep/logs/` for job-specific output
- Use `analyze_results.py` to get comprehensive comparison
"""
    
    with open(readme, 'w') as f:
        f.write(readme_content)
    
    return readme


def main():
    print("RandomBarcodes Parameter Sweep Generator")
    print("=" * 60)
    
    # Create directories
    log_dir = create_directories()
    print(f"✓ Created directories")
    
    # Generate all combinations
    combinations = list(product(NTRIAGE_VALUES, NTHRESH_VALUES))
    print(f"✓ Will generate {len(combinations)} parameter combinations")
    
    job_files = []
    
    for ntriage, nthresh in combinations:
        # Generate parameter file
        param_file = generate_param_file(ntriage, nthresh, OUTPUT_BASE)
        
        # Generate job script
        job_file = generate_job_script(ntriage, nthresh, param_file, log_dir)
        job_files.append(job_file)
    
    print(f"✓ Generated {len(job_files)} parameter files and job scripts")
    
    # Generate submission script
    submit_script = generate_submission_script(job_files)
    print(f"✓ Created submission script: {submit_script}")
    
    # Generate analysis script
    analysis_script = generate_analysis_script()
    print(f"✓ Created analysis script: {analysis_script}")
    
    # Generate README
    readme = generate_summary_table()
    print(f"✓ Created README: {readme}")
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print(f"  1. Review parameter files in: {PARAMS_DIR}")
    print(f"  2. Review job scripts in: {JOBS_DIR}")
    print(f"  3. Submit all jobs: {submit_script}")
    print(f"  4. Monitor: squeue -u $USER")
    print(f"  5. Analyze results: {analysis_script}")
    print("\n")


if __name__ == "__main__":
    main()

