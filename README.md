# Quality-Constrained and Deadline-Aware Compression of Chest Radiographs

This repository contains a reproducible evaluation of fixed JPEG and JPEG 2000 compression, a global-SSIM selector, a lung-mask regional selector, and a custom base-plus-residual representation. It evaluates 138 Montgomery County chest radiographs under three simulated bandwidth profiles with a 20-second delivery deadline. The benchmark runs in GitHub Actions, downloads the dataset at run time, and preserves the measured outputs and analysis needed to verify the paper.


## Related work and comparison

A closely related study is **MedROI: Codec-Agnostic Region of Interest-Centric Compression for Medical Images** by Jiwon Kim and Ikbeom Jang (April 2026). MedROI removes background voxels using an intensity-based tissue bounding box, stores compact spatial metadata, and then applies existing image codecs to the cropped region. It evaluates 200 T1-weighted brain MRI volumes from ADNI across six conventional and learned codec configurations, reporting compression-ratio and processing-time gains while maintaining ROI quality. Our study addresses a different, complementary question: how do practical compression and quality-selection strategies behave when chest radiographs must reach a receiver before a fixed delivery deadline under changing bandwidth? [Read MedROI on arXiv](https://arxiv.org/abs/2604.04511).

A second, especially relevant comparison is **Adaptive Region-Aware Compression for Healthcare Applications in O-RAN** (Osman, Badawy, and Salem, 2026), which jointly considers ROI/non-ROI quality, latency, and computational limits in an O-RAN healthcare transmission setting ([DOI: 10.1111/exsy.70246](https://doi.org/10.1111/exsy.70246)). The studies overlap in their concern for region-aware medical-image delivery, but differ in system scope and experimental setup.

| Comparison dimension | MedROI (Kim & Jang, 2026) | Adaptive Region-Aware Compression (Osman et al., 2026) | This study |
|---|---|---|---|
| Main focus | Remove non-tissue background before codec compression. | Joint ROI/non-ROI compression for healthcare fronthaul. | Compare compression and quality-selection strategies against a delivery deadline. |
| Images evaluated | 200 T1-weighted brain MRI volumes from ADNI. | Chest X-rays and bone-fracture X-rays. | 138 Montgomery County chest radiographs. |
| Region handling | Intensity-thresholded tissue bounding box, with metadata for spatial restoration. | Separate ROI and non-ROI regions with different quantisation. | Manual lung masks; local lung-region SSIM constraints on an 8×8 grid for P1. |
| Network/deadline model | Reports compression ratio and encoding/decoding time; not the same three-profile, 20-second delivery experiment. | Explicit end-to-end latency and O-RAN resource constraints. | Simulated 128 kbps, 512 kbps, and 2 Mbps profiles, 0.5-second latency, and a 20-second deadline. |
| Quality/evaluation | ROI reconstruction quality, compression ratio, and processing time. | Rate-distortion, latency/resource constraints, and reported diagnostic-accuracy evaluation. | PSNR, global SSIM, lung-region SSIM, error bounds, payload, and deadline outcomes; no clinical diagnostic-accuracy test. |
| What the comparison supports | A complementary ROI-preprocessing strategy, not a direct numerical baseline for our results. | A closely related latency-aware ROI framework; our experiments are a smaller, reproducible CXR codec/selector comparison rather than an O-RAN system evaluation. | Evidence about which tested methods meet the chosen image-quality constraints before the simulated deadline on this dataset. |

### What do our results show?

For the tested Montgomery County images and simulated network profiles, **P1 (lung-region-constrained JPEG 2000)** met its defined quality bound by the 20-second deadline for 100.0% of images on the good profile, 99.3% on moderate, and 75.4% on poor. The global-SSIM selector (B3) achieved 74.6%, 74.6%, and 66.7%, respectively. These are results from our own experiment, not a head-to-head comparison with MedROI or the O-RAN method.

| Method | Good bandwidth | Moderate bandwidth | Poor bandwidth |
|---|---:|---:|---:|
| B3 — global-SSIM selector | 74.6% | 74.6% | 66.7% |
| **P1 — lung-region-constrained selector** | **100.0%** | **99.3%** | **75.4%** |

**Does this solve the problem?** It provides a positive result for a narrow, measurable version of the problem: P1 improves the rate at which the selected lung-region quality bound is met before the simulated deadline, compared with the global-SSIM selector, on this 138-image dataset. It does **not** establish that the method is better than MedROI or the O-RAN framework, nor that it is ready for clinical deployment. Those claims would require a common-dataset, common-codec head-to-head experiment, real network measurements, broader multi-site data, and radiologist/diagnostic validation. The contribution should therefore be presented as a reproducible deadline-aware comparative evaluation, not as a universally superior compression algorithm.

## Dependencies

The recorded primary benchmark environment used **Python 3.12.15** (Python 3.12 is required) and these exact package versions, read from `results/run_metadata.json`:

| Package | Recorded version |
|---|---:|
| NumPy | 2.5.4 |
| pandas | 3.1.0 |
| Pillow | 13.0.0 |
| SciPy | 1.18.1 |
| scikit-image | 0.26.0 |
| huggingface_hub | 2.3.0 |

Package requirements by task:

- **Primary benchmark (`benchmark_montgomery.py`):** all six packages listed above.
- **Analysis and unit tests (`analyze_results.py`, `tests/`):** NumPy, pandas, and SciPy only.
- **Supplemental lossless baseline (`supplemental_lossless_baseline.py`):** NumPy, pandas, Pillow, and huggingface_hub.
- **Dataset acquisition:** an internet connection is required at run time to download the radiographs and lung masks from the Hugging Face dataset mirror. Source images and masks are not stored in this repository.

Install the benchmark environment with:

```bash
python -m pip install -r requirements.txt
```

For analysis and tests only:

```bash
python -m pip install numpy pandas scipy
```

## Repository contents

The timestamps below are UTC. For tracked files, they are the committer timestamps of the latest commit touching that path on the current repository history. The two evidence-directory timestamps come from their immutable run metadata. Files created or updated for the repository cleanup use the UTC time the cleanup content was prepared; the README's related-work addition is marked by its update date.

| File | Purpose | Finalized (UTC) |
|---|---|---|
| `README.md` | Project overview, related-work comparison, dependencies, reproduction instructions, provenance, and limitations. | Updated 2026-10-30 UTC |
| `.gitignore` | Excludes Python bytecode, local virtual environments, and generated analysis output. | 2026-10-30T06:25:43Z |
| `benchmark_montgomery.py` | Primary image-compression benchmark; unchanged. | 2026-10-29 11:23:24 |
| `supplemental_lossless_baseline.py` | Supplemental reversible JPEG 2000 baseline. | 2026-10-29 12:56:50 |
| `analyze_results.py` | Validates committed outputs and computes paired statistical analysis. | 2026-10-29 15:58:14 |
| `requirements.txt` | Primary benchmark dependency list; unchanged. | 2026-10-29 10:46:10 |
| `tests/test_analyze_results.py` | Unit tests for analysis statistics and sensitivity calculations. | 2026-10-29 13:56:23 |
| `docs/DATASET.md` | Dataset provenance, input representation, attribution, and terms. | 2026-10-29 16:31:50 |
| `docs/EXPERIMENTS.md` | Experimental protocol and output definitions. | 2026-10-29 14:00:58 |
| `docs/EXPERIMENTAL_END_REPORT.md` | Evidence-audited experimental results and publication status. | 2026-10-30T06:25:43Z |
| `.github/workflows/benchmark.yml` | Full 138-image benchmark workflow; unchanged. | 2026-10-29 11:20:30 |
| `.github/workflows/lossless-baseline.yml` | Manually dispatched supplemental lossless baseline workflow. | 2026-10-30T06:25:43Z |
| `.github/workflows/provenance-check.yml` | Dataset provenance audit workflow; unchanged. | 2026-10-29 12:35:35 |
| `.github/workflows/analyze-results.yml` | Runs output validation/statistical analysis and uploads its artifact. | 2026-10-30T06:25:43Z |
| `.github/workflows/check-analysis.yml` | Compiles the analysis module and runs unit tests. | 2026-10-30T06:25:43Z |
| `results/` | Immutable primary benchmark evidence: CSV outputs, run log, and metadata. | 2026-10-29 14:37:48.676341 |
| `lossless-results/` | Immutable supplemental lossless baseline evidence: CSV outputs, run log, and metadata. | 2026-10-29 13:54:33.671639 |

## Reproducing the results

1. **Primary benchmark:** open the [Real-image compression benchmark workflow](.github/workflows/benchmark.yml) in GitHub Actions and run it with `workflow_dispatch`, or make a benchmark-triggering change only when a new four-hour experiment is intended. The workflow sets `MAX_IMAGES=0` to process all 138 images. **Locally, the script defaults `MAX_IMAGES` to 30 when the environment variable is not set**; set `MAX_IMAGES=0` explicitly for the full dataset.
2. **Supplemental lossless baseline:** run the [Supplemental standalone lossless JPEG 2000 baseline workflow](.github/workflows/lossless-baseline.yml) manually with `workflow_dispatch`.
3. **Analysis:** run the [analysis workflow](.github/workflows/analyze-results.yml), or validate and analyze the committed evidence locally:

   ```bash
   python -m unittest discover -s tests
   python analyze_results.py --results-dir results --lossless-results-dir lossless-results --output-dir analysis-output
   ```

The committed primary and lossless results have been checked by the analysis pipeline: **Checks passed: 54, Checks failed: 0**. The analysis produces a quality-control report, adjusted paired-comparison table, and threshold-sensitivity table in `analysis-output/`.

## CAUTION — benchmark workflow runtime

Changing `benchmark_montgomery.py`, `requirements.txt`, or `.github/workflows/benchmark.yml` on `main` triggers the full benchmark workflow. It runs for about **4 hours** and publishes new results, overwriting the committed primary evidence. These files are deliberately unchanged by this cleanup.

## Dataset and attribution

The experiment uses the **Montgomery County chest X-ray set**, courtesy of the **U.S. National Library of Medicine (NLM)**. The benchmark downloads radiographs and manual lung masks at run time from a Hugging Face mirror; the source data are never committed here. The mirror's licence metadata is `other`, which is not a clear reuse licence. Follow the official NLM ReadMe and applicable terms, do not redistribute the images or masks, and do not imply NLM endorsement.

Cite both dataset papers:

1. S. Jaeger et al., “Automatic tuberculosis screening using chest radiographs,” *IEEE Transactions on Medical Imaging*, vol. 33, no. 2, pp. 233–245, Feb. 2014, doi: [10.1109/TMI.2013.2284099](https://doi.org/10.1109/TMI.2013.2284099).
2. S. Candemir et al., “Lung segmentation in chest radiographs using anatomical atlases with nonrigid registration,” *IEEE Transactions on Medical Imaging*, vol. 33, no. 2, pp. 577–590, Feb. 2014, doi: [10.1109/TMI.2013.2290491](https://doi.org/10.1109/TMI.2013.2290491).

The requested acknowledgement is **“Courtesy of the U.S. National Library of Medicine.”** Attribution does not indicate NLM endorsement. Review [docs/DATASET.md](docs/DATASET.md) for the source description, public 8-bit representation, provenance evidence, and use restrictions. If intended use is unclear, contact NLM before submission.

## Limitations

- The evaluation uses one dataset containing 138 radiographs; results may not generalize to other datasets, scanners, populations, or imaging tasks.
- The public images evaluated are 8-bit grayscale PNGs; the results do not establish preservation of native 12-bit data.
- Network conditions and deadline outcomes are simulated, not measured on a live network.
- PSNR and SSIM are objective image metrics and do not establish diagnostic safety or diagnostic accuracy.
- P2 is a custom JPEG 2000 base plus a separately compressed residual; it is **not** a standards-compliant progressive JPEG 2000 codestream.
