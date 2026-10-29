# Initial Methods and Statistics Audit

Status: initial code-reading review; no code changes or local tests were performed as part of this audit. Revalidate against the final benchmark commit and outputs.

## Confirmed design choices
- The benchmark evaluates real public Montgomery PNGs and manual left/right masks; it explicitly refuses to continue if a selected image has no mask.
- Source images are decoded one at a time to limit memory.
- Codec payload sizes are measured from actual encoded bytes.
- P1's fallback to lossless JPEG 2000 is explicit in per-image output.
- P2 residual round trips are checked against the normalized 8-bit reference.
- Network results are simulated, and the README correctly warns that PSNR/SSIM do not establish diagnostic safety.
- The primary summary includes separate first-stage and full-delivery miss rates.

## Issues to resolve before publication
### 1. Primary run status and outputs
The active primary benchmark run (40865016332) was still in progress at the last check. No results artifact was available then. Do not use the older committed log ending at image 19/138 as full-set evidence.

### 2. Statistical test for binary paired outcomes
The current script applies Wilcoxon signed-rank comparisons to binary paired metrics such as `full_delivery_miss` and `quality_bound_met_by_deadline`. For paired binary outcomes, consider an exact McNemar test (with discordant-pair counts) instead. Keep paired bootstrap confidence intervals for risk/rate differences if appropriately implemented.

### 3. Multiple comparisons
The script reports multiple tests: four P1-vs-B3 metrics and two P2-vs-P1 metrics for each of three profiles. The p-values are unadjusted. Apply a prespecified correction such as Holm's method, or clearly label the tests exploratory and report the multiplicity limitation.

### 4. Lognormal bandwidth calibration
The simulator draws throughput as `mean * exp(N(0, sigma^2)) / exp(sigma^2/2)`. This preserves the configured mean, but its coefficient of variation is `sqrt(exp(sigma^2)-1)`, not exactly `sigma`. The estimator initializes variance as `(sigma * mean)^2`; this is an approximation, not an exact match to the distribution's variance. Either initialize with the exact lognormal variance or explicitly describe the estimator as an approximate prior and test sensitivity.

### 5. Deadline-conditioned quality interpretation
The delivery summary computes quality metrics for the image/reconstruction available by the deadline. For P2, when the base arrives but the residual does not, the metrics describe the base reconstruction, not the exact final reconstruction. Manuscript tables and captions must distinguish:
- full encoded representation's nominal quality;
- quality of the base stage;
- reconstruction actually available at the deadline;
- whether the residual completed.
Avoid presenting these as one interchangeable “quality” metric.

### 6. P2 contribution and fairness
P2 uses a custom base-plus-residual format, not a standardized progressive JPEG 2000 stream. Its full payload includes the separately compressed residual; its first-stage payload is only the base. The paper must report both sizes and both deadline outcomes. If full-set results show large residual overhead or poor deadline performance, report that honestly and reconsider whether P2 belongs as a main proposed method or a negative/ablation result.

### 7. P1 regional constraint definition
The implementation computes a full-image SSIM map, averages map values inside each eligible 8x8-grid cell's lung-mask pixels, and takes the fifth percentile across eligible cells. Cells require at least 5% mask coverage. State this precisely; do not describe it as a clinical ROI metric or assume that all local image structures are clinically important.

### 8. Dataset precision
The provenance audit indicates public PNGs are 8-bit grayscale, contrary to the original dataset paper's 12-bit description. Report the representation actually evaluated; no claim of native 12-bit preservation is supported.

### 9. Supplemental lossless baseline
Run 40877527634 completed on all 138 images with exact lossless JPEG 2000 round trips. Mean payload was 3,854,278 bytes, median 3,801,277.5 bytes, mean compression ratio 5.3118:1, median encode time 0.7038 s. Simulated full-delivery miss rates were 100% at 128 kbps, 99.2754% at 512 kbps, and 26.087% at 2 Mbps. This baseline is valuable, but ensure the main and supplemental runs use aligned data ordering, random draws, and definitions before making paired comparisons.

## Required validation
- Confirm final run outputs agree with the documented counts and method names.
- Verify summary values can be recomputed from per-image CSVs.
- Check that paired comparisons use matching image keys and handle missing values explicitly.
- Re-run tests after any methodology change.
- Preserve logs, metadata, and the code commit SHA used for final reported values.
