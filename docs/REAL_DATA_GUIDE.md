# Running Barcode Calling Pipeline with Real Sequencing Data

This guide explains how to use the pipeline with real sequencing data where no ground truth is available.

## Overview

The pipeline now supports two modes:
1. **Simulated Data Mode**: With ground truth for precision/recall calculation
2. **Real Data Mode**: Without ground truth, using statistical quality metrics

## Quick Start - Real Data

### Basic Command

```bash
nextflow run main.nf \
    --tool quik \
    --barcode_file barcodes.txt \
    --r1_fastq sample_R1.fastq \
    --r2_fastq sample_R2.fastq \
    --sample_id my_sample \
    --barcode_length 36 \
    --data_mode real \
    --outdir results/
```

### Using a Parameters File

```bash
nextflow run main.nf -params-file test_params_real_data.json
```

## Parameters

### Required Parameters
- `--barcode_file`: Path to barcode library file (one barcode per line)
- `--r1_fastq`: Path to R1 FASTQ file
- `--r2_fastq`: Path to R2 FASTQ file
- `--sample_id`: Sample identifier for output files

### Data Mode Parameters
- `--data_mode`: Mode selection
  - `"auto"` (default): Automatically detect based on ground_truth parameter
  - `"real"`: Force real data mode (no ground truth required)
  - `"simulated"`: Force simulated data mode (requires ground_truth)
- `--ground_truth`: Path to ground truth file (optional, only for simulated data)

### Tool-Specific Parameters

#### QUIK
```bash
--tool quik \
--strategy 4_mer_gpu_v4 \
--rejection_threshold 5 \
--barcode_start 10 \
--barcode_length 36
```

#### RandomBarcodes
```bash
--tool randombarcodes \
--ntriage 100 \
--nthresh 5 \
--gpus 1 \
--barcode_length 36
```

#### Columba
```bash
--tool columba \
--identity_threshold 77 \
--barcode_window "0-36"
```

## Outputs for Real Data

When running in real data mode (no ground truth), the pipeline generates:

### 1. Barcode Calling Results
- `{sample_id}_filtered_R1.fastq`: Filtered R1 reads with barcode assignments
- `{sample_id}_filtered_R2.fastq`: Filtered R2 reads
- `{sample_id}_stats.txt`: Tool-specific statistics

### 2. Quality Metrics (NEW)
- `{sample_id}_stats_report.txt`: **Detailed statistical report**
- `{sample_id}_stats_summary.csv`: **Summary metrics in CSV format**
- `{sample_id}_per_barcode.csv`: **Per-barcode read counts**

### 3. Metrics Included

#### Assignment Metrics
- Total reads processed
- Reads assigned to barcodes
- Reads unassigned/rejected
- Assignment rate (%)

#### Distribution Metrics
- Number of barcodes detected
- Barcodes with zero coverage
- Mean/median reads per barcode
- Min/max reads per barcode
- Coefficient of variation (uniformity measure)

#### Quality Indicators
- Singleton barcodes (only 1 read)
- Low coverage barcodes (<10 reads)
- Top 10 most abundant barcodes

## Interpreting Results

### Assignment Rate
- **>80%**: Excellent assignment
- **60-80%**: Good assignment
- **<60%**: May indicate quality issues or suboptimal parameters

### Coefficient of Variation (CV)
Measures uniformity of barcode distribution:
- **CV < 0.3**: Excellent uniformity
- **CV 0.3-0.5**: Good uniformity
- **CV 0.5-0.8**: Fair uniformity
- **CV > 0.8**: Poor uniformity (investigate library prep)

### Barcode Detection Rate
Percentage of barcodes in library that received at least one read:
- Should be close to 100% for well-covered libraries
- Low rates may indicate:
  - Insufficient sequencing depth
  - Library complexity issues
  - Failed barcodes

## Examples

### Example 1: QUIK with Real Data

```bash
nextflow run main.nf \
    --tool quik \
    --barcode_file /data/barcodes_21K_28nt.txt \
    --r1_fastq /data/Munchen_S1_R1.fastq \
    --r2_fastq /data/Munchen_S1_R2.fastq \
    --sample_id Munchen_21K_quik \
    --barcode_length 28 \
    --barcode_start 10 \
    --strategy 4_mer_gpu_v4 \
    --rejection_threshold 5 \
    --data_mode real \
    --outdir results/munchen/
```

### Example 2: RandomBarcodes with Real Data

```bash
nextflow run main.nf \
    --tool randombarcodes \
    --barcode_file /data/barcodes_85K_36nt.txt \
    --r1_fastq /data/Sample_R1.fastq.gz \
    --r2_fastq /data/Sample_R2.fastq.gz \
    --sample_id Sample_85K_RB \
    --barcode_length 36 \
    --ntriage 100 \
    --nthresh 7 \
    --gpus 1 \
    --data_mode real \
    --outdir results/sample/
```

### Example 3: Comparing Simulated vs Real Data

```bash
# First run: Simulated data with ground truth
nextflow run main.nf \
    --tool quik \
    --barcode_file barcodes.txt \
    --r1_fastq simulated_R1.fastq \
    --r2_fastq simulated_R2.fastq \
    --sample_id sim_quik \
    --ground_truth truth.txt \
    --outdir results/simulated/

# Second run: Real data without ground truth
nextflow run main.nf \
    --tool quik \
    --barcode_file barcodes.txt \
    --r1_fastq real_R1.fastq \
    --r2_fastq real_R2.fastq \
    --sample_id real_quik \
    --data_mode real \
    --outdir results/real/
```

## Troubleshooting

### Low Assignment Rate
**Problem**: Assignment rate < 50%

**Possible causes**:
- Rejection threshold too stringent
- Barcode start position incorrect
- Sequencing quality issues

**Solutions**:
- Try lowering rejection threshold
- Verify barcode position in reads
- Check FASTQ quality scores

### High CV (Poor Uniformity)
**Problem**: CV > 0.8

**Possible causes**:
- Uneven library amplification
- PCR bias
- Barcode synthesis quality issues

**Solutions**:
- Review library prep protocol
- Check for barcode sequence bias
- Consider reducing PCR cycles

### Many Zero-Coverage Barcodes
**Problem**: >10% barcodes not detected

**Possible causes**:
- Insufficient sequencing depth
- Failed barcode synthesis
- Library complexity loss

**Solutions**:
- Increase sequencing depth
- Verify barcode library quality
- Check for bottlenecks in library prep

## Comparing Results Across Samples

To compare multiple samples, you can consolidate the summary CSVs:

```bash
# Combine summary files
head -1 sample1_stats_summary.csv > combined_stats.csv
tail -n +2 sample1_stats_summary.csv >> combined_stats.csv
tail -n +2 sample2_stats_summary.csv >> combined_stats.csv
tail -n +2 sample3_stats_summary.csv >> combined_stats.csv
```

## Next Steps

After analyzing your real data results:

1. **Review the detailed report** (`*_stats_report.txt`) for quality assessment
2. **Check per-barcode coverage** (`*_per_barcode.csv`) for outliers
3. **Compare assignment rates** across different threshold values
4. **Visualize barcode distribution** to identify potential issues

For advanced analysis, see:
- `notebooks/` - Example analysis notebooks
- `util_scripts/` - Helper scripts for downstream analysis

## Support

For issues or questions:
1. Check the main README.md
2. Review example notebooks in `notebooks/`
3. See test data examples in `test_data/`
