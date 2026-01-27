# Barcode Calling Benchmark Pipeline

## Overview

A Nextflow-based pipeline for benchmarking DNA barcode calling algorithms on simulated and real sequencing data. The pipeline supports multiple barcode calling tools and provides comprehensive performance metrics.

## Supported Tools

- **QUIK**: GPU-accelerated barcode calling using C++/CUDA
- **RandomBarcodes** (Press et al.): Python/PyTorch-based GPU barcode calling
- **Columba**: Coming soon

## Features

- ✅ Multi-tool support with easy tool selection
- ✅ **Real data support** - Run without ground truth for real sequencing data
- ✅ Automated precision/recall calculation against ground truth (simulated data)
- ✅ **Comprehensive statistics** - Assignment rates, distribution metrics, quality indicators
- ✅ GPU-accelerated processing
- ✅ Modular design for easy extension
- ✅ Multiple execution profiles (local, PBS, SLURM)
- ✅ Comprehensive statistics and reporting

## Data Modes

### Simulated Data (with Ground Truth)
- Full precision/recall/accuracy metrics
- Per-barcode error analysis
- Optimal threshold identification

### Real Data (without Ground Truth) **NEW**
- Assignment rate analysis
- Barcode distribution statistics
- Coverage uniformity metrics
- Quality indicators (singletons, low coverage)
- Per-barcode read counts

See [REAL_DATA_GUIDE.md](docs/REAL_DATA_GUIDE.md) for detailed instructions.

## Quick Start

### Running QUIK

```bash
nextflow run main.nf \
    -profile vsc_conda \
    -params-file test_params.json \
    --tool quik
```

### Running RandomBarcodes

```bash
nextflow run main.nf \
    -profile vsc_conda \
    -params-file test_params_randombarcodes.json \
    --tool randombarcodes
```

See [TOOL_SELECTION.md](docs/TOOL_SELECTION.md) for detailed usage instructions.

---

# Precision Calculation Module

The pipeline includes a precision calculation module that compares barcode calling results against ground truth data. This is designed for evaluating barcode calling performance on simulated datasets.

## Input Requirements

### 1. Ground Truth File
- **Format**: Plain text file with one barcode index per line
- **Content**: Each line contains an integer representing the barcode index (0-based)
- **Example**: For 1 million simulated reads, the file will have 1 million lines
- **Location**: `/path/to/ground_truth.txt`

```
21254
21254
7343
4711
...
```

### 2. Barcode Reference File
- **Format**: Plain text file with one barcode sequence per line
- **Example**:
```
ataataaatgagtgggataataaatgagt  # Index 0
caaataactgatcgggataataaatgagt  # Index 1
aaacaaacagaaagggataataaatgagt  # Index 2
...
```

### 3. Filtered FASTQ Files
- Output from QUIK barcode calling
- Must have barcode information in the read headers
- Format: `@read_N_BARCODE` or similar

## Usage

### Basic Usage with Ground Truth

Add the `ground_truth` parameter to your params file or command line:

```bash
# Using params file
nextflow run main.nf -profile conda -params-file test_params.json

# Command line
nextflow run main.nf \\
    -profile conda \\
    --barcode_file /path/to/barcodes.txt \\
    --r1_fastq /path/to/R1.fastq \\
    --r2_fastq /path/to/R2.fastq \\
    --ground_truth /path/to/ground_truth.txt \\
    --sample_id my_sample \\
    --outdir ./results
```

### Parameters File Example

```json
{
    "barcode_file": "/path/to/barcodes.txt",
    "r1_fastq": "/path/to/R1.fastq",
    "r2_fastq": "/path/to/R2.fastq",
    "sample_id": "test_sample",
    "ground_truth": "/path/to/ground_truth.txt",
    "barcode_start": 0,
    "barcode_length": 29,
    "strategy": "7_mer_gpu_v1",
    "distance_measure": "SEQUENCE_LEVENSHTEIN",
    "rejection_threshold": 7,
    "outdir": "./results"
}
```

## Output Files

The precision calculation produces two output files in the sample's output directory:

### 1. Detailed Report (`{sample_id}_precision_report.txt`)

Contains:
- Overall metrics (total reads, assigned, unassigned)
- Accuracy metrics (precision, recall, accuracy, assignment rate)
- Top misassignments with barcode sequences

Example:
```
================================================================================
BARCODE CALLING PRECISION REPORT
================================================================================

=== OVERALL METRICS ===
Total reads (ground truth): 1000000
Reads processed: 1000000
Reads assigned: 850000
Reads unassigned/rejected: 150000

=== ACCURACY METRICS ===
Correct assignments: 840000
Incorrect assignments: 10000
Assignment rate: 85.00%
Precision (correct/assigned): 98.82%
Recall (correct/total): 84.00%
Accuracy (correct/total): 84.00%

=== TOP MISASSIGNMENTS ===
Count | True Barcode (idx) | Assigned Barcode (idx)
--------------------------------------------------------------------------------
  234 | ataataaatgagtggg... (   12) | caaataactgatcggg... (  145)
  189 | attcgaacagagcggg... (  456) | aatcctactcacaggg... (  789)
...
```

### 2. Summary CSV (`{sample_id}_precision_summary.csv`)

Machine-readable summary for downstream analysis:

```csv
metric,value
total_reads,1000000
total_processed,1000000
correct_assignments,840000
incorrect_assignments,10000
unassigned_reads,150000
assignment_rate_percent,85.0000
precision_percent,98.8235
recall_percent,84.0000
accuracy_percent,84.0000
```

## Metrics Explained

- **Precision**: Percentage of assigned reads that were correctly assigned
  - Formula: `(correct assignments / total assigned) × 100`
  - Measures how accurate the assignments are when a barcode is assigned

- **Recall**: Percentage of all reads that were correctly assigned
  - Formula: `(correct assignments / total reads) × 100`
  - Measures how many reads receive the correct barcode overall

- **Accuracy**: Same as recall in this context
  - Formula: `(correct assignments / total reads) × 100`

- **Assignment Rate**: Percentage of reads that received any barcode assignment
  - Formula: `(total assigned / total reads) × 100`
  - Reads that don't meet quality thresholds are rejected (unassigned)

## Running Without Ground Truth

If you don't specify a ground truth file, the pipeline will run normally without precision calculation:

```bash
nextflow run main.nf -profile conda -params-file params_no_truth.json
```

The pipeline will log:
```
No ground truth file provided. Skipping precision calculation.
To enable precision calculation, specify --ground_truth <file>
```

## Standalone Script Usage

You can also run the precision calculation script independently:

```bash
calculate_precision.py \\
    barcodes.txt \\
    ground_truth.txt \\
    filtered_R1.fastq \\
    output_report.txt \\
    output_summary.csv \\
    --verbose
```

## Notes

- The ground truth file must have the same number of lines as there are reads in the input FASTQ files
- Barcode indices in the ground truth file are 0-based (first barcode = index 0)
- Reads that were rejected during barcode calling are counted as "unassigned"
- The precision calculation only uses R1 FASTQ file (assumes barcode is in R1)

## Troubleshooting

### Issue: "Ground truth file not found"
- Verify the file path is correct
- Check file permissions

### Issue: "Mismatch between ground truth and FASTQ"
- Ensure ground truth file has one line per read
- Verify the ground truth corresponds to the input FASTQ files

### Issue: "No barcodes found in FASTQ headers"
- Check that the filtered FASTQ files have barcode information in headers
- Verify the header format matches expected pattern (e.g., `@read_N_BARCODE`)
