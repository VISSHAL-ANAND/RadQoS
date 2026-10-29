# Research Paper State

Last reconciled: 2026-10-29 (UTC; see GitHub Actions timestamps below)

## Project
- Repository: https://github.com/VISSHAL-ANAND/research-papper
- Working branch: `publication-readiness`
- Research topic: deadline-aware adaptive compression of Montgomery County chest radiographs, with lung-region quality constraints.
- Intended deliverable: an IEEE conference-style manuscript with verified experiments and a polished DOCX/PDF.
- User supplied `IEEEpaper.pdf` as a visual formatting example. It is a six-page, two-column 2019 IEEE conference-proceedings paper. It is not the research manuscript and its educational research content must not be copied.

## Verified repository facts
- The current primary implementation is `benchmark_montgomery.py`.
- The main workflow is `.github/workflows/benchmark.yml`, configured for Python 3.12, `MAX_IMAGES=0`, and a 240-minute job timeout.
- The README specifies 138 Montgomery chest radiographs, 80 normal and 58 with TB-related findings, with manual left/right lung masks.
- Provenance audit: the public NLM PNG headers report 8-bit grayscale for all 138 images: 97 at 4892x4020 and 41 at 4020x4892. The README records a five-image / ten-mask byte-for-byte SHA-256 comparison between the NLM source and Hugging Face mirror.
- Do not claim native 12-bit preservation. Current benchmark evaluates the distributed 8-bit PNG representation.
- Expected primary outputs: `quality_by_image.csv`, `delivery_by_image_profile.csv`, `candidate_diagnostics.csv`, `summary.csv`, `paired_comparisons.csv`, `monotonicity_diagnostics.csv`, `dataset_manifest.csv`, `run_metadata.json`, and `run.log`.

## Methods currently specified
- B1: JPEG quality 75.
- B2: JPEG 2000 target ratio 20.
- B3: smallest measured JPEG 2000 payload meeting global mean SSIM >= 0.95, with an explicit best-quality fallback if infeasible.
- P1: smallest measured payload meeting fifth-percentile SSIM over eligible lung-mask grid regions >= 0.95 and maximum absolute error <= 24; lossless JPEG 2000 fallback if infeasible.
- P2: custom JPEG 2000 base plus zlib-compressed signed residual, with exact reconstruction of the normalized 8-bit image checked. This is not a standards-compliant progressive JPEG 2000 codestream.
- Ratios: [4, 6, 8, 10, 15, 20, 30, 40, 60, 80, 120].
- Simulated mean bandwidths: 128 kbps, 512 kbps, 2 Mbps; lognormal throughput, 0.5 s latency, 20 s deadline. These are simulation settings, not live-network measurements.

## Verified experiment evidence
### Five-image pilot
- Run: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40863808178
- Conclusion: success.
- Processed five real images; no synthetic images were used.
- Summary is in the job log. Pilot results are exploratory and must not be presented as full-dataset evidence.
- On the pilot, P1 payloads were larger than B3; P2's full residual payload often missed deadlines even where its base stage arrived.

### Full-set standalone lossless JPEG 2000 baseline
- Run: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40877527634
- Conclusion: success.
- Processed all 138 real images and verified exact lossless reconstruction for all.
- Mean payload: 3,854,278 bytes; median payload: 3,801,277.5 bytes.
- Mean compression ratio versus raw 8-bit pixels: 5.3118:1.
- Median encode time: 0.7038 s.
- Simulated full-delivery miss rates: poor/128 kbps 100%; moderate/512 kbps 99.2754%; good/2 Mbps 26.087%.
- This is a supplemental standalone baseline, not the completed primary benchmark. Preserve this distinction.

### Primary full-dataset benchmark
- Run: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40865016332
- Last observed status: in progress; benchmark step still running; no artifact available at the last check.
- The current committed `results/run.log` ends at image 19/138, but it is not proof that the active run stopped there; it may reflect an earlier published attempt.
- Do not cancel or replace this run without checking its latest state. Wait for the run to conclude or timeout, then inspect job logs and artifacts.
- Many earlier main-branch attempts were cancelled during iterative code changes; at least some early attempts failed. Do not represent those as successful full-set results.

## Manuscript status
- No manuscript DOCX/PDF was found at the checked root paths `paper.docx` or `paper.pdf`; both returned 404.
- The supplied `IEEEpaper.pdf` is a style reference, not the target paper.
- Therefore the current manuscript is not verified as present in the repository. Search the user's conversation/library for the previously reported draft before recreating it.

## Publication blockers
1. Primary full-set benchmark has not been verified successful.
2. Final per-image outputs and full primary statistical analysis are not yet available in the main branch.
3. The dataset license/terms need explicit review; the mirror labels license metadata as `other`.
4. Statistical methods require review, including paired binary outcome testing and multiplicity handling.
5. Exact target conference/journal, page limit, author list, affiliations, and corresponding author details are not yet confirmed in this repository.
6. No similarity-check report is available. A target below 20% is not a verified score.
7. No clinical safety or diagnostic performance claim is supported by PSNR/SSIM alone.

## Working rule
Never invent, backfill, or round unsupported results. Manuscript claims must be traceable to completed run outputs, cited literature, or clearly labeled interpretation.
