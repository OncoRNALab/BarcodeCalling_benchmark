#!/usr/bin/env python3
"""
Generate parameter sweep for Columba optimization
Creates parameter files and job scripts for different identity thresholds
"""

import json
import os
from pathlib import Path

# Configuration
BASE_CONFIG = {
    "tool": "columba",
    "barcode_file": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/barcodes_21K_28_subset1",
    "r1_fastq": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/reads_21K_28_low_R1.fastq",
    "r2_fastq": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/reads_21K_28_low_R2.fastq",
    "ground_truth": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K/21K_28nt/answers_21K_28_low",
    "barcode_length": 28,
    "barcode_window": "0-28",
    "columba_repo": "/user/gent/446/vsc44685/ScratchVO_dir/columba"
}

# Parameter ranges
IDENTITY_THRESHOLDS = [72, 75, 77, 80, 83]

# Directories
OUTPUT_BASE = "/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/columba_sweep"
PARAMS_DIR = Path("./columba_parameter_sweep/params")
JOBS_DIR = Path("./columba_parameter_sweep/jobs")
LOG_DIR = Path("./columba_parameter_sweep/logs")

# Job template
JOB_TEMPLATE = """#!/bin/bash
#SBATCH -J Columba_I{identity_threshold}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --output={log_dir}/Columba_I{identity_threshold}.out
#SBATCH --error={log_dir}/Columba_I{identity_threshold}.err

# Environment setup
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_columba_sweep/I{identity_threshold}"

# Create and move to unique work directory for this job to avoid lock conflicts
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Run pipeline
nextflow run "$PROJECT_DIR/main.nf" \\
    -c "$PROJECT_DIR/nextflow.config" \\
    -profile slurm \\
    -params-file {params_file} \\
    -work-dir "$WORK_DIR" \\
    -resume

echo "Job completed for identity_threshold={identity_threshold}"
"""


def create_directories():
    """Create output directories"""
    PARAMS_DIR.mkdir(parents=True, exist_ok=True)
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def generate_param_file(identity_threshold, output_dir):
    """Generate a parameter JSON file for a specific combination"""
    params = BASE_CONFIG.copy()
    params["identity_threshold"] = identity_threshold
    params["sample_id"] = f"Columba_I{identity_threshold}"
    params["outdir"] = f"{output_dir}/I{identity_threshold}"
    
    filename = PARAMS_DIR / f"params_I{identity_threshold}.json"
    with open(filename, 'w') as f:
        json.dump(params, f, indent=2)
    
    return filename


def generate_job_script(identity_threshold, params_file):
    """Generate a Slurm job script for a specific combination"""
    job_content = JOB_TEMPLATE.format(
        identity_threshold=identity_threshold,
        params_file=params_file.absolute(),
        log_dir=LOG_DIR.absolute()
    )
    
    job_file = JOBS_DIR / f"job_I{identity_threshold}.sh"
    with open(job_file, 'w') as f:
        f.write(job_content)
    
    # Make executable
    job_file.chmod(0o755)
    
    return job_file


def generate_submission_script(job_files):
    """Generate a master script to submit all jobs"""
    submit_script = Path("./columba_parameter_sweep/submit_all.sh")
    
    with open(submit_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Submit all Columba parameter sweep jobs\n\n")
        f.write("echo 'Submitting {} jobs...'\n\n".format(len(job_files)))
        
        for job_file in sorted(job_files):
            f.write(f"echo 'Submitting {job_file.name}'\n")
            f.write(f"sbatch {job_file.absolute()}\n")
            f.write("sleep 1  # Avoid overwhelming scheduler\n\n")
        
        f.write("echo 'All jobs submitted!'\n")
        f.write("echo 'Monitor with: squeue -u $USER'\n")
    
    submit_script.chmod(0o755)
    return submit_script


def main():
    print("Columba Parameter Sweep Generator")
    print("=" * 60)
    
    # Create directories
    create_directories()
    print(f"✓ Created directories")
    
    print(f"✓ Will generate {len(IDENTITY_THRESHOLDS)} parameter combinations")
    print(f"  - Identity thresholds: {IDENTITY_THRESHOLDS}")
    
    job_files = []
    
    for identity_threshold in IDENTITY_THRESHOLDS:
        # Generate parameter file
        param_file = generate_param_file(identity_threshold, OUTPUT_BASE)
        
        # Generate job script
        job_file = generate_job_script(identity_threshold, param_file)
        job_files.append(job_file)
    
    print(f"✓ Generated {len(job_files)} parameter files and job scripts")
    
    # Generate submission script
    submit_script = generate_submission_script(job_files)
    print(f"✓ Created submission script: {submit_script}")
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print(f"  1. Review parameter files in: {PARAMS_DIR}")
    print(f"  2. Review job scripts in: {JOBS_DIR}")
    print(f"  3. Submit all jobs: {submit_script}")
    print(f"  4. Monitor: squeue -u $USER")
    print("\n")


if __name__ == "__main__":
    main()
