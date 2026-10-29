# Deadline-aware adaptive compression of chest radiographs

This repository evaluates a quality-constrained, deadline-aware compression pipeline on real Montgomery County chest radiographs. The primary experiment is implemented in `benchmark_montgomery.py` and runs in GitHub Actions so no local laptop setup is required.

## Dataset

The benchmark uses the Hugging Face mirror `Famatsu123/montgomery-shenzhen-tuberculosis-cxr`, selecting the Montgomery subset and its manual left/right lung masks. The full Montgomery collection contains 138 frontal chest X-rays (80 normal and 58 with TB-related findings). The original source describes 12-bit grayscale PNGs.

- Hugging Face mirror: https://huggingface.co/datasets/Famatsu123/montgomery-shenzhen-tuberculosis-cxr
- Official NLM dataset directory: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/
- Dataset paper: Jaeger et al., *Two public datasets of chest X-ray images for computer-aided screening of pulmonary diseases*, Quantitative Imaging in Medicine and Surgery, 2014. https://pmc.ncbi.nlm.nih.gov/articles/PMC4256233/

The Hugging Face mirror reports its license metadata as `other`. Retain attribution and check the original source terms before reuse. Dataset images are downloaded at run time and are not committed to this repository.

## Methods

- **B1:** fixed JPEG quality 75.
- **B2:** fixed JPEG 2000 target ratio 20.
- **B3:** smallest JPEG 2000 candidate meeting global mean SSIM ≥ 0.95; if none meets the constraint, the highest-mean-SSIM candidate is selected.
- **P1:** smallest candidate meeting the fifth-percentile local SSIM bound over an 8×8 grid of lung-mask regions (threshold 0.95) and maximum absolute error ≤ 24; if none meets the bound, lossless JPEG 2000 is used.
- **P2:** deadline-aware JPEG 2000 base plus a separately encoded zlib-compressed signed residual. The residual is decoded and verified to reconstruct the normalized 8-bit reference exactly.

The codec candidate ratios are `[4, 6, 8, 10, 15, 20, 30, 40, 60, 80, 120]`. Network profiles are simulated with mean bandwidths of 128 kbps, 512 kbps, and 2 Mbps; throughput varies lognormally, a conservative lower-bound estimate is updated, latency is set to 0.5 s, and the first-stage/full-image deadline is 20 s. These are simulation settings, not measurements of live networks.

The original source images are preserved in the download cache, but the codec experiment evaluates 8-bit renditions. Integer sources in the range 0–4095 are mapped linearly to 0–255 using a fixed denominator of 4095. The manifest records source mode, dtype, range, dimensions, mask coverage, file size, and SHA-256. This is not a native-12-bit-preserving workflow.

## Reproduction

The main workflow downloads and evaluates all 138 Montgomery images by setting `MAX_IMAGES=0`. To run a smaller, reproducible pilot, set `MAX_IMAGES=30`; a fixed seed controls sampling. GitHub Actions publishes the result files and logs to the repository and uploads a downloadable artifact.

Expected outputs in `results/`:
- `quality_by_image.csv`: quality/size results for B1, B2, B3, and P1.
- `delivery_by_image_profile.csv`: simulated delivery and deadline outcomes for each method/profile/image.
- `candidate_diagnostics.csv`: per-image JPEG 2000 candidate sizes and quality metrics.
- `summary.csv`: aggregate results by method and network profile.
- `paired_comparisons.csv`: paired bootstrap confidence intervals and Wilcoxon comparisons.
- `monotonicity_diagnostics.csv`: empirical codec size/quality monotonicity checks.
- `dataset_manifest.csv`: source-image provenance and lung-mask metadata.
- `run_metadata.json`: fixed parameters and limitations.
- `run.log`: console output and any traceback if a run fails.

## Interpretation and limitations

The set is small and limited to chest radiographs; it does not represent all scanners, populations, modalities, or clinical tasks. PSNR/SSIM do not establish diagnostic safety, and the experiment does not measure downstream diagnostic accuracy. P2 is a custom base-plus-residual representation, not a standards-compliant progressive JPEG 2000 codestream. Network results are simulated. Report only outputs from a completed successful real-image run; do not fill manuscript tables from synthetic tests or assumed values.
