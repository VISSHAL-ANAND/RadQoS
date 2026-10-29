# Publication Tasks

Updated: 2026-10-29 UTC

## Completed experimental and analysis work
- [x] Full primary benchmark completed on 138 real images (commit `b8ead4566b07cf2130a3f06546392c6c739fa44b`).
- [x] Verify expected row counts: manifest 138; quality 552; candidate diagnostics 1,518; delivery 2,070; summary 15; original paired table 10; monotonicity diagnostics 138.
- [x] Audit duplicate keys, image/mask coverage, metric ranges, P1 constraints, summary recomputation, run log, and metadata.
- [x] Standalone lossless JPEG 2000 baseline completed; exact reconstruction of all 138 normalized 8-bit inputs.
- [x] Verify primary and lossless runs use identical per-image/profile throughput draws before paired B0 comparisons.
- [x] Publication-analysis QC: 54 checks passed, 0 failed.
- [x] Statistical analysis: 2,000 paired bootstrap resamples, seed 42; Wilcoxon signed-rank tests; exact McNemar tests; Holm correction across 19 comparisons.
- [x] Candidate-based threshold sensitivity analysis.
- [x] Correct P2 paired binary difference output schema to use common `mean_difference` column.
- [x] Re-run analysis workflow after schema correction: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906893245
- [x] Re-run analysis unit-test workflow after schema correction: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906898568
- [x] Add evidence-audited experimental end report at `docs/EXPERIMENTAL_END_REPORT.md`.

## Completed evidence and limitations documentation
- [x] Record exact source commit, software versions, seed, parameters, timestamp, and run links.
- [x] Document the public 8-bit versus original-paper 12-bit discrepancy; make no native 12-bit preservation claim.
- [x] Document simulated network profiles and avoid presenting them as live network measurements.
- [x] Document that PSNR/SSIM do not establish diagnostic safety.
- [x] Document that P2 is a custom base-plus-residual format, not standards-compliant progressive JPEG 2000.
- [x] Document all 138 lossless reconstructions and the paired-throughput matching check.

## Branch content consolidation
- [x] Merge publication-readiness documentation, analysis script, tests, and workflows into `main` (PR #1).
- [x] Merge standalone lossless baseline code, workflow, and measured CSV/log/metadata artifacts into `main` (PR #2).
- [x] Merge dataset provenance audit workflow into `main` (PR #3).
- [x] Merge isolated five-image pilot workflow into `main` (PR #4).
- [ ] Delete the four non-main branch refs after verifying their unique content is present on `main`; branch deletion is not exposed by the GitHub actions available in this session.

## Publication items not honestly verifiable as complete yet
- [x] Review official NLM dataset ReadMe and general terms, plus the mirror dataset card. Document the required NLM attribution/citations and no-sharing instruction; the mirror's `other` metadata is not a clear reuse license, so do not redistribute source images/masks or imply a license grant.
- [x] Integrate a focused related-work section and source-grounded citations into `docs/IEEE_MANUSCRIPT_AUTHOR_REVIEW_DRAFT.md` and add `docs/RELATED_WORK_AUDIT.md`.
- [ ] Expand the literature search for ROI-based medical compression, task-based/reader-study evaluation, and network-aware medical image delivery before making any novelty claim.
- [ ] Confirm target council/venue and its required template, page limit, and declarations.
- [ ] Confirm author names, affiliations, corresponding author, and any funding/conflict/ethics statements; do not invent details.
- [x] Create `docs/IEEE_MANUSCRIPT_AUTHOR_REVIEW_DRAFT.md` with the validated full-set values, statistical comparisons, simulation outcomes, limitations, attribution requirements, and references.
- [ ] Reconcile this Markdown author-review draft with the original DOCX manuscript and target venue template; perform a final independent table/number audit before release.
- [ ] Generate and inspect the final submission PDF. No final submission PDF has been created in this work session.
- [ ] Run a real similarity checker and record the tool and actual score; a target below 20% cannot be guaranteed.
- [x] Preserve primary benchmark, analysis, tests, lossless baseline, provenance workflow, pilot workflow, and manuscript/report documentation on `main`.
- [ ] Archive the final submission files and evidence against a fixed source revision after venue-specific finalization.

## Release rule
Do not label the manuscript or PDF submission-ready until the external/user-dependent publication items above are resolved and the final PDF has been inspected. The current experiments do not support clinical-safety or diagnostic-accuracy claims.
