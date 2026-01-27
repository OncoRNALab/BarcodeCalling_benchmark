# Real Sequencing Data Analysis

This directory contains jobs and parameter files to run all three barcode calling tools (RandomBarcodes, QUIK, and Columba) on real sequencing data from the Munich dataset.

## Directory Structure

```
barcode_seq/
├── randombarcodes/
│   ├── jobs/          # SLURM job scripts for RandomBarcodes
│   ├── params/        # Parameter JSON files
│   ├── logs/          # Job output logs
│   └── submit_all.sh  # Submit all RandomBarcodes jobs
├── quik/
│   ├── jobs/          # SLURM job scripts for QUIK
│   ├── params/        # Parameter JSON files
│   ├── logs/          # Job output logs
│   └── submit_all.sh  # Submit all QUIK jobs
├── columba/
│   ├── jobs/          # SLURM job scripts for Columba
│   ├── params/        # Parameter JSON files
│   ├── logs/          # Job output logs
│   └── submit_all.sh  # Submit all Columba jobs
├── results/           # Output results directory
└── submit_all_tools.sh # Submit ALL jobs for all tools
```

## Datasets

Three real sequencing datasets with different barcode library sizes:

| Dataset | Barcode Count | R1 FASTQ | R2 FASTQ | Barcode File |
|---------|---------------|----------|----------|--------------|
| 21k | 21,476 | Munchen_25024_1in4_S4_L001_R1_001.fastq | Munchen_25024_1in4_S4_L001_R2_001.fastq | bar_1in4_column_major.txt |
| 42k | 42,652 | Munchen_25024_1in2_S1_L001_R1_001.fastq | Munchen_25024_1in2_S1_L001_R2_001.fastq | bar_1in2_column_major.txt |
| 85k | 85,305 | Munchen_25024_1in1_S2_L001_R1_001.fastq | Munchen_25024_1in1_S2_L001_R2_001.fastq | bar_1in1_column_major.txt |

All barcode sequences are **36 nucleotides** long.

## Tool Parameters

### RandomBarcodes
- Threshold: 9
- ntriage: 100
- GPUs: 2

### QUIK
- Threshold: 8
- Strategy: 4_mer_gpu_v4
- GPUs: 1

### Columba
- Identity Thresholds: 76, 77 (testing both)
- CPUs: 16

## Running the Analysis

### Option 1: Submit All Jobs at Once

```bash
cd /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/barcode_seq
bash submit_all_tools.sh
```

This will submit **12 total jobs**:
- 3 RandomBarcodes jobs (21k, 42k, 85k)
- 3 QUIK jobs (21k, 42k, 85k)
- 6 Columba jobs (21k×2, 42k×2, 85k×2 for two thresholds)

### Option 2: Submit by Tool

**RandomBarcodes only:**
```bash
cd randombarcodes
bash submit_all.sh
```

**QUIK only:**
```bash
cd quik
bash submit_all.sh
```

**Columba only:**
```bash
cd columba
bash submit_all.sh
```

### Option 3: Submit Individual Jobs

```bash
cd randombarcodes/jobs
sbatch job_21k.sh
```

## Monitoring Jobs

**Check job status:**
```bash
squeue -u $USER
```

**Check specific job logs:**
```bash
# RandomBarcodes 21k log
tail -f randombarcodes/logs/RB_real_21k.out

# QUIK 42k log
tail -f quik/logs/QUIK_real_42k.out

# Columba 85k (threshold 77) log
tail -f columba/logs/Columba_85k_I77.out
```

**Cancel all jobs:**
```bash
scancel -u $USER
```

## Expected Outputs

For each dataset, the pipeline will generate in the respective results directory:

### 1. Barcode Calling Results
- `{sample_id}_filtered_R1.fastq` - Filtered R1 reads with barcode assignments
- `{sample_id}_filtered_R2.fastq` - Filtered R2 reads
- `{sample_id}_stats.txt` - Tool-specific statistics

### 2. Quality Metrics (Real Data Mode)
- `{sample_id}_stats_report.txt` - **Detailed statistical report**
- `{sample_id}_stats_summary.csv` - **Summary metrics in CSV format**
- `{sample_id}_per_barcode.csv` - **Per-barcode read counts**

### 3. Key Metrics

Since this is real data without ground truth, you'll get:
- **Assignment Rate**: Percentage of reads successfully assigned to barcodes
- **Distribution Uniformity**: Coefficient of variation (CV) - lower is more uniform
- **Coverage**: Mean/median/min/max reads per barcode
- **Quality Indicators**: Singleton barcodes, low coverage barcodes

## Interpreting Results

### Assignment Rate
- **>80%**: Excellent quality
- **60-80%**: Good quality
- **<60%**: Poor quality, investigate issues

### Coefficient of Variation (CV)
- **<0.3**: Excellent uniformity
- **0.3-0.5**: Good uniformity
- **>0.5**: High variability, may indicate issues

See [REAL_DATA_GUIDE.md](../docs/REAL_DATA_GUIDE.md) for detailed interpretation.

## Work Directories

Each job uses a unique work directory to avoid conflicts:
```
/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_realdata/
├── randombarcodes/
│   ├── 21k/
│   ├── 42k/
│   └── 85k/
├── quik/
│   ├── 21k/
│   ├── 42k/
│   └── 85k/
└── columba/
    ├── 21k_I76/
    ├── 21k_I77/
    ├── 42k_I76/
    ├── 42k_I77/
    ├── 85k_I76/
    └── 85k_I77/
```

## Resource Requirements

| Tool | CPUs | GPUs | Memory | Time Limit |
|------|------|------|--------|------------|
| RandomBarcodes | 2 | 2 | 16G | 24h |
| QUIK | 1 | 1 | 16G | 24h |
| Columba | 16 | 0 | 32G | 48h |

## Troubleshooting

**Job fails to start:**
- Check SLURM logs in the `logs/` directory
- Verify input files exist: `ls -lh /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BCseq_01/`

**Pipeline errors:**
- Check Nextflow logs in the work directory
- Look for `.nextflow.log` file

**Low assignment rates:**
- Verify barcode file format (one barcode per line, 36nt each)
- Check FASTQ quality scores
- Consider adjusting tool-specific thresholds

## Next Steps

After jobs complete:
1. Review statistics summaries in results directories
2. Compare assignment rates across tools and datasets
3. Analyze distribution uniformity (CV values)
4. Create visualizations for comparison with simulated data results
