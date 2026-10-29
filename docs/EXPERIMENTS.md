# Experimental Protocol and Output Contract

Last reconciled: 2026-10-29 UTC

## Dataset unit

The intended primary evaluation uses all 138 Montgomery County radiographs and their manual left/right lung masks. A five-image pilot exists but is exploratory and must not be mixed with results from the corrected full-dataset configuration.

## Methods

- **B0 — Lossless JPEG 2000 reference:** supplemental standalone baseline; exact reconstruction is checked.
- **B1 — Fixed JPEG:** quality 75.
- **B2 — Fixed JPEG 2000:** target compression ratio 20.
- **B3 — Global-quality-constrained JPEG 2000:** choose the smallest measured payload meeting global mean SSIM >= 0.95; if infeasible, use the documented best-quality fallback and report infeasibility.
- **P1 — Lung-region-constrained JPEG 2000:** choose the smallest measured payload satisfying fifth-percentile local SSIM >= 0.95 over eligible cells in an 8×8 grid of lung-mask regions and maximum absolute error <= 24; use lossless JPEG 2000 if no lossy candidate satisfies the constraints.
- **P2 — Base plus residual:** custom JPEG 2000 base with a zlib-compressed signed residual; verify exact reconstruction of the normalized 8-bit reference. This is not a standards-compliant progressive JPEG 2000 codestream.

The codec candidate ratios documented by the README are `[4, 6, 8, 10, 15, 20, 30, 40, 60, 80, 120]`.

## Network simulation

Documented profiles use mean bandwidths of 128 kbps, 512 kbps, and 2 Mbps, lognormal throughput variation, a conservative bandwidth estimate, 0.5-second latency, and a 20-second delivery deadline. These are simulated conditions, not measurements from live networks.

The exact random seed, throughput parameterization, estimator initialization, draw order, software versions, and code commit must be taken from the completed run's metadata and source revision. Do not assume different runs are paired unless per-image/per-profile draws and order are verified to match.

## Outcomes

Report separately:
- Encoded bytes for each method and stage.
- Global image-quality metrics, including SSIM and PSNR where computed.
- Lung-region quality metrics and constraint feasibility.
- Maximum absolute reconstruction error where applicable.
- P2 base bytes, residual bytes, total bytes, base-stage delivery, and full-delivery outcomes.
- Simulated delivery time and deadline success/failure by image and profile.
- Lossless reconstruction correctness.
- Candidate-selection and codec monotonicity diagnostics.
- Fallback counts and all infeasible constraints.

For P2, quality available by the deadline may reflect only the base if the residual has not arrived. Label this separately from the quality of the final exact reconstruction.

## Expected primary outputs

- `results/quality_by_image.csv`
- `results/delivery_by_image_profile.csv`
- `results/candidate_diagnostics.csv`
- `results/summary.csv`
- `results/paired_comparisons.csv`
- `results/monotonicity_diagnostics.csv`
- `results/dataset_manifest.csv`
- `results/run_metadata.json`
- `results/run.log`

These are the documented output contract. Their existence and completeness must be verified from the actual completed run; documentation does not imply that a file has been generated.

## Expected row counts (verify against implementation)

The current task tracker expects 138 manifest rows, 552 quality rows, 1,518 candidate-diagnostic rows, 2,070 delivery rows, 15 summary rows, and 138 monotonicity rows. Treat these as validation expectations only; inspect the implementation and completed output schema before interpreting any mismatch.

## Statistical analysis

- Use image-level paired resampling for continuous paired metrics when pairing is justified.
- Use an appropriate paired binary-outcome test (e.g. exact McNemar) for paired deadline success/failure.
- Report discordant-pair counts for binary comparisons.
- Prespecify the comparison family or apply a multiplicity adjustment such as Holm.
- Report effect sizes, uncertainty intervals, denominators, and missing/infeasible cases.
- Recompute aggregate summaries from per-image records.
- Treat post-hoc threshold sensitivity as exploratory.
- Do not interpret statistical significance as clinical significance.

## Run acceptance criteria

A primary run is acceptable for manuscript use only after:
1. Workflow completion is successful.
2. All 138 images are accounted for exactly once per required method.
3. Mask/image mapping and provenance checks pass.
4. Constraints, fallbacks, and residual round trips are audited.
5. Output schemas and row counts match the implementation.
6. Summary values can be reproduced from raw per-image outputs.
7. Metadata identifies code revision, dependencies, parameters, seed, and timestamp.
8. Logs and artifacts are retained for reproducibility.
