#!/usr/bin/env python3
"""
Generate parameter files and job scripts for barcode count parameter sweep.
This sweep tests how barcode count (21K, 42K, 85K) affects optimal rejection thresholds
across different barcode lengths (28, 30, 32, 34, 36nt) for three tools:
- RandomBarcodes
- QUIK
- Columba

Total jobs: 240 (75 RandomBarcodes + 75 QUIK + 90 Columba)

Structure follows the project organization:
BarCall_benchmark/parameter_sweeps_barcode_count/{tool}/{count}_{length}nt/{params,jobs,logs}/
"""

import json
import os
from pathlib import Path

# Base configuration
BASE_DIR = "/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
PROJECT_DIR = BASE_DIR
NEXTFLOW_SCRIPT = f"{PROJECT_DIR}/main.nf"
NEXTFLOW_CONFIG = f"{PROJECT_DIR}/nextflow.config"

# Tool configurations
TOOLS = {
    'randombarcodes': {
        'name': 'RandomBarcodes',
        'thresholds': [5, 6, 7, 8, 9],
        'fixed_params': {
            'ntriage': 100,
            'gpus': 1
        },
        'resource_requirements': {
            'cpus': 1,
            'mem': '8G',
            'time': '04:00:00'
        }
    },
    'quik': {
        'name': 'QUIK',
        'thresholds': [5, 6, 7, 8, 9],
        'fixed_params': {
            'strategy': '4_mer_gpu_v4',
            'gpus': 1
        },
        'resource_requirements': {
            'cpus': 1,
            'mem': '8G',
            'time': '04:00:00'
        }
    },
    'columba': {
        'name': 'Columba',
        'thresholds': [77, 78, 79, 80, 81, 82],
        'fixed_params': {
            'cpus': 4
        },
        'resource_requirements': {
            'cpus': 16,
            'mem': '32G',
            'time': '04:00:00'
        }
    }
}

# Barcode configurations
BARCODE_LENGTHS = [28, 30, 32, 34, 36]
BARCODE_COUNTS = [21000, 42000, 85000]
BARCODE_COUNT_LABELS = {21000: '21K', 42000: '42K', 85000: '85K'}

# Data paths for each barcode count and length
DATA_PATHS = {
    21000: {
        'barcodes_path': {
            28: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_28nt/barcodes_21K_28_subset1",
            30: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_30nt/barcodes_21K_30_subset1",
            32: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_32nt/barcodes_21K_32_subset1",
            34: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_34nt/barcodes_21K_34_subset1",
            36: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_36nt/barcodes_21K_36_subset1"
        },
        'reads_path': {
            28: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_28nt/reads_21K_28_low_R1.fastq",
            30: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_30nt/reads_21K_30_low_R1.fastq",
            32: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_32nt/reads_21K_32_low_R1.fastq",
            34: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_34nt/reads_21K_34_low_R1.fastq",
            36: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_36nt/reads_21K_36_low_R1.fastq"
        },
        'reads_r2_path': {
            28: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_28nt/reads_21K_28_low_R2.fastq",
            30: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_30nt/reads_21K_30_low_R2.fastq",
            32: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_32nt/reads_21K_32_low_R2.fastq",
            34: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_34nt/reads_21K_34_low_R2.fastq",
            36: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_36nt/reads_21K_36_low_R2.fastq"
        },
        'answers_path': {
            28: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_28nt/answers_21K_28_low",
            30: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_30nt/answers_21K_30_low",
            32: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_32nt/answers_21K_32_low",
            34: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_34nt/answers_21K_34_low",
            36: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/21K_36nt/answers_21K_36_low"
        }
    },
    42000: {
        'barcodes_path': {
            28: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_28nt/barcodes_42K_28_subset1",
            30: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_30nt/barcodes_42K_30_subset1",
            32: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_32nt/barcodes_42K_32_subset1",
            34: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_34nt/barcodes_42K_34_subset1",
            36: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_36nt/barcodes_42K_36_subset1"
        },
        'reads_path': {
            28: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_28nt/reads_42K_28_low_R1.fastq",
            30: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_30nt/reads_42K_30_low_R1.fastq",
            32: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_32nt/reads_42K_32_low_R1.fastq",
            34: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_34nt/reads_42K_34_low_R1.fastq",
            36: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_36nt/reads_42K_36_low_R1.fastq"
        },
        'reads_r2_path': {
            28: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_28nt/reads_42K_28_low_R2.fastq",
            30: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_30nt/reads_42K_30_low_R2.fastq",
            32: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_32nt/reads_42K_32_low_R2.fastq",
            34: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_34nt/reads_42K_34_low_R2.fastq",
            36: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_36nt/reads_42K_36_low_R2.fastq"
        },
        'answers_path': {
            28: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_28nt/answers_42K_28_low",
            30: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_30nt/answers_42K_30_low",
            32: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_32nt/answers_42K_32_low",
            34: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_34nt/answers_42K_34_low",
            36: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/42K_36nt/answers_42K_36_low"
        }
    },
    85000: {
        'barcodes_path': {
            28: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_28nt/barcodes_85K_28_subset1",
            30: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_30nt/barcodes_85K_30_subset1",
            32: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_32nt/barcodes_85K_32_subset1",
            34: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_34nt/barcodes_85K_34_subset1",
            36: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_36nt/barcodes_85K_36_subset1"
        },
        'reads_path': {
            28: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_28nt/reads_85K_28_low_R1.fastq",
            30: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_30nt/reads_85K_30_low_R1.fastq",
            32: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_32nt/reads_85K_32_low_R1.fastq",
            34: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_34nt/reads_85K_34_low_R1.fastq",
            36: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_36nt/reads_85K_36_low_R1.fastq"
        },
        'reads_r2_path': {
            28: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_28nt/reads_85K_28_low_R2.fastq",
            30: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_30nt/reads_85K_30_low_R2.fastq",
            32: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_32nt/reads_85K_32_low_R2.fastq",
            34: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_34nt/reads_85K_34_low_R2.fastq",
            36: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_36nt/reads_85K_36_low_R2.fastq"
        },
        'answers_path': {
            28: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_28nt/answers_85K_28_low",
            30: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_30nt/answers_85K_30_low",
            32: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_32nt/answers_85K_32_low",
            34: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_34nt/answers_85K_34_low",
            36: "/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K_200K/85K_36nt/answers_85K_36_low"
        }
    }
}


def create_randombarcodes_params(barcode_count, barcode_length, threshold):
    """Create parameter file for RandomBarcodes."""
    count_label = BARCODE_COUNT_LABELS[barcode_count]
    paths = DATA_PATHS[barcode_count]
    
    params = {
        "barcode_file": paths['barcodes_path'][barcode_length],
        "r1_fastq": paths['reads_path'][barcode_length],
        "r2_fastq": paths['reads_r2_path'][barcode_length],
        "ground_truth": paths['answers_path'][barcode_length],
        "barcode_length": barcode_length,
        "n_barcodes": barcode_count,
        "gpus": TOOLS['randombarcodes']['fixed_params']['gpus'],
        "tool": "randombarcodes",
        "ntriage": TOOLS['randombarcodes']['fixed_params']['ntriage'],
        "nthresh": threshold,
        "sample_id": f"RB_{count_label}_{barcode_length}nt_t100_n{threshold}",
        "outdir": f"{BASE_DIR}/parameter_sweeps_barcode_count/randombarcodes/{count_label}_{barcode_length}nt/results/t100_n{threshold}"
    }
    
    return params


def create_quik_params(barcode_count, barcode_length, threshold):
    """Create parameter file for QUIK."""
    count_label = BARCODE_COUNT_LABELS[barcode_count]
    paths = DATA_PATHS[barcode_count]
    
    params = {
        "tool": "quik",
        "barcode_file": paths['barcodes_path'][barcode_length],
        "r1_fastq": paths['reads_path'][barcode_length],
        "r2_fastq": paths['reads_r2_path'][barcode_length],
        "ground_truth": paths['answers_path'][barcode_length],
        "barcode_length": barcode_length,
        "barcode_start": 0,
        "distance_measure": "SEQUENCE_LEVENSHTEIN",
        "strategy": TOOLS['quik']['fixed_params']['strategy'],
        "rejection_threshold": threshold,
        "sample_id": f"QUIK_{count_label}_{barcode_length}nt_4mer_r{threshold}",
        "outdir": f"{BASE_DIR}/parameter_sweeps_barcode_count/quik/{count_label}_{barcode_length}nt/results/4mer_r{threshold}"
    }
    
    return params


def create_columba_params(barcode_count, barcode_length, threshold):
    """Create parameter file for Columba."""
    count_label = BARCODE_COUNT_LABELS[barcode_count]
    paths = DATA_PATHS[barcode_count]
    
    params = {
        "tool": "columba",
        "barcode_file": paths['barcodes_path'][barcode_length],
        "r1_fastq": paths['reads_path'][barcode_length],
        "r2_fastq": paths['reads_r2_path'][barcode_length],
        "ground_truth": paths['answers_path'][barcode_length],
        "barcode_length": barcode_length,
        "barcode_window": f"0-{barcode_length}",
        "columba_repo": "/user/gent/446/vsc44685/ScratchVO_dir/columba",
        "identity_threshold": threshold,
        "sample_id": f"Columba_{count_label}_{barcode_length}nt_I{threshold}",
        "outdir": f"{BASE_DIR}/parameter_sweeps_barcode_count/columba/{count_label}_{barcode_length}nt/results/I{threshold}"
    }
    
    return params


def create_job_script(tool_key, barcode_count, barcode_length, threshold, param_file_path):
    """Create SLURM job script for a parameter sweep job following project structure."""
    tool_info = TOOLS[tool_key]
    count_label = BARCODE_COUNT_LABELS[barcode_count]
    
    # Create job name and work directory
    if tool_key == 'randombarcodes':
        job_name = f"RB_{count_label}_{barcode_length}nt_n{threshold}"
        work_dir = f"/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_barcode_count/{tool_key}/{count_label}_{barcode_length}nt/t100_n{threshold}"
    elif tool_key == 'quik':
        job_name = f"QK_{count_label}_{barcode_length}nt_r{threshold}"
        work_dir = f"/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_barcode_count/{tool_key}/{count_label}_{barcode_length}nt/4mer_r{threshold}"
    else:  # columba
        job_name = f"CB_{count_label}_{barcode_length}nt_I{threshold}"
        work_dir = f"/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_barcode_count/{tool_key}/{count_label}_{barcode_length}nt/I{threshold}"
    
    # Log file paths
    log_dir = f"{BASE_DIR}/parameter_sweeps_barcode_count/{tool_key}/{count_label}_{barcode_length}nt/logs"
    
    script = f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={tool_info['resource_requirements']['cpus']}
#SBATCH --time={tool_info['resource_requirements']['time']}
#SBATCH --mem={tool_info['resource_requirements']['mem']}
#SBATCH --output={log_dir}/{job_name}.out
#SBATCH --error={log_dir}/{job_name}.err

# Load Nextflow module
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="{PROJECT_DIR}"
WORK_DIR="{work_dir}"

# Create and move to unique work directory for this job to avoid lock conflicts
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Run pipeline
nextflow run "$PROJECT_DIR/main.nf" \\
    -c "$PROJECT_DIR/nextflow.config" \\
    -profile slurm \\
    -params-file {param_file_path} \\
    -work-dir "$WORK_DIR" \\
    -resume

echo "Job completed for {tool_info['name']} - {count_label} {barcode_length}nt threshold={threshold}"
"""
    
    return script


def main():
    """Generate all parameter files and job scripts."""
    
    print("="*80)
    print("BARCODE COUNT PARAMETER SWEEP - FILE GENERATOR")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Tools: {', '.join([TOOLS[t]['name'] for t in TOOLS])}")
    print(f"  Barcode lengths: {BARCODE_LENGTHS}")
    print(f"  Barcode counts: {[BARCODE_COUNT_LABELS[c] for c in BARCODE_COUNTS]}")
    print(f"  RandomBarcodes thresholds: {TOOLS['randombarcodes']['thresholds']}")
    print(f"  QUIK thresholds: {TOOLS['quik']['thresholds']}")
    print(f"  Columba thresholds: {TOOLS['columba']['thresholds']}")
    
    # Calculate total jobs
    rb_jobs = len(BARCODE_LENGTHS) * len(BARCODE_COUNTS) * len(TOOLS['randombarcodes']['thresholds'])
    quik_jobs = len(BARCODE_LENGTHS) * len(BARCODE_COUNTS) * len(TOOLS['quik']['thresholds'])
    columba_jobs = len(BARCODE_LENGTHS) * len(BARCODE_COUNTS) * len(TOOLS['columba']['thresholds'])
    total_jobs = rb_jobs + quik_jobs + columba_jobs
    
    print(f"\nTotal jobs to generate:")
    print(f"  RandomBarcodes: {rb_jobs}")
    print(f"  QUIK: {quik_jobs}")
    print(f"  Columba: {columba_jobs}")
    print(f"  TOTAL: {total_jobs}")
    print("="*80)
    
    # Track created files
    job_scripts_by_tool_count = {tool: {count: [] for count in BARCODE_COUNTS} for tool in TOOLS}
    
    # Generate files for each tool
    for tool_key, tool_info in TOOLS.items():
        print(f"\n{'='*80}")
        print(f"Generating files for {tool_info['name']}")
        print(f"{'='*80}")
        
        # Generate parameter files for each combination
        for barcode_count in BARCODE_COUNTS:
            count_label = BARCODE_COUNT_LABELS[barcode_count]
            
            for barcode_length in BARCODE_LENGTHS:
                # Create subdirectory structure for this barcode count and length
                base_count_length_dir = f"{BASE_DIR}/parameter_sweeps_barcode_count/{tool_key}/{count_label}_{barcode_length}nt"
                params_dir = f"{base_count_length_dir}/params"
                jobs_dir = f"{base_count_length_dir}/jobs"
                logs_dir = f"{base_count_length_dir}/logs"
                results_dir = f"{base_count_length_dir}/results"
                
                # Create directories
                for dir_path in [params_dir, jobs_dir, logs_dir, results_dir]:
                    os.makedirs(dir_path, exist_ok=True)
                
                for threshold in tool_info['thresholds']:
                    # Generate parameter file
                    if tool_key == 'randombarcodes':
                        params = create_randombarcodes_params(barcode_count, barcode_length, threshold)
                        param_filename = f"params_t100_n{threshold}.json"
                        job_filename = f"job_t100_n{threshold}.sh"
                    elif tool_key == 'quik':
                        params = create_quik_params(barcode_count, barcode_length, threshold)
                        param_filename = f"params_4mer_r{threshold}.json"
                        job_filename = f"job_4mer_r{threshold}.sh"
                    else:  # columba
                        params = create_columba_params(barcode_count, barcode_length, threshold)
                        param_filename = f"params_I{threshold}.json"
                        job_filename = f"job_I{threshold}.sh"
                    
                    # Write parameter file
                    param_file_path = f"{params_dir}/{param_filename}"
                    with open(param_file_path, 'w') as f:
                        json.dump(params, f, indent=4)
                    
                    # Generate job script
                    job_script = create_job_script(tool_key, barcode_count, barcode_length, threshold, param_file_path)
                    job_file_path = f"{jobs_dir}/{job_filename}"
                    with open(job_file_path, 'w') as f:
                        f.write(job_script)
                    
                    # Make job script executable
                    os.chmod(job_file_path, 0o755)
                    
                    # Track job script
                    job_scripts_by_tool_count[tool_key][barcode_count].append(job_file_path)
                    
                    print(f"  Created: {count_label} {barcode_length}nt threshold={threshold}")
    
    # Create submission scripts for each tool and barcode count
    print(f"\n{'='*80}")
    print("Creating submission scripts")
    print(f"{'='*80}")
    
    all_submit_scripts = []
    
    for tool_key in TOOLS:
        for barcode_count in BARCODE_COUNTS:
            count_label = BARCODE_COUNT_LABELS[barcode_count]
            
            submit_script_path = f"{BASE_DIR}/parameter_sweeps_barcode_count/{tool_key}/submit_all_{count_label}.sh"
            
            with open(submit_script_path, 'w') as f:
                f.write(f"""#!/bin/bash
# Submit all {TOOLS[tool_key]['name']} jobs for {count_label} barcodes

echo "Submitting {TOOLS[tool_key]['name']} jobs for {count_label} barcode count..."
echo "Total jobs: {len(job_scripts_by_tool_count[tool_key][barcode_count])}"
echo ""

""")
                
                for job_script in job_scripts_by_tool_count[tool_key][barcode_count]:
                    f.write(f"sbatch {job_script}\n")
                
                f.write(f'\necho ""\necho "All {TOOLS[tool_key]["name"]} jobs for {count_label} submitted!"\n')
            
            os.chmod(submit_script_path, 0o755)
            all_submit_scripts.append(submit_script_path)
            print(f"  Created: {submit_script_path}")
    
    # Create master submission script
    master_script_path = f"{BASE_DIR}/parameter_sweeps_barcode_count/submit_all_barcode_count_sweep.sh"
    
    with open(master_script_path, 'w') as f:
        f.write(f"""#!/bin/bash
# Master script to submit ALL barcode count parameter sweep jobs
# Total: {total_jobs} jobs ({rb_jobs} RandomBarcodes + {quik_jobs} QUIK + {columba_jobs} Columba)

echo "="*80
echo "BARCODE COUNT PARAMETER SWEEP - MASTER SUBMISSION SCRIPT"
echo "="*80
echo ""
echo "This will submit {total_jobs} jobs total:"
echo "  - RandomBarcodes: {rb_jobs} jobs"
echo "  - QUIK: {quik_jobs} jobs"
echo "  - Columba: {columba_jobs} jobs"
echo ""
echo "Across:"
echo "  - Barcode counts: {', '.join([BARCODE_COUNT_LABELS[c] for c in BARCODE_COUNTS])}"
echo "  - Barcode lengths: {', '.join([str(l) + 'nt' for l in BARCODE_LENGTHS])}"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "Starting job submission..."
echo ""

""")
        
        for submit_script in all_submit_scripts:
            f.write(f"bash {submit_script}\n")
            f.write('echo ""\n')
        
        f.write(f"""
echo "="*80
echo "All {total_jobs} jobs submitted!"
echo "="*80
echo ""
echo "Monitor jobs with: squeue -u $USER"
echo "Check logs in: {BASE_DIR}/parameter_sweeps_barcode_count/{{tool}}/{{count}}_{{length}}nt/logs/"
""")
    
    os.chmod(master_script_path, 0o755)
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"\nGenerated files:")
    print(f"  Parameter files: {total_jobs}")
    print(f"  Job scripts: {total_jobs}")
    print(f"  Submission scripts: {len(all_submit_scripts)}")
    print(f"  Master script: 1")
    print(f"\nDirectory structure:")
    print(f"  {BASE_DIR}/parameter_sweeps_barcode_count/")
    print(f"    {{tool}}/")
    print(f"      {{count}}_{{length}}nt/")
    print(f"        params/  - Parameter JSON files")
    print(f"        jobs/    - SLURM job scripts")
    print(f"        logs/    - Job output logs")
    print(f"        results/ - Pipeline results")
    print(f"\nTo submit all jobs:")
    print(f"  bash {master_script_path}")
    print(f"\nOr submit by tool/barcode count:")
    for submit_script in all_submit_scripts:
        print(f"  bash {submit_script}")
    print(f"\n{'='*80}")
    print("✓ Generation complete!")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
