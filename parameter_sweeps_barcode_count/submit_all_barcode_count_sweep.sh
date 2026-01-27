#!/bin/bash
# Master script to submit ALL barcode count parameter sweep jobs
# Total: 240 jobs (75 RandomBarcodes + 75 QUIK + 90 Columba)

echo "="*80
echo "BARCODE COUNT PARAMETER SWEEP - MASTER SUBMISSION SCRIPT"
echo "="*80
echo ""
echo "This will submit 240 jobs total:"
echo "  - RandomBarcodes: 75 jobs"
echo "  - QUIK: 75 jobs"
echo "  - Columba: 90 jobs"
echo ""
echo "Across:"
echo "  - Barcode counts: 21K, 42K, 85K"
echo "  - Barcode lengths: 28nt, 30nt, 32nt, 34nt, 36nt"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "Starting job submission..."
echo ""

bash /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/randombarcodes/submit_all_21K.sh
echo ""
bash /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/randombarcodes/submit_all_42K.sh
echo ""
bash /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/randombarcodes/submit_all_85K.sh
echo ""
bash /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/quik/submit_all_21K.sh
echo ""
bash /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/quik/submit_all_42K.sh
echo ""
bash /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/quik/submit_all_85K.sh
echo ""
bash /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/columba/submit_all_21K.sh
echo ""
bash /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/columba/submit_all_42K.sh
echo ""
bash /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/columba/submit_all_85K.sh
echo ""

echo "="*80
echo "All 240 jobs submitted!"
echo "="*80
echo ""
echo "Monitor jobs with: squeue -u $USER"
echo "Check logs in: /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps_barcode_count/{tool}/{count}_{length}nt/logs/"
