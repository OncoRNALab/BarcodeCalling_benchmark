#!/usr/bin/env python3
"""
Visualize RandomBarcodes parameter sweep results
Creates heatmaps and plots to help identify optimal parameters
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Configuration
RESULTS_CSV = "./parameter_sweep/sweep_results.csv"
OUTPUT_DIR = Path("./parameter_sweep/plots")

def load_results():
    """Load results from CSV"""
    if not Path(RESULTS_CSV).exists():
        print(f"Error: Results file not found: {RESULTS_CSV}")
        print("Run 'python parameter_sweep/analyze_results.py' first!")
        return None
    
    df = pd.read_csv(RESULTS_CSV)
    return df

def create_heatmap(df, metric, title, filename):
    """Create a heatmap for a specific metric"""
    # Pivot data for heatmap
    pivot = df.pivot(index='nthresh', columns='ntriage', values=metric)
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Create heatmap
    sns.heatmap(
        pivot, 
        annot=True, 
        fmt='.4f', 
        cmap='YlOrRd',
        cbar_kws={'label': metric.replace('_', ' ').title()},
        linewidths=0.5,
        linecolor='gray'
    )
    
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel('ntriage (Triage Size)', fontsize=12)
    plt.ylabel('nthresh (Distance Threshold)', fontsize=12)
    plt.tight_layout()
    
    # Save figure
    plt.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Created: {filename}")

def create_line_plots(df, metric, title, filename):
    """Create line plots showing parameter effects"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Effect of ntriage (separate lines for each nthresh)
    for nthresh in sorted(df['nthresh'].unique()):
        subset = df[df['nthresh'] == nthresh]
        ax1.plot(subset['ntriage'], subset[metric], 
                marker='o', label=f'nthresh={int(nthresh)}', linewidth=2)
    
    ax1.set_xlabel('ntriage (Triage Size)', fontsize=12)
    ax1.set_ylabel(metric.replace('_', ' ').title(), fontsize=12)
    ax1.set_title(f'{title}\n(Effect of ntriage)', fontsize=14, fontweight='bold')
    ax1.legend(title='nthresh', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    
    # Plot 2: Effect of nthresh (separate lines for each ntriage)
    for ntriage in sorted(df['ntriage'].unique()):
        subset = df[df['ntriage'] == ntriage]
        ax2.plot(subset['nthresh'], subset[metric], 
                marker='s', label=f'ntriage={int(ntriage)}', linewidth=2)
    
    ax2.set_xlabel('nthresh (Distance Threshold)', fontsize=12)
    ax2.set_ylabel(metric.replace('_', ' ').title(), fontsize=12)
    ax2.set_title(f'{title}\n(Effect of nthresh)', fontsize=14, fontweight='bold')
    ax2.legend(title='ntriage', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Created: {filename}")

def create_scatter_plots(df):
    """Create scatter plots comparing metrics"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Precision vs Recall
    ax = axes[0, 0]
    scatter = ax.scatter(df['recall'], df['precision'], 
                        c=df['f1_score'], s=100, cmap='viridis',
                        edgecolors='black', linewidth=1)
    ax.set_xlabel('Recall', fontsize=12)
    ax.set_ylabel('Precision', fontsize=12)
    ax.set_title('Precision vs Recall\n(colored by F1 Score)', fontsize=12, fontweight='bold')
    plt.colorbar(scatter, ax=ax, label='F1 Score')
    ax.grid(True, alpha=0.3)
    
    # Add annotations for best points
    if 'f1_score' in df.columns:
        best_idx = df['f1_score'].idxmax()
        best = df.loc[best_idx]
        ax.annotate(f"Best F1\n(t={int(best['ntriage'])}, n={int(best['nthresh'])})",
                   xy=(best['recall'], best['precision']),
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    # F1 Score by ntriage
    ax = axes[0, 1]
    for nthresh in sorted(df['nthresh'].unique()):
        subset = df[df['nthresh'] == nthresh]
        ax.plot(subset['ntriage'], subset['f1_score'], 
               marker='o', label=f'nthresh={int(nthresh)}', linewidth=2)
    ax.set_xlabel('ntriage', fontsize=12)
    ax.set_ylabel('F1 Score', fontsize=12)
    ax.set_title('F1 Score by ntriage', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    
    # F1 Score by nthresh
    ax = axes[1, 0]
    for ntriage in sorted(df['ntriage'].unique()):
        subset = df[df['ntriage'] == ntriage]
        ax.plot(subset['nthresh'], subset['f1_score'], 
               marker='s', label=f'ntriage={int(ntriage)}', linewidth=2)
    ax.set_xlabel('nthresh', fontsize=12)
    ax.set_ylabel('F1 Score', fontsize=12)
    ax.set_title('F1 Score by nthresh', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Accuracy heatmap
    ax = axes[1, 1]
    pivot = df.pivot(index='nthresh', columns='ntriage', values='accuracy')
    sns.heatmap(pivot, annot=True, fmt='.4f', cmap='RdYlGn', 
               cbar_kws={'label': 'Accuracy'}, ax=ax, linewidths=0.5)
    ax.set_title('Accuracy Heatmap', fontsize=12, fontweight='bold')
    ax.set_xlabel('ntriage', fontsize=12)
    ax.set_ylabel('nthresh', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'scatter_plots.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Created: scatter_plots.png")

def create_summary_table(df):
    """Create a summary table with best parameters"""
    summary_file = OUTPUT_DIR / 'best_parameters.txt'
    
    with open(summary_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("BEST PARAMETERS FOR RANDOMBARCODES\n")
        f.write("=" * 80 + "\n\n")
        
        # Best for each metric
        metrics = ['precision', 'recall', 'f1_score', 'accuracy']
        
        for metric in metrics:
            if metric in df.columns:
                best_idx = df[metric].idxmax()
                best = df.loc[best_idx]
                
                f.write(f"\nBest {metric.replace('_', ' ').title()}:\n")
                f.write(f"  Value: {best[metric]:.4f}\n")
                f.write(f"  ntriage: {int(best['ntriage'])}\n")
                f.write(f"  nthresh: {int(best['nthresh'])}\n")
                f.write(f"  Precision: {best['precision']:.4f}\n")
                f.write(f"  Recall: {best['recall']:.4f}\n")
                f.write(f"  F1 Score: {best['f1_score']:.4f}\n")
                f.write(f"  Accuracy: {best['accuracy']:.4f}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("PARAMETER SENSITIVITY ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        
        # Calculate parameter sensitivity
        f.write("Effect of ntriage (averaged across nthresh values):\n")
        ntriage_effect = df.groupby('ntriage')[['precision', 'recall', 'f1_score']].mean()
        f.write(ntriage_effect.to_string() + "\n\n")
        
        f.write("Effect of nthresh (averaged across ntriage values):\n")
        nthresh_effect = df.groupby('nthresh')[['precision', 'recall', 'f1_score']].mean()
        f.write(nthresh_effect.to_string() + "\n\n")
    
    print(f"✓ Created: best_parameters.txt")
    
    # Also print to console
    with open(summary_file, 'r') as f:
        print("\n" + f.read())

def main():
    print("RandomBarcodes Parameter Sweep Visualization")
    print("=" * 60)
    
    # Load results
    df = load_results()
    if df is None:
        return
    
    print(f"✓ Loaded {len(df)} results")
    print(f"  ntriage values: {sorted(df['ntriage'].unique())}")
    print(f"  nthresh values: {sorted(df['nthresh'].unique())}")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created output directory: {OUTPUT_DIR}")
    
    # Create visualizations
    print("\nGenerating visualizations...")
    
    # Heatmaps
    if 'precision' in df.columns:
        create_heatmap(df, 'precision', 'Precision Heatmap', 'heatmap_precision.png')
    
    if 'recall' in df.columns:
        create_heatmap(df, 'recall', 'Recall Heatmap', 'heatmap_recall.png')
    
    if 'f1_score' in df.columns:
        create_heatmap(df, 'f1_score', 'F1 Score Heatmap', 'heatmap_f1.png')
    
    if 'accuracy' in df.columns:
        create_heatmap(df, 'accuracy', 'Accuracy Heatmap', 'heatmap_accuracy.png')
    
    # Line plots
    if 'precision' in df.columns:
        create_line_plots(df, 'precision', 'Precision', 'lines_precision.png')
    
    if 'recall' in df.columns:
        create_line_plots(df, 'recall', 'Recall', 'lines_recall.png')
    
    if 'f1_score' in df.columns:
        create_line_plots(df, 'f1_score', 'F1 Score', 'lines_f1.png')
    
    # Scatter plots
    if all(col in df.columns for col in ['precision', 'recall', 'f1_score']):
        create_scatter_plots(df)
    
    # Summary table
    create_summary_table(df)
    
    print("\n" + "=" * 60)
    print("Visualization complete!")
    print("=" * 60)
    print(f"\nPlots saved in: {OUTPUT_DIR}")
    print("\nGenerated files:")
    for f in sorted(OUTPUT_DIR.iterdir()):
        print(f"  - {f.name}")

if __name__ == "__main__":
    main()


