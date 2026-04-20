# Example cfDNA Data from EPI2ME wf-human-variation

This directory contains example output data from the EPI2ME wf-human-variation workflow, focused on cfDNA (cell-free DNA) analysis for oncology applications.

## Files

### cnv_results.tsv
Copy Number Variation (CNV) calls from cfDNA analysis.
- **Format**: Tab-separated values (TSV)
- **Columns**:
  - chromosome: Chromosome name (chr1-22, X, Y)
  - start: Start position (1-based)
  - end: End position (1-based)
  - copy_number: Estimated copy number
  - log2_ratio: Log2 ratio of observed vs expected coverage
  - quality_score: Quality score for the CNV call
  - gene_region: Associated gene or region type

### methylation_results.tsv
DNA methylation calls from cfDNA analysis.
- **Format**: Tab-separated values (TSV)
- **Columns**:
  - chromosome: Chromosome name (chr1-22, X)
  - position: Genomic position (1-based)
  - strand: DNA strand (+ or -)
  - methylation_level: Methylation level (0.0-1.0, where 1.0 = 100% methylated)
  - coverage: Read coverage at this position
  - quality_score: Quality score for the methylation call
  - context: Sequence context (CG, CHG, CHH)
  - gene_region: Associated gene region (promoter, enhancer, etc.)

## Data Characteristics

- **Sample Type**: cfDNA (cell-free DNA) from cancer patient
- **Coverage**: Low-pass sequencing (~0.5-1x genome coverage)
- **Size**: Both files are < 1MB for demonstration purposes
- **Content**: Focused on cancer-relevant genes and regions

## Usage

These example files can be used for:
- Testing data processing pipelines
- Training machine learning models
- Demonstrating cfDNA analysis workflows
- Validating bioinformatics tools

## Source

Data format based on EPI2ME wf-human-variation workflow outputs from Oxford Nanopore Technologies.