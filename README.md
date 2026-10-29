# Deadline-aware medical image compression study

This repository is being initialized for a reproducible evaluation of adaptive compression for chest radiographs.

## Current status

- The original manuscript and experiment script were reviewed in the ChatGPT working environment.
- The original implementation's claimed refinement size was not a real encoded refinement stream; it has been replaced in the benchmark with a separately encoded residual payload whose byte count is measured.
- The benchmark evaluates JPEG and JPEG 2000 baselines, a mean-SSIM constrained method, a spatial-region quality-bound method, and a two-stage base-plus-residual method.
- Synthetic tests are software smoke tests only and are not research evidence.
- No clinical-safety claim is made from PSNR/SSIM.

## Dataset

The planned external test set is the Montgomery County chest X-ray set, obtained through the Hugging Face mirror `Famatsu123/montgomery-shenzhen-tuberculosis-cxr`. The repository's license metadata is listed as `other`; check the dataset card and preserve the original attribution before reuse. Do not commit the downloaded images to this repository.

Dataset page: https://huggingface.co/datasets/Famatsu123/montgomery-shenzhen-tuberculosis-cxr  
Original dataset paper: Jaeger et al., *Automatic tuberculosis screening using chest radiographs*, IEEE Transactions on Medical Imaging, 2014, DOI: 10.1109/TMI.2013.2284099.

## Reproducibility

The cloud workflow downloads data at run time, records the dataset/image counts and file modes, runs the benchmark, and publishes CSV/JSON results as a workflow artifact. The script records all fixed parameters. Network profiles are simulations, not measurements of a real network.

## Interpretation warning

Objective image metrics do not establish diagnostic safety. This is a compression/transmission engineering experiment, not a clinical validation study. Results must be reported only if the cloud workflow actually completes successfully on real images.
