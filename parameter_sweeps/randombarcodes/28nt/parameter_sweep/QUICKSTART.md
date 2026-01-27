# Parameter Sweep Quick Start Guide

## 🎯 Goal

Find the optimal values for `ntriage` and `nthresh` parameters in RandomBarcodes by testing:
- **ntriage**: 100, 1000, 2000, 5000, 10000 (5 values)
- **nthresh**: 5, 6, 7, 8, 9, 10 (6 values)
- **Total combinations**: 30

## 📋 Prerequisites

✅ Already done:
- [x] Generated 30 parameter files
- [x] Generated 30 PBS job scripts
- [x] Created submission script
- [x] Created analysis scripts

## 🚀 Usage

### Step 1: Review Generated Files (Optional)

```bash
# Check a sample parameter file
cat parameter_sweep/params/params_t1000_n7.json

# Check a sample job script
cat parameter_sweep/jobs/job_t1000_n7.sh

# Count total files
ls parameter_sweep/params/*.json | wc -l  # Should show 30
ls parameter_sweep/jobs/*.sh | wc -l     # Should show 30
```

### Step 2: Submit All Jobs

```bash
# Submit all 30 jobs at once
./parameter_sweep/submit_all.sh

# Output will show:
# Submitting 30 jobs...
# Submitting job_t100_n5.sh
# [job_id].node.cluster
# ...
```

**Expected behavior:**
- Jobs will be submitted with 1-second delay between each
- Each job requests: 2 CPUs, 1 GPU, 32GB RAM, 4 hours wall time
- Job names format: `RB_t{ntriage}_n{nthresh}` (e.g., `RB_t1000_n7`)

### Step 3: Monitor Jobs

```bash
# Check job status
qstat -u $USER

# Watch job status (updates every 30 seconds)
watch -n 30 'qstat -u $USER'

# Count running/queued jobs
qstat -u $USER | grep "RB_" | wc -l

# Check specific job
qstat -f [job_id]

# View live log output
tail -f parameter_sweep/logs/RB_t1000_n7.out
```

**Job states:**
- `Q` = Queued (waiting to run)
- `R` = Running
- `C` = Completed
- `E` = Error

### Step 4: Check Progress

```bash
# Count completed jobs
ls /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/randombarcodes_sweep/*/RB_*/precision_summary.csv 2>/dev/null | wc -l

# List completed jobs
ls /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/randombarcodes_sweep/

# Check for errors in logs
grep -l "ERROR" parameter_sweep/logs/*.err
```

### Step 5: Analyze Results (After All Jobs Complete)

```bash
# Collect and analyze all results
python parameter_sweep/analyze_results.py

# This will:
# - Scan all result directories
# - Extract precision/recall metrics
# - Save to: parameter_sweep/sweep_results.csv
# - Print summary table
# - Identify best parameters
```

**Expected output:**
```
================================================================================
PARAMETER SWEEP RESULTS
================================================================================
   ntriage  nthresh  precision    recall  f1_score  accuracy
       100        5     0.9234    0.8876    0.9052    0.9123
       100        6     0.9345    0.8967    0.9153    0.9234
       ...       ...        ...       ...       ...       ...

================================================================================
BEST PARAMETERS
================================================================================

Best Precision: 0.9567
  ntriage: 5000
  nthresh: 7

Best Recall: 0.9234
  ntriage: 2000
  nthresh: 6

Best F1 Score: 0.9387
  ntriage: 5000
  nthresh: 7
```

### Step 6: Visualize Results

```bash
# Generate plots and heatmaps
python parameter_sweep/visualize_results.py

# This creates:
# - Heatmaps for precision, recall, F1, accuracy
# - Line plots showing parameter effects
# - Scatter plots comparing metrics
# - Summary table of best parameters
```

**Generated plots:**
```
parameter_sweep/plots/
├── heatmap_precision.png      # Heatmap of precision values
├── heatmap_recall.png          # Heatmap of recall values
├── heatmap_f1.png              # Heatmap of F1 scores
├── heatmap_accuracy.png        # Heatmap of accuracy values
├── lines_precision.png         # Line plots for precision
├── lines_recall.png            # Line plots for recall
├── lines_f1.png                # Line plots for F1
├── scatter_plots.png           # Multi-panel comparison
└── best_parameters.txt         # Text summary
```

## 📊 Interpreting Results

### Heatmaps
- **Darker colors** = better performance
- Look for "hot spots" indicating optimal parameter combinations
- Check if patterns are consistent across metrics

### Line Plots
- **Left panel**: Effect of `ntriage` (different lines = different `nthresh`)
- **Right panel**: Effect of `nthresh` (different lines = different `ntriage`)
- Look for plateaus or peaks

### Best Parameters
- **High precision** = fewer false positives (conservative)
- **High recall** = fewer false negatives (sensitive)
- **High F1** = balanced performance (usually best choice)

## 🔧 Troubleshooting

### Job Failed with Error

```bash
# Check error log
cat parameter_sweep/logs/RB_t1000_n7.err

# Common issues:
# - Out of memory: Increase mem in generate_sweep.py
# - Timeout: Increase walltime in generate_sweep.py
# - Conda env issue: Check NXF_CONDA_CACHEDIR is set
```

### Re-run Failed Jobs

```bash
# Find failed jobs
for log in parameter_sweep/logs/*.err; do
    if grep -q "ERROR\|failed\|killed" "$log"; then
        echo "Failed: $(basename $log .err)"
    fi
done

# Resubmit specific job
qsub parameter_sweep/jobs/job_t1000_n7.sh
```

### Resume Interrupted Jobs

The pipeline uses `-resume` flag, so interrupted jobs will continue from where they stopped. Just resubmit the job script.

### No Results Found

```bash
# Check if jobs actually ran
ls parameter_sweep/logs/*.out

# Check if results were written
ls /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/randombarcodes_sweep/

# Check nextflow logs in work directories
```

## 📈 Expected Timeline

| Stage | Time | Notes |
|-------|------|-------|
| Submit jobs | 1 min | Submits all 30 jobs |
| Queue wait | Variable | Depends on cluster load |
| Per job runtime | 30 min - 2 hr | Depends on parameters |
| Total wall time | 4 hr | With buffer |
| Analysis | 1 min | After all jobs complete |
| Visualization | 1 min | After analysis |

**Parallel execution**: If cluster has capacity, multiple jobs will run simultaneously.

## 💡 Tips

1. **Start small**: Test with a few parameter combinations first before running all 30
2. **Monitor resources**: Check actual CPU/memory usage to optimize future runs
3. **Check early results**: Don't wait for all jobs - analyze partial results to spot trends
4. **Save results**: The CSV and plots are important for your paper/report
5. **Document**: Note the best parameters and why you chose them

## 📝 Next Steps After Optimization

Once you identify optimal parameters:

1. Update `test_params_randombarcodes.json` with best values:
   ```json
   {
     "ntriage": 5000,
     "nthresh": 7,
     ...
   }
   ```

2. Test on other datasets to validate:
   ```bash
   nextflow run main.nf \
       -profile hpc_conda \
       --tool randombarcodes \
       -params-file test_params_randombarcodes.json
   ```

3. Compare with QUIK and Columba:
   ```bash
   # Run all three tools with their optimal parameters
   nextflow run main.nf -profile hpc_conda --tool quik -params-file params_quik.json
   nextflow run main.nf -profile hpc_conda --tool randombarcodes -params-file params_rb.json
   nextflow run main.nf -profile hpc_conda --tool columba -params-file params_columba.json
   ```

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `generate_sweep.py` | Generate all parameter files and job scripts |
| `submit_all.sh` | Submit all jobs to PBS |
| `analyze_results.py` | Collect and analyze results |
| `visualize_results.py` | Create plots and visualizations |
| `params/*.json` | Parameter files (30 files) |
| `jobs/*.sh` | PBS job scripts (30 files) |
| `logs/*.{out,err}` | Job output and error logs |
| `sweep_results.csv` | Aggregated results table |
| `plots/` | Visualization outputs |

---

**Ready to start?** Run: `./parameter_sweep/submit_all.sh`

**Questions?** Check `parameter_sweep/README.md` for more details.


