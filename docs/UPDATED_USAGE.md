# QUIK Pipeline - Updated Execution Guide

## ✅ Changes Made

The pipeline has been updated to **remove HPC module loading** from the default profiles and focus on **portable execution methods** (Singularity and Conda).

### What Changed:

1. ✅ **Removed module loading** from process definition
2. ✅ **Default profiles** now use only Singularity or Conda
3. ✅ **Modules profile** created for backward compatibility
4. ✅ **Cleaner separation** of execution methods

---

## 🚀 Recommended Usage (Standard Nextflow Best Practices)

### Option 1: Singularity (Recommended for Production)

**Local execution:**
```bash
nextflow run main.nf -params-file test_params.json -profile singularity
```

**On PBS cluster:**
```bash
nextflow run main.nf -params-file test_params.json -profile pbs,singularity
```

**On VSC (PBS + Singularity combined):**
```bash
nextflow run main.nf -params-file test_params.json -profile vsc_singularity
```

### Option 2: Conda (Recommended for Non-Container Users)

**Local execution:**
```bash
nextflow run main.nf -params-file test_params.json -profile conda
```

**On PBS cluster:**
```bash
nextflow run main.nf -params-file test_params.json -profile pbs,conda
```

**On VSC (PBS + Conda combined):**
```bash
nextflow run main.nf -params-file test_params.json -profile vsc_conda
```

---

## 📋 All Available Profiles

| Profile | Description | Use Case | Command |
|---------|-------------|----------|---------|
| **singularity** | Singularity container | ✅ Recommended for reproducibility | `-profile singularity` |
| **conda** | Conda environment | ✅ Recommended for non-container | `-profile conda` |
| **docker** | Docker container | Local dev with Docker | `-profile docker` |
| **conda_minimal** | Minimal conda (faster) | Testing | `-profile conda_minimal` |
| **modules** | HPC modules | VSC backward compat | `-profile modules` |
| **pbs** | PBS scheduler only | Combine with singularity/conda | `-profile pbs,singularity` |
| **slurm** | SLURM scheduler only | Combine with singularity/conda | `-profile slurm,singularity` |
| **vsc_singularity** | PBS + Singularity | VSC one-command | `-profile vsc_singularity` |
| **vsc_conda** | PBS + Conda | VSC one-command | `-profile vsc_conda` |
| **vsc_modules** | PBS + Modules | VSC old method | `-profile vsc_modules` |
| **local** | Local executor | Testing locally | `-profile local,singularity` |
| **test** | Small resources | Quick tests | `-profile test,singularity` |

---

## 🎯 Quick Reference by Use Case

### I want reproducibility and portability
```bash
nextflow run main.nf -params-file params.json -profile singularity
```

### I'm on VSC and want the fastest setup
```bash
# First run (creates conda env, ~5 min)
nextflow run main.nf -params-file params.json -profile vsc_conda

# Subsequent runs (instant)
nextflow run main.nf -params-file params.json -profile vsc_conda -resume
```

### I'm on VSC and want reproducibility
```bash
nextflow run main.nf -params-file params.json -profile vsc_singularity
```

### I don't have containers or conda (VSC legacy)
```bash
nextflow run main.nf -params-file params.json -profile vsc_modules
```

### I'm testing locally without a cluster
```bash
# With Singularity
nextflow run main.nf -params-file params.json -profile local,singularity

# With Conda
nextflow run main.nf -params-file params.json -profile local,conda
```

---

## 📊 Profile Comparison

| Aspect | Singularity | Conda | Modules |
|--------|-------------|-------|---------|
| **Setup time (first run)** | 2-5 min (auto-pull) | 5-30 min (env creation) | None |
| **Setup time (subsequent)** | Instant | Instant | None |
| **Portability** | ✅ High | ⚠️ Medium | ❌ Low |
| **Reproducibility** | ✅ Excellent | ⚠️ Good | ❌ Poor |
| **Speed** | ⚡ Fast | ⚡ Fast | ⚡ Fastest |
| **Disk space** | ~1-2 GB (cached) | ~2-3 GB (env) | None |
| **GPU support** | ✅ Native | ✅ From env | ✅ From modules |
| **Publication ready** | ✅ Yes | ⚠️ Maybe | ❌ No |

---

## 🔧 Migration from Old Setup

### If you were using:
```bash
nextflow run main.nf -params-file test_params.json
```

### Now use (recommended):
```bash
# Option 1: Singularity (best for reproducibility)
nextflow run main.nf -params-file test_params.json -profile vsc_singularity

# Option 2: Conda (best for development)
nextflow run main.nf -params-file test_params.json -profile vsc_conda

# Option 3: Modules (backward compatible)
nextflow run main.nf -params-file test_params.json -profile vsc_modules
```

---

## 💡 Tips and Best Practices

### Pre-create Conda Environment (Faster)

Instead of letting Nextflow create it on each run:

```bash
# Create once
conda env create -f envs/quik_cuda.yml

# Update nextflow.config to use the named environment:
# conda = 'quik_cuda'  # instead of conda = "${projectDir}/envs/quik_cuda.yml"

# Run pipeline
nextflow run main.nf -params-file test_params.json -profile conda
```

### Use Resume for Failed Runs

```bash
nextflow run main.nf -params-file test_params.json -profile singularity -resume
```

### Combine Multiple Profiles

```bash
# PBS scheduler + Singularity container + Test resources
nextflow run main.nf -params-file test_params.json -profile pbs,singularity,test
```

### Check Which Container/Environment is Used

```bash
# Look in the .nextflow.log or work directory
cat work/*/*/.command.run | grep -E "container|conda"
```

---

## 🐛 Troubleshooting

### No default profile specified

**Error:**
```
ERROR ~ No execution environment specified
```

**Solution:** Always specify a profile:
```bash
nextflow run main.nf -params-file test_params.json -profile singularity
```

### Singularity not found

**Error:**
```
ERROR ~ Singularity not installed
```

**Solution:** Use conda or modules instead:
```bash
nextflow run main.nf -params-file test_params.json -profile conda
```

### Conda environment creation fails

**Error:**
```
Failed to create Conda environment
```

**Solution 1:** Use Singularity instead (faster, easier)
```bash
nextflow run main.nf -params-file test_params.json -profile singularity
```

**Solution 2:** Pre-create the environment
```bash
conda env create -f envs/quik_cuda.yml
# Then edit nextflow.config: conda = 'quik_cuda'
```

### Module not found error (old setup)

**Error:**
```
ERROR ~ Module CUDA/12.6.0 not found
```

**Solution:** Use Singularity or Conda profiles (recommended):
```bash
nextflow run main.nf -params-file test_params.json -profile singularity
```

Or explicitly use the modules profile:
```bash
nextflow run main.nf -params-file test_params.json -profile vsc_modules
```

---

## 📝 Summary of Changes

### Before (Old Setup):
- ❌ Default execution used HPC modules
- ❌ Not portable to other systems
- ❌ Module loading hardcoded in process

### After (New Setup):
- ✅ Default execution uses Singularity/Conda
- ✅ Portable to any system
- ✅ Modules optional (backward compatibility)
- ✅ Follows Nextflow best practices
- ✅ Publication-ready

### Backward Compatibility:
If you need the old behavior with modules:
```bash
nextflow run main.nf -params-file test_params.json -profile vsc_modules
```

---

## 🎓 Learn More

- [Nextflow Containers Documentation](https://www.nextflow.io/docs/latest/container.html)
- [Nextflow Conda Documentation](https://www.nextflow.io/docs/latest/conda.html)
- [Singularity User Guide](https://sylabs.io/guides/latest/user-guide/)
- See also: `docs/EXECUTION_METHODS.md` for detailed setup instructions
