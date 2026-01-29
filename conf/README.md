# Configuration Guide

This directory contains modular configuration files for the Barcode Calling Benchmark pipeline.

## Configuration Files

### `base.config`
**Purpose**: Defines default process resources and reporting settings common to all execution environments.

**Contains**:
- Default CPU, memory, and time allocations for each process
- GPU requirements for QUIK and RandomBarcodes
- Reporting configuration (timeline, trace, DAG)

### `modules.config`
**Purpose**: Process-specific settings independent of executor or environment.

**Contains**:
- Process labels (CPU/GPU requirements)
- Conda environment assignments for local execution
- Tool-specific configurations

### `standard.config`
**Purpose**: Generic resource allocations for standard execution.

**Contains**:
- Default resource settings by process label
- No executor-specific settings

### `executors/`
**Purpose**: Executor-specific configurations.

**Files**:
- `local.config` - Local machine execution settings
- `slurm.config` - SLURM HPC scheduler with module loading

---

## Usage Examples

### Local Execution with Conda
```bash
nextflow run main.nf -profile conda -params-file params.json
```
- Local executor
- Pure conda environments (no HPC modules)
- Best for development and testing

### Local Execution with Singularity
```bash
nextflow run main.nf -profile singularity,local -params-file params.json
```
- Local executor
- Singularity containers with GPU support (`--nv`)
- Good for reproducibility

### SLURM with HPC Modules (Recommended for HPC)
```bash
nextflow run main.nf -profile slurm -params-file params.json
```
- SLURM scheduler
- Loads optimized HPC modules (PyTorch-bundle, CMake, GCCcore)
- GPU allocation via `--gres=gpu:N`
- RandomBarcodes and Columba use HPC modules instead of conda

### SLURM with Conda (Alternative)
```bash
nextflow run main.nf -profile conda,slurm -params-file params.json
```
- SLURM scheduler
- Uses conda environments for all tools
- Slower than HPC modules but more portable

---

## Profile Decision Tree

```
Where are you running?
│
├─ HPC with SLURM
│   │
│   ├─ Want optimized HPC performance?
│   │   └─ Use: -profile slurm
│   │      (RandomBarcodes & Columba use HPC modules)
│   │
│   └─ Need portable conda environments?
│       └─ Use: -profile conda,slurm
│
└─ Local workstation / development
    │
    ├─ Want conda environments?
    │   └─ Use: -profile conda
    │
    └─ Want Singularity containers?
        └─ Use: -profile singularity,local
```

---

## Environment Management

### RandomBarcodes & Columba

**Profile-dependent behavior:**

| Profile | RandomBarcodes | Columba |
|---------|----------------|---------|
| `slurm` | HPC modules (PyTorch-bundle + CUDA) | HPC modules (CMake + GCCcore) |
| `conda,slurm` | Conda (`envs/randombarcodes.yml`) | Conda (`envs/columba.yml`) |
| `conda` | Conda (`envs/randombarcodes.yml`) | Conda (`envs/columba.yml`) |
| `singularity,local` | Container (pytorch/pytorch:2.1.0) | Conda (`envs/columba.yml`) |

**Implementation:**
- Module files contain conda directives for local execution
- `slurm.config` overrides conda directives to `null` and loads HPC modules
- Ensures optimized builds on HPC, portable environments elsewhere

### QUIK

**Always uses conda** (`envs/quik_minimal.yml`) - builds from source in all environments.

---

## Customization

### Modifying Resource Requirements

Edit `conf/base.config` or `conf/standard.config`:

```groovy
withName: 'QUIK_BARCODE_CALLING' {
    cpus   = 4      // Increase from default
    memory = 64.GB  // Increase from default
    time   = 4.h    // Increase from default
}
```

### Adapting to Different HPC Systems

Copy `conf/executors/slurm.config` and modify:

1. Change executor name (if needed)
2. Update module names to match your system
3. Adjust `clusterOptions` format for your scheduler
4. Update cluster names in GPU allocation section

Example for different SLURM system:
```groovy
// In your custom executor config
withLabel: use_gpu {
    beforeScript = 'module load PyTorch/2.1.2-CUDA-12.1'  // Your module name
    clusterOptions = "--gres=gpu:1 --partition=gpu_partition"  // Your cluster options
}
```

---

## Best Practices

1. **Parameter files**: Always use `-params-file params.json` for reproducibility
2. **Profile selection**: Choose the appropriate profile for your environment
3. **Test locally**: Use `-profile conda` for development before HPC submission
4. **Monitor resources**: Check generated reports in `results/pipeline_info/`
5. **Cache management**: Conda/Singularity caches are stored in scratch directories

---

## Troubleshooting

### "Module not found" errors on SLURM
- Module names in `slurm.config` don't match your HPC system
- **Solution**: Update module names or use `-profile conda,slurm` instead

### "CUDA not available" errors with RandomBarcodes
- PyTorch module isn't loading correctly
- **Solution**: Check module availability: `module avail PyTorch`
- **Alternative**: Use `-profile conda,slurm` to use conda PyTorch

### Slow conda environment creation
- First-time environment build can be slow
- **Solution**: Environments are cached; subsequent runs are fast
- **Alternative**: Use Singularity containers (`-profile singularity,local`)

### CMake errors when building Columba
- CMake module not available or too old (requires ≥3.14)
- **Solution**: Use `-profile conda,slurm` (conda provides CMake 3.20+)

### Permission errors with cache directories
- Cache directories not writable
- **Solution**: Set environment variables before running:
  ```bash
  export NXF_CONDA_CACHEDIR=/path/to/writable/cache
  export SINGULARITY_CACHEDIR=/path/to/writable/singularity
  ```

---

## Additional Resources

- **Main README**: `../README.md` - Pipeline usage and benchmark reproduction
- **Institutional configs**: `institutional/` - Site-specific examples
- **Config documentation**: `../docs/CONFIG_USAGE.md` - Detailed configuration guide
