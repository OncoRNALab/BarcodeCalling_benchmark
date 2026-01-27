#!/usr/bin/env python3
"""
Script to generate all config files and PBS job scripts for barcode generation and read simulation
"""

import os
from pathlib import Path

# Define parameters
barcode_lengths = [36, 34, 32, 30, 28]
codeword_counts = [85000, 42000, 21000]

error_rates = {
    'low': {'srate': 0.02, 'irate': 0.03, 'drate': 0.13},
    'medium': {'srate': 0.03, 'irate': 0.04, 'drate': 0.14},
    'high': {'srate': 0.03, 'irate': 0.15, 'drate': 0.14}
}

# Base directories
base_dir = Path("/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes")
config_dir = base_dir / "config_files"
jobs_dir = base_dir / "jobs"
outputs_dir = base_dir / "outputs" / "benchmark_85K_42K_21K"

# Create directories
config_dir.mkdir(exist_ok=True)
jobs_dir.mkdir(exist_ok=True)
outputs_dir.mkdir(exist_ok=True)

# Template for barcode generation config
barcode_config_template = """N: {N} # Number of codewords
M: {M} # Length of a codeword (nt)
filename_1: "{filename_1}" # Output file path for subset 1
filename_2: "{filename_2}" # Output file path for subset 2
picklefilename: "{picklefilename}" # Pickle file path
fac: 8
homomax: 3
gmax: 0.27
cyclemax: 2.1
Q: 1000000 # Number of simulated reads
nave: 4 # Average Poisson number of reads from each randomly selected codeword
srate: 0.04 
irate: 0.05
drate: 0.14
readsfilename: "{readsfilename}" # Output file path for reads
answersfilename: "{answersfilename}" # Output file path for answers
Nthresh: 9 # Levenshtein score threshold
best_path: "{best_path}"
"""

# Template for simulation config
sim_config_template = """N: {N} # Number of codewords
M: {M} # Length of a codeword (nt)
filename_1: "{filename_1}" # Input barcode file path for subset 1
filename_2: "{filename_2}" # Input barcode file path for subset 2
picklefilename: "{picklefilename}" # Pickle file path
fac: 8
homomax: 3
gmax: 0.27
cyclemax: 2.1
Q: 1000000 # Number of simulated reads
nave: 4 # Average Poisson number of reads from each randomly selected codeword
srate: {srate} 
irate: {irate}
drate: {drate}
readsfilename: "{readsfilename}" # Output file path for reads
answersfilename: "{answersfilename}" # Output file path for answers
Nthresh: 9 # Levenshtein score threshold
best_path: "{best_path}"
"""

# Template for PBS job script
pbs_template = """#!/bin/bash
#PBS -N {job_name}
#PBS -l nodes=1:ppn=1
#PBS -l walltime=24:00:00
#PBS -l mem=32gb

module load PyTorch/2.6.0-foss-2024a

cd $PBS_O_WORKDIR

{commands}
"""

print("Generating configuration files and PBS job scripts...")
print("=" * 80)

# Step 1: Generate barcode generation config files and PBS jobs
print("\n1. Creating barcode generation configs and PBS jobs...")
barcode_configs = []

for length in barcode_lengths:
    for count in codeword_counts:
        count_label = f"{count//1000}K"
        
        # Create output directory for this barcode set
        barcode_output_dir = outputs_dir / f"{count_label}_{length}nt"
        barcode_output_dir.mkdir(exist_ok=True, parents=True)
        
        # Config file name
        config_name = f"config_benchmark_{count_label}_{length}nt_bargen.yaml"
        config_path = config_dir / config_name
        
        # File paths
        filename_1 = str(barcode_output_dir / f"barcodes_{count_label}_{length}_subset1")
        filename_2 = str(barcode_output_dir / f"barcodes_{count_label}_{length}_subset2")
        picklefilename = filename_1 + ".pkl"
        readsfilename = str(barcode_output_dir / f"reads_{count_label}_{length}_placeholder")
        answersfilename = str(barcode_output_dir / f"answers_{count_label}_{length}_placeholder")
        best_path = str(barcode_output_dir / f"best_{count_label}_{length}_placeholder.txt")
        
        # Create config file
        config_content = barcode_config_template.format(
            N=count,
            M=length,
            filename_1=filename_1,
            filename_2=filename_2,
            picklefilename=picklefilename,
            readsfilename=readsfilename,
            answersfilename=answersfilename,
            best_path=best_path
        )
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"   Created: {config_name}")
        
        # Store for later reference
        barcode_configs.append({
            'length': length,
            'count': count,
            'count_label': count_label,
            'config_name': config_name,
            'filename_1': filename_1,
            'output_dir': barcode_output_dir
        })
        
        # Create PBS job script
        job_name = f"bargen_{count_label}_{length}nt"
        pbs_name = f"job_bargen_{count_label}_{length}nt.pbs"
        pbs_path = jobs_dir / pbs_name
        
        commands = f"python {base_dir}/scripts/1_BarcodeGen_split.py --config {config_path}"
        
        pbs_content = pbs_template.format(
            job_name=job_name,
            commands=commands
        )
        
        with open(pbs_path, 'w') as f:
            f.write(pbs_content)
        
        print(f"   Created: {pbs_name}")

# Step 2: Generate simulation config files and PBS jobs
print("\n2. Creating read simulation configs and PBS jobs...")

for barcode_cfg in barcode_configs:
    length = barcode_cfg['length']
    count = barcode_cfg['count']
    count_label = barcode_cfg['count_label']
    filename_1 = barcode_cfg['filename_1']
    filename_2 = filename_1.replace('subset1', 'subset2')
    picklefilename = filename_1 + ".pkl"
    output_dir = barcode_cfg['output_dir']
    
    for error_level, error_params in error_rates.items():
        # Config file name
        config_name = f"config_benchmark_{count_label}_{length}nt_sim_{error_level}.yaml"
        config_path = config_dir / config_name
        
        # File paths
        readsfilename = str(output_dir / f"reads_{count_label}_{length}_{error_level}")
        answersfilename = str(output_dir / f"answers_{count_label}_{length}_{error_level}")
        best_path = str(output_dir / f"best_{count_label}_{length}_{error_level}.txt")
        
        # Create config file
        config_content = sim_config_template.format(
            N=count,
            M=length,
            filename_1=filename_1,
            filename_2=filename_2,
            picklefilename=picklefilename,
            srate=error_params['srate'],
            irate=error_params['irate'],
            drate=error_params['drate'],
            readsfilename=readsfilename,
            answersfilename=answersfilename,
            best_path=best_path
        )
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"   Created: {config_name}")
        
        # Create PBS job script
        job_name = f"simgen_{count_label}_{length}nt_{error_level}"
        pbs_name = f"job_simgen_{count_label}_{length}nt_{error_level}.pbs"
        pbs_path = jobs_dir / pbs_name
        
        commands = f"python {base_dir}/scripts/2_SimGen_split.py --config {config_path}"
        
        pbs_content = pbs_template.format(
            job_name=job_name,
            commands=commands
        )
        
        with open(pbs_path, 'w') as f:
            f.write(pbs_content)
        
        print(f"   Created: {pbs_name}")

print("\n" + "=" * 80)
print("SUMMARY:")
print(f"  - Created {len(barcode_configs)} barcode generation config files")
print(f"  - Created {len(barcode_configs)} barcode generation PBS job files")
print(f"  - Created {len(barcode_configs) * len(error_rates)} simulation config files")
print(f"  - Created {len(barcode_configs) * len(error_rates)} simulation PBS job files")
print(f"  - Total config files: {len(barcode_configs) + len(barcode_configs) * len(error_rates)}")
print(f"  - Total PBS job files: {len(barcode_configs) + len(barcode_configs) * len(error_rates)}")
print(f"\nOutput directory: {outputs_dir}")
print(f"Config files directory: {config_dir}")
print(f"PBS job files directory: {jobs_dir}")
print("\nTo submit all barcode generation jobs:")
print(f"  cd {jobs_dir}")
print(f"  for f in job_bargen_*.pbs; do qsub $f; done")
print("\nTo submit all simulation jobs (after barcodes are generated):")
print(f"  for f in job_simgen_*.pbs; do qsub $f; done")
print("=" * 80)
