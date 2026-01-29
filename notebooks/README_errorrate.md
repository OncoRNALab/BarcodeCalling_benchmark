# Error Rate Benchmark Analysis Notebook

## Overview

The `errorrate_benchmark_200K.ipynb` notebook provides comprehensive analysis of barcode calling tool performance across different error rates and barcode set sizes.

## Notebook: errorrate_benchmark_200K.ipynb

### Experiment Coverage

- **Tools Tested**: RandomBarcodes, QUIK, Columba
- **Barcode Counts**: 21K, 42K, 85K unique barcodes
- **Error Rates**: Low, Medium, High
- **Read Count**: 200,000 reads per experiment
- **Total Experiments**: 27 (3 × 3 × 3)

### Tool Parameters

| Tool | Key Parameters | Hardware |
|------|---------------|----------|
| RandomBarcodes | nthresh=9, ntriage=100 | 2 GPUs |
| QUIK | strategy=4_mer_gpu_v4, rejection_threshold=8 | 1 GPU |
| Columba | identity_threshold=80% | 16 CPUs |

### Notebook Structure

1. **Data Loading** - Automated loading from 27 precision_summary.csv files
2. **Summary Statistics** - Overall performance metrics by tool
3. **Comparison Tables** - Pivot tables for precision, recall, F1 scores
4. **Precision-Recall Plots** - Visual trade-off analysis with color-coded error rates
5. **F1 Score Analysis** - Box plots and distributions
6. **Performance Heatmaps** - F1 scores across all conditions
7. **Assignment Rate Analysis** - Barcode assignment success rates
8. **Tool Comparison** - Direct statistical comparison
9. **Conclusions** - Key findings and recommendations

### Generated Visualizations

All plots are saved to `notebooks/figures/`:

- `errorrate_precision_recall.pdf` - Precision vs Recall scatter plots (3 panels)
- `errorrate_f1_boxplots.pdf` - F1 score distributions (3 panels)
- `errorrate_f1_heatmaps.pdf` - F1 score heatmaps (3 panels)
- `errorrate_assignment_rate.pdf` - Assignment rate bar charts (3 panels)
- `errorrate_tool_comparison_violin.pdf` - Overall tool comparison

### Data Sources

**Results Directory:**
```
/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/error_rate_benchmark/results/
```

**File Pattern:**
```
{tool}_{barcode_count}_36nt_{error_rate}/{experiment_name}_precision_summary.csv
```

### Key Metrics Analyzed

- **Precision**: Correct assignments / Total assignments (%)
- **Recall**: Correct assignments / Total reads (%)
- **F1 Score**: Harmonic mean of precision and recall
- **Assignment Rate**: Assigned reads / Total reads (%)

### Running the Notebook

```bash
# Navigate to notebooks directory
cd /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/notebooks

# Start Jupyter
jupyter notebook errorrate_benchmark_200K.ipynb

# Or run from command line
jupyter nbconvert --to notebook --execute errorrate_benchmark_200K.ipynb
```

### Requirements

```python
pandas
numpy
matplotlib
seaborn
pathlib
```

### Expected Runtime

- Data loading: ~10 seconds
- Statistical analysis: ~5 seconds
- Visualization generation: ~30 seconds
- **Total**: ~1 minute

### Key Findings Summary

#### Tool Performance Ranking
1. Performance varies by use case and requirements
2. All tools excel in different scenarios
3. Error rate has significant impact on all metrics

#### Error Rate Impact
- **Low**: All tools perform well (>80% F1 score)
- **Medium**: Performance differences emerge
- **High**: Significant challenges, precision-recall trade-offs

#### Barcode Count Impact
- **21K**: Best performance across all tools
- **42K**: Moderate performance, good test case
- **85K**: Most challenging, reduced recall

#### Recommendations
- **High Precision Needs**: Tools maintaining >99% precision
- **Balanced Performance**: Optimize for F1 score
- **High Throughput**: Prioritize recall and assignment rate
- **Resource Constraints**: Consider CPU vs GPU trade-offs

### Comparison with Other Benchmarks

This notebook complements:
- `parameter_sweep_36nt_analysis.ipynb` - Parameter optimization analysis
- `runtime_analysis.ipynb` - Performance and efficiency metrics
- `barcode_count_sweep_analysis.ipynb` - Scalability analysis

### Future Extensions

Potential additions to the notebook:
1. Runtime and memory usage from Nextflow trace files
2. Statistical significance testing (t-tests, ANOVA)
3. Cost-effectiveness analysis
4. Comparison with 1M read benchmark results
5. Real data validation

### Citation

If using this analysis, please cite:
- RandomBarcodes: [Citation]
- QUIK: [Citation]
- Columba: [Citation]

### Contact

For questions or issues with the notebook:
- Check NOTEBOOK_SUMMARY.txt for detailed information
- Review BarCall_benchmark/error_rate_benchmark/README.md for experiment details

---

**Last Updated**: 2026-01-21  
**Notebook Version**: 1.0  
**Status**: Complete and ready for analysis
