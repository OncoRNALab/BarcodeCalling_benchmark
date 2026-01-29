# Fullset Benchmark 1M Reads Analysis Notebook

## Overview

This notebook (`Fullset_benchmark_1M.ipynb`) provides a comprehensive analysis of barcode calling tool performance on a 1 million read dataset.

## Experiments Analyzed

- **Dataset Size**: 1,000,000 reads (36nt barcodes, medium error rate)
- **Tools**: RandomBarcodes, QUIK, Columba
- **Barcode Sets**: 21K, 42K, 85K unique barcodes
- **Total Experiments**: 9 (3 tools × 3 barcode counts)

## Tool Parameters

| Tool | Parameters |
|------|------------|
| **RandomBarcodes** | nthresh=9, ntriage=100, GPUs=1 |
| **QUIK** | strategy=4_mer_gpu_v4, rejection_threshold=8, GPUs=1 |
| **Columba** | identity_threshold=80%, CPUs=16 |

## Notebook Structure

### 1. Data Loading (Cells 1-4)
- Import libraries and set visualization style
- Load precision/recall results from 1M reads experiments
- Extract metrics from precision_summary.csv files

### 2. Runtime Analysis (Cells 5-7)
- Parse Nextflow trace files for runtime and memory usage
- Extract duration, CPU usage, memory consumption
- Display resource usage summary

### 3. 200K Data Loading (Cells 8-9)
- Load 200K reads results matching the same parameters
- Filter for comparable experiments
- Prepare for scaling analysis

### 4. Performance Tables (Cells 10-12)
- Summary statistics by tool
- Best F1 scores for each tool
- Pivot tables for precision, recall, F1 by tool and barcode count

### 5. Precision vs Recall Plots (Cells 13-16)
- Individual plots for each tool
- Combined plot with all tools
- Color-coded by tool, different markers for barcode sizes
- F1 score isolines for reference

### 6. Scaling Analysis (Cells 17-20)
- Compare 200K vs 1M performance
- Calculate precision/recall changes
- Visualize scaling behavior
- Identify tools that scale well

### 7. Runtime Comparison (Cells 21-22)
- Runtime by tool and barcode count
- Parse and visualize execution times
- Compare computational efficiency

### 8. Conclusions (Cell 23)
- Key findings summary
- Tool-specific observations
- Scaling insights
- Recommendations by use case

## Key Analyses

### Performance Metrics
- **Precision**: Correctness of barcode assignments
- **Recall**: Fraction of reads successfully assigned
- **F1 Score**: Harmonic mean of precision and recall
- **Assignment Rate**: Percentage of reads assigned a barcode

### Visualizations
1. **Precision vs Recall Scatter Plots**: Individual and combined views
2. **Scaling Comparison**: 200K vs 1M performance overlay
3. **Runtime Bar Charts**: Execution time by tool and barcode count
4. **F1 Score Isolines**: Reference lines for performance evaluation

### Comparisons
- **Tool Comparison**: RandomBarcodes vs QUIK vs Columba
- **Scaling Behavior**: How performance changes from 200K to 1M reads
- **Barcode Set Size Impact**: 21K vs 42K vs 85K barcodes
- **Runtime Efficiency**: Speed vs accuracy trade-offs

## Output Files

All figures are saved to: `notebooks/figures/`

- `1M_precision_recall.pdf` - Per-tool precision vs recall
- `1M_precision_recall_combined.pdf` - All tools combined
- `scaling_200K_vs_1M.pdf` - Scaling analysis plots
- `1M_runtime_comparison.pdf` - Runtime comparison bar chart

## Usage

### Prerequisites
```python
pip install pandas numpy matplotlib seaborn
```

### Running the Notebook

1. **Open in Jupyter**:
   ```bash
   cd /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/notebooks
   jupyter notebook Fullset_benchmark_1M.ipynb
   ```

2. **Run All Cells**:
   - Kernel → Restart & Run All

3. **View Results**:
   - Tables display inline
   - Plots display and save to PDF
   - Runtime: ~1-2 minutes

### Cell-by-Cell Execution

For interactive analysis:
1. Run cells sequentially from top to bottom
2. Examine intermediate results
3. Modify parameters as needed
4. Re-run specific analyses

## Key Findings

### Tool Performance Summary

**RandomBarcodes:**
- ✓ Highest precision (>99.9%)
- ⚠ Moderate recall
- ⚡ Fast with GPU

**QUIK:**
- ✓ Best F1 scores
- ✓ Excellent balance
- ✓ Highest assignment rates
- ⚡ Moderate runtime

**Columba:**
- ✓ CPU-based (no GPU needed)
- ⚠ Lower assignment rates
- ⏱ Longer runtime

### Scaling Insights

- Performance generally maintained from 200K → 1M
- Runtime scales approximately linearly
- QUIK shows most consistent scaling
- Memory usage remains manageable

### Recommendations

| Use Case | Recommended Tool | Rationale |
|----------|------------------|-----------|
| Maximum throughput | QUIK | Best F1, high recall |
| Maximum precision | RandomBarcodes | >99.9% precision |
| CPU-only | Columba | No GPU requirement |
| Large barcode sets | QUIK | Scales well |
| Diagnostic applications | RandomBarcodes | Minimize false positives |

## Data Sources

### Input Data
- **1M Results**: `/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_1million_reads/`
- **200K Results**: `/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_sweep/results_36nt/summaries/all_corrected_metrics.csv`
- **Runtime Data**: `/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_1million_reads/`

### File Structure
```
results_1million_reads/
├── randombarcodes_21K/
│   └── randombarcodes_21K_1M/
│       ├── *_precision_summary.csv
│       └── *_stats_summary.csv
├── quik_21K/
│   └── quik_21K_1M/
│       ├── *_precision_summary.csv
│       └── *_stats_summary.csv
└── columba_21K/
    └── columba_21K_1M/
        └── *_barcode_calling_stats.txt
```

## Troubleshooting

### Missing Data
- Check that all 9 experiments completed successfully
- Verify precision_summary.csv files exist
- Confirm trace files are present in work directories

### Plot Issues
- Ensure figures directory exists
- Check matplotlib backend
- Verify sufficient disk space

### Performance
- Notebook runs in ~1-2 minutes on standard hardware
- Large figures may take longer to render
- Consider reducing plot complexity for faster execution

## Related Notebooks

- `parameter_sweep_36nt_analysis.ipynb` - 200K reads parameter sweep
- `errorrate_benchmark_200K.ipynb` - Error rate analysis (200K reads)

## Citation

If using these results, please document:
- Tool versions used
- Parameter settings
- Dataset characteristics
- Analysis date

## Contact

For questions or issues, refer to the main BarCall_benchmark documentation.

---

**Created**: 2026-01-22  
**Dataset**: 1M reads, 36nt barcodes, medium error rate  
**Total Cells**: 24  
**Status**: ✅ Complete and ready to run
