# Interaction Log

## 2026-10-29 — Experimental evidence and publication readiness

### Primary benchmark
- Confirmed successful full-set workflow: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40865016332
- Code commit: `b8ead4566b07cf2130a3f06546392c6c739fa44b`; 138 real images; seed 42; 11 candidate settings; `synthetic=false`.
- Verified expected output counts, table keys, image/mask coverage, metric ranges, summary recomputation, P1 constraint satisfaction, and successful run completion.
- Confirmed the standalone lossless baseline reconstructs all 138 normalized 8-bit inputs exactly and uses identical per-image/profile throughput draws to the primary run.

### Statistical analysis
- Original analysis workflow: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906476864
- QC report: 54 checks passed, 0 failed.
- Used 2,000 paired image-level bootstrap resamples with seed 42, Wilcoxon tests for continuous paired metrics, exact McNemar tests for paired binary outcomes, and Holm correction across 19 comparisons.
- Corrected the P2 paired binary mean-difference output schema.
- Re-ran corrected analysis: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906893245
- Re-ran analysis unit tests: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906898568
- Updated STATE and TASKS to remove stale claims that the schema fix remained pending.

### Report and integrity notes
- Added `docs/EXPERIMENTAL_END_REPORT.md` with measured results, methods, statistics, limitations, provenance, and references.
- Public NLM PNG headers indicate 8-bit grayscale across 138 images, while the original paper describes 12-bit. Results are scoped to the public 8-bit representation.
- All deadline outcomes are simulated. The experiment does not establish diagnostic safety or clinical performance.
- The mirror license metadata is `other`; applicable reuse terms still require review.
- No final submission PDF or similarity-check score exists in this work session.
- Consolidated branch content: PR #1 publication analysis/docs, PR #2 lossless baseline artifacts, PR #3 provenance audit workflow, and PR #4 pilot workflow were merged into `main`. All four PRs merged successfully.
- The four non-main branch refs remain present. This session's GitHub action set does not expose branch deletion, so delete those refs in GitHub after checking `main` contains the preserved files.


### 2026-10-29 — Manuscript integration and branch verification
- Added `docs/IEEE_MANUSCRIPT_AUTHOR_REVIEW_DRAFT.md` with the verified full-set results, methods, statistics, simulated delivery outcomes, limitations, dataset attribution, and reference list.
- Added/updated `docs/RELATED_WORK_AUDIT.md` with source-grounded citation roles and limits on novelty claims.
- Linked both documents from README and reconciled TASKS/STATE.
- Verified manuscript and citation-audit files exist on `main`.
- After PRs #1–#4 were merged, the available branch listing returned only `main`; the four working branch refs no longer appear.
- A final submission PDF is still not present. The document-generation operation remains unavailable in this session; no PDF, similarity score, or venue-compliance certification is claimed.
