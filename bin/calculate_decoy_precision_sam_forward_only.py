#!/usr/bin/env python3
"""
Estimate precision from a *decoy-only* Columba SAM output (forward-mapped only).

Context (real data / unknown ground truth):
  When aligning reads against a decoy barcode reference (barcodes not present in
  the experiment), any mapped read is a false positive. The decoy hit rate is
  used to estimate a lower bound on precision.

This script computes:
  - total_reads: number of SAM records (non-header lines)
  - decoy_mapped_forward: mapped AND forward (FLAG !&4 and !&16) AND RNAME matches barcode_<idx>
  - decoy_mapped_reverse: mapped AND reverse (FLAG &16) AND RNAME matches barcode_<idx>
  - unmapped: FLAG &4

Then:
  decoy_fp_rate_forward_percent = 100 * decoy_mapped_forward / total_reads
  estimated_precision_percent    = 100 - decoy_fp_rate_forward_percent

Outputs:
  - a human-readable report
  - a 2-column CSV (metric,value)
"""

import argparse
import csv
import re


FLAG_UNMAPPED = 0x4
FLAG_REVERSE = 0x10


def compute_decoy_fp_rate(sam_file: str):
    total = 0
    unmapped = 0
    mapped_forward = 0
    mapped_reverse = 0
    invalid_rname = 0

    rname_re = re.compile(r"^barcode_(\d+)$")

    with open(sam_file, "r") as f:
        for line in f:
            if line.startswith("@"):
                continue

            total += 1
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 6:
                # malformed record; ignore from mapped/unmapped counts but still part of total
                continue

            try:
                flag = int(fields[1])
            except ValueError:
                continue

            if flag & FLAG_UNMAPPED:
                unmapped += 1
                continue

            rname = fields[2]
            if not rname_re.match(rname):
                invalid_rname += 1
                continue

            if flag & FLAG_REVERSE:
                mapped_reverse += 1
            else:
                mapped_forward += 1

    fp_rate_fwd = (mapped_forward / total * 100.0) if total else 0.0
    fp_rate_all = ((mapped_forward + mapped_reverse) / total * 100.0) if total else 0.0
    est_prec_fwd = 100.0 - fp_rate_fwd
    est_prec_all = 100.0 - fp_rate_all

    return {
        "total_reads": total,
        "unmapped_reads": unmapped,
        "decoy_mapped_forward": mapped_forward,
        "decoy_mapped_reverse": mapped_reverse,
        "invalid_rname_mapped": invalid_rname,
        "decoy_fp_rate_forward_percent": fp_rate_fwd,
        "decoy_fp_rate_all_mapped_percent": fp_rate_all,
        "estimated_precision_forward_only_percent": est_prec_fwd,
        "estimated_precision_all_mapped_percent": est_prec_all,
    }


def write_report(metrics: dict, report_file: str, sample_id=None):
    with open(report_file, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("DECOY-BASED PRECISION ESTIMATE (Columba SAM; forward-mapped only)\n")
        f.write("=" * 80 + "\n\n")
        if sample_id:
            f.write(f"Sample ID: {sample_id}\n\n")

        f.write("=== COUNTS ===\n")
        f.write(f"Total reads: {metrics['total_reads']}\n")
        f.write(f"Unmapped reads (FLAG 4): {metrics['unmapped_reads']}\n")
        f.write(f"Decoy-mapped forward (FLAG !16): {metrics['decoy_mapped_forward']}\n")
        f.write(f"Decoy-mapped reverse (FLAG 16): {metrics['decoy_mapped_reverse']}\n")
        if metrics.get("invalid_rname_mapped", 0):
            f.write(f"Mapped with invalid RNAME: {metrics['invalid_rname_mapped']}\n")

        f.write("\n=== DECOY HIT RATES ===\n")
        f.write(
            f"Decoy false-positive rate (forward-only): {metrics['decoy_fp_rate_forward_percent']:.4f}%\n"
        )
        f.write(
            f"Estimated precision (forward-only): {metrics['estimated_precision_forward_only_percent']:.4f}%\n"
        )

        f.write("\n(For reference)\n")
        f.write(
            f"Decoy false-positive rate (all mapped incl. reverse): {metrics['decoy_fp_rate_all_mapped_percent']:.4f}%\n"
        )
        f.write(
            f"Estimated precision (all mapped incl. reverse): {metrics['estimated_precision_all_mapped_percent']:.4f}%\n"
        )


def write_summary_csv(metrics: dict, csv_file: str):
    with open(csv_file, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for k, v in metrics.items():
            if isinstance(v, float):
                w.writerow([k, f"{v:.6f}"])
            else:
                w.writerow([k, v])


def main():
    ap = argparse.ArgumentParser(
        description="Estimate precision from decoy-only Columba SAM (forward-mapped only)"
    )
    ap.add_argument("sam_file", help="Columba SAM alignment output against decoy barcode reference")
    ap.add_argument("report_out", help="Output report file (text)")
    ap.add_argument("summary_out", help="Output summary file (CSV)")
    ap.add_argument("--sample-id", default=None, help="Optional sample ID to include in report")
    args = ap.parse_args()

    metrics = compute_decoy_fp_rate(args.sam_file)
    write_report(metrics, args.report_out, sample_id=args.sample_id)
    write_summary_csv(metrics, args.summary_out)


if __name__ == "__main__":
    main()

