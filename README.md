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
- **Singularity/Apptainer** (for local execution with containers)
- **SLURM** (for HPC execution with modules)

### Tool-Specific Requirements

#### QUIK & RandomBarcodes
- Conda environments provided in `envs/`
- Containers available for Singularity execution
- Nextflow handles dependency management automatically

#### Columba
**Two execution modes:**

**1. Local execution with Singularity** (`-profile local,singularity`)
- Uses pre-built container from Quay.io: `oras://quay.io/francoaps/columba_vanilla:latest`
- **No manual installation required** - container is automatically pulled and cached
- **No `columba_repo` parameter needed**
- Container includes Columba 2.0.3 with all dependencies

**2. HPC execution with SLURM** (`-profile slurm`)
- Requires manual Columba installation
- Clone and build Columba from source:
  ```bash
  cd /path/to/your/software
  git clone https://github.com/biointec/columba.git
  cd columba
  bash build_script.sh Vanilla
  ```
- **Must provide `columba_repo` parameter** in JSON files pointing to the cloned directory
- Pipeline uses HPC modules (CMake/GCCcore) for compilation

---

## HPC Module Configuration

### Default Modules (UGent HPC - Joltik/Accelgor)

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

### Customizing for Your HPC System

If you're using a different HPC system, you'll need to modify the module names to match your environment:

#### Step 1: Check Available Modules

```bash
# List all available modules
module avail

# Search for specific packages
module spider CMake
module spider PyTorch
module spider CUDA
module spider GCC
```

#### Step 2: Modify Configuration File

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

#### Step 3: Required Software Versions

Make sure your modules provide:
- **CMake**: ≥ 3.20
- **CUDA**: ≥ 11.8 (for GPU tools)
- **PyTorch**: ≥ 2.0 with CUDA support
- **GCC/g++**: ≥ 11.0 (for Columba)

#### Alternative: Skip Module Loading

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

---

## Singularity/Apptainer Cache Configuration

### Avoiding Home Directory Disk Quota Issues

By default, Singularity/Apptainer stores container images and temporary files in your home directory (`~/.apptainer/cache`), which can quickly exceed disk quotas when pulling large container images.

**All generated job scripts automatically configure cache directories to use scratch space** by exporting these environment variables before running Nextflow:

```bash
SCRATCH_DIR="${VSC_SCRATCH_VO_USER:-${VSC_SCRATCH:-$HOME/scratch}}"
export APPTAINER_TMPDIR="$SCRATCH_DIR/.apptainer/tmp"
export APPTAINER_CACHEDIR="$SCRATCH_DIR/.apptainer/cache"
export SINGULARITY_CACHEDIR="$SCRATCH_DIR/singularity"
export NXF_SINGULARITY_CACHEDIR="$SCRATCH_DIR/.apptainer/cache"
```

### Manual Execution

If you're running Nextflow commands manually (not using generated job scripts), **export these variables before running Nextflow**:

```bash
# Set cache directories to scratch
SCRATCH_DIR="${VSC_SCRATCH_VO_USER:-${VSC_SCRATCH:-$HOME/scratch}}"
export APPTAINER_TMPDIR="$SCRATCH_DIR/.apptainer/tmp"
export APPTAINER_CACHEDIR="$SCRATCH_DIR/.apptainer/cache"
export SINGULARITY_CACHEDIR="$SCRATCH_DIR/singularity"
export NXF_SINGULARITY_CACHEDIR="$SCRATCH_DIR/.apptainer/cache"

# Create cache directories
mkdir -p "$APPTAINER_TMPDIR" "$APPTAINER_CACHEDIR" "$SINGULARITY_CACHEDIR"

# Now run Nextflow
nextflow run main.nf -profile local,singularity -params-file params.json
```

### Why This Is Necessary

These environment variables must be set **before** running Nextflow because:
1. Nextflow pulls container images **before** launching processes
2. At image pull time, it uses the shell environment where the `nextflow` command runs
3. Process-level environment variables (set in `conf/executors/*.config`) only apply to spawned processes, not to Nextflow's image pulling

### Customizing for Other HPC Systems

If your HPC uses different scratch directory environment variables:
1. Modify the `SCRATCH_DIR` variable in generated job scripts
2. Or set it manually before running Nextflow:
   ```bash
   export SCRATCH_DIR="/your/scratch/path"
   ```

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

The pipeline supports two main execution modes:

#### 1. Local execution with Singularity (`-profile local,singularity`)
- Uses Singularity containers for all tools
- **Recommended for testing and reproducibility**
- Columba uses pre-built container (no `columba_repo` needed)
- Example:
  ```bash
  nextflow run main.nf \
      --tool columba \
      --barcode_file data/barcodes.fasta \
      --r1_fastq data/reads_R1.fastq \
      --r2_fastq data/reads_R2.fastq \
      --sample_id test_columba \
      --identity_threshold 80 \
      --outdir results/test \
      -profile local,singularity
  ```

#### 2. HPC execution with SLURM (`-profile slurm`)
- Uses SLURM scheduler with HPC modules
- **Recommended for production benchmarks on HPC clusters**
- Columba requires `columba_repo` parameter (path to cloned repository)
- Example:
  ```bash
  nextflow run main.nf \
      --tool columba \
      --barcode_file data/barcodes.fasta \
      --r1_fastq data/reads_R1.fastq \
      --r2_fastq data/reads_R2.fastq \
      --sample_id test_columba \
      --identity_threshold 80 \
      --columba_repo /path/to/columba \
      --outdir results/test \
      -profile slurm
  ```

**Note for Columba users:**
- `local,singularity`: Container binaries used automatically (no setup needed)
- `slurm`: Must download and provide `columba_repo` parameter (see Software Requirements)

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
