# Publication Tasks

Updated: 2026-10-29

## P0 — Recover and complete experimental evidence
- [ ] Recheck primary run 40865016332: https://github.com/VISSHAL-ANAND/research-papper/actions/runs/40865016332
- [ ] When it finishes, inspect all job steps, full logs, artifacts, and published output files.
- [ ] Confirm 138 unique images, matching image/mask dimensions, and two masks per image.
- [ ] Check expected primary output counts: manifest 138 rows; quality 552 rows; candidate diagnostics 1,518 rows; delivery 2,070 rows; 15 summary rows; paired-comparison rows per configured test; monotonicity diagnostics 138 rows.
- [ ] Validate duplicate keys, missing values, metric ranges, file sizes, source hashes, mask coverage, software metadata, and residual round trips.
- [ ] Confirm P1 fallback count and constraint feasibility; report infeasible cases transparently.
- [ ] If the primary run fails/times out, diagnose logs before modifying code or rerunning.
- [ ] Preserve completed full-set lossless baseline run 40877527634 and its artifact.

## P1 — Methods/statistics audit
- [ ] Review exact lognormal throughput parameterization and correct/document the approximate variance prior.
- [ ] Use suitable paired binary-outcome inference (e.g., exact McNemar test) with discordant-pair counts where applicable.
- [ ] Apply a prespecified multiple-comparison correction such as Holm, or explicitly classify all tests as exploratory.
- [ ] Verify paired bootstrap CIs are paired by image, with fixed seed and stated resampling unit.
- [ ] Separate unconditional encoded-image quality, base-stage quality, and quality available by deadline.
- [ ] Report first-stage and full-delivery misses separately for P2; report base, residual, and total bytes.
- [ ] Compare B1/B2/B3/P1/P2 against lossless B0 only where input, draw order, and metric definitions align.
- [ ] Decide whether P2 should remain a main method or be framed as a negative/ablation result based on full-set outcomes.
- [ ] Consider sensitivity analysis for regional grid size, percentile, SSIM threshold, max-error threshold, and random seed; do not tune on the same result and claim confirmatory evidence without qualification.

## P2 — Literature, provenance, reproducibility
- [ ] Expand related work with primary research on ROI-based JPEG 2000, medical image compression, JPIP/network-aware transmission, diagnostic compression evaluation, and SSIM limitations.
- [ ] Verify every citation, DOI, publication year, volume/pages, and claim against primary sources.
- [ ] Verify original NLM dataset terms and mirror license metadata; retain attribution and do not rehost image files.
- [ ] Record exact code commit, dataset source/revision, dependency versions, seed, parameters, and run timestamp.
- [ ] Recompute summaries from per-image CSVs and confirm output files match the README schema.
- [ ] Generate plots/tables from final validated CSVs, with uncertainty intervals and denominators.

## P3 — Manuscript and submission
- [ ] Update existing Library draft `IEEE_Manuscript_Quality_Constrained_Compression_DRAFT.docx`; do not recreate from scratch.
- [ ] Reconcile the draft with newer provenance audit and successful lossless baseline.
- [ ] Confirm exact target venue, current official template, page limit, and submission rules.
- [ ] Confirm author names, affiliations, emails, corresponding author, funding, conflicts, acknowledgements, and institutional ethics wording; never invent details.
- [ ] Write final abstract/results/conclusion only after final primary results are locked.
- [ ] Verify every number in abstract, tables, plots, discussion, and conclusion against the same run outputs.
- [ ] Format to official venue template; use uploaded PDF only as a visual reference.
- [ ] Inspect DOCX and exported PDF page-by-page for clipping, font embedding, column overflow, equation rendering, figure legibility, references, and page count.
- [ ] Run a suitable similarity checker; report actual score and tool, not an assumed percentage.
- [ ] Archive manuscript, source, scripts, logs, CSVs, metadata, figures, and exact code commit for reproducibility.

## Exit criteria
Do not call the paper submission-ready until the primary experiment is completed and validated (or the study is explicitly rescoped), every reported value traces to evidence, related work and references are verified, venue rules are met, and the final DOCX/PDF has been inspected.
