#!/usr/bin/env python3
"""
Generate SLURM job files and parameter JSONs for real data benchmark.

Benchmark: Test 3 tools × 3 arrays × (real + decoy) = 18 total runs
Data required: Download real sequencing FASTQ files and barcode references from Zenodo
"""

import json
from pathlib import Path
import argparse


def generate_real_data_benchmark(
    data_dir: Path,
    barcode_dir: Path,
    output_dir: Path,
    results_dir: Path
):
    """Generate jobs and params for real data benchmark."""
    
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
            'identity_threshold': {
                '21k': 77,
                '42k': 80,
                '85k': 80
            },
            'cpus': 32
        }
    }
    
    ARRAYS = {
        '21k': {
            'count': 21476,
            'r1': 'Munchen_25024_1in4_S4_L001_R1_001.fastq.gz',
            'r2': 'Munchen_25024_1in4_S4_L001_R2_001.fastq.gz',
            'real_barcodes': 'Realbar_1in4_column_major.txt',
            'decoy_barcodes': 'Decoybar_1in4_column_major.txt'
        },
        '42k': {
            'count': 42653,
            'r1': 'Munchen_25024_1in2_S1_L001_R1_001.fastq.gz',
            'r2': 'Munchen_25024_1in2_S1_L001_R2_001.fastq.gz',
            'real_barcodes': 'Realbar_1in2_column_major.txt',
            'decoy_barcodes': 'Decoybar_1in2_column_major.txt'
        },
        '85k': {
            'count': 85305,
            'r1': 'Munchen_25024_1in1_S2_L001_R1_001.fastq.gz',
            'r2': 'Munchen_25024_1in1_S2_L001_R2_001.fastq.gz',
            'real_barcodes': 'Realbar_1in1_column_major.txt',
            'decoy_barcodes': 'Decoybar_1in1_column_major.txt'
        }
    }
    
    BARCODE_WINDOW = "10-46"  # Real data has handles; barcode is at positions 10-46
    
    # Create output directories
    for tool in TOOLS:
        tool_dir = output_dir / tool
        (tool_dir / 'params').mkdir(parents=True, exist_ok=True)
        (tool_dir / 'jobs').mkdir(parents=True, exist_ok=True)
        (tool_dir / 'logs').mkdir(exist_ok=True)
    
    print(f"Generating real-data benchmark files...")
    print(f"  Data directory (FASTQ): {data_dir}")
    print(f"  Barcode directory: {barcode_dir}")
    print(f"  Output directory: {output_dir}")
    print(f"  Results directory: {results_dir}")
    
    for tool in TOOLS:
        tool_dir = output_dir / tool
        
        for array_label, array_info in ARRAYS.items():
            # Generate for both real and decoy runs
            for run_type in ['real', 'decoy']:
                bc_file = array_info[f'{run_type}_barcodes']
                
                sample_id_suffix = f"{array_label}"
                if run_type == 'decoy':
                    sample_id_suffix = f"decoy_{array_label}"
                
                sample_id = f"{tool.capitalize()}_{sample_id_suffix}"
                
                # Get identity threshold for Columba (varies by array size)
                if tool == 'columba':
                    identity_thresh = TOOLS[tool]['identity_threshold'][array_label]
                    sample_id += f"_I{identity_thresh}"
                
                # Create parameter JSON
                params = {
                    "barcode_file": str(barcode_dir / bc_file),
                    "r1_fastq": str(data_dir / array_info['r1']),
                    "r2_fastq": str(data_dir / array_info['r2']),
                    "barcode_window": BARCODE_WINDOW,
                    "tool": tool,
                    "sample_id": sample_id,
                    "data_mode": "real",
                    "outdir": str(results_dir / tool / f"{array_label}_{run_type}") if run_type == 'decoy' else str(results_dir / tool / array_label)
                }
                
                # Add tool-specific parameters
                if tool == 'randombarcodes':
                    params.update({
                        "n_barcodes": array_info['count'],
                        "ntriage": TOOLS[tool]['ntriage'],
                        "nthresh": TOOLS[tool]['nthresh'],
                        "gpus": TOOLS[tool]['gpus'],
                        "barcode_start": 10,
                        "barcode_length": 36
                    })
                elif tool == 'quik':
                    params.update({
                        "strategy": TOOLS[tool]['strategy'],
                        "distance_measure": TOOLS[tool]['distance_measure'],
                        "rejection_threshold": TOOLS[tool]['rejection_threshold'],
                        "gpus": TOOLS[tool]['gpus'],
                        "barcode_start": 10,
                        "barcode_length": 36
                    })
                elif tool == 'columba':
                    params.update({
                        "identity_threshold": identity_thresh,
                        "cpus": TOOLS[tool]['cpus'],
                        "columba_repo": "/user/gent/446/vsc44685/ScratchVO_dir/columba"
                    })
                
                # Write parameter JSON
                params_file = tool_dir / 'params' / f"params_{array_label}{'_decoy' if run_type == 'decoy' else ''}.json"
                with open(params_file, 'w') as f:
                    json.dump(params, f, indent=2)
                
                # Create SLURM job script
                job_name = f"{tool.upper()[:4]}_{run_type}_{array_label}"
                job_file = tool_dir / 'jobs' / f"job_{array_label}{'_decoy' if run_type == 'decoy' else ''}.sh"
                
                # Relative paths from project root
                params_rel = f"real_data/{tool}/params/params_{array_label}{'_decoy' if run_type == 'decoy' else ''}.json"
                work_rel = f"work_real_data/{tool}/{array_label}_{run_type}"
                logs_rel = f"real_data/{tool}/logs"
                
                # Reports directory - use results_dir for consistency
                reports_dir = f"{results_dir}/reports"
                
                # Determine resource requirements
                if tool == 'columba':
                    time_limit = "12:00:00"
                    resources = f"#SBATCH --cpus-per-task={TOOLS[tool]['cpus']}\n#SBATCH --mem=16G"
                else:  # GPU tools
                    time_limit = "08:00:00"
                    resources = f"#SBATCH --gres=gpu:1\n#SBATCH --cpus-per-task=1\n#SBATCH --mem=16G\n#SBATCH --clusters=joltik,accelgor"
                
                job_content = f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH --ntasks=1
{resources}
#SBATCH --time={time_limit}
#SBATCH --output={logs_rel}/{job_name}.out
#SBATCH --error={logs_rel}/{job_name}.err

# Load Nextflow module
ml Nextflow/25.04.8

# Run pipeline from project root directory
nextflow run main.nf \\
    -params-file {params_rel} \\
    -work-dir {work_rel} \\
    -profile slurm \\
    -with-report {reports_dir}/{job_name}_report.html \\
    -with-timeline {reports_dir}/{job_name}_timeline.html \\
    -with-dag {reports_dir}/{job_name}_dag.html
"""
                
                with open(job_file, 'w') as f:
                    f.write(job_content)
                
                job_file.chmod(0o755)
                
                print(f"  Created: {tool}/{array_label}_{run_type}")
    
    # Create tool-specific submission scripts
    for tool in TOOLS:
        tool_dir = output_dir / tool
        submit_script = tool_dir / 'submit_all.sh'
        with open(submit_script, 'w') as f:
            f.write(f"""#!/bin/bash
# Submit all {tool} real-data jobs

cd {tool_dir}/jobs

for job in *.sh; do
    echo "Submitting $job..."
    sbatch "$job"
done
""")
        submit_script.chmod(0o755)
    
    # Create master submission script
    submit_all = output_dir / 'submit_all_tools.sh'
    with open(submit_all, 'w') as f:
        f.write(f"""#!/bin/bash
# Submit all real-data benchmark jobs (all tools)

for tool in randombarcodes quik columba; do
    echo "Submitting $tool jobs..."
    bash {output_dir}/$tool/submit_all.sh
done

echo "All real-data benchmark jobs submitted."
""")
    submit_all.chmod(0o755)
    
    total_params = sum(len(list((output_dir / tool / 'params').glob('*.json'))) for tool in TOOLS)
    total_jobs = sum(len(list((output_dir / tool / 'jobs').glob('*.sh'))) for tool in TOOLS)
    
    print(f"\n✓ Generated {total_params} parameter files")
    print(f"✓ Generated {total_jobs} job scripts")
    print(f"✓ Master submission script: {submit_all}")


def main():
    parser = argparse.ArgumentParser(description='Generate real-data benchmark files')
    parser.add_argument(
        '--data-dir',
        type=Path,
        required=True,
        help='Directory containing real sequencing FASTQ files (from Zenodo)'
    )
    parser.add_argument(
        '--barcode-dir',
        type=Path,
        required=True,
        help='Directory containing real and decoy barcode reference files'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'real_data',
        help='Output directory for jobs/params (default: real_data/)'
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
        return 1
    
    if not args.barcode_dir.exists():
        print(f"ERROR: Barcode directory not found: {args.barcode_dir}")
        return 1
    
    generate_real_data_benchmark(args.data_dir, args.barcode_dir, args.output_dir, args.results_dir)
    return 0


if __name__ == '__main__':
    exit(main())
