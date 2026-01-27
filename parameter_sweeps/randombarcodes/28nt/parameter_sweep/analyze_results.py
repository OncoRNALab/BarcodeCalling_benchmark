#!/usr/bin/env python3
"""
Analyze results from RandomBarcodes parameter sweep
Collects precision/recall metrics from all runs
"""

import pandas as pd
import json
from pathlib import Path
import re

# Configuration
RESULTS_BASE = "/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/randombarcodes_sweep"

def extract_metrics(result_dir):
    """Extract metrics from a single run"""
    summary_file = result_dir / "precision_summary.csv"
    
    if not summary_file.exists():
        return None
    
    df = pd.read_csv(summary_file)
    return df.iloc[0].to_dict()

def parse_run_name(dirname):
    """Extract ntriage and nthresh from directory name"""
    match = re.search(r't(\d+)_n(\d+)', dirname)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def main():
    results_path = Path(RESULTS_BASE)
    
    if not results_path.exists():
        print(f"Results directory not found: {results_path}")
        return
    
    all_results = []
    
    # Iterate through all result directories
    for run_dir in results_path.iterdir():
        if not run_dir.is_dir():
            continue
        
        ntriage, nthresh = parse_run_name(run_dir.name)
        if ntriage is None:
            continue
        
        # Look for precision summary in subdirectory
        sample_dirs = list(run_dir.glob("RB_t*_n*"))
        if not sample_dirs:
            continue
        
        sample_dir = sample_dirs[0]
        metrics = extract_metrics(sample_dir)
        
        if metrics:
            metrics['ntriage'] = ntriage
            metrics['nthresh'] = nthresh
            all_results.append(metrics)
    
    if not all_results:
        print("No results found!")
        return
    
    # Create DataFrame
    df = pd.DataFrame(all_results)
    
    # Sort by ntriage and nthresh
    df = df.sort_values(['ntriage', 'nthresh'])
    
    # Save to CSV
    output_file = Path("./parameter_sweep/sweep_results.csv")
    df.to_csv(output_file, index=False)
    print(f"Results saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("PARAMETER SWEEP RESULTS")
    print("="*80)
    print(df.to_string(index=False))
    
    # Find best parameters
    print("\n" + "="*80)
    print("BEST PARAMETERS")
    print("="*80)
    
    if 'precision' in df.columns:
        best_precision = df.loc[df['precision'].idxmax()]
        print(f"\nBest Precision: {best_precision['precision']:.4f}")
        print(f"  ntriage: {int(best_precision['ntriage'])}")
        print(f"  nthresh: {int(best_precision['nthresh'])}")
    
    if 'recall' in df.columns:
        best_recall = df.loc[df['recall'].idxmax()]
        print(f"\nBest Recall: {best_recall['recall']:.4f}")
        print(f"  ntriage: {int(best_recall['ntriage'])}")
        print(f"  nthresh: {int(best_recall['nthresh'])}")
    
    if 'f1_score' in df.columns:
        best_f1 = df.loc[df['f1_score'].idxmax()]
        print(f"\nBest F1 Score: {best_f1['f1_score']:.4f}")
        print(f"  ntriage: {int(best_f1['ntriage'])}")
        print(f"  nthresh: {int(best_f1['nthresh'])}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
