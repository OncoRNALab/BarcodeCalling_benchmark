#!/bin/bash
# Submit all columba jobs for 30nt barcode length

echo "Submitting 5 jobs for columba with 30nt barcodes..."

sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/30nt/jobs/job_I77.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/30nt/jobs/job_I78.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/30nt/jobs/job_I80.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/30nt/jobs/job_I82.sh
sbatch /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark/parameter_sweeps/columba/30nt/jobs/job_I84.sh

echo "All jobs submitted for columba 30nt"
