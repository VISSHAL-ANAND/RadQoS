# Testing and Validation Plan

Last reconciled: 2026-10-29 UTC

## Levels of validation

### 1. Unit tests

Test isolated helper functions and analysis utilities, including:
- Summary calculations against hand-computed examples.
- Duplicate/missing-key detection.
- Metric-range validation.
- Paired bootstrap resampling behavior and deterministic seed handling.
- Paired binary-outcome tests and discordant-pair calculations.
- Holm adjustment.
- Threshold-sensitivity calculations.
- Error handling for missing files, columns, or malformed records.

Record the exact test command, code commit, and exit status. A passing unit suite does not validate the full benchmark.

### 2. Codec and reconstruction tests

- Verify B0 and P2 reconstruction against the declared normalized 8-bit reference.
- Record maximum absolute error and exact-equality outcomes.
- Verify payload byte counts against actual encoded files or buffers.
- Test constraint satisfaction and infeasible-candidate fallback behavior.
- Verify masks align with image coordinates and regional eligibility is applied consistently.

### 3. Dataset integrity tests

- Check 138 unique images.
- Check expected mask mappings and dimensions.
- Check file hashes and source provenance.
- Check mode, dtype, pixel range, and mask coverage.
- Record every excluded or malformed input.

### 4. Full-run acceptance

- Verify workflow success and inspect every job step.
- Verify all expected outputs exist and are nonempty.
- Verify expected keys and row counts against the implementation.
- Recompute summaries independently from raw CSVs.
- Check for NaN/Inf values, duplicate records, impossible payload sizes, invalid metric ranges, and inconsistent fallback counts.
- Verify run metadata matches the source commit and fixed parameters.
- Retain logs, artifacts, manifest, raw CSVs, and code revision.

### 5. Statistical checks

- Confirm continuous paired comparisons use the same images and justified pairing.
- Confirm binary paired outcomes use a suitable test such as exact McNemar and report discordant pairs.
- Apply the prespecified multiplicity policy.
- Confirm bootstrap resampling unit is the image, with fixed seed and stated number of replicates.
- Distinguish exploratory sensitivity analysis from confirmatory inference.

## Reporting rule

Do not describe a test as passed unless its result is available. Distinguish unit-test success, pipeline smoke tests, codec correctness, and successful full-dataset execution. A completed workflow alone is not sufficient unless the produced results pass the acceptance checks.
