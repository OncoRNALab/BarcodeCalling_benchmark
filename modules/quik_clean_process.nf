process QUIK_BARCODE_CALLING {
    tag "$meta.id"
    label 'use_gpu'
    // GPU count set to 1 (QUIK doesn't support multi-GPU)

    // Container definitions (nf-core style)
    conda "${moduleDir}/../envs/quik_minimal.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'or as://registry-1.docker.io/francops1722/quik_cuda:latest' :
        'francops1722/quik_cuda:latest' }"

    // Publish outputs to results directory
    publishDir "${params.outdir}", mode: 'copy'

    input:
    tuple val(meta), path(reads), path(barcode_file)
    
    output:
    tuple val(meta), path("${meta.id}_R1_filtered.fastq"), path("${meta.id}_R2_filtered.fastq"), emit: filtered_reads
    tuple val(meta), path("${meta.id}_barcode_calling_stats.txt"), emit: stats
    path "versions.yml", emit: versions
    
    when:
    task.ext.when == null || task.ext.when
    
    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    
    // Extract parameters from meta map
    // barcode_file is now a path input, not from meta
    def barcode_start = meta.barcode_start
    def barcode_length = meta.barcode_length
    def strategy = meta.strategy ?: '4_7_mer_gpu_v1'
    def distance_measure = meta.distance_measure ?: 'SEQUENCE_LEVENSHTEIN'
    def rejection_threshold = meta.rejection_threshold ?: 3
    
    """
    # Debug: Check environment and available tools
    echo "=== Environment Debug ==="
    echo "PATH: \$PATH"
    echo "PWD: \$(pwd)"
    which cmake || echo "cmake not found in PATH"
    which make || echo "make not found in PATH"
    which g++ || echo "g++ not found in PATH"
    which nvcc || echo "nvcc not found in PATH"
    cmake --version || echo "cmake version check failed"
    nvcc --version || echo "nvcc version check failed"
    echo "========================="
    
    # Copy quik source from bin directory
    cp -r ${projectDir}/bin/quik .
    
    # Create tmp directory for nvcc temporary files
    mkdir -p \${TMPDIR:-/tmp}
    export TMPDIR=\${TMPDIR:-\$(pwd)/tmp}
    mkdir -p \$TMPDIR
    echo "TMPDIR set to: \$TMPDIR"
    
    # Build the executable using HPC modules
    cd quik
    # Clean any previous build artifacts to avoid cache conflicts
    rm -rf build
    mkdir -p build
    cd build
    cmake ..
    make -j${task.cpus}
    
    # Copy executable to working directory
    echo "Files in build directory:"
    ls -la
    echo "Current directory: \$(pwd)"
    WORK_DIR=\$(pwd | sed 's|/quik/build||')
    echo "Work directory: \$WORK_DIR"
    echo "Copying executable to work directory..."
    cp single_strategy_benchmark_fastq_paired \$WORK_DIR/
    cd ../..
    echo "Files in work directory after copy:"
    ls -la
    echo "Making executable..."
    chmod +x single_strategy_benchmark_fastq_paired
    
    # Decompress FASTQ files if gzipped (QUIK doesn't handle .gz natively)
    if [[ ${reads[0]} == *.gz ]]; then
        echo "Decompressing R1 FASTQ..."
        gunzip -c ${reads[0]} > R1_decompressed.fastq
        R1_INPUT=R1_decompressed.fastq
    else
        R1_INPUT=${reads[0]}
    fi
    
    if [[ ${reads[1]} == *.gz ]]; then
        echo "Decompressing R2 FASTQ..."
        gunzip -c ${reads[1]} > R2_decompressed.fastq
        R2_INPUT=R2_decompressed.fastq
    else
        R2_INPUT=${reads[1]}
    fi
    
    # Run quik_clean barcode calling using the built executable
    ./single_strategy_benchmark_fastq_paired \\
        ${barcode_file} \\
        \$R1_INPUT \\
        \$R2_INPUT \\
        ${barcode_start} \\
        ${barcode_length} \\
        ${strategy} \\
        ${distance_measure} \\
        ${rejection_threshold} \\
        ${prefix}_R1_filtered.fastq \\
        ${prefix}_R2_filtered.fastq \\
        > ${prefix}_barcode_calling_stats.txt 2>&1
    
    # Clean up decompressed files
    rm -f R1_decompressed.fastq R2_decompressed.fastq
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        quik_clean: \$(echo "1.0.0")
        cuda: \$(nvcc --version | grep release | cut -d' ' -f6 | cut -d',' -f1)
        cmake: \$(cmake --version | head -1 | cut -d' ' -f3)
    END_VERSIONS
    """
    
    stub:
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    touch ${prefix}_R1_filtered.fastq
    touch ${prefix}_R2_filtered.fastq
    touch ${prefix}_barcode_calling_stats.txt
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        quik_clean: \$(echo "1.0.0")
        container: /user/gent/446/vsc44685/ScratchVO_dir/barcalling_review/containers_trials/quik_build.sif
    END_VERSIONS
    """
}
