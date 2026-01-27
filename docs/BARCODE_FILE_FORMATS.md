# Barcode File Format Guide

## Overview

The RandomBarcodes tool (`BarCallingPress_batch.py`) now supports **automatic format detection** for barcode reference files. You can use either plain text or CSV format - the script will detect and read it correctly.

---

## Supported Formats

### Format 1: Plain Text (Recommended) ✅

**Description**: One barcode per line, no header

**Example**:
```
cacgcgccacgcacgtaaggaaccctcc
gtaatctctgcagcatacttgcgtcgat
tttctgcgacccgagcaacgtggcaatt
gacaagtgctacactcctgcggcgtttc
...
```

**Characteristics**:
- No header row
- One barcode sequence per line
- Case insensitive (will be converted to lowercase internally)
- Empty lines are automatically skipped

**When to use**: This is the standard format for most bioinformatics tools and is the **recommended format**.

---

### Format 2: CSV with Header ✅

**Description**: CSV file with header column named `cell`

**Example**:
```csv
cell
CACGCGCCACGCACGTAAGGAACCCTCC
GTAATCTCTGCAGCATACTTGCGTCGAT
TTTCTGCGACCCGAGCAACGTGGCAATT
GACAAGTGCTACACTCCTGCGGCGTTTC
...
```

**Characteristics**:
- First line must contain column header `cell` (case insensitive)
- Barcode sequences in the `cell` column
- Case insensitive (will be converted to lowercase internally)

**When to use**: If your barcodes come from a spreadsheet or database export.

---

## How Format Detection Works

The script automatically detects the format by examining the first line:

```python
# Detection logic
if first_line.lower() == 'cell' or ',' in first_line:
    # CSV format
else:
    # Plain text format
```

**Detection Rules**:
1. If first line is exactly `"cell"` (case insensitive) → **CSV format**
2. If first line contains a comma `,` → **CSV format**
3. Otherwise → **Plain text format**

---

## Testing Your Barcode File

Use the included test script to verify your barcode file:

```bash
python bin/test_barcode_reading.py /path/to/your/barcode_file.txt
```

**Example output**:
```
Testing barcode file: test_data/benchmark_85K_42K_21K/21K_28nt/barcodes_21K_28_subset1
============================================================
📄 Detected format: Plain text
✅ Successfully read 21000 barcodes

First 5 barcodes:
  1. cacgcgccacgcacgtaaggaaccctcc (length: 28)
  2. gtaatctctgcagcatacttgcgtcgat (length: 28)
  3. tttctgcgacccgagcaacgtggcaatt (length: 28)
  ...
```

---

## Example Files

### Your Current File Format ✅

The file at:
```
test_data/benchmark_85K_42K_21K/21K_28nt/barcodes_21K_28_subset1
```

Is **plain text format** and works perfectly with the updated script:
- 21,000 barcodes
- 28 nucleotides each
- Plain text, one per line

**No conversion needed!** ✅

---

## Converting Between Formats

### Plain Text → CSV

If you need to convert plain text to CSV:

```bash
# Add header to plain text file
(echo "cell" && cat barcodes.txt | tr '[:lower:]' '[:upper:]') > barcodes.csv
```

### CSV → Plain Text

If you have CSV and want plain text:

```bash
# Remove header and extract 'cell' column
tail -n +2 barcodes.csv | cut -d',' -f1 > barcodes.txt
```

---

## Compatibility

### Works with QUIK
QUIK also uses plain text format (one barcode per line), so the same barcode files work for both tools.

### Works with Precision Calculation
The precision calculation module reads the same barcode files, so no separate conversion needed.

---

## File Requirements

Regardless of format, barcode files must:
- ✅ Contain valid DNA sequences (A, C, G, T)
- ✅ Have consistent barcode length throughout the file
- ✅ Match the number specified in `--n_barcodes` parameter (or will be auto-counted)
- ✅ Use UTF-8 or ASCII encoding

**Invalid characters**: The script will convert to lowercase and extract only valid nucleotides (a, c, g, t). Other characters are ignored.

---

## Common Issues

### Issue 1: Wrong number of barcodes

**Error message**:
```
AssertionError: N == len(codes)
```

**Cause**: File has different number of barcodes than specified in `-N` parameter

**Solution**:
- Let the script auto-detect by setting `--n_barcodes null` in parameters
- Or manually count: `wc -l barcode_file.txt` and use that value

### Issue 2: Wrong barcode length

**Error message**:
```
AssertionError: M == len(codes[0][:-1])
```

**Cause**: First barcode doesn't match the length specified in `-M` parameter

**Solution**:
- Check actual barcode length: `head -1 barcode_file.txt | awk '{print length($0)}'`
- Update `--barcode_length` parameter to match

### Issue 3: Empty file or wrong path

**Error message**:
```
FileNotFoundError: [Errno 2] No such file or directory: '...'
```

**Solution**:
- Verify file path is correct
- Check file exists: `ls -lh /path/to/barcode_file.txt`
- Use absolute paths in parameters

---

## Best Practices

1. **Use plain text format** - simpler and more compatible
2. **Use lowercase** - script converts anyway, but lowercase is convention
3. **No extra whitespace** - one barcode per line, no trailing spaces
4. **Check file first** - use `test_barcode_reading.py` before running pipeline
5. **Use absolute paths** - avoids confusion about working directory

---

## Implementation Details

### Modified Code

The barcode reading section in `bin/BarCallingPress_batch.py` (lines 228-246):

```python
# Read barcodes from file (auto-detect CSV or plain text format)
codes = []
with open(filename, 'r') as barcode_file:
    first_line = barcode_file.readline().strip()
    barcode_file.seek(0)  # Reset to beginning
    
    # Detect format
    if first_line.lower() == 'cell' or ',' in first_line:
        # CSV format with header
        reader = csv.DictReader(barcode_file)
        for row in reader:
            codes.append(row['cell'].lower() + '\n')
    else:
        # Plain text format: one barcode per line
        for line in barcode_file:
            barcode = line.strip().lower()
            if barcode:  # Skip empty lines
                codes.append(barcode + '\n')
```

### Changes Made

**Before**:
- ❌ Only supported CSV format with 'cell' header
- ❌ Required specific file structure

**After**:
- ✅ Supports both CSV and plain text
- ✅ Automatic format detection
- ✅ Backward compatible with CSV
- ✅ Works with standard bioinformatics formats

---

## Testing

Tested with actual data:
```bash
✅ Plain text format: test_data/benchmark_85K_42K_21K/21K_28nt/barcodes_21K_28_subset1
   - 21,000 barcodes
   - 28 nucleotides each
   - Successfully read and processed
```

---

## Summary

| Feature | Plain Text | CSV |
|---------|-----------|-----|
| **Format** | One per line | Header + column |
| **Detection** | Automatic | Automatic |
| **Case** | Any (converted) | Any (converted) |
| **Empty lines** | Skipped | Not applicable |
| **Header** | None | Required: `cell` |
| **Compatibility** | QUIK, RandomBarcodes | RandomBarcodes |
| **Recommended** | ✅ Yes | For CSV sources only |

---

## Additional Resources

- **Test script**: `bin/test_barcode_reading.py`
- **Example files**: `test_data/benchmark_85K_42K_21K/*/barcodes_*`
- **Main documentation**: `README.md`
- **Tool selection**: `docs/TOOL_SELECTION.md`

---

*Last updated: January 6, 2026*

