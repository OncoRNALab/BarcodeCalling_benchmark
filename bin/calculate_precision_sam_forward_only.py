#!/usr/bin/env python3
"""
Calculate precision and recall for Columba SAM output (forward-mapped only).

This is a modified copy of `calculate_precision_sam.py`.

Key change:
- Only considers *mapped forward* alignments as valid barcode calls.
  Any alignment with FLAG bit 16 set (reverse strand) is rejected (unassigned).

Other behavior is intentionally kept consistent with the original script:
- Only FLAG bit 4 (unmapped) and invalid RNAME cause rejection.
- The `--identity-threshold` argument is accepted for compatibility, but this
  script does not compute identity from SAM tags; it assumes Columba's `-I`
  filtering was applied during alignment.
"""

import argparse
import csv
import re
from collections import Counter


FLAG_UNMAPPED = 0x4
FLAG_REVERSE = 0x10
FLAG_SECONDARY = 0x100
FLAG_SUPPLEMENTARY = 0x800


def parse_sam_alignments_forward_only(sam_file, identity_threshold=72, allow_secondary=False):
    """
    Parse SAM file and extract barcode calls for each read, using only forward-mapped alignments.

    Args:
        sam_file: Path to SAM file
        identity_threshold: Accepted for CLI compatibility (not used for filtering here)
        allow_secondary: If True, consider secondary/supplementary alignments; otherwise ignore them

    Returns:
        dict: read_id -> {barcode_idx, status ('called' or 'rejected'), ...}
    """
    # Keep best eligible alignment per read_id (by MAPQ)
    best_calls = {}
    rejected = {}  # read_id -> rejection dict (only used if no called alignment is found)

    with open(sam_file, "r") as f:
        for line in f:
            if line.startswith("@"):
                continue

            fields = line.rstrip("\n").split("\t")
            if len(fields) < 11:
                continue

            read_id = fields[0]
            try:
                flag = int(fields[1])
            except ValueError:
                # Malformed flag; treat as rejected if nothing better exists
                rejected.setdefault(
                    read_id,
                    {"barcode_idx": None, "status": "rejected", "reason": "invalid_flag"},
                )
                continue

            rname = fields[2]  # reference name (barcode ID)
            try:
                mapq = int(fields[4])
            except ValueError:
                mapq = 0

            # Ignore secondary/supplementary by default to avoid overriding the primary call
            if not allow_secondary and (flag & FLAG_SECONDARY or flag & FLAG_SUPPLEMENTARY):
                continue

            # Unmapped
            if flag & FLAG_UNMAPPED:
                rejected.setdefault(
                    read_id,
                    {"barcode_idx": None, "status": "rejected", "reason": "unmapped"},
                )
                continue

            # Reverse strand -> reject (forward-only policy)
            if flag & FLAG_REVERSE:
                rejected.setdefault(
                    read_id,
                    {"barcode_idx": None, "status": "rejected", "reason": "reverse_strand"},
                )
                continue

            # Extract barcode index from reference name (e.g., "barcode_0" -> 0)
            match = re.match(r"barcode_(\d+)", rname)
            if not match:
                rejected.setdefault(
                    read_id,
                    {"barcode_idx": None, "status": "rejected", "reason": "invalid_rname"},
                )
                continue

            barcode_idx = int(match.group(1))

            # Eligible forward-mapped call: keep best MAPQ for this read_id
            prev = best_calls.get(read_id)
            if prev is None or mapq > prev.get("mapq", -1):
                best_calls[read_id] = {"barcode_idx": barcode_idx, "status": "called", "mapq": mapq}

    # Merge: called alignments override any rejection records for that read_id
    read_calls = dict(rejected)
    read_calls.update(best_calls)
    return read_calls


def load_ground_truth(ground_truth_file):
    """Load ground truth barcode assignments (one barcode index per line)."""
    ground_truth = []
    with open(ground_truth_file, "r") as f:
        for line in f:
            idx = line.strip()
            if idx:
                ground_truth.append(int(idx))
    return ground_truth


def load_barcode_sequences(barcode_file):
    """Load barcode sequences from file (one barcode per line)."""
    barcodes = []
    with open(barcode_file, "r") as f:
        for line in f:
            barcode = line.strip()
            if barcode:
                barcodes.append(barcode)
    return barcodes


def calculate_metrics(read_calls, ground_truth, barcodes):
    """
    Calculate precision, recall, and accuracy metrics.

    The core logic is identical to the original script:
    - unassigned if missing or rejected
    - correct if predicted_idx == ground_truth[read_idx]
    """
    total_reads = len(ground_truth)

    # Build fast lookup: read_idx -> read_id
    read_idx_to_id = {}
    for read_id in read_calls.keys():
        parts = read_id.split("_")
        for i, part in enumerate(parts):
            if part == "read" and i + 1 < len(parts):
                try:
                    read_idx = int(parts[i + 1])
                    read_idx_to_id[read_idx] = read_id
                    break
                except ValueError:
                    continue

    correct = 0
    incorrect = 0
    unassigned = 0
    misassignments = Counter()

    for read_idx, true_barcode_idx in enumerate(ground_truth):
        read_id = read_idx_to_id.get(read_idx)
        if read_id is None or read_calls[read_id]["status"] == "rejected":
            unassigned += 1
            continue

        predicted_idx = read_calls[read_id]["barcode_idx"]
        if predicted_idx == true_barcode_idx:
            correct += 1
        else:
            incorrect += 1
            true_bc = (
                barcodes[true_barcode_idx]
                if true_barcode_idx < len(barcodes)
                else f"barcode_{true_barcode_idx}"
            )
            pred_bc = (
                barcodes[predicted_idx] if predicted_idx < len(barcodes) else f"barcode_{predicted_idx}"
            )
            misassignments[(true_bc, true_barcode_idx, pred_bc, predicted_idx)] += 1

    assigned = correct + incorrect
    assignment_rate = (assigned / total_reads * 100) if total_reads > 0 else 0
    precision = (correct / assigned * 100) if assigned > 0 else 0
    recall = (correct / total_reads * 100) if total_reads > 0 else 0
    accuracy = recall

    return {
        "total_reads": total_reads,
        "correct": correct,
        "incorrect": incorrect,
        "unassigned": unassigned,
        "assigned": assigned,
        "assignment_rate": assignment_rate,
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
        "misassignments": misassignments,
    }


def write_report(metrics, report_file, top_n=10):
    """Write detailed text report."""
    with open(report_file, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("BARCODE CALLING PRECISION REPORT (Columba SAM output, forward-mapped only)\n")
        f.write("=" * 80 + "\n\n")

        f.write("=== OVERALL METRICS ===\n")
        f.write(f"Total reads (ground truth): {metrics['total_reads']}\n")
        f.write(f"Reads processed: {metrics['total_reads']}\n")
        f.write(f"Reads assigned: {metrics['assigned']}\n")
        f.write(f"Reads unassigned/rejected: {metrics['unassigned']}\n\n")

        f.write("=== ACCURACY METRICS ===\n")
        f.write(f"Correct assignments: {metrics['correct']}\n")
        f.write(f"Incorrect assignments: {metrics['incorrect']}\n")
        f.write(f"Assignment rate: {metrics['assignment_rate']:.2f}%\n")
        f.write(f"Precision (correct/assigned): {metrics['precision']:.2f}%\n")
        f.write(f"Recall (correct/total): {metrics['recall']:.2f}%\n")
        f.write(f"Accuracy (correct/total): {metrics['accuracy']:.2f}%\n\n")

        if metrics["misassignments"]:
            f.write(f"=== TOP {top_n} MISASSIGNMENTS ===\n")
            f.write(
                f"{'Count':<7} | {'True Barcode (idx)':<30} | {'Assigned Barcode (idx)':<30}\n"
            )
            f.write("-" * 80 + "\n")

            for (true_bc, true_idx, pred_bc, pred_idx), count in metrics["misassignments"].most_common(
                top_n
            ):
                true_display = (
                    f"{true_bc[:20]}... ({true_idx:>5})"
                    if len(true_bc) > 20
                    else f"{true_bc} ({true_idx:>5})"
                )
                pred_display = (
                    f"{pred_bc[:20]}... ({pred_idx:>5})"
                    if len(pred_bc) > 20
                    else f"{pred_bc} ({pred_idx:>5})"
                )
                f.write(f"{count:<7} | {true_display:<30} | {pred_display:<30}\n")


def write_summary_csv(metrics, csv_file):
    """Write summary metrics to CSV."""
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerow(["total_reads", metrics["total_reads"]])
        writer.writerow(["total_processed", metrics["total_reads"]])
        writer.writerow(["correct_assignments", metrics["correct"]])
        writer.writerow(["incorrect_assignments", metrics["incorrect"]])
        writer.writerow(["unassigned_reads", metrics["unassigned"]])
        writer.writerow(["assignment_rate_percent", f"{metrics['assignment_rate']:.4f}"])
        writer.writerow(["precision_percent", f"{metrics['precision']:.4f}"])
        writer.writerow(["recall_percent", f"{metrics['recall']:.4f}"])
        writer.writerow(["accuracy_percent", f"{metrics['accuracy']:.4f}"])


def main():
    parser = argparse.ArgumentParser(
        description="Calculate precision/recall for Columba SAM output (forward-mapped only)"
    )
    parser.add_argument("barcode_file", help="Barcode reference file (plain text)")
    parser.add_argument("ground_truth", help="Ground truth file (one index per line)")
    parser.add_argument("sam_file", help="Columba SAM alignment output")
    parser.add_argument("report_out", help="Output report file (text)")
    parser.add_argument("summary_out", help="Output summary file (CSV)")
    parser.add_argument(
        "--identity-threshold",
        type=int,
        default=72,
        help="Identity threshold used in Columba (accepted for compatibility; not enforced from SAM)",
    )
    parser.add_argument(
        "--allow-secondary",
        action="store_true",
        help="Include secondary/supplementary alignments when selecting best forward call (default: ignore)",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        print(f"Loading barcode sequences from {args.barcode_file}...")
    barcodes = load_barcode_sequences(args.barcode_file)

    if args.verbose:
        print(f"Loading ground truth from {args.ground_truth}...")
    ground_truth = load_ground_truth(args.ground_truth)

    if args.verbose:
        print(f"Parsing SAM alignments from {args.sam_file} (forward-only)...")
    read_calls = parse_sam_alignments_forward_only(
        args.sam_file, identity_threshold=args.identity_threshold, allow_secondary=args.allow_secondary
    )

    if args.verbose:
        print("Calculating metrics...")
    metrics = calculate_metrics(read_calls, ground_truth, barcodes)

    if args.verbose:
        print(f"Writing report to {args.report_out}...")
    write_report(metrics, args.report_out)

    if args.verbose:
        print(f"Writing summary to {args.summary_out}...")
    write_summary_csv(metrics, args.summary_out)

    if args.verbose:
        print("\nMetrics Summary:")
        print(f"  Precision: {metrics['precision']:.2f}%")
        print(f"  Recall: {metrics['recall']:.2f}%")
        print(f"  Assignment rate: {metrics['assignment_rate']:.2f}%")


if __name__ == "__main__":
    main()

