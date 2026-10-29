# Deadline-aware adaptive compression of chest radiographs

This repository evaluates a quality-constrained, deadline-aware compression pipeline on public Montgomery County chest radiographs. The benchmark runs in GitHub Actions so no local laptop setup is required.

## Dataset and attribution

The workflow downloads selected files from the public Hugging Face mirror of the Montgomery County chest X-ray set, which preserves the NLM collection and manual lung masks. It contains 138 frontal chest radiographs (80 normal and 58 with TB-related findings) and manual left/right lung masks. The original dataset paper describes the images as 12-bit grayscale PNGs. The dataset is downloaded at run time and is not committed to this repository.

- Hugging Face mirror: https://huggingface.co/datasets/Famatsu123/montgomery-shenzhen-tuberculosis-cxr
- Official NLM dataset directory: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/
- Dataset paper: S. Jaeger et al., “Automatic tuberculosis screening using chest radiographs,” *IEEE Transactions on Medical Imaging*, vol. 33, no. 2, pp. 233–245, Feb. 2014, doi: 10.1109/TMI.2013.2284099.
- Related dataset description: https://pmc.ncbi.nlm.nih.gov/articles/PMC4256233/

The Hugging Face mirror lists its licence metadata as `other`; review the dataset card and original NLM source terms, retain attribution, and cite the dataset paper. Do not commit the source images or masks to this repository.

## Methods

- **B1:** fixed JPEG quality 75.
- **B2:** fixed JPEG 2000 target ratio 20.
- **B3:** candidate with the smallest measured payload meeting global mean SSIM ≥ 0.95; if none meets the constraint, the highest-mean-SSIM candidate is selected and the infeasibility is visible in the results.
- **P1:** candidate with the smallest measured payload meeting the fifth-percentile local SSIM bound over an 8×8 grid of lung-mask regions (threshold 0.95) and maximum absolute error ≤ 24; if none meets the bound, lossless JPEG 2000 is used.
- **P2:** deadline-aware JPEG 2000 base plus a separately encoded zlib-compressed signed residual. The residual is decoded and verified to reconstruct the normalized 8-bit reference exactly.

The codec candidate ratios are `[4, 6, 8, 10, 15, 20, 30, 40, 60, 80, 120]`. Network profiles are simulated with mean bandwidths of 128 kbps, 512 kbps, and 2 Mbps; throughput varies lognormally, a conservative lower-bound estimate is updated, latency is set to 0.5 s, and the deadline is 20 s. These are simulation settings, not measurements of live networks.

A GitHub Actions provenance audit checked the PNG IHDR header of every image in the official NLM `CXR_png` directory: all 138 headers report 8-bit grayscale, with 97 images at 4,892×4,020 and 41 at 4,020×4,892. For five pilot radiographs and their ten left/right masks, the Hugging Face files were byte-identical to the official NLM files by SHA-256 and byte count; the five radiographs were 8-bit grayscale and the masks were 1-bit PNGs. This conflicts with the original dataset paper's description of the images as 12-bit grayscale. The benchmark therefore reports the publicly distributed 8-bit PNG representation and makes no native 12-bit preservation claim. The run manifest records each image's hash, size, mode, dtype, sample range, mapping, dimensions, and mask coverage.

## Reproduction

The current GitHub Actions workflow is configured to evaluate all 138 Montgomery images (`MAX_IMAGES=0`) in a cloud runner; it downloads the source images and masks at run time and decodes one image at a time to limit RAM use. For a faster preliminary pilot, set `MAX_IMAGES=30`; a fixed seed controls the random sample. A successful full-set run is still limited to this one dataset and does not establish clinical safety. GitHub Actions publishes result files and diagnostics to the repository and uploads a downloadable artifact.

Expected outputs in `results/`:
- `quality_by_image.csv`: quality/size results for B1, B2, B3, and P1.
- `delivery_by_image_profile.csv`: simulated delivery and deadline outcomes for each method/profile/image.
- `candidate_diagnostics.csv`: per-image JPEG 2000 candidate sizes and quality metrics.
- `summary.csv`: aggregate results by method and network profile.
- `paired_comparisons.csv`: paired bootstrap confidence intervals and Wilcoxon comparisons.
- `monotonicity_diagnostics.csv`: empirical codec size/quality monotonicity checks.
- `dataset_manifest.csv`: source-image provenance and lung-mask metadata.
- `run_metadata.json`: software versions, fixed parameters, timestamp and limitations.
- `run.log`: console output and any traceback if a run fails.

## Interpretation and limitations

The set is small and limited to chest radiographs; it does not represent all scanners, populations, modalities, or clinical tasks. PSNR/SSIM do not establish diagnostic safety, and the experiment does not measure downstream diagnostic accuracy. P2 is a custom base-plus-residual representation, not a standards-compliant progressive JPEG 2000 codestream. The base selector exhaustively evaluates candidate encodings and prioritizes the regional quality/error constraint among candidates predicted to meet the deadline; actual outcomes are evaluated using simulated bandwidth draws. Network results are simulated. Report only outputs from a completed successful real-image run; do not fill manuscript tables from synthetic tests or assumed values.
