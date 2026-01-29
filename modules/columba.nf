// Columba barcode calling processes

process COLUMBA_BUILD {
    tag "columba_build"
    label 'process_medium'
    
    // Conda environment for LOCAL execution
    // On SLURM: overridden to null, uses HPC modules instead (see conf/executors/slurm.config)
    conda "${moduleDir}/../envs/columba.yml"
    container "${moduleDir}/../containers_backup/columba_build.sif"
    
    publishDir "${params.outdir}/columba_build", mode: 'copy'
    
    input:
    path columba_repo
    
    output:
    path "build_Vanilla/columba*", emit: binaries
    path "versions.yml", emit: versions
    
    when:
    task.ext.when == null || task.ext.when
    
    script:
    """
    # Determine source directory
    if [ -d "${columba_repo}" ]; then
        echo "Using provided Columba repository: ${columba_repo}"
        REPO_DIR="\$(readlink -f ${columba_repo})"
        # Check if already built
        if [ -d "\${REPO_DIR}/build_Vanilla" ] && [ -f "\${REPO_DIR}/build_Vanilla/columba" ] && [ -f "\${REPO_DIR}/build_Vanilla/columba_build" ]; then
            echo "Found existing build_Vanilla directory with binaries - skipping build"
            NEED_BUILD=false
        else
            echo "No existing build found - will build"
            NEED_BUILD=true
        fi
    else
        echo "Cloning Columba repository..."
        git clone git@github.com:biointec/columba.git
        REPO_DIR="\$(pwd)/columba"
        NEED_BUILD=true
    fi
    # Build Columba only if needed
    if [ "\$NEED_BUILD" = "true" ]; then
        echo "Building Columba in \${REPO_DIR}..."
        cd "\${REPO_DIR}"
        bash build_script.sh Vanilla
        cd -
    else
        echo "Using existing Columba binaries from \${REPO_DIR}"
    fi
    # Copy build directory to output location
    echo "Copying binaries from \${REPO_DIR}/build_Vanilla to ./build_Vanilla"
    cp -rL "\${REPO_DIR}/build_Vanilla" ./
    # Verify binaries exist
    ls -lh build_Vanilla/columba*
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        columba: \$(./build_Vanilla/columba --version 2>&1 | head -1 || echo "unknown")
    END_VERSIONS
    """
    
    stub:
    """
    mkdir -p build_Vanilla
    touch build_Vanilla/columba
    touch build_Vanilla/columba_build
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        columba: "stub-version"
    END_VERSIONS
    """
}

process COLUMBA_INDEX {
    tag "$meta.id"
    label 'process_medium'
    
    // Conda environment for LOCAL execution
    // On SLURM: overridden to null, uses HPC modules instead (see conf/executors/slurm.config)
    conda "${moduleDir}/../envs/columba.yml"
    container "${moduleDir}/../containers_backup/columba_build.sif"
    
    publishDir "${params.outdir}/${meta.id}/columba_index", mode: 'copy'
    
    input:
    tuple val(meta), path(barcode_fasta)
    path columba_binaries
    
    output:
    tuple val(meta), path("${meta.id}_index*"), emit: index
    path "versions.yml", emit: versions
    
    when:
    task.ext.when == null || task.ext.when
    
    script:
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    # Build Columba index from FASTA file
    ./columba_build \
        -r ${prefix}_index \
        -f ${barcode_fasta}
    # Verify index files were created
    ls -lh ${prefix}_index*
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        columba_build: \$(./columba_build --version 2>&1 | head -1 || echo "unknown")
    END_VERSIONS
    """
    
    stub:
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    touch ${prefix}_index.columba
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        columba_build: "stub-version"
    END_VERSIONS
    """
}

process COLUMBA_ALIGN {
    tag "$meta.id"
    label 'process_high'
    
    // Conda environment for LOCAL execution
    // On SLURM: overridden to null, uses HPC modules instead (see conf/executors/slurm.config)
    conda "${moduleDir}/../envs/columba.yml"
    container "${moduleDir}/../containers_backup/columba_build.sif"
    
    publishDir "${params.outdir}/${meta.id}", mode: 'copy'
    
    input:
    tuple val(meta), path(reads), path(index_files)
    path columba_binaries
    
    output:
    tuple val(meta), path("${meta.id}_alignment.sam"), emit: sam
    tuple val(meta), path("${meta.id}_barcode_calling_stats.txt"), emit: stats
    path "versions.yml", emit: versions
    
    when:
    task.ext.when == null || task.ext.when
    
    script:
    def prefix = task.ext.prefix ?: "${meta.id}"
    def identity_threshold = meta.identity_threshold ?: 72
    def barcode_window = meta.barcode_window ?: "0-${meta.barcode_length}"
    // Use cpus from meta (parameter file), not from task allocation
    def threads = meta.cpus ?: params.cpus ?: task.cpus
    // Use R1 for single-end mode or merge reads for paired-end
    def input_fastq = reads instanceof List ? reads[0] : reads
    """
    # Run Columba alignment and capture timing information
    # Columba writes SAM to ColumbaOutput.sam by default and logs to stdout
    echo "=== Running Columba Alignment ===" > ${prefix}_timing.log
    START_TIME=\$(date +%s.%N)
    ./columba \
        -f ${input_fastq} \
        -r ${meta.id}_index \
        -I ${identity_threshold} \
        -T ${barcode_window} \
        -t ${threads} \
        2>&1 | tee -a ${prefix}_timing.log
    END_TIME=\$(date +%s.%N)
    DURATION=\$(awk -v start=\$START_TIME -v end=\$END_TIME 'BEGIN {printf "%.3f", end-start}')
    # Rename the output SAM file
    mv ColumbaOutput.sam ${prefix}_alignment.sam
    # Create statistics file
    echo "Columba Barcode Calling Statistics" > ${prefix}_barcode_calling_stats.txt
    echo "==========================================" >> ${prefix}_barcode_calling_stats.txt
    echo "Sample ID: ${meta.id}" >> ${prefix}_barcode_calling_stats.txt
    echo "Identity threshold (-I): ${identity_threshold}" >> ${prefix}_barcode_calling_stats.txt
    echo "Barcode window (-T): ${barcode_window}" >> ${prefix}_barcode_calling_stats.txt
    echo "Threads: ${threads}" >> ${prefix}_barcode_calling_stats.txt
    echo "" >> ${prefix}_barcode_calling_stats.txt
    echo "Output files:" >> ${prefix}_barcode_calling_stats.txt
    echo "  SAM: ${prefix}_alignment.sam" >> ${prefix}_barcode_calling_stats.txt
    echo "" >> ${prefix}_barcode_calling_stats.txt
    echo "Alignment statistics:" >> ${prefix}_barcode_calling_stats.txt
    # Count alignments
    TOTAL_READS=\$(grep -c '^@' ${input_fastq} || echo 0)
    ALIGNED_READS=\$(grep -cv '^@' ${prefix}_alignment.sam || echo 0)
    UNMAPPED=\$(awk '\$2 == 4 {count++} END {print count+0}' ${prefix}_alignment.sam)
    MAPPED=\$((ALIGNED_READS - UNMAPPED))
    echo "  Total reads: \$TOTAL_READS" >> ${prefix}_barcode_calling_stats.txt
    echo "  Mapped reads: \$MAPPED" >> ${prefix}_barcode_calling_stats.txt
    echo "  Unmapped reads: \$UNMAPPED" >> ${prefix}_barcode_calling_stats.txt
    if [ \$TOTAL_READS -gt 0 ]; then
        MAPPING_RATE=\$(awk -v mapped=\$MAPPED -v total=\$TOTAL_READS 'BEGIN {printf "%.2f", (mapped/total)*100}')
        echo "  Mapping rate: \${MAPPING_RATE}%" >> ${prefix}_barcode_calling_stats.txt
    fi
    # Add timing information
    echo "" >> ${prefix}_barcode_calling_stats.txt
    echo "Timing information:" >> ${prefix}_barcode_calling_stats.txt
    echo "  Total alignment time: \${DURATION} seconds" >> ${prefix}_barcode_calling_stats.txt
    if [ \$TOTAL_READS -gt 0 ]; then
        TIME_PER_READ=\$(awk -v dur=\$DURATION -v reads=\$TOTAL_READS 'BEGIN {printf "%.6f", (dur/reads)*1000}')
        echo "  Time per read: \${TIME_PER_READ} ms" >> ${prefix}_barcode_calling_stats.txt
    fi
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        columba: \$(./columba --version 2>&1 | head -1 || echo "unknown")
    END_VERSIONS
    """
    
    stub:
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    touch ${prefix}_alignment.sam
    touch ${prefix}_barcode_calling_stats.txt
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        columba: "stub-version"
    END_VERSIONS
    """
}

