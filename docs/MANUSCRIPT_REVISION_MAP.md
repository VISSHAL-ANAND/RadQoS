# Manuscript Revision Map

Target file recovered from Library: `IEEE_Manuscript_Quality_Constrained_Compression_DRAFT.docx` and matching PDF. Keep this as the working manuscript; do not rewrite from scratch.

## Required changes by section

### Front matter
- Replace title only after deciding whether P2 is a main method or a negative/ablation result. A conservative title should describe an empirical evaluation, not imply a new codec.
- Replace author/affiliation/email placeholders only with user-confirmed details.
- Confirm target venue, official template, paper length, and conference metadata. Never copy the example PDF's conference header, DOI, copyright line, or event branding.
- Keep abstract provisional until the primary full-set analysis passes QC. Final abstract must contain only final numbers and conclusions.

### Abstract and keywords
- Single self-contained paragraph; IEEE guidance recommends at most 250 words and 3–5 keywords/phrases.
- State that the input was the public 8-bit grayscale PNG representation, not native 12-bit data.
- State that network outcomes are simulated.
- Include one or two core numerical findings only after validated results exist.
- If results are negative, null, or mixed, state them plainly; do not imply superiority without evidence.

### I. Introduction
- Tighten the gap to the specific empirical question: measured JPEG 2000 candidate selection under a lung-mask-derived objective bound and a defined simulated deadline.
- Avoid claiming ROI coding, adaptive compression, or network-aware transmission is new.
- State contributions as a reproducible empirical evaluation, per-image measurement/provenance, and transparent delivery analysis.
- Define what this paper does not claim (clinical safety or diagnostic efficacy).

### II. Related Work
- Add verified prior work on lung-region/ROI JPEG 2000, regional artifacts in chest CT, network-aware medical transmission/JPIP, diagnosis-oriented learned compression, and limits of SSIM in diagnostic imaging.
- Verify all bibliographic metadata and claims against publisher/primary sources.
- Distinguish the current whole-image JPEG 2000 candidate selection based on a regional metric from actual ROI coding that allocates different bit rates to regions.

### III. Methods
- Resolve all 12-bit/8-bit wording: provenance audit reports all public NLM PNG headers as 8-bit grayscale; state the original paper's description and current-file observation separately.
- Include the completed standalone lossless JPEG 2000 baseline (B0) if its outputs pass validation and draw-order matching.
- Clarify that P2 is a custom base plus separately compressed signed residual, not JPIP or standards-compliant progressive JPEG 2000.
- Precisely define P1's grid, cell eligibility, regional percentile, max-error constraint, candidate set, and lossless fallback.
- Precisely describe the lognormal draw parameterization and estimator variance initialization. Current variance prior is approximate relative to the lognormal distribution; do not call it an exact match.
- State seed, source revision, software versions, codec settings, bandwidth profiles, latency, deadline, and all fallback rules.
- Explain PSNR's 99 dB reporting cap for exact reconstruction.

### IV. Results
- Replace the pending-results placeholder only after the primary run and QC pass.
- Report exact denominators, per-method payloads, quality metrics, P1 fallback count, and candidate monotonicity diagnostics.
- Separate unconditional codec quality from the reconstruction available by the deadline.
- For P2, report base bytes, residual bytes, total bytes, first-stage miss, full-delivery miss, and base-stage quality separately.
- Compare B0 against the other methods only if identical per-image/profile bandwidth draws are verified.
- Use the corrected analysis output with paired confidence intervals, exact McNemar tests for binary paired outcomes, and Holm-adjusted p-values.
- Include the threshold-sensitivity table, clearly labeled descriptive/post-hoc. Do not describe tested thresholds as clinically validated.

### V. Discussion
- Explain trade-offs rather than declaring a winner from one metric.
- Discuss whether P1's regional constraint earns its extra payload.
- If P2's residual overhead harms delivery, report that as a negative finding and consider moving P2 to an ablation/limitations section.
- Discuss lossless baseline deadline misses as a payload/deadline trade-off, not as evidence of clinical utility.
- Keep network results explicitly simulated.

### Limitations / validity / ethics
- One public dataset, 138 images, one modality and acquisition collection.
- Current public image files are 8-bit; no native 12-bit preservation claim.
- Synthetic network draws and fixed latency; no live traces, packet loss, or retransmission model.
- Objective metrics and hand-set constraints are not clinical acceptance criteria.
- No radiologist reader study or downstream diagnostic task.
- Verify dataset reuse terms and institutional requirements; do not assert an ethics exemption without confirmation.

### Conclusion
- Write last, after all results and statistics are frozen.
- State the measured trade-offs and the limits of inference.
- No unsupported claim that the proposed method is superior, diagnostically safe, or deployment-ready.

### References, figures, and final QA
- Add the verified primary literature listed in `docs/RELATED_WORK_AUDIT.md`; do not add references that are not cited.
- Every figure/table number and cross-reference must be checked after reflow.
- Figures should be readable at IEEE two-column size; include units and uncertainty where applicable.
- Inspect every page of the final DOCX/PDF. Check equations, column breaks, caption placement, font embedding, page count, references, and author metadata.
- Run the target venue's PDF compliance tool if required.
- Run a similarity checker; report the actual score and tool. The <20% target is not a guarantee and does not replace citation review.
