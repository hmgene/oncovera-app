# Multi-omics AI Bioinformatics Role Summary

## 1. Multi-omics system designer
You design how fragmented biological data becomes one coherent system:

- Genomics (WGS/WES, CNV)  
- Transcriptomics (bulk, single-cell)  
- Epigenomics (ATAC, methylation, HiChIP)  
- Proteomics / spatial biology  
- cfDNA / fragmentomics / liquid biopsy  
- Clinical longitudinal outcomes  

👉 Core question:
**“What is the correct joint representation of disease across modalities?”**

Not separate datasets — but a unified structure of disease states.

---

## 2. AI disease-profile model developer (core identity)

You build **patient-level biological state embeddings**, not just features:

- Latent disease-state vectors (progression, AR dependence, etc.)
- Trajectory models (disease evolution over time)
- Interpretable factor models (NMF, VAE, graph-based states)
- cfDNA → tissue state mapping models
- Multimodal fusion (early, late, hierarchical)

👉 Output is not genes  
👉 Output is a **disease state**, e.g.:

> “Plasticity-transition, AR-independent, immune-excluded, DDR-high state with rising metastatic risk”

---

## 3. Translational AI layer (biology → clinical action)

You operate between discovery and decision-making:

- Omics signals → biological mechanisms
- Mechanisms → patient risk states
- States → treatment response probabilities

👉 Core function:
**Convert molecular measurements into clinical stratification models**

---

## 4. Biomarker-to-system builder

You do not only find biomarkers — you structure them:

- Classify biomarkers:
  - prognostic
  - predictive
  - resistance-associated
  - liquid surrogate of tissue state
- Build biomarker networks (not lists)
- Define state transitions they represent

Example mappings:
- EZH2 ↑ → plasticity transition axis  
- AR-V7 ↑ → ligand-independent AR axis  
- CNV 8q gain → genomic instability axis  

---

## 5. Multi-modal AI infrastructure engineer

You design the computational backbone:

- Cross-assay feature harmonization
- Batch correction vs biological signal separation
- Graph-based patient trajectory models
- Longitudinal/time-aware modeling
- Uncertainty-aware prediction systems

👉 Essentially building:
**foundation models for cancer progression**

---

## 6. Liquid biopsy + spatial bridging specialist

You connect tissue and blood biology:

- Spatial tissue state (ground truth)
  → cfDNA / EV / CTC signals (observables)

You answer:
**“What part of tumor biology is detectable in blood, and when?”**

👉 This is core translational value, not secondary analysis.

---

# 🧭 One-line definition

You are a **multi-omics systems modeler** who builds AI representations of cancer as evolving biological states and translates them into clinically actionable patient trajectories using both tissue and liquid biopsy data.

---

# ⚙️ Interview-ready version

> “I build multi-omics AI models that integrate genomic, epigenomic, spatial, and liquid biopsy data into interpretable disease-state trajectories for cancer progression and treatment response prediction.”
