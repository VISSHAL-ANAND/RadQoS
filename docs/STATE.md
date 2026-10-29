# Research Paper State

Last reconciled: 2026-10-29 UTC

## Project
- Repository: https://github.com/VISSHAL-ANAND/research-papper
- Publication-support branch: `publication-readiness`; PR #1 remains open/draft and is not merged to `main`.
- Research topic: quality-constrained and deadline-aware compression of Montgomery County chest radiographs.
- Experimental end report: [`docs/EXPERIMENTAL_END_REPORT.md`](EXPERIMENTAL_END_REPORT.md).
- Existing Library manuscript draft: `IEEE_Manuscript_Quality_Constrained_Compression_DRAFT.docx` and companion PDF. Preserve/update this draft rather than recreate it.
- Target venue, author names, affiliations, institutional email, corresponding author, funding/conflict/ethics wording, and page limit remain unconfirmed.
- User supplied `IEEEpaper.pdf` as a visual reference only; it is not the target paper.

## Primary full-dataset benchmark — now verified successful
- Workflow: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40865016332
- Code commit: `b8ead4566b07cf2130a3f06546392c6c739fa44b`.
- Workflow completed successfully on 2026-10-29; run metadata timestamp is 2026-10-29T14:37:48.676341+00:00.
- 138 real images; Python 3.12.15; NumPy 2.5.4; pandas 3.1.0; Pillow 13.0.0; SciPy 1.18.1; scikit-image 0.26.0; Hugging Face Hub 2.3.0; seed 42; 11 candidate settings; no synthetic benchmark images.
- Raw outputs on `main`: `results/dataset_manifest.csv`, `quality_by_image.csv`, `candidate_diagnostics.csv`, `delivery_by_image_profile.csv`, `summary.csv`, `paired_comparisons.csv`, `monotonicity_diagnostics.csv`, `run_metadata.json`, `run.log`.
- Verified expected row counts: manifest 138; quality 552; candidate diagnostics 1,518; delivery 2,070; summary 15; original paired table 10; monotonicity diagnostics 138.
- Verified no duplicate keys in audited tables; all expected image sets align; two lung-mask files per image; positive mask coverage and payload sizes; quality metrics within expected ranges; summary aggregates match independent recomputation; P1 has zero lossless fallbacks and all non-fallback selected candidates meet both constraints; run log records 138-image completion with no traceback.
- Separate full-set lossless baseline: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40885682147. All 138 evaluated normalized 8-bit inputs reconstruct exactly. Primary and lossless per-image/profile bandwidth draws were independently checked to be identical before paired comparisons.
- Pilot run remains exploratory and must not be combined with the corrected full-set results.

## Publication analysis — completed
- Analysis workflow: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906476864
- QC report: 54 checks passed, 0 failed.
- Artifact: `publication-analysis-report` (QC report, adjusted paired comparisons, threshold-sensitivity output).
- Statistical postprocessor uses paired per-image bootstrap intervals (2,000 resamples, seed 42), Wilcoxon signed-rank tests for continuous paired metrics, exact McNemar tests for paired binary outcomes, and Holm adjustment across 19 comparisons.
- Threshold sensitivity from already encoded candidates reproduces the primary B3 and P1 operating-point mean payloads. It is post-hoc descriptive analysis, not clinical threshold validation.
- P2 residual round-trip equality is checked for each image by the benchmark; the run aborts on mismatch. The successful run passed that guard.
- A schema/presentation issue remains in the analysis CSV/log: P2 paired binary rows put the mean rate difference in a differently named column while the shared `mean_difference` column is blank. The numeric value is present, but the report format should be normalized before final archival if feasible.

## Principal recorded results
- B1 JPEG quality 75: mean payload 937.35 KiB; mean PSNR 52.4342 dB; mean global SSIM 0.9956348; mean regional SSIM p05 0.9936473.
- B2 JPEG 2000 target 20: 960.16 KiB; 50.9420 dB; 0.9914530; 0.9876800.
- B3 global SSIM selector: 170.35 KiB; 45.7667 dB; 0.9751190; 0.9564491.
- P1 regional selector: 208.61 KiB; 46.0556 dB; 0.9770307; 0.9601459.
- P1-minus-B3 mean payload difference: 39,177.93 bytes; paired bootstrap 95% CI 26,095.46–52,839.50 bytes. Mean PSNR difference +0.28885 dB (95% CI +0.19457 to +0.38536); mean global SSIM difference +0.001912 (95% CI +0.001252 to +0.002608); mean regional SSIM p05 difference +0.003697 (95% CI +0.002408 to +0.005062).
- P1 mean payload is approximately 23% higher than B3. This is an objective-metric/payload trade-off, not clinical superiority.
- Full-delivery miss rates for B3/P1: poor 14.49%/24.64%; moderate 0.72%/0.72%; good 0%/0%.
- P2 full-delivery miss rates: poor 100%; moderate 100%; good 60.14%. Mean full payload varies by profile: 5,733.49 KiB poor; 5,541.42 KiB moderate; 5,030.19 KiB good. Distinguish base-stage from full residual delivery.
- B0 lossless baseline mean payload 3,854,278 bytes (3,763.94 KiB), mean ratio 5.311806:1, exact reconstruction 138/138 normalized 8-bit inputs; full-delivery miss rates poor 100%, moderate 99.28%, good 26.09%.

## Dataset and method limitations
- Dataset: 138 frontal images (80 normal, 58 with TB-related findings) with manual left/right lung masks.
- Public NLM PNG IHDR audit reports 8-bit grayscale for all 138 files (97 at 4,892×4,020; 41 at 4,020×4,892). The original dataset paper describes 12-bit images. The benchmark results apply to the publicly distributed 8-bit representation and do not establish native 12-bit preservation.
- Mirror license metadata is `other`; verify source terms and attribution before publication or redistribution.
- Network profiles (128 kbit/s, 512 kbit/s, 2 Mbit/s), 0.5 s latency, 20 s deadline, and lognormal throughput are simulated, not live network measurements.
- Regional SSIM p05 over eligible cells in an 8×8 lung-mask grid, coverage threshold 5%, SSIM threshold 0.95, and max error 24 are engineering settings, not clinically validated thresholds.
- P2 is custom JPEG 2000 base + zlib signed residual, not standards-compliant progressive JPEG 2000.
- No reader study, diagnostic accuracy, clinical safety, or clinical non-inferiority is measured.

## Remaining publication blockers
1. Review official NLM dataset terms and mirror license metadata.
2. Expand and verify related work (ROI JPEG 2000, JPIP/network-aware transmission, diagnostic compression evaluation, SSIM limitations); verify every citation against primary publisher/DOI records.
3. Normalize the adjusted-statistics output schema and rerun the analysis/unit workflow if the output is changed.
4. Update the existing manuscript draft with the verified results and limitations.
5. Confirm target venue/template/page limit and all author/declaration fields; do not invent missing information.
6. Generate final tables/figures from validated CSVs and check every manuscript value.
7. Export and inspect final DOCX/PDF page-by-page. The DOCX/PDF generation operation has not been completed in this conversation.
8. Run a suitable similarity checker and record its actual score; below 20% is a target, not a guarantee.

## Branch safety
No benchmark outputs were modified and no changes were merged to `main`. Publication-support changes remain on `publication-readiness`.
