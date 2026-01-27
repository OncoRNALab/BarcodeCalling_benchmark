# Conda Environment Setup for QUIK

## ⚠️ Important Note About Conda and CUDA

Installing CUDA toolkit via conda can be problematic because:
1. Conda CUDA may conflict with system CUDA drivers
2. Conda CUDA packages are large (~2-3 GB)
3. GPU driver compatibility issues
4. Slower environment solving

**Recommendation**: Use **Singularity containers** instead for reproducibility, or use system CUDA with a minimal conda environment.

---

## Option 1: Minimal Conda (Recommended for Conda Users)

This approach uses system/module CUDA and only installs build tools via conda.

### Create Environment

```bash
# Create minimal environment (no CUDA)
conda env create -f envs/quik_cuda_simple.yml

# Activate environment
conda activate quik_cuda_simple

# Load system CUDA (on HPC)
module load CUDA/12.6.0

# Verify
nvcc --version  # Should show system CUDA
cmake --version  # From conda
g++ --version   # From conda
```

### Use with Nextflow

Update `nextflow.config`:
```groovy
process {
    withName: 'QUIK_BARCODE_CALLING' {
        conda = "${projectDir}/envs/quik_cuda_simple.yml"
        module = ['CUDA/12.6.0']  // Load CUDA from modules
    }
}
```

---

## Option 2: Full Conda with CUDA (Not Recommended)

If you must use conda CUDA (slow and large):

```bash
# Create full environment with conda CUDA
conda env create -f envs/quik_cuda.yml

# This will download ~2-3 GB and take 10-30 minutes
```

**Issues you may encounter**:
- ❌ CUDA driver version mismatch
- ❌ Long solve times
- ❌ Large environment size
- ❌ GPU not recognized

---

## Option 3: Pre-create Environment (Faster Pipeline Runs)

Instead of letting Nextflow create the environment each time, pre-create it:

```bash
# Create environment once
conda env create -f envs/quik_cuda_simple.yml

# Verify it works
conda activate quik_cuda_simple
module load CUDA/12.6.0
nvcc --version
```

Update `nextflow.config` to use the named environment:
```groovy
process {
    withName: 'QUIK_BARCODE_CALLING' {
        conda = 'quik_cuda_simple'  // Use pre-created environment name
        module = ['CUDA/12.6.0']
    }
}
```

Run pipeline:
```bash
nextflow run main.nf -params-file test_params.json -profile conda
```

---

## Troubleshooting

### Error: `mamba: command not found`

**Solution 1**: Disable mamba in `nextflow.config`
```groovy
conda {
    conda.enabled = true
    conda.useMamba = false  // Changed from true
}
```

**Solution 2**: Install mamba (optional, faster)
```bash
conda install -n base -c conda-forge mamba
```

### Error: `CUDA not found` or `nvcc: command not found`

**Solution**: Load CUDA from system modules
```bash
module load CUDA/12.6.0
nvcc --version  # Verify it works
```

In Nextflow, combine conda profile with module loading:
```groovy
process {
    withName: 'QUIK_BARCODE_CALLING' {
        conda = 'quik_cuda_simple'
        module = ['CUDA/12.6.0', 'CMake/3.29.3-GCCcore-13.3.0']
    }
}
```

### Error: `CUDA driver version mismatch`

This happens when conda CUDA version doesn't match your GPU driver.

**Solution**: Use system CUDA instead
```bash
# Don't use envs/quik_cuda.yml
# Use envs/quik_cuda_simple.yml instead
conda env create -f envs/quik_cuda_simple.yml
```

### Error: Environment solving is very slow

**Solution 1**: Use mamba (faster conda)
```bash
conda install -n base -c conda-forge mamba
```

**Solution 2**: Use simpler environment
```bash
# Use quik_cuda_simple.yml instead of quik_cuda.yml
conda env create -f envs/quik_cuda_simple.yml
```

**Solution 3**: Switch to Singularity (recommended)
```bash
nextflow run main.nf -params-file test_params.json -profile singularity
```

---

## Why Containers are Better Than Conda for CUDA

| Aspect | Conda | Singularity |
|--------|-------|-------------|
| **Setup time** | 10-30 min | 2-5 min (auto-pull) |
| **Size** | 2-3 GB | 1-2 GB |
| **CUDA support** | ⚠️ Tricky | ✅ Native |
| **Reproducibility** | ⚠️ Medium | ✅ High |
| **Speed** | 🐢 Slower | ⚡ Fast |
| **Best for** | Development | Production |

---

## Recommended Workflow

### For Development/Testing
```bash
# Quick: Use HPC modules (no environment setup)
nextflow run main.nf -params-file test_params.json

# OR: Use minimal conda + system CUDA
conda env create -f envs/quik_cuda_simple.yml
nextflow run main.nf -params-file test_params.json -profile conda
```

### For Production/Publication
```bash
# Use Singularity (best reproducibility)
nextflow run main.nf -params-file test_params.json -profile singularity
```

---

## Example: Complete Setup with Minimal Conda

```bash
# 1. Create conda environment (one-time, ~2 minutes)
cd envs/
conda env create -f quik_cuda_simple.yml

# 2. Test the environment
conda activate quik_cuda_simple
module load CUDA/12.6.0
nvcc --version        # System CUDA
cmake --version       # Conda CMake
g++ --version         # Conda GCC

# 3. Run pipeline
cd ..
nextflow run main.nf -params-file test_params.json -profile conda

# The profile will automatically:
# - Activate the conda environment
# - Load required modules (CUDA, CMake)
# - Build and run QUIK
```

---

## Cleanup

### Remove Conda Environment
```bash
conda env remove -n quik_cuda_simple
# OR
conda env remove -n quik_cuda
```

### Clean Nextflow Conda Cache
```bash
# Remove cached conda environments
rm -rf $HOME/.nextflow/conda/*

# OR specify in nextflow.config:
conda.cacheDir = '/path/to/shared/conda/cache'
```

---

## Summary: Choose Your Path

| If you want... | Use this... | Command |
|---------------|-------------|---------|
| **Fastest setup** | HPC modules | `nextflow run main.nf -params-file test_params.json` |
| **Reproducibility** | Singularity | `nextflow run main.nf -params-file test_params.json -profile singularity` |
| **Conda (simple)** | Minimal conda + modules | Create `quik_cuda_simple`, then `-profile conda` |
| **Full conda** | Full conda (slow) | Create `quik_cuda`, wait 30 min, then `-profile conda` |

**Our recommendation**: Use Singularity for production, HPC modules for quick testing.
