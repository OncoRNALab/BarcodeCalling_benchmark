# Notebook Update Guide: New Results Directory Structure

## Overview

The project has been updated with generator scripts that create standardized job submissions and parameter files. All results are now stored in:

```
results/parameter_sweeps/
├── results_28nt/
│   ├── randombarcodes_sweep/
│   ├── quik_sweep/
│   └── columba_sweep/
├── results_30nt/
│   ├── randombarcodes_sweep/
│   ├── quik_sweep/
│   └── columba_sweep/
├── results_32nt/
├── results_34nt/
└── results_36nt/
```

## Required Notebook Updates

### 1. `precision_recall_curves_28_36nt.ipynb`

**Current Issue**: Uses hardcoded paths to old `results_sweep` directory with precomputed summary files.

**Old Code (Cell 3)**:
```python
# Define file paths
file_28nt = Path("/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_sweep/results_28nt/new_summaries/summary_all_metrics.csv")
file_36nt = Path("/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_sweep/results_36nt/new_summaries/summary_all_metrics.csv")

# Load data
if file_28nt.exists():
    df_28nt = pd.read_csv(file_28nt)
    df_28nt['barcode_length'] = 28
    print(f"✓ Loaded 28nt data: {len(df_28nt)} samples")
    print(f"  Tools: {df_28nt['tool'].unique().tolist()}")
```

**New Code**:
```python
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Define base directory (relative to notebook location or absolute)
BASE_DIR = Path("../results/parameter_sweeps")  # Relative from notebooks/
# Or use absolute: BASE_DIR = Path("/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/results/parameter_sweeps")

def load_precision_reports_for_length(base_dir, barcode_length):
    """
    Scan all tool sweep directories and load precision_report.txt files.
    Returns a combined DataFrame with all results for this barcode length.
    """
    results_dir = base_dir / f"results_{barcode_length}nt"
    
    all_data = []
    
    # Scan for precision reports in all sweep subdirectories
    for sweep_type in ['randombarcodes_sweep', 'quik_sweep', 'columba_sweep']:
        sweep_dir = results_dir / sweep_type
        if not sweep_dir.exists():
            continue
        
        # Find all precision_report.txt files
        for report_file in sweep_dir.rglob('precision_report.txt'):
            try:
                # Parse precision report
                with open(report_file, 'r') as f:
                    lines = f.readlines()
                
                # Extract metrics (adjust parsing based on actual format)
                metrics = {}
                for line in lines:
                    if 'Precision:' in line:
                        metrics['precision'] = float(line.split(':')[1].strip().replace('%', '')) / 100
                    elif 'Recall:' in line:
                        metrics['recall'] = float(line.split(':')[1].strip().replace('%', '')) / 100
                    elif 'F1 Score:' in line:
                        metrics['f1_score'] = float(line.split(':')[1].strip().replace('%', '')) / 100
                
                # Extract parameters from parent directory name
                param_dir = report_file.parent.name
                
                # Add tool info
                if 'randombarcodes' in str(sweep_dir):
                    metrics['tool'] = 'RandomBarcodes'
                    # Parse t100_n9 format
                    if '_t' in param_dir and '_n' in param_dir:
                        metrics['ntriage'] = int(param_dir.split('_t')[1].split('_')[0])
                        metrics['nthresh'] = int(param_dir.split('_n')[1])
                elif 'quik' in str(sweep_dir):
                    metrics['tool'] = 'QUIK'
                    # Parse 4mer_r8 format
                    if 'mer_r' in param_dir:
                        metrics['strategy'] = param_dir.split('_r')[0] + '_mer'
                        metrics['rejection_threshold'] = int(param_dir.split('_r')[1])
                elif 'columba' in str(sweep_dir):
                    metrics['tool'] = 'Columba'
                    # Parse I80 format
                    if param_dir.startswith('I'):
                        metrics['identity_threshold'] = int(param_dir[1:])
                
                metrics['barcode_length'] = barcode_length
                all_data.append(metrics)
            
            except Exception as e:
                print(f"Warning: Could not parse {report_file}: {e}")
                continue
    
    return pd.DataFrame(all_data) if all_data else pd.DataFrame()

# Load data for both barcode lengths
print(f"Loading data from: {BASE_DIR}")

df_28nt = load_precision_reports_for_length(BASE_DIR, 28)
if not df_28nt.empty:
    print(f"✓ Loaded 28nt data: {len(df_28nt)} samples")
    print(f"  Tools: {df_28nt['tool'].unique().tolist()}")
else:
    print(f"✗ No 28nt data found")

df_36nt = load_precision_reports_for_length(BASE_DIR, 36)
if not df_36nt.empty:
    print(f"✓ Loaded 36nt data: {len(df_36nt)} samples")
    print(f"  Tools: {df_36nt['tool'].unique().tolist()}")
else:
    print(f"✗ No 36nt data found")

# Combine datasets
df = pd.concat([df_28nt, df_36nt], ignore_index=True)
print(f"\n✓ Combined dataset: {len(df)} samples")
```

---

### 2. `parameter_sweep_analysis_30_32_34nt.ipynb`

**Current Issue**: Uses hardcoded paths to old `results_sweep` directory.

**Old Code (Cell 2)**:
```python
# Base directory
BASE_DIR = "/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results_sweep"

# Result directories for each barcode length
RESULT_DIRS = {
    30: f"{BASE_DIR}/results_30nt",
    32: f"{BASE_DIR}/results_32nt",
    34: f"{BASE_DIR}/results_34nt"
}
```

**New Code**:
```python
from pathlib import Path

# Base directory - use relative path from notebooks/ or absolute path
BASE_DIR = Path("../results/parameter_sweeps")  # Relative from notebooks/
# Or use absolute:
# BASE_DIR = Path("/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/results/parameter_sweeps")

# Ensure BASE_DIR is absolute for consistency
if not BASE_DIR.is_absolute():
    BASE_DIR = (Path.cwd().parent / BASE_DIR).resolve()

# Result directories for each barcode length
RESULT_DIRS = {
    30: BASE_DIR / "results_30nt",
    32: BASE_DIR / "results_32nt",
    34: BASE_DIR / "results_34nt"
}

# Tool configurations (unchanged)
TOOLS = {
    'randombarcodes': {
        'name': 'RandomBarcodes',
        'sweep_dir': 'randombarcodes_sweep',
        'thresholds': [5, 6, 7, 8, 9],
        'threshold_param': 'nthresh'
    },
    'quik': {
        'name': 'QUIK',
        'sweep_dir': 'quik_sweep',
        'thresholds': [5, 6, 7, 8, 9],
        'threshold_param': 'rejection_threshold'
    },
    'columba': {
        'name': 'Columba',
        'sweep_dir': 'columba_sweep',
        'thresholds': [77, 78, 80, 82, 84],
        'threshold_param': 'identity_threshold'
    }
}

BARCODE_LENGTHS = [30, 32, 34]

print(f"Base directory: {BASE_DIR}")
print(f"Barcode lengths: {BARCODE_LENGTHS}")
print(f"Tools: {', '.join([TOOLS[t]['name'] for t in TOOLS])}")
```

**Also Update Output Paths (Later cells)**:

The notebook saves outputs to `BASE_DIR`. Update those lines to save to a better location:

```python
# Export complete results to CSV
OUTPUT_DIR = Path("../notebooks/tables")  # Save to notebooks/tables/
OUTPUT_DIR.mkdir(exist_ok=True)

output_csv = OUTPUT_DIR / 'parameter_sweep_results_30_32_34nt.csv'
df.to_csv(output_csv, index=False)
print(f"Complete results exported to: {output_csv}")

# Export best results
best_output_csv = OUTPUT_DIR / 'best_parameters_30_32_34nt.csv'
best_df.to_csv(best_output_csv, index=False)
print(f"Best parameters exported to: {best_output_csv}")

# Create summary report
summary_file = OUTPUT_DIR / 'parameter_sweep_summary_30_32_34nt.txt'
with open(summary_file, 'w') as f:
    # ... (rest of summary code)
    
print(f"\nSummary report saved to: {summary_file}")
```

**Update Figure Save Paths**:

Find all lines with `plt.savefig(f'{BASE_DIR}/...` and update to:

```python
FIGURES_DIR = Path("../notebooks/figures")
FIGURES_DIR.mkdir(exist_ok=True)

plt.savefig(FIGURES_DIR / 'precision_recall_vs_threshold_by_length.pdf', dpi=300, bbox_inches='tight')
plt.savefig(FIGURES_DIR / 'precision_recall_curves_by_tool.pdf', dpi=300, bbox_inches='tight')
plt.savefig(FIGURES_DIR / 'performance_heatmaps.pdf', dpi=300, bbox_inches='tight')
# etc.
```

---

## Summary of Changes

### Key Updates:

1. **Relative Paths**: Use `../results/parameter_sweeps` relative to `notebooks/` directory
2. **Path Objects**: Use `pathlib.Path` for better cross-platform compatibility
3. **Dynamic Loading**: Scan directory structure instead of expecting precomputed files
4. **Output Organization**: Save figures to `notebooks/figures/`, tables to `notebooks/tables/`

### Benefits:

- ✅ Works with new generator script output structure
- ✅ Portable across different systems
- ✅ No hardcoded absolute paths
- ✅ Automatically discovers all result files
- ✅ Better organized outputs

## Testing

After making these changes, test by:

1. Generate parameter sweep results:
   ```bash
   cd /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark
   python3 bin/generate_jobs_and_params_parameter_sweep.py \
       --data-dir data/benchmark_85K_42K_21K_200K \
       --results-dir results/parameter_sweeps
   ```

2. Run some jobs to generate results

3. Open notebooks and verify they load data correctly

## Notes

- The `find_precision_reports` function in `parameter_sweep_analysis_30_32_34nt.ipynb` already scans directories, so it should work with minimal changes
- Columba identity thresholds may differ slightly - verify the actual values used in your sweeps
- Adjust the precision report parsing logic if the output format has changed
