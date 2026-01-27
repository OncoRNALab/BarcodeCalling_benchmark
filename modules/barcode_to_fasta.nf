process BARCODE_TO_FASTA {
    tag "$meta.id"
    label 'process_low'
    
    conda "${moduleDir}/../envs/python_basic.yml"
    
    publishDir "${params.outdir}/${meta.id}/columba_prep", mode: 'copy'
    
    input:
    tuple val(meta), path(barcode_file)
    
    output:
    tuple val(meta), path("${meta.id}_barcodes.fasta"), emit: fasta
    path "versions.yml", emit: versions
    
    when:
    task.ext.when == null || task.ext.when
    
    script:
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    #!/usr/bin/env python3
    
    # Convert plain text barcode file to FASTA format for Columba
    with open("${barcode_file}", 'r') as infile, \\
         open("${prefix}_barcodes.fasta", 'w') as outfile:
        
        for idx, line in enumerate(infile):
            barcode = line.strip()
            if barcode:  # Skip empty lines
                # Use 0-based index for header (barcode_0, barcode_1, ...)
                outfile.write(f">barcode_{idx}\\n")
                outfile.write(f"{barcode}\\n")
    
    # Count barcodes
    import subprocess
    result = subprocess.run(['grep', '-c', '^>', '${prefix}_barcodes.fasta'], 
                          capture_output=True, text=True)
    n_barcodes = result.stdout.strip()
    print(f"Converted {n_barcodes} barcodes to FASTA format")
    
    # Create versions file
    with open("versions.yml", 'w') as f:
        f.write('"${task.process}":\\n')
        f.write('    barcode_to_fasta: "1.0.0"\\n')
        f.write('    python: "' + __import__('sys').version.split()[0] + '"\\n')
    """
    
    stub:
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    touch ${prefix}_barcodes.fasta
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        barcode_to_fasta: "1.0.0"
        python: \$(python --version | cut -d' ' -f2)
    END_VERSIONS
    """
}

