# Barcode Calling Benchmark - Complete Setup Guide

This guide provides step-by-step instructions to download data, generate jobs, and analyze results for all benchmark experiments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Data Download from Zenodo](#data-download-from-zenodo)
3. [Generate Jobs and Parameters](#generate-jobs-and-parameters)
4. [Run Benchmarks](#run-benchmarks)
5. [Analyze Results with Notebooks](#analyze-results-with-notebooks)
6. [Results Directory Structure](#results-directory-structure)

---

## Prerequisites

### Software Requirements

- **Nextflow**: Version 25.04.8 or later
- **Python**: Version 3.8 or later
- **SLURM**: For job submission
- **Jupyter**: For running analysis notebooks

### Tools Required

- **RandomBarcodes**: GPU-accelerated barcode matcher
- **QUIK**: Fast k-mer based barcode caller
- **Columba**: CPU-based alignment tool

---

## Data Download from Zenodo

All benchmark datasets are available on Zenodo. Download the following archives:

###  1. Error Rate & 1M Scaling Benchmarks

**Dataset**: `benchmark_85K_42K_21K.tar.gz`  
**Zenodo DOI**: [INSERT_DOI_HERE]  
**Size**: ~XX GB

```bash
# Download
wget https://zenodo.org/record/[RECORD_ID]/files/benchmark_85K_42K_21K.tar.gz

# Extract
tar -xzf benchmark_85K_42K_21K.tar.gz

# Expected directory structure:
# benchmark_85K_42K_21K/
# ├── 21K_36nt/
# ├── 42K_36nt/
# └── 85K_36nt/
```

**Location for scripts**:
```bash
DATA_DIR=/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K
```

### 2. Parameter Sweep Benchmarks

**Dataset**: `benchmark_parameter_sweeps.tar.gz`  
**Zenodo DOI**: [INSERT_DOI_HERE]  
**Size**: ~XX GB

```bash
# Download
wget https://zenodo.org/record/[RECORD_ID]/files/benchmark_parameter_sweeps.tar.gz

# Extract
tar -xzf benchmark_parameter_sweeps.tar.gz

# Expected directory structure:
# benchmark_parameter_sweeps/
# ├── 21K_28nt/
# ├── 21K_30nt/
# ├── 21K_32nt/
# ├── 21K_34nt/
# └── 21K_36nt/
```

**Location for scripts**:
```bash
DATA_DIR=/user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_parameter_sweeps
```

### 3. Real Data Benchmarks

#### 3a. FASTQ Files

**Datasets**: Real sequencing data  
**Zenodo DOI**: [INSERT_DOI_HERE]  
**Size**: ~XX GB

```bash
# Create directory
mkdir -p real_data_files

# Download all FASTQ.gz files
cd real_data_files
wget https://zenodo.org/record/[RECORD_ID]/files/Munchen_25024_1in4_S4_L001_R1_001.fastq.gz
wget https://zenodo.org/record/[RECORD_ID]/files/Munchen_25024_1in4_S4_L001_R2_001.fastq.gz
wget https://zenodo.org/record/[RECORD_ID]/files/Munchen_25025_1in20_S5_L001_R1_001.fastq.gz
wget https://zenodo.org/record/[RECORD_ID]/files/Munchen_25025_1in20_S5_L001_R2_001.fastq.gz
wget https://zenodo.org/record/[RECORD_ID]/files/Munchen_25026_4in1_S6_L001_R1_001.fastq.gz
wget https://zenodo.org/record/[RECORD_ID]/files/Munchen_25026_4in1_S6_L001_R2_001.fastq.gz
cd ..
```

**Location for scripts**:
```bash
DATA_DIR=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/real_data_files
```

#### 3b. Barcode References

**Dataset**: `BCseq_barcodes.tar.gz`  
**Zenodo DOI**: [INSERT_DOI_HERE]  
**Size**: ~XX MB

```bash
# Download
wget https://zenodo.org/record/[RECORD_ID]/files/BCseq_barcodes.tar.gz

# Extract (creates BCseq_barcodes/ directory)
tar -xzf BCseq_barcodes.tar.gz

# Expected structure:
# BCseq_barcodes/
# ├── Realbar_1in4_column_major.txt
# ├── Realbar_1in20_column_major.txt
# ├── Realbar_4in1_column_major.txt
# ├── Decoybar_1in4_column_major.txt
# ├── Decoybar_1in20_column_major.txt
# └── Decoybar_4in1_column_major.txt
```

**Location for scripts**:
```bash
BARCODE_DIR=/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BCseq_barcodes
```

---

## Generate Jobs and Parameters

All generation scripts are located in `bin/` and create SLURM job files and parameter JSONs.

### 1. Error Rate Benchmark

**Purpose**: Test tools across 3 barcode counts × 3 error rates (27 experiments, 200K reads each)

```bash
cd BarCall_benchmark

python3 bin/generate_jobs_and_params_error_rate.py \
    --data-dir /user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K \
    --output-dir error_rate_benchmark \
    --results-dir results/error_rate_benchmark
```

**Output**:
- Jobs: `error_rate_benchmark/jobs/*.sh`
- Params: `error_rate_benchmark/params/*.json`
- Results will go to: `results/error_rate_benchmark/`
- Reports will go to: `results/error_rate_benchmark/reports/`

### 2. 1M Scaling Benchmark

**Purpose**: Test tools across 3 barcode counts (9 experiments, 1M reads each)

```bash
cd BarCall_benchmark

python3 bin/generate_jobs_and_params_1M_scaling.py \
    --data-dir /user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K \
    --output-dir 1million_reads \
    --results-dir results/scaling_1M_benchmark
```

**Output**:
- Jobs: `1million_reads/jobs/*.sh`
- Params: `1million_reads/params/*.json`
- Results will go to: `results/scaling_1M_benchmark/`
- Reports will go to: `results/scaling_1M_benchmark/reports/`

### 3. Runtime Benchmark

**Purpose**: Test performance across different read counts (9 experiments per tool)

```bash
cd BarCall_benchmark

python3 bin/generate_jobs_and_params_runtime.py \
    --data-dir /user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K \
    --output-dir runtime_benchmarks \
    --results-dir results/runtime_benchmark
```

**Output**:
- Jobs: `runtime_benchmarks/{tool}/jobs/*.sh`
- Params: `runtime_benchmarks/{tool}/params/*.json`
- Results will go to: `results/runtime_benchmark/`
- Reports will go to: `results/runtime_benchmark/reports/`

### 4. Parameter Sweep Benchmarks

**Purpose**: Test tools across parameter ranges for 5 barcode lengths (28, 30, 32, 34, 36nt)

```bash
cd BarCall_benchmark

python3 bin/generate_jobs_and_params_parameter_sweep.py \
    --data-dir /user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_parameter_sweeps \
    --output-dir parameter_sweeps \
    --results-dir results/parameter_sweep
```

**Output**:
- Jobs: `parameter_sweeps/{length}nt/{tool}/jobs/*.sh`
- Params: `parameter_sweeps/{length}nt/{tool}/params/*.json`
- Results will go to: `results/parameter_sweep/results_{length}nt/`
- Reports will go to: `results/parameter_sweep/results_{length}nt/reports/`

### 5. Real Data Benchmark

**Purpose**: Test tools on real sequencing data (18 experiments: 3 arrays × 2 barcode sets × 3 tools)

```bash
cd BarCall_benchmark

python3 bin/generate_jobs_and_params_real_data.py \
    --data-dir /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/real_data_files \
    --barcode-dir /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BCseq_barcodes \
    --output-dir real_data \
    --results-dir results/real_data
```

**Output**:
- Jobs: `real_data/{tool}/jobs/*.sh`
- Params: `real_data/{tool}/params/*.json`
- Results will go to: `results/real_data/`
- Reports will go to: `results/real_data/reports/`

---

## Run Benchmarks

### Submit Individual Jobs

```bash
# Example: Submit one job
cd BarCall_benchmark
sbatch error_rate_benchmark/jobs/randombarcodes_21K_low.sh
```

### Submit All Jobs for a Benchmark

```bash
# Error rate benchmark
bash error_rate_benchmark/submit_all_error_rate_benchmarks.sh

# 1M scaling benchmark
bash 1million_reads/submit_all_1M_benchmarks.sh

# Runtime benchmark
bash runtime_benchmarks/submit_all_runtime_benchmarks.sh

# Parameter sweeps (by barcode length)
bash parameter_sweeps/28nt/submit_all_28nt.sh
bash parameter_sweeps/30nt/submit_all_30nt.sh
bash parameter_sweeps/32nt/submit_all_32nt.sh
bash parameter_sweeps/34nt/submit_all_34nt.sh
bash parameter_sweeps/36nt/submit_all_36nt.sh

# Real data benchmark
bash real_data/submit_all_real_data.sh
```

### Monitor Jobs

```bash
# Check job status
squeue -u $USER

# Check specific job
squeue -j <job_id>

# Check logs
tail -f error_rate_benchmark/logs/*.out
```

---

## Analyze Results with Notebooks

All analysis notebooks are in the `notebooks/` directory and are configured to load data from the correct results directories.

### Notebook-to-Results Mapping

| Notebook | Benchmark | Results Directory | Purpose |
|----------|-----------|-------------------|---------|
| `errorrate_benchmark_200K.ipynb` | Error Rate | `results/error_rate_benchmark` | Analyze performance across error rates |
| `Fullset_benchmark_1M.ipynb` | 1M Scaling | `results/scaling_1M_benchmark` | Analyze scalability to 1M reads |
| `runtime_analysis.ipynb` | Runtime | `results/runtime_benchmark` | Analyze computational performance |
| `precision_recall_curves_28_36nt.ipynb` | Parameter Sweep | `results/parameter_sweep` | Precision-recall curves for 28/36nt |
| `parameter_sweep_analysis_30_32_34nt.ipynb` | Parameter Sweep | `results/parameter_sweep` | Performance analysis for 30/32/34nt |
| `real_data_comparison.ipynb` | Real Data | `results/real_data` | Compare tools on real data |

### Run a Notebook

```bash
cd BarCall_benchmark/notebooks

# Start Jupyter
jupyter notebook

# Or use JupyterLab
jupyter lab

# Then open the desired notebook
```

### Expected Workflow

1. **Generate jobs** using the commands above
2. **Submit jobs** to SLURM
3. **Wait for completion** (check logs)
4. **Run notebooks** to analyze results

---

## Results Directory Structure

After running all benchmarks, your results directory will look like this:

```
results/
├── error_rate_benchmark/
│   ├── randombarcodes/
│   │   ├── 21K_36nt_low/
│   │   ├── 21K_36nt_medium/
│   │   ├── 21K_36nt_high/
│   │   └── ... (9 total)
│   ├── quik/
│   │   └── ... (9 total)
│   ├── columba/
│   │   └── ... (9 total)
│   └── reports/
│       ├── RB_21K_36nt_low_report.html
│       ├── RB_21K_36nt_low_timeline.html
│       └── ... (81 HTML files: 27 × 3)
│
├── scaling_1M_benchmark/
│   ├── randombarcodes/
│   │   ├── 21K_36nt/
│   │   ├── 42K_36nt/
│   │   └── 85K_36nt/
│   ├── quik/
│   │   └── ... (3 total)
│   ├── columba/
│   │   └── ... (3 total)
│   └── reports/
│       └── ... (27 HTML files: 9 × 3)
│
├── runtime_benchmark/
│   ├── randombarcodes/
│   │   ├── 200reads/
│   │   ├── 2Kreads/
│   │   └── ... (9 total)
│   ├── quik/
│   │   └── ... (9 total)
│   ├── columba/
│   │   └── ... (9 total)
│   └── reports/
│       └── ... (81 HTML files)
│
├── parameter_sweep/
│   ├── results_28nt/
│   │   ├── randombarcodes_sweep/
│   │   ├── quik_sweep/
│   │   ├── columba_sweep/
│   │   └── reports/
│   ├── results_30nt/
│   │   └── ...
│   ├── results_32nt/
│   │   └── ...
│   ├── results_34nt/
│   │   └── ...
│   └── results_36nt/
│       └── ...
│
└── real_data/
    ├── randombarcodes/
    │   ├── 21k/
    │   ├── 21k_decoy/
    │   ├── 42k/
    │   └── ... (6 total)
    ├── quik/
    │   └── ... (6 total)
    ├── columba/
    │   └── ... (6 total)
    └── reports/
        └── ... (54 HTML files: 18 × 3)
```

---

## Troubleshooting

### Common Issues

#### 1. Data Directory Not Found

```bash
ERROR: Data directory not found: /path/to/data
```

**Solution**: Verify the data directory path and ensure you've extracted the Zenodo archives.

#### 2. Module Not Found

```bash
ERROR: Nextflow module not available
```

**Solution**: Load the Nextflow module before running:
```bash
ml Nextflow/25.04.8
```

#### 3. Permission Denied

```bash
Permission denied: ./job.sh
```

**Solution**: The generation scripts should make files executable, but if not:
```bash
chmod +x error_rate_benchmark/jobs/*.sh
```

#### 4. Notebook Can't Find Results

**Solution**: Verify the results directory exists and matches the path in the notebook:
```bash
ls -la results/error_rate_benchmark/
```

---

## Summary of Commands

### Complete Workflow

```bash
# 1. Download data (see Data Download section)

# 2. Generate all jobs
cd BarCall_benchmark

python3 bin/generate_jobs_and_params_error_rate.py \
    --data-dir /user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K \
    --output-dir error_rate_benchmark \
    --results-dir results/error_rate_benchmark

python3 bin/generate_jobs_and_params_1M_scaling.py \
    --data-dir /user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K \
    --output-dir 1million_reads \
    --results-dir results/scaling_1M_benchmark

python3 bin/generate_jobs_and_params_runtime.py \
    --data-dir /user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_85K_42K_21K \
    --output-dir runtime_benchmarks \
    --results-dir results/runtime_benchmark

python3 bin/generate_jobs_and_params_parameter_sweep.py \
    --data-dir /user/gent/446/vsc44685/DataVO_dir/RandomBarcodes/outputs/benchmark_parameter_sweeps \
    --output-dir parameter_sweeps \
    --results-dir results/parameter_sweep

python3 bin/generate_jobs_and_params_real_data.py \
    --data-dir /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/real_data_files \
    --barcode-dir /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BCseq_barcodes \
    --output-dir real_data \
    --results-dir results/real_data

# 3. Submit jobs (example for one benchmark)
bash error_rate_benchmark/submit_all_error_rate_benchmarks.sh

# 4. Monitor
squeue -u $USER

# 5. Analyze
cd notebooks
jupyter notebook
```

---

## Citation

If you use these benchmarks in your research, please cite:

```
[INSERT CITATION HERE]
```

---

## Contact

For questions or issues, please open an issue on GitHub or contact:

- [INSERT CONTACT INFO]

---

**Last Updated**: 2026-01-25  
**Version**: 1.0
