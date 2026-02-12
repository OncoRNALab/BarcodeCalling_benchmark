#!/usr/bin/env python3
"""
Generate SLURM job files and parameter JSONs for barcode library size benchmarks.

Benchmark: Test the effect of barcode library size on tool performance
Data required: Download benchmark_85K_42K_21K_200K.tar.gz from Zenodo

Notes:
- Tests 3 barcode counts (21K, 42K, 85K) with 200K reads
- Tests 2 barcode lengths (28nt, 36nt)
- Each combination has parameter sweeps for all 3 tools
"""

import json
from pathlib import Path
import argparse


def generate_barcode_count_sweep(
    data_dir: Path,
    output_dir: Path,
    results_dir: Path,
    columba_repo: str
):
    """Generate jobs and params for barcode count sweep across all combinations."""
    
    # Fixed parameters
    BARCODE_COUNTS = [21000, 42000, 85000]
    BARCODE_LENGTHS = [28, 36]
    ERROR_RATE = 'low'
    
    # Tool-specific configurations
    RB_CONFIGS = {
        'ntriage_values': [100],
        'nthresh_values': [5, 6, 7, 8, 9],
        'gpus': 2
    }
    
    QUIK_CONFIGS = {
        'strategies': ['4_mer_gpu_v4'],
        'rejection_thresholds': [5, 6, 7, 8, 9, 10],
        'gpus': 1
    }
    
    COLUMBA_IDENTITY_THRESHOLDS = [77, 78, 79, 80, 81, 82, 83]
    COLUMBA_CPUS = 8
    
    print("\n" + "="*80)
    print("Generating Barcode Count Parameter Sweep Jobs")
    print("="*80)
    
    for barcode_count in BARCODE_COUNTS:
        for barcode_length in BARCODE_LENGTHS:
            bc_count_str = f"{barcode_count//1000}K"  # Convert to 21K, 42K, 85K
            combo_name = f"{bc_count_str}_{barcode_length}nt"
            
            print(f"\nGenerating jobs for {combo_name}...")
            
            # Data paths - relative to project root
            bc_dir = data_dir / f"{bc_count_str}_{barcode_length}nt"
            
            # === RandomBarcodes ===
            print(f"  - RandomBarcodes")
            rb_dir = output_dir / 'randombarcodes' / combo_name
            rb_params_dir = rb_dir / 'params'
            rb_jobs_dir = rb_dir / 'jobs'
            rb_logs_dir = rb_dir / 'logs'
            rb_params_dir.mkdir(parents=True, exist_ok=True)
            rb_jobs_dir.mkdir(exist_ok=True)
            rb_logs_dir.mkdir(exist_ok=True)
            
            for ntriage in RB_CONFIGS['ntriage_values']:
                for nthresh in RB_CONFIGS['nthresh_values']:
                    sample_id = f"RB_{bc_count_str}_{barcode_length}nt_t{ntriage}_n{nthresh}"
                    
                    params = {
                        "barcode_file": str(bc_dir / f"barcodes_{bc_count_str}_{barcode_length}_subset1"),
                        "r1_fastq": str(bc_dir / f"reads_{bc_count_str}_{barcode_length}_{ERROR_RATE}_R1.fastq"),
                        "r2_fastq": str(bc_dir / f"reads_{bc_count_str}_{barcode_length}_{ERROR_RATE}_R2.fastq"),
                        "ground_truth": str(bc_dir / f"answers_{bc_count_str}_{barcode_length}_{ERROR_RATE}"),
                        "barcode_length": barcode_length,
                        "barcode_start": 0,
                        "n_barcodes": barcode_count,
                        "gpus": RB_CONFIGS['gpus'],
                        "tool": "randombarcodes",
                        "ntriage": ntriage,
                        "nthresh": nthresh,
                        "sample_id": sample_id,
                        "outdir": str(results_dir / "randombarcodes" / combo_name / f"t{ntriage}_n{nthresh}")
                    }
                    
                    params_file = rb_params_dir / f"params_t{ntriage}_n{nthresh}.json"
                    with open(params_file, 'w') as f:
                        json.dump(params, f, indent=2)
                    
                    job_name = f"RB_{bc_count_str}_{barcode_length}nt_n{nthresh}"
                    job_file = rb_jobs_dir / f"job_t{ntriage}_n{nthresh}.sh"
                    
                    # Relative paths from project root
                    params_rel = f"parameter_sweeps_barcode_count/randombarcodes/{combo_name}/params/params_t{ntriage}_n{nthresh}.json"
                    work_rel = f"work_barcode_count/randombarcodes/{combo_name}/t{ntriage}_n{nthresh}"
                    logs_rel = f"parameter_sweeps_barcode_count/randombarcodes/{combo_name}/logs"
                    
                    # Reports directory
                    reports_dir = f"{results_dir}/reports/randombarcodes/{combo_name}"
                    
                    job_content = f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH --ntasks=1
#SBATCH --gres=gpu:{RB_CONFIGS['gpus']}
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --clusters=joltik,accelgor
#SBATCH --time=08:00:00
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
            
            # === QUIK ===
            print(f"  - QUIK")
            quik_dir = output_dir / 'quik' / combo_name
            quik_params_dir = quik_dir / 'params'
            quik_jobs_dir = quik_dir / 'jobs'
            quik_logs_dir = quik_dir / 'logs'
            quik_params_dir.mkdir(parents=True, exist_ok=True)
            quik_jobs_dir.mkdir(exist_ok=True)
            quik_logs_dir.mkdir(exist_ok=True)
            
            for strategy in QUIK_CONFIGS['strategies']:
                for r in QUIK_CONFIGS['rejection_thresholds']:
                    strat_short = strategy.split('_')[0]  # '4' from '4_mer_gpu_v4'
                    sample_id = f"QUIK_{bc_count_str}_{barcode_length}nt_{strat_short}mer_r{r}"
                    
                    params = {
                        "tool": "quik",
                        "barcode_file": str(bc_dir / f"barcodes_{bc_count_str}_{barcode_length}_subset1"),
                        "r1_fastq": str(bc_dir / f"reads_{bc_count_str}_{barcode_length}_{ERROR_RATE}_R1.fastq"),
                        "r2_fastq": str(bc_dir / f"reads_{bc_count_str}_{barcode_length}_{ERROR_RATE}_R2.fastq"),
                        "ground_truth": str(bc_dir / f"answers_{bc_count_str}_{barcode_length}_{ERROR_RATE}"),
                        "barcode_length": barcode_length,
                        "barcode_start": 0,
                        "distance_measure": "SEQUENCE_LEVENSHTEIN",
                        "strategy": strategy,
                        "rejection_threshold": r,
                        "sample_id": sample_id,
                        "outdir": str(results_dir / "quik" / combo_name / f"{strat_short}mer_r{r}")
                    }
                    
                    params_file = quik_params_dir / f"params_{strat_short}mer_r{r}.json"
                    with open(params_file, 'w') as f:
                        json.dump(params, f, indent=2)
                    
                    job_name = f"QUIK_{bc_count_str}_{barcode_length}nt_{strat_short}mer_r{r}"
                    job_file = quik_jobs_dir / f"job_{strat_short}mer_r{r}.sh"
                    
                    # Relative paths from project root
                    params_rel = f"parameter_sweeps_barcode_count/quik/{combo_name}/params/params_{strat_short}mer_r{r}.json"
                    work_rel = f"work_barcode_count/quik/{combo_name}/{strat_short}mer_r{r}"
                    logs_rel = f"parameter_sweeps_barcode_count/quik/{combo_name}/logs"
                    
                    # Reports directory
                    reports_dir = f"{results_dir}/reports/quik/{combo_name}"
                    
                    job_content = f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH --ntasks=1
#SBATCH --gres=gpu:{QUIK_CONFIGS['gpus']}
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --clusters=joltik,accelgor
#SBATCH --time=08:00:00
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
            
            # === Columba ===
            print(f"  - Columba")
            columba_dir = output_dir / 'columba' / combo_name
            columba_params_dir = columba_dir / 'params'
            columba_jobs_dir = columba_dir / 'jobs'
            columba_logs_dir = columba_dir / 'logs'
            columba_params_dir.mkdir(parents=True, exist_ok=True)
            columba_jobs_dir.mkdir(exist_ok=True)
            columba_logs_dir.mkdir(exist_ok=True)
            
            for identity in COLUMBA_IDENTITY_THRESHOLDS:
                sample_id = f"Columba_{bc_count_str}_{barcode_length}nt_I{identity}"
                
                params = {
                    "tool": "columba",
                    "barcode_file": str(bc_dir / f"barcodes_{bc_count_str}_{barcode_length}_subset1"),
                    "r1_fastq": str(bc_dir / f"reads_{bc_count_str}_{barcode_length}_{ERROR_RATE}_R1.fastq"),
                    "r2_fastq": str(bc_dir / f"reads_{bc_count_str}_{barcode_length}_{ERROR_RATE}_R2.fastq"),
                    "ground_truth": str(bc_dir / f"answers_{bc_count_str}_{barcode_length}_{ERROR_RATE}"),
                    "barcode_length": barcode_length,
                    "barcode_window": f"0-{barcode_length}",
                    "identity_threshold": identity,
                    "cpus": COLUMBA_CPUS,
                    "sample_id": sample_id,
                    "outdir": str(results_dir / "columba" / combo_name / f"I{identity}")
                }
                
                # Only add columba_repo if provided (needed for slurm profile only)
                if columba_repo:
                    params["columba_repo"] = columba_repo
                
                params_file = columba_params_dir / f"params_I{identity}.json"
                with open(params_file, 'w') as f:
                    json.dump(params, f, indent=2)
                
                job_name = f"Columba_{bc_count_str}_{barcode_length}nt_I{identity}"
                job_file = columba_jobs_dir / f"job_I{identity}.sh"
                
                # Relative paths from project root
                params_rel = f"parameter_sweeps_barcode_count/columba/{combo_name}/params/params_I{identity}.json"
                work_rel = f"work_barcode_count/columba/{combo_name}/I{identity}"
                logs_rel = f"parameter_sweeps_barcode_count/columba/{combo_name}/logs"
                
                # Reports directory
                reports_dir = f"{results_dir}/reports/columba/{combo_name}"
                
                job_content = f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={COLUMBA_CPUS}
#SBATCH --mem=32G
#SBATCH --time=08:00:00
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
    
    print("\n" + "="*80)
    print("Generation Complete!")
    print("="*80)
    print(f"\nGenerated jobs in: {output_dir}")
    print(f"Results will be saved to: {results_dir}")
    
    # Print summary
    total_jobs = 0
    for bc_count in BARCODE_COUNTS:
        for bc_len in BARCODE_LENGTHS:
            rb_jobs = len(RB_CONFIGS['ntriage_values']) * len(RB_CONFIGS['nthresh_values'])
            quik_jobs = len(QUIK_CONFIGS['strategies']) * len(QUIK_CONFIGS['rejection_thresholds'])
            columba_jobs = len(COLUMBA_IDENTITY_THRESHOLDS)
            total_jobs += rb_jobs + quik_jobs + columba_jobs
    
    print(f"\nTotal jobs generated: {total_jobs}")
    print(f"  - Per combination: {rb_jobs} (RB) + {quik_jobs} (QUIK) + {columba_jobs} (Columba) = {rb_jobs + quik_jobs + columba_jobs}")
    print(f"  - Combinations: {len(BARCODE_COUNTS)} counts × {len(BARCODE_LENGTHS)} lengths = {len(BARCODE_COUNTS) * len(BARCODE_LENGTHS)}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate jobs and params for barcode library size benchmarks'
    )
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=Path('data/benchmark_85K_42K_21K_200K'),
        help='Path to benchmark data directory relative to project root (default: %(default)s)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('parameter_sweeps_barcode_count'),
        help='Output directory for jobs and params (default: %(default)s)'
    )
    parser.add_argument(
        '--results-dir',
        type=Path,
        default=Path('results/barcode_count_sweep'),
        help='Results directory for benchmark outputs (default: %(default)s)'
    )
    parser.add_argument(
        '--columba-repo',
        type=str,
        default=None,
        help='Absolute path to Columba repository (required for slurm profile, not needed for singularity profile)'
    )
    
    args = parser.parse_args()
    
    generate_barcode_count_sweep(
        args.data_dir,
        args.output_dir,
        args.results_dir,
        args.columba_repo
    )


if __name__ == '__main__':
    main()
