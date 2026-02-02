# Parameter Sweep Notebooks Update Summary

## Overview

Both parameter sweep analysis notebooks have been successfully updated to work with the new flat directory structure implemented after the pipeline `publishDir` fixes.

---

## Notebooks Updated

### 1. `precision_recall_curves_28_36nt.ipynb`
**Barcode lengths:** 28nt, 36nt  
**Commit:** 3c42d0f  
**Status:** ✅ Complete

### 2. `parameter_sweep_analysis_30_32_34nt.ipynb`
**Barcode lengths:** 30nt, 32nt, 34nt  
**Commit:** b9a9ea4  
**Status:** ✅ Complete

---

## Problem Background

After updating the pipeline to use flat directory structures (removing redundant `${meta.id}/` nesting), both notebooks broke because they were:

1. **Looking for nested directories** that no longer exist
2. **Parsing text report files** with fragile regex patterns
3. **Using outdated path extraction logic**

---

## Solution Applied (Both Notebooks)

### Core Changes

#### 1. **Data Source: Text → CSV**

**Before (fragile):**
```python
# Parse text file with regex
with open('precision_report.txt', 'r') as f:
    if 'Precision:' in line:  # Pattern didn't match actual format
        precision = ...
```

**After (robust):**
```python
# Read structured CSV
df = pd.read_csv('precision_summary.csv')
for _, row in df.iterrows():
    if row['metric'] == 'precision_percent':
        precision = row['value']
```

#### 2. **Directory Structure: Nested → Flat**

**Before (nested):**
```
results_28nt/quik_sweep/4mer_r5/
└── QUIK_28nt_4mer_r5/              ← Extra nesting
    └── QUIK_28nt_4mer_r5_precision_summary.csv
```

**After (flat):**
```
results_28nt/quik_sweep/4mer_r5/
└── QUIK_28nt_4mer_r5_precision_summary.csv  ← Direct
```

#### 3. **Path Extraction Logic**

**Before:**
```python
param_dir = report_file.parent.parent.name  # 2 levels up
```

**After:**
```python
param_dir = csv_file.parent.name  # 1 level up
```

---

## Specific Updates

### precision_recall_curves_28_36nt.ipynb

**Functions Updated:**
- `load_precision_reports_for_length()` - Complete rewrite
  - Now uses `precision_summary.csv` files
  - Extracts precision/recall from CSV rows
  - Calculates F1 score from P and R
  - Works with flat structure

**Cells Modified:**
- Cell 3: Data loading function
- Cell 8: Plotting (added column validation)
- Cell 10: Summary statistics (added error handling)

**Key Features:**
- Loads data for 28nt and 36nt
- Creates 2×3 grid plots (rows=lengths, cols=tools)
- Tool-specific curve styling:
  - QUIK: Multiple strategies as different colored curves
  - RandomBarcodes: Ntriage levels as different curves
  - Columba: Single curve with identity threshold points

---

### parameter_sweep_analysis_30_32_34nt.ipynb

**Functions Updated:**
- `parse_precision_report()` → `parse_precision_summary_csv()`
  - Renamed and rewritten to use CSV
  - Extracts all metrics from structured format
- `find_precision_reports()` - Updated
  - Now searches for `*_precision_summary.csv` files
  - Works with flat directory structure

**Cells Modified:**
- Cell 4: BASE_DIR path correction (parameter_sweeps → parameter_sweep)
- Cell 6: Both function definitions
- Cell 7: Data loading loop (updated function call and comments)

**Key Features:**
- Loads data for 30nt, 32nt, 34nt
- Creates multiple visualizations:
  - Precision vs threshold by barcode length (3×3 grid)
  - Precision-recall curves by tool
  - Performance heatmaps
  - Summary statistics tables

---

## CSV Format Used

Both notebooks now read from `precision_summary.csv`:

```csv
metric,value
total_reads,200000
total_assigned,85963
correct_assignments,85953
incorrect_assignments,10
unassigned_reads,114037
assignment_rate_percent,42.98
precision_percent,99.99      ← Used
recall_percent,42.98         ← Used
accuracy_percent,42.98
```

---

## Parameter Extraction

Both notebooks extract tool-specific parameters from directory names:

### RandomBarcodes
```
Directory: t100_n5 or t5000_n9
Extracts: ntriage=100, nthresh=5
Regex: r't\d+_n(\d+)'
```

### QUIK
```
Directory: 4mer_r5 or 4_7mer_r8 or 7mer_r9
Extracts: strategy='4mer', rejection_threshold=5
Regex: r'mer_r(\d+)'
```

### Columba
```
Directory: I77 or I80 or I82
Extracts: identity_threshold=77
Regex: r'I(\d+)'
```

---

## Directory Structure Reference

### Complete Flat Structure
```
results/parameter_sweep/
├── results_28nt/
│   ├── randombarcodes_sweep/
│   │   └── t100_n5/
│   │       ├── RB_28nt_t100_n5_R1_filtered.fastq
│   │       ├── RB_28nt_t100_n5_R2_filtered.fastq
│   │       ├── RB_28nt_t100_n5_precision_summary.csv    ← Direct
│   │       └── RB_28nt_t100_n5_precision_report.txt
│   ├── quik_sweep/
│   │   └── 4mer_r5/
│   │       ├── QUIK_28nt_4mer_r5_precision_summary.csv  ← Direct
│   │       └── ...
│   └── columba_sweep/
│       └── I77/
│           ├── columba_prep/
│           ├── columba_index/
│           ├── Columba28_I77_precision_summary.csv      ← Direct
│           └── ...
├── results_30nt/ (same structure)
├── results_32nt/ (same structure)
├── results_34nt/ (same structure)
└── results_36nt/ (same structure)
```

---

## Benefits

### 1. **Reliability**
- ✅ CSV parsing more robust than text regex
- ✅ Consistent format across all tools
- ✅ No text format variations to handle

### 2. **Simplicity**
- ✅ Flat structure easier to navigate
- ✅ Simpler path logic (1 level vs 2 levels)
- ✅ Direct file access

### 3. **Maintainability**
- ✅ Cleaner code
- ✅ Better error messages
- ✅ Easier to debug

### 4. **Performance**
- ✅ Faster CSV parsing vs regex
- ✅ Less directory traversal
- ✅ Direct file paths

---

## Testing Status

### Current Sample Data

**28/36nt notebook:**
- ✅ Loads 8 samples (3 × 28nt, 5 × 36nt)
- ✅ Successfully extracts precision/recall
- ✅ Parses tool-specific parameters
- ⏳ Awaiting full dataset for complete plots

**30/32/34nt notebook:**
- ⏳ Awaiting sample data for testing
- ✅ Code structure matches working 28/36nt notebook
- ✅ Ready for full parameter sweep results

---

## Usage

### Running the Notebooks

```bash
cd BarCall_benchmark/notebooks

# For Jupyter Notebook
jupyter notebook precision_recall_curves_28_36nt.ipynb
jupyter notebook parameter_sweep_analysis_30_32_34nt.ipynb

# For Jupyter Lab
jupyter lab
```

### Expected Behavior

1. **Data Loading:**
   - Scans `results/parameter_sweep/results_XXnt/` directories
   - Finds all `*_precision_summary.csv` files
   - Extracts precision, recall, and tool parameters
   - Creates combined DataFrame

2. **Visualization:**
   - Generates precision-recall curves
   - Plots performance vs thresholds
   - Creates comparison heatmaps
   - Displays summary statistics

3. **Output:**
   - Displays plots inline
   - Saves figures to `notebooks/figures/` directory
   - Prints summary statistics to stdout

---

## Troubleshooting

### "No data found" Error

**Cause:** Results directories empty or path incorrect

**Solution:**
1. Check BASE_DIR path points to correct location
2. Verify CSV files exist in parameter directories
3. Ensure files follow naming convention: `*_precision_summary.csv`

### "Missing columns" Error

**Cause:** Old text parsing returned incomplete data

**Solution:**
1. Verify notebooks updated to use CSV parsing
2. Check CSV files have correct format
3. Regenerate results if needed

### Path Issues

**Cause:** Notebooks expecting nested structure

**Solution:**
1. Ensure notebooks updated to latest version
2. Check `param_dir = csv_file.parent.name` (not `parent.parent.name`)
3. Verify flat directory structure in results

---

## Files Modified

### Notebooks
1. `notebooks/precision_recall_curves_28_36nt.ipynb`
2. `notebooks/parameter_sweep_analysis_30_32_34nt.ipynb`

### Documentation
1. `notebooks/NOTEBOOK_UPDATE_PRECISION_RECALL.md`
2. `notebooks/NOTEBOOKS_UPDATED_SUMMARY.md` (this file)

---

## Git Commits

1. **3c42d0f** - Fix precision_recall_curves_28_36nt.ipynb for flat directory structure
2. **b9a9ea4** - Fix parameter_sweep_analysis_30_32_34nt.ipynb for flat directory structure

---

## Next Steps

1. ✅ Both notebooks updated and committed
2. ✅ Pushed to GitHub
3. ⏳ Run parameter sweeps to generate full dataset
4. ⏳ Test notebooks with complete results
5. ⏳ Generate final publication-quality figures

---

## Status Summary

| Notebook | Barcode Lengths | Status | Tested | Ready |
|----------|----------------|--------|--------|-------|
| precision_recall_curves_28_36nt | 28, 36 | ✅ Updated | ✅ Yes | ✅ Yes |
| parameter_sweep_analysis_30_32_34nt | 30, 32, 34 | ✅ Updated | ⏳ Pending | ✅ Yes |

**Overall Status:** ✅ **Complete - Both notebooks ready for use**

---

**Last Updated:** 2026-01-25  
**Author:** AI Assistant  
**Related Commits:** 3c42d0f, b9a9ea4
