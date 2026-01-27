# Conda Environments for Barcode Calling Pipeline

## Overview

The pipeline uses different conda environments for different tools to manage dependencies effectively.

---

## Environment Files

### 1. `randombarcodes.yml` - **For RandomBarcodes Tool**

**Purpose**: GPU-accelerated Python-based barcode calling

**Key Dependencies**:
- ✅ Python 3.11
- ✅ **PyTorch ≥2.0** with CUDA 11.8 support (CRITICAL for GPU)
- ✅ NumPy ≥1.24
- ✅ TorchVision, TorchAudio

**Used by**: `modules/randombarcodes.nf`

**Installation**:
```bash
conda env create -f envs/randombarcodes.yml
conda activate randombarcodes
```

**GPU Requirements**: CUDA 11.8 or compatible

---

### 2. `python_basic.yml` - **For Precision Calculation**

**Purpose**: Basic Python environment for precision/recall metrics

**Key Dependencies**:
- ✅ Python 3.11
- ✅ BioPython
- ✅ NumPy
- ✅ Pandas
- ✅ **PyTorch with CUDA** (added for compatibility)

**Used by**: `modules/precision_process.nf`

**Installation**:
```bash
conda env create -f envs/python_basic.yml
conda activate python_basic
```

---

### 3. `quik_cuda.yml` - **For QUIK Tool**

**Purpose**: CUDA-enabled C++ compilation environment

**Key Dependencies**:
- CUDA toolkit
- CMake
- C++ compiler (GCC)

**Used by**: `modules/quik_clean_process.nf`

---

### 4. `quik_cuda_simple.yml` - **Simplified QUIK Environment**

**Purpose**: Minimal CUDA environment for QUIK

**Used by**: Alternative for `quik_clean_process.nf`

---

## Environment Selection

The pipeline automatically uses the correct environment based on:
1. The selected tool (`--tool quik` or `--tool randombarcodes`)
2. The execution profile (`-profile conda`, `-profile singularity`, etc.)

### Using Conda Profile

```bash
# Automatically uses randombarcodes.yml
nextflow run main.nf -profile conda --tool randombarcodes ...

# Automatically uses quik_cuda.yml
nextflow run main.nf -profile conda --tool quik ...
```

---

## Critical Package: PyTorch with CUDA

### Why PyTorch is Required

RandomBarcodes uses PyTorch for:
- GPU-accelerated distance calculations
- Efficient batch processing
- Parallel GPU execution

**Without PyTorch, RandomBarcodes will fail immediately!**

### Installation Verification

After creating the environment, verify PyTorch + CUDA:

```bash
conda activate randombarcodes

# Check PyTorch version
python -c "import torch; print('PyTorch version:', torch.__version__)"

# Check CUDA availability
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

# Check CUDA version
python -c "import torch; print('CUDA version:', torch.version.cuda)"

# Check GPU count
python -c "import torch; print('GPU count:', torch.cuda.device_count())"
```

**Expected Output**:
```
PyTorch version: 2.0.1 (or higher)
CUDA available: True
CUDA version: 11.8
GPU count: 1 (or more)
```

If `CUDA available: False`, then:
1. Check CUDA driver installation: `nvidia-smi`
2. Reinstall PyTorch with correct CUDA version
3. Ensure GPU resources are allocated in your job scheduler

---

## Troubleshooting

### Problem: "No module named 'torch'"

**Cause**: PyTorch not installed in the environment

**Solution**:
```bash
conda activate randombarcodes
conda install pytorch>=2.0 pytorch-cuda=11.8 -c pytorch -c nvidia
```

### Problem: "CUDA not available" (torch.cuda.is_available() = False)

**Cause 1**: PyTorch installed without CUDA support

**Solution**:
```bash
conda activate randombarcodes
# Reinstall with CUDA
conda install pytorch pytorch-cuda=11.8 -c pytorch -c nvidia
```

**Cause 2**: CUDA driver not loaded or incompatible

**Solution**:
```bash
# Check GPU
nvidia-smi

# Load CUDA module (on HPC)
module load CUDA/12.6.0

# Verify driver version matches CUDA version
```

**Cause 3**: GPU not allocated in job

**Solution**:
```bash
# For PBS
qsub -l nodes=1:ppn=2:gpus=1 ...

# For SLURM
sbatch --gres=gpu:1 ...

# Check environment variable
echo $CUDA_VISIBLE_DEVICES  # Should show GPU ID (e.g., "0")
```

### Problem: Environment creation fails

**Cause**: Channel priority or package conflicts

**Solution**:
```bash
# Clean conda cache
conda clean --all

# Create with specific channels
conda env create -f envs/randombarcodes.yml --override-channels

# Or use mamba (faster)
conda install mamba -c conda-forge
mamba env create -f envs/randombarcodes.yml
```

### Problem: CUDA version mismatch

**Current environment**: CUDA 11.8 (in randombarcodes.yml)

**If you have different CUDA version**:

```yaml
# Edit randombarcodes.yml
dependencies:
  - pytorch>=2.0
  - pytorch-cuda=12.1  # Change to your CUDA version
```

**Available CUDA versions for PyTorch**:
- 11.7, 11.8 (most compatible)
- 12.1, 12.4 (newer systems)

Check your system CUDA version:
```bash
nvcc --version
nvidia-smi  # Shows driver version and max CUDA support
```

---

## Container Alternative

If conda environments are problematic, use containers:

### Singularity (Recommended for HPC)

```bash
nextflow run main.nf -profile singularity --tool randombarcodes ...
```

The pipeline will automatically pull:
- `docker://pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime`

### Docker (Local Testing)

```bash
nextflow run main.nf -profile docker --tool randombarcodes ...
```

---

## Environment Comparison

| Tool | Environment | Key Package | Size | GPU Required |
|------|-------------|-------------|------|--------------|
| RandomBarcodes | `randombarcodes.yml` | PyTorch + CUDA | ~5 GB | Yes |
| QUIK | `quik_cuda.yml` | CUDA + CMake | ~3 GB | Yes |
| Precision Calc | `python_basic.yml` | NumPy + Pandas | ~500 MB | No |

---

## Best Practices

1. **Use dedicated environments**: Don't mix QUIK and RandomBarcodes in the same env
2. **Verify GPU access**: Always check `nvidia-smi` before running
3. **Match CUDA versions**: Ensure PyTorch CUDA matches system CUDA driver
4. **Use containers on HPC**: Often more reliable than conda on shared systems
5. **Test environment first**: Run verification commands before starting pipeline

---

## Quick Setup Guide

### For RandomBarcodes

```bash
# Create environment
conda env create -f envs/randombarcodes.yml

# Activate
conda activate randombarcodes

# Verify
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Run pipeline
nextflow run main.nf -profile conda --tool randombarcodes -params-file test_params_randombarcodes.json
```

### For QUIK

```bash
# Create environment
conda env create -f envs/quik_cuda.yml

# Activate
conda activate quik_cuda

# Run pipeline
nextflow run main.nf -profile conda --tool quik -params-file test_params.json
```

---

## Notes

- **Python 3.11** is used for all environments (good compatibility with PyTorch 2.x)
- **PyTorch 2.0+** provides significant performance improvements over 1.x
- **CUDA 11.8** is widely supported and compatible with most GPU drivers
- Built-in Python modules (argparse, subprocess, re, gzip, csv) don't need explicit installation

---

## Support

If you encounter environment issues:
1. Check this documentation
2. Verify GPU access with `nvidia-smi`
3. Test PyTorch CUDA with verification commands
4. Consider using container profiles instead of conda
5. Check Nextflow logs in `.nextflow.log` and `work/` directories

---

*Last updated: January 6, 2026*

