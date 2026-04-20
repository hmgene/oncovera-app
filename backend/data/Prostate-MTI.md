Prostate-MTI: A Multimodal AI Framework for Prostate Cancer Outcome Prediction
Technical Overview for Biological Scientists and Clinicians
April 16. 2026 - by Josh Kim

1. Motivation and Clinical Context

Prostate cancer exhibits profound molecular and clinical heterogeneity that current risk stratification tools — ISUP grade groups, PSA kinetics, CAPRA scores, and nomograms — only partially capture. Patients with identical Gleason scores and clinical staging frequently diverge dramatically in their trajectories: one remains indolent for decades, another develops castration-resistant disease within two years. This divergence is encoded in the tumour's molecular architecture at multiple biological scales simultaneously.
The Prostate-MTI framework is built on the premise that no single omic layer is sufficient to model this complexity. Clinically actionable signals are distributed across the genome, transcriptome, proteome, epigenome, tumour microenvironment (TME), and histomorphology — and critically, the interactions between these layers carry information that each layer alone cannot provide. The framework therefore assembles modality-specific foundation models into an end-to-end pipeline that produces a unified, patient-level embedding suitable for survival analysis, risk stratification, and treatment response prediction.

3. Modality-Specific Inputs and Encoders

Each biological data stream is processed by a dedicated foundation model pretrained on large domain-specific corpora before fine-tuning on prostate cancer data. Below are the specific inputs, feature representations, and encoding strategies for each modality.

2.1  Whole Genome Sequencing (WGS) — Nucleotide-Resolution Genomic Encoding

Foundation Model: Evo (7B parameters, Arc Institute / TogetherAI)
Specific Inputs:

Raw nucleotide sequence (hg38-aligned reads; tumour and matched germline)
Somatic single-nucleotide variants (SNVs) and their trinucleotide mutational context
Small insertions and deletions (indels)
Structural variants (SVs): translocations, inversions, large deletions/duplications
Copy number alterations (CNAs): focal and arm-level amplifications/deletions (e.g., PTEN loss at 10q23, AR amplification at Xq12, MYC gain at 8q24)
Tumour mutational burden (TMB) and microsatellite instability (MSI) status
COSMIC mutational signature decomposition (SBS, DBS, ID catalogues)
Chromothripsis and genome doubling events

Encoding Approach:

Evo is a 7-billion parameter genomic foundation model built on the StripedHyena architecture — a hybrid that alternates data-controlled convolutional operators (hyena layers) with sparse multi-head attention blocks. It operates at single-nucleotide, byte-level resolution with a context window spanning 131 kilobases, sufficient to capture intra-gene regulatory interactions, splice site disruptions, and promoter-exon relationships in a single forward pass. The StripedHyena design is critical because pure transformer attention scales quadratically with sequence length, making megabase-scale processing computationally prohibitive; hyena layers reduce this to near-linear complexity while preserving long-range dependency modelling.
Evo was pretrained on 300 billion nucleotides spanning prokaryotic and phage genomes, learning deep evolutionary conservation patterns before domain adaptation to human oncogenomics. In the prostate cancer context, Evo is sensitive to recurrent driver alterations: ETS family fusions (TMPRSS2::ERG, TMPRSS2::ETV1), SPOP and FOXA1 mutations, CDK12 biallelic inactivation (associated with tandem duplicator phenotype and neoantigen load), RB1 and TP53 co-deletion (linked to neuroendocrine transdifferentiation), and homologous recombination deficiency (HRD) signatures in BRCA2, ATM, and CDK12 contexts.
Output: A dense embedding vector encoding systems-level genomic state, including mutational processes, structural rearrangement burden, and copy number landscape.

2.1b  Regulatory Genome Annotation — Sequence-to-Regulatory-Feature Prediction
Foundation Model: AlphaGenome (Google DeepMind)

Rationale:

While Evo encodes the raw DNA sequence into a genomic state embedding, it does not explicitly model the functional regulatory consequences of sequence variation at base-pair resolution across the full range of regulatory outputs. AlphaGenome fills this gap as a complementary encoder specifically designed to predict the regulatory state of the genome directly from DNA sequence — without requiring experimental measurements of chromatin or transcription factor (TF) binding in the patient's tumour.

Specific Inputs:

DNA sequence windows (up to 1 Mb context) centred on regions of interest: promoters, enhancers, CTCF binding sites, topologically associating domain (TAD) boundaries
Tumour-specific SNVs and indels at regulatory loci (non-coding mutations)
Reference genome annotations: ENCODE cCREs (candidate cis-regulatory elements), Roadmap Epigenomics chromatin state segmentations
Known prostate-relevant regulatory elements: AR-bound enhancers (AREs), TMPRSS2 enhancer region, MYC super-enhancer at 8q24, SCHLAP1 lncRNA locus

Encoding Approach:

AlphaGenome is a sequence-to-function foundation model that ingests raw DNA sequence and simultaneously predicts a comprehensive catalogue of regulatory outputs at base-pair resolution:

Chromatin accessibility: ATAC-Seq and DNase-Seq peak profiles across hundreds of cell types, enabling identification of open chromatin regions in prostate epithelial and tumour cell contexts without matched ATAC data from the patient
Transcription factor binding: Predicted occupancy profiles for >700 TFs, including AR, FOXA1, HOXB13, NKX3-1, ERG (in fusion-positive tumours), and pioneer factors governing luminal identity
Histone modification landscapes: H3K27ac (active enhancers), H3K4me3 (active promoters), H3K27me3 (Polycomb repression), H3K9me3 (constitutive heterochromatin) — predicted genome-wide from sequence alone
Gene expression: Predicted RNA-Seq abundance profiles, allowing the model to estimate the transcriptional consequence of non-coding mutations at regulatory elements
Splicing: Predicted splice site strengths and alternative splicing outcomes at each position — directly relevant to AR exon 3 skipping (AR-V7) and TMPRSS2::ERG fusion splice variants
3D genome organisation: Predicted contact frequency maps (Hi-C proxies) and TAD boundary strength, enabling identification of regulatory element-promoter loop disruptions caused by structural variants

Prostate Cancer Regulatory Alterations Captured:
AlphaGenome is particularly well-suited to prostate cancer because the disease is driven by extensive non-coding regulatory rewiring:

AR enhancer amplification and gain of novel AR binding sites through chromatin remodelling
TMPRSS2::ERG fusion placing ERG under androgen-regulated TMPRSS2 enhancer control — detectable as an AR-occupied enhancer upstream of an ERG-expressing locus
MYC super-enhancer activation at 8q24 (the most common CNA in prostate cancer) — AlphaGenome predicts the regulatory consequence of copy number gain at this locus
Enhancer hijacking events where SVs juxtapose strong prostate enhancers with proto-oncogene promoters
CpG island methylation effects on predicted TF binding (AlphaGenome accepts methylation-aware sequence encodings)
Non-coding mutations in AR response elements (AREs) that alter predicted AR occupancy scores — a class of driver alterations invisible to coding-sequence-only analyses

Integration with Evo:
Evo and AlphaGenome operate at different levels of abstraction and are complementary. Evo provides a global, evolutionary-context-aware embedding of the entire tumour genome. AlphaGenome provides high-resolution, position-specific regulatory predictions at loci of interest. Their outputs are combined via concatenation before entry into the fusion core, with Kronecker product terms computed between AlphaGenome's regulatory feature predictions and Evo's structural variant embedding — capturing interactions such as "SV disrupts TAD boundary AND creates novel AR binding site."
Output: A regulatory genome embedding encoding predicted TF occupancy, chromatin state, splicing landscape, and 3D genome organisation consequences of the tumour's sequence — including non-coding driver alterations invisible to standard somatic mutation callers.

2.2  Tumour Mutation Profiles — Pathway-Aware Mutation Graph Encoding
Foundation Model: MutationProjector
Specific Inputs:

Somatic mutation calls: SNVs, indels, CNAs (segment-level log2 ratios and allele-specific copy numbers)
Variant allele frequencies (VAFs) as proxies for clonal architecture
Known driver vs. passenger mutation annotations (OncoKB, ClinVar tiers)
Mutation hotspot coordinates (e.g., SPOP F133 cluster, AR ligand-binding domain mutations)
Gene-level binary alteration matrix (mutated/not mutated per patient)

Encoding Approach:
Rather than treating mutations as an unordered list of gene-level events, the mutation encoder represents the genome as a heterogeneous biological network. Each gene is a node; edges encode eight distinct types of molecular interaction: protein-protein interaction (PPI), signalling pathway membership, co-expression, metabolic, regulatory (TF-target), miRNA-target, genetic interaction (synthetic lethality), and physical proximity networks.
Graph Attention Networks (GATs) propagate each somatic alteration's signal across this multi-relational graph. This is biologically motivated: a PTEN loss is meaningless in isolation but becomes a potent PI3K/AKT/mTOR pathway activator when broadcast across signalling network edges. Attention weights are learned per edge type, allowing the model to discover which network contexts are most predictive of clinical outcome — for instance, upweighting co-expression edges for transcriptionally active alterations and PPI edges for missense mutations at protein interfaces.
The result is a compact cancer subtype representation that reflects the downstream functional consequences of mutation burden rather than the raw alteration catalogue.
Output: A mutation-graph embedding capturing pathway activation patterns, clonal dominance signals, and epistatic relationships between co-occurring alterations.

2.3  Single-Cell Transcriptomics — Tumour Microenvironment Encoding
This modality accepts input from three distinct sources depending on clinical and logistical context: scRNA-Seq from tumour tissue, a normal-cell reference foundation model, or scRNA-Seq derived from liquid biopsy. These are not mutually exclusive — where multiple sources are available they are fused; where only one is available the architecture degrades gracefully to that source alone.

2.3a  Tissue scRNA-Seq (Primary Source)
Specific Inputs:

Per-cell gene expression UMI count matrices (QC thresholds: >200 genes/cell, <20% mitochondrial read fraction)
Cell barcode × gene matrices post ambient RNA correction (SoupX or CellBender) and doublet removal (DoubletFinder or Scrublet)
UMAP coordinates and Leiden/Louvain cluster assignments
Cell cycle phase scores (G1/S/G2M gene signatures per Tirosh et al.)
Inferred copy number profiles (inferCNV or CopyKAT) to discriminate malignant epithelial cells from non-malignant stroma
Cell type abundance fractions across compartments:

Epithelial: luminal (AR+, KLK3+, NKX3-1+), basal (TP63+, KRT5+, KRT14+), luminal-intermediate (CD38+, PSCA+), club/hillock (LTF+, PIGR+), neuroendocrine (SYP+, CHGA+, INSM1+)
Stromal: myCAF (ACTA2+, MMP11+), iCAF (IL6+, CXCL12+, CCL2+), endothelial, pericyte, smooth muscle
Immune: CD8+ cytotoxic TILs (GZMB+, PRF1+), exhausted CD8+ T cells (PDCD1+, HAVCR2+, TIGIT+), CD4+ Tregs (FOXP3+, IL2RA+), M1 macrophages (CD80+, CXCL10+), M2/TAMs (CD163+, MRC1+, TREM2+), MDSCs (S100A8/A9+), NK cells (NCAM1+, KLRB1+), mast cells (KIT+, TPSAB1+), plasmacytoid dendritic cells

Encoding Approach:

Transformer-based single-cell language models — scGPT and Geneformer: Both models treat the ranked gene expression profile of each cell as a token sequence — genes with highest expression appearing first. scGPT was pretrained on over 33 million human single-cell transcriptomes using masked gene modelling, enabling zero-shot cell type annotation and gene regulatory network inference. Geneformer was initially pretrained on 30 million single-cell transcriptomes and continually pretrained on approximately 14 million cancer-specific transcriptomes via masked gene modelling (randomly masking 15% of gene tokens and predicting their expression rank), conferring strong representations of oncogenic cell states. Fine-tuning of both models emphasises AR transcriptional programme activity, luminal differentiation state, and immunosuppressive TME configurations relevant to prostate cancer.
Universal multiscale cell embedding — UCE (Universal Cell Embedding): UCE generates cell embeddings generalisable across tissues and species by grounding gene representations in protein sequence space — practically important for transferring cell-type annotations to bulk RNA-Seq cohorts (TCGA-PRAD) where matched single-cell data is absent. UCE also enables deconvolution of bulk transcriptomes into pseudo-single-cell resolution.
Downstream features include: tumour cell differentiation state (luminal A vs. luminal B vs. AR-low vs. NEPC), CD8+/Treg ratio, M1/M2 polarisation index, myCAF/iCAF ratio, and ligand-receptor interaction scores between malignant and immune compartments (CellChat / NicheNet).

2.3b  Normal-Cell Reference Foundation Model (Alternative / Complementary Source)

Rationale:
A key limitation of tumour-derived scRNA-Seq is that it requires fresh or adequately cryopreserved tissue — often unavailable from archival FFPE biopsy material, which constitutes the majority of prostate cancer specimens in clinical practice. An important alternative is to use a foundation model pretrained exclusively on normal human cells, then apply it to characterise tumour cells by measuring their deviation from normality rather than their absolute transcriptional state.
This approach is conceptually powerful: cancerous transformation is, by definition, a departure from normal cellular identity. A model that deeply encodes normal prostate epithelial cell biology — including the transcriptional programmes governing luminal differentiation, AR-regulated secretory function, basal-to-luminal maturation, and cell cycle quiescence — can serve as a fixed reference frame against which pathological states are measured.
Specific Inputs (from normal-cell reference model):

Normal prostate tissue atlas: scRNA-Seq profiles from benign prostate tissue (transition zone, peripheral zone, central zone) across multiple healthy donors — covering full differentiation hierarchy from basal stem-like progenitors through luminal intermediate to terminally differentiated secretory cells
Matched normal adjacent tissue (NAT) profiles from radical prostatectomy specimens, providing patient-specific normal reference embeddings
Human Cell Atlas (HCA) prostate cell type reference embeddings
Normal immune cell atlas references for TME immune compartment normalisation

Encoding Approach:
The normal-cell reference foundation model is UCE or Geneformer pretrained exclusively on large compendia of healthy human single-cell transcriptomes — spanning the Human Cell Atlas, Tabula Sapiens, and curated prostate-specific atlases. Crucially, this model is not fine-tuned on cancer data; its weights represent a stable learned manifold of normal cell identity.
At inference, tumour cell embeddings from the same encoder architecture are projected into the normal-cell embedding space. Two biologically informative quantities are then extracted:

Cellular deviation score: The Euclidean or cosine distance between a tumour cell's embedding and its nearest normal cell archetype in the reference manifold. High deviation indicates severe transcriptional dysregulation — characteristic of high-grade, dedifferentiated tumour cells. Low deviation indicates a cell retaining near-normal transcriptional identity, relevant to well-differentiated Gleason pattern 3 disease.
Pseudotime displacement: Using normal differentiation trajectories inferred from the reference model (basal → luminal intermediate → luminal secretory), each tumour cell is assigned a position along the normal differentiation axis and a perpendicular "off-trajectory" displacement. Tumour cells that are off-trajectory despite appearing differentiated (common in SPOP-mutant prostate cancer) are distinguished from those that are arrested at an immature state (common in TP53/RB1-deleted NEPC precursors).
Cell identity confusion index: Some tumour cells embed near the boundary between two normal cell types (e.g., luminal and neuroendocrine), reflecting transcriptional plasticity and lineage infidelity — a known mechanism of treatment resistance in CRPC through AR-indifferent, neuroendocrine, or double-negative (AR−, NE−) phenotypes.

This reference-anchored encoding strategy is particularly valuable for detecting neuroendocrine transdifferentiation (NEPC) early — where tumour cells progressively depart from their luminal identity towards a SYP+/CHGA+/INSM1+ NE identity — and for characterising the luminal-intermediate "castration-resistant progenitor" cell state (CD38+, PSCA+, SOX2+) implicated in ADT resistance.
Practical advantage: Because the reference model requires only the encoder weights (not fresh tumour tissue), deviation scores can be computed from bulk RNA-Seq via pseudo-single-cell deconvolution, significantly expanding applicability to TCGA-PRAD and other bulk cohorts.

2.3c  Liquid Biopsy scRNA-Seq (Alternative / Longitudinal Source)
Rationale:
Tissue biopsy is invasive, spatially limited (sampling bias), and typically obtained only at diagnosis and disease progression — providing static molecular snapshots rather than dynamic disease monitoring. Liquid biopsy scRNA-Seq, applied to circulating tumour cells (CTCs) or to single cells isolated from cell-free fractions of peripheral blood, offers a minimally invasive, longitudinally repeatable alternative that captures the metastatic and treatment-resistant subpopulations most relevant to lethal prostate cancer outcomes.
Specific Input Sources:
Circulating Tumour Cells (CTCs):

CTCs isolated by epithelial capture (EpCAM+ enrichment: CellSearch, microfluidic chip) or epithelial-independent methods (DEPArray, size-based filtration — important for capturing EpCAM-low mesenchymal/NEPC CTCs that are missed by EpCAM-only platforms)
Single-cell RNA-Seq of individual CTCs (SmartSeq2, 10x Chromium; low input adaptation required)
CTC cluster (CTC microemboli) transcriptomes — particularly relevant as CTC clusters have 23–50× higher metastatic potential than single CTCs (Aceto et al.)
Key CTC markers: EPCAM+/CD45− for epithelial CTCs; EpCAM−/VIM+/N-cadherin+ for mesenchymal CTCs; SYP+/CHGA+ for NEPC CTCs
AR splice variant expression at single-cell level (AR-V7, AR-V9) — directly predictive of enzalutamide/abiraterone resistance
EMT (epithelial-mesenchymal transition) score per cell (CDH1/CDH2 ratio, VIM, SNAI1, ZEB1 expression)

Extracellular Vesicle (EV) / Exosome-Associated RNA:

Small RNA-Seq from plasma-derived exosomes (tumour-derived EV fraction enriched by size exclusion chromatography or immunocapture on PSMA+ or EpCAM+ beads)
Single EV transcriptomics (emerging methodology; provides cell-of-origin attribution for circulating RNA)

Cell-Free RNA (cfRNA) from Plasma:

Bulk plasma cfRNA-Seq as a proxy for tumour transcriptional state when CTC counts are insufficient for single-cell analysis (<1 CTC/7.5 mL blood, common in localised disease)
Tumour-derived cfRNA fraction estimated by allele-specific expression at somatic heterozygous SNV sites

Encoding Approach:
Liquid biopsy scRNA-Seq data is processed through the same transformer-based single-cell encoder as tissue scRNA-Seq, with two key modifications:

Sparsity adaptation: CTCs typically yield 500–2,000 detected genes per cell versus 3,000–6,000 for tissue-dissociated cells due to the stress of circulating in blood, RNase exposure, and low input material. The encoder is fine-tuned on intentionally downsampled tissue scRNA-Seq data to learn robust representations from sparse gene expression profiles, preventing artifactual distance from normal cell archetypes driven purely by dropout rather than true transcriptional dysregulation.
Normal-cell reference anchoring (as in 2.3b): CTC embeddings are projected onto the normal prostate cell reference manifold. Because CTCs are by definition the most aggressive, invasive subpopulation — having survived anoikis, evaded immune surveillance, and entered systemic circulation — they are expected to show high cellular deviation scores and strong EMT/NEPC off-trajectory displacement. These deviation metrics from CTCs serve as biomarkers of metastatic potential distinct from primary tumour biopsy data.

Longitudinal Integration:
A key advantage of liquid biopsy scRNA-Seq is serial sampling. CTC transcriptomes collected at baseline, after 4 weeks of ADT, and at biochemical progression are encoded as a temporal sequence of embeddings. A recurrent or time-aware attention module models the trajectory of the CTC transcriptional state over treatment — capturing, for example, the emergence of an AR-V7+ CTC subclone under selective pressure of enzalutamide, or the progressive expansion of a SYP+/NEPC CTC population during CRPC evolution. These trajectory embeddings are fused into the patient-level representation alongside the static primary tumour embedding.
Clinical utility of liquid biopsy scRNA-Seq specifically in prostate cancer:

Detection of AR-V7 splice variant expression in CTCs (PROPHECY trial validated) as predictor of primary resistance to enzalutamide/abiraterone — directly actionable (switch to taxane-based therapy)
NEPC transdifferentiation detection: SYP+/CHGA+ CTC emergence under AR-pathway therapy pressure
EMT score as predictor of lymph node and visceral metastatic spread
CTC cluster count as independent prognostic factor in mCRPC (superior to single CTC enumeration)


Unified Output (all 2.3 sources):
A cell-state embedding that captures: (a) intratumoural transcriptional heterogeneity and dominant cell states from tissue (if available), (b) deviation from normal prostate cell identity as measured by reference-model distance metrics, and (c) metastatic/treatment-resistant subpopulation dynamics from liquid biopsy CTCs (if serially available). All three sub-embeddings are concatenated and passed through a modality-presence-aware attention layer before entering the fusion core.

2.4  Bulk Multi-Omics — Proteomics, Epigenomics, Transcriptomics
Foundation Models: SeNMo · DeePathNet · mosGraphGPT
Specific Inputs:
Bulk RNA-Seq:

Normalised gene expression (TPM or VST-transformed counts)
Splice variant usage ratios (e.g., AR-V7 splicing, ERG fusion isoforms)
Gene fusion calls from paired-end reads
Deconvoluted immune cell fractions (CIBERSORT, TIMER2)

DNA Methylation (EPIC array or WGBS):

Beta values at CpG sites; M-values for differential methylation analysis
Promoter methylation status of key suppressors: GSTP1, APC, RASSF1, CDH1
Global methylation landscape (hypomethylation burden)
Methylation-based immune cell deconvolution

Proteomics (mass spectrometry — LC-MS/MS or reverse-phase protein array, RPPA):

Protein abundance (log2 iTRAQ ratios or LFQ intensities)
Phosphoproteomic profiles (activated kinase signalling: phospho-AKT S473, phospho-ERK T202/Y204, phospho-AR S81)
Post-translational modification (PTM) site occupancy

miRNA:

Small RNA-Seq derived mature miRNA expression (miR-141, miR-375, miR-21, miR-200 family — prostate-relevant)

Encoding Approach — Self-Normalising Multi-Omics Network: SeNMo
The "big P, small n" challenge (p >> n; thousands of features, hundreds of patients) is a fundamental statistical problem in multi-omics. Standard batch normalisation collapses when mini-batches are small; dropout causes instability in high-dimensional sparse inputs.
SeNMo (Self-Normalizing Deep Learning Model for Multi-Omics) addresses this by pairing Scaled Exponential Linear Unit (SELU) activations with Alpha-Dropout. SELU activations have the remarkable property that, under appropriate weight initialisation (Lecun normal), the mean and variance of activations converge to fixed points (μ→0, σ²→1) across arbitrarily deep layers. This eliminates the need for explicit normalisation layers while preventing both vanishing and exploding gradients — critical for stable training on small prostate cancer cohorts.
SeNMo processes gene expression, DNA methylation, miRNA, and protein expression simultaneously in a single forward pass, learning cross-omic feature correlations (e.g., methylation-driven silencing of GSTP1 co-occurring with loss of GSTP1 protein, itself correlated with oxidative stress transcriptomic signature) that modality-siloed models cannot capture.
Encoding Approach — Biological Pathway Transformer: DeePathNet
DeePathNet is a complementary, explainable transformer-based encoder that projects all omics measurements into a biologically interpretable latent space defined by 241 literature-curated cancer pathways (including PI3K/AKT/mTOR, AR signalling, DNA damage response, Wnt/β-catenin, cell cycle, MAPK, hypoxia/HIF, and immune checkpoint pathways). A pathway encoder first maps raw omics features onto pathway activation scores; these scores are then processed by a multi-head self-attention transformer module that models inter-pathway dependencies — learning, for instance, that simultaneous activation of the AR pathway and suppression of the DDR pathway predicts a distinct clinical behaviour compared with either alteration alone.
DeePathNet's pathway-centric architecture provides direct interpretability: activation scores are mappable to known biology and actionable therapeutic targets.
Encoding Approach — Generative Multi-Omic Graph Model: mosGraphGPT
mosGraphGPT is a generative AI foundation model that integrates multi-omic data through multi-level signalling graphs, modelling gene-gene, gene-protein, and pathway-pathway interactions simultaneously. Its generative pretraining objective allows it to impute missing omic modalities at inference time — for patients with RNA-Seq but no proteomics, mosGraphGPT can generate a probabilistic protein expression estimate conditioned on the transcriptomic input, partially compensating for data modality gaps.
Output: A multi-omics embedding encoding pathway activation state, epigenetic silencing landscape, proteomic signalling activity, and cross-omic interaction patterns.

2.4b  Protein Structure and Molecular Interaction Modelling
Foundation Models: AlphaFold2 · AlphaFold3 (Google DeepMind)
Rationale:
Bulk proteomics and phosphoproteomics (section 2.4) measure abundance of proteins and their modification states, but do not capture the structural consequences of somatic mutations on protein function. A missense mutation in SPOP at the F133 cluster, for example, does not reduce SPOP protein abundance — it disrupts the SPOP-substrate binding interface, preventing ubiquitination of AR and BET bromodomain proteins. Similarly, AR ligand-binding domain mutations (T878A, W742C, H875Y) alter the structural geometry of the androgen-binding pocket, enabling agonist activity of enzalutamide and conferring treatment resistance. These functional consequences are structurally encoded and require protein structure modelling to capture.
Specific Inputs:
For AlphaFold2 (single-chain protein structure prediction):

Amino acid sequences of mutant and wildtype proteins derived from tumour WGS: AR (including LBD mutants and AR-V7 truncated sequence), SPOP (with F133 cluster missense variants), FOXA1 (wing2 domain mutations), CDK12 (kinase domain mutations), BRCA2 (BRCT and BRC repeat domain variants), ATM (FAT and kinase domain mutations)
Multiple sequence alignments (MSAs) from UniRef90 and BFD databases for evolutionary context
Structural templates from the Protein Data Bank (PDB)

For AlphaFold3 (multimeric and multi-molecular complex prediction):

Protein-protein complexes: AR homodimer with coactivator peptides (SRC-1, CBP/p300), SPOP-CULLIN3-RBX1 E3 ligase complex with substrate degrons, AR-FOXA1-HOXB13 pioneer factor complex at ARE-containing chromatin
Protein-DNA complexes: AR bound to androgen response elements (AREs), FOXA1 bound to nucleosomal DNA (chromatin pioneer function)
Protein-ligand complexes: AR LBD bound to enzalutamide, abiraterone, darolutamide, and novel small molecules — directly relevant to drug response prediction
Protein-RNA complexes: splicing regulatory proteins bound to AR pre-mRNA at exon 3 splice sites (relevant to AR-V7 biogenesis)

Encoding Approach:
AlphaFold2 uses an Evoformer architecture — a specialised transformer that jointly processes multiple sequence alignments (evolutionary co-variation information) and pairwise inter-residue distance representations — to predict high-confidence 3D coordinates (pLDDT score >70 considered reliable) for individual protein chains. For each somatic missense mutation identified by Evo, AlphaFold2 generates paired wildtype and mutant structure predictions; structural differences are quantified as:

ΔΔG (predicted folding free energy change): Destabilising mutations (ΔΔG >> 0) suggest loss-of-function via protein misfolding; stabilising mutations at active sites may enhance function.
Interface ΔRMSD: Root-mean-square deviation at predicted protein-protein or protein-ligand interaction interfaces between wildtype and mutant structures — the primary readout for missense mutations at binding interfaces (e.g., SPOP F133 variants disrupting substrate binding)
Predicted local distance difference test (pLDDT) delta: Localised confidence drops in the mutant structure indicate regions of induced disorder.

AlphaFold3 extends this to full molecular complexes using a diffusion-based structure generation module following an updated Pairformer. For prostate cancer, the most clinically informative AlphaFold3 applications are:

AR LBD mutant-drug docking: Predicting whether enzalutamide, abiraterone, or darolutamide can stably occupy the mutant AR ligand-binding pocket — directly predicting resistance to AR-pathway therapies before clinical progression is observed. T878A creates a larger binding pocket that accommodates enzalutamide as an agonist; AlphaFold3 structural predictions quantify this.
AR-FOXA1 co-occupancy at pioneer enhancers: Predicting how FOXA1 wing2 domain mutations alter cooperative binding with AR at AREs — mechanistically linking non-coding regulatory rewiring (AlphaGenome) with structural protein changes.
SPOP E3 ligase complex disruption: Modelling how F133 cluster mutations alter the geometry of the SPOP substrate-binding MATH domain relative to the CULLIN3 scaffold, predicting which substrates (AR, BRD4, TRIM24) escape degradation.

Structural Embeddings for Fusion:
Raw 3D coordinate outputs from AlphaFold2/3 are not directly suitable for downstream machine learning. Structural features are extracted and encoded as:

Graph neural network (GNN) encoding of protein contact maps: Residue-level nodes, edges defined by predicted Cβ-Cβ distances <8Å, edge weights informed by predicted aligned error (PAE). GNN message passing produces a residue-level structural embedding.
Mutation-site local structure descriptors: For each somatic missense mutation, a local structural fingerprint (secondary structure context, solvent accessibility, interface burial, B-factor proxy from pLDDT) is extracted as a fixed-length feature vector.
Interface buried surface area (BSA) delta: The change in predicted buried surface area at known interaction interfaces between wildtype and mutant — a continuous measure of interface disruption severity.

These structural features are concatenated with the SeNMo/DeePathNet multi-omics embeddings and the Evo sequence embeddings, with Kronecker product terms computed between structural interface disruption scores and AlphaGenome's predicted TF binding changes — capturing the interaction between protein structural alterations and their downstream regulatory consequences.
Output: Protein structure embeddings encoding the 3D structural consequences of somatic missense mutations, protein-protein and protein-drug interaction interface alterations, and predicted drug binding affinities — providing mechanistic interpretability beyond sequence-level mutation annotations.

2.5  Histopathology — Whole-Slide Image Encoding
Foundation Models: MUSK · UNI / UNI2-h · Giga-Path · Virchow · CONCH · PLIP
Specific Inputs:

Haematoxylin and eosin (H&E) stained whole-slide images (WSIs; 20× or 40× magnification; typically 50,000 × 50,000+ pixels)
Immunohistochemistry (IHC) slides: AR, PSA (KLK3), Ki-67 (proliferation), p53, ERG, PTEN (IHC score semi-quantitative: 0–3+), CD8, CD163 (TME immune infiltration)
Pathologist-annotated regions of interest (ROIs): tumour vs. stroma vs. benign glands
Gleason pattern annotations (primary and secondary patterns 3–5)
Cribriform architecture presence/absence (independent adverse prognostic factor)
Perineural invasion, lymphovascular invasion, extraprostatic extension annotations

Encoding Approach:
WSIs are tessellated into non-overlapping patches (typically 256×256 or 512×512 pixels at 20× magnification). The primary encoder is MUSK (Multimodal transformer with Unified maSKed modelling), a vision-language foundation model pretrained on 50 million pathology image patches from 11,577 patients using masked image modelling and contrastive learning against one billion paired pathology report text tokens. The joint image-text pretraining is critical: it grounds visual features in clinical semantics, allowing the model to associate cribriform glandular architecture with the linguistic concept of "Gleason pattern 4" without explicit pixel-level labelling.
Slide-level aggregation uses attention-based multiple instance learning (ABMIL), where an attention module learns which patches are most informative for outcome prediction — typically upweighting invasive tumour front, high-grade gland morphology, and immune infiltrate-rich regions.
Alternative and complementary pathology encoders include:

UNI / UNI2-h: A general-purpose computational pathology foundation model trained on 100,000+ WSIs from The Cancer Genome Atlas and other sources, producing highly prognostic patch-level and slide-level vision embeddings. UNI2-h uses a hierarchical ViT architecture enabling multi-scale feature extraction from subcellular resolution to tissue architecture.
Giga-Path: A gigapixel-scale pathology foundation model pretrained on over 1.3 billion pathology image tiles from 171,189 whole slides, using a long-range token attention architecture purpose-built for slide-level reasoning.
Virchow: A pathology foundation model pretrained on 1.5 million H&E WSIs using self-supervised learning, with particular strength in rare histological pattern recognition.
CONCH and PLIP: Vision-language models specifically pretrained on pathology image-caption pairs from social media and medical literature respectively, providing strong zero-shot pathology concept grounding.

Output: A slide-level embedding capturing Gleason grade heterogeneity, spatial TME distribution, morphological growth patterns, and IHC-derived protein expression surrogates.

2.6  Electronic Health Records and Clinical Text
Foundation Models: GatorTron · Med-Gemma · BioMistral-7B · Qwen3 · Llama-3.2
Specific Inputs:

Structured clinical variables: age at diagnosis, PSA at biopsy, PSA density, PSA velocity, clinical T/N/M stage, ISUP grade group (1–5), number of positive biopsy cores, percentage of core involvement, laterality
Pathological staging (post-prostatectomy): pT2–pT4, surgical margin status (R0/R1), lymph node yield and positivity
Treatment history: radical prostatectomy, external beam radiotherapy (EBRT; dose and fractionation), brachytherapy, ADT (LHRH agonist/antagonist, anti-androgen; cumulative duration), docetaxel/cabazitaxel chemotherapy, enzalutamide/abiraterone, PARP inhibitors, 177Lu-PSMA therapy
PSA response kinetics post-treatment: PSA nadir, time to PSA recurrence, PSA doubling time (PSADT)
Comorbidities (Charlson Comorbidity Index), ECOG performance status
Unstructured text: biopsy pathology reports, radiology reports (mpMRI PI-RADS scores, PSMA-PET findings), clinical encounter notes, MDT meeting summaries

Encoding Approach:
Unstructured clinical narratives are tokenised and encoded using medical domain-adapted large language models. GatorTron (a 8.9B parameter clinical encoder pretrained on 90 billion words of de-identified clinical text from the University of Florida Health system) and Med-Gemma (Google's medically adapted Gemma model) provide strong biomedical named entity recognition and clinical concept extraction. BioMistral-7B offers a lightweight, open-weight alternative pretrained on PubMed and clinical corpora, suitable for on-premise deployment under data governance constraints. General-purpose frontier models Qwen3 and Llama-3.2 have demonstrated exceptional clinical text semantic understanding and are used where instruction-following and multi-step clinical reasoning over long EHR documents is required.
Structured variables are embedded through learned numeric and categorical embeddings before concatenation with the text-derived representation. Temporal treatment sequences (e.g., ADT → EBRT → enzalutamide → progression) are encoded with positional embeddings to preserve treatment order information.
Output: A clinical embedding encoding disease burden at diagnosis, treatment exposure history, PSA kinetics, and pathological staging — the contextual backbone against which molecular signals are interpreted.

3. Multimodal Fusion Core — HONeYBEE Architecture and Rationale
Framework: HONeYBEE (Harmonized ONcologY Biomedical Embedding Encoder)
The HONeYBEE framework is responsible for harmonising the modality-specific embeddings from Evo, AlphaGenome, MutationProjector, AlphaFold2/3, scGPT/Geneformer/UCE, SeNMo/DeePathNet/mosGraphGPT, MUSK/UNI, and the clinical LLMs into a single, patient-level representation. This is non-trivial: the embeddings are heterogeneous in dimensionality, statistical distribution, information density, and biological scale. The fusion strategy must be (a) robust to missing modalities, (b) capable of modelling cross-modal interactions, and (c) computationally tractable at clinical scale.
3.1  Embedding Standardisation
Before fusion, each modality embedding is independently projected to a common dimensionality d via a modality-specific linear projection layer followed by layer normalisation. This standardisation step aligns the statistical distributions of embeddings without destroying modality-specific structure. It also serves as a dimensionality reduction step: genomic embeddings may be high-dimensional (d_genome >> d_fusion), and projection prevents any single modality from dominating the fused representation by sheer vector size.
3.2  Missing Modality Handling
Real prostate cancer cohorts are frequently incomplete. TCGA-PRAD has bulk RNA-Seq and WGS for most patients but lacks matched single-cell data and proteomics for many. CPTAC-Prostate has deep proteomics but limited scRNA-Seq. Clinical-only datasets may lack any molecular profiling.
The fusion core handles this via a masking-and-imputation strategy:

Observed modalities contribute their full standardised embedding.
Missing modalities are replaced by a learned modality-specific "missing" token — a trainable vector initialised to the training-set mean embedding for that modality. This allows the attention-based fusion module to learn appropriate downweighting of imputed signals.
Modality availability mask is passed explicitly to the fusion transformer, allowing it to condition its attention patterns on which data streams are observed versus imputed.

This is preferable to naive mean imputation because the model explicitly learns how to adjust its cross-modal reasoning when information is absent — rather than silently treating an imputed embedding as observed.
3.3  Pairwise Cross-Modal Interaction Modelling — Kronecker Product Fusion
The dominant failure mode of concatenation-based fusion is that it treats modality embeddings as statistically independent. Biologically, they are not: methylation-driven silencing of PTEN (epigenome layer) is mechanistically linked to AKT phosphorylation (proteome layer) and downstream transcriptional activation of cell cycle genes (transcriptome layer). Capturing these dependencies requires explicit cross-modal interaction terms.
The Kronecker product of two embedding vectors u ∈ ℝ^p and v ∈ ℝ^q produces a pairwise interaction tensor u ⊗ v ∈ ℝ^(p×q), where every element (i,j) encodes the product u_i · v_j — i.e., the co-activation of feature i from modality A with feature j from modality B. In practice, this tensor is projected back to a lower-dimensional space to prevent combinatorial explosion.
Applied to multi-omics pairs (e.g., genomic embedding × methylation embedding, or proteomic embedding × transcriptomic embedding), the Kronecker product explicitly parameterises cross-modal feature interactions: the model can learn, for instance, that high AR pathway activity (transcriptome) combined with AR gene amplification (genome) predicts a qualitatively different phenotype than either signal alone — a biologically well-established non-linear interaction that additive models miss.
Kronecker fusion is applied selectively to modality pairs with known mechanistic coupling:

Genome (Evo) × Methylome (SeNMo methylation channel) — driver mutation × epigenetic silencing
AlphaGenome regulatory features × Evo structural variant embedding — TAD boundary disruption × novel TF binding site creation
Transcriptome (SeNMo RNA channel) × Proteome (SeNMo protein channel) — mRNA abundance × protein abundance, capturing translational regulation and PTM
AlphaFold3 structural interface disruption scores × AlphaGenome predicted TF occupancy — protein structural alteration × downstream regulatory consequence
scRNA TME embedding (scGPT/Geneformer) × Histopathology embedding (MUSK/UNI) — cellular composition × spatial tissue architecture
MutationProjector graph embedding × DeePathNet pathway activation — genotype × phenotype

3.4  Hierarchical Attention-Based Fusion
After pairwise interaction terms are computed, all modality embeddings (observed, imputed, and pairwise Kronecker terms) are assembled into a sequence and processed by a multi-head cross-modal attention transformer. Each modality embedding is treated as a "token"; attention heads learn to route information selectively between tokens.
This architecture has two key properties:

Modality importance weighting: Attention scores across modality tokens are interpretable as learned importance weights. In patients with high-quality WGS and proteomics but poor-quality scRNA-Seq (low cell counts), the model learns to downweight the single-cell token — analogous to a clinician discounting a low-quality biopsy result.
Higher-order interactions: While Kronecker products capture pairwise interactions, the transformer can capture higher-order dependencies through its stacked attention layers — for instance, three-way interactions between genomic driver mutation, methylation state, and immune infiltration.

3.5  Fusion Fallback Strategies
For patient cohorts where only one or two modalities are available (e.g., clinical-only records), the fusion core degrades gracefully:

Concatenation: Standardised embeddings are concatenated directly. Trivially parallelisable and robust, though blind to cross-modal interactions.
Mean pooling: Embeddings are averaged element-wise. Appropriate when modalities are of similar quality and dimensionality; naturally downweights any single outlier modality.
Single-modality passthrough: When only clinical data is available, the clinical embedding passes directly to the prediction head without fusion. The model remains deployable in low-resource settings.

The appropriate strategy is selected at inference time based on the observed modality availability mask.
3.6  Patient-Level Representation
The output of the fusion transformer is a single, unified patient-level embedding of dimension d_patient. This vector encodes the joint molecular and clinical state of the patient across all observed data modalities, with cross-modal interaction terms explicitly represented. It serves as the input to all downstream prediction heads.

4. Prediction Heads
4.1  Survival Analysis
The primary clinical endpoint is biochemical recurrence-free survival (bRFS) and overall survival (OS). Two complementary approaches are used:

Cox Proportional Hazards (CoxPH) with deep embedding input: The patient-level embedding replaces hand-crafted covariates as input to the partial likelihood function. This preserves the statistical framework familiar to clinical researchers while allowing the embedding to capture non-linear covariate interactions.
Random Survival Forest (RSF): A non-parametric ensemble method that makes no proportional hazards assumption — appropriate when treatment heterogeneity violates the CoxPH proportionality condition.

Performance is evaluated by Harrell's concordance index (C-index), integrated Brier score, and time-dependent AUC at 5, 10, and 15 years.
4.2  Treatment Response Prediction
Binary and multi-class classifiers predict PSA response to ADT, response to PARP inhibitor therapy (stratified by HRD status), and eligibility for 177Lu-PSMA based on PSMA expression surrogates derived from the multi-omics embedding.
4.3  Molecular Subtype Classification
The fused embedding is used to classify patients into established molecular subtypes — ETS-fusion positive vs. negative, SPOP-mutant, IDH-mutant (rare), CHD1-deleted, NEPC (neuroendocrine) — and into novel data-driven subtypes identified by unsupervised clustering of the patient-level embedding space.

5. Training, Validation, and Generalisation Strategy
5.1  Primary Training Cohort — TCGA-PRAD
The primary training dataset is the TCGA Prostate Adenocarcinoma (TCGA-PRAD) cohort: 499 patients with matched WGS, RNA-Seq, DNA methylation (450K array), miRNA, RPPA proteomics, copy number, somatic mutation calls, and clinical outcome data. Survival endpoints are supplemented with curated biochemical recurrence data from linked clinical records.
5.2  Internal Validation
Stratified k-fold cross-validation (k=5) with stratification by ISUP grade group, age quartile, self-reported race/ethnicity, and vital status ensures balanced outcome representation across folds. Model selection uses the validation C-index; hyperparameter optimisation is performed via Bayesian search within training folds only.
5.3  External Validation — CPTAC-Prostate
Independent external validation uses the CPTAC (Clinical Proteomic Tumor Analysis Consortium) Prostate cohort, which provides deep proteomics and phosphoproteomics not available in TCGA, enabling assessment of multi-omics generalisation. Additional validation cohorts from institutional biobanks (where IRB-approved and data sharing agreements permit) provide geographic and demographic diversity.
5.4  Subgroup Analyses
Pre-specified subgroup analyses assess performance in: (a) Black patients (who are systematically underrepresented in genomic cancer cohorts and experience disproportionate disease burden), (b) patients with metastatic castration-sensitive disease, (c) patients with HRD signatures (a clinically actionable predictive biomarker), and (d) patients managed with active surveillance.

6. Technical Glossary
AlphaFold2 / AlphaFold3 (Google DeepMind): Deep learning models for protein structure prediction. AlphaFold2 uses an Evoformer architecture to predict high-accuracy 3D coordinates for single protein chains from sequence and MSA inputs. AlphaFold3 extends this to full molecular complexes — protein-protein, protein-DNA, protein-RNA, and protein-ligand — using a diffusion-based structure generation module, enabling prediction of drug binding poses and transcription factor-DNA interactions.
AlphaGenome (Google DeepMind): A sequence-to-function foundation model that predicts a comprehensive range of regulatory genomic outputs (chromatin accessibility, TF binding, histone modifications, gene expression, splicing, 3D genome contact maps) at base-pair resolution directly from DNA sequence. Complements sequence-embedding models like Evo by providing explicit, biologically annotated regulatory predictions rather than implicit sequence embeddings.
Attention Mechanism: A learned weighting function that assigns differential importance to elements of an input sequence or set. In transformers, each element attends to all others via scaled dot-product similarity, enabling the model to focus on the most contextually relevant features.
Cancer-Associated Fibroblast (CAF): Stromal fibroblasts reprogrammed by tumour-secreted signals. myCAF subtypes (αSMA+) are spatially proximate to tumour cells and promote invasion; iCAF subtypes are more distal and secrete pro-inflammatory cytokines.
Concordance Index (C-index): The probability that, for two randomly selected patients, the patient with the higher predicted risk score has the shorter survival time. Analogous to the AUC for survival data; 0.5 = random, 1.0 = perfect.
DeePathNet: An explainable transformer-based deep learning model that projects multi-omic data into 241 literature-curated cancer pathways, then models inter-pathway dependencies via multi-head self-attention. Provides biologically interpretable embeddings directly mappable to therapeutic targets.
Embedding: A real-valued vector representation of a complex input object (DNA sequence, cell profile, image) learned by a neural network such that semantically or biologically similar inputs map to nearby points in the embedding space.
Evo: A 7-billion parameter genomic foundation model built on the StripedHyena architecture, trained on 300 billion nucleotides. Operates at single-nucleotide resolution with a 131 kb context window.
Foundation Model: A large-scale neural network pretrained on broad domain data (e.g., all sequenced genomes, all available single-cell transcriptomes) using self-supervised objectives, then fine-tuned or prompted for specific downstream tasks. Pretraining confers generalised biological representations that transfer with limited task-specific labelled data.
Geneformer: A transformer foundation model pretrained on 30 million single-cell transcriptomes and continually pretrained on 14 million cancer transcriptomes, using rank-based gene tokenisation and masked gene modelling.
Graph Attention Network (GAT): A neural network architecture operating on graph-structured data where nodes aggregate information from neighbours with learned, context-dependent attention weights — allowing the model to learn which biological interactions are most relevant for a given prediction task.
HONeYBEE: The Harmonized ONcologY Biomedical Embedding Encoder — the multimodal fusion framework that harmonises embeddings from all modality-specific foundation models into a unified patient-level representation using concatenation, mean pooling, Kronecker product pairwise interaction terms, and cross-modal transformer attention.
Homologous Recombination Deficiency (HRD): A DNA repair defect resulting from biallelic inactivation of BRCA2, BRCA1, ATM, CDK12, or related HR pathway genes. HRD tumours exhibit a characteristic genomic scar (large-scale state transitions, telomeric allelic imbalance) and sensitivity to PARP inhibitors and platinum chemotherapy.
Kronecker Product: For vectors u ∈ ℝ^p and v ∈ ℝ^q, u ⊗ v ∈ ℝ^(pq) encodes all pairwise products between elements of u and v. In multi-omics fusion, this explicitly parameterises multiplicative (non-additive) interactions between features from different data modalities.
mosGraphGPT: A generative AI foundation model integrating multi-omic data through multi-level signalling graphs; capable of imputing missing omic modalities at inference time via generative pretraining.
MUSK: Multimodal transformer with Unified maSKed modelling — a vision-language pathology foundation model pretrained on 50 million pathology images and one billion text tokens using masked data modelling and contrastive learning.
MutationProjector: A foundation model that translates tumour mutation profiles into cancer subtype representations using Graph Attention Networks broadcasting mutations across eight molecular interaction networks.
scGPT: A single-cell foundation model pretrained on 33 million human single-cell transcriptomes using masked gene modelling; enables zero-shot cell type annotation and gene regulatory network inference.
SELU (Scaled Exponential Linear Unit): An activation function with self-normalising properties — under Lecun normal weight initialisation, activations converge to mean 0, variance 1 across layers without batch normalisation. Critical for stable training of deep networks on small multi-omics datasets.
SeNMo: Self-Normalizing Deep Learning Model for Multi-Omics — uses SELU activations and Alpha-Dropout to process high-dimensional, low-sample-size multi-omics data (gene expression, DNA methylation, miRNA, proteomics) in a single forward pass without overfitting.
Tumour Microenvironment (TME): The non-malignant cellular and acellular components of a tumour, including immune cells (TILs, TAMs, MDSCs, NK cells), fibroblasts, endothelial cells, and extracellular matrix. TME composition is a major determinant of treatment response and immune evasion.
UCE (Universal Cell Embedding): A single-cell foundation model producing cross-tissue, cross-species generalisable cell embeddings by grounding gene representations in protein sequence space. Enables transfer from single-cell to bulk RNA-Seq contexts.
UNI / UNI2-h: General-purpose computational pathology foundation models trained on 100,000+ whole-slide images. UNI2-h uses a hierarchical ViT architecture for multi-scale feature extraction from subcellular to tissue-architecture resolution.
Vision-Language Model: A neural network jointly trained on paired image and text data using contrastive or masked modelling objectives. In pathology, pretraining on WSI patches paired with pathology report text grounds visual representations in clinical semantic space.

Technical questions regarding model architecture, hyperparameter configurations, training schedules, and dataset access agreements should be directed to the bioinformatics and machine learning teams. This document reflects the framework as of April 2026.
