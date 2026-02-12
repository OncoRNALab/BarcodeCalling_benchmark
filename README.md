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

## Execution Profiles

The pipeline supports two execution profiles that work with **all three tools** (QUIK, RandomBarcodes, Columba):

### 1. `local,singularity` — Container-based execution
- **Uses**: Singularity/Apptainer containers for all tools
- **Recommended for**: Testing, reproducibility, systems without SLURM
- **Requirements**: Singularity/Apptainer installed
- **Advantages**: 
  - No manual tool installation needed
  - Consistent across different systems
  - Pre-built containers from Quay.io
- **Example**:
  ```bash
  nextflow run main.nf -profile local,singularity -params-file params.json
  ```

### 2. `slurm` — HPC cluster execution
- **Uses**: SLURM scheduler with HPC modules
- **Recommended for**: Production benchmarks on HPC clusters
- **Requirements**: SLURM, HPC modules (CMake, CUDA, PyTorch, GCC)
- **Advantages**:
  - Optimized for HPC environments
  - Better resource management for large jobs
  - Uses system-provided CUDA/GPU libraries
- **Example**:
  ```bash
  nextflow run main.nf -profile slurm -params-file params.json
  ```

---

## Software Requirements

### Essential
- **Nextflow** ≥ 23.04 ([install guide](https://www.nextflow.io/docs/latest/getstarted.html))

### Profile-Specific Requirements

#### For `local,singularity` profile:
- **Singularity/Apptainer** (any recent version)
- **Sufficient disk space** for container cache (scratch space recommended)
- All tool containers are automatically pulled from Quay.io

#### For `slurm` profile:
- **SLURM** scheduler
- **HPC modules**: CMake, CUDA, PyTorch, GCC (see [HPC Module Configuration](#hpc-module-configuration))
- **Manual Columba installation** (see below)

### Tool-Specific Notes

#### QUIK & RandomBarcodes
- **`local,singularity`**: Fully containerized, no setup needed
- **`slurm`**: Compiled from source using HPC modules, no manual installation needed

#### Columba
- **`local,singularity`**: Fully containerized, no setup needed
- **`slurm`**: Requires manual installation
  ```bash
  cd /path/to/your/software
  git clone https://github.com/biointec/columba.git
  cd columba
  bash build_script.sh Vanilla
  ```
  Then provide `columba_repo` parameter in JSON files pointing to the cloned directory

---

## Profile Setup and Configuration

### Setup for `local,singularity` Profile

When using the `local,singularity` profile, you **must configure Apptainer/Singularity cache directories** to avoid home directory disk quota issues.

**Before running Nextflow, export these variables** (adjust paths to directories with sufficient disk space):

```bash
# Example: Using scratch space (recommended for HPC)
export APPTAINER_TMPDIR="${VSC_SCRATCH_VO_USER}/.apptainer/tmp"
export APPTAINER_CACHEDIR="${VSC_SCRATCH_VO_USER}/.apptainer/cache"
export SINGULARITY_CACHEDIR="${VSC_SCRATCH_VO_USER}/singularity"
export NXF_SINGULARITY_CACHEDIR="${VSC_SCRATCH_VO_USER}/.apptainer/cache"

# Create cache directories
mkdir -p "$APPTAINER_TMPDIR" "$APPTAINER_CACHEDIR" "$SINGULARITY_CACHEDIR"
```

**Why this is necessary**: Nextflow pulls container images before launching processes. The cache location must be configured in your shell environment to take effect during image pulling.

**For persistent configuration**, add these exports to your `~/.bashrc` or `~/.bash_profile`.

---

### Setup for `slurm` Profile

#### HPC Module Configuration

##### Default Modules (UGent HPC - Joltik/Accelgor)

When using `-profile slurm`, the pipeline automatically loads the following HPC modules:

#### For QUIK & RandomBarcodes (GPU tools):
```bash
module load CMake/3.26.3-GCCcore-12.3.0
module load PyTorch-bundle/2.1.2-foss-2023a-CUDA-12.1.1
```
- **CMake**: Required for compiling QUIK from source
- **PyTorch-bundle**: Provides PyTorch, CUDA, and dependencies for GPU acceleration

#### For Columba:
```bash
module load CMake/3.29.3-GCCcore-13.3.0  # For building
module load GCCcore/13.3.0               # For indexing and alignment
```
- **CMake**: Required for compiling Columba
- **GCCcore**: Provides g++ and build tools

##### Customizing for Your HPC System

If you're using a different HPC system, you'll need to modify the module names to match your environment:

**Step 1: Check Available Modules**

```bash
# List all available modules
module avail

# Search for specific packages
module spider CMake
module spider PyTorch
module spider CUDA
module spider GCC
```

**Step 2: Modify Configuration File**

Edit `conf/executors/slurm.config` and update the module names:

```groovy
// For GPU processes (QUIK & RandomBarcodes)
withLabel: use_gpu {
    beforeScript = 'module load CMake/YOUR_VERSION && module load PyTorch-bundle/YOUR_VERSION'
}

// For Columba
withName: 'COLUMBA_BUILD' {
    beforeScript = 'module load CMake/YOUR_VERSION'
}
withName: 'COLUMBA_INDEX' {
    beforeScript = 'module load GCCcore/YOUR_VERSION'
}
withName: 'COLUMBA_ALIGN' {
    beforeScript = 'module load GCCcore/YOUR_VERSION'
}
```

**Step 3: Required Software Versions**

Make sure your modules provide:
- **CMake**: ≥ 3.20
- **CUDA**: ≥ 11.8 (for GPU tools)
- **PyTorch**: ≥ 2.0 with CUDA support
- **GCC/g++**: ≥ 11.0 (for Columba)

**Alternative: Skip Module Loading**

If your HPC doesn't use modules, or software is already in PATH, you can remove module loading:

```groovy
// For GPU processes
withLabel: use_gpu {
    beforeScript = ''  // Empty - assumes software is in PATH
}

// For Columba
withName: 'COLUMBA_BUILD' {
    beforeScript = ''
}
```

**Note**: Job submission scripts also load `Nextflow/25.04.8` module. If your HPC uses a different module name or if Nextflow is already available, modify the generated job scripts accordingly.

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

# Download real data barcodes (for real data benchmark)
wget https://zenodo.org/records/18387161/files/BCseq_barcodes.tar.gz -O data/BCseq_barcodes.tar.gz
tar -xzf data/BCseq_barcodes.tar.gz -C data/
# This creates: data/BCseq_barcodes/ containing real and decoy barcode files

# Download real sequencing data FASTQ files
cd data/
wget https://zenodo.org/record/18387161/files/Munchen_25024_1in4_S4_L001_R1_001.fastq.gz
wget https://zenodo.org/record/18387161/files/Munchen_25024_1in4_S4_L001_R2_001.fastq.gz
wget https://zenodo.org/record/18387161/files/Munchen_25024_1in2_S1_L001_R1_001.fastq.gz
wget https://zenodo.org/record/18387161/files/Munchen_25024_1in2_S1_L001_R2_001.fastq.gz
wget https://zenodo.org/record/18387161/files/Munchen_25024_1in1_S2_L001_R1_001.fastq.gz
wget https://zenodo.org/record/18387161/files/Munchen_25024_1in1_S2_L001_R2_001.fastq.gz
cd ..
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
├── BCseq_barcodes/                 # Real data barcodes (real and decoy)
│   ├── Realbar_1in1_column_major.txt   # 85K array barcodes
│   ├── Realbar_1in2_column_major.txt   # 42K array barcodes
│   ├── Realbar_1in4_column_major.txt   # 21K array barcodes
│   ├── Decoybar_1in1_column_major.txt  # 85K decoy barcodes
│   ├── Decoybar_1in2_column_major.txt  # 42K decoy barcodes
│   └── Decoybar_1in4_column_major.txt  # 21K decoy barcodes
└── Munchen_*.fastq.gz              # Real sequencing data FASTQ files
```

## Quick Start

### 1. Test the pipeline (single run)

#### Example 1: QUIK with `local,singularity` profile
```bash
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
    -profile local,singularity
```

#### Example 2: Columba with `slurm` profile
```bash
nextflow run main.nf \
    --tool columba \
    --barcode_file data/benchmark_85K_42K_21K_200K/21K_36nt/barcodes_21K_36_subset1 \
    --r1_fastq data/benchmark_85K_42K_21K_200K/21K_36nt/reads_21K_36_low_R1.fastq \
    --r2_fastq data/benchmark_85K_42K_21K_200K/21K_36nt/reads_21K_36_low_R2.fastq \
    --ground_truth data/benchmark_85K_42K_21K_200K/21K_36nt/answers_21K_36_low \
    --sample_id test_columba_21K \
    --identity_threshold 72 \
    --columba_repo /path/to/columba \
    --outdir results/test \
    -profile slurm
```

### 2. Reproduce full benchmarks

Each benchmark has a **generator script** in `bin/` that creates all job submission files and parameter JSONs.

## Benchmark Reproduction

**IMPORTANT**: All generator scripts create job submission files with relative paths. You must be in the **project root directory** when submitting jobs to SLURM:

```bash
cd /path/to/BarCall_benchmark  # Always run from project root!
sbatch error_rate_benchmark/jobs/some_job.sh
```

### Error-Rate Benchmark (3 tools × 3 barcode counts × 3 error rates = 27 runs)

```bash
# 1. Generate jobs and params (from project root)
python3 bin/generate_jobs_and_params_error_rate.py \
    --data-dir data/benchmark_85K_42K_21K_200K \
    --results-dir results/error_rate

# 2. Submit all jobs (from project root)
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

### Barcode Count Sweep (library size effects)

```bash
# 1. Generate jobs and params
# For SLURM profile (specify Columba installation path)
python3 bin/generate_jobs_and_params_barcode_count.py \
    --data-dir data/benchmark_85K_42K_21K_200K \
    --output-dir parameter_sweeps_barcode_count \
    --results-dir results/barcode_count_sweep \
    --columba-repo /path/to/columba

# For Singularity profile (no --columba-repo needed)
python3 bin/generate_jobs_and_params_barcode_count.py \
    --data-dir data/benchmark_85K_42K_21K_200K \
    --output-dir parameter_sweeps_barcode_count \
    --results-dir results/barcode_count_sweep

# 2. Submit jobs (example for 21K 28nt)
for job in parameter_sweeps_barcode_count/randombarcodes/21K_28nt/jobs/*.sh; do sbatch "$job"; done
for job in parameter_sweeps_barcode_count/quik/21K_28nt/jobs/*.sh; do sbatch "$job"; done
for job in parameter_sweeps_barcode_count/columba/21K_28nt/jobs/*.sh; do sbatch "$job"; done
# Submit all combinations (21K, 42K, 85K × 28nt, 36nt)
```

### Real Data Benchmark (photolithographic arrays)

```bash
# 1. Generate jobs and params
python3 bin/generate_jobs_and_params_real_data.py \
    --data-dir data/ \
    --barcode-dir data/BCseq_barcodes \
    --results-dir results/real_data

# 2. Submit all jobs
bash barcode_seq/submit_all_tools.sh
```

## Configuration

For detailed configuration options, see `conf/README.md`.

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
- `errorrate_benchmark_200K.ipynb`: Error-rate analysis
- `Fullset_benchmark_1M.ipynb`: 1M scaling analysis
- `runtime_analysis.ipynb`: Runtime/scaling analysis
- `precision_recall_curves_28_36nt.ipynb`: Parameter sweep analysis (28/36nt)
- `parameter_sweep_analysis_30_32_34nt.ipynb`: Parameter sweep analysis (30/32/34nt)
- `barcode_count_sweep_analysis.ipynb`: Barcode library size effects
- `real_data_comparison.ipynb`: Real data results and overlap analysis

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
├── parameter_sweeps_barcode_count/    # Barcode count sweep jobs/params (generated)
├── barcode_seq/                       # Real-data jobs/params (generated)
└── notebooks/                         # Jupyter analysis notebooks
```

## License

This benchmarking pipeline is released under [license TBD].  
Individual tools retain their original licenses.

## Contact

For questions or issues: [francoalexander.pomasoto@ugent.be](mailto:francoalexander.pomasoto@ugent.be)
