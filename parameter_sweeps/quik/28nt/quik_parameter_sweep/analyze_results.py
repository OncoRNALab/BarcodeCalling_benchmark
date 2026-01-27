#!/usr/bin/env python3
"""
Analyze results from QUIK parameter sweep
Collects precision/recall metrics from all runs
"""

import pandas as pd
import json
from pathlib import Path
import re

# Configuration
RESULTS_BASE = "/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/results/quik_sweep"

def extract_metrics(result_dir):
    """Extract metrics from a single run"""
    summary_file = result_dir / "precision_summary.csv"
    
    if not summary_file.exists():
        return None
    
    df = pd.read_csv(summary_file)
    return df.iloc[0].to_dict()

def parse_run_name(dirname):
    """Extract strategy and rejection_threshold from directory name"""
    match = re.search(r'(\w+)_r(\d+)', dirname)
    if match:
        return match.group(1), int(match.group(2))
    return None, None

def main():
    results_path = Path(RESULTS_BASE)
    
    if not results_path.exists():
        print(f"Results directory not found: {{results_path}}")
        return
    
    all_results = []
    
    # Iterate through all result directories
    for run_dir in results_path.iterdir():
        if not run_dir.is_dir():
            continue
        
        strategy_short, rejection_threshold = parse_run_name(run_dir.name)
        if strategy_short is None:
            continue
        
        # Look for precision summary in subdirectory
        sample_dirs = list(run_dir.glob("QUIK_*"))
        if not sample_dirs:
            continue
        
        sample_dir = sample_dirs[0]
        metrics = extract_metrics(sample_dir)
        
        if metrics:
            metrics['strategy'] = strategy_short
            metrics['rejection_threshold'] = rejection_threshold
            all_results.append(metrics)
    
    if not all_results:
        print("No results found!")
        return
    
    # Create DataFrame
    df = pd.DataFrame(all_results)
    
    # Sort by strategy and rejection_threshold
    df = df.sort_values(['strategy', 'rejection_threshold'])
    
    # Save to CSV
    output_file = Path("./quik_parameter_sweep/sweep_results.csv")
    df.to_csv(output_file, index=False)
    print(f"Results saved to: {{output_file}}")
    
    # Print summary
    print("\n" + "="*80)
    print("QUIK PARAMETER SWEEP RESULTS")
    print("="*80)
    print(df.to_string(index=False))
    
    # Find best parameters for each strategy
    print("\n" + "="*80)
    print("BEST PARAMETERS BY STRATEGY")
    print("="*80)
    
    for strategy in df['strategy'].unique():
        strategy_df = df[df['strategy'] == strategy]
        print(f"\n=== Strategy: {{strategy}} ===")
        
        if 'precision' in df.columns:
            best_precision = strategy_df.loc[strategy_df['precision'].idxmax()]
            print(f"Best Precision: {{best_precision['precision']:.4f}} @ rejection_threshold={{int(best_precision['rejection_threshold'])}}")
        
        if 'recall' in df.columns:
            best_recall = strategy_df.loc[strategy_df['recall'].idxmax()]
            print(f"Best Recall: {{best_recall['recall']:.4f}} @ rejection_threshold={{int(best_recall['rejection_threshold'])}}")
        
        if 'f1_score' in df.columns:
            best_f1 = strategy_df.loc[strategy_df['f1_score'].idxmax()]
            print(f"Best F1 Score: {{best_f1['f1_score']:.4f}} @ rejection_threshold={{int(best_f1['rejection_threshold'])}}")
    
    # Overall best
    print("\n" + "="*80)
    print("OVERALL BEST PARAMETERS")
    print("="*80)
    
    if 'f1_score' in df.columns:
        best_overall = df.loc[df['f1_score'].idxmax()]
        print(f"\nBest F1 Score: {{best_overall['f1_score']:.4f}}")
        print(f"  Strategy: {{best_overall['strategy']}}")
        print(f"  Rejection Threshold: {{int(best_overall['rejection_threshold'])}}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
