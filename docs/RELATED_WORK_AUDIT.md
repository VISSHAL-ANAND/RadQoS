# Related-Work and Citation Audit

Updated: 2026-10-29

## Verified primary references and relevance

1. **Jaeger et al., IEEE Transactions on Medical Imaging, 2014, DOI 10.1109/TMI.2013.2284099.** Source dataset and tuberculosis-screening context. Cite for the Montgomery collection and original screening context; not as evidence that compressed images are clinically safe.
2. **Jaeger et al., Quantitative Imaging in Medicine and Surgery, 2014, DOI 10.3978/j.issn.2223-4292.2014.11.20.** Public dataset overview.
3. **Candemir et al., IEEE Transactions on Medical Imaging, 2014, DOI 10.1109/TMI.2013.2290491.** Lung segmentation in chest radiographs. The official NLM ReadMe asks Montgomery dataset users to cite this publication.
4. **Liu et al., Information, 2017, DOI 10.3390/info8040131.** Review of compression standards in medical imaging; background rather than direct validation of the methods in this study.
5. **Wang et al., IEEE Transactions on Image Processing, 2004, DOI 10.1109/TIP.2003.819861.** Foundational SSIM reference; not evidence of clinical adequacy.
6. **Pambrun and Noumeir, IEEE ICIP 2015, pp. 2960–2963, DOI 10.1109/ICIP.2015.7351345.** Discusses limitations of SSIM in diagnostic-imaging contexts. Supports caution against treating SSIM as a clinical acceptance test.
7. **Noumeir and Pambrun, Journal of Digital Imaging, 2011, DOI 10.1007/s10278-010-9343-0.** Studies use of the JPEG 2000 interactive protocol for streaming large images or image sets. The present implementation does not implement JPIP.
8. **NLM Montgomery dataset ReadMe.** Gives source attribution, required citations to Jaeger et al. and Candemir et al., and the instruction not to share the dataset outside the user's research group/organization.
9. **NLM Terms and Conditions.** Requires acknowledgement of NLM source and prohibits implying NLM endorsement. This is not a dataset redistribution licence.

## Claims intentionally not made
- No claim that SSIM, PSNR, regional SSIM, or maximum absolute error establishes diagnostic safety.
- No claim that the selector or adaptive compression is the first or novel method of its kind.
- No claim of native 12-bit preservation: audited public PNGs are 8-bit grayscale.
- No claim of real-world network performance: throughput and deadline outcomes are simulated.
- No claim that the custom base-plus-residual format is standards-compliant progressive JPEG 2000.
- No claim that mirror licence metadata “other” is a clear licence grant.

## Literature coverage limitation
The sources support dataset context, compression-standard background, SSIM background and limitations, and JPEG 2000 interactive streaming. This is a focused reference set, not proof of exhaustive literature coverage. Before submission, search the target venue's indexing resources for additional ROI-based medical-image compression, task-based compression evaluation, clinical reader studies, and network-aware medical-image delivery. Any added claim must be tied to a source actually reviewed.

## Source links
- NLM dataset ReadMe: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/MontgomerySet/NLM-MontgomeryCXRSet-ReadMe.pdf
- NLM dataset directory: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/
- NLM terms: https://www.nlm.nih.gov/databases/download/terms_and_conditions.html
- IEEE author guidance on paper structure: https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/structure-your-paper/
- Pambrun and Noumeir record: https://espace2.etsmtl.ca/id/eprint/12070/
- Liu et al.: https://www.mdpi.com/2078-2489/8/4/131
