# Interaction Log

## 2026-10-29 — Experimental evidence reconciliation

### User goal
Complete the pending research work in one continuous effort, with the full experimental report based on actual results and without inventing values.

### Primary benchmark recheck
- Inspected the primary workflow: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40865016332
- Confirmed success on code commit `b8ead4566b07cf2130a3f06546392c6c739fa44b`.
- Confirmed run metadata timestamp, software versions, seed, parameters, and `synthetic=false`.
- Confirmed expected output row counts and matching image sets from the publication-analysis QC workflow.
- Confirmed 54 QC checks passed and 0 failed, including independent summary recomputation, zero P1 fallback, exact lossless reconstruction, and identical per-image/profile throughput draws between primary and lossless runs.

### Statistical analysis
- Triggered the existing analysis workflow on `publication-readiness` after the completed primary results were available.
- Workflow: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40906476864
- Generated adjusted paired comparisons and candidate-based threshold sensitivity.
- Used 2,000 paired image-level bootstrap resamples with seed 42; Wilcoxon tests for continuous P1/B3 comparisons; exact McNemar tests for paired binary outcomes; Holm adjustment across 19 comparisons.
- Found an analysis-output schema issue: P2 binary mean differences are stored under a separate column name while the common `mean_difference` column is blank. The numerical differences are present, but normalize the schema before final archival.

### Documentation
- Added `docs/EXPERIMENTAL_END_REPORT.md` with full-set results, statistical results, limitations, references, and publication-readiness checklist.
- Updated project state and task tracker to replace the stale “primary run in progress” status.
- No changes were made to primary benchmark outputs; no merge to `main` was performed.

### Remaining work
- Normalize statistical output schema and rerun tests/analysis.
- Complete dataset-terms and literature/reference review.
- Update existing manuscript draft, confirm venue and author/declaration details, then format and inspect final DOCX/PDF.
- DOCX/PDF generation and page-by-page inspection have not yet been completed in this conversation.
