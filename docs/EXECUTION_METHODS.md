# QUIK Barcode Calling Pipeline - Execution Methods Guide

This guide explains how to run the QUIK barcode calling pipeline using different execution methods: HPC modules, Singularity containers, Docker containers, or Conda environments.

## Quick Start - Choose Your Method

### Method 1: HPC Modules (Current Default - VSC HPC)

**Best for**: Running on VSC HPC infrastructure where modules are available

```bash
# Standard execution (uses modules by default)
nextflow run main.nf -params-file test_params.json

# OR explicitly specify standard profile
nextflow run main.nf -params-file test_params.json -profile standard
```

**Requirements**: CUDA/12.6.0 and CMake/3.29.3-GCCcore-13.3.0 modules available

---

### Method 2: Singularity Container (Recommended for Portability)

**Best for**: Reproducible pipelines, shared workflows, publication

#### Step 1: Build or Obtain Container

**Option A: Pull from Docker Hub (easiest)**
```bash
# Container is pulled automatically on first run
# No pre-build needed!
```

**Option B: Build your own container**
```bash
cd containers/

# Build with Singularity
singularity build quik_cuda.sif quik_cuda.def

# OR build remotely (Sylabs Cloud)
singularity remote login
singularity build --remote quik_cuda.sif quik_cuda.def
```

#### Step 2: Run Pipeline

**Using Docker Hub image (auto-pull)**:
```bash
nextflow run main.nf \
    -params-file test_params.json \
    -profile singularity
```

**Using local SIF file**:
```bash
# First, edit nextflow.config to uncomment and set the container path:
# container = "${projectDir}/containers/quik_cuda.sif"

nextflow run main.nf \
    -params-file test_params.json \
    -profile singularity
```

---

### Method 3: Docker Container

**Best for**: Local development, systems with Docker installed

#### Step 1: Ensure Docker and NVIDIA Container Toolkit

```bash
# Check Docker
docker --version

# Check NVIDIA container runtime
docker run --rm --gpus all nvidia/cuda:12.6.0-base nvidia-smi
```

#### Step 2: Run Pipeline

```bash
nextflow run main.nf \
    -params-file test_params.json \
    -profile docker
```

---

### Method 4: Conda Environment

**Best for**: Development, testing, systems without container support

#### Step 1: Create Conda Environment

```bash
# Create from YAML file
conda env create -f envs/quik_cuda.yml

# Activate to test
conda activate quik_cuda
nvcc --version
cmake --version
```

#### Step 2: Run Pipeline

```bash
nextflow run main.nf \
    -params-file test_params.json \
    -profile conda
```

**Note**: Conda CUDA support can be tricky. If you encounter issues, use containers instead.

---

## Running on Different HPC Systems

### VSC (Vlaams Supercomputer Centrum)

**With Modules** (fastest, recommended):
```bash
module load Nextflow
nextflow run main.nf -params-file test_params.json -profile pbs
```

**With Singularity**:
```bash
module load Nextflow Singularity
nextflow run main.nf -params-file test_params.json -profile vsc_singularity
```

### Generic SLURM Cluster

```bash
nextflow run main.nf \
    -params-file test_params.json \
    -profile slurm,singularity
```

### Local Machine (No Cluster)

```bash
nextflow run main.nf \
    -params-file test_params.json \
    -profile local,singularity
```

---

## Combining Profiles

You can combine multiple profiles using commas:

```bash
# SLURM scheduler + Singularity container
nextflow run main.nf -params-file test_params.json -profile slurm,singularity

# PBS scheduler + Conda environment
nextflow run main.nf -params-file test_params.json -profile pbs,conda

# Local execution + Docker
nextflow run main.nf -params-file test_params.json -profile local,docker
```

---

## Profile Comparison

| Profile | Pros | Cons | Setup Required |
|---------|------|------|----------------|
| **standard** (modules) | ✅ Fast<br>✅ No setup | ❌ Not portable<br>❌ System-dependent | Module system |
| **singularity** | ✅ Portable<br>✅ Reproducible<br>✅ No conflicts | ⚠️ Initial build | Singularity installed |
| **docker** | ✅ Easy to use<br>✅ Portable | ❌ Needs Docker daemon<br>❌ Root access | Docker + NVIDIA runtime |
| **conda** | ✅ Easy to create<br>✅ Flexible | ⚠️ CUDA support issues<br>❌ Slower | Conda/Mamba |

---

## Troubleshooting

### Singularity: Container doesn't see GPU

**Problem**: CUDA not available inside container

**Solution**:
```bash
# Ensure --nv flag is set (should be automatic with profile)
# Check it's in nextflow.config:
singularity.runOptions = '--nv'

# Test GPU access
singularity exec --nv docker://nvidia/cuda:12.6.0-base nvidia-smi
```

### Conda: CUDA toolkit not found

**Problem**: nvcc or CUDA libraries not found

**Solution**:
```bash
# Activate environment
conda activate quik_cuda

# Set CUDA paths
export CUDA_HOME=$CONDA_PREFIX
export PATH=$CUDA_PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

# Verify
nvcc --version
```

### Docker: Permission denied

**Problem**: Docker requires root or docker group membership

**Solution**:
```bash
# Add user to docker group (requires admin)
sudo usermod -aG docker $USER
newgrp docker

# OR use Singularity instead
```

### Module not found on HPC

**Problem**: CUDA/CMake modules not available

**Solution**:
```bash
# Check available modules
module avail CUDA
module avail CMake

# Update nextflow.config with correct module names
# OR switch to container-based execution
```

---

## Testing Your Setup

### Quick Test Script

```bash
#!/bin/bash
# test_setup.sh - Test your chosen execution method

METHOD=${1:-standard}  # Default to standard

echo "Testing $METHOD execution method..."

# Create minimal test params
cat > test_minimal.json << 'EOF'
{
    "barcode_file": "test_data/barcodes.txt",
    "r1_fastq": "test_data/test_R1.fastq",
    "r2_fastq": "test_data/test_R2.fastq",
    "sample_id": "test",
    "barcode_start": 9,
    "barcode_length": 36,
    "strategy": "4_7_mer_gpu_v1",
    "distance_measure": "SEQUENCE_LEVENSHTEIN",
    "rejection_threshold": 8,
    "outdir": "./test_results_${METHOD}"
}
EOF

# Run with specified profile
nextflow run main.nf -params-file test_minimal.json -profile $METHOD

# Check results
if [ -f "./test_results_${METHOD}/test/test_barcode_calling_stats.txt" ]; then
    echo "✅ Test passed!"
    cat "./test_results_${METHOD}/test/test_barcode_calling_stats.txt"
else
    echo "❌ Test failed - no output file generated"
    exit 1
fi
```

**Usage**:
```bash
chmod +x test_setup.sh

# Test with modules
./test_setup.sh standard

# Test with Singularity
./test_setup.sh singularity

# Test with Conda
./test_setup.sh conda
```

---

## Best Practices

### For Development
1. Use modules or conda (fast iteration)
2. Test locally before cluster submission

### For Production
1. Use Singularity containers (reproducibility)
2. Document exact container version/hash
3. Store container in accessible location

### For Publication
1. Provide Singularity definition file
2. Host container on public registry (Docker Hub, Singularity Hub)
3. Include container in supplementary materials

### For Collaboration
1. Use containers (ensures everyone has same environment)
2. Version your container with git tags
3. Provide both Dockerfile and Singularity definition

---

## Environment-Specific Tips

### VSC HPC Systems
- Modules are fastest (optimized for local hardware)
- Singularity available on most nodes
- Use `-profile vsc_modules` or `-profile vsc_singularity`

### Generic HPC with SLURM
- Singularity usually available
- Check GPU partition name (update in config)
- Use `-profile slurm,singularity`

### Cloud Computing (AWS, GCP, Azure)
- Docker preferred (better cloud integration)
- Use spot/preemptible instances for cost savings
- Consider Nextflow Tower for monitoring

### Local Workstation
- Docker easiest (if you have NVIDIA GPU)
- Conda good for CPU-only testing
- Use `-profile local,docker`

---

## Getting Help

### Check Execution Method
```bash
# See which profile is active
nextflow run main.nf -params-file test_params.json -profile singularity -with-report

# Check the report.html file - shows container/conda used
```

### Debug Container Issues
```bash
# Test container interactively
singularity shell --nv docker://nvidia/cuda:12.6.0-devel-ubuntu22.04
# Inside container:
nvcc --version
cmake --version
```

### Debug Conda Issues
```bash
# Activate and test
conda activate quik_cuda
which nvcc
which cmake
```

---

## Advanced Configuration

### Custom Container Path

Edit `nextflow.config`:
```groovy
process {
    withName: 'QUIK_BARCODE_CALLING' {
        container = '/shared/containers/quik_cuda_v1.0.sif'
    }
}
```

### Custom Conda Environment Location

```groovy
process {
    withName: 'QUIK_BARCODE_CALLING' {
        conda = '/shared/envs/quik_cuda'
    }
}
```

### Mixed Execution (Different Methods per Process)

```groovy
process {
    withName: 'PROCESS_A' {
        module = 'CUDA/12.6.0'
    }
    withName: 'PROCESS_B' {
        container = 'docker://myimage:latest'
    }
}
```
