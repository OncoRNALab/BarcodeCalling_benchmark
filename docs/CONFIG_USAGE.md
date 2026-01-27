# Configuration Quick Reference

## Overview

The pipeline configuration is organized into modular components:

```
conf/
├── base.config              # Resource labels (CPU, memory, time)
├── modules.config           # Process-specific settings
├── executors/
│   ├── local.config        # Local workstation execution
│   ├── pbs.config          # PBS/Torque scheduler
│   └── slurm.config        # SLURM scheduler
└── institutional/
    └── README.md           # Guide for creating HPC-specific configs
```

## Quick Usage Examples

### Local Execution

#### With Docker
```bash
nextflow run main.nf \
    -profile docker \
    --tool quik \
    --barcode_file barcodes.txt \
    --r1_fastq reads_R1.fastq.gz \
    --r2_fastq reads_R2.fastq.gz \
    --outdir results
```

#### With Singularity
```bash
nextflow run main.nf \
    -profile singularity \
    --tool randombarcodes \
    --barcode_file barcodes.txt \
    --r1_fastq reads_R1.fastq.gz \
    --r2_fastq reads_R2.fastq.gz \
    --outdir results
```

#### With Conda
```bash
nextflow run main.nf \
    -profile conda \
    --tool columba \
    --barcode_file barcodes.txt \
    --r1_fastq reads_R1.fastq.gz \
    --r2_fastq reads_R2.fastq.gz \
    --outdir results
```

### HPC Execution

#### PBS/Torque with Singularity
```bash
nextflow run main.nf \
    -profile singularity,pbs \
    --tool quik \
    --barcode_file barcodes.txt \
    --r1_fastq reads_R1.fastq.gz \
    --r2_fastq reads_R2.fastq.gz \
    --outdir results
```

#### SLURM with Singularity
```bash
nextflow run main.nf \
    -profile singularity,slurm \
    --tool randombarcodes \
    --barcode_file barcodes.txt \
    --r1_fastq reads_R1.fastq.gz \
    --r2_fastq reads_R2.fastq.gz \
    --outdir results
```

#### With Institutional Config
```bash
nextflow run main.nf \
    -profile singularity,slurm \
    -c conf/institutional/my_hpc.config \
    --tool quik \
    --barcode_file barcodes.txt \
    --r1_fastq reads_R1.fastq.gz \
    --r2_fastq reads_R2.fastq.gz \
    --outdir results
```

## Profile Combinations

Profiles can be combined to customize execution:

| Container Engine | Executor | Example |
|-----------------|----------|---------|
| `docker` | `local` (default) | `-profile docker` |
| `singularity` | `local` (default) | `-profile singularity` |
| `conda` | `local` (default) | `-profile conda` |
| `singularity` | `pbs` | `-profile singularity,pbs` |
| `singularity` | `slurm` | `-profile singularity,slurm` |
| `conda` | `pbs` | `-profile conda,pbs` |
| `conda` | `slurm` | `-profile conda,slurm` |

## Configuration Hierarchy

Configurations are loaded in this order (later configs override earlier ones):

1. `conf/base.config` - Resource labels
2. `conf/modules.config` - Process-specific settings
3. Profile config (e.g., `conf/executors/slurm.config`)
4. Institutional config (if specified with `-c`)
5. Command-line parameters (e.g., `--outdir`)

## GPU Processes

The following processes use GPUs and are labeled with `use_gpu`:
- `QUIK_BARCODE_CALLING`
- `RANDOMBARCODES`

GPU allocation is automatically handled by the executor configs:
- **Local**: Uses `--nv` (Singularity) or `--gpus all` (Docker)
- **PBS**: Uses `:gpus=1` in cluster options
- **SLURM**: Uses `--gres=gpu:1` in cluster options

## Resource Labels

Processes are assigned resource labels in `conf/modules.config`:

| Label | CPUs | Memory | Time | Used By |
|-------|------|--------|------|---------|
| `process_single` | 1 | 4 GB | 1 h | BARCODE_TO_FASTA |
| `process_low` | 2 | 8 GB | 2 h | CALCULATE_PRECISION, COLUMBA_INDEX |
| `process_medium` | 4 | 16 GB | 4 h | COLUMBA_BUILD |
| `process_high` | 8 | 32 GB | 8 h | - |
| `process_high_memory` | 4 | 64 GB | 4 h | COLUMBA_ALIGN |
| `use_gpu` | 2 | 32 GB | 4 h | QUIK, RANDOMBARCODES |

## Creating Institutional Configs

For HPC-specific settings (module loading, queue names, etc.), create a custom config:

```bash
# Copy the template
cat > conf/institutional/my_hpc.config << 'EOF'
/*
========================================================================================
    My HPC Configuration
========================================================================================
*/

executor {
    name = 'slurm'
}

process {
    queue = 'gpu'
    clusterOptions = '--account=my_project'
    
    withLabel: use_gpu {
        beforeScript = 'module load CUDA/12.6.0'
        clusterOptions = '--account=my_project --gres=gpu:a100:1'
    }
}
EOF

# Use it
nextflow run main.nf \
    -profile singularity,slurm \
    -c conf/institutional/my_hpc.config \
    --outdir results
```

See [conf/institutional/README.md](conf/institutional/README.md) for detailed instructions.

## Troubleshooting

### GPU Not Detected

1. **Check GPU allocation in job**:
   ```bash
   # SLURM
   scontrol show job <job_id> | grep Gres
   
   # PBS
   qstat -f <job_id> | grep gpu
   ```

2. **Check container options**:
   - Singularity needs `--nv` flag
   - Docker needs `--gpus all` flag
   - These are set automatically in executor configs

3. **Check module loading** (HPC only):
   - Look at `.command.sh` in work directory
   - Verify CUDA module is loaded

### Job Submission Fails

1. **Check executor name**:
   - PBS: `executor.name = 'pbs'`
   - SLURM: `executor.name = 'slurm'`

2. **Check queue/partition names**:
   - Use institutional config to specify correct queue

3. **Check account/project**:
   - Add to institutional config: `clusterOptions = '--account=my_project'`

### Container Not Found

1. **Check cache directory**:
   ```bash
   ls -la $VSC_SCRATCH/singularity/
   ```

2. **Clear cache if needed**:
   ```bash
   rm -rf $VSC_SCRATCH/singularity/*
   rm -rf $VSC_SCRATCH/.apptainer/cache/*
   ```

## Migration from Old Configs

If you were using the old config structure:

| Old Profile | New Profile |
|------------|-------------|
| `hpc_conda` | `conda,pbs` + institutional config |
| `hpc_singularity` | `singularity,pbs` + institutional config |
| `conda` | `conda` (unchanged) |
| `singularity` | `singularity` (unchanged) |
| `docker` | `docker` (unchanged) |

**Example migration**:

Old:
```bash
nextflow run main.nf -profile hpc_singularity --outdir results
```

New:
```bash
nextflow run main.nf \
    -profile singularity,pbs \
    -c conf/institutional/my_hpc.config \
    --outdir results
```

## Further Documentation

- [Nextflow Configuration](https://www.nextflow.io/docs/latest/config.html)
- [Nextflow Executors](https://www.nextflow.io/docs/latest/executor.html)
- [nf-core Configs](https://github.com/nf-core/configs)
