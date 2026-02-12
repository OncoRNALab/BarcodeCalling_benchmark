# Analysis Notebooks

This directory contains Jupyter notebooks for analyzing benchmark results.

## Notebooks Overview

### 1. Error-Rate Analysis
**`errorrate_benchmark_200K.ipynb`**
- Analyzes performance under low/medium/high error regimes
- Plots: Precision-recall curves by error rate
- Tables: Summary statistics per tool × barcode count × error regime
- **Data required**: `error_rate_benchmark/results/`

### 2. Scaling Analysis (200K vs 1M reads)
**`Fullset_benchmark_1M.ipynb`**
- Compares performance at 200k and 1M read depths
- Plots: Delta metrics (Δ precision, Δ recall)
- Tables: Scaling stability metrics
- **Data required**: `error_rate_benchmark/results/` + `results_1million_reads/`

### 3. Barcode Library Size Analysis
**`barcode_count_sweep_analysis.ipynb`**
- Evaluates effect of increasing barcode count (21k → 42k → 85k)
- Selection criterion: precision ≥99.5%, then max recall
- **Data required**: `parameter_sweeps_barcode_count/` results

### 4. Parameter Calibration (Threshold Sweeps)
**`precision_recall_curves_28_36nt.ipynb`**
**`parameter_sweep_analysis_30_32_34nt.ipynb`**
- Precision-recall trade-off curves for each tool
- Optimal operating-point selection
- **Data required**: `results_sweep/results_<LEN>nt/`

### 5. Precision-Recall Curves
**`precision_recall_curves_28_36nt.ipynb`**
- Combined precision-recall visualization
- **Data required**: parameter sweep results

### 6. Real Data Analysis
**`real_data_comparison.ipynb`**
- Assignment rates and decoy-estimated precision
- Barcode overlap/coverage analysis (Venn diagrams, Jaccard similarity)
- **Data required**: `barcode_seq/results/`

### 7. Runtime Analysis
**`runtime_analysis.ipynb`**
- Throughput comparison (reads/s)
- Parallel scaling efficiency
- **Data required**: `runtime_benchmarks/` work directories and trace files

## Output Directories

- **`figures/`**: PDF/PNG plots for the manuscript
- **`tables/`**: CSV exports of summary tables

## Running Notebooks

All notebooks expect results to be present in the locations specified above (relative to the benchmark output directories). If you've reproduced the benchmarks using the generator scripts, the paths should match automatically.

### Example workflow

```bash
# 1. Run a benchmark
python3 bin/generate_jobs_and_params_error_rate.py \
    --data-dir data/benchmark_85K_42K_21K_200K \
    --results-dir results/error_rate
bash error_rate_benchmark/submit_all_error_rate_benchmarks.sh

# 2. Wait for jobs to complete

# 3. Open the corresponding notebook
jupyter notebook notebooks/errorrate_benchmark_200K.ipynb
```

## Notes

- Notebooks contain hard-coded paths reflecting the original benchmark structure. If you change output directories, update the path definitions in the notebook's first cells.
- Some notebooks (e.g., `Fullset_benchmark_1M.ipynb`) require **both** 200K and 1M results to be present for comparison.
- Notebooks generate figures incrementally; re-run all cells to regenerate plots after updating results.

## Dependencies

Notebooks require:
- Python ≥3.8
- pandas
- matplotlib
- seaborn
- numpy

Install via:
```bash
pip install pandas matplotlib seaborn numpy jupyter
```

Or use the `envs/python_basic.yml` environment.
