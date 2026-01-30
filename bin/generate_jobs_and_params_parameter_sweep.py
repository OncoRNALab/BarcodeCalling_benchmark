#!/usr/bin/env python3
"""
Generate SLURM job files and parameter JSONs for parameter sweep benchmarks.

Benchmark: Test optimal parameters for 3 tools across 5 barcode lengths
Data required: Download benchmark_85K_42K_21K_200K.tar.gz from Zenodo

Notes:
- For 28nt and 36nt: comprehensive sweeps (strategies, triage sizes)
- For 30nt, 32nt, 34nt: minimal sweeps (only rejection/distance thresholds)
"""

import json
from pathlib import Path
import argparse


def generate_parameter_sweep(
    data_dir: Path,
    output_dir: Path,
    results_dir: Path,
    barcode_length: int
):
    """Generate jobs and params for one barcode length."""
    
    BARCODE_COUNT = '21K'
    ERROR_RATE = 'low'
    
    # Define sweep configurations based on barcode length
    if barcode_length in [28, 36]:
        # Comprehensive sweeps
        RB_CONFIGS = {
            'ntriage_values': [100, 1000, 2000, 5000, 10000],
            'nthresh_values': [5, 6, 7, 8, 9, 10]
        }
        QUIK_CONFIGS = {
            'strategies': ['4_mer_gpu_v4', '4_7_mer_gpu_v1', '7_7_mer_gpu_v1'],
            'rejection_thresholds': [5, 6, 7, 8, 9, 10]
        }
    else:  # 30, 32, 34
        # Minimal sweeps: fixed triage/strategy, sweep threshold only
        RB_CONFIGS = {
            'ntriage_values': [100],
            'nthresh_values': [5, 6, 7, 8, 9]
        }
        QUIK_CONFIGS = {
            'strategies': ['4_mer_gpu_v4'],
            'rejection_thresholds': [5, 6, 7, 8, 9]
        }
    
    COLUMBA_IDENTITY_THRESHOLDS = [77, 78, 79, 80, 81, 82]
    
    # Data paths
    bc_dir = data_dir / f"{BARCODE_COUNT}_{barcode_length}nt"
    
    # Create output structure
    length_dir = output_dir / f"{barcode_length}nt"
    
    print(f"\nGenerating parameter sweep for {barcode_length}nt barcodes...")
    print(f"  Output: {length_dir}")
    
    # === RandomBarcodes ===
    rb_dir = length_dir / 'randombarcodes'
    rb_params_dir = rb_dir / 'params'
    rb_jobs_dir = rb_dir / 'jobs'
    rb_params_dir.mkdir(parents=True, exist_ok=True)
    rb_jobs_dir.mkdir(exist_ok=True)
    (rb_dir / 'logs').mkdir(exist_ok=True)
    
    for ntriage in RB_CONFIGS['ntriage_values']:
        for nthresh in RB_CONFIGS['nthresh_values']:
            sample_id = f"RB_{barcode_length}nt_t{ntriage}_n{nthresh}"
            
            params = {
                "tool": "randombarcodes",
                "barcode_file": str(bc_dir / f"barcodes_{BARCODE_COUNT}_{barcode_length}_subset1"),
                "r1_fastq": str(bc_dir / f"reads_{BARCODE_COUNT}_{barcode_length}_{ERROR_RATE}_R1.fastq"),
                "r2_fastq": str(bc_dir / f"reads_{BARCODE_COUNT}_{barcode_length}_{ERROR_RATE}_R2.fastq"),
                "ground_truth": str(bc_dir / f"answers_{BARCODE_COUNT}_{barcode_length}_{ERROR_RATE}"),
                "sample_id": sample_id,
                "barcode_length": barcode_length,
                "barcode_start": 0,
                "outdir": str(results_dir / f"results_{barcode_length}nt" / "randombarcodes_sweep" / f"t{ntriage}_n{nthresh}"),
                "ntriage": ntriage,
                "nthresh": nthresh,
                "gpus": 1
            }
            
            params_file = rb_params_dir / f"params_t{ntriage}_n{nthresh}.json"
            with open(params_file, 'w') as f:
                json.dump(params, f, indent=2)
            
            job_name = f"RB{barcode_length}_t{ntriage}_n{nthresh}"
            job_file = rb_jobs_dir / f"job_t{ntriage}_n{nthresh}.sh"
            
            # Relative paths from project root
            params_rel = f"parameter_sweeps/{barcode_length}nt/randombarcodes/params/params_t{ntriage}_n{nthresh}.json"
            work_rel = f"work_sweep_rb_{barcode_length}nt/t{ntriage}_n{nthresh}"
            logs_rel = f"parameter_sweeps/{barcode_length}nt/randombarcodes/logs"
            
            job_content = f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --clusters=joltik,accelgor
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
    
    # === QUIK ===
    quik_dir = length_dir / 'quik'
    quik_params_dir = quik_dir / 'params'
    quik_jobs_dir = quik_dir / 'jobs'
    quik_params_dir.mkdir(parents=True, exist_ok=True)
    quik_jobs_dir.mkdir(exist_ok=True)
    (quik_dir / 'logs').mkdir(exist_ok=True)
    
    for strategy in QUIK_CONFIGS['strategies']:
        for r in QUIK_CONFIGS['rejection_thresholds']:
            strat_short = strategy.split('_')[0]  # e.g., '4' or '7'
            sample_id = f"QUIK_{barcode_length}nt_{strat_short}mer_r{r}"
            
            params = {
                "tool": "quik",
                "barcode_file": str(bc_dir / f"barcodes_{BARCODE_COUNT}_{barcode_length}_subset1"),
                "r1_fastq": str(bc_dir / f"reads_{BARCODE_COUNT}_{barcode_length}_{ERROR_RATE}_R1.fastq"),
                "r2_fastq": str(bc_dir / f"reads_{BARCODE_COUNT}_{barcode_length}_{ERROR_RATE}_R2.fastq"),
                "ground_truth": str(bc_dir / f"answers_{BARCODE_COUNT}_{barcode_length}_{ERROR_RATE}"),
                "sample_id": sample_id,
                "barcode_length": barcode_length,
                "barcode_start": 0,
                "barcode_window": f"0-{barcode_length}",
                "outdir": str(results_dir / f"results_{barcode_length}nt" / "quik_sweep" / f"{strat_short}mer_r{r}"),
                "strategy": strategy,
                "distance_measure": "SEQUENCE_LEVENSHTEIN",
                "rejection_threshold": r,
                "gpus": 1
            }
            
            params_file = quik_params_dir / f"params_{strat_short}mer_r{r}.json"
            with open(params_file, 'w') as f:
                json.dump(params, f, indent=2)
            
            job_name = f"QK{barcode_length}_{strat_short}mer_r{r}"
            job_file = quik_jobs_dir / f"job_{strat_short}mer_r{r}.sh"
            
            # Relative paths from project root
            params_rel = f"parameter_sweeps/{barcode_length}nt/quik/params/params_{strat_short}mer_r{r}.json"
            work_rel = f"work_sweep_quik_{barcode_length}nt/{strat_short}mer_r{r}"
            logs_rel = f"parameter_sweeps/{barcode_length}nt/quik/logs"
            
            job_content = f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --clusters=joltik,accelgor
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
    
    # === Columba ===
    col_dir = length_dir / 'columba'
    col_params_dir = col_dir / 'params'
    col_jobs_dir = col_dir / 'jobs'
    col_params_dir.mkdir(parents=True, exist_ok=True)
    col_jobs_dir.mkdir(exist_ok=True)
    (col_dir / 'logs').mkdir(exist_ok=True)
    
    for identity_thresh in COLUMBA_IDENTITY_THRESHOLDS:
        sample_id = f"Columba{barcode_length}_I{identity_thresh}"
        
        params = {
            "barcode_file": str(bc_dir / f"barcodes_{BARCODE_COUNT}_{barcode_length}_subset1"),
            "r1_fastq": str(bc_dir / f"reads_{BARCODE_COUNT}_{barcode_length}_{ERROR_RATE}_R1.fastq"),
            "r2_fastq": str(bc_dir / f"reads_{BARCODE_COUNT}_{barcode_length}_{ERROR_RATE}_R2.fastq"),
            "ground_truth": str(bc_dir / f"answers_{BARCODE_COUNT}_{barcode_length}_{ERROR_RATE}"),
            "barcode_start": 0,
            "barcode_length": barcode_length,
            "tool": "columba",
            "columba_repo": "/user/gent/446/vsc44685/ScratchVO_dir/columba",
            "identity_threshold": identity_thresh,
            "barcode_window": f"0-{barcode_length}",
            "cpus": 4,
            "sample_id": sample_id,
            "outdir": str(results_dir / f"results_{barcode_length}nt" / "columba_sweep" / f"I{identity_thresh}")
        }
        
        params_file = col_params_dir / f"params_I{identity_thresh}.json"
        with open(params_file, 'w') as f:
            json.dump(params, f, indent=2)
        
        job_name = f"CB{barcode_length}_I{identity_thresh}"
        job_file = col_jobs_dir / f"job_I{identity_thresh}.sh"
        
        # Relative paths from project root
        params_rel = f"parameter_sweeps/{barcode_length}nt/columba/params/params_I{identity_thresh}.json"
        work_rel = f"work_sweep_columba_{barcode_length}nt/I{identity_thresh}"
        logs_rel = f"parameter_sweeps/{barcode_length}nt/columba/logs"
        
        job_content = f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
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
    
    # Create submission scripts for each tool
    for tool_dir, tool_name in [(rb_dir, 'randombarcodes'), (quik_dir, 'quik'), (col_dir, 'columba')]:
        submit_script = tool_dir / 'submit_all.sh'
        with open(submit_script, 'w') as f:
            f.write(f"""#!/bin/bash
cd {tool_dir}/jobs
for job in job_*.sh; do
    echo "Submitting $job..."
    sbatch "$job"
done
""")
        submit_script.chmod(0o755)
    
    # Create master submission script for this length
    submit_all = length_dir / 'submit_all.sh'
    with open(submit_all, 'w') as f:
        f.write(f"""#!/bin/bash
# Submit all parameter sweep jobs for {barcode_length}nt barcodes

bash {rb_dir}/submit_all.sh
bash {quik_dir}/submit_all.sh
bash {col_dir}/submit_all.sh

echo "All {barcode_length}nt parameter sweep jobs submitted."
""")
    submit_all.chmod(0o755)
    
    total_params = (
        len(list(rb_params_dir.glob('*.json'))) +
        len(list(quik_params_dir.glob('*.json'))) +
        len(list(col_params_dir.glob('*.json')))
    )
    
    print(f"  ✓ {barcode_length}nt: {total_params} total parameter files")


def main():
    parser = argparse.ArgumentParser(description='Generate parameter sweep benchmark files')
    parser.add_argument(
        '--data-dir',
        type=Path,
        required=True,
        help='Path to benchmark_85K_42K_21K_200K directory (downloaded from Zenodo)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'parameter_sweeps',
        help='Output directory for jobs/params (default: parameter_sweeps/)'
    )
    parser.add_argument(
        '--results-dir',
        type=Path,
        required=True,
        help='Base directory where results will be written'
    )
    parser.add_argument(
        '--barcode-lengths',
        type=int,
        nargs='+',
        default=[28, 30, 32, 34, 36],
        help='Barcode lengths to generate (default: 28 30 32 34 36)'
    )
    
    args = parser.parse_args()
    
    if not args.data_dir.exists():
        print(f"ERROR: Data directory not found: {args.data_dir}")
        print("Please download benchmark_85K_42K_21K_200K.tar.gz from Zenodo and extract it.")
        return 1
    
    print(f"Generating parameter sweep benchmarks...")
    print(f"  Data directory: {data_dir}")
    print(f"  Output directory: {args.output_dir}")
    print(f"  Results directory: {args.results_dir}")
    print(f"  Barcode lengths: {args.barcode_lengths}")
    
    for length in args.barcode_lengths:
        generate_parameter_sweep(args.data_dir, args.output_dir, args.results_dir, length)
    
    # Create master submission script for all lengths
    submit_all_master = args.output_dir / 'submit_all_parameter_sweeps.sh'
    with open(submit_all_master, 'w') as f:
        f.write(f"""#!/bin/bash
# Submit all parameter sweep jobs (all barcode lengths)

cd {args.output_dir}

for length in {' '.join(str(l) for l in args.barcode_lengths)}; do
    echo "Submitting ${{length}}nt parameter sweep..."
    bash "${{length}}nt/submit_all.sh"
done

echo "All parameter sweep jobs submitted."
""")
    submit_all_master.chmod(0o755)
    
    print(f"\n✓ Master submission script: {submit_all_master}")
    return 0


if __name__ == '__main__':
    exit(main())
