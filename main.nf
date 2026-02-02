#!/usr/bin/env nextflow

/*
========================================================================================
    Barcode Calling Benchmark Workflow
========================================================================================
    Benchmarking workflow for barcode calling algorithms
    Supports: QUIK, RandomBarcodes (Press et al.)
----------------------------------------------------------------------------------------
*/

nextflow.enable.dsl = 2

// Include barcode calling processes
include { QUIK_BARCODE_CALLING } from './modules/quik_clean_process.nf'
include { RANDOMBARCODES } from './modules/randombarcodes.nf'
include { BARCODE_TO_FASTA } from './modules/barcode_to_fasta.nf'
include { COLUMBA_BUILD; COLUMBA_INDEX; COLUMBA_ALIGN } from './modules/columba.nf'
include { CALCULATE_PRECISION } from './modules/precision_process.nf'
include { CALCULATE_PRECISION_SAM } from './modules/precision_sam.nf'
include { CALCULATE_BARCODE_STATISTICS } from './modules/barcode_statistics.nf'

/*
========================================================================================
    WORKFLOW: Main testing workflow
========================================================================================
*/

workflow {
    
    // Tool selection parameter
    params.tool = "quik"  // Options: "quik", "randombarcodes", "columba"
    
    def tool_name = params.tool.toLowerCase()
    
    log.info """
    ============================================
    B A R C O D E   C A L L I N G   B E N C H M A R K
    ============================================
    Tool: ${tool_name.toUpperCase()}
    Workflow for Paired FASTQ Processing
    ============================================
    """
    
    // Define test parameters - MODIFY THESE FOR YOUR TEST DATA
    params.barcode_file = "/path/to/your/barcode_file.txt"
    params.r1_fastq = "/path/to/your/sample_R1.fastq"
    params.r2_fastq = "/path/to/your/sample_R2.fastq"
    params.sample_id = "test_sample"
    params.barcode_start = 10
    params.barcode_length = 36
    params.ground_truth = null  // Optional: ground truth file for precision calculation
    params.data_mode = "auto"   // Options: "auto", "simulated", "real"
    
    // QUIK-specific parameters
    params.strategy = "4_7_mer_gpu_v1"
    params.distance_measure = "SEQUENCE_LEVENSHTEIN"
    params.rejection_threshold = 3
    
    // RandomBarcodes-specific parameters
    params.n_barcodes = null  // Will be auto-detected if not provided
    params.ntriage = 5000      // Triage size for RandomBarcodes
    params.nthresh = 3         // Distance threshold for RandomBarcodes
    params.gpus = 1            // Number of GPUs to use for RandomBarcodes
    
    // Columba-specific parameters
    params.columba_repo = null       // Path to Columba repository (if pre-cloned)
    params.identity_threshold = 72   // Minimum identity threshold (-I parameter)
    params.barcode_window = null     // Barcode window in reads (-T parameter, e.g., "0-36")
    
    // Validate required parameters
    if (!params.barcode_file || !file(params.barcode_file).exists()) {
        error "Barcode file not found: ${params.barcode_file}. Please specify --barcode_file"
    }
    if (!params.r1_fastq || !file(params.r1_fastq).exists()) {
        error "R1 FASTQ file not found: ${params.r1_fastq}. Please specify --r1_fastq"
    }
    if (!params.r2_fastq || !file(params.r2_fastq).exists()) {
        error "R2 FASTQ file not found: ${params.r2_fastq}. Please specify --r2_fastq"
    }
    
    // Validate tool selection
    if (!(tool_name in ['quik', 'randombarcodes', 'columba'])) {
        error "Unknown tool: ${tool_name}. Please specify --tool quik, --tool randombarcodes, or --tool columba"
    }
    
    // Create metadata map with all parameters
    def meta = [
        id: params.sample_id,
        barcode_file: params.barcode_file,
        barcode_length: params.barcode_length,
        // QUIK-specific parameters
        barcode_start: params.barcode_start,
        strategy: params.strategy,
        distance_measure: params.distance_measure,
        rejection_threshold: params.rejection_threshold,
        // RandomBarcodes-specific parameters
        n_barcodes: params.n_barcodes,
        ntriage: params.ntriage,
        nthresh: params.nthresh,
        gpus: params.gpus,
        // Columba-specific parameters
        identity_threshold: params.identity_threshold,
        barcode_window: params.barcode_window
    ]
    
    // Create input channel with tuple val(meta), path(reads)
    input_ch = Channel.of([
        meta,
        [file(params.r1_fastq), file(params.r2_fastq)]
    ])
    
    // Run the selected barcode calling tool
    if (tool_name == 'quik') {
        log.info "Running QUIK barcode calling..."
        QUIK_BARCODE_CALLING(input_ch)
        barcode_results = QUIK_BARCODE_CALLING.out.filtered_reads
        barcode_stats = QUIK_BARCODE_CALLING.out.stats
        columba_output = null
    } else if (tool_name == 'randombarcodes') {
        log.info "Running RandomBarcodes barcode calling..."
        RANDOMBARCODES(input_ch)
        barcode_results = RANDOMBARCODES.out.filtered_reads
        barcode_stats = RANDOMBARCODES.out.stats
        columba_output = null
    } else if (tool_name == 'columba') {
        log.info "Running Columba barcode calling..."
        
        // Step 1: Convert plain text barcodes to FASTA
        barcode_ch = input_ch.map { m, reads -> [m, file(m.barcode_file)] }
        BARCODE_TO_FASTA(barcode_ch)
        
        // Step 2: Build Columba (if needed) or use existing binaries
        if (params.columba_repo) {
            columba_repo_path = file(params.columba_repo)
        } else {
            columba_repo_path = file('.')  // Will clone in process
        }
        COLUMBA_BUILD(columba_repo_path)
        
        // Step 3: Build index from FASTA
        COLUMBA_INDEX(BARCODE_TO_FASTA.out.fasta, COLUMBA_BUILD.out.binaries)
        
        // Step 4: Run alignment
        columba_input = input_ch.join(COLUMBA_INDEX.out.index)
        COLUMBA_ALIGN(columba_input, COLUMBA_BUILD.out.binaries)
        
        // Columba outputs SAM instead of filtered FASTQ
        barcode_results = null
        barcode_stats = COLUMBA_ALIGN.out.stats
        columba_output = COLUMBA_ALIGN.out.sam
    }
    
    // Run precision calculation if ground truth is provided
    if (params.ground_truth && file(params.ground_truth).exists()) {
        log.info "Ground truth file provided: ${params.ground_truth}"
        log.info "Will calculate precision metrics..."
        
        ground_truth_ch = file(params.ground_truth)
        
        if (tool_name == 'columba') {
            // Use SAM-specific precision calculation for Columba
            CALCULATE_PRECISION_SAM(
                columba_output,
                ground_truth_ch
            )
            precision_summary = CALCULATE_PRECISION_SAM.out.summary
            precision_report = CALCULATE_PRECISION_SAM.out.report
        } else {
            // Use standard FASTQ-based precision calculation for QUIK/RandomBarcodes
            CALCULATE_PRECISION(
                barcode_results,
                ground_truth_ch
            )
            precision_summary = CALCULATE_PRECISION.out.summary
            precision_report = CALCULATE_PRECISION.out.report
        }
        
        // Display precision results
        precision_summary.view { sample_meta, csv ->
            """
            ============================================
            PRECISION METRICS for sample: ${sample_meta.id}
            Tool: ${tool_name.toUpperCase()}
            ============================================
            Summary CSV: ${params.outdir}/${sample_meta.id}/${csv.name}
            """
        }
        
        precision_report.view { sample_meta, report ->
            """
            Detailed Report: ${params.outdir}/${sample_meta.id}/${report.name}
            ============================================
            """
        }
    } else {
        log.info "No ground truth file provided. Skipping precision calculation."
        log.info "To enable precision calculation, specify --ground_truth <file>"
    }
    
    // Calculate barcode statistics (works with or without ground truth)
    if (tool_name != 'columba' && barcode_results != null) {
        log.info "Calculating barcode assignment statistics..."
        
        CALCULATE_BARCODE_STATISTICS(barcode_results)
        
        // Display statistics results
        CALCULATE_BARCODE_STATISTICS.out.summary.view { sample_meta, csv ->
            """
            ============================================
            BARCODE STATISTICS for sample: ${sample_meta.id}
            ============================================
            Summary CSV: ${params.outdir}/${sample_meta.id}/${csv.name}
            """
        }
        
        CALCULATE_BARCODE_STATISTICS.out.report.view { sample_meta, report ->
            """
            Detailed Report: ${params.outdir}/${sample_meta.id}/${report.name}
            """
        }
        
        CALCULATE_BARCODE_STATISTICS.out.per_barcode.view { sample_meta, csv ->
            """
            Per-barcode CSV: ${params.outdir}/${sample_meta.id}/${csv.name}
            ============================================
            """
        }
    }
    
    // Display results
    if (tool_name == 'columba') {
        columba_output.view { sample_meta, sam ->
            """
            ============================================
            RESULTS for sample: ${sample_meta.id}
            Tool: ${tool_name.toUpperCase()}
            ============================================
            SAM alignment: ${params.outdir}/${sam.name}
            ============================================
            """
        }
    } else {
        barcode_results.view { sample_meta, r1, r2 ->
            """
            ============================================
            RESULTS for sample: ${sample_meta.id}
            Tool: ${tool_name.toUpperCase()}
            ============================================
            Filtered R1: ${params.outdir}/${sample_meta.id}/${r1.name}
            Filtered R2: ${params.outdir}/${sample_meta.id}/${r2.name}
            ============================================
            """
        }
    }
    
    barcode_stats.view { sample_meta, stats ->
        """
        Statistics file: ${params.outdir}/${stats.name}
        """
    }
}

/*
========================================================================================
    WORKFLOW COMPLETION
========================================================================================
*/

workflow.onComplete {
    log.info """
    ============================================
    Workflow completed successfully!
    ============================================
    Duration: ${workflow.duration}
    Success:  ${workflow.success}
    Exit status: ${workflow.exitStatus}
    ============================================
    """
}
