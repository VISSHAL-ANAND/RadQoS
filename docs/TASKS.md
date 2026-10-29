# Publication Tasks

Updated: 2026-10-29

## P0 — Recover and complete evidence
- [ ] Recheck status of primary run 40865016332: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40865016332
- [ ] After completion, inspect all job steps, full log, artifacts, and published output files.
- [ ] Confirm exactly 138 unique images were processed and all expected result files exist.
- [ ] Validate dataset manifest, per-image counts, mask coverage, source hashes, image dimensions, and software metadata.
- [ ] Confirm all residual round trips are exact; confirm P1 fallback count and whether quality constraints hold for all selected P1 outputs.
- [ ] If the primary run failed or timed out, identify the root cause from logs before changing code or retrying.
- [ ] Preserve and document the completed full-set lossless JPEG 2000 baseline (run 40877527634).

## P1 — Methodology and statistical review
- [ ] Audit that reported quality values distinguish unconditional codec quality from quality actually delivered by the deadline.
- [ ] Check whether the bandwidth estimator's assumed standard deviation matches the lognormal distribution's actual coefficient of variation; document or correct on a separate reviewed branch.
- [ ] Use a suitable paired test for binary outcomes (e.g. McNemar exact test where appropriate) instead of relying only on Wilcoxon signed-rank for binary paired outcomes.
- [ ] Account for multiple hypothesis tests (e.g. Holm correction) or explicitly label exploratory analyses.
- [ ] Verify confidence intervals are paired by image and describe bootstrap procedure and seed.
- [ ] Report infeasible constraints and fallbacks transparently.
- [ ] Compare B1/B2/B3/P1/P2 with the supplemental lossless baseline only where metrics and simulation assumptions are aligned.
- [ ] Decide whether P2 is a useful contribution or should be presented as a negative/ablation result based on full data.
- [ ] Add a limitations section that explicitly states the dataset is one small public collection, the network is simulated, and no clinical diagnostic safety was evaluated.

## P2 — Literature, provenance, and reproducibility
- [ ] Verify every bibliographic record, DOI, URL, and claim against primary sources.
- [ ] Expand related work on image compression, JPEG 2000, ROI-aware quality, image transmission under deadlines, and reproducible evaluation.
- [ ] Verify license and terms of use for the original NLM dataset and mirror; preserve attribution.
- [ ] Record exact dependency versions, runner environment, run timestamp, seed, codec settings, and code commit SHA in the manuscript/supplement.
- [ ] Add or verify an experiment reproduction guide and output schema.
- [ ] Ensure any released figures are generated directly from final CSVs and have accessible labels.

## P3 — Manuscript and submission
- [ ] Locate and inspect the prior manuscript draft from conversation/library if it exists; do not assume it is in the repository.
- [ ] Confirm target conference/journal, exact official template, page limit, and submission rules.
- [ ] Confirm author names, affiliations, emails, corresponding author, funding, conflicts, and acknowledgements; do not invent these.
- [ ] Draft abstract only after final results are locked.
- [ ] Align title, contributions, equations, tables, plots, discussion, limitations, and conclusion with actual evidence.
- [ ] Format using the official template for the target venue; use the uploaded six-page PDF only as a visual reference.
- [ ] Validate the DOCX and exported PDF page-by-page.
- [ ] Check all in-text citations against the reference list and verify citation order/format.
- [ ] Run a suitable similarity checker; report the actual result and limitations, not an assumed percentage.
- [ ] Complete a final submission checklist and archive the code, metadata, data provenance, results, and manuscript version.

## Exit criteria
Do not call the paper submission-ready until the primary experiment is either completed and reproducible or the manuscript has been redesigned to reflect a smaller, explicitly scoped study; all reported values trace to evidence; the target venue rules are followed; and the final DOCX/PDF has been inspected.
