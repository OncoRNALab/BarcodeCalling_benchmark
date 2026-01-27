# FASTQ Pair Generation from Simulated Reads

## Script: 3_Generate_FASTQ_pairs.py

This script converts simulated reads into paired FASTQ files suitable for downstream analysis.

## Features

- **Read1 (R1)**: Contains the original simulated read
- **Read2 (R2)**: Contains the reverse complement of the read
- **Headers**: Format `@read_<index>_barcode_<barcode_index>` (e.g., `@read_0_barcode_12345`)
- **Quality Scores**: Randomly generated in Phred+33 format (default range: 20-40)
- **Order Preservation**: Maintains the same order as input files for matching with answer files

## Usage

### Option 1: Using Config File (Recommended)

The script can read directly from the same config files used for simulation:

```bash
python scripts/3_Generate_FASTQ_pairs.py --config config_files/config_benchmark_85K_36nt_sim_low.yaml
```

The script will:
- Read `readsfilename` and `answersfilename` from the config
- Auto-generate output filenames: `<readsfilename>_R1.fastq` and `<readsfilename>_R2.fastq`

### Option 2: Direct File Paths

```bash
python scripts/3_Generate_FASTQ_pairs.py \
  --reads outputs/benchmark_85K_42K_21K/85K_36nt/reads_85K_36_low \
  --answers outputs/benchmark_85K_42K_21K/85K_36nt/answers_85K_36_low \
  --output-r1 outputs/benchmark_85K_42K_21K/85K_36nt/reads_85K_36_low_R1.fastq \
  --output-r2 outputs/benchmark_85K_42K_21K/85K_36nt/reads_85K_36_low_R2.fastq
```

### Option 3: Custom Quality Score Range

```bash
python scripts/3_Generate_FASTQ_pairs.py \
  --reads reads_file \
  --answers answers_file \
  --min-qual 15 \
  --max-qual 35
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--config` | Path to YAML config file | - |
| `--reads` | Path to simulated reads file | - |
| `--answers` | Path to answers file | - |
| `--output-r1` | Output path for Read1 FASTQ | Auto-generated |
| `--output-r2` | Output path for Read2 FASTQ | Auto-generated |
| `--min-qual` | Minimum quality score | 20 |
| `--max-qual` | Maximum quality score | 40 |

## Output Format

### FASTQ Record Structure

Each FASTQ record consists of 4 lines:
1. Header line (starts with @)
2. Sequence line
3. Plus line (+)
4. Quality line (same length as sequence)

### Example Output

**Read1 (R1):**
```
@read_0_barcode_12345
ATCGATCGATCGATCG
+
8<;9:>=<?@;:9<>=
```

**Read2 (R2):**
```
@read_0_barcode_12345
CGATCGATCGATCGAT
+
;:9<>=8<;9:>=<?@
```

## Batch Processing

To generate FASTQ files for all simulations, you can create a batch script:

```bash
#!/bin/bash
# Generate FASTQ pairs for all simulations

for config in config_files/config_benchmark_*_sim_*.yaml; do
    echo "Processing: $config"
    python scripts/3_Generate_FASTQ_pairs.py --config "$config"
done
```

Or for specific parameter combinations:

```bash
#!/bin/bash
# Generate FASTQ pairs for 85K 36nt simulations

for error in low medium high; do
    python scripts/3_Generate_FASTQ_pairs.py \
      --config config_files/config_benchmark_85K_36nt_sim_${error}.yaml
done
```

## Performance

- Processing speed: ~100,000 read pairs per second
- Memory usage: Minimal (reads line by line)
- Output size: ~2× input read file size (one FASTQ file per read end)

## File Size Estimates

For 1,000,000 reads of 36nt:
- Input reads file: ~36 MB
- Output R1.fastq: ~72 MB
- Output R2.fastq: ~72 MB
- Total output: ~144 MB

## Verification

The script includes built-in verification:
- Checks that reads and answers files have the same number of lines
- Reports progress every 100,000 reads
- Confirms successful completion with file paths

## Testing

A test script is provided to verify functionality:

```bash
python test_fastq_simple.py
```

This will:
- Create sample input files
- Generate paired FASTQ files
- Verify reverse complement generation
- Display sample output

## Integration with Existing Workflow

### Current Workflow
1. Generate barcodes: `1_BarcodeGen_split.py`
2. Simulate reads: `2_SimGen_split.py`

### Extended Workflow
1. Generate barcodes: `1_BarcodeGen_split.py`
2. Simulate reads: `2_SimGen_split.py`
3. **Generate FASTQ pairs: `3_Generate_FASTQ_pairs.py`** ← NEW

The FASTQ files can then be used with standard bioinformatics tools (alignment, quality control, etc.)

## Quality Scores

Quality scores are in Phred+33 format:
- ASCII characters from 33 to 73
- Quality score 20 = ASCII 53 = '5'
- Quality score 30 = ASCII 63 = '?'
- Quality score 40 = ASCII 73 = 'I'

Quality score interpretation:
- Q20: 1% error probability
- Q30: 0.1% error probability
- Q40: 0.01% error probability

## Troubleshooting

### ModuleNotFoundError: No module named 'yaml'

Install PyYAML:
```bash
pip install pyyaml
```

Or run without config file using direct paths.

### Mismatch error

Ensure reads and answers files have the same number of lines:
```bash
wc -l reads_file answers_file
```

### Memory issues with large files

The script processes line-by-line, so memory usage should be minimal even for large files.
