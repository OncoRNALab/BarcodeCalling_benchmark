# Institutional Configuration Files

This directory contains HPC-specific configuration files for different institutional computing environments.

## Purpose

Institutional configs allow you to customize the pipeline for your specific HPC system, including:
- Module loading (e.g., CUDA, CMake, GCC)
- Queue/partition names
- Account/project specifications
- GPU type specifications
- Storage paths and scratch directories
- Scheduler-specific options

## Usage

To use an institutional config, add it to your Nextflow command with the `-c` flag:

```bash
nextflow run main.nf \
    -profile singularity,slurm \
    -c conf/institutional/my_hpc.config \
    --barcode_file barcodes.txt \
    --r1_fastq reads_R1.fastq.gz \
    --r2_fastq reads_R2.fastq.gz \
    --outdir results
```

## Creating Your Own Institutional Config

### Template Structure

Create a new file: `conf/institutional/<your_institution>.config`

```groovy
/*
========================================================================================
    <Institution Name> HPC Configuration
========================================================================================
    Institution: <Your Institution>
    System: <System Name>
    Scheduler: <PBS/SLURM/SGE>
    
    Usage:
        nextflow run main.nf \\
            -profile <singularity/conda>,<pbs/slurm> \\
            -c conf/institutional/<your_institution>.config \\
            --outdir results
========================================================================================
*/

// Override executor settings if needed
executor {
    name = 'slurm'  // or 'pbs', 'sge', etc.
    queueSize = 50
    submitRateLimit = '10/1min'
}

// Define institution-specific scratch directory
def scratch_dir = System.getenv("SCRATCH") ?: 
                  System.getenv("TMPDIR") ?: 
                  "${System.getenv("HOME")}/scratch"

// Environment variables
env {
    APPTAINER_CACHEDIR = "$scratch_dir/.apptainer/cache"
    SINGULARITY_CACHEDIR = "$scratch_dir/singularity"
    // Add other institution-specific env vars
}

// Process-specific configurations
process {
    
    // Queue/partition selection
    queue = { task.label == 'use_gpu' ? 'gpu_queue' : 'cpu_queue' }
    
    // Account specification (if required)
    clusterOptions = { "--account=my_project ${task.label == 'use_gpu' ? '--gres=gpu:1' : ''}" }
    
    // GPU processes with module loading
    withLabel: use_gpu {
        // Load CUDA module
        beforeScript = 'module load CUDA/12.6.0'
        
        // Specify GPU type if multiple GPU types available
        clusterOptions = '--account=my_project --gres=gpu:a100:1'
        
        // Queue for GPU jobs
        queue = 'gpu_queue'
    }
    
    // Module loading for specific tools
    withName: 'COLUMBA_BUILD' {
        beforeScript = 'module load CMake/3.29.3'
    }
    
    withName: 'COLUMBA_INDEX|COLUMBA_ALIGN' {
        beforeScript = 'module load GCCcore/13.3.0'
    }
}

// Container cache directory
singularity {
    cacheDir = "$scratch_dir/singularity"
}

apptainer {
    cacheDir = "$scratch_dir/.apptainer/cache"
}
```

## Common Institutional Settings

### PBS/Torque Systems

```groovy
executor {
    name = 'pbs'
}

process {
    clusterOptions = { "-A my_project" }
    
    withLabel: use_gpu {
        clusterOptions = { "-A my_project -l nodes=1:ppn=${task.cpus}:gpus=1" }
        queue = 'gpu'
    }
}
```

### SLURM Systems

```groovy
executor {
    name = 'slurm'
}

process {
    clusterOptions = { "--account=my_project" }
    
    withLabel: use_gpu {
        clusterOptions = '--account=my_project --gres=gpu:1 --partition=gpu'
        queue = 'gpu'
    }
}
```

### SGE Systems

```groovy
executor {
    name = 'sge'
}

process {
    clusterOptions = { "-P my_project" }
    
    withLabel: use_gpu {
        clusterOptions = '-P my_project -l gpu=1'
        queue = 'gpu.q'
    }
}
```

## Module Loading Examples

### Loading CUDA for GPU processes

```groovy
process {
    withLabel: use_gpu {
        beforeScript = 'module load CUDA/12.6.0'  // Adjust version
    }
}
```

### Loading Multiple Modules

```groovy
process {
    withName: 'COLUMBA_BUILD' {
        beforeScript = '''
            module load GCC/13.3.0
            module load CMake/3.29.3
        '''.stripIndent().trim()
    }
}
```

## Testing Your Configuration

1. **Test with a small dataset**:
   ```bash
   nextflow run main.nf \
       -profile singularity,slurm,test \
       -c conf/institutional/my_hpc.config \
       --tool quik \
       --barcode_file test_data/barcodes.txt \
       --r1_fastq test_data/reads_R1.fastq.gz \
       --r2_fastq test_data/reads_R2.fastq.gz \
       --outdir test_results
   ```

2. **Check GPU allocation**:
   - Monitor job submission: `squeue -u $USER` (SLURM) or `qstat -u $USER` (PBS)
   - Verify GPU is allocated in job details
   - Check the `.command.log` file for GPU detection

3. **Verify module loading**:
   - Check `.command.sh` scripts in work directories
   - Ensure modules are loaded before tool execution

## Tips

- **Module Names**: Check available modules with `module avail` on your HPC
- **Queue Names**: Use `sinfo` (SLURM) or `qstat -Q` (PBS) to see available queues
- **GPU Types**: Consult your HPC documentation for GPU specifications
- **Accounts**: Check with your HPC admin for project/account names
- **Storage**: Use fast scratch storage for `TMPDIR` and cache directories

## Support

For help creating institutional configs:
1. Check your HPC documentation
2. Contact your HPC support team
3. See working examples in the nf-core/configs repository: https://github.com/nf-core/configs
