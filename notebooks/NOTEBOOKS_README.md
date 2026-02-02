# Analysis Notebooks Guide

This directory contains Jupyter notebooks for analyzing barcode calling benchmark results.

---

## Quick Reference

| Notebook | Benchmark | Results Directory | Description |
|----------|-----------|-------------------|-------------|
| `errorrate_benchmark_200K.ipynb` | Error Rate | `../results/error_rate_benchmark` | Performance across error rates (low/medium/high) |
| `Fullset_benchmark_1M.ipynb` | 1M Scaling | `../results/scaling_1M_benchmark` | Scalability analysis with 1M reads |
| `runtime_analysis.ipynb` | Runtime | `../results/runtime_benchmark` | Computational performance analysis |
| `precision_recall_curves_28_36nt.ipynb` | Parameter Sweep | `../results/parameter_sweep` | Precision-recall curves for 28/36nt barcodes |
| `parameter_sweep_analysis_30_32_34nt.ipynb` | Parameter Sweep | `../results/parameter_sweep` | Performance analysis for 30/32/34nt barcodes |
| `real_data_comparison.ipynb` | Real Data | `../results/real_data` | Comparison on real sequencing data |
| `barcode_count_sweep_analysis.ipynb` | Barcode Count Sweep | Various | Analysis across different barcode counts |

---

## Prerequisites

Before running any notebook, ensure you have:

1. **Generated jobs and parameters** using the generation scripts (see `../BENCHMARK_SETUP_GUIDE.md`)
2. **Run the benchmarks** and have results in the correct directories
3. **Installed required Python packages**:
   ```bash
   pip install jupyter pandas numpy matplotlib seaborn pathlib
   ```

---

## Detailed Notebook Descriptions

### 1. Error Rate Benchmark (`errorrate_benchmark_200K.ipynb`)

**Results Directory**: `../results/error_rate_benchmark`

**Purpose**: Analyze tool performance across different sequencing error rates

**What it analyzes**:
- Precision, recall, F1 score across 3 error rates (low, medium, high)
- Performance degradation with increasing error rates
- Tool-specific error sensitivity
- 27 experiments total (3 tools × 3 barcode counts × 3 error rates)

**Key Visualizations**:
- Precision vs Recall scatter plots
- F1 score comparison across error rates
- Performance heatmaps
- Assignment rate analysis

**Expected Data Structure**:
```
../results/error_rate_benchmark/
├── randombarcodes/
│   ├── 21K_36nt_low/
│   ├── 21K_36nt_medium/
│   ├── 21K_36nt_high/
│   └── ... (9 total)
├── quik/
│   └── ... (9 total)
└── columba/
    └── ... (9 total)
```

**To Run**:
```bash
jupyter notebook errorrate_benchmark_200K.ipynb
```

---

### 2. 1M Scaling Benchmark (`Fullset_benchmark_1M.ipynb`)

**Results Directory**: `../results/scaling_1M_benchmark`

**Purpose**: Evaluate tool performance and computational requirements at production scale (1M reads)

**What it analyzes**:
- Precision, recall, F1 score with 1M reads
- Runtime and memory usage
- Scalability across different barcode counts
- 9 experiments total (3 tools × 3 barcode counts)

**Key Visualizations**:
- Performance comparison tables
- Precision vs Recall plots
- Runtime analysis
- Memory usage patterns

**Expected Data Structure**:
```
../results/scaling_1M_benchmark/
├── randombarcodes/
│   ├── 21K_36nt/
│   ├── 42K_36nt/
│   └── 85K_36nt/
├── quik/
│   └── ... (3 total)
└── columba/
    └── ... (3 total)
```

**To Run**:
```bash
jupyter notebook Fullset_benchmark_1M.ipynb
```

---

### 3. Runtime Analysis (`runtime_analysis.ipynb`)

**Results Directory**: `../results/runtime_benchmark`

**Purpose**: Analyze computational efficiency across different read counts

**What it analyzes**:
- Runtime scaling with read count
- CPU vs GPU performance
- Computational efficiency metrics
- Multiple read counts: 200, 2K, 20K, 200K, 400K, 600K, 800K, 1M, 1.2M reads

**Key Visualizations**:
- Runtime vs read count plots
- Tool comparison charts
- Efficiency curves
- Resource utilization analysis

**Expected Data Structure**:
```
../results/runtime_benchmark/
├── randombarcodes/
│   ├── 200reads/
│   ├── 2Kreads/
│   └── ... (9 total)
├── quik/
│   └... (9 total)
└── columba/
    └── ... (9 total)
```

**To Run**:
```bash
jupyter notebook runtime_analysis.ipynb
```

---

### 4. Parameter Sweep - 28/36nt (`precision_recall_curves_28_36nt.ipynb`)

**Results Directory**: `../results/parameter_sweep`

**Purpose**: Explore precision-recall trade-offs for 28nt and 36nt barcodes

**What it analyzes**:
- Parameter sensitivity for each tool
- Optimal parameter selection
- Precision-recall curves
- Tool-specific parameter ranges:
  - **RandomBarcodes**: ntriage (100, 5000) × nthresh (5-9)
  - **QUIK**: strategies (4mer, 7mer, 4_7mer) × rejection thresholds (5-9)
  - **Columba**: identity thresholds (77-84%)

**Key Visualizations**:
- Precision-recall curves (2×3 grid: 2 lengths × 3 tools)
- F1 score heatmaps
- Parameter sensitivity plots
- Tool comparison charts

**Expected Data Structure**:
```
../results/parameter_sweep/
├── results_28nt/
│   ├── randombarcodes_sweep/
│   ├── quik_sweep/
│   └── columba_sweep/
└── results_36nt/
    └── ...
```

**To Run**:
```bash
jupyter notebook precision_recall_curves_28_36nt.ipynb
```

---

### 5. Parameter Sweep - 30/32/34nt (`parameter_sweep_analysis_30_32_34nt.ipynb`)

**Results Directory**: `../results/parameter_sweep`

**Purpose**: Comprehensive parameter sweep analysis for intermediate barcode lengths

**What it analyzes**:
- Performance across 30nt, 32nt, 34nt barcodes
- Parameter optimization for each length
- Comparative analysis across lengths
- Same parameter ranges as 28/36nt notebook

**Key Visualizations**:
- Precision vs rejection threshold (3×3 grid: 3 lengths × 3 tools)
- Precision-recall curves by tool
- Performance heatmaps
- Summary statistics tables

**Expected Data Structure**:
```
../results/parameter_sweep/
├── results_30nt/
│   └── ...
├── results_32nt/
│   └── ...
└── results_34nt/
    └── ...
```

**To Run**:
```bash
jupyter notebook parameter_sweep_analysis_30_32_34nt.ipynb
```

---

### 6. Real Data Comparison (`real_data_comparison.ipynb`)

**Results Directory**: `../results/real_data`

**Purpose**: Validate tools on real BCseq data with known barcodes

**What it analyzes**:
- Performance on real sequencing data
- Real vs decoy barcode discrimination
- Three array sizes: 21k, 42k, 85k barcodes
- Actual vs expected assignment patterns
- 18 experiments total (3 arrays × 2 barcode sets × 3 tools)

**Key Visualizations**:
- Assignment rate comparisons
- Real vs decoy discrimination
- Tool performance tables
- Array-specific analysis

**Expected Data Structure**:
```
../results/real_data/
├── randombarcodes/
│   ├── 21k/         (real barcodes)
│   ├── 21k_decoy/   (decoy barcodes)
│   ├── 42k/
│   ├── 42k_decoy/
│   ├── 85k/
│   └── 85k_decoy/
├── quik/
│   └── ... (6 total)
└── columba/
    └── ... (6 total)
```

**To Run**:
```bash
jupyter notebook real_data_comparison.ipynb
```

---

### 7. Barcode Count Sweep (`barcode_count_sweep_analysis.ipynb`)

**Results Directory**: Multiple (historical data)

**Purpose**: Analyze performance trends across different barcode set sizes

**What it analyzes**:
- Effect of barcode count on performance
- Trends across 21K, 42K, 85K barcodes
- Tool comparison at different scales

**To Run**:
```bash
jupyter notebook barcode_count_sweep_analysis.ipynb
```

---

## Common Workflow

### 1. Ensure Results Exist

Before running a notebook, verify the results directory exists:

```bash
# Check error rate benchmark results
ls -la ../results/error_rate_benchmark/

# Check 1M scaling results
ls -la ../results/scaling_1M_benchmark/

# Check parameter sweep results
ls -la ../results/parameter_sweep/
```

### 2. Start Jupyter

```bash
cd notebooks
jupyter notebook
```

Or use JupyterLab:
```bash
jupyter lab
```

### 3. Run the Notebook

- Select the desired notebook
- Run all cells: `Cell > Run All`
- Or run cells individually: `Shift + Enter`

### 4. Export Figures

Most notebooks save figures to the `figures/` subdirectory:

```bash
ls -la figures/
```

---

## Troubleshooting

### Issue: "No data found" or "Results directory doesn't exist"

**Cause**: Results haven't been generated yet or are in the wrong location

**Solution**:
1. Check if results directory exists
2. Verify you've run the generation scripts
3. Ensure benchmarks have completed successfully
4. Check the results path matches the generation script `--results-dir` argument

### Issue: "Module not found" errors

**Cause**: Missing Python packages

**Solution**:
```bash
pip install pandas numpy matplotlib seaborn jupyter
```

### Issue: "Kernel died" or memory errors

**Cause**: Large datasets consuming too much memory

**Solution**:
1. Restart the kernel: `Kernel > Restart`
2. Run cells individually instead of all at once
3. Close other notebooks
4. Increase available memory

### Issue: Plots not displaying

**Cause**: Missing backend or display settings

**Solution**:
```python
# Add to first cell
%matplotlib inline
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = (12, 8)
```

---

## Results Directory Structure Reference

All notebooks expect results in the following structure (generated by the scripts):

```
BarCall_benchmark/
├── results/
│   ├── error_rate_benchmark/
│   │   ├── randombarcodes/
│   │   ├── quik/
│   │   ├── columba/
│   │   └── reports/
│   │
│   ├── scaling_1M_benchmark/
│   │   ├── randombarcodes/
│   │   ├── quik/
│   │   ├── columba/
│   │   └── reports/
│   │
│   ├── runtime_benchmark/
│   │   ├── randombarcodes/
│   │   ├── quik/
│   │   ├── columba/
│   │   └── reports/
│   │
│   ├── parameter_sweep/
│   │   ├── results_28nt/
│   │   ├── results_30nt/
│   │   ├── results_32nt/
│   │   ├── results_34nt/
│   │   └── results_36nt/
│   │
│   └── real_data/
│       ├── randombarcodes/
│       ├── quik/
│       ├── columba/
│       └── reports/
│
└── notebooks/          ← You are here
    ├── errorrate_benchmark_200K.ipynb
    ├── Fullset_benchmark_1M.ipynb
    ├── runtime_analysis.ipynb
    ├── precision_recall_curves_28_36nt.ipynb
    ├── parameter_sweep_analysis_30_32_34nt.ipynb
    ├── real_data_comparison.ipynb
    ├── barcode_count_sweep_analysis.ipynb
    ├── figures/         ← Generated plots
    └── NOTEBOOKS_README.md  ← This file
```

---

## Generating Complete Documentation

### For Each Benchmark

See `../BENCHMARK_SETUP_GUIDE.md` for complete instructions on:
1. Downloading data from Zenodo
2. Generating jobs and parameters
3. Running benchmarks
4. Expected output directories

### Quick Start Example

```bash
# 1. Generate jobs for error rate benchmark
cd BarCall_benchmark
python3 bin/generate_jobs_and_params_error_rate.py \
    --data-dir /path/to/benchmark_data \
    --output-dir error_rate_benchmark \
    --results-dir results/error_rate_benchmark

# 2. Submit jobs
bash error_rate_benchmark/submit_all_error_rate_benchmarks.sh

# 3. Wait for completion
squeue -u $USER

# 4. Analyze results
cd notebooks
jupyter notebook errorrate_benchmark_200K.ipynb
```

---

## Additional Resources

- **Main Setup Guide**: `../BENCHMARK_SETUP_GUIDE.md`
- **Pipeline Documentation**: `../README.md`
- **Generation Scripts**: `../bin/generate_jobs_and_params_*.py`

---

## Notes

- All paths in notebooks are **relative** to the `notebooks/` directory
- Use `../results/` prefix to access results from notebooks
- Figures are saved to `figures/` subdirectory (auto-created)
- Notebooks are independent and can be run in any order
- Each notebook is self-contained with its own data loading

---

**Last Updated**: 2026-01-25  
**Maintainer**: [Your Name]
