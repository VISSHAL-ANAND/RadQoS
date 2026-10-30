# Experimental End Report
## Quality-Constrained and Deadline-Aware Compression of Montgomery County Chest Radiographs

**Status:** Experimental analysis complete (54 checks passed, 0 failed); manuscript prepared outside this repository; similarity check and venue requirements remain pending  
**Report date:** 29 October 2026  
**Repository:** https://github.com/VISSHAL-ANAND/research-papper  
**Primary benchmark commit:** `b8ead4566b07cf2130a3f06546392c6c739fa44b`  
**Primary workflow:** https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40865016332  
**Analysis workflow:** https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906476864  
**Author / affiliation / email:** To be completed by the author; no details are inferred.

> **Evidence note.** The full 138-image primary workflow completed successfully. A separate publication-analysis workflow validated the recorded outputs with 54 checks passed and 0 checks failed. This report uses the recorded outputs and the automated validation report. It does not imply clinical validation. All deadline results are simulated. The public source representation evaluated is 8-bit grayscale, not native 12-bit preservation.

---

## 1. Executive summary

This study evaluates fixed and quality-constrained image compression methods for the Montgomery County chest-radiograph collection. It measures actual encoded payloads and objective reconstruction metrics, then evaluates delivery under three simulated bandwidth profiles with a 20-second deadline. The experiment is intended to make the trade-off between payload size, image similarity, regional image-quality constraints, and deadline success explicit and reproducible.

The primary run evaluated 138 real radiographs. The analysis workflow confirmed the expected row counts: 138 manifest rows, 552 quality rows, 1,518 candidate rows, 2,070 delivery rows, 15 summary rows, 10 original paired-comparison rows, and 138 monotonicity-diagnostic rows. It found no duplicate keys in the tested tables, confirmed that every image had both lung-mask files, verified the P1 constraints and zero P1 lossless fallbacks, independently recomputed summary aggregates, and confirmed that the primary and standalone lossless runs used identical per-image/profile throughput draws. The full quality-control report records 54 passed checks and no failed checks.

The principal recorded payload and quality results are:

- B1, JPEG quality 75: mean payload 937.35 KiB, PSNR 52.43 dB, global SSIM 0.995635.
- B2, JPEG 2000 target ratio 20: mean payload 960.16 KiB, PSNR 50.94 dB, global SSIM 0.991453.
- B3, global mean-SSIM-constrained selection: mean payload 170.35 KiB, PSNR 45.77 dB, global SSIM 0.975119.
- P1, regional-constrained selection: mean payload 208.61 KiB, PSNR 46.06 dB, global SSIM 0.977031.

P1 used approximately 23.0% more payload than B3 on average. In paired analysis, P1-minus-B3 mean payload difference was 39,177.93 bytes (paired bootstrap 95% CI 26,095.46–52,839.50); mean PSNR difference was +0.28885 dB (95% CI 0.19457–0.38536); mean global SSIM difference was +0.001912 (95% CI 0.001252–0.002608); and mean fifth-percentile regional SSIM difference was +0.003697 (95% CI 0.002408–0.005062). These are objective-metric differences, not evidence of clinical superiority.

Under the poor simulated profile (128 kbit/s), B3's recorded full-delivery miss rate was 14.49%, while P1's was 24.64%. Under the moderate (512 kbit/s) and good (2 Mbit/s) profiles, the corresponding B3 and P1 full-delivery miss rates were 0.72% and 0.72%, and 0% and 0%, respectively. The P2 base-plus-residual representation had much larger total payloads and very high full-delivery miss rates: 100% for poor and moderate profiles, and 60.14% for the good profile.

A separate lossless JPEG 2000 baseline reconstructed all 138 evaluated 8-bit inputs exactly, with a mean payload of 3,854,278 bytes (3,763.94 KiB). Its full-delivery miss rates were 100% at 128 kbit/s, 99.28% at 512 kbit/s, and 26.09% at 2 Mbit/s. The lossless baseline is supplemental; its paired delivery comparisons are permitted here because the analysis verified identical image/profile throughput draws.

The findings support a narrow engineering conclusion: within this dataset representation, candidate set, objective metrics, and simulation, the regional-constrained selector trades a larger payload for somewhat higher global and regional similarity metrics. The study does not establish diagnostic accuracy, clinical safety, clinical non-inferiority, or real-world network performance.

## 2. Research objectives and questions

### 2.1 Objective

Evaluate the payload, objective reconstruction quality, and simulated deadline behavior of fixed compression baselines, a global quality-constrained selector, a regional lung-mask-constrained selector, and a custom base-plus-residual representation.

### 2.2 Research questions

1. How does a regional lung-mask quality constraint change the measured payload-quality trade-off relative to a global mean-SSIM constraint?
2. How often does each selected representation arrive before the deadline under poor, moderate, and good simulated bandwidth profiles?
3. What are the payload and delivery limitations of a lossy JPEG 2000 base paired with a separately compressed residual intended to enable exact reconstruction?

### 2.3 Scope

This is a compression and delivery engineering study. It does not evaluate tuberculosis detection, diagnostic accuracy, radiologist agreement, clinical non-inferiority, or patient outcomes. PSNR and SSIM are objective image-quality metrics, not clinical acceptance criteria.

## 3. Dataset and provenance

The benchmark uses the Montgomery County chest X-ray collection, described in the literature as containing 138 frontal radiographs (80 normal and 58 with TB-related findings) and manual left/right lung masks. The workflow downloaded source files at run time and did not commit radiographs or masks to the repository.

The dataset provenance audit reports that all 138 public National Library of Medicine PNG headers inspected are 8-bit grayscale: 97 images are 4,892 × 4,020 pixels and 41 are 4,020 × 4,892 pixels. The original dataset paper describes 12-bit images. A five-image/ten-mask SHA-256 comparison found the examined mirror files byte-identical to the corresponding NLM files. That limited comparison does not establish identity for every mirror file; the primary run manifest retains source hashes.

**Representation limitation:** the results apply to the publicly distributed 8-bit PNG representation actually processed. They do not demonstrate native 12-bit preservation. Any manuscript should state this explicitly.

Sources:
- Official NLM directory: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/
- Public mirror: https://huggingface.co/datasets/Famatsu123/montgomery-shenzhen-tuberculosis-cxr
- Dataset description: https://pmc.ncbi.nlm.nih.gov/articles/PMC4256233/

The mirror lists license metadata as “other,” which is not a clear reuse license. The official NLM dataset ReadMe asks users not to share the dataset outside their research group/organization and requests that publications attribute the National Library of Medicine, National Institutes of Health, Bethesda, MD, USA, and cite both the tuberculosis-screening paper by Jaeger et al. (2014) and the lung-segmentation paper by Candemir et al. (2014). NLM’s general data terms also request the conspicuous acknowledgment “Courtesy of the U.S. National Library of Medicine” and prohibit implying NLM endorsement. This report does not redistribute images or masks. The manuscript should include the requested source attribution and both citations; do not upload or share source images/masks. If any intended use is ambiguous, contact NLM before submission.

## 4. Methods

### 4.1 Methods compared

- **B0 — Standalone lossless JPEG 2000:** a supplemental baseline; exact reconstruction is checked in the normalized 8-bit domain.
- **B1 — JPEG quality 75:** fixed lossy baseline.
- **B2 — JPEG 2000 target ratio 20:** fixed operating point; actual encoded bytes are measured.
- **B3 — Global mean-SSIM-constrained selector:** choose the smallest measured JPEG 2000 candidate with global mean SSIM ≥ 0.95. If no candidate meets the constraint, the documented best-quality fallback is selected and infeasibility should be reported.
- **P1 — Regional-constrained selector:** choose the smallest measured JPEG 2000 candidate with fifth-percentile regional SSIM ≥ 0.95 and maximum absolute error ≤ 24. If no lossy candidate satisfies both conditions, use lossless JPEG 2000 and record the fallback.
- **P2 — Deadline-aware base plus residual:** select a JPEG 2000 base under the deadline heuristic and separately encode a signed pixel residual with zlib. The base and residual together reconstruct the evaluated normalized 8-bit input exactly when both are received and decoded. This is a custom base-plus-residual representation, not a standards-compliant progressive JPEG 2000 codestream.

### 4.2 Candidate set and regional metric

The candidate ratios are 4, 6, 8, 10, 15, 20, 30, 40, 60, 80, and 120. Each candidate is actually encoded and measured; nominal target ratios are not assumed to equal achieved ratios.

For regional SSIM, the merged lung mask is divided into an 8 × 8 grid. Cells are eligible when at least 5% of their pixels are covered by the lung mask. The mean SSIM-map value is computed over lung-mask pixels in each eligible cell; the fifth percentile across eligible cells is the regional statistic. P1 additionally requires maximum absolute pixel error ≤ 24 on the normalized 8-bit scale.

The grid, coverage threshold, percentile, and error threshold are engineering choices. They are not clinically validated thresholds. Changing the grid or percentile requires recalculating the regional metric from image and mask pixels.

### 4.3 Metrics

- **Payload:** actual encoded bytes; mean payload is also reported in KiB (1 KiB = 1,024 bytes).
- **Compression ratio:** raw normalized 8-bit image bytes divided by encoded payload bytes.
- **PSNR:** calculated with an 8-bit data range of 255. Exact reconstruction is capped at 99 dB as a reporting convention.
- **Global SSIM:** mean structural similarity map value across the image.
- **Regional SSIM p05:** fifth percentile of eligible lung-mask cell scores.
- **Maximum absolute error:** maximum pixelwise absolute difference between the normalized 8-bit reference and reconstruction.

None of these metrics alone demonstrates diagnostic safety or clinical equivalence.

### 4.4 Simulated network

The profiles use mean bandwidths of 128,000 bit/s, 512,000 bit/s, and 2,000,000 bit/s, relative standard-deviation settings 0.50, 0.40, and 0.30, fixed latency of 0.5 seconds, and a 20-second deadline. Throughput is sampled from a lognormal distribution normalized to the configured profile mean. A conservative estimate is updated with EWMA alpha 0.3; the lower bound is max(estimated mean − estimated standard deviation, 0.1 × estimated mean).

These are simulation settings, not live-network measurements. The model does not comprehensively represent congestion, packet loss, retransmission, protocol overhead, encryption overhead, or real DICOM/transport behavior. The analysis verified that the primary and lossless baseline used identical per-image/profile sampled throughput values, permitting paired delivery comparisons between those runs.

## 5. Reproducibility and quality-control audit

Primary run:
- Workflow: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40865016332
- Code commit: `b8ead4566b07cf2130a3f06546392c6c739fa44b`
- Run metadata timestamp: 2026-10-29 14:37:48 UTC
- Python 3.12.15; NumPy 2.5.4; pandas 3.1.0; Pillow 13.0.0; SciPy 1.18.1; scikit-image 0.26.0; Hugging Face Hub 2.3.0
- Seed: 42; 138 images; all 11 candidate settings; `MAX_IMAGES=0`; synthetic=false.

Automated analysis:
- Workflow: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906476864
- QC result: 54 checks passed; 0 checks failed.
- Verified counts: manifest 138; quality 552; candidate diagnostics 1,518; delivery 2,070; summary 15; existing paired comparisons 10; monotonicity diagnostics 138.
- Verified: unique keys in tested tables; matching image sets; 2 lung-mask files per image; positive mask coverage; positive payload sizes; metric ranges; P1 non-fallback constraint satisfaction; P1 lossless fallback count 0; no traceback; completed log for 138 real images; stored summary matches independent recomputation from delivery rows; all 138 standalone lossless reconstructions exact; identical primary/lossless per-image/profile throughput draws.
- The primary implementation checks P2 residual round-trip equality during processing and raises an error on mismatch; the successful 138-image workflow therefore passed that per-image guard.

The automated QC is a strong reproducibility check, but it is not a substitute for clinical validation, legal review, or an external replication.

## 6. Main image-quality and payload results

The following values are the recorded full-set aggregates. Payload and quality means are from the 138-image quality table; the deadline-conditioned quality means in the summary can differ by profile because not every selected representation arrives before the deadline.

| Method | Mean payload (KiB) | Mean compression ratio vs raw 8-bit | Mean PSNR (dB) | Mean global SSIM | Mean regional SSIM p05 | Mean max absolute error |
|---|---:|---:|---:|---:|---:|---:|
| B1 — JPEG quality 75 | 937.35 | 21.07:1 | 52.4342 | 0.9956348 | 0.9936473 | 33.63 |
| B2 — JPEG 2000 target 20 | 960.16 | 20.00:1 | 50.9420 | 0.9914530 | 0.9876800 | 7.04 |
| B3 — Global SSIM selector | 170.35 | 117.63:1 | 45.7667 | 0.9751190 | 0.9564491 | 17.36 |
| P1 — Regional selector | 208.61 | 105.92:1 | 46.0556 | 0.9770307 | 0.9601459 | 15.68 |

P1’s mean payload is about 39.18 KiB larger than B3’s, approximately 23.0% relative to B3. The recorded mean regional SSIM p05 is higher for P1 (0.96015) than B3 (0.95645), and the recorded mean maximum absolute error is lower (15.68 versus 17.36). These differences support a payload-versus-objective-quality trade-off within the selected operating rules. They do not prove that P1 is clinically superior.

## 7. Paired analysis: P1 versus B3

The publication-analysis script used paired per-image differences, 2,000 paired bootstrap resamples with seed 42, percentile 95% intervals, and two-sided Wilcoxon signed-rank tests. Holm adjustment was applied across all 19 comparisons in the generated statistical table; therefore, adjusted values for these four comparisons are 2.477 × 10⁻⁶.

| Metric (P1 − B3) | n | Mean paired difference | Median paired difference | Bootstrap 95% CI | Raw p | Holm-adjusted p |
|---|---:|---:|---:|---:|---:|---:|
| Payload bytes | 138 | +39,177.93 B | 0 B | 26,095.46 to 52,839.50 B | 2.477 × 10⁻⁷ | 2.477 × 10⁻⁶ |
| PSNR | 138 | +0.28885 dB | 0 dB | +0.19457 to +0.38536 dB | 2.477 × 10⁻⁷ | 2.477 × 10⁻⁶ |
| Global SSIM | 138 | +0.0019116 | 0 | +0.001252 to +0.002608 | 2.477 × 10⁻⁷ | 2.477 × 10⁻⁶ |
| Regional SSIM p05 | 138 | +0.0036968 | 0 | +0.002408 to +0.005062 | 2.477 × 10⁻⁷ | 2.477 × 10⁻⁶ |

The zero medians indicate that at least half of paired image-level differences are zero or centered at zero under the recorded outputs, while the positive means reflect changes on a subset of images. This distribution should be retained in the discussion rather than describing the mean as a uniform per-image improvement.

## 8. Deadline results

### 8.1 B3 and P1

| Profile | Method | Mean payload (KiB) | Full-delivery miss rate | Quality bound met by deadline |
|---|---|---:|---:|---:|
| Poor, 128 kbit/s | B3 | 170.35 | 14.49% | 66.67% |
| Poor, 128 kbit/s | P1 | 208.61 | 24.64% | 75.36% |
| Moderate, 512 kbit/s | B3 | 170.35 | 0.72% | 74.64% |
| Moderate, 512 kbit/s | P1 | 208.61 | 0.72% | 99.28% |
| Good, 2 Mbit/s | B3 | 170.35 | 0.00% | 74.64% |
| Good, 2 Mbit/s | P1 | 208.61 | 0.00% | 100.00% |

The deadline-miss and quality-bound rates describe different outcomes. A delivered representation may fail the regional/error bound, and a quality mean calculated only when an image is delivered has a profile-dependent denominator. All rates above use 138 images as the denominator.

At poor bandwidth, the larger P1 payload is associated with a higher miss rate than B3. At moderate and good bandwidth, P1 meets the selected objective quality bound more frequently in this simulation. This conclusion is conditional on the stated throughput model and deadline.

### 8.2 P2 base-plus-residual

| Profile | Mean full payload (KiB) | First-stage miss rate | Full-representation miss rate | Quality bound met by deadline |
|---|---:|---:|---:|---:|
| Poor, 128 kbit/s | 5,733.49 | 13.04% | 100.00% | 65.94% |
| Moderate, 512 kbit/s | 5,541.42 | 5.07% | 100.00% | 92.75% |
| Good, 2 Mbit/s | 5,030.19 | 4.35% | 60.14% | 95.65% |

P2's base can arrive before the deadline while its residual does not. In that case, the quality recorded as available by the deadline describes the lossy base, not exact reconstruction. Exact reconstruction requires both components. The high full-delivery miss rates and multi-megabyte payloads make P2 a negative/ablation result under the current deadline settings rather than evidence of an effective exact-delivery strategy.

## 9. Statistical comparison of P2 and P1

Binary outcomes were paired by image and profile and tested using exact two-sided McNemar tests. Discordant counts are ordered as (P2=1, P1=0) / (P1=1, P2=0); for a miss outcome, 1 means a miss, while for quality-bound success, 1 means success. Percent-point differences are P2 minus P1. Bootstrap intervals use 2,000 image-level paired resamples, seed 42. Holm adjustment covers all 19 comparisons in the generated analysis table.

| Profile | Outcome | P2 − P1 rate difference | Discordant pairs | Raw p | Holm-adjusted p | 95% paired bootstrap CI |
|---|---|---:|---:|---:|---:|---:|
| Poor | First-stage/deadline miss | −11.59 pp | 1 / 17 | 1.4496 × 10⁻⁴ | 8.6975 × 10⁻⁴ | −17.39 to −6.50 pp |
| Poor | Full-delivery miss | +75.36 pp | 104 / 0 | 9.8608 × 10⁻³² | 1.5777 × 10⁻³⁰ | +68.12 to +82.61 pp |
| Poor | Quality-bound success | −9.42 pp | 0 / 13 | 2.4414 × 10⁻⁴ | 1.2207 × 10⁻³ | −14.49 to −5.07 pp |
| Moderate | First-stage/deadline miss | +4.35 pp | 7 / 1 | 0.070313 | 0.093750 | +0.72 to +8.70 pp |
| Moderate | Full-delivery miss | +99.28 pp | 137 / 0 | 1.1479 × 10⁻⁴¹ | 2.1811 × 10⁻⁴⁰ | +97.83 to +100.00 pp |
| Moderate | Quality-bound success | −6.52 pp | 0 / 9 | 0.003906 | 0.015625 | −10.87 to −2.90 pp |
| Good | First-stage/deadline miss | +4.35 pp | 6 / 0 | 0.031250 | 0.093750 | +1.45 to +7.97 pp |
| Good | Full-delivery miss | +60.14 pp | 83 / 0 | 2.0680 × 10⁻²⁵ | 2.6883 × 10⁻²⁴ | +52.17 to +68.84 pp |
| Good | Quality-bound success | −4.35 pp | 0 / 6 | 0.031250 | 0.093750 | −7.97 to −1.45 pp |

The comparison indicates that P2 has markedly worse full-representation delivery under all three profiles. Some differences in first-stage misses and quality-bound success are not statistically significant after Holm adjustment. Statistical significance is not clinical importance, and these results are confined to the simulation.

## 10. Lossless JPEG 2000 baseline (B0)

The standalone full-set baseline processed all 138 images and verified exact reconstruction of all normalized 8-bit inputs.

| Metric | Recorded result |
|---|---:|
| Mean payload | 3,854,278.043 bytes (3,763.94 KiB) |
| Median payload | 3,801,277.5 bytes |
| Mean compression ratio versus raw 8-bit pixels | 5.311806:1 |
| Median encode time | 0.699541 s (runner-dependent) |
| Exact round trips | 138/138 |
| Full-delivery miss rate, poor profile | 100.00% |
| Full-delivery miss rate, moderate profile | 99.28% |
| Full-delivery miss rate, good profile | 26.09% |

The lossless baseline is exact only with respect to the evaluated normalized 8-bit inputs. It does not demonstrate preservation of native 12-bit information. Its payload is much larger than the lossy methods, resulting in substantial deadline misses under the 20-second simulation.

The publication-analysis workflow verified that the B0 and primary runs used identical per-image/profile bandwidth draws, so paired B0-versus-P1 binary comparisons are supported. For full-delivery misses, B0 minus P1 differences were +75.36 percentage points (poor; 95% CI +68.12 to +82.61), +98.55 points (moderate; +96.38 to +100.00), and +26.09 points (good; +18.84 to +34.06). Holm-adjusted p-values were 1.5777 × 10⁻³⁰, 4.1326 × 10⁻⁴⁰, and 3.4925 × 10⁻¹⁰, respectively. These are simulated delivery comparisons, not real-world transmission guarantees.

## 11. Threshold sensitivity

The publication-analysis workflow evaluated descriptive threshold sensitivity using already encoded candidate metrics; it did not re-encode images. It confirmed that the B3 threshold of global SSIM ≥ 0.95 and P1 thresholds of regional SSIM p05 ≥ 0.95 plus maximum error ≤ 24 reproduce the primary operating-point mean payloads.

Examples from the sensitivity output:
- B3 global SSIM threshold 0.90: mean payload 163,747.46 bytes, median 163,780.5 bytes, p95 payload 163,888.6 bytes, mean global SSIM 0.974260, mean regional SSIM p05 0.955154, and mean maximum error 17.67.
- At the selected P1 thresholds (regional p05 0.95, maximum error 24), the selector reproduces the primary P1 payload result and has zero lossy infeasibility/fallbacks in this run.

This is post-hoc descriptive robustness analysis, not clinical threshold validation. Changing the grid geometry or regional percentile would require recalculating the regional metrics from pixels and masks.

## 12. Discussion

The fixed JPEG and fixed-target JPEG 2000 baselines produce mean payloads near 1 MiB. The two quality-constrained selectors use substantially smaller payloads within the finite candidate set. P1 uses a larger payload than B3 but improves the recorded mean regional SSIM p05 and lowers the recorded mean maximum absolute error. The paired results suggest that these differences are concentrated in a subset of images rather than uniformly positive across all cases.

Deadline behavior reveals the cost of payload size under restrictive simulated throughput. P1's larger payload has a higher poor-profile miss rate than B3. At moderate and good profiles, the recorded miss rates are low, and P1 meets the selected quality bound more often. These results are conditional on the simulated model, estimator, and 20-second deadline.

P2 illustrates the cost of requiring exact reconstruction through a separate residual. Its base can arrive early, but the residual frequently does not arrive by the deadline. Its full-delivery misses are 100% in the poor and moderate profiles and 60.14% in the good profile. Under these conditions, P2 should be described as an informative negative/ablation result, not as an effective exact-delivery method.

The study's contribution should be framed narrowly: a reproducible evaluation of measured payloads, global and regional objective metrics, and simulated deadline behavior for specified selectors on the evaluated 8-bit Montgomery representation. The report should not claim that ROI-aware compression, SSIM-constrained selection, or network-aware delivery is itself novel without a broader literature review.

## 13. Limitations and threats to validity

1. **Bit depth and provenance:** the public files audited are 8-bit, despite the original paper's 12-bit description. Results do not establish native 12-bit preservation.
2. **Dataset size and coverage:** only 138 images from one collection were evaluated. Results may not generalize to other datasets, devices, populations, bit depths, or imaging tasks.
3. **Objective quality:** PSNR, global SSIM, regional SSIM, and maximum error do not establish diagnostic safety or accuracy. No radiologist reader study or downstream task validation was performed.
4. **Engineering thresholds:** the regional grid, coverage threshold, percentile, SSIM bound, and error limit are not clinically validated.
5. **Candidate grid:** the selectors choose among a finite set of tested candidates; other encoder versions or settings may yield different results.
6. **Network model:** the profiles are simulated, not live traces. Real systems introduce additional transport and operational effects.
7. **P2 custom representation:** base-plus-residual is not a standards-compliant progressive JPEG 2000 codestream and is frequently too large for the deadline.
8. **Licensing:** the mirror lists license metadata as “other”; official source terms and attribution need review.
9. **Statistical scope:** paired tests and Holm adjustment improve the analysis, but results remain bounded to this dataset and model. Post-hoc sensitivity is exploratory.
10. **Novelty:** related work on medical compression, ROI-based JPEG 2000, JPIP, network-aware delivery, and diagnostic quality must be reviewed in depth before asserting novelty.

## 14. Ethics and clinical interpretation

This is a secondary analysis of a public research dataset. The final manuscript must accurately describe the source, applicable terms, and any institutional requirements. Do not invent an ethics approval or exemption statement. Confirm the correct wording with the relevant institution or target venue.

The study does not evaluate patient outcomes or diagnostic decisions. It cannot support claims that any compressed image is diagnostically equivalent to the reference, safe for clinical use, or suitable for a regulated workflow. Such claims would require a separately designed clinical/task-based validation study and appropriate approvals.

## 15. Conclusions

The verified 138-image benchmark shows that the specified quality-constrained selectors can substantially reduce mean payload relative to the fixed operating points. P1 has a higher mean payload than B3 and modestly higher recorded global and regional SSIM metrics. Under the poor simulated profile, P1's larger payload is associated with a higher miss rate; under moderate and good profiles, its recorded quality-bound success is higher.

The lossless baseline exactly reconstructs the evaluated normalized 8-bit inputs but has a large payload and substantial deadline misses. P2's full base-plus-residual representation is frequently not delivered within the deadline, limiting its usefulness for exact delivery under the current simulated conditions.

The results are valid only within the declared data representation, candidate settings, objective metrics, and simulation. They do not establish clinical safety, diagnostic accuracy, clinical equivalence, or real-world network performance. The main benchmark and automated numerical QC have completed successfully; publication still requires venue-specific formatting, author/declaration completion, licensing review, and a deeper verified literature review.

## 16. Publication-readiness checklist

### Completed and evidenced
- [x] Full-set primary benchmark completed on the 138-image Montgomery County dataset.
- [x] Analysis and numerical quality control completed: 54 checks passed and 0 checks failed.
- [x] The manuscript has been prepared outside this repository; no manuscript text is included here.

### Pending before submission
- [ ] Run a suitable similarity checker and record the actual tool and score.
- [ ] Select the target IEEE venue and verify its current official template, page limit, and submission requirements.
- [ ] Complete venue-specific formatting, declarations, and final submission-compliance checks.

## 17. References

[1] S. Jaeger et al., “Automatic tuberculosis screening using chest radiographs,” *IEEE Transactions on Medical Imaging*, vol. 33, no. 2, pp. 233–245, Feb. 2014, doi: 10.1109/TMI.2013.2284099.

[2] S. Jaeger et al., “Two public chest X-ray datasets for computer-aided screening of pulmonary diseases,” *Quantitative Imaging in Medicine and Surgery*, vol. 4, no. 6, pp. 475–477, Dec. 2014, doi: 10.3978/j.issn.2223-4292.2014.11.20.

[3] F. Liu, M. Hernández-Cabronero, V. Sanchez, M. W. Marcellin, and A. Bilgin, “The current role of image compression standards in medical imaging,” *Information*, vol. 8, no. 4, Art. no. 131, 2017, doi: 10.3390/info8040131.

[4] Z. Wang, A. C. Bovik, H. R. Sheikh, and E. P. Simoncelli, “Image quality assessment: From error visibility to structural similarity,” *IEEE Transactions on Image Processing*, vol. 13, no. 4, pp. 600–612, Apr. 2004, doi: 10.1109/TIP.2003.819861.

[5] J.-F. Pambrun and R. Noumeir, “Limitations of the SSIM quality metric in the context of diagnostic imaging,” in *Proceedings of the IEEE International Conference on Image Processing (ICIP)*, pp. 2960–2963, Quebec City, Canada, Sep. 2015, doi: 10.1109/ICIP.2015.7351345.

[6] S. Jaeger et al., “Automatic screening for tuberculosis in chest radiographs: a survey,” *Quantitative Imaging in Medicine and Surgery*, vol. 3, no. 2, pp. 89–99, Apr. 2013, doi: 10.3978/j.issn.2223-4292.2013.04.03.

[7] U.S. National Library of Medicine, “Tuberculosis Chest X-ray Datasets: Montgomery County CXR Set.” [Online]. Available: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/. Verify access date and source terms before submission.

[8] Famatsu123, “Montgomery and Shenzhen Tuberculosis Chest X-rays,” *Hugging Face Datasets*, dataset card. [Online]. Available: https://huggingface.co/datasets/Famatsu123/montgomery-shenzhen-tuberculosis-cxr. Verify dataset-card revision, license metadata, and access date before submission.

[9] S. Candemir et al., “Lung segmentation in chest radiographs using anatomical atlases with nonrigid registration,” *IEEE Transactions on Medical Imaging*, vol. 33, no. 2, pp. 577–590, Feb. 2014, doi: 10.1109/TMI.2013.2290491.

[10] U.S. National Library of Medicine, “NLM-MontgomeryCXRSet ReadMe,” dataset citation and use instructions. [Online]. Available: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/MontgomerySet/NLM-MontgomeryCXRSet-ReadMe.pdf.

[11] U.S. National Library of Medicine, “National Library of Medicine Terms and Conditions,” last reviewed May 21, 2019. [Online]. Available: https://www.nlm.nih.gov/databases/download/terms_and_conditions.html.

[12] R. Noumeir and J.-F. Pambrun, “Using JPEG 2000 interactive protocol to stream a large image or a large image set,” *Journal of Digital Imaging*, vol. 24, no. 5, pp. 833–843, Oct. 2011, doi: 10.1007/s10278-010-9343-0.


---

## Appendix A. Artifact inventory

Primary run outputs:
- `results/dataset_manifest.csv`
- `results/quality_by_image.csv`
- `results/candidate_diagnostics.csv`
- `results/delivery_by_image_profile.csv`
- `results/summary.csv`
- `results/paired_comparisons.csv`
- `results/monotonicity_diagnostics.csv`
- `results/run_metadata.json`
- `results/run.log`

The supplemental lossless baseline artifacts are now preserved on `main`:
- `lossless-results/lossless_quality_by_image.csv`
- `lossless-results/lossless_delivery_by_image_profile.csv`
- `lossless-results/lossless_manifest.csv`
- `lossless-results/lossless_delivery_summary.csv`
- `lossless-results/run_metadata.json`
- `lossless-results/run.log`
- `supplemental_lossless_baseline.py`
- `.github/workflows/lossless-baseline.yml`

The publication-analysis workflow uploads `publication-analysis-report`, containing the QC report, adjusted paired comparisons, and sensitivity-analysis table. Its QC report records 54 checks passed and 0 failed.

## Appendix B. Interpretation rules

1. Use the main full-set run for B1, B2, B3, P1, and P2. Do not combine pilot results with the corrected full-set run.
2. Use B0 only as a separate baseline; paired delivery comparisons are supported only because identical per-image/profile throughput draws were checked.
3. State that the public input representation was 8-bit grayscale.
4. Label all deadline outcomes as simulated.
5. For P2, distinguish base-stage delivery and quality from complete base-plus-residual reconstruction.
6. Do not claim clinical safety, diagnostic equivalence, diagnostic accuracy, or a clinically validated regional threshold.
7. Treat threshold sensitivity as post-hoc descriptive robustness analysis.
8. Do not claim a plagiarism/similarity percentage until a suitable checker has actually produced it.
