#!/bin/bash
# Submit all columba jobs for 32nt barcode length

echo "Submitting 5 jobs for columba with 32nt barcodes..."

sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/32nt/jobs/job_I77.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/32nt/jobs/job_I78.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/32nt/jobs/job_I80.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/32nt/jobs/job_I82.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/32nt/jobs/job_I84.sh

echo "All jobs submitted for columba 32nt"
