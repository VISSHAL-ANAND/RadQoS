# Publication Readiness Checklist

## Venue and template
- [ ] Confirm the exact target conference or journal. “IEEE format” alone does not identify a single template or page limit.
- [ ] Download the current official template from the IEEE Author Center and follow the venue's call for papers and submission instructions.
- [ ] Use the supplied `IEEEpaper.pdf` only as a visual reference: it is a six-page, two-column conference paper with title/author block, abstract, keywords, numbered sections, tables/figures, references, and an appendix.
- [ ] Do not force the manuscript to six pages unless the target venue requires that limit.
- [ ] Remove all template guidance text and placeholders before submission.

## Scientific integrity
- [ ] Every number in abstract, tables, figures, and conclusion must trace to a completed run output.
- [ ] State the dataset representation as the verified public 8-bit grayscale PNGs.
- [ ] Distinguish simulation from live-network measurement.
- [ ] Describe the P2 representation as a custom base-plus-residual format, not standards-compliant progressive JPEG 2000.
- [ ] Report infeasible quality constraints, fallback counts, deadline misses, and negative results.
- [ ] Do not claim clinical safety, diagnostic accuracy, or clinical utility without a suitable clinical evaluation.
- [ ] Verify dataset license/terms and attribution.
- [ ] Verify every citation and DOI against a primary source.
- [ ] Do not copy wording or results from the visual example paper.

## Technical presentation
- [ ] Abstract is a single self-contained paragraph, concise and within the target venue's word limit (IEEE conference guidance recommends up to 250 words).
- [ ] Title is specific and descriptive.
- [ ] Keywords reflect the actual contribution.
- [ ] Introduction states problem, gap, research question, and contributions.
- [ ] Related work distinguishes prior art from the present contribution.
- [ ] Methods include equations, parameters, candidate sets, fallback rules, dataset provenance, simulation assumptions, seeds, and software versions.
- [ ] Results separate image quality, payload size, delivery reliability, and quality available at deadline.
- [ ] Figures are legible in two columns and remain understandable in grayscale/print.
- [ ] Tables use consistent units and define abbreviations.
- [ ] Limitations and threats to validity are explicit.
- [ ] Conclusion makes only claims supported by results.

## Document validation
- [ ] Verify author names, affiliations, email, funding, conflicts, and acknowledgements with the author(s).
- [ ] Check headings, equations, cross-references, table/figure numbering, references, and page breaks.
- [ ] Inspect the exported PDF page by page for clipping, font issues, column overflow, and unreadable plots.
- [ ] Confirm DOCX and PDF agree.
- [ ] Use the target venue's PDF compliance tool if required.
- [ ] Run a suitable similarity check and report the actual score. Similarity percentage alone does not prove originality.
- [ ] Archive final manuscript, code commit, logs, CSVs, metadata, and figure-generation scripts.
