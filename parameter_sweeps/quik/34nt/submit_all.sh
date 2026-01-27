#!/bin/bash
# Submit all quik jobs for 34nt barcode length

echo "Submitting 5 jobs for quik with 34nt barcodes..."

sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/quik/34nt/jobs/job_4mer_r5.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/quik/34nt/jobs/job_4mer_r6.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/quik/34nt/jobs/job_4mer_r7.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/quik/34nt/jobs/job_4mer_r8.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/quik/34nt/jobs/job_4mer_r9.sh

echo "All jobs submitted for quik 34nt"
