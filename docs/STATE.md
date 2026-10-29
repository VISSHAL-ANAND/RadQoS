# Research Paper State

Last reconciled: 2026-10-29 UTC

## Project and repository
- Repository: https://github.com/VISSHAL-ANAND/research-papper
- Publication-support changes and unique content from all four working branches have been merged into `main` through PRs #1–#4. The branch refs still exist; this connected GitHub toolset does not expose branch deletion.
- Research topic: quality-constrained and deadline-aware compression of Montgomery County chest radiographs.
- Experimental report: [docs/EXPERIMENTAL_END_REPORT.md](EXPERIMENTAL_END_REPORT.md).
- User's existing manuscript drafts are in the ChatGPT Library; do not claim they have been updated unless the files are actually edited.
- Author details and target council/venue/template/page limit are not confirmed.
- Similarity checker has not been run; no actual similarity score is known.
- No final submission PDF has been generated in this work session.

## Primary full-dataset benchmark
- Workflow: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40865016332
- Code commit: `b8ead4566b07cf2130a3f06546392c6c739fa44b`.
- Successful full run: 138 real images; seed 42; 11 candidate settings; `synthetic=false`.
- Expected counts: manifest 138; quality 552; candidate diagnostics 1,518; delivery 2,070; summary 15; original paired table 10; monotonicity diagnostics 138.
- QC verified table keys, image sets, mask coverage, positive payloads, metric ranges, P1 constraint satisfaction, summary recomputation, successful log completion, and absence of traceback.
- The standalone lossless baseline reconstructed all 138 normalized 8-bit inputs exactly. Primary and lossless runs used identical per-image/profile throughput draws before paired comparisons.
- Pilot results remain exploratory and are not mixed with the primary full-set results.

## Publication analysis
- Original analysis workflow: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906476864
- Schema correction commit: `d4f6fa53f7a78f25b0d5b5e7b3fb4ba7967734a8`.
- Latest corrected analysis workflow: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906893245
- Latest unit-test workflow: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906898568
- QC report: 54 checks passed, 0 failed.
- Analysis uses paired image-level bootstrap intervals (2,000 resamples, seed 42), Wilcoxon signed-rank tests, exact McNemar tests, and Holm correction across 19 comparisons.
- The P2 paired-binary mean-difference column inconsistency was fixed and the analysis/test workflows rerun successfully.
- Candidate-based threshold sensitivity is post-hoc descriptive analysis, not clinical threshold validation.

## Key recorded results
- B1 JPEG quality 75: mean payload 937.35 KiB; PSNR 52.4342 dB; global SSIM 0.9956348; regional SSIM p05 0.9936473.
- B2 JPEG 2000 target 20: 960.16 KiB; PSNR 50.9420 dB; global SSIM 0.9914530; regional SSIM p05 0.9876800.
- B3 global SSIM selector: 170.35 KiB; PSNR 45.7667 dB; global SSIM 0.9751190; regional SSIM p05 0.9564491.
- P1 regional selector: 208.61 KiB; PSNR 46.0556 dB; global SSIM 0.9770307; regional SSIM p05 0.9601459.
- P1 uses approximately 23% more mean payload than B3; observed metric improvements are not proof of clinical superiority.
- Full-delivery miss rates B3/P1: poor 14.49%/24.64%; moderate 0.72%/0.72%; good 0%/0%.
- P2 full-delivery miss rates: poor 100%; moderate 100%; good 60.14%.
- B0 lossless mean payload 3,854,278 bytes (3,763.94 KiB); all 138 normalized 8-bit inputs reconstructed exactly.

## Material limitations
- All 138 public NLM PNG headers examined report 8-bit grayscale, despite the original paper describing 12-bit images. Results apply to the public 8-bit representation and do not demonstrate native 12-bit preservation.
- The mirror license metadata is `other`; applicable terms still require review.
- Network results use simulated bandwidth (128 kbit/s, 512 kbit/s, 2 Mbit/s), 0.5 s latency, and a 20 s deadline; these are not live-network measurements.
- Regional SSIM and maximum-error thresholds are engineering choices, not clinically validated thresholds.
- P2 is a custom JPEG 2000 base plus zlib-compressed signed residual, not a standards-compliant progressive JPEG 2000 codestream.
- No reader study, diagnostic accuracy, clinical safety, or clinical non-inferiority was measured.

## Remaining publication blockers
1. Dataset terms were reviewed and documented. The mirror's `other` license metadata is not a clear license; do not redistribute images/masks, and contact NLM if intended use is ambiguous.
2. Finish primary-source literature/reference verification and integrate it into the manuscript.
3. Confirm the target council/venue, template, page limit, author details, and required declarations.
4. Update the existing manuscript and reconcile all reported values to the validated outputs.
5. Generate and inspect the final PDF; it does not yet exist in this work session.
6. Run a real similarity checker and record its actual score.
7. Branch content consolidation is complete: publication-readiness, lossless-baseline, provenance-check, and benchmark-pilot unique files are now preserved on `main`. Branch refs still exist and require deletion through GitHub's branch UI or an authorized API/CLI because branch deletion is not available through this session's GitHub actions.
