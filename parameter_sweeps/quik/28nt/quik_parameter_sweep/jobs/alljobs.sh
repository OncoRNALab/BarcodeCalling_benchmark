#!/bin/bash
#SBATCH -J QUIK_sweep
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --mem=32G
#SBATCH --clusters=accelgor
#SBATCH --output=/kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/logs/QUIK_all.out
#SBATCH --error=/kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/logs/QUIK_all.err

# Environment setup
ml Nextflow/25.04.8

# Define directories
PROJECT_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/BarCall_benchmark"
WORK_DIR="/user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/work_quik_sweep/all"

# Create and change to work directory
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_4mer_r9.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_4mer_r9.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_4mer_r10.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_47mer_r5.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_47mer_r6.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_47mer_r7.json 
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_47mer_r8.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_47mer_r9.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_47mer_r10.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_77mer_r5.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_77mer_r6.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_77mer_r7.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_77mer_r8.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_77mer_r9.json
nextflow run "$PROJECT_DIR/main.nf" -profile singularity,local -params-file /kyukon/scratch/gent/vo/000/gvo00027/vsc44685/barcalling_review/BarCall_benchmark/quik_parameter_sweep/params/params_77mer_r10.json

echo "All QUIK jobs completed"

