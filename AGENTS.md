# Repository Working Rules

## Purpose
This repository evaluates deadline-aware adaptive compression of public Montgomery County chest radiographs. Its results may support a research manuscript, so reproducibility and evidence traceability take priority over favorable-looking outcomes.

## Before changing code
1. Read `README.md`, this file, `docs/STATE.md`, and the active tasks in `docs/TASKS.md`.
2. Read relevant protocol, dataset, testing, and decision documents before changing benchmark behavior.
3. Inspect the current branch, recent commits, workflow status, and Git diff before editing.
4. Preserve working history and do not overwrite completed experiment evidence.

## Research integrity
- Never invent, estimate, or backfill experimental values.
- Distinguish pilot results, completed full-dataset runs, simulations, and unit tests.
- Every manuscript number must trace to a raw output from a completed run.
- Record code revision, parameters, seed, software versions, and dataset provenance.
- Describe the public image representation actually evaluated; do not claim native 12-bit preservation when using verified 8-bit PNGs.
- Clearly label simulated network outcomes.
- Do not claim clinical safety or diagnostic accuracy without suitable clinical validation.
- Report negative results, infeasible constraints, fallback cases, and limitations.

## Dataset handling
- Download source radiographs and masks at runtime; do not commit or rehost them.
- Retain attribution and verify dataset source terms before publication or redistribution.
- Preserve provenance and mask-alignment checks.

## Experimental changes
- Do not cancel or replace a running experiment without inspecting its latest state and preserving available artifacts.
- Do not mix pilot outputs with corrected full-dataset results.
- Validate raw output schemas and recompute aggregates independently.
- Use statistically appropriate paired tests and state the multiplicity policy.

## Documentation maintenance
- Update `docs/STATE.md` when verified project state changes.
- Update `docs/TASKS.md` when tasks are completed, blocked, or reprioritized.
- Record material methodological changes in `docs/DECISIONS.md`.
- Update protocol/testing documentation when implementation behavior changes.
- Keep the README concise and link to focused documents rather than duplicating every detail.
- Do not mark an action complete until the resulting artifact or test output has been verified.

## Branch safety
- Work on a dedicated review branch for publication-support changes.
- Do not merge to `main` or alter the primary benchmark results without review.
- Do not commit secrets, credentials, or private information.
