# Results Directory Structure - Standardization Plan

## Proposed Standard Structure

```
results/
├── error_rate/              # Error rate benchmark (3 tools × 3 counts × 3 error rates)
│   ├── quik/
│   │   ├── 21K_36nt_low/
│   │   ├── 21K_36nt_medium/
│   │   ├── 21K_36nt_high/
│   │   ├── 42K_36nt_low/
│   │   └── 85K_36nt_low/
│   ├── randombarcodes/
│   │   └── [same structure]
│   └── columba/
│       └── [same structure]
│
├── parameter_sweeps/        # Parameter sweeps (multiple barcode lengths)
│   ├── results_28nt/
│   │   ├── quik_sweep/
│   │   │   ├── 4mer_r5/
│   │   │   ├── 4mer_r6/
│   │   │   └── 7mer_r8/
│   │   ├── randombarcodes_sweep/
│   │   │   ├── t100_n5/
│   │   │   └── t5000_n9/
│   │   └── columba_sweep/
│   │       ├── I77/
│   │       └── I80/
│   ├── results_30nt/
│   ├── results_32nt/
│   ├── results_34nt/
│   └── results_36nt/
│
├── runtime/                 # Runtime/scaling benchmarks
│   ├── quik/
│   │   └── 36nt/
│   │       ├── 4mer_1gpu/
│   │       ├── 4mer_2gpu/
│   │       ├── 4mer_4gpu/
│   │       ├── 4_7mer_1gpu/
│   │       ├── 4_7mer_2gpu/
│   │       └── 4_7mer_4gpu/
│   ├── randombarcodes/
│   │   └── 36nt/
│   │       ├── t100_1gpu/
│   │       ├── t100_2gpu/
│   │       ├── t100_4gpu/
│   │       ├── t5000_1gpu/
│   │       ├── t5000_2gpu/
│   │       └── t5000_4gpu/
│   └── columba/
│       └── 36nt/
│           ├── 1cpu/
│           ├── 2cpu/
│           ├── 4cpu/
│           ├── 8cpu/
│           └── 16cpu/
│
├── 1M_scaling/              # 1M read scaling (3 tools × 3 barcode counts)
│   ├── quik/
│   │   ├── 21K_36nt/
│   │   ├── 42K_36nt/
│   │   └── 85K_36nt/
│   ├── randombarcodes/
│   │   └── [same structure]
│   └── columba/
│       └── [same structure]
│
└── real_data/               # Real sequencing data
    ├── quik/
    │   ├── munchen_25024_1in4/
    │   ├── munchen_25024_1in2/
    │   └── munchen_25024_1in1/
    ├── randombarcodes/
    │   └── [same structure]
    └── columba/
        └── [same structure]
```

## Structure Rationale

1. **Top level**: Benchmark type (what question we're answering)
2. **Second level**: Tool name (which tool is being tested)
3. **Third level**: Dataset/configuration specifics (barcode count, length, parameters)
4. **Deepest level**: Individual run outputs (sample_id directories with results)

## Benefits

- Clear separation between different benchmark types
- Easy to find results for specific analyses
- Consistent tool → dataset → config hierarchy
- Notebooks can easily navigate to correct benchmark
- No mixing of results from different analyses
