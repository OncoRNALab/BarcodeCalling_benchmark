# BarCall_benchmark: Barcode Calling Benchmark Pipeline

Reproducible benchmarking workflow for evaluating DNA barcode calling tools under high error rates.

## Overview

This repository provides a **Nextflow-based pipeline** to benchmark three barcode calling methods:
- **RandomBarcodes** (Press 2022) — trimer-statistics triage with GPU acceleration
- **QUIK** (Uphoff et al. 2026) — k-mer filtering with GPU acceleration  
- **Columba** (Renders et al. 2024) — lossless approximate matching using FM-index search schemes

The benchmarks evaluate accuracy (precision/recall), runtime, and scalability across:
- Multiple barcode lengths (28–36 nt)
- Multiple barcode library sizes (21k, 42k, 85k)
- Multiple error regimes (low, medium, high)
- Simulated and real sequencing data

## Software Requirements

### Essential
- **Nextflow** ≥ 23.04 ([install guide](https://www.nextflow.io/docs/latest/getstarted.html))
- **Conda** or **Singularity** (for dependency management)
- **SLURM** (if running on HPC) or local execution

### Conda environments
All tool-specific dependencies are provided as environment YML files in `envs/`. Nextflow will automatically create and activate them when using `-profile conda` or `-profile singularity`.

### Manual tool installation (optional)
If not using containers/conda, you can install:
- **QUIK**: build from source (see `bin/quik/README.md`)
- **RandomBarcodes**: Python + PyTorch + CUDA ([see Press 2022](https://github.com/...))
- **Columba**: clone and build from [Columba repo](https://github.com/biointec/columba)

## Data Download (Zenodo)

All benchmark datasets are deposited at **Zenodo DOI: [10.5281/zenodo.18387161](https://doi.org/10.5281/zenodo.18387161)**

### Download and extract

```bash
# Create data directory
mkdir -p data/

# Download simulated data (200k reads)
wget https://zenodo.org/record/18387161/files/benchmark_85K_42K_21K_200K.tar.gz -O data/benchmark_200K.tar.gz
tar -xzf data/benchmark_200K.tar.gz -C data/

# Download simulated data (1M reads)
wget https://zenodo.org/record/18387161/files/benchmark_85K_42K_21K.tar.gz -O data/benchmark_1M.tar.gz
tar -xzf data/benchmark_1M.tar.gz -C data/

# Download real sequencing data
cd data/
wget https://zenodo.org/record/18387161/files/Munchen_25024_1in4_S4_L001_R1_001.fastq.gz
wget https://zenodo.org/record/18387161/files/Munchen_25024_1in4_S4_L001_R2_001.fastq.gz
wget https://zenodo.org/record/18387161/files/Munchen_25024_1in2_S1_L001_R1_001.fastq.gz
wget https://zenodo.org/record/18387161/files/Munchen_25024_1in2_S1_L001_R2_001.fastq.gz
wget https://zenodo.org/record/18387161/files/Munchen_25024_1in1_S2_L001_R1_001.fastq.gz
wget https://zenodo.org/record/18387161/files/Munchen_25024_1in1_S2_L001_R2_001.fastq.gz
cd ..

# (Optional) Download barcode references for real data if not included in benchmark archives
```

### Expected directory structure after extraction

```
data/
├── benchmark_85K_42K_21K_200K/     # 200k simulated reads
│   ├── 21K_28nt/
│   │   ├── barcodes_21K_28_subset1
│   │   ├── answers_21K_28_low
│   │   ├── reads_21K_28_low_R1.fastq
│   │   └── reads_21K_28_low_R2.fastq
│   ├── 21K_36nt/
│   ├── 42K_28nt/
│   ├── ...
│   └── 85K_36nt/
├── benchmark_85K_42K_21K/          # 1M simulated reads
│   ├── 21K_36nt/
│   ├── 42K_36nt/
│   └── 85K_36nt/
└── Munchen_*.fastq.gz              # Real sequencing data
```

## Quick Start

### 1. Test the pipeline (single run)

```bash
# Example: Run QUIK on 21K 36nt barcodes
nextflow run main.nf \
    --tool quik \
    --barcode_file data/benchmark_85K_42K_21K_200K/21K_36nt/barcodes_21K_36_subset1 \
    --r1_fastq data/benchmark_85K_42K_21K_200K/21K_36nt/reads_21K_36_low_R1.fastq \
    --r2_fastq data/benchmark_85K_42K_21K_200K/21K_36nt/reads_21K_36_low_R2.fastq \
    --ground_truth data/benchmark_85K_42K_21K_200K/21K_36nt/answers_21K_36_low \
    --sample_id test_quik_21K \
    --strategy 4_mer_gpu_v4 \
    --rejection_threshold 8 \
    --outdir results/test \
    -profile slurm
```

### 2. Reproduce full benchmarks

Each benchmark has a **generator script** in `bin/` that creates all job submission files and parameter JSONs.

## Benchmark Reproduction

### Error-Rate Benchmark (3 tools × 3 barcode counts × 3 error rates = 27 runs)

```bash
# 1. Generate jobs and params
python3 bin/generate_jobs_and_params_error_rate.py \
    --data-dir data/benchmark_85K_42K_21K_200K \
    --results-dir results/error_rate

# 2. Submit all jobs
bash error_rate_benchmark/submit_all_error_rate_benchmarks.sh

# 3. Analyze results (see notebooks/)
```

### 1M Scaling Benchmark (3 tools × 3 barcode counts = 9 runs)

```bash
# 1. Generate jobs and params
python3 bin/generate_jobs_and_params_1M_scaling.py \
    --data-dir data/benchmark_85K_42K_21K \
    --results-dir results/1million_reads

# 2. Submit all jobs
bash 1million_reads/submit_all_1M_benchmarks.sh
```

### Runtime Benchmark (testing parallel scaling)

```bash
# 1. Generate jobs and params
python3 bin/generate_jobs_and_params_runtime.py \
    --data-dir data/benchmark_85K_42K_21K_200K \
    --results-dir results/runtime

# 2. Submit all jobs
bash runtime_benchmarks/SUBMIT_ALL_JOBS.sh
```

### Parameter Sweep (optimal threshold identification)

```bash
# 1. Generate jobs and params for all barcode lengths
python3 bin/generate_jobs_and_params_parameter_sweep.py \
    --data-dir data/benchmark_85K_42K_21K_200K \
    --results-dir results/parameter_sweeps \
    --barcode-lengths 28 30 32 34 36

# 2. Submit all jobs
bash parameter_sweeps/submit_all_parameter_sweeps.sh
```

### Real Data Benchmark (photolithographic arrays)

```bash
# 1. Generate jobs and params
python3 bin/generate_jobs_and_params_real_data.py \
    --data-dir data/ \
    --barcode-dir /path/to/real_and_decoy_barcodes \
    --results-dir results/real_data

# 2. Submit all jobs
bash barcode_seq/submit_all_tools.sh
```

## Configuration

### Profiles

- **`-profile slurm`**: For HPC with SLURM scheduler
- **`-profile local`**: For local execution
- **`-profile conda`**: Use Conda for dependencies
- **`-profile singularity`**: Use Singularity containers
- **Combined**: `-profile slurm,conda` or `-profile local,singularity`

See `conf/` for detailed configuration options.

### Customizing parameters

All benchmarks use generator scripts that accept:
- `--data-dir`: where you extracted Zenodo datasets
- `--results-dir`: where to write outputs
- `--output-dir`: where to write job/params files (optional; has sensible defaults)

Edit the generator scripts in `bin/` to change:
- Tool-specific parameters (ntriage, rejection thresholds, etc.)
- Resource allocations (CPUs, GPUs, memory, time limits)
- SLURM partitions/clusters

## Analysis

Jupyter notebooks for analyzing benchmark results are provided in `notebooks/`:
- `error_rate_benchmark_200K.ipynb`: Error-rate analysis
- `Fullset_benchmark_1M.ipynb`: 1M scaling analysis
- `barcode_count_sweep_analysis.ipynb`: Barcode library size effects
- `parameter_sweep_analysis_*.ipynb`: Parameter calibration
- `real_data_comparison.ipynb`: Real data results and overlap analysis
- `runtime_analysis.ipynb`: Runtime/scaling analysis

Tables and figures from the manuscript are exported to `notebooks/tables/` and `notebooks/figures/`.

## Citation

If you use this pipeline or benchmark data, please cite:

```
Poma-Soto et al. (2026). Benchmarking DNA Barcode Decoding Strategies Under High Error Rates.
DOI: 10.5281/zenodo.18387161
```

Original tool papers:
- **RandomBarcodes**: Press WH. (2022). PNAS Nexus, 1(5):pgac252
- **QUIK**: Uphoff RC et al. (2026). [publication details]
- **Columba**: Renders L et al. (2024). Bioinformatics

## Project Structure

```
BarCall_benchmark/
├── bin/                               # Generator scripts and helper utilities
│   ├── generate_jobs_and_params_*.py  # Benchmark generators
│   ├── calculate_precision*.py         # Metric calculation scripts
│   └── quik/                          # QUIK source code
├── envs/                              # Conda environment YML files
├── modules/                           # Nextflow process modules
├── conf/                              # Nextflow configuration
├── docs/                              # Extended documentation
├── main.nf                            # Main Nextflow workflow
├── error_rate_benchmark/              # Error-rate jobs/params (generated)
├── 1million_reads/                    # 1M scaling jobs/params (generated)
├── runtime_benchmarks/                # Runtime jobs/params (generated)
├── parameter_sweeps/                  # Parameter sweep jobs/params (generated)
├── barcode_seq/                       # Real-data jobs/params (generated)
└── notebooks/                         # Jupyter analysis notebooks
```

## License

This benchmarking pipeline is released under [license TBD].  
Individual tools retain their original licenses.

## Contact

For questions or issues: [franco.pomasoto@ugent.be](mailto:franco.pomasoto@ugent.be)
