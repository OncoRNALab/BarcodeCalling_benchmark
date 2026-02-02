# Columba Output Structure Simplification

## Problem

Columba was generating an overly complex directory structure with unnecessary nesting:

**Before (Complex):**
```
results/error_rate_benchmark/columba/21K_36nt_low/
├── columba_build/                    ← NOT NEEDED (only versions.yml)
│   └── versions.yml
└── columba_21K_36nt_low/             ← EXTRA NESTING
    ├── columba_prep/
    │   ├── columba_21K_36nt_low_barcodes.fasta
    │   └── versions.yml
    ├── columba_index/
    │   ├── columba_21K_36nt_low_index.*
    │   └── versions.yml
    ├── columba_21K_36nt_low_alignment.sam
    ├── columba_21K_36nt_low_barcode_calling_stats.txt
    ├── columba_21K_36nt_low_precision_report.txt
    ├── columba_21K_36nt_low_precision_summary.csv
    └── versions.yml
```

### Issues:
1. `columba_build/` folder created with only `versions.yml` (build artifacts not needed in results)
2. All actual results nested under an extra `${meta.id}/` folder
3. Difficult to navigate and inconsistent with other tools

## Solution

Simplified the output structure by modifying `publishDir` directives in Nextflow processes.

**After (Simplified):**
```
results/error_rate_benchmark/columba/21K_36nt_low/
├── columba_prep/
│   ├── columba_21K_36nt_low_barcodes.fasta
│   └── versions.yml
├── columba_index/
│   ├── columba_21K_36nt_low_index.*
│   └── versions.yml
├── columba_21K_36nt_low_alignment.sam
├── columba_21K_36nt_low_barcode_calling_stats.txt
├── columba_21K_36nt_low_precision_report.txt
├── columba_21K_36nt_low_precision_summary.csv
└── versions.yml
```

### Benefits:
- Clean, flat structure
- No unnecessary `columba_build/` folder
- All outputs at same level
- Easy to find SAM files and summaries
- Consistent with user expectations

## Changes Made

### 1. `modules/barcode_to_fasta.nf`
**Before:**
```groovy
publishDir "${params.outdir}/${meta.id}/columba_prep", mode: 'copy'
```

**After:**
```groovy
publishDir "${params.outdir}/columba_prep", mode: 'copy'
```

### 2. `modules/columba.nf` - COLUMBA_BUILD
**Before:**
```groovy
publishDir "${params.outdir}/columba_build", mode: 'copy'
```

**After:**
```groovy
// Do not publish columba_build outputs (binaries not needed in results)
```

**Rationale:** Build artifacts (binaries) are intermediate files not needed in final results. Only `versions.yml` was being published, which is redundant.

### 3. `modules/columba.nf` - COLUMBA_INDEX
**Before:**
```groovy
publishDir "${params.outdir}/${meta.id}/columba_index", mode: 'copy'
```

**After:**
```groovy
publishDir "${params.outdir}/columba_index", mode: 'copy'
```

### 4. `modules/columba.nf` - COLUMBA_ALIGN
**Before:**
```groovy
publishDir "${params.outdir}/${meta.id}", mode: 'copy'
```

**After:**
```groovy
publishDir "${params.outdir}", mode: 'copy'
```

### 5. `main.nf` - Display Messages
Updated workflow completion messages to reflect new flat structure:

**Before:**
```groovy
SAM alignment: ${params.outdir}/${sample_meta.id}/${sam.name}
Statistics file: ${params.outdir}/${sample_meta.id}/${stats.name}
```

**After:**
```groovy
SAM alignment: ${params.outdir}/${sam.name}
Statistics file: ${params.outdir}/${stats.name}
```

## Output Structure by Benchmark Type

### Error Rate Benchmark
```
results/error_rate_benchmark/columba/21K_36nt_low/
├── columba_prep/
│   └── columba_21K_36nt_low_barcodes.fasta
├── columba_index/
│   └── columba_21K_36nt_low_index.*
├── columba_21K_36nt_low_alignment.sam
├── columba_21K_36nt_low_barcode_calling_stats.txt
├── columba_21K_36nt_low_precision_report.txt
└── columba_21K_36nt_low_precision_summary.csv
```

### Parameter Sweeps
```
results/parameter_sweeps/results_28nt/columba_sweep/I77/
├── columba_prep/
├── columba_index/
├── Columba28_I77_alignment.sam
└── [summaries]
```

### Real Data
```
results/real_data/columba/21k/
├── columba_prep/
├── columba_index/
├── Columba_21k_alignment.sam
└── [summaries]
```

## Testing

To verify the new structure works correctly:

1. **Regenerate a Columba job:**
   ```bash
   cd BarCall_benchmark
   python bin/generate_jobs_and_params_error_rate.py \
       --data-dir /path/to/data
   ```

2. **Run a test job:**
   ```bash
   nextflow run main.nf \
       -params-file error_rate_benchmark/params/columba_21K_low.json \
       -profile local,singularity
   ```

3. **Verify structure:**
   ```bash
   tree results/error_rate_benchmark/columba/21K_36nt_low/
   
   # Should show:
   # ├── columba_prep/
   # ├── columba_index/
   # ├── *.sam
   # └── *.txt, *.csv
   
   # Should NOT show:
   # └── columba_build/  (removed)
   # └── columba_21K_36nt_low/  (flattened)
   ```

## Files Modified

1. `modules/barcode_to_fasta.nf` - Removed `/${meta.id}` from publishDir
2. `modules/columba.nf` - Modified 3 processes:
   - `COLUMBA_BUILD` - Disabled publishDir
   - `COLUMBA_INDEX` - Removed `/${meta.id}` from publishDir
   - `COLUMBA_ALIGN` - Removed `/${meta.id}` from publishDir
3. `main.nf` - Updated display messages to reflect flat structure

## Impact

- **Existing results:** Old nested structure remains unchanged
- **New runs:** Will use simplified flat structure
- **Scripts/notebooks:** May need updates if they expect nested paths
- **Parameter files:** No changes needed (outdir remains the same)

## Migration Note

If you have existing analysis scripts or notebooks that reference the old nested structure:

**Old path pattern:**
```python
sam_file = f"{outdir}/columba_build/../{sample_id}/{sample_id}_alignment.sam"
```

**New path pattern:**
```python
sam_file = f"{outdir}/{sample_id}_alignment.sam"
```

**Update pattern matching:**
```python
# Old
sam_files = glob.glob(f"{results_dir}/**/columba_*/columba_*/*_alignment.sam")

# New
sam_files = glob.glob(f"{results_dir}/**/*_alignment.sam")
```

## Commit Details

**Commit:** [to be added]
**Files Modified:** 3 files (barcode_to_fasta.nf, columba.nf, main.nf)
**Impact:** All future Columba runs will use simplified structure
**Status:** ✅ Ready for testing
