# Research Decisions and Open Questions

Last reconciled: 2026-10-29 UTC

This log records decisions that affect interpretation or reproducibility. It is not a substitute for implementation review or experimental evidence.

## D-001 — Evaluate the public 8-bit representation

**Decision:** Describe and evaluate the publicly distributed 8-bit PNG files verified by the provenance audit.

**Reason:** The audit reports 8-bit grayscale PNG headers for all 138 images in the official NLM directory, despite the original dataset paper describing 12-bit images.

**Consequence:** Do not claim native 12-bit preservation. Explain the discrepancy and identify the representation actually evaluated.

**Status:** Recorded; manuscript reconciliation remains required.

## D-002 — Keep source radiographs out of Git

**Decision:** Download dataset files at run time and do not commit source images or masks.

**Reason:** Avoid rehosting source data and keep the repository focused on code, documentation, and derived experiment outputs.

**Status:** Recorded.

## D-003 — Treat network delivery as simulation

**Decision:** Describe bandwidth/deadline results as simulated.

**Reason:** The current protocol models bandwidth profiles and latency; it does not measure a live network.

**Consequence:** Do not claim validated real-network performance without a separate real-network experiment.

**Status:** Recorded.

## D-004 — Treat P2 as a custom representation

**Decision:** Describe P2 as a custom JPEG 2000 base plus zlib-compressed signed residual.

**Reason:** It is not a standards-compliant progressive JPEG 2000 codestream.

**Consequence:** Report base and residual overhead separately and avoid implying standards compliance.

**Status:** Recorded.

## D-005 — Separate pilot evidence from full-set evidence

**Decision:** The five-image pilot is exploratory and must not be combined with the corrected 138-image benchmark.

**Reason:** The pilot used an older bandwidth-estimator initialization and is not directly comparable to the corrected full-set configuration.

**Status:** Recorded.

## D-006 — Do not claim clinical safety

**Decision:** Treat SSIM, PSNR, pixel error, and simulated delivery as technical measurements only.

**Reason:** No clinical reader study or downstream diagnostic-accuracy evaluation is documented.

**Status:** Recorded.

## Open decisions

- **OD-001:** Select the target IEEE venue and confirm its current official template/page limit.
- **OD-002:** Resolve dataset licensing/terms and attribution before submission.
- **OD-003:** Review the lognormal throughput parameterization and estimator variance assumptions against the actual code.
- **OD-004:** Decide how P2 is positioned (main method, ablation, or negative result) based on full-set results.
- **OD-005:** Decide which primary comparisons and multiplicity correction are prespecified in the final analysis.
- **OD-006:** Confirm author details, funding, conflicts, and institutional ethics wording.
