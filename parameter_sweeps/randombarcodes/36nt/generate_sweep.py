#!/usr/bin/env python3
"""
Generate RandomBarcodes parameter sweep for 36nt barcodes
Creates parameter files and job scripts for different ntriage and nthresh combinations
"""

import os
import json
from pathlib import Path

# Output directories
SCRIPT_DIR = Path(__file__).parent
PARAMS_DIR = SCRIPT_DIR / "params"
JOBS_DIR = SCRIPT_DIR / "jobs"
LOGS_DIR = SCRIPT_DIR / "logs"

# Create directories
PARAMS_DIR.mkdir(exist_ok=True)
JOBS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Base configuration for 36nt barcodes
BASE_CONFIG = {
    "barcode_file": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_36nt/barcodes_21K_36_subset1",
    "r1_fastq": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_36nt/reads_21K_36_low_R1.fastq",
    "r2_fastq": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_36nt/reads_21K_36_low_R2.fastq",
    "ground_truth": "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_36nt/answers_21K_36_low",
    "barcode_length": 36,
    "n_barcodes": 21000,
    "gpus": 1,
    "tool": "randombarcodes"
}

# Parameter sweep ranges
NTRIAGE_VALUES = [100, 1000, 2000, 5000, 10000]
NTHRESH_VALUES = [5, 6, 7, 8, 9, 10]

# Job template with Slurm headers
JOB_TEMPLATE = """#!/bin/bash
#SBATCH -J RB36_t{ntriage}_n{nthresh}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=24:00:00
#SBATCH --mem=8G
#SBATCH --output={log_dir}/RB36_t{ntriage}_n{nthresh}.out
#SBATCH --error={log_dir}/RB36_t{ntriage}_n{nthresh}.err

# Load Nextflow module
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_sweep_36nt/randombarcodes/t{ntriage}_n{nthresh}"

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

echo "Job completed for ntriage={ntriage}, nthresh={nthresh}"
"""

def generate_parameter_files():
    """Generate parameter JSON files for each combination"""
    configs = []
    
    for ntriage in NTRIAGE_VALUES:
        for nthresh in NTHRESH_VALUES:
            # Create config for this combination
            config = BASE_CONFIG.copy()
            config["ntriage"] = ntriage
            config["nthresh"] = nthresh
            config["sample_id"] = f"RB36_t{ntriage}_n{nthresh}"
            config["outdir"] = f"/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_36nt/randombarcodes_sweep/t{ntriage}_n{nthresh}"
            
            # Write parameter file
            params_file = PARAMS_DIR / f"params_t{ntriage}_n{nthresh}.json"
            with open(params_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            configs.append({
                'ntriage': ntriage,
                'nthresh': nthresh,
                'params_file': str(params_file.absolute()),
                'sample_id': config['sample_id']
            })
            
            print(f"Created parameter file: {params_file.name}")
    
    return configs

def generate_job_scripts(configs):
    """Generate job scripts for each configuration"""
    for config in configs:
        job_file = JOBS_DIR / f"job_t{config['ntriage']}_n{config['nthresh']}.sh"
        
        job_content = JOB_TEMPLATE.format(
            ntriage=config['ntriage'],
            nthresh=config['nthresh'],
            params_file=config['params_file'],
            log_dir=str(LOGS_DIR.absolute())
        )
        
        with open(job_file, 'w') as f:
            f.write(job_content)
        
        # Make executable
        os.chmod(job_file, 0o755)
        
        print(f"Created job script: {job_file.name}")

def generate_submit_script(configs):
    """Generate script to submit all jobs"""
    submit_file = SCRIPT_DIR / "submit_all.sh"
    
    submit_content = """#!/bin/bash
# Submit all RandomBarcodes 36nt parameter sweep jobs

echo 'Submitting {} jobs...'

for job_file in $(ls -v {}/job_*.sh); do
    echo "Submitting $(basename "$job_file")"
    sbatch "$job_file"
    sleep 1  # Avoid overwhelming scheduler
done

echo 'All jobs submitted!'
echo 'Monitor with: squeue -u $USER'
""".format(len(configs), str(JOBS_DIR.absolute()))
    
    with open(submit_file, 'w') as f:
        f.write(submit_content)
    
    os.chmod(submit_file, 0o755)
    print(f"\nCreated submission script: {submit_file.name}")

def main():
    print("="*60)
    print("RandomBarcodes 36nt Parameter Sweep Generator")
    print("="*60)
    print()
    
    print("Generating parameter files...")
    configs = generate_parameter_files()
    print(f"\nGenerated {len(configs)} parameter files")
    
    print("\nGenerating job scripts...")
    generate_job_scripts(configs)
    print(f"\nGenerated {len(configs)} job scripts")
    
    print("\nGenerating submission script...")
    generate_submit_script(configs)
    
    print("\n" + "="*60)
    print("Summary:")
    print(f"  Parameter sweep configurations: {len(configs)}")
    print(f"  Ntriage values: {NTRIAGE_VALUES}")
    print(f"  Nthresh values: {NTHRESH_VALUES}")
    print(f"  Barcode length: 36nt")
    print(f"  Output directory: parameter_sweeps/randombarcodes/36nt/")
    print("="*60)
    print("\nTo submit all jobs, run:")
    print(f"  ./submit_all.sh")
    print("\nOr submit individual jobs from:")
    print(f"  {JOBS_DIR}/")
    print("="*60)

if __name__ == "__main__":
    main()
