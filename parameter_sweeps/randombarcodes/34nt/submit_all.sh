#!/bin/bash
# Submit all randombarcodes jobs for 34nt barcode length

echo "Submitting 5 jobs for randombarcodes with 34nt barcodes..."

sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/34nt/jobs/job_t100_n5.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/34nt/jobs/job_t100_n6.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/34nt/jobs/job_t100_n7.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/34nt/jobs/job_t100_n8.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/randombarcodes/34nt/jobs/job_t100_n9.sh

echo "All jobs submitted for randombarcodes 34nt"
