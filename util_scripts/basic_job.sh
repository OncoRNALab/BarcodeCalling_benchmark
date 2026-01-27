#!/bin/bash
#PBS -N Randombarcodes_job1
#PBS -l nodes=1:ppn=1:
#PBS -l walltime=10:00:00
#PBS -l mem=32gb

ml  Nextflow/25.04.8

export APPTAINER_TMPDIR=/user/gent/446/vsc44685/ScratchVO_dir/apptainer_cache/tmp
export APPTAINER_CACHEDIR=/user/gent/446/vsc44685/ScratchVO_dir/singularity
export SINGULARITY_CACHEDIR=/user/gent/446/vsc44685/ScratchVO_dir/singularity
export NXF_SINGULARITY_CACHEDIR=/user/gent/446/vsc44685/ScratchVO_dir/apptainer_cache
export CONDA_PKGS_DIRS=/user/gent/446/vsc44685/ScratchVO_dir/conda_pkgs
export NXF_CONDA_CACHEDIR=/user/gent/446/vsc44685/ScratchVO_dir/conda_cache
export CONDA_ENVS_PATH=/user/gent/446/vsc44685/ScratchVO_dir/conda_envs
export TMPDIR=/user/gent/446/vsc44685/ScratchVO_dir/tmp
export CONDA_TMPDIR=/user/gent/446/vsc44685/ScratchVO_dir/tmp
export CONDA_PKGS_DIRS=/user/gent/446/vsc44685/ScratchVO_dir/conda_pkgs

#complete with the correct parameters
nextflow run main.nf -profile vsc_singularity -params-file test_params_randombarcodes.json

