#!/usr/bin/env python3
"""
Generate parameter sweep for QUIK optimization
Creates parameter files and job scripts for all combinations of strategy and rejection_threshold
"""

import json
import os
from pathlib import Path
from itertools import product

# Configuration
BASE_CONFIG = {
    "tool": "quik",
    "barcode_file": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/barcodes_21K_28_subset1",
    "r1_fastq": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/reads_21K_28_low_R1.fastq",
    "r2_fastq": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/reads_21K_28_low_R2.fastq",
    "ground_truth": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/answers_21K_28_low",
    "barcode_length": 28,
    "barcode_start": 0,
    "distance_measure": "SEQUENCE_LEVENSHTEIN"
}

# Parameter ranges
STRATEGIES = {
    "4mer": "4_mer_gpu_v4",
    "47mer": "4_7_mer_gpu_v1",
    "77mer": "7_7_mer_gpu_v1"
}
REJECTION_THRESHOLDS = [5, 6, 7, 8, 9, 10]

# Directories
OUTPUT_BASE = "/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/quik_sweep"
PARAMS_DIR = Path("./quik_parameter_sweep/params")
JOBS_DIR = Path("./quik_parameter_sweep/jobs")

# Job template
JOB_TEMPLATE = """#!/bin/bash
#SBATCH -J QUIK_{strategy_short}_r{rejection_threshold}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=24:00:00
#SBATCH --mem=8G
#SBATCH --output={log_dir}/QUIK_{strategy_short}_r{rejection_threshold}.out
#SBATCH --error={log_dir}/QUIK_{strategy_short}_r{rejection_threshold}.err

# Environment setup
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_quik_sweep/{strategy_short}_r{rejection_threshold}"

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

echo "Job completed for strategy={strategy}, rejection_threshold={rejection_threshold}"
"""


def create_directories():
    """Create output directories"""
    PARAMS_DIR.mkdir(parents=True, exist_ok=True)
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    
    log_dir = Path("./quik_parameter_sweep/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    return log_dir


def generate_param_file(strategy_short, strategy_full, rejection_threshold, output_dir):
    """Generate a parameter JSON file for a specific combination"""
    params = BASE_CONFIG.copy()
    params["strategy"] = strategy_full
    params["rejection_threshold"] = rejection_threshold
    params["sample_id"] = f"QUIK_{strategy_short}_r{rejection_threshold}"
    params["outdir"] = f"{output_dir}/{strategy_short}_r{rejection_threshold}"
    
    filename = PARAMS_DIR / f"params_{strategy_short}_r{rejection_threshold}.json"
    with open(filename, 'w') as f:
        json.dump(params, f, indent=2)
    
    return filename


def generate_job_script(strategy_short, strategy_full, rejection_threshold, params_file, log_dir):
    """Generate a Slurm job script for a specific combination"""
    job_content = JOB_TEMPLATE.format(
        strategy_short=strategy_short,
        strategy=strategy_full,
        rejection_threshold=rejection_threshold,
        params_file=params_file.absolute(),
        log_dir=log_dir.absolute()
    )
    
    job_file = JOBS_DIR / f"job_{strategy_short}_r{rejection_threshold}.sh"
    with open(job_file, 'w') as f:
        f.write(job_content)
    
    # Make executable
    job_file.chmod(0o755)
    
    return job_file


def generate_submission_script(job_files):
    """Generate a master script to submit all jobs"""
    submit_script = Path("./quik_parameter_sweep/submit_all.sh")
    
    with open(submit_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Submit all QUIK parameter sweep jobs\n\n")
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
    analysis_script = Path("./quik_parameter_sweep/analyze_results.py")
    
    # Use triple quotes with proper escaping
    analysis_code = f"""#!/usr/bin/env python3
\"\"\"
Analyze results from QUIK parameter sweep
Collects precision/recall metrics from all runs
\"\"\"

import pandas as pd
import json
from pathlib import Path
import re

# Configuration
RESULTS_BASE = "{OUTPUT_BASE}"

def extract_metrics(result_dir):
    \"\"\"Extract metrics from a single run\"\"\"
    summary_file = result_dir / "precision_summary.csv"
    
    if not summary_file.exists():
        return None
    
    df = pd.read_csv(summary_file)
    return df.iloc[0].to_dict()

def parse_run_name(dirname):
    \"\"\"Extract strategy and rejection_threshold from directory name\"\"\"
    match = re.search(r'(\\w+)_r(\\d+)', dirname)
    if match:
        return match.group(1), int(match.group(2))
    return None, None

def main():
    results_path = Path(RESULTS_BASE)
    
    if not results_path.exists():
        print(f"Results directory not found: {{{{results_path}}}}")
        return
    
    all_results = []
    
    # Iterate through all result directories
    for run_dir in results_path.iterdir():
        if not run_dir.is_dir():
            continue
        
        strategy_short, rejection_threshold = parse_run_name(run_dir.name)
        if strategy_short is None:
            continue
        
        # Look for precision summary in subdirectory
        sample_dirs = list(run_dir.glob("QUIK_*"))
        if not sample_dirs:
            continue
        
        sample_dir = sample_dirs[0]
        metrics = extract_metrics(sample_dir)
        
        if metrics:
            metrics['strategy'] = strategy_short
            metrics['rejection_threshold'] = rejection_threshold
            all_results.append(metrics)
    
    if not all_results:
        print("No results found!")
        return
    
    # Create DataFrame
    df = pd.DataFrame(all_results)
    
    # Sort by strategy and rejection_threshold
    df = df.sort_values(['strategy', 'rejection_threshold'])
    
    # Save to CSV
    output_file = Path("./quik_parameter_sweep/sweep_results.csv")
    df.to_csv(output_file, index=False)
    print(f"Results saved to: {{{{output_file}}}}")
    
    # Print summary
    print("\\n" + "="*80)
    print("QUIK PARAMETER SWEEP RESULTS")
    print("="*80)
    print(df.to_string(index=False))
    
    # Find best parameters for each strategy
    print("\\n" + "="*80)
    print("BEST PARAMETERS BY STRATEGY")
    print("="*80)
    
    for strategy in df['strategy'].unique():
        strategy_df = df[df['strategy'] == strategy]
        print(f"\\n=== Strategy: {{{{strategy}}}} ===")
        
        if 'precision' in df.columns:
            best_precision = strategy_df.loc[strategy_df['precision'].idxmax()]
            print(f"Best Precision: {{{{best_precision['precision']:.4f}}}} @ rejection_threshold={{{{int(best_precision['rejection_threshold'])}}}}")
        
        if 'recall' in df.columns:
            best_recall = strategy_df.loc[strategy_df['recall'].idxmax()]
            print(f"Best Recall: {{{{best_recall['recall']:.4f}}}} @ rejection_threshold={{{{int(best_recall['rejection_threshold'])}}}}")
        
        if 'f1_score' in df.columns:
            best_f1 = strategy_df.loc[strategy_df['f1_score'].idxmax()]
            print(f"Best F1 Score: {{{{best_f1['f1_score']:.4f}}}} @ rejection_threshold={{{{int(best_f1['rejection_threshold'])}}}}")
    
    # Overall best
    print("\\n" + "="*80)
    print("OVERALL BEST PARAMETERS")
    print("="*80)
    
    if 'f1_score' in df.columns:
        best_overall = df.loc[df['f1_score'].idxmax()]
        print(f"\\nBest F1 Score: {{{{best_overall['f1_score']:.4f}}}}")
        print(f"  Strategy: {{{{best_overall['strategy']}}}}")
        print(f"  Rejection Threshold: {{{{int(best_overall['rejection_threshold'])}}}}")
    
    print("\\n" + "="*80)

if __name__ == "__main__":
    main()
"""
    
    with open(analysis_script, 'w') as f:
        f.write(analysis_code)
    
    analysis_script.chmod(0o755)
    return analysis_script


def generate_readme():
    """Generate a README for the parameter sweep"""
    readme = Path("./quik_parameter_sweep/README.md")
    
    readme_content = f"""# QUIK Parameter Sweep

## Overview

Testing {len(STRATEGIES)} strategies × {len(REJECTION_THRESHOLDS)} rejection thresholds = {len(STRATEGIES) * len(REJECTION_THRESHOLDS)} parameter combinations

**Parameters:**
- `strategy`: {list(STRATEGIES.values())}
  - `4_mer_gpu_v4`: 4-mer filtering
  - `4_7_mer_gpu_v1`: 4-mer then 7-mer refinement (default)
  - `7_7_mer_gpu_v1`: 7-mer only
- `rejection_threshold`: {REJECTION_THRESHOLDS}

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
{OUTPUT_BASE}/
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
- Total: ~{len(STRATEGIES) * len(REJECTION_THRESHOLDS)} jobs
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
"""
    
    with open(readme, 'w') as f:
        f.write(readme_content)
    
    return readme


def main():
    print("QUIK Parameter Sweep Generator")
    print("=" * 60)
    
    # Create directories
    log_dir = create_directories()
    print(f"✓ Created directories")
    
    # Generate all combinations
    combinations = []
    for strategy_short, strategy_full in STRATEGIES.items():
        for rejection_threshold in REJECTION_THRESHOLDS:
            combinations.append((strategy_short, strategy_full, rejection_threshold))
    
    print(f"✓ Will generate {len(combinations)} parameter combinations")
    print(f"  - Strategies: {list(STRATEGIES.keys())}")
    print(f"  - Rejection thresholds: {REJECTION_THRESHOLDS}")
    
    job_files = []
    
    for strategy_short, strategy_full, rejection_threshold in combinations:
        # Generate parameter file
        param_file = generate_param_file(strategy_short, strategy_full, rejection_threshold, OUTPUT_BASE)
        
        # Generate job script
        job_file = generate_job_script(strategy_short, strategy_full, rejection_threshold, param_file, log_dir)
        job_files.append(job_file)
    
    print(f"✓ Generated {len(job_files)} parameter files and job scripts")
    
    # Generate submission script
    submit_script = generate_submission_script(job_files)
    print(f"✓ Created submission script: {submit_script}")
    
    # Generate analysis script
    analysis_script = generate_analysis_script()
    print(f"✓ Created analysis script: {analysis_script}")
    
    # Generate README
    readme = generate_readme()
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

