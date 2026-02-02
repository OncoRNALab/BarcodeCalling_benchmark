/*
========================================================================================
    RandomBarcodes Barcode Calling Process
========================================================================================
    NOTE: This process intentionally omits conda/container directives at the process level.
    
    Configuration is controlled per-executor:
    - PBS executor: Uses HPC modules (PyTorch-bundle) via beforeScript in pbs.config
                    See conf/executors/pbs.config for null overrides
    - Local executor: Uses conda/container specified in conf/modules.config
    
    DO NOT add conda/container directives here - they are managed in config files.
========================================================================================
*/

process RANDOMBARCODES {
    tag "$meta.id"
    label 'use_gpu'
    // GPU count set to 1 (QUIK doesn't support multi-GPU)

    // Publish outputs to results directory
    publishDir "${params.outdir}", mode: 'copy'
    
    input:
    tuple val(meta), path(reads)
    
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
    def barcode_file = meta.barcode_file
    def barcode_start = meta.barcode_start ?: 0
    def barcode_length = meta.barcode_length ?: meta.len_barcode ?: 28
    def n_barcodes = meta.n_barcodes ?: 21000
    def ntriage = meta.ntriage ?: 5000
    def nthresh = meta.nthresh ?: 3
    def gpus = meta.gpus ?: params.gpus ?: 1
    
    // Determine barcode count from barcode file if not provided
    def count_barcodes = n_barcodes == null || n_barcodes == 0
    
    """
    # Debug: Check environment
    echo "=== Environment Debug ==="
    echo "CUDA_VISIBLE_DEVICES: \${CUDA_VISIBLE_DEVICES:-not set}"
    echo "PATH: \$PATH"
    echo "PWD: \$(pwd)"
    which python || echo "python not found"
    python --version || echo "python version check failed"
    python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available())" || echo "PyTorch check failed"
    echo "========================="
    
    # Count barcodes if needed
    ${count_barcodes ? "N_BARCODES=\$(wc -l < ${barcode_file})" : "N_BARCODES=${n_barcodes}"}
    echo "Number of barcodes: \$N_BARCODES"
    
    # Run RandomBarcodes barcode calling with multi-GPU support
    echo "Starting RandomBarcodes with ${gpus} GPU(s)..."
    
    # Run barcode calling with parallel GPU processing
    ${generateRandomBarcodesCommands(gpus, reads, barcode_file, barcode_start, barcode_length, ntriage, nthresh, prefix)}
    
    # Wait for all processes to complete
    wait
    
    # Check if any GPU process failed
    MAX_GPU_IDX=\$((${gpus} - 1))
    for i in \$(seq 0 \$MAX_GPU_IDX); do
        if [ -f gpu_\${i}.log ]; then
            echo "=== GPU \${i} Output ==="
            cat gpu_\${i}.log
            echo "===================="
        fi
    done
    
    # Verify output files were created
    if [ ! -s "${prefix}_1of${gpus}_R1.fastq.gz" ]; then
        echo "ERROR: GPU processes did not produce output files"
        echo "Checking for error details..."
        ls -lah
        exit 1
    fi
    
    # Combine outputs from all GPU segments
    # Note: Script outputs files with format like "prefix_1of1_R1.fastq.gz" when Seg_id is "1/1"
    if [ ${gpus} -gt 1 ]; then
        echo "Combining outputs from ${gpus} GPU segments..."
        cat ${prefix}_*of${gpus}_R1.fastq.gz > ${prefix}_R1_combined.fastq.gz
        cat ${prefix}_*of${gpus}_R2.fastq.gz > ${prefix}_R2_combined.fastq.gz
        rm -f ${prefix}_*of${gpus}_R1.fastq.gz ${prefix}_*of${gpus}_R2.fastq.gz
    else
        mv ${prefix}_1of1_R1.fastq.gz ${prefix}_R1_combined.fastq.gz
        mv ${prefix}_1of1_R2.fastq.gz ${prefix}_R2_combined.fastq.gz
    fi
    
    # Decompress output files (to match QUIK output format)
    gunzip -c ${prefix}_R1_combined.fastq.gz > ${prefix}_R1_filtered.fastq
    gunzip -c ${prefix}_R2_combined.fastq.gz > ${prefix}_R2_filtered.fastq
    
    # Create stats file
    echo "RandomBarcodes Barcode Calling Statistics" > ${prefix}_barcode_calling_stats.txt
    echo "==========================================" >> ${prefix}_barcode_calling_stats.txt
    echo "Sample ID: ${meta.id}" >> ${prefix}_barcode_calling_stats.txt
    echo "Number of barcodes: \$N_BARCODES" >> ${prefix}_barcode_calling_stats.txt
    echo "Barcode length: ${barcode_length}" >> ${prefix}_barcode_calling_stats.txt
    echo "Triage size (Ntriage): ${ntriage}" >> ${prefix}_barcode_calling_stats.txt
    echo "Distance threshold (Nthresh): ${nthresh}" >> ${prefix}_barcode_calling_stats.txt
    echo "GPUs used: ${gpus}" >> ${prefix}_barcode_calling_stats.txt
    echo "" >> ${prefix}_barcode_calling_stats.txt
    echo "Output files:" >> ${prefix}_barcode_calling_stats.txt
    echo "  R1: ${prefix}_R1_filtered.fastq" >> ${prefix}_barcode_calling_stats.txt
    echo "  R2: ${prefix}_R2_filtered.fastq" >> ${prefix}_barcode_calling_stats.txt
    echo "" >> ${prefix}_barcode_calling_stats.txt
    echo "Read counts:" >> ${prefix}_barcode_calling_stats.txt
    R1_COUNT=\$(grep -c "^@" ${prefix}_R1_filtered.fastq || echo 0)
    R2_COUNT=\$(grep -c "^@" ${prefix}_R2_filtered.fastq || echo 0)
    echo "  R1 reads: \$R1_COUNT" >> ${prefix}_barcode_calling_stats.txt
    echo "  R2 reads: \$R2_COUNT" >> ${prefix}_barcode_calling_stats.txt
    
    # Extract timing information from GPU logs
    echo "" >> ${prefix}_barcode_calling_stats.txt
    echo "Runtime metrics:" >> ${prefix}_barcode_calling_stats.txt
    
    # Aggregate timing from all GPU logs
    TOTAL_TIME=0
    TOTAL_READS=0
    GPU_COUNT=0
    
    for gpu_log in gpu_*.log; do
        if [ -f "\$gpu_log" ]; then
            GPU_COUNT=\$((GPU_COUNT + 1))
            
            # Extract total time (in seconds)
            TIME_SEC=\$(grep "Barcode decoding completed in" "\$gpu_log" | awk '{print \$5}')
            if [ -n "\$TIME_SEC" ]; then
                TOTAL_TIME=\$(awk "BEGIN {print \$TOTAL_TIME + \$TIME_SEC}")
            fi
            
            # Extract reads processed for this GPU
            READS_PROC=\$(grep "Total reads processed:" "\$gpu_log" | awk '{print \$4}')
            if [ -n "\$READS_PROC" ]; then
                TOTAL_READS=\$((TOTAL_READS + READS_PROC))
            fi
        fi
    done
    
    # Calculate and report metrics
    if [ "\$GPU_COUNT" -gt 0 ]; then
        echo "  Total time (seconds): \$TOTAL_TIME" >> ${prefix}_barcode_calling_stats.txt
        
        # Calculate time per read in milliseconds
        if [ "\$TOTAL_READS" -gt 0 ]; then
            TIME_PER_READ=\$(awk -v t="\$TOTAL_TIME" -v r="\$TOTAL_READS" 'BEGIN {printf "%.6f", (t / r) * 1000}')
            echo "  Time per read (milliseconds): \$TIME_PER_READ" >> ${prefix}_barcode_calling_stats.txt
        fi
    fi
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        randombarcodes: 1.0.0
        python: \$(python --version | sed 's/Python //')
        torch: \$(python -c "import torch; print(torch.__version__)" 2>/dev/null || echo "N/A")
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
        randombarcodes: 1.0.0
        python: "stub-version"
        torch: "stub-version"
    END_VERSIONS
    """
}

// Helper function to generate multi-GPU commands
def generateRandomBarcodesCommands(gpus, reads, barcode_file, barcode_start, barcode_length, ntriage, nthresh, prefix) {
    def commands = []
    for (int i = 1; i <= gpus; i++) {
        int cuda = (i - 1) % gpus
        commands << """
        echo "Launching GPU ${i}/${gpus} on CUDA device ${cuda}..."
        BarCallingPress_batch.py \\
            -R1 ${reads[0]} \\
            -R2 ${reads[1]} \\
            -N \$N_BARCODES \\
            -M ${barcode_length} \\
            --barcode-start ${barcode_start} \\
            -B ${barcode_file} \\
            --Ntriage ${ntriage} \\
            --Nthresh ${nthresh} \\
            --out-prefix ${prefix} \\
            -C ${cuda} \\
            --Seg_id ${i}/${gpus} > gpu_${cuda}.log 2>&1 &
        pid${i - 1}=\$!
        echo "GPU ${i}/${gpus} launched with PID \$pid${i - 1}"
        """
    }
    return commands.join("\n")
}