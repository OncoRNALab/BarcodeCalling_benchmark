process CALCULATE_BARCODE_STATISTICS {
    tag "$meta.id"
    label 'process_low'

    conda "${moduleDir}/../envs/python_basic.yml"
    
    publishDir "${params.outdir}", mode: 'copy'

    input:
    tuple val(meta), path(filtered_r1), path(filtered_r2)
    
    output:
    tuple val(meta), path("${meta.id}_stats_report.txt"), emit: report
    tuple val(meta), path("${meta.id}_stats_summary.csv"), emit: summary
    tuple val(meta), path("${meta.id}_per_barcode.csv"), emit: per_barcode
    path "versions.yml", emit: versions
    
    when:
    task.ext.when == null || task.ext.when
    
    script:
    def prefix = task.ext.prefix ?: "${meta.id}"
    def barcode_file = meta.barcode_file
    
    """
    calculate_barcode_stats.py \\
        ${barcode_file} \\
        ${filtered_r1} \\
        ${prefix}_stats_report.txt \\
        ${prefix}_stats_summary.csv \\
        ${prefix}_per_barcode.csv \\
        --verbose
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | cut -d' ' -f2)
        calculate_barcode_stats: 1.0.0
    END_VERSIONS
    """
    
    stub:
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    touch ${prefix}_stats_report.txt
    touch ${prefix}_stats_summary.csv
    touch ${prefix}_per_barcode.csv
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | cut -d' ' -f2)
        calculate_barcode_stats: 1.0.0
    END_VERSIONS
    """
}
