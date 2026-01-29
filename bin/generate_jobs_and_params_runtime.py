#!/usr/bin/env python3
"""
Generate SLURM job files and parameter JSONs for runtime benchmarks.

Benchmark: Test tool scaling with different resource allocations
Data required: Download benchmark_85K_42K_21K_200K.tar.gz from Zenodo
"""

import json
from pathlib import Path
import argparse


def generate_runtime_benchmark(
    data_dir: Path,
    output_dir: Path,
    results_dir: Path
):
    """Generate jobs and params for runtime benchmark."""
    
    # Configuration from cleaning_prompt.json
    RUNTIME_CONFIGS = {
        'randombarcodes': [
            {'ntriage': 100, 'nthresh': 9, 'gpus': 1, 'name': 't100_1gpu'},
            {'ntriage': 100, 'nthresh': 9, 'gpus': 2, 'name': 't100_2gpu'},
            {'ntriage': 100, 'nthresh': 9, 'gpus': 4, 'name': 't100_4gpu'},
            {'ntriage': 5000, 'nthresh': 9, 'gpus': 1, 'name': 't5000_1gpu'},
            {'ntriage': 5000, 'nthresh': 9, 'gpus': 2, 'name': 't5000_2gpu'},
            {'ntriage': 5000, 'nthresh': 9, 'gpus': 4, 'name': 't5000_4gpu'},
        ],
        'quik': [
            {'strategy': '4_mer_gpu_v4', 'rejection_threshold': 8, 'gpus': 1, 'name': '4mer_1gpu'},
            {'strategy': '4_mer_gpu_v4', 'rejection_threshold': 8, 'gpus': 2, 'name': '4mer_2gpu'},
            {'strategy': '4_mer_gpu_v4', 'rejection_threshold': 8, 'gpus': 4, 'name': '4mer_4gpu'},
            {'strategy': '4_7_mer_gpu_v1', 'rejection_threshold': 8, 'gpus': 1, 'name': '4_7mer_1gpu'},
            {'strategy': '4_7_mer_gpu_v1', 'rejection_threshold': 8, 'gpus': 2, 'name': '4_7mer_2gpu'},
            {'strategy': '4_7_mer_gpu_v1', 'rejection_threshold': 8, 'gpus': 4, 'name': '4_7mer_4gpu'},
        ],
        'columba': [
            {'identity_threshold': 77, 'cpus': 1, 'name': '1cpu'},
            {'identity_threshold': 77, 'cpus': 2, 'name': '2cpu'},
            {'identity_threshold': 77, 'cpus': 4, 'name': '4cpu'},
            {'identity_threshold': 77, 'cpus': 8, 'name': '8cpu'},
            {'identity_threshold': 77, 'cpus': 16, 'name': '16cpu'},
        ]
    }
    
    BARCODE_COUNT = '21K'
    BARCODE_LENGTH = 36
    ERROR_RATE = 'low'
    
    # Data paths
    bc_dir = data_dir / f"{BARCODE_COUNT}_{BARCODE_LENGTH}nt"
    
    print(f"Generating runtime benchmark files...")
    print(f"  Data directory: {data_dir}")
    print(f"  Output directory: {output_dir}")
    print(f"  Results directory: {results_dir}")
    
    for tool, configs in RUNTIME_CONFIGS.items():
        tool_dir = output_dir / tool
        params_dir = tool_dir / 'params'
        jobs_dir = tool_dir / 'jobs'
        logs_dir = tool_dir / 'logs'
        
        params_dir.mkdir(parents=True, exist_ok=True)
        jobs_dir.mkdir(exist_ok=True)
        logs_dir.mkdir(exist_ok=True)
        
        for config in configs:
            config_name = config['name']
            sample_id = f"runtime_{config_name}"
            
            # Create parameter JSON
            params = {
                "tool": tool,
                "barcode_file": str(bc_dir / f"barcodes_{BARCODE_COUNT}_{BARCODE_LENGTH}_subset1"),
                "r1_fastq": str(bc_dir / f"reads_{BARCODE_COUNT}_{BARCODE_LENGTH}_{ERROR_RATE}_R1.fastq"),
                "r2_fastq": str(bc_dir / f"reads_{BARCODE_COUNT}_{BARCODE_LENGTH}_{ERROR_RATE}_R2.fastq"),
                "sample_id": sample_id,
                "barcode_length": BARCODE_LENGTH,
                "outdir": str(results_dir / tool),
                "ground_truth": str(bc_dir / f"answers_{BARCODE_COUNT}_{BARCODE_LENGTH}_{ERROR_RATE}"),
            }
            
            # Add tool-specific runtime parameters
            if tool == 'randombarcodes':
                params.update({
                    "ntriage": config['ntriage'],
                    "nthresh": config['nthresh'],
                    "gpus": config['gpus'],
                    "barcode_start": 0
                })
                resources = f"#SBATCH --gres=gpu:{config['gpus']}\n#SBATCH --cpus-per-task={config['gpus']}\n#SBATCH --mem=16G\n#SBATCH --clusters=joltik,accelgor"
            elif tool == 'quik':
                params.update({
                    "strategy": config['strategy'],
                    "distance_measure": "SEQUENCE_LEVENSHTEIN",
                    "rejection_threshold": config['rejection_threshold'],
                    "gpus": config['gpus'],
                    "barcode_start": 0,
                    "barcode_window": f"0-{BARCODE_LENGTH}"
                })
                resources = f"#SBATCH --gres=gpu:{config['gpus']}\n#SBATCH --cpus-per-task={config['gpus']}\n#SBATCH --mem=16G\n#SBATCH --clusters=joltik,accelgor"
            elif tool == 'columba':
                params.update({
                    "identity_threshold": config['identity_threshold'],
                    "cpus": config['cpus'],
                    "columba_repo": "/user/gent/446/vsc44685/ScratchVO_dir/columba",
                    "barcode_window": f"0-{BARCODE_LENGTH}"
                })
                resources = f"#SBATCH --cpus-per-task={config['cpus']}\n#SBATCH --mem=16G"
            
            # Write parameter JSON
            params_file = params_dir / f"params_{config_name}.json"
            with open(params_file, 'w') as f:
                json.dump(params, f, indent=4)
            
            # Create SLURM job script
            job_name = f"{tool.upper()[:2]}_runtime_{config_name}"
            job_file = jobs_dir / f"job_{config_name}.sh"
            
            # Get absolute paths
            project_dir = output_dir.parent.resolve()
            params_file_abs = params_file.resolve()
            work_dir_abs = project_dir / "work_runtime" / tool / config_name
            logs_dir_abs = logs_dir.resolve()
            
            job_content = f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH --ntasks=1
{resources}
#SBATCH --time=08:00:00
#SBATCH --output={logs_dir_abs}/{job_name}.out
#SBATCH --error={logs_dir_abs}/{job_name}.err

# Load Nextflow module
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="{project_dir}"
WORK_DIR="{work_dir_abs}"

# Create and move to unique work directory for this job to avoid lock conflicts
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Run pipeline
nextflow run "$PROJECT_DIR/main.nf" \\
    -c "$PROJECT_DIR/nextflow.config" \\
    -profile slurm \\
    -params-file {params_file_abs} \\
    -work-dir "$WORK_DIR" \\
    -resume

echo "Job completed for {tool.upper()} - runtime {config_name}"
"""
            
            with open(job_file, 'w') as f:
                f.write(job_content)
            
            job_file.chmod(0o755)
            
            print(f"  Created: {tool}/{config_name}")
        
        # Create tool-specific submission script
        submit_script = tool_dir / 'jobs' / f'submit_all_{tool}.sh'
        with open(submit_script, 'w') as f:
            f.write(f"""#!/bin/bash
# Submit all {tool} runtime benchmark jobs

cd {jobs_dir}

for job in job_*.sh; do
    echo "Submitting $job..."
    sbatch "$job"
done
""")
        submit_script.chmod(0o755)
    
    # Create master submission script
    submit_all = output_dir / 'SUBMIT_ALL_JOBS.sh'
    with open(submit_all, 'w') as f:
        f.write(f"""#!/bin/bash
# Submit all runtime benchmark jobs (all tools)

for tool in randombarcodes quik columba; do
    echo "Submitting $tool runtime jobs..."
    bash {output_dir}/$tool/jobs/submit_all_$tool.sh
done

echo "All runtime benchmark jobs submitted."
""")
    submit_all.chmod(0o755)
    
    total_params = sum(len(list((output_dir / tool / 'params').glob('*.json'))) for tool in RUNTIME_CONFIGS)
    total_jobs = sum(len(list((output_dir / tool / 'jobs').glob('job_*.sh'))) for tool in RUNTIME_CONFIGS)
    
    print(f"\n✓ Generated {total_params} parameter files")
    print(f"✓ Generated {total_jobs} job scripts")
    print(f"✓ Master submission script: {submit_all}")


def main():
    parser = argparse.ArgumentParser(description='Generate runtime benchmark files')
    parser.add_argument(
        '--data-dir',
        type=Path,
        required=True,
        help='Path to benchmark_85K_42K_21K_200K directory (downloaded from Zenodo)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'runtime_benchmarks',
        help='Output directory for jobs/params (default: runtime_benchmarks/)'
    )
    parser.add_argument(
        '--results-dir',
        type=Path,
        required=True,
        help='Base directory where results will be written'
    )
    
    args = parser.parse_args()
    
    if not args.data_dir.exists():
        print(f"ERROR: Data directory not found: {args.data_dir}")
        print("Please download benchmark_85K_42K_21K_200K.tar.gz from Zenodo and extract it.")
        return 1
    
    generate_runtime_benchmark(args.data_dir, args.output_dir, args.results_dir)
    return 0


if __name__ == '__main__':
    exit(main())
