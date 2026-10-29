# Deadline-aware medical image compression study

This repository contains a reproducible engineering benchmark for deadline-aware compression of chest radiographs.

## Status and scope

- `benchmark.py` downloads the Montgomery County chest X-ray set from the official U.S. National Library of Medicine (NLM) public source at run time.
- It evaluates fixed JPEG quality settings and JPEG 2000 target rates when the installed Pillow build supports JPEG 2000.
- Two adaptive ablations are compared: (1) a global mean-SSIM threshold and (2) a worst-region bound using the fifth percentile of the local SSIM map within the union of the manual lung masks, plus a maximum absolute error limit.
- If no candidate satisfies the quality rule within the deadline byte budget, the selector chooses the best-scoring candidate that fits; if none fits, it returns the smallest candidate and records a deadline miss.
- It tests a genuine two-stage representation: a JPEG base image plus a separately encoded lossless PNG residual. The residual size is measured, and a round-trip assertion verifies exact reconstruction of the normalized 8-bit reference.
- It computes paired Wilcoxon comparisons, bootstrap confidence intervals for means, Wilson intervals for deadline-miss rates, and diagnostics for observed quality-versus-size monotonicity.
- No clinical-safety claim is made from PSNR, SSIM, or lung-mask-region metrics.

## Dataset and attribution

The Montgomery County CXR set contains 138 frontal chest radiographs (80 normal and 58 with TB-related manifestations) and manually segmented lung masks. The original publication describes the radiographs as 12-bit grayscale PNGs.

- Official NLM dataset directory: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/
- Dataset paper: Jaeger et al., *Two public datasets of chest X-ray images for computer-aided screening of pulmonary diseases*, Quantitative Imaging in Medicine and Surgery, 2014. https://pmc.ncbi.nlm.nih.gov/articles/PMC4256233/
- A Hugging Face mirror also exists: https://huggingface.co/datasets/Famatsu123/montgomery-shenzhen-tuberculosis-cxr. Its metadata says license `other`; the benchmark uses the official NLM source instead and retains the source attribution.

The benchmark does not commit or redistribute the image files. It records source image dimensions, mode, value range, normalization rule, and SHA-256 in `source_manifest.csv`. For codec comparisons, 12-bit source values are mapped to 8-bit with a fixed full-scale denominator of 4095; this information loss is an explicit limitation and must be considered when interpreting results.

## Reproducibility

The GitHub Actions workflow downloads the dataset, installs dependencies, runs the benchmark, publishes run logs/results to the repository, and uploads a workflow artifact. It records software versions and all fixed parameters. Network transfer times are calculated simulations at 1, 5, and 20 Mbps with a 10-second deadline and 50-ms fixed latency; they are not live-network measurements.

Outputs:
- `candidate_metrics.csv`: per-image, per-codec candidate sizes, PSNR/SSIM, lung-region SSIM, and maximum absolute error.
- `per_image_decisions.csv`: method/profile decisions and simulated deadline outcomes.
- `summary.csv`: aggregate results by method and network profile.
- `summary_confidence_intervals.csv`: bootstrap confidence intervals for metric means and Wilson intervals for deadline-miss rates.
- `paired_tests.csv`: exploratory paired Wilcoxon tests against fixed JPEG quality 75 (unadjusted p-values).
- `monotonicity_diagnostics.csv`: observed quality-versus-size monotonicity checks.
- `source_manifest.csv`: per-image source metadata and hashes.
- `run_manifest.json`: run settings, dataset counts, software details, and limitations.
- `run.log`: console log, including failures if the benchmark does not complete.

## Interpretation warning

The Montgomery set is small and not representative of all modalities, scanners, populations, or clinical tasks. PSNR/SSIM do not establish diagnostic safety, and this experiment does not measure downstream diagnostic accuracy. Network profiles are simulations. Any paper claims must match the run's actual outputs, and no numerical result should be reported until a successful real-image run has completed.
