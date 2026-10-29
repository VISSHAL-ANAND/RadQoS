# Quality-Constrained and Deadline-Aware Compression of Chest Radiographs: A Reproducible Evaluation on the Montgomery County Dataset

**Status: author-review manuscript draft. Not a final submission PDF.**

**Author(s): [CONFIRM NAMES]**  
**Affiliation(s): [CONFIRM INSTITUTION(S)]**  
**Corresponding author: [CONFIRM EMAIL]**

## Abstract
Medical-image delivery over constrained networks requires balancing encoded payload, reconstruction quality, and the probability of completing transmission before a deadline. This study evaluates fixed compression baselines, a global structural-similarity-constrained selector, a lung-region-constrained selector, and a custom base-plus-residual representation using 138 Montgomery County chest radiographs in the publicly distributed 8-bit grayscale representation. The benchmark measures actual encoded bytes, peak signal-to-noise ratio (PSNR), global structural similarity (SSIM), a fifth-percentile regional SSIM statistic computed over lung-mask regions, maximum absolute error, and delivery outcomes under three simulated bandwidth profiles with a 20-s deadline. A separate lossless JPEG 2000 baseline verifies exact reconstruction of the normalized 8-bit inputs. The regional selector averaged 208.61 KiB per image, compared with 170.35 KiB for the global-SSIM selector; mean PSNR was 0.28885 dB higher and mean regional SSIM was 0.0036968 higher. The paired mean payload increase was 39,177.93 bytes (95% paired bootstrap confidence interval [26,095.46, 52,839.50]). Under the poor simulated profile, full-delivery miss rates were 24.64% for the regional selector and 14.49% for the global selector; both had 0% misses under the good profile. The custom base-plus-residual representation frequently failed to deliver the complete representation by the deadline. Results are limited to the public 8-bit representation and the stated simulation. Objective image metrics do not establish diagnostic safety, accuracy, or clinical equivalence.

**Index Terms—** medical image compression, chest radiography, JPEG 2000, structural similarity, region of interest, deadline-aware transmission, reproducibility.

## I. Introduction
Large medical images can be costly to transmit over constrained networks. Compression reduces payload size, but reconstruction error depends on the image, codec, and operating point. A nominal compression ratio alone does not describe the quality of the reconstruction or whether the representation arrives before an operational deadline. This motivates evaluating measured encoded size, objective image-quality metrics, and delivery outcomes together.

The Montgomery County chest-radiograph collection has been used in computer-aided screening research and includes 138 frontal radiographs and manually generated left/right lung masks [1], [2], [9]. These masks allow quality statistics focused on the lung region rather than relying only on a whole-image average. Such regional statistics are engineering choices, not validated diagnostic acceptance criteria. Structural similarity (SSIM) has documented limitations in diagnostic imaging, including sensitivity to pooling and local image characteristics [5].

This work evaluates specified candidate-selection rules rather than proposing a new image transform or claiming that adaptive compression or network-aware delivery is itself novel. It compares fixed JPEG and JPEG 2000 operating points with a selector constrained by global mean SSIM, a selector constrained by a regional lung-mask statistic and maximum pixel error, and a custom JPEG 2000 base plus separately compressed residual. Delivery behavior is evaluated under explicit simulated bandwidth profiles. A standalone lossless JPEG 2000 baseline quantifies the payload cost of exact reconstruction in the normalized 8-bit domain.

The research questions are: (1) how does a regional lung-mask constraint change the measured payload–quality trade-off relative to a global mean-SSIM constraint? (2) how do methods compare in full-delivery misses and objective-quality-bound success under simulated deadlines? and (3) what are the payload and delivery limitations of the base-plus-residual representation?

## II. Related Work
Jaeger et al. introduced the Montgomery County and Shenzhen chest radiograph datasets for computer-aided screening research [1], [2]. Candemir et al. described lung segmentation in chest radiographs using anatomical atlases and nonrigid registration [9]. These resources support reproducible algorithmic research but do not establish that compressed images are suitable for clinical decisions.

Liu et al. reviewed the role of image-compression standards in medical imaging [3]. JPEG 2000 supports interactive access mechanisms, and Noumeir and Pambrun studied the JPEG 2000 interactive protocol for streaming large images and image sets [12]. This study does not implement JPIP; it measures encoded representations and evaluates a simplified deadline model.

Wang et al. introduced SSIM as a structural image-quality measure [4]. However, SSIM should not be treated as a clinical acceptance test. Pambrun and Noumeir described limitations of SSIM in diagnostic-imaging contexts, including uniform pooling and distortions that may be underestimated in particular image regions [5]. This motivates reporting both a global statistic and a regional lung-mask statistic while retaining the caveat that neither was clinically validated here.

The contribution is limited to a reproducible comparison of particular candidate-selection rules and a specified delivery simulation on one public 8-bit dataset representation. No broad novelty claim is made for ROI coding, SSIM-constrained selection, or network-aware delivery.

## III. Materials and Methods

### A. Dataset and provenance
The evaluation used 138 frontal radiographs from the Montgomery County collection, described in the dataset literature as 80 normal images and 58 with tuberculosis-related findings, together with left/right lung masks [1], [2], [9]. Images and masks were retrieved at run time and are not committed to the repository. The run manifest records per-image hashes and relevant metadata.

A provenance audit inspected PNG headers for all 138 images in the official National Library of Medicine (NLM) directory. The audited public files were 8-bit grayscale: 97 were 4,892 × 4,020 pixels and 41 were 4,020 × 4,892 pixels. This differs from the original dataset paper's description of 12-bit images. A SHA-256 and byte-count comparison found five examined mirror images and their ten masks byte-identical to corresponding NLM files; this limited comparison does not prove identity of every mirror file. Results therefore apply to the publicly distributed 8-bit representation actually processed. No native 12-bit preservation claim is made.

The official NLM ReadMe requests that users not share the dataset outside their research group or organization and that publications attribute NLM and cite both the tuberculosis-screening and lung-segmentation papers [1], [9], [10]. This manuscript reports aggregate analysis and does not redistribute images or masks. The Hugging Face mirror's licence metadata is “other,” which is not a clear licence grant [11]. NLM also requests acknowledgement as “Courtesy of the U.S. National Library of Medicine” and prohibits implying NLM endorsement [10], [13]. No institutional ethics approval or exemption is claimed; the authors must confirm any institutional or venue-specific declaration before submission.

### B. Methods compared
B1 is fixed JPEG quality 75. B2 is JPEG 2000 with target ratio 20; actual encoded payload was measured rather than assuming the target was achieved. B3 selects the smallest measured JPEG 2000 candidate with global mean SSIM at least 0.95; if no candidate satisfies the bound, the implementation selects the highest-mean-SSIM candidate and reports infeasibility. P1 selects the smallest measured JPEG 2000 candidate with regional SSIM fifth percentile at least 0.95 and maximum absolute pixel error no greater than 24 gray levels. If no lossy candidate satisfies both constraints, the implementation uses lossless JPEG 2000 and records the fallback. P2 selects a JPEG 2000 base using a deadline heuristic and separately encodes a signed pixel residual with zlib. Both components together reconstruct the normalized 8-bit input exactly when received and decoded. P2 is a custom base-plus-residual representation, not a standards-compliant progressive JPEG 2000 codestream.

A separate B0 lossless JPEG 2000 baseline was run independently. Exact reconstruction is defined relative to the normalized 8-bit input, not the original acquisition bit depth. JPEG 2000 candidate settings were 4, 6, 8, 10, 15, 20, 30, 40, 60, 80, and 120. Each candidate was encoded, decoded, and measured.

### C. Metrics and regional statistic
Payload is actual encoded file size in bytes; mean payload is reported in KiB using 1 KiB = 1,024 bytes. Compression ratio is raw normalized 8-bit image bytes divided by encoded payload bytes. PSNR uses a data range of 255. Global SSIM is the mean SSIM-map value over the full image. Maximum absolute error is the largest absolute pixelwise difference between reference and reconstruction. Exact-reconstruction PSNR is capped at 99 dB as a reporting convention.

For the regional statistic, the merged lung mask is divided into an 8 × 8 grid. Cells are eligible when at least 5% of their pixels are covered by the lung mask. Within each eligible cell, the mean SSIM-map value is calculated over lung-mask pixels. The fifth percentile of these eligible-cell means is the regional SSIM statistic. P1 requires this statistic to be at least 0.95 and maximum absolute error to be at most 24. Grid geometry, coverage cutoff, percentile, SSIM bound, and error threshold are engineering parameters, not clinically validated thresholds.

### D. Simulated network
The profiles use mean bandwidths of 128 kbit/s (poor), 512 kbit/s (moderate), and 2 Mbit/s (good), with relative standard-deviation settings of 0.50, 0.40, and 0.30. Latency is fixed at 0.5 s and the deadline at 20 s. Throughput is generated from a lognormal distribution normalized to the configured profile mean. The estimator uses an exponentially weighted update with alpha 0.3. Its conservative lower bound is the larger of the estimated mean minus estimated standard deviation and 10% of the estimated mean. The selection heuristic estimates transfer time using payload and this conservative bandwidth bound; simulated outcomes use sampled throughput and fixed latency.

These are simulation assumptions, not live-network measurements. The model does not fully represent congestion, packet loss, retransmission, protocol overhead, encryption, DICOM transport, or real device behavior. The same per-image/profile throughput draw was used across methods for paired comparisons. The analysis verified identical per-image/profile draws between primary and lossless runs.

### E. Statistical analysis and reproducibility
Continuous paired differences used 2,000 image-level paired bootstrap resamples with seed 42 for percentile 95% confidence intervals and two-sided Wilcoxon signed-rank tests. Binary outcomes used exact two-sided McNemar tests. Holm correction was applied across 19 comparisons in the generated statistical table. Candidate-based threshold sensitivity used existing encoded candidate metrics and did not re-encode images; it is post-hoc descriptive analysis.

The primary full-dataset workflow completed on 138 real images with seed 42, all 11 candidate settings, and synthetic=false. The code commit was b8ead4566b07cf2130a3f06546392c6c739fa44b. The run used Python 3.12.15, NumPy 2.5.4, pandas 3.1.0, Pillow 13.0.0, SciPy 1.18.1, scikit-image 0.26.0, and Hugging Face Hub 2.3.0. The run metadata timestamp was 2026-10-29 14:37:48 UTC.

Expected row counts were 138 manifest rows, 552 quality rows, 1,518 candidate diagnostics, 2,070 delivery rows, 15 summary rows, 10 original paired-comparison rows, and 138 monotonicity diagnostics. The publication-analysis workflow reported 54 checks passed and zero failed. Checks covered tested-key uniqueness, image and mask coverage, positive payloads, metric ranges, P1 constraint satisfaction, zero P1 lossless fallbacks, independent recomputation of summary aggregates, completed logs, and exact reconstruction in the lossless baseline. These checks support numerical reproducibility but do not replace external replication, clinical validation, or legal review.

## IV. Results

### A. Payload and image-quality outcomes

**Table I. Full-set mean payload and quality (n = 138).**

| Method | Mean payload (KiB) | Compression ratio | PSNR (dB) | Global SSIM | Regional SSIM p05 | Maximum absolute error |
|---|---:|---:|---:|---:|---:|---:|
| B1 — JPEG quality 75 | 937.35 | 21.07:1 | 52.4342 | 0.9956348 | 0.9936473 | 33.63 |
| B2 — JPEG 2000 target 20 | 960.16 | 20.00:1 | 50.9420 | 0.9914530 | 0.9876800 | 7.04 |
| B3 — Global SSIM selector | 170.35 | 117.63:1 | 45.7667 | 0.9751190 | 0.9564491 | 17.36 |
| P1 — Regional selector | 208.61 | 105.92:1 | 46.0556 | 0.9770307 | 0.9601459 | 15.68 |

B3 and P1 produced substantially smaller mean payloads than the fixed operating points in this dataset and candidate set. P1's mean payload was 39,177.93 bytes greater than B3's, approximately 23.0% larger relative to B3. P1's mean PSNR was 0.28885 dB higher, global SSIM was 0.0019116 higher, and regional SSIM p05 was 0.0036968 higher. These are measured objective-metric trade-offs, not evidence of clinical superiority.

### B. Paired P1-versus-B3 comparison

| Metric | Mean difference | Median difference | Paired bootstrap 95% CI | Raw p | Holm-adjusted p |
|---|---:|---:|---:|---:|---:|
| Payload | +39,177.93 bytes | 0 bytes | [26,095.46, 52,839.50] bytes | 2.477 × 10⁻⁷ | 2.477 × 10⁻⁶ |
| PSNR | +0.28885 dB | 0 dB | [0.19457, 0.38536] dB | 2.477 × 10⁻⁷ | 2.477 × 10⁻⁶ |
| Global SSIM | +0.0019116 | 0 | [0.001252, 0.002608] | 2.477 × 10⁻⁷ | 2.477 × 10⁻⁶ |
| Regional SSIM p05 | +0.0036968 | 0 | [0.002408, 0.005062] | 2.477 × 10⁻⁷ | 2.477 × 10⁻⁶ |

The zero median paired differences indicate that the positive means do not represent a uniform improvement on every image. Mean effects are concentrated in a subset of cases.

### C. Simulated deadline performance

| Profile | Method | Mean payload (KiB) | Full-delivery miss | Quality bound met by deadline |
|---|---|---:|---:|---:|
| Poor, 128 kbit/s | B3 | 170.35 | 14.49% | 66.67% |
| Poor, 128 kbit/s | P1 | 208.61 | 24.64% | 75.36% |
| Moderate, 512 kbit/s | B3 | 170.35 | 0.72% | 74.64% |
| Moderate, 512 kbit/s | P1 | 208.61 | 0.72% | 99.28% |
| Good, 2 Mbit/s | B3 | 170.35 | 0.00% | 74.64% |
| Good, 2 Mbit/s | P1 | 208.61 | 0.00% | 100.00% |

At poor simulated bandwidth, P1 had a higher full-delivery miss rate than B3, consistent with its larger mean payload. Under moderate and good profiles, P1 met the defined quality bound more frequently. Full-delivery miss and quality-bound success are different outcomes: a representation can arrive but fail the objective bound. All rates use 138 images as the denominator and are simulated, not observed in a live network.

### D. P2 base-plus-residual

| Profile | Mean full payload (KiB) | First-stage miss | Full-representation miss | Quality bound met by deadline |
|---|---:|---:|---:|---:|
| Poor, 128 kbit/s | 5,733.49 | 13.04% | 100.00% | 65.94% |
| Moderate, 512 kbit/s | 5,541.42 | 5.07% | 100.00% | 92.75% |
| Good, 2 Mbit/s | 5,030.19 | 4.35% | 60.14% | 95.65% |

The base may arrive by the deadline without the residual. In that case, the available image is a lossy base rather than an exact reconstruction. Exact reconstruction requires both components. Full-representation misses were 100% under poor and moderate profiles and 60.14% under the good profile. Under the current simulation, this is an unfavorable result for exact delivery using the custom residual representation.

### E. Lossless baseline

| Metric | Result |
|---|---:|
| Mean payload | 3,854,278.043 bytes (3,763.94 KiB) |
| Median payload | 3,801,277.5 bytes |
| Mean ratio versus raw normalized 8-bit pixels | 5.311806:1 |
| Median encode time | 0.699541 s (runner-dependent) |
| Exact reconstructions | 138/138 |
| Full-delivery miss, poor profile | 100.00% |
| Full-delivery miss, moderate profile | 99.28% |
| Full-delivery miss, good profile | 26.09% |

The lossless baseline exactly reconstructed the normalized 8-bit inputs but had substantially larger payloads and high simulated deadline-miss rates at poor and moderate bandwidth. It does not demonstrate preservation of native 12-bit data.

### F. Threshold sensitivity
With the B3 global SSIM threshold set to 0.90, mean payload was 163,747.46 bytes, median payload 163,780.5 bytes, 95th-percentile payload 163,888.6 bytes, mean global SSIM 0.974260, mean regional SSIM p05 0.955154, and mean maximum absolute error 17.67. This post-hoc descriptive analysis did not re-encode images and is not clinical threshold validation.

## V. Discussion
The results show a payload–objective-quality trade-off for the tested selectors on the evaluated 8-bit representation. P1 uses approximately 23% more mean payload than B3 and yields modestly higher mean global and regional similarity values. Since the median paired differences are zero, the mean improvements should not be described as uniform across images.

Deadline results show why quality and delivery reliability should be reported separately. Under the poor profile, the larger P1 payload is associated with a higher miss rate. Under moderate and good profiles, P1 meets the defined quality bound more frequently while full-delivery misses remain low. These outcomes depend on the throughput distributions, estimator, latency, and deadline; they should not be generalized to real deployments without representative network traces or operational testing.

The lossless baseline establishes exact recovery of the normalized 8-bit input, but its payload is much larger. P2 demonstrates that delivering a lossy base is not equivalent to delivering the exact representation: the residual is essential for exact recovery and frequently fails to arrive within the deadline. P2 should be reported as an unfavorable ablation under these settings, not an effective exact-delivery solution.

The regional metric may expose a different objective than whole-image averaging, but the chosen 8 × 8 grid and fifth percentile can still miss small diagnostic features. Maximum pixel error is sensitive to isolated pixels. Neither global nor regional metrics were validated against radiologist judgments, lesion detection, tuberculosis classification, or clinical outcomes.

## VI. Limitations and Conclusion
Limitations include the 8-bit public representation despite the original paper's 12-bit description; a single 138-image dataset; no reader study or downstream diagnostic evaluation; unvalidated regional thresholds; a finite candidate set; simulated rather than live network conditions; and a custom P2 representation that is not standards-compliant progressive JPEG 2000. Statistical significance is limited to the sampled images and simulation and does not imply clinical importance. The mirror's licence metadata is unclear, and source images or masks must not be redistributed.

In conclusion, the quality-constrained selectors substantially reduced mean payload relative to fixed operating points. P1 used approximately 23% more payload than B3 and showed modestly higher mean PSNR, global SSIM, and regional SSIM p05. Under the poor simulated profile, its larger payload was associated with a higher miss rate; under moderate and good profiles, it met the defined objective quality bound more frequently. The lossless baseline exactly reconstructed the normalized 8-bit inputs but incurred a large payload, while P2 frequently failed to deliver its complete representation within the deadline. These findings support an engineering comparison of measured payload, objective metrics, and simulated delivery—not claims of diagnostic safety, equivalence, or clinical suitability.

## Acknowledgment
The final version should include the requested acknowledgment “Courtesy of the U.S. National Library of Medicine” and cite the source dataset and lung-segmentation papers [1], [9], [10]. This acknowledgment does not imply NLM endorsement. Authors must confirm institutional declarations, funding, and other acknowledgements before submission.

## References
[1] S. Jaeger et al., “Automatic tuberculosis screening using chest radiographs,” *IEEE Transactions on Medical Imaging*, vol. 33, no. 2, pp. 233–245, Feb. 2014, doi: 10.1109/TMI.2013.2284099.

[2] S. Jaeger et al., “Two public chest X-ray datasets for computer-aided screening of pulmonary diseases,” *Quantitative Imaging in Medicine and Surgery*, vol. 4, no. 6, pp. 475–477, Dec. 2014, doi: 10.3978/j.issn.2223-4292.2014.11.20.

[3] F. Liu, M. Hernández-Cabronero, V. Sanchez, M. W. Marcellin, and A. Bilgin, “The current role of image compression standards in medical imaging,” *Information*, vol. 8, no. 4, Art. no. 131, 2017, doi: 10.3390/info8040131.

[4] Z. Wang, A. C. Bovik, H. R. Sheikh, and E. P. Simoncelli, “Image quality assessment: From error visibility to structural similarity,” *IEEE Transactions on Image Processing*, vol. 13, no. 4, pp. 600–612, Apr. 2004, doi: 10.1109/TIP.2003.819861.

[5] J.-F. Pambrun and R. Noumeir, “Limitations of the SSIM quality metric in the context of diagnostic imaging,” in *Proc. IEEE International Conference on Image Processing (ICIP)*, pp. 2960–2963, Quebec City, QC, Canada, Sep. 2015, doi: 10.1109/ICIP.2015.7351345.

[6] S. Jaeger et al., “Automatic screening for tuberculosis in chest radiographs: a survey,” *Quantitative Imaging in Medicine and Surgery*, vol. 3, no. 2, pp. 89–99, Apr. 2013, doi: 10.3978/j.issn.2223-4292.2013.04.03.

[7] U.S. National Library of Medicine, “Tuberculosis Chest X-ray Datasets: Montgomery County CXR Set.” [Online]. Available: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/.

[8] Famatsu123, “Montgomery and Shenzhen Tuberculosis Chest X-rays,” *Hugging Face Datasets*. [Online]. Available: https://huggingface.co/datasets/Famatsu123/montgomery-shenzhen-tuberculosis-cxr.

[9] S. Candemir et al., “Lung segmentation in chest radiographs using anatomical atlases with nonrigid registration,” *IEEE Transactions on Medical Imaging*, vol. 33, no. 2, pp. 577–590, Feb. 2014, doi: 10.1109/TMI.2013.2290491.

[10] U.S. National Library of Medicine, “NLM-MontgomeryCXRSet ReadMe,” dataset citation and use instructions. [Online]. Available: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/MontgomerySet/NLM-MontgomeryCXRSet-ReadMe.pdf.

[11] U.S. National Library of Medicine, “National Library of Medicine Terms and Conditions.” [Online]. Available: https://www.nlm.nih.gov/databases/download/terms_and_conditions.html.

[12] R. Noumeir and J.-F. Pambrun, “Using JPEG 2000 interactive protocol to stream a large image or a large image set,” *Journal of Digital Imaging*, vol. 24, no. 5, pp. 833–843, Oct. 2011, doi: 10.1007/s10278-010-9343-0.

## Reproducibility
Repository: https://github.com/VISSHAL-ANAND/research-papper  
Primary full-set run: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40865016332  
Corrected analysis run: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906893245  
Corrected analysis unit tests: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906898568  
Experimental end report: https://github.com/VISSHAL-ANAND/research-papper/blob/main/docs/EXPERIMENTAL_END_REPORT.md

**Release checks not represented as complete:** confirm author and affiliation details, target venue and official template, institutional/funding declarations, venue-specific PDF compliance, final page-by-page PDF inspection, and the actual output of a similarity checker. No similarity score or PDF compliance certificate is claimed.
