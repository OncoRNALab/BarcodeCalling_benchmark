# HPC Usage Guide - UGent Joltik/Accelgor

## Quick Start

### For PBS with HPC Modules (Recommended)
```bash
nextflow run main.nf \
    -profile pbs \
    --tool randombarcodes \
    --barcode_file barcodes.txt \
    --r1_fastq reads_R1.fastq.gz \
    --r2_fastq reads_R2.fastq.gz \
    --outdir results
```

### For SLURM with Singularity
```bash
nextflow run main.nf \
    -profile singularity,slurm \
    --tool randombarcodes \
    --barcode_file barcodes.txt \
    --r1_fastq reads_R1.fastq.gz \
    --r2_fastq reads_R2.fastq.gz \
    --outdir results
```

## Configuration Details

### PBS Profile (Uses HPC Modules)

The `pbs` profile is configured to:
- **Use HPC environment modules** instead of containers
- Load `PyTorch-bundle/2.1.2-foss-2023a-CUDA-12.1.1` for GPU processes
- Request GPUs via PBS cluster options
- Work natively with the HPC environment

**Advantages:**
- ✅ Direct access to GPU without container overhead
- ✅ No CUDA version mismatch issues
- ✅ Faster execution
- ✅ Simpler debugging

**Configuration** ([conf/executors/pbs.config](../conf/executors/pbs.config)):
```groovy
process {
    withLabel: use_gpu {
        module = 'PyTorch-bundle/2.1.2-foss-2023a-CUDA-12.1.1'
        clusterOptions = { "-l nodes=1:ppn=${task.cpus}:gpus=1" }
    }
}
```

### SLURM Profile (Uses Singularity Containers)

The `slurm` profile is configured to:
- **Use Singularity containers** with GPU support
- Load `cuDNN/9.5.0.50-CUDA-12.6.0` module on the host
- Target joltik and accelgor clusters
- Use `--nv` flag for GPU access in containers

**Configuration** ([conf/executors/slurm.config](../conf/executors/slurm.config)):
```groovy
process {
    withLabel: use_gpu {
        module = 'cuDNN/9.5.0.50-CUDA-12.6.0'
        clusterOptions = { 
            "--gpus=1 --clusters=joltik,accelgor" + 
            (System.getenv("SBATCH_ACCOUNT") || System.getenv("SLURM_ACCOUNT") ? 
                " --account=" + (System.getenv("SBATCH_ACCOUNT") ?: System.getenv("SLURM_ACCOUNT")) : 
                "")
        }
        containerOptions = '--nv'
    }
}
```

## Which Profile to Use?

| Scenario | Recommended Profile | Why |
|----------|-------------------|-----|
| Production runs on joltik/accelgor | `pbs` | Native HPC modules, more reliable |
| Testing with containers | `singularity,slurm` | Reproducible environment |
| Parameter sweeps | `pbs` | Faster, simpler |
| Debugging GPU issues | `pbs` | Direct CUDA access |

## Troubleshooting

### PBS Profile Issues

#### GPU Not Detected
```bash
# Check if module is loaded
module list

# Should show: PyTorch-bundle/2.1.2-foss-2023a-CUDA-12.1.1

# Test CUDA availability
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

#### Module Not Found
```bash
# Make sure you're on the right cluster
ml swap cluster/joltik
# or
ml swap cluster/accelgor

# Check available PyTorch modules
ml avail pytorch
```

### SLURM Profile Issues

#### Container CUDA Issues
The SLURM profile may have CUDA visibility issues inside containers. Use PBS profile instead.

#### Wrong Cluster
```bash
# Ensure you're targeting GPU clusters
ml swap cluster/joltik
# or  
ml swap cluster/accelgor
```

## Complete Example

### Parameter Sweep with PBS

```bash
#!/bin/bash
#PBS -N barcode_sweep
#PBS -l walltime=10:00:00
#PBS -l nodes=1:ppn=1
#PBS -l mem=8gb

cd $PBS_O_WORKDIR

# Run parameter sweep
for ntriage in 100 500 1000 5000; do
    for nthresh in 3 5 7; do
        nextflow run main.nf \
            -profile pbs \
            --tool randombarcodes \
            --barcode_file barcodes.txt \
            --r1_fastq reads_R1.fastq.gz \
            --r2_fastq reads_R2.fastq.gz \
            --ntriage $ntriage \
            --nthresh $nthresh \
            --outdir results/t${ntriage}_n${nthresh}
    done
done
```

## Module Information

### Available on Joltik/Accelgor

```bash
# PyTorch with CUDA (for PBS)
PyTorch-bundle/2.1.2-foss-2023a-CUDA-12.1.1

# CUDA/cuDNN (for SLURM with containers)
cuDNN/9.5.0.50-CUDA-12.6.0
```

### What's Included in PyTorch-bundle

- Python 3.11
- PyTorch 2.1.2
- CUDA 12.1.1
- NumPy
- SciPy
- Other scientific Python packages

All dependencies needed for RandomBarcodes and QUIK are included.

## Performance Comparison

Based on benchmarking:

| Configuration | Job Submission | GPU Access | Execution Speed |
|--------------|----------------|------------|----------------|
| PBS + Modules | Fast | Direct | Fastest |
| SLURM + Singularity | Medium | Via --nv | Slower (container overhead) |

**Recommendation:** Use `pbs` profile for production work.

## Configuration Validation (Smoke Tests)

Before running the full pipeline, validate your configuration with these commands:

### 1. Check RandomBarcodes PBS Configuration

Verify that RandomBarcodes uses HPC modules (not conda/containers) on PBS:

```bash
nextflow config -profile pbs | grep -A10 "withName:.*RANDOMBARCODES"
```

**Expected output:**
```
withName:'RANDOMBARCODES' {
    conda = null
    container = null
}
```

If you see conda or container paths instead of `null`, the PBS override is not working.

### 2. Check QUIK/Columba Flexibility

Verify that QUIK can use containers with PBS:

```bash
nextflow config -profile singularity,pbs | grep -A5 "withName:.*QUIK_BARCODE_CALLING"
```

**Expected:** Should show container directive with pytorch image, NOT null.

### 3. Validate Profile Order

Test that profile order matters:

```bash
# Correct order - singularity should be enabled
nextflow config -profile singularity,pbs | grep "singularity.enabled"
# Should output: singularity.enabled = true

# Wrong order - might show different result
nextflow config -profile pbs,singularity | grep "singularity.enabled"
```

### 4. Full Configuration Dump

Review all process-level settings:

```bash
nextflow config -profile singularity,pbs -showAllProfiles > config_dump.txt
```

Then check:
- `RANDOMBARCODES` should have `conda = null, container = null`
- `QUIK_BARCODE_CALLING` should have container directive
- `use_gpu` label should have `beforeScript` with module load

### 5. Test Run (Dry Run)

Validate without executing:

```bash
nextflow run main.nf \
    -profile pbs \
    --tool randombarcodes \
    --barcode_file test_data/barcodes.txt \
    --r1_fastq test_data/reads_R1.fastq.gz \
    --r2_fastq test_data/reads_R2.fastq.gz \
    -preview
```

This shows what commands will be executed without running them.

## Common Configuration Mistakes

### ❌ Wrong: Using pbs profile alone for QUIK with containers
```bash
nextflow run main.nf -profile pbs --tool quik  # May not use containers
```

### ✅ Correct: Combine singularity with pbs for QUIK
```bash
nextflow run main.nf -profile singularity,pbs --tool quik
```

### ❌ Wrong: Profile order (executor first)
```bash
nextflow run main.nf -profile pbs,singularity  # singularity may not be enabled
```

### ✅ Correct: Environment profile first
```bash
nextflow run main.nf -profile singularity,pbs
```

### ❌ Wrong: Trying to force containers for RandomBarcodes on PBS
The configuration explicitly prevents this. RandomBarcodes MUST use HPC modules on PBS.

### ✅ Correct: Use containers for RandomBarcodes only on local executor
```bash
nextflow run main.nf -profile singularity --tool randombarcodes  # Uses local executor
```

