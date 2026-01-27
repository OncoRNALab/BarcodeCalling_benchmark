# Barcode Benchmark Workflow

This benchmark tests barcode generation and read simulation across multiple parameter combinations.

## Overview

- **Barcode Lengths**: 36nt, 34nt, 32nt, 30nt, 28nt
- **Codeword Counts**: 85,000, 42,000, 21,000
- **Error Rates**: Low, Medium, High

### Error Rate Parameters

| Level  | Substitution | Insertion | Deletion |
|--------|-------------|-----------|----------|
| Low    | 0.02        | 0.03      | 0.13     |
| Medium | 0.03        | 0.04      | 0.14     |
| High   | 0.03        | 0.15      | 0.14     |

## Directory Structure

```
RandomBarcodes/
├── config_files/           # Configuration files (60 total)
│   ├── config_benchmark_85K_36nt_bargen.yaml
│   ├── config_benchmark_85K_36nt_sim_low.yaml
│   ├── config_benchmark_85K_36nt_sim_medium.yaml
│   ├── config_benchmark_85K_36nt_sim_high.yaml
│   └── ... (56 more files)
├── jobs/                   # PBS job scripts (60 total)
│   ├── job_bargen_85K_36nt.pbs
│   ├── job_simgen_85K_36nt_low.pbs
│   └── ... (58 more files)
├── outputs/benchmark_85K_42K_21K/  # Output directories
│   ├── 85K_36nt/
│   ├── 85K_34nt/
│   ├── 85K_32nt/
│   └── ... (15 directories total)
└── scripts/
    ├── 1_BarcodeGen_split.py
    └── 2_SimGen_split.py
```

## Generated Files

### Configuration Files (60 total)
- **15 barcode generation configs**: One for each combination of length × codeword count
- **45 simulation configs**: Three error rates for each of the 15 barcode sets

### PBS Job Files (60 total)
- **15 barcode generation jobs**
- **45 simulation jobs**

### Output Directories (15 total)
Each combination of codeword count and length has its own directory:
- 85K_36nt, 85K_34nt, 85K_32nt, 85K_30nt, 85K_28nt
- 42K_36nt, 42K_34nt, 42K_32nt, 42K_30nt, 42K_28nt
- 21K_36nt, 21K_34nt, 21K_32nt, 21K_30nt, 21K_28nt

## Workflow

### Step 1: Generate Barcodes (15 jobs)

Submit all barcode generation jobs:

```bash
./submit_barcode_jobs.sh
```

Or submit individual jobs:

```bash
cd jobs
qsub job_bargen_85K_36nt.pbs
qsub job_bargen_42K_36nt.pbs
# ... etc
```

Each barcode generation job will:
- Generate random barcodes with chemical filtering
- Create two subset files (subset1 and subset2)
- Save barcodes in text format and pickle format
- Output files: `barcodes_<count>_<length>_subset1` and corresponding .pkl file

### Step 2: Simulate Reads (45 jobs)

**IMPORTANT**: Only run after ALL barcode generation jobs complete!

Submit all simulation jobs:

```bash
./submit_simulation_jobs.sh
```

Or submit individual jobs:

```bash
cd jobs
qsub job_simgen_85K_36nt_low.pbs
qsub job_simgen_85K_36nt_medium.pbs
qsub job_simgen_85K_36nt_high.pbs
# ... etc
```

Each simulation job will:
- Load the generated barcodes from the pickle file
- Simulate 1,000,000 reads with specified error rates
- Output files: `reads_<count>_<length>_<error_level>` and corresponding answers file

## Monitoring Jobs

Check job status:

```bash
qstat -u $USER
```

Check specific job output:

```bash
# Job output files will be in the job submission directory
cat <job_name>.o<job_id>  # stdout
cat <job_name>.e<job_id>  # stderr
```

## Expected Outputs

For each barcode set (e.g., 85K_36nt), you will have:

### Barcode Files
- `barcodes_85K_36_subset1` - Text file with barcodes
- `barcodes_85K_36_subset2` - Text file with second subset
- `barcodes_85K_36_subset1.pkl` - Pickle file with barcode data

### Simulation Files (for each error level)
- `reads_85K_36_low` - Simulated reads (low error)
- `answers_85K_36_low` - True barcode indices
- `best_85K_36_low.txt` - Decoding results
- (Same for medium and high error levels)

## File Sizes (Approximate)

- Barcode text files: ~M × N bytes (e.g., 36 × 85,000 = 3.06 MB)
- Pickle files: ~64 × M × N bytes (e.g., 64 × 36 × 85,000 = 196 MB)
- Simulation reads: ~1,000,000 × M bytes (e.g., 36 MB per simulation)

Total expected storage: ~50-60 GB for all outputs

## Configuration Parameters

All config files use these standard parameters:
- **fac**: 8 (filtering factor)
- **homomax**: 3 (max homopolymer length)
- **gmax**: 0.27 (max GC content deviation)
- **cyclemax**: 2.1 (max cycle count)
- **Q**: 1,000,000 (number of simulated reads)
- **nave**: 4 (average Poisson reads per codeword)
- **Nthresh**: 9 (Levenshtein threshold for erasure)

## Regenerating Files

If you need to regenerate all config and job files:

```bash
python generate_configs_and_jobs.py
```

This will overwrite existing files in `config_files/` and `jobs/` directories.

## Troubleshooting

### Job fails with module not found
- Ensure PyTorch module is available: `ml avail PyTorch`
- Check the module load command in PBS scripts

### Insufficient memory
- Edit PBS scripts to increase memory: `#PBS -l mem=64gb`

### Barcode generation fails
- Check chemical filtering parameters (fac, homomax, gmax, cyclemax)
- Increase `fac` parameter if needed

### Simulation fails with "file not found"
- Ensure barcode generation completed successfully
- Check that pickle files exist in the output directories

## Summary Statistics

| Category              | Count |
|-----------------------|-------|
| Total Jobs            | 60    |
| Barcode Gen Jobs      | 15    |
| Simulation Jobs       | 45    |
| Config Files          | 60    |
| Output Directories    | 15    |
| Total Barcode Sets    | 15    |
| Total Simulations     | 45    |

## Naming Convention

### Config Files
- Barcode generation: `config_benchmark_<count>_<length>_bargen.yaml`
- Simulation: `config_benchmark_<count>_<length>_sim_<error_level>.yaml`

### PBS Job Files
- Barcode generation: `job_bargen_<count>_<length>.pbs`
- Simulation: `job_simgen_<count>_<length>_<error_level>.pbs`

### Output Files
- Barcodes: `barcodes_<count>_<length>_subset[1|2]`
- Pickle: `barcodes_<count>_<length>_subset1.pkl`
- Reads: `reads_<count>_<length>_<error_level>`
- Answers: `answers_<count>_<length>_<error_level>`
- Best: `best_<count>_<length>_<error_level>.txt`

Where:
- `<count>` = 85K, 42K, or 21K
- `<length>` = 36nt, 34nt, 32nt, 30nt, or 28nt
- `<error_level>` = low, medium, or high
