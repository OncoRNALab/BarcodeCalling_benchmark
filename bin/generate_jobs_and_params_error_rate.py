#!/usr/bin/env python3
"""
Generate SLURM job files and parameter JSONs for error-rate benchmark.

Benchmark: Test 3 tools × 3 barcode counts × 3 error rates (27 total runs)
Data required: Download benchmark_85K_42K_21K_200K.tar.gz from Zenodo
"""

import json
from pathlib import Path
import argparse


def generate_error_rate_benchmark(
    data_dir: Path,
    output_dir: Path,
    results_dir: Path
):
    """Generate jobs and params for error-rate benchmark."""
    
    # Configuration from cleaning_prompt.json
    TOOLS = {
        'randombarcodes': {
            'ntriage': 100,
            'nthresh': 9,
            'gpus': 1
        },
        'quik': {
            'strategy': '4_mer_gpu_v4',
            'distance_measure': 'SEQUENCE_LEVENSHTEIN',
            'rejection_threshold': 8,
            'gpus': 1
        },
        'columba': {
            'identity_threshold': 80,
            'cpus': 16
        }
    }
    
    BARCODE_COUNTS = {
        '21K': 21000,
        '42K': 42000,
        '85K': 85000
    }
    
    ERROR_RATES = ['low', 'medium', 'high']
    BARCODE_LENGTH = 36
    
    # Create output directories
    params_dir = output_dir / 'params'
    jobs_dir = output_dir / 'jobs'
    params_dir.mkdir(parents=True, exist_ok=True)
    jobs_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating error-rate benchmark files...")
    print(f"  Data directory: {data_dir}")
    print(f"  Output directory: {output_dir}")
    print(f"  Results directory: {results_dir}")
    
    for tool in TOOLS:
        for bc_label, bc_count in BARCODE_COUNTS.items():
            for error_rate in ERROR_RATES:
                # Define paths
                bc_dir = data_dir / f"{bc_label}_{BARCODE_LENGTH}nt"
                
                sample_id = f"{tool}_{bc_label}_{BARCODE_LENGTH}nt_{error_rate}"
                
                # Create parameter JSON
                params = {
                    "comment": f"{tool.capitalize()} parameters for {bc_label} barcodes, {BARCODE_LENGTH}nt, {error_rate} error rate",
                    "tool": tool,
                    "barcode_file": str(bc_dir / f"barcodes_{bc_label}_{BARCODE_LENGTH}_subset1"),
                    "r1_fastq": str(bc_dir / f"reads_{bc_label}_{BARCODE_LENGTH}_{error_rate}_R1.fastq"),
                    "r2_fastq": str(bc_dir / f"reads_{bc_label}_{BARCODE_LENGTH}_{error_rate}_R2.fastq"),
                    "sample_id": sample_id,
                    "barcode_length": BARCODE_LENGTH,
                    "outdir": str(results_dir / sample_id),
                    "ground_truth": str(bc_dir / f"answers_{bc_label}_{BARCODE_LENGTH}_{error_rate}"),
                }
                
                # Add tool-specific parameters
                if tool == 'randombarcodes':
                    params.update({
                        "comment_randombarcodes": "RandomBarcodes-specific parameters",
                        "ntriage": TOOLS[tool]['ntriage'],
                        "nthresh": TOOLS[tool]['nthresh'],
                        "gpus": TOOLS[tool]['gpus']
                    })
                elif tool == 'quik':
                    params.update({
                        "comment_quik": "QUIK-specific parameters",
                        "strategy": TOOLS[tool]['strategy'],
                        "distance_measure": TOOLS[tool]['distance_measure'],
                        "rejection_threshold": TOOLS[tool]['rejection_threshold'],
                        "gpus": TOOLS[tool]['gpus'],
                        "barcode_start": 0,
                        "barcode_window": f"0-{BARCODE_LENGTH}"
                    })
                elif tool == 'columba':
                    params.update({
                        "comment_columba": "Columba-specific parameters",
                        "columba_repo": "/user/gent/446/vsc44685/ScratchVO_dir/columba",
                        "identity_threshold": TOOLS[tool]['identity_threshold'],
                        "barcode_window": f"0-{BARCODE_LENGTH}",
                        "cpus": TOOLS[tool]['cpus']
                    })
                
                # Write parameter JSON
                params_file = params_dir / f"{tool}_{bc_label}_{error_rate}.json"
                with open(params_file, 'w') as f:
                    json.dump(params, f, indent=4)
                
                # Create SLURM job script
                job_name = f"{tool.upper()[:2]}_{bc_label}_{BARCODE_LENGTH}nt_{error_rate}"
                job_file = jobs_dir / f"{tool}_{bc_label}_{error_rate}.sh"
                
                # Relative paths from project root
                params_rel = f"error_rate_benchmark/params/{tool}_{bc_label}_{error_rate}.json"
                work_rel = f"work_error_rate/{tool}/{bc_label}_{error_rate}"
                logs_rel = f"error_rate_benchmark/logs"
                
                # Determine resource requirements
                if tool == 'columba':
                    resources = f"#SBATCH --cpus-per-task={TOOLS[tool]['cpus']}\n#SBATCH --mem=16G"
                else:  # GPU tools
                    resources = f"#SBATCH --gres=gpu:1\n#SBATCH --cpus-per-task=1\n#SBATCH --mem=16G\n#SBATCH --clusters=joltik,accelgor"
                
                job_content = f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH --ntasks=1
{resources}
#SBATCH --time=08:00:00
#SBATCH --output={logs_rel}/{job_name}.out
#SBATCH --error={logs_rel}/{job_name}.err

# Load Nextflow module
ml Nextflow/25.04.8

# Run pipeline from project root directory
nextflow run main.nf \\
    -params-file {params_rel} \\
    -work-dir {work_rel} \\
    -profile slurm
"""
                
                with open(job_file, 'w') as f:
                    f.write(job_content)
                
                job_file.chmod(0o755)
                
                print(f"  Created: {tool}_{bc_label}_{error_rate}")
    
    # Create master submission script
    submit_all = output_dir / 'submit_all_error_rate_benchmarks.sh'
    with open(submit_all, 'w') as f:
        f.write(f"""#!/bin/bash
# Submit all error-rate benchmark jobs

cd {jobs_dir}

for job in *.sh; do
    echo "Submitting $job..."
    sbatch "$job"
done

echo "All error-rate benchmark jobs submitted."
""")
    submit_all.chmod(0o755)
    
    print(f"\n✓ Generated {len(list(params_dir.glob('*.json')))} parameter files")
    print(f"✓ Generated {len(list(jobs_dir.glob('*.sh')))} job scripts")
    print(f"✓ Master submission script: {submit_all}")


def main():
    parser = argparse.ArgumentParser(description='Generate error-rate benchmark files')
    parser.add_argument(
        '--data-dir',
        type=Path,
        required=True,
        help='Path to benchmark_85K_42K_21K_200K directory (downloaded from Zenodo)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'error_rate_benchmark',
        help='Output directory for jobs/params (default: error_rate_benchmark/)'
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
    
    generate_error_rate_benchmark(args.data_dir, args.output_dir, args.results_dir)
    return 0


if __name__ == '__main__':
    exit(main())
