# Notebook Update: precision_recall_curves_28_36nt.ipynb

## Problem

After updating the pipeline output directory structure to be flat (removing redundant `${meta.id}/` nesting), the notebook `precision_recall_curves_28_36nt.ipynb` stopped working correctly. It was only loading tool and barcode_length information, but not the actual precision/recall values.

## Root Causes

### 1. Directory Structure Change
**Before (nested):**
```
results_28nt/quik_sweep/4mer_r5/QUIK_28nt_4mer_r5/QUIK_28nt_4mer_r5_precision_summary.csv
```

**After (flat):**
```
results_28nt/quik_sweep/4mer_r5/QUIK_28nt_4mer_r5_precision_summary.csv
```

The notebook was looking for files in a nested subdirectory structure that no longer exists.

### 2. Data Source Issue
The notebook was parsing text `precision_report.txt` files instead of using the structured `precision_summary.csv` files, which is:
- More fragile (text parsing)
- Less reliable (inconsistent format between tools)
- Slower

### 3. Text Parsing Format Mismatch
The text report uses:
- `"Precision (correct/assigned):"` NOT `"Precision:"`
- `"Recall (correct/total):"` NOT `"Recall:"`

So the regex patterns were not matching.

## Solution Implemented

### Updated `load_precision_reports_for_length()` Function

1. **Changed data source**: Use `precision_summary.csv` files instead of text reports
2. **Fixed path logic**: Updated to work with flat directory structure
3. **Read CSV directly**: Parse structured CSV data instead of text
4. **Calculate F1 score**: Compute from precision and recall values

### Key Changes

#### Cell 3 - Data Loading

**Old approach:**
```python
# Find all precision_report.txt files (nested structure)
for report_file in sweep_dir.rglob('*precision_report.txt'):
    # Parse text file with regex
    if 'Precision:' in line:
        metrics['precision'] = ...
    # Get param dir (two levels up for nested structure)
    param_dir = report_file.parent.parent.name
```

**New approach:**
```python
# Find all precision_summary.csv files (flat structure)
for csv_file in sweep_dir.rglob('*precision_summary.csv'):
    # Read CSV directly
    df_metrics = pd.read_csv(csv_file)
    # Extract precision/recall from CSV rows
    for _, row in df_metrics.iterrows():
        if row['metric'] == 'precision_percent':
            metrics['precision'] = row['value']
    # Get param dir (one level up for flat structure)
    param_dir = csv_file.parent.name
```

#### Cell 8 - Plotting

Added checks for:
- Empty dataframe
- Missing 'precision' and 'recall' columns
- Missing tool-specific parameter columns ('strategy', 'ntriage', etc.)
- Better error messages

#### Cell 10 - Summary Statistics

Added checks for:
- Empty dataframe
- Missing required columns
- Better error handling

## File Structure Reference

### Flat Structure (Current)
```
results/parameter_sweep/
├── results_28nt/
│   ├── randombarcodes_sweep/
│   │   └── t100_n5/
│   │       ├── RB_28nt_t100_n5_R1_filtered.fastq
│   │       ├── RB_28nt_t100_n5_R2_filtered.fastq
│   │       ├── RB_28nt_t100_n5_precision_summary.csv     ← Direct
│   │       └── RB_28nt_t100_n5_precision_report.txt
│   ├── quik_sweep/
│   │   └── 4mer_r5/
│   │       ├── QUIK_28nt_4mer_r5_R1_filtered.fastq
│   │       ├── QUIK_28nt_4mer_r5_precision_summary.csv   ← Direct
│   │       └── QUIK_28nt_4mer_r5_precision_report.txt
│   └── columba_sweep/
│       └── I77/
│           ├── columba_prep/
│           ├── columba_index/
│           ├── Columba28_I77_alignment.sam
│           ├── Columba28_I77_precision_summary.csv       ← Direct
│           └── Columba28_I77_precision_report.txt
└── results_36nt/
    └── (same structure)
```

## CSV Format

`precision_summary.csv` structure:
```csv
metric,value
total_reads,200000
total_assigned,85963
correct_assignments,85953
incorrect_assignments,10
unassigned_reads,114037
assignment_rate_percent,42.9815
precision_percent,99.9884      ← Used
recall_percent,42.9765         ← Used
accuracy_percent,42.9765
```

## Parameter Parsing

The notebook parses parameter directory names to extract tool-specific parameters:

### RandomBarcodes
- Directory format: `t100_n5`
- Extracts: `ntriage=100`, `nthresh=5`

### QUIK
- Directory format: `4mer_r5` or `4_7mer_r5`
- Extracts: `strategy='4mer'`, `rejection_threshold=5`

### Columba
- Directory format: `I77`
- Extracts: `identity_threshold=77`

## Testing

With the current sample data:
- **28nt**: 3 samples (1 QUIK, 2 Columba)
- **36nt**: 5 samples (2 QUIK, 3 Columba)
- **Total**: 8 samples

Expected output columns:
- `tool`, `barcode_length`, `sample_id`
- `precision`, `recall`, `accuracy`, `f1_score`
- Tool-specific: `strategy`/`rejection_threshold` OR `ntriage`/`nthresh` OR `identity_threshold`

## Future Improvements

1. **Add RandomBarcodes data**: Currently missing from test dataset
2. **Add more parameter points**: For better curve visualization
3. **Consider caching**: Cache parsed data for faster reloading
4. **Add data validation**: Check for missing/invalid values
5. **Better error reporting**: More detailed messages for debugging

## Files Modified

- `notebooks/precision_recall_curves_28_36nt.ipynb`
  - Cell 3: Data loading function
  - Cell 8: Plotting code
  - Cell 10: Summary statistics

## Status

✅ Notebook updated to work with flat directory structure
✅ Uses CSV files for reliable data parsing
✅ Handles missing data gracefully
✅ Tested with current sample dataset
⏳ Ready for full dataset when available
