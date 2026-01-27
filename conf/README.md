# Configuration Guide

This directory contains modular configuration files for the Barcode Calling Benchmark pipeline.

## Configuration Files

### `base.config`
**Purpose**: Defines default process resources and reporting settings that are common to all execution environments.

**Contains**:
- Default CPU, memory, and time allocations for each process
- GPU requirements for QUIK, RandomBarcodes
- Reporting configuration (timeline, trace, DAG)

### `hpc.config`
**Purpose**: HPC-specific configuration for systems with environment modules and PBS scheduler.

**Contains**:
- PBS/Torque executor settings
- Module loading via `beforeScript` directives (CUDA, CMake, GCC)
- GPU resource allocation in cluster options
- Conda cache directory configuration

**Use when**: Running on institutional HPC systems like VSC that use environment modules.

### `standard.config`
**Purpose**: Generic configuration using only conda environments or containers.

**Contains**:
- Local executor defaults
- Conda/Singularity/Docker settings
- No module system dependencies

**Use when**: Running on local workstations, cloud environments, or HPC systems without module loading.

---

## Usage Examples

### HPC with PBS + Conda (VSC HPC)
```bash
nextflow run main.nf -profile hpc_conda -params-file params.json
```
- Uses PBS scheduler
- Loads system modules (CUDA, CMake, GCC)
- Uses conda environments defined in workflow

### HPC with PBS + Singularity
```bash
nextflow run main.nf -profile hpc_singularity -params-file params.json
```
- Uses PBS scheduler
- Loads system modules for build dependencies
- Uses Singularity containers

### Standard with Conda (Local/Cloud)
```bash
nextflow run main.nf -profile conda -params-file params.json
```
- Local executor
- Pure conda environments (no modules)
- No HPC scheduler

### Standard with Singularity
```bash
nextflow run main.nf -profile singularity -params-file params.json
```
- Local executor
- Singularity containers
- No HPC scheduler

### Standard with Docker
```bash
nextflow run main.nf -profile docker -params-file params.json
```
- Local executor
- Docker containers
- GPU support enabled

### Combining Profiles

You can combine profiles for custom setups:

**PBS + Conda (without modules)**:
```bash
nextflow run main.nf -profile pbs,conda -params-file params.json
```

**SLURM + Singularity**:
```bash
nextflow run main.nf -profile slurm,singularity -params-file params.json
```

**Testing locally**:
```bash
nextflow run main.nf -profile local,conda,test -params-file params.json
```

---

## Profile Decision Tree

```
Are you on an HPC with environment modules?
│
├─ YES (e.g., VSC HPC)
│   │
│   ├─ Want to use Conda?
│   │   └─ Use: -profile hpc_conda
│   │
│   └─ Want to use Singularity?
│       └─ Use: -profile hpc_singularity
│
└─ NO (local workstation, cloud, or HPC without modules)
    │
    ├─ Want to use Conda?
    │   └─ Use: -profile conda
    │
    ├─ Want to use Singularity?
    │   └─ Use: -profile singularity
    │
    └─ Want to use Docker?
        └─ Use: -profile docker
```

---

## Customization

### Adding a New HPC System

1. Copy `hpc.config` to `hpc_newsystem.config`
2. Modify executor settings (e.g., change from PBS to SLURM)
3. Update module names to match your system
4. Adjust cluster options format
5. Add a new profile in `nextflow.config`:
```groovy
newsystem_conda {
    includeConfig 'conf/hpc_newsystem.config'
    conda.enabled = true
}
```

### Modifying Resource Requirements

Edit `conf/base.config` to change default CPU, memory, or time allocations:

```groovy
withName: 'QUIK_BARCODE_CALLING' {
    cpus   = 4  // Change from 2 to 4
    memory = 64.GB  // Change from 32 to 64
    time   = 4.h  // Change from 2h to 4h
}
```

### Adding New Modules (HPC)

Edit `conf/hpc.config` to add module loading for new processes:

```groovy
withName: 'MY_NEW_PROCESS' {
    beforeScript = 'module load MyModule/1.0 2>/dev/null || true'
}
```

---

## Best Practices

1. **Always use parameter files** (`-params-file params.json`) instead of command-line parameters for reproducibility
2. **Use appropriate profiles** based on your execution environment
3. **Test locally first** with `-profile local,conda,test` before submitting to HPC
4. **Monitor resource usage** using the generated reports in `results/` directory
5. **Cache environments**: Conda and Singularity caches are stored in `~/.nextflow/` to speed up subsequent runs

---

## Troubleshooting

### "Module not found" errors
- You're using an HPC profile but modules aren't available
- Solution: Use standard profiles instead (e.g., `conda` or `singularity`)

### "CUDA not available" errors  
- System modules aren't loaded properly
- Solution: Check module names in `hpc.config` match your system

### Slow conda environment creation
- Solution: Install mamba and set `conda.useMamba = true` in config

### Permission errors with Singularity cache
- Solution: Set custom cache directory in your profile or environment
  ```bash
  export NXF_SINGULARITY_CACHEDIR=/path/to/writable/dir
  ```

