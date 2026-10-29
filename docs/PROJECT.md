# Project Definition

Last reconciled: 2026-10-29 UTC

## Purpose

Evaluate whether a deadline-aware image-compression pipeline can reduce chest-radiograph transmission cost while meeting explicit image-quality constraints, including constraints measured within annotated lung regions.

The study uses the public Montgomery County chest X-ray dataset and simulated network conditions. It is a technical compression-and-delivery study, not a clinical validation study.

## Research question

How do fixed compression, global-quality-constrained compression, lung-region-constrained compression, and a custom base-plus-residual strategy compare in encoded payload size, reconstruction quality, and simulated deadline delivery across specified bandwidth profiles?

## Planned methods

- B0: lossless JPEG 2000 reference baseline (supplemental experiment).
- B1: JPEG quality 75.
- B2: JPEG 2000 target ratio 20.
- B3: smallest measured JPEG 2000 payload meeting global mean SSIM >= 0.95; report infeasibility and fallback explicitly.
- P1: smallest measured payload meeting the specified lung-region local-SSIM and maximum-error constraints; lossless fallback if infeasible.
- P2: custom JPEG 2000 base plus zlib-compressed signed residual, with exact reconstruction of the normalized 8-bit reference checked.

The exact operational definitions must be taken from the implementation and experiment metadata when reporting results.

## Scope

In scope:
- Dataset provenance and input characteristics.
- Actual codec payload sizes and reconstruction metrics.
- Lung-mask-region quality constraints.
- Simulated delivery outcomes under fixed documented network profiles.
- Reproducible per-image analysis and appropriate statistical comparisons.

Out of scope:
- Claims of clinical diagnostic safety.
- Claims of improved diagnostic accuracy.
- Claims of performance on live networks unless separately measured.
- Claims of generalization to other datasets or modalities without additional experiments.

## Success criteria

The research is ready for manuscript finalization only when:
1. The primary full-dataset benchmark has a completed successful run or the study scope is explicitly revised.
2. Inputs, masks, parameters, and code revision are traceable.
3. Per-image results pass integrity and metric-range checks.
4. Summary tables are independently recomputed from raw outputs.
5. Statistical methods match outcome types and address multiplicity.
6. Every manuscript number maps to validated output.
7. Limitations, dataset representation, and simulated-network assumptions are explicit.
8. The target venue's current template and submission requirements are met.

## Main artifacts

- Implementation: `benchmark_montgomery.py`
- Primary workflow: `.github/workflows/benchmark.yml`
- Main README: `README.md`
- Current state: `docs/STATE.md`
- Task tracker: `docs/TASKS.md`
- Dataset facts: `docs/DATASET.md`
- Experimental design and outputs: `docs/EXPERIMENTS.md`
- Decisions and changes to assumptions: `docs/DECISIONS.md`
- Testing and validation: `docs/TESTING.md`
- Submission checklist: `docs/PUBLICATION.md`
