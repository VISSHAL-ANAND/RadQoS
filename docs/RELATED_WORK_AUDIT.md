# Related-Work Audit for the Manuscript

Status: initial literature audit on 2026-10-29. This is a targeted starting set, not an exhaustive systematic review. Recheck metadata and expand before claiming novelty.

## Findings that constrain the novelty claim

### 1. Lung-region / ROI-aware JPEG 2000 is established prior art
Odry et al. studied 3D region-based JPEG 2000 compression using segmented lungs as regions of interest and evaluated downstream lung-nodule detection. This directly establishes that lung-region-aware JPEG 2000 is not itself a new concept.
- B. L. Odry et al., “The effects of 3D region-based compression on the performance of an automatic lung nodule detection system,” Proc. SPIE, 2005. DOI: https://doi.org/10.1117/12.595475

Kim et al. evaluated regional compression artifacts in low-dose chest CT, comparing lung and chest-wall/mediastinal regions using radiologist ratings, PSNR, and a perceptual metric. This is especially relevant because it demonstrates that mathematical error and perceptual/reader judgments can disagree across anatomical regions.
- K. J. Kim et al., “Regional Difference in Compression Artifacts in Low-Dose Chest CT Images: Effects of Mathematical and Perceptual Factors,” American Journal of Roentgenology. DOI: https://doi.org/10.2214/AJR.07.3462

### 2. Medical-image compression needs task-specific validation
Koff et al. report a multi-modality, multi-anatomical-region evaluation of JPEG and JPEG 2000 using objective and reader-oriented criteria. Their work cautions against presenting one universal compression threshold as clinically safe.
- D. Koff et al., “Pan-Canadian Evaluation of Irreversible Compression Ratios (‘Lossy’ Compression) for Development of National Guidelines,” Journal of Digital Imaging, 22(6), 569–578, 2009. DOI: https://doi.org/10.1007/s10278-008-9139-7

Kowalik-Urbaniak et al. compare objective quality metrics against radiologist assessments in work on “diagnostically lossless” compression. The manuscript should use this literature to justify why PSNR/SSIM are engineering metrics here, not evidence of diagnostic acceptability.
- I. Kowalik-Urbaniak et al., “The quest for ‘diagnostically lossless’ medical image compression: A comparative study of objective quality metrics for compressed medical images,” SPIE Medical Imaging, 2014. Source: https://www.ece.uwaterloo.ca/~z70wang/publications/spie14.pdf

### 3. Network-aware medical image transmission and JPIP predate this study
Prior work has explored context-aware wireless medical-image/video transmission and JPEG 2000 Interactive Protocol (JPIP) streaming. The current code does not implement JPIP or a standards-compliant progressive JPEG 2000 codestream. The manuscript must not imply that bandwidth adaptation, progressive image delivery, or ROI coding is new in general.
- C. Doukas and I. Maglogiannis, “Adaptive transmission of medical image and video using scalable coding and context-aware wireless medical networks,” EURASIP Journal on Wireless Communications and Networking, 2008. DOI: https://doi.org/10.1155/2008/428397
- R. Noumeir and J.-F. Pambrun, “Using JPEG 2000 interactive protocol to stream a large image or a large image set,” Journal of Digital Imaging, 24(5), 833–843, 2011. DOI: https://doi.org/10.1007/s10278-010-9343-0

### 4. SSIM and PSNR are not clinical acceptance criteria
SSIM is a widely used structural similarity metric, but medical-image compression literature documents limitations and disagreement between pixel-domain metrics and reader/perceptual assessments. The paper must state that its fifth-percentile regional SSIM and maximum-error thresholds are preselected engineering criteria, not validated clinical thresholds.
- Z. Wang, A. C. Bovik, H. R. Sheikh, and E. P. Simoncelli, “Image quality assessment: From error visibility to structural similarity,” IEEE Transactions on Image Processing, 13(4), 600–612, 2004. DOI: https://doi.org/10.1109/TIP.2003.819861
- J.-F. Pambrun and R. Noumeir, “Limitations of the SSIM quality metric in the context of diagnostic imaging,” Proc. IEEE ICIP, 2015. DOI: https://doi.org/10.1109/ICIP.2015.7351345

### 5. Dataset description and provenance
The dataset paper reports 138 Montgomery County frontal chest radiographs, 80 normal and 58 with TB manifestations, at dimensions 4020×4892 or 4892×4020, and describes the original PNGs as 12-bit grayscale. The project’s provenance audit reports that the public NLM PNG headers currently inspected are 8-bit grayscale. This discrepancy must be described as a difference between the publication's description and the actual files analyzed, not silently “resolved” by assuming one representation is the original.
- S. Jaeger et al., “Two public chest X-ray datasets for computer-aided screening of pulmonary diseases,” Quantitative Imaging in Medicine and Surgery, 4(6), 475–477, 2014. https://qims.amegroups.org/article/view/5132/html
- S. Jaeger et al., “Automatic tuberculosis screening using chest radiographs,” IEEE Transactions on Medical Imaging, 33(2), 233–245, 2014. DOI: https://doi.org/10.1109/TMI.2013.2284099
- Official NLM source directory: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/
- Current mirror dataset card: https://huggingface.co/datasets/Famatsu123/montgomery-shenzhen-tuberculosis-cxr


### 6. More recent work makes broad novelty claims especially risky
Recent literature includes region-aware compression of chest CT, diagnosis-oriented learned medical-image compression, and reviews of JPEG/JPEG 2000 effects on deep-learning pipelines. These are not necessarily direct apples-to-apples baselines for the current hand-designed 8-bit CXR selector, but they show that “adaptive medical image compression” and “diagnosis-oriented compression” are active, established topics.

- Y. Zhang, Z. Cai, and B. Ye, “An Image Importance Partition-Based Compression Method for COVID-19 Computed Tomography Scan,” IEEE Transactions on Industrial Informatics, vol. 18, no. 7, pp. 4596–4607, July 2022. DOI: https://doi.org/10.1109/TII.2021.3117258. This work extracts bilateral lung contours and adapts CT coding/quantization by image region.
- G. Xie, X. S. Li, X. Pan, and Z. Chen, “Diagnosis-oriented Medical Image Compression with Efficient Transfer Learning,” IEEE International Conference on Visual Communications and Image Processing (VCIP), 2023. DOI: https://doi.org/10.1109/VCIP59821.2023.10402638. This work optimizes compression with a downstream medical task in view, using coronary-artery segmentation as its evaluation task.
- I. A. Urbaniak, “Using Compressed JPEG and JPEG2000 Medical Images in Deep Learning: A Review,” Applied Sciences, 14(22), 10524, 2024. https://doi.org/10.3390/app142210524. Use it as a review map, then verify primary studies directly.
- U. P. Srivastava and T. Fujii, “Region of Interest based Medical Image Compression,” arXiv:2501.02895, 2025. https://doi.org/10.48550/arXiv.2501.02895. This is a preprint, not evidence of peer-reviewed acceptance; treat accordingly.
- “Lung Image Segmentation and Compression Using Deep Learning,” IEEE Xplore document 10743495. https://ieeexplore.ieee.org/document/10743495. Retrieve full metadata and read the paper before deciding how directly it overlaps.

## Revised novelty risk
**Risk level: high for a claim of a new adaptive/ROI compression method; moderate-to-high even for an empirical benchmark.** ROI-aware JPEG 2000, lung-region compression, and network-aware medical-image delivery are prior art. The likely defensible contribution is a carefully reproducible evaluation protocol and empirical result on a specific public 8-bit CXR representation—not a novel codec. To make the study competitive, the paper may need (a) corrected full-set evidence, (b) stronger or newer directly relevant baselines, (c) a justified sensitivity analysis, and (d) a clear explanation of why the chosen regional metric adds value beyond prior ROI coding. The target venue's standards determine whether this scope is sufficient.

## Prior-work comparison for the manuscript

| Work | Established contribution | Relevance to this study | Necessary distinction |
|---|---|---|---|
| Odry et al. (2005) | 3D region-based JPEG 2000 using segmented lung regions; evaluates downstream lung-nodule detection | Lung ROI and JPEG 2000 are established | Current P1 does not allocate different bit rates to ROI/background; it selects a whole-image codestream using an ROI-derived metric |
| Kim et al. (2008) | Regional compression-artifact evaluation in low-dose chest CT, including perceptual/reader considerations | Shows that anatomical-region distortions and objective metrics require care | Current work has no radiologist reader study or CT images |
| Koff et al. (2009) | Multi-modality, multi-region lossy-compression evaluation with diagnostic criteria | Supports careful compression-quality claims and task-specific validation | Current work reports engineering metrics and simulated delivery only |
| Doukas & Maglogiannis (2008) | Scalable, context-aware wireless medical-image/video transmission | Adaptive/network-aware transmission is prior art | Current work is a simple offline candidate selector and simulated link model |
| Noumeir & Pambrun (2011) | JPEG 2000 Interactive Protocol streaming of large images/sets | Standardized interactive delivery is prior art | Current P2 is not JPIP and not a standards-compliant progressive codestream |
| Zhang et al. (2022) | Importance-partition compression for COVID-19 chest CT with lung contours and region-dependent coding | Direct overlap with lung-region-aware compression | Current study uses Montgomery CXR and a global candidate codestream constrained by regional metrics |
| Xie et al. (2023) | Diagnosis-oriented learned compression with transfer learning and a downstream segmentation task | Directly relevant to task-oriented medical compression | Current work does not train a codec or evaluate diagnostic-task accuracy |
| Urbaniak (2024) | Review of compressed JPEG/JPEG 2000 images in deep-learning pipelines | Useful map of later studies and downstream effects | Use it to find primary studies; do not cite the review as proof of a specific algorithm's results |
| Pambrun & Noumeir (2015) | Analysis of SSIM limitations in diagnostic imaging | Supports the construct-validity limitation | Current SSIM thresholds are engineering constraints, not clinical thresholds |

### Required dataset/annotation citations and reuse caution
The current NLM dataset page asks users to cite both the dataset description and the annotation paper. Because this study uses the manual lung masks, cite both sources:
- S. Rajaraman, L. R. Folio, J. Dimperio, P. O. Alderson, and S. K. Antani, “Improved Semantic Segmentation of Tuberculosis-Consistent Findings in Chest X-rays Using Augmented Training of Modality-Specific U-Net Models with Weak Localizations,” *Diagnostics*, vol. 11, no. 4, art. 616, 2021. DOI: https://doi.org/10.3390/diagnostics11040616.
- Official NLM dataset description and citation instructions: https://www.lhncbc.nlm.nih.gov/LHC-publications/pubs/TuberculosisChestXrayDatasets.html
- Official NLM readme PDF: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/MontgomerySet/NLM-MontgomeryCXRSet-ReadMe.pdf

The original dataset publication asks users not to share the dataset outside their research group/organization and encourages requests directly to NLM. The project should not re-host or commit the radiographs/masks. Cite the authoritative source, preserve required attribution, and verify the current terms before distributing derived files or source archives. The official page says the source data are de-identified and that use/sharing were reviewed and exempted by the original ethics boards; do not infer that this automatically determines the current authors' local institutional obligations.

## Appropriate contribution framing

Do not claim a new compression codec, new ROI coding paradigm, new progressive JPEG 2000 method, or clinically safe threshold.

A defensible framing—subject to a broader literature review and results—is a reproducible empirical comparison of:
1. an explicitly defined regional objective constraint (5th-percentile grid-region SSIM plus max absolute error),
2. measured candidate-file sizes,
3. a clearly specified deadline simulation,
4. an explicitly custom base-plus-residual strategy,
5. and per-image provenance and paired uncertainty analysis on the Montgomery public 8-bit PNG representation.

Whether this contribution is sufficiently novel for a particular IEEE venue is not established. The target venue's scope and novelty expectations must be checked before submission.

## Additional literature work still required
- Search IEEE Xplore, PubMed/PMC, Scopus/Web of Science or equivalent indexed databases for more recent work on region-aware medical-image compression, deadline-aware image transmission, quality-aware progressive delivery, and task-based quality metrics.
- Check for newer work on adaptive compression using segmentation masks and quality constraints.
- Compare against more directly relevant baselines if the target venue expects algorithmic novelty.
- Verify all bibliographic metadata, page ranges, issue numbers, publication years, and DOIs from publisher/primary sources.
- Do not cite a source solely because a search engine returned it; read and verify the relevant claim.
