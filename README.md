# Quality-Constrained and Deadline-Aware Compression of Chest Radiographs

This repository contains a reproducible evaluation of fixed JPEG and JPEG 2000 compression, a global-SSIM selector, a lung-mask regional selector, and a custom base-plus-residual representation. It evaluates 138 Montgomery County chest radiographs under three simulated bandwidth profiles with a 20-second delivery deadline. The benchmark runs in GitHub Actions, downloads the dataset at run time, and preserves the measured outputs and analysis needed to verify the paper.

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

The timestamps below are UTC. For tracked files, they are the committer timestamps of the latest commit touching that path on the current repository history. The two evidence-directory timestamps come from their immutable run metadata. Files created or updated for this cleanup PR use the UTC time the cleanup content was prepared.

| File | Purpose | Finalized (UTC) |
|---|---|---|
| `README.md` | Project overview, dependencies, reproduction instructions, provenance, and limitations. | 2026-10-30T06:22:35Z |
| `.gitignore` | Excludes Python bytecode, local virtual environments, and generated analysis output. | 2026-10-30T06:22:35Z |
| `benchmark_montgomery.py` | Primary image-compression benchmark; unchanged. | 2026-10-29 11:23:24 |
| `supplemental_lossless_baseline.py` | Supplemental reversible JPEG 2000 baseline. | 2026-10-29 12:56:50 |
| `analyze_results.py` | Validates committed outputs and computes paired statistical analysis. | 2026-10-29 15:58:14 |
| `requirements.txt` | Primary benchmark dependency list; unchanged. | 2026-10-29 10:46:10 |
| `tests/test_analyze_results.py` | Unit tests for analysis statistics and sensitivity calculations. | 2026-10-29 13:56:23 |
| `docs/DATASET.md` | Dataset provenance, input representation, attribution, and terms. | 2026-10-29 16:31:50 |
| `docs/EXPERIMENTS.md` | Experimental protocol and output definitions. | 2026-10-29 14:00:58 |
| `docs/EXPERIMENTAL_END_REPORT.md` | Evidence-audited experimental results and publication status. | 2026-10-30T06:22:35Z |
| `.github/workflows/benchmark.yml` | Full 138-image benchmark workflow; unchanged. | 2026-10-29 11:20:30 |
| `.github/workflows/lossless-baseline.yml` | Manually dispatched supplemental lossless baseline workflow. | 2026-10-30T06:22:35Z |
| `.github/workflows/provenance-check.yml` | Dataset provenance audit workflow; unchanged. | 2026-10-29 12:35:35 |
| `.github/workflows/analyze-results.yml` | Runs output validation/statistical analysis and uploads its artifact. | 2026-10-30T06:22:35Z |
| `.github/workflows/check-analysis.yml` | Compiles the analysis module and runs unit tests. | 2026-10-30T06:22:35Z |
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
