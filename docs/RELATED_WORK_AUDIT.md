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
