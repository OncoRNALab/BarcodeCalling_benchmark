process CALCULATE_PRECISION_SAM {
    tag "$meta.id"
    label 'process_low'

    conda "${moduleDir}/../envs/python_basic.yml"
    
    publishDir "${params.outdir}/${meta.id}", mode: 'copy'

    input:
    tuple val(meta), path(sam_file)
    path ground_truth
    
    output:
    tuple val(meta), path("${meta.id}_precision_report.txt"), emit: report
    tuple val(meta), path("${meta.id}_precision_summary.csv"), emit: summary
    path "versions.yml", emit: versions
    
    when:
    task.ext.when == null || task.ext.when
    
    script:
    def prefix = task.ext.prefix ?: "${meta.id}"
    def barcode_file = meta.barcode_file
    def identity_threshold = meta.identity_threshold ?: 72
    
    """
    python3 ${moduleDir}/../bin/calculate_precision_sam_forward_only.py \\
        ${barcode_file} \\
        ${ground_truth} \\
        ${sam_file} \\
        ${prefix}_precision_report.txt \\
        ${prefix}_precision_summary.csv \\
        --identity-threshold ${identity_threshold} \\
        --verbose
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | cut -d' ' -f2)
        calculate_precision_sam_forward_only: 1.0.0
    END_VERSIONS
    """
    
    stub:
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    touch ${prefix}_precision_report.txt
    touch ${prefix}_precision_summary.csv
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | cut -d' ' -f2)
        calculate_precision_sam_forward_only: 1.0.0
    END_VERSIONS
    """
}

