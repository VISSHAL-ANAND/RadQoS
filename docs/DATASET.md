# Dataset and Provenance

Last reconciled: 2026-10-29 UTC

## Source and composition

The benchmark targets the Montgomery County chest X-ray dataset. The repository README documents 138 frontal radiographs: 80 normal and 58 with TB-related findings, with manual left/right lung masks.

Sources:
- Official NLM dataset directory: https://data.lhncbc.nlm.nih.gov/public/Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/
- Public Hugging Face mirror used by the workflow: https://huggingface.co/datasets/Famatsu123/montgomery-shenzhen-tuberculosis-cxr
- Dataset paper: S. Jaeger et al., “Automatic tuberculosis screening using chest radiographs,” IEEE Transactions on Medical Imaging, vol. 33, no. 2, pp. 233–245, Feb. 2014, doi: 10.1109/TMI.2013.2284099.
- Related description: https://pmc.ncbi.nlm.nih.gov/articles/PMC4256233/

## Input representation and discrepancy

The original dataset paper describes the images as 12-bit grayscale PNGs. The repository's provenance audit inspected the PNG IHDR headers of all 138 images in the official NLM `CXR_png` directory and reported 8-bit grayscale for all images:
- 97 images: 4,892 × 4,020
- 41 images: 4,020 × 4,892

A five-image/ten-mask comparison reported byte-identical mirror and NLM files by SHA-256 and byte count. The five radiographs were 8-bit grayscale and the masks were 1-bit PNGs.

The evaluated representation must therefore be described as the publicly distributed 8-bit PNG representation. Do not claim native 12-bit preservation or silently infer that the public files contain 12-bit pixel values.

## Runtime acquisition and repository hygiene

The primary workflow downloads the selected image/mask files at run time. Do not commit or rehost source radiographs or masks in this repository. Record source identifiers, file hashes, sizes, dimensions, pixel mode/dtype/range, mapping, and mask coverage in the run manifest where the implementation provides them.

## Licensing and attribution

The mirror lists its license metadata as `other`. This is unresolved. Before submission or redistribution, review the mirror dataset card and original NLM source terms, retain attribution, and do not assume a license permission that has not been verified.

## Data-quality checks required for a full run

- Exactly 138 unique radiographs are represented.
- Each image maps to its expected left and right masks.
- Image and mask dimensions align after the documented preprocessing.
- Image hashes and source metadata are recorded.
- Pixel mode, dtype, and sample range are consistent with the declared input representation.
- Mask coverage is nonzero and within expected bounds.
- Any missing, malformed, or excluded file is explicitly recorded.

## Limitations

This dataset is limited in size and source. Results do not establish performance across all scanner vendors, patient populations, imaging protocols, or clinical tasks. Image-quality metrics do not establish clinical safety or diagnostic adequacy.
