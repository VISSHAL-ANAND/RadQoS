# Research Paper State

Last reconciled: 2026-10-29 UTC

## Project
- Repository: https://github.com/VISSHAL-ANAND/research-papper
- Working branch: `publication-readiness`
- Research topic: deadline-aware adaptive compression of Montgomery County chest radiographs, with lung-region quality constraints.
- Intended deliverable: a publication-ready IEEE conference-style manuscript and DOCX/PDF, backed by validated experiments.
- User supplied `IEEEpaper.pdf` as a visual reference. It is a six-page, two-column 2019 IEEE conference-proceedings paper. It is not the target manuscript; do not copy its content.
- IEEE guidance says use the current official conference template and the target venue's instructions. Exact venue and page limit remain unknown.

## Manuscript and supporting documents recovered from the user's Library
These exist outside the GitHub repository:
- `IEEE_Manuscript_Quality_Constrained_Compression_DRAFT.docx` (six-page draft; created 2026-10-29 12:07 UTC)
- `IEEE_Manuscript_Quality_Constrained_Compression_DRAFT.pdf`
- `Adaptive_Compression_Research_Draft_WORKING.docx`
- `Experiment_Protocol_and_Reproducibility.docx`
- `Real_Image_Pilot_Validation_Report.docx`
The current draft is method-first and explicitly leaves full-set results pending. It has author/affiliation/email placeholders. Preserve and update this draft rather than recreate the paper. The checked repository root does not contain `paper.docx` or `paper.pdf`.

## Verified repository facts
- Primary implementation: `benchmark_montgomery.py`.
- Main workflow: `.github/workflows/benchmark.yml`, Python 3.12, `MAX_IMAGES=0`, 240-minute timeout.
- Dataset: 138 frontal radiographs (80 normal, 58 with TB-related findings), manual left/right lung masks.
- Provenance audit reports 8-bit grayscale for all 138 public NLM PNG headers: 97 images at 4892×4020 and 41 at 4020×4892. A five-image/ten-mask SHA-256 comparison found byte-identical files between the mirror and NLM source.
- The original dataset paper describes 12-bit images; the current public PNGs inspected in the audit are 8-bit. Do not claim native 12-bit preservation. State the exact public representation evaluated.
- Do not commit or rehost source images/masks. Dataset mirror metadata says license `other`; retain attribution and verify source terms before publication.

## Methods currently specified
- B1: JPEG quality 75.
- B2: JPEG 2000 target ratio 20.
- B3: smallest measured JPEG 2000 payload meeting global mean SSIM >= 0.95; explicit best-quality fallback if infeasible.
- P1: smallest measured payload meeting fifth-percentile SSIM over eligible lung-mask grid regions >= 0.95 and max absolute error <= 24; lossless JPEG 2000 fallback if infeasible.
- P2: custom JPEG 2000 base plus zlib-compressed signed residual; exact reconstruction of normalized 8-bit reference is checked. This is not a standards-compliant progressive JPEG 2000 codestream.
- Candidate ratios: [4, 6, 8, 10, 15, 20, 30, 40, 60, 80, 120].
- Simulated mean bandwidths: 128 kbps, 512 kbps, 2 Mbps; lognormal throughput; 0.5 s latency; 20 s deadline. These are simulation settings, not live-network measurements.

## Verified experiment evidence
### Five-image pilot
- Run: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40863808178
- Conclusion: success; five real images, 15 image/mask files; 20 single-stage quality rows, 55 candidate rows, 75 delivery rows, 15 summary rows, 10 paired-comparison rows.
- Pilot used an older bandwidth-estimator initialization and is descriptive only; do not combine it with corrected full-set results.
- The pilot showed P1 payloads larger than B3 in aggregate and P2 residual/full-delivery misses. These are not full-set conclusions.

### Full-set standalone lossless JPEG 2000 baseline
- Run: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40877527634
- Conclusion: success; all 138 real images processed and exact lossless reconstruction verified for all.
- Mean payload: 3,854,278.043 bytes; median payload: 3,801,277.5 bytes.
- Mean compression ratio versus raw 8-bit pixels: 5.311806:1.
- Median encode time in the latest rerun: 0.699541 s (timing is runner-dependent).
- Simulated full-delivery miss rates: 100% at 128 kbps, 99.2754% at 512 kbps, 26.087% at 2 Mbps.
- The latest successful rerun is 40885682147: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40885682147. Its CSVs, manifest, metadata, and log are now committed under `lossless-results/` on branch `lossless-baseline`.
- This is a supplemental standalone baseline, not the completed primary benchmark. The baseline script documents matched sorted image order, seed, profile order, and throughput RNG draw order; the postprocessor independently checks actual per-image/profile bandwidth draws before paired comparisons.

### Primary full-dataset benchmark
- Run: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40865016332
- Last checked: in progress, primary benchmark step running, no artifact yet. Job started 2026-10-29 11:23:27 UTC.
- Current committed `results/run.log` ends at image 19/138, but that file is not conclusive evidence that the active run stopped there; it may be from an earlier published attempt.
- Do not cancel or replace this run without checking its latest state. When it concludes or times out, inspect its job logs, artifacts, and published outputs.
- Several earlier main-branch attempts were cancelled during iterative code changes; early attempts also failed. Do not present those as successful full-set experiments.

## Publication-readiness branch work
- Draft PR: https://github.com/VISSHAL-ANAND/research-papper/pull/1 (open, draft, not merged).
- Added `analyze_results.py` to validate expected output counts, image/mask keys, constraints, residual-related completion logs, and summary aggregates.
- Added paired continuous analysis (Wilcoxon + paired bootstrap CI), exact McNemar tests for paired binary outcomes, and Holm adjustment.
- Added threshold sensitivity analysis over the already encoded candidate table; P1 fallback sizes use the matched lossless baseline. This is exploratory sensitivity analysis, not clinical threshold validation.
- Added unit tests and a branch-specific GitHub Actions check. Latest test run 40886253948 completed successfully, including the threshold-sensitivity test. An earlier run failed because the test omitted a pandas import; that was corrected and the rerun passed.
- Added an analysis workflow that reads main-branch primary outputs and the lossless-baseline branch, then uploads a report artifact without modifying main.
- A rerun of the lossless baseline completed successfully and published its raw CSVs to the `lossless-baseline` branch; run 40885682147 succeeded.
- The analysis workflow currently has only produced a pending report because the complete primary result CSVs were not yet present on main.

## Initial methods/statistics audit
- Current script uses Wilcoxon signed-rank for some paired binary outcomes; consider exact McNemar tests for binary paired outcomes.
- P-values across multiple comparisons are unadjusted; apply a prespecified correction such as Holm or label exploratory.
- Lognormal draws are normalized to the specified mean. For lognormal shape parameter s, CV is sqrt(exp(s^2)-1), not exactly s; the estimator prior uses (s*mean)^2, so it is approximate, not exactly matched. Correct or document and perform sensitivity analysis.
- Delivery-summary quality is the reconstruction available by deadline. For P2, if the base arrives but residual does not, quality describes the base, not the exact final reconstruction. Label this clearly.
- P2 is a custom base-plus-residual heuristic and may be inefficient; full-set evidence should decide whether it is a main contribution or a negative/ablation result.
- P1's regional metric uses an 8×8 grid; eligible cells have >=5% lung-mask coverage; each cell score is mean SSIM-map value over lung-mask pixels; regional score is fifth percentile. This is an engineering metric, not a clinically validated ROI criterion.
- PSNR/SSIM do not establish diagnostic safety or diagnostic accuracy.

## Publication blockers
1. Primary full-set benchmark is not yet verified successful.
2. Final primary CSVs and statistical analysis are not yet available.
3. Dataset license/terms need review.
4. Statistical analysis requires review, especially paired binary testing and multiplicity.
5. Exact target conference/journal, template, page limit, author names, affiliations, email, corresponding author, funding, and conflict statements are not confirmed.
6. Similarity report is not available; below 20% remains a target, not a verified score.
7. No clinical validation or diagnostic-safety claim is supported.

## Working rule
Every manuscript number must trace to a completed run output, every literature claim to a verified source, and every limitation must be disclosed. Never invent or backfill results.
