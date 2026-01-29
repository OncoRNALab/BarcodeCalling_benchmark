# Fullset_benchmark_1M.ipynb - Fixes Summary

## Date: 2026-01-22

## Issues Fixed

### 1. RandomBarcodes Runtime Extraction (Cell 6)

**Problem:**
- The notebook was trying to extract runtime data from Nextflow trace files
- RandomBarcodes doesn't generate trace files in the work directory
- This caused 0/3 RandomBarcodes runtimes to be loaded

**Solution:**
- Added new function `parse_randombarcodes_stats()` to extract runtime from `_barcode_calling_stats.txt` files
- These files are located in the results directory: `results_1million_reads/{tool}_{bc_count}/{exp_name}/{exp_name}_barcode_calling_stats.txt`
- Function parses "Total time (seconds): X" line and converts to "Xm Ys" format
- Now correctly extracts runtime for all 3 RandomBarcodes experiments (21K, 42K, 85K)

**Example:**
```
File: randombarcodes_21K_1M_barcode_calling_stats.txt
Line: Total time (seconds): 8500.56
Parsed: 141m 40s
```

### 2. 200K Data Loading for Comparison (Cell 9)

**Problem:**
- The notebook was loading from wrong directory: `results_sweep/results_36nt/summaries/all_corrected_metrics.csv`
- This file contained results with multiple error rates and parameter combinations
- Not appropriate for direct comparison with 1M results (which used medium error rate)

**Solution:**
- Changed source directory to: `BarCall_benchmark/error_rate_benchmark/results`
- Now loads only **medium error rate** experiments for comparison
- Directly reads from precision_summary.csv files for each tool/barcode combination
- Matches the experimental conditions of the 1M reads benchmark

**Directory Structure:**
```
error_rate_benchmark/results/
├── randombarcodes_21K_36nt_medium/
│   └── randombarcodes_21K_36nt_medium/
│       └── randombarcodes_21K_36nt_medium_precision_summary.csv
├── randombarcodes_42K_36nt_medium/
├── randombarcodes_85K_36nt_medium/
├── quik_21K_36nt_medium/
├── quik_42K_36nt_medium/
├── quik_85K_36nt_medium/
├── columba_21K_36nt_medium/
├── columba_42K_36nt_medium/
└── columba_85K_36nt_medium/
```

## Expected Results After Fixes

### Runtime Extraction:
- **Before:** 6/9 experiments (0 RandomBarcodes, 3 QUIK, 3 Columba)
- **After:** 9/9 experiments (3 RandomBarcodes, 3 QUIK, 3 Columba)

### 200K Comparison Data:
- **Before:** 0 experiments loaded (wrong file path)
- **After:** 9 experiments loaded (3 tools × 3 barcode counts, medium error rate only)

## Benefits

1. **Complete Runtime Analysis:** All 9 runtime measurements now available for comparison plots
2. **Accurate Scaling Analysis:** Proper comparison between 200K and 1M using same error rate (medium)
3. **Consistent Parameters:** Both datasets use the same tool parameters (nthresh=9, rejection_threshold=8, identity_threshold=80)
4. **Valid Conclusions:** Scaling metrics (200K → 1M) are now meaningful and accurate

## Verification

To verify the fixes worked correctly, check the notebook output:

**Cell 6 Output should show:**
```
✓ Extracted: RANDOMBARCODES  21K (from stats file)
✓ Extracted: RANDOMBARCODES  42K (from stats file)
✓ Extracted: RANDOMBARCODES  85K (from stats file)
✓ Extracted: QUIK            21K (from trace)
✓ Extracted: QUIK            42K (from trace)
✓ Extracted: QUIK            85K (from trace)
✓ Extracted: COLUMBA         21K (from trace)
✓ Extracted: COLUMBA         42K (from trace)
✓ Extracted: COLUMBA         85K (from trace)

Runtime info extracted: 9 / 9
```

**Cell 9 Output should show:**
```
✓ Loaded: RANDOMBARCODES  21K
✓ Loaded: RANDOMBARCODES  42K
✓ Loaded: RANDOMBARCODES  85K
✓ Loaded: QUIK            21K
✓ Loaded: QUIK            42K
✓ Loaded: QUIK            85K
✓ Loaded: COLUMBA         21K
✓ Loaded: COLUMBA         42K
✓ Loaded: COLUMBA         85K

✓ Loaded 200K results: 9 experiments (medium error rate)
```

## New Visualizations Added

### Precision and Recall Bar Plots (Section 6.1)

Added grouped bar plots comparing precision and recall between 200K and 1M datasets:

**Features:**
- **Layout:** 2 rows × 3 columns (Precision top, Recall bottom; one column per tool)
- **Color Coding:**
  - 🔴 Red bars = 200K reads
  - 🟢 Green bars = 1M reads
- **Value Labels:** Numeric values displayed on top of each bar
- **Grouped by:** Barcode count (21K, 42K, 85K) on x-axis

**Benefits:**
- Direct visual comparison of performance at different scales
- Easy identification of trends (improvement/degradation) when scaling from 200K to 1M
- Clear quantitative values for each condition
- Consistent color scheme for dataset size across all plots

**Output:** `figures/precision_recall_bars_200K_vs_1M.pdf`

### Delta Metrics Analysis (Section 6.2)

Added two-panel dot plots showing metric changes (Δ) when scaling from 200K to 1M reads:

**Panel A - Δ Precision:**
- Formula: Δ Precision = Precision₁ₘ - Precision₂₀₀ₖ
- Y-axis: Change in precision (percentage points)
- X-axis: Tool (Randombarcodes, QUIK, Columba)

**Panel B - Δ Recall:**
- Formula: Δ Recall = Recall₁ₘ - Recall₂₀₀ₖ
- Y-axis: Change in recall (percentage points)
- X-axis: Tool (Randombarcodes, QUIK, Columba)

**Visual Encoding:**
- 🔵 **Blue dots** = 21K barcodes
- 🔴 **Red dots** = 42K barcodes
- 🟢 **Green dots** = 85K barcodes
- **Horizontal reference line at y=0:** No change
- **Value labels:** Exact change shown above each point

**Interpretation:**
- **At y=0:** Performance unchanged
- **Positive values (above line):** Improvement at 1M reads
- **Negative values (below line):** Degradation at 1M reads
- **Symmetric y-axes:** Makes small changes clearly visible

**Benefits:**
- Makes **small changes visible** (key advantage over scatter plots)
- Quantitative and honest representation
- No overplotting - each point clearly visible
- Immediately answers: "Does performance change at scale?"
- Side-by-side comparison reveals if precision/recall trends differ
- Grouped by tool for easy cross-tool comparison

**Output:** `figures/delta_metrics_200K_vs_1M.pdf`

## Related Files

- **Notebook:** `/notebooks/Fullset_benchmark_1M.ipynb`
- **1M Results:** `/results_1million_reads/`
- **200K Results:** `/BarCall_benchmark/error_rate_benchmark/results/`
- **README:** `/BarCall_benchmark/1million_reads/README.md`
