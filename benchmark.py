#!/usr/bin/env python3
"""Reproducible benchmark for deadline-aware compression of Montgomery chest radiographs.

Images are normalized to 8-bit for JPEG/JPEG2000 codec comparison. The original
12-bit source values and normalization rule are recorded in the manifest. This is
an engineering benchmark; objective metrics are not evidence of clinical safety.
"""
from __future__ import annotations

import csv
import hashlib
import html.parser
import io
import json
import math
import os
import platform
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import PIL
from PIL import Image, features
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

BASE_URL = (
    "https://data.lhncbc.nlm.nih.gov/public/"
    "Tuberculosis-Chest-X-ray-Datasets/Montgomery-County-CXR-Set/MontgomerySet/"
)
DATA_ROOT = Path(os.environ.get("DATA_ROOT", "data/MontgomerySet"))
OUT = Path(os.environ.get("RESULTS_DIR", "results"))
JPEG_QUALITIES = [25, 40, 50, 60, 70, 75, 85, 90, 95]
JP2_RATES = [20, 10, 5, 3, 2, 1]
QUALITY_THRESHOLD = 0.95
ROI_PERCENTILE = 5
MAX_ABS_ERROR_LIMIT = 24
BANDWIDTHS_MBPS = [1, 5, 20]
DEADLINE_SECONDS = 10.0
FIXED_LATENCY_SECONDS = 0.05
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 20261029
EXPECTED_IMAGES = 138


class LinkParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            for key, value in attrs:
                if key.lower() == "href" and value:
                    self.links.append(value)


def fetch_bytes(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "research-reproducibility-benchmark/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def list_png_urls(index_url: str) -> list[str]:
    body = fetch_bytes(index_url).decode("utf-8", errors="replace")
    parser = LinkParser()
    parser.feed(body)
    urls = []
    for href in parser.links:
        if href.lower().split("?")[0].endswith(".png"):
            urls.append(urljoin(index_url, href))
    return sorted(set(urls))


def download_one(url: str, dest: Path) -> tuple[str, int]:
    if dest.exists() and dest.stat().st_size > 0:
        return dest.name, dest.stat().st_size
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = fetch_bytes(url)
    temp = dest.with_suffix(dest.suffix + ".part")
    temp.write_bytes(payload)
    temp.replace(dest)
    return dest.name, len(payload)


def download_dataset() -> dict:
    targets = {
        "CXR_png": BASE_URL + "CXR_png/index.html",
        "ManualMask/leftMask": BASE_URL + "ManualMask/leftMask/index.html",
        "ManualMask/rightMask": BASE_URL + "ManualMask/rightMask/index.html",
    }
    tasks = []
    for relative, index_url in targets.items():
        urls = list_png_urls(index_url)
        if not urls:
            raise RuntimeError(f"No PNG links discovered at {index_url}")
        for url in urls:
            tasks.append((url, DATA_ROOT / relative / url.rsplit("/", 1)[-1]))
    downloaded = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(download_one, url, dest) for url, dest in tasks]
        for future in as_completed(futures):
            downloaded.append(future.result())
    images = sorted((DATA_ROOT / "CXR_png").glob("*.png"))
    if len(images) != EXPECTED_IMAGES:
        raise RuntimeError(
            f"Expected {EXPECTED_IMAGES} Montgomery images from the source listing, found {len(images)}."
        )
    return {
        "source": BASE_URL,
        "images": len(images),
        "left_masks": len(list((DATA_ROOT / "ManualMask/leftMask").glob("*.png"))),
        "right_masks": len(list((DATA_ROOT / "ManualMask/rightMask").glob("*.png"))),
        "downloaded_or_cached_files": len(downloaded),
        "downloaded_bytes_this_run": int(sum(n for _, n in downloaded)),
    }


def read_source(path: Path) -> tuple[np.ndarray, dict]:
    with Image.open(path) as im:
        arr = np.asarray(im)
        mode = im.mode
    if arr.ndim == 3:
        arr = arr[..., :3].astype(np.float32).mean(axis=2)
    arr = np.asarray(arr)
    raw_min = int(np.min(arr))
    raw_max = int(np.max(arr))
    if arr.dtype == np.uint8 and raw_max <= 255:
        denom = 255
        norm_rule = "8-bit unchanged"
    elif raw_max <= 4095:
        denom = 4095
        norm_rule = "12-bit fixed full-scale mapping: round(value*255/4095)"
    else:
        denom = 65535
        norm_rule = "16-bit fixed full-scale mapping: round(value*255/65535)"
    ref = np.rint(np.clip(arr.astype(np.float64), 0, denom) * (255.0 / denom)).astype(np.uint8)
    meta = {
        "source_mode": mode,
        "source_dtype": str(arr.dtype),
        "source_min": raw_min,
        "source_max": raw_max,
        "normalization_denominator": denom,
        "normalization_rule": norm_rule,
        "width": int(ref.shape[1]),
        "height": int(ref.shape[0]),
        "source_file_bytes": path.stat().st_size,
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    return ref, meta


def load_lung_mask(image_name: str, shape: tuple[int, int]) -> np.ndarray | None:
    masks = []
    for side in ("leftMask", "rightMask"):
        path = DATA_ROOT / "ManualMask" / side / image_name
        if path.exists():
            with Image.open(path) as im:
                mask = np.asarray(im.convert("L")) > 0
            if mask.shape != shape:
                mask_img = Image.fromarray(mask.astype(np.uint8) * 255).resize(
                    (shape[1], shape[0]), Image.Resampling.NEAREST
                )
                mask = np.asarray(mask_img) > 0
            masks.append(mask)
    if not masks:
        return None
    union = np.logical_or.reduce(masks)
    return union if int(union.sum()) > 0 else None


def encode_decode(ref: np.ndarray, codec: str, parameter: int) -> tuple[bytes, np.ndarray]:
    buf = io.BytesIO()
    im = Image.fromarray(ref, mode="L")
    if codec == "JPEG":
        im.save(buf, format="JPEG", quality=parameter, optimize=True, progressive=False)
    elif codec == "JPEG2000":
        im.save(
            buf, format="JPEG2000", quality_mode="rates",
            quality_layers=[parameter], irreversible=True
        )
    else:
        raise ValueError(codec)
    payload = buf.getvalue()
    with Image.open(io.BytesIO(payload)) as decoded:
        recon = np.asarray(decoded.convert("L"), dtype=np.uint8)
    return payload, recon


def measure(ref: np.ndarray, recon: np.ndarray, mask: np.ndarray | None) -> dict:
    if np.array_equal(ref, recon):
        psnr = float("inf")
    else:
        psnr = float(peak_signal_noise_ratio(ref, recon, data_range=255))
    ssim, ssim_map = structural_similarity(ref, recon, data_range=255, full=True)
    max_abs_error = int(np.max(np.abs(ref.astype(np.int16) - recon.astype(np.int16))))
    if mask is None:
        roi_mean_ssim = float("nan")
        roi_p5_ssim = float("nan")
    else:
        roi_mean_ssim = float(np.mean(ssim_map[mask]))
        roi_p5_ssim = float(np.percentile(ssim_map[mask], ROI_PERCENTILE))
    return {
        "psnr_db": psnr,
        "ssim": float(ssim),
        "lung_roi_ssim": roi_mean_ssim,
        "lung_roi_ssim_p5": roi_p5_ssim,
        "max_abs_error": max_abs_error,
    }


def make_residual_payload(ref: np.ndarray, base_recon: np.ndarray) -> bytes:
    # Signed residual range is [-255,255]. Offset by 255 and store losslessly
    # as uint16 PNG. This is a real, decodable second-stage payload, not an
    # estimated byte count. Base + residual reconstructs the normalized 8-bit
    # reference exactly after clipping.
    residual = ref.astype(np.int16) - base_recon.astype(np.int16)
    stored = (residual + 255).astype(np.uint16)
    buf = io.BytesIO()
    Image.fromarray(stored, mode="I;16").save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def decode_residual(base_recon: np.ndarray, residual_payload: bytes) -> np.ndarray:
    with Image.open(io.BytesIO(residual_payload)) as im:
        stored = np.asarray(im, dtype=np.int32)
    residual = stored - 255
    return np.clip(base_recon.astype(np.int32) + residual, 0, 255).astype(np.uint8)


def transfer_seconds(nbytes: int, mbps: float) -> float:
    return FIXED_LATENCY_SECONDS + (nbytes * 8.0) / (mbps * 1_000_000.0)


def choose_adaptive(candidates: list[dict], byte_budget: int, mode: str) -> tuple[dict, bool]:
    def quality_passes(candidate: dict) -> bool:
        if mode == "mean_ssim":
            return candidate["ssim"] >= QUALITY_THRESHOLD
        if mode == "worst_region":
            roi_value = candidate["lung_roi_ssim_p5"]
            return (
                not math.isnan(roi_value)
                and roi_value >= QUALITY_THRESHOLD
                and candidate["max_abs_error"] <= MAX_ABS_ERROR_LIMIT
            )
        raise ValueError(f"Unknown selector mode: {mode}")

    feasible = [c for c in candidates if c["size_bytes"] <= byte_budget and quality_passes(c)]
    if feasible:
        return min(feasible, key=lambda c: (c["size_bytes"], -c["ssim"])), True

    deadline_candidates = [c for c in candidates if c["size_bytes"] <= byte_budget]
    if deadline_candidates:
        def fallback_score(c: dict) -> tuple:
            regional = c["lung_roi_ssim_p5"]
            if math.isnan(regional):
                regional = c["ssim"]
            return (min(c["ssim"], regional), c["ssim"], -c["size_bytes"])
        return max(deadline_candidates, key=fallback_score), False

    # No candidate fits the byte budget. Return the smallest and record the miss.
    return min(candidates, key=lambda c: c["size_bytes"]), False


def main() -> None:
    start = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    dataset_info = download_dataset()
    jp2_available = bool(features.check("jpg_2000"))
    candidate_rows = []
    decision_rows = []
    source_rows = []
    paired = []
    image_paths = sorted((DATA_ROOT / "CXR_png").glob("*.png"))

    for index, path in enumerate(image_paths, 1):
        ref, source_meta = read_source(path)
        source_meta["image"] = path.name
        source_rows.append(source_meta)
        mask = load_lung_mask(path.name, ref.shape)
        candidates = []
        for q in JPEG_QUALITIES:
            payload, recon = encode_decode(ref, "JPEG", q)
            row = {
                "image": path.name, "codec": "JPEG", "parameter_name": "quality",
                "parameter": q, "size_bytes": len(payload),
                **measure(ref, recon, mask),
            }
            candidates.append(row)
            candidate_rows.append(row)
        if jp2_available:
            for rate in JP2_RATES:
                payload, recon = encode_decode(ref, "JPEG2000", rate)
                row = {
                    "image": path.name, "codec": "JPEG2000", "parameter_name": "target_rate",
                    "parameter": rate, "size_bytes": len(payload),
                    **measure(ref, recon, mask),
                }
                candidates.append(row)
                candidate_rows.append(row)

        base_payload, base_recon = encode_decode(ref, "JPEG", 35)
        residual_payload = make_residual_payload(ref, base_recon)
        full_recon = decode_residual(base_recon, residual_payload)
        if not np.array_equal(full_recon, ref):
            raise RuntimeError(f"Residual round-trip verification failed for {path.name}")
        base_metrics = measure(ref, base_recon, mask)
        full_metrics = measure(ref, full_recon, mask)
        two_stage = {
            "image": path.name,
            "base_bytes": len(base_payload),
            "residual_bytes": len(residual_payload),
            "full_bytes": len(base_payload) + len(residual_payload),
            "base_ssim": base_metrics["ssim"],
            "base_lung_roi_ssim": base_metrics["lung_roi_ssim"],
            "full_ssim": full_metrics["ssim"],
            "full_lung_roi_ssim": full_metrics["lung_roi_ssim"],
        }
        for mbps in BANDWIDTHS_MBPS:
            budget = max(0, int((DEADLINE_SECONDS - FIXED_LATENCY_SECONDS) * mbps * 1_000_000 / 8))
            mean_choice, mean_quality_met = choose_adaptive(candidates, budget, "mean_ssim")
            region_choice, region_quality_met = choose_adaptive(candidates, budget, "worst_region")
            methods = [
                ("Adaptive_mean_ssim", mean_choice, mean_quality_met),
                ("Adaptive_worst_region", region_choice, region_quality_met),
                ("JPEG_Q50", next(c for c in candidates if c["codec"] == "JPEG" and c["parameter"] == 50), np.nan),
                ("JPEG_Q75", next(c for c in candidates if c["codec"] == "JPEG" and c["parameter"] == 75), np.nan),
                ("JPEG_Q90", next(c for c in candidates if c["codec"] == "JPEG" and c["parameter"] == 90), np.nan),
            ] + (
                [
                    ("JPEG2000_R10", next(c for c in candidates if c["codec"] == "JPEG2000" and c["parameter"] == 10), np.nan),
                    ("JPEG2000_R5", next(c for c in candidates if c["codec"] == "JPEG2000" and c["parameter"] == 5), np.nan),
                    ("JPEG2000_R2", next(c for c in candidates if c["codec"] == "JPEG2000" and c["parameter"] == 2), np.nan),
                ] if jp2_available else []
            )
            for method, candidate, quality_met in methods:
                transfer = transfer_seconds(int(candidate["size_bytes"]), mbps)
                decision_rows.append({
                    "image": path.name, "method": method, "bandwidth_mbps": mbps,
                    "deadline_seconds": DEADLINE_SECONDS, "bytes": int(candidate["size_bytes"]),
                    "transfer_seconds_simulated": transfer,
                    "deadline_met": bool(transfer <= DEADLINE_SECONDS),
                    "quality_constraints_met_by_adaptive_selector": quality_met,
                    "psnr_db": candidate["psnr_db"], "ssim": candidate["ssim"],
                    "lung_roi_ssim": candidate["lung_roi_ssim"],
                    "lung_roi_ssim_p5": candidate["lung_roi_ssim_p5"],
                    "max_abs_error": candidate["max_abs_error"],
                    "codec": candidate["codec"], "parameter": candidate["parameter"],
                })
            two_stage.update({
                f"base_transfer_s_{mbps}mbps": transfer_seconds(len(base_payload), mbps),
                f"full_transfer_s_{mbps}mbps": transfer_seconds(len(base_payload) + len(residual_payload), mbps),
            })
        for mbps in BANDWIDTHS_MBPS:
            decision_rows.extend([
                {
                    "image": path.name, "method": "Two_stage_base_only", "bandwidth_mbps": mbps,
                    "deadline_seconds": DEADLINE_SECONDS, "bytes": len(base_payload),
                    "transfer_seconds_simulated": transfer_seconds(len(base_payload), mbps),
                    "deadline_met": transfer_seconds(len(base_payload), mbps) <= DEADLINE_SECONDS,
                    "quality_constraints_met_by_adaptive_selector": np.nan,
                    "psnr_db": base_metrics["psnr_db"], "ssim": base_metrics["ssim"],
                    "lung_roi_ssim": base_metrics["lung_roi_ssim"],
                    "lung_roi_ssim_p5": base_metrics["lung_roi_ssim_p5"],
                    "max_abs_error": base_metrics["max_abs_error"], "codec": "JPEG", "parameter": 35,
                },
                {
                    "image": path.name, "method": "Two_stage_base_plus_residual", "bandwidth_mbps": mbps,
                    "deadline_seconds": DEADLINE_SECONDS, "bytes": len(base_payload) + len(residual_payload),
                    "transfer_seconds_simulated": transfer_seconds(len(base_payload) + len(residual_payload), mbps),
                    "deadline_met": transfer_seconds(len(base_payload) + len(residual_payload), mbps) <= DEADLINE_SECONDS,
                    "quality_constraints_met_by_adaptive_selector": np.nan,
                    "psnr_db": full_metrics["psnr_db"], "ssim": full_metrics["ssim"],
                    "lung_roi_ssim": full_metrics["lung_roi_ssim"],
                    "lung_roi_ssim_p5": full_metrics["lung_roi_ssim_p5"],
                    "max_abs_error": full_metrics["max_abs_error"],
                    "codec": "JPEG+lossless-residual-PNG", "parameter": 35,
                },
            ])
        print(f"[{index}/{len(image_paths)}] {path.name} complete; JP2={'yes' if jp2_available else 'no'}", flush=True)

    candidates_df = pd.DataFrame(candidate_rows)
    decisions_df = pd.DataFrame(decision_rows)
    sources_df = pd.DataFrame(source_rows)
    candidates_df.to_csv(OUT / "candidate_metrics.csv", index=False)
    decisions_df.to_csv(OUT / "per_image_decisions.csv", index=False)
    sources_df.to_csv(OUT / "source_manifest.csv", index=False)

    summary = (
        decisions_df.groupby(["bandwidth_mbps", "method"], dropna=False)
        .agg(
            n=("image", "nunique"),
            mean_bytes=("bytes", "mean"),
            median_bytes=("bytes", "median"),
            mean_ssim=("ssim", "mean"),
            median_ssim=("ssim", "median"),
            mean_psnr_db=("psnr_db", "mean"),
            mean_lung_roi_ssim=("lung_roi_ssim", "mean"),
            mean_lung_roi_ssim_p5=("lung_roi_ssim_p5", "mean"),
            mean_max_abs_error=("max_abs_error", "mean"),
            deadline_miss_rate=("deadline_met", lambda x: float(1.0 - x.mean())),
        )
        .reset_index()
    )

    # Deterministic bootstrap confidence intervals for means; Wilson interval for miss rate.
    def bootstrap_ci(values, seed_offset=0):
        arr = np.asarray(values, dtype=float)
        arr = arr[np.isfinite(arr)]
        if len(arr) == 0:
            return float("nan"), float("nan")
        if len(arr) == 1:
            return float(arr[0]), float(arr[0])
        rng = np.random.default_rng(BOOTSTRAP_SEED + seed_offset)
        sampled = rng.choice(arr, size=(BOOTSTRAP_RESAMPLES, len(arr)), replace=True).mean(axis=1)
        return float(np.percentile(sampled, 2.5)), float(np.percentile(sampled, 97.5))

    def wilson_interval(successes, n, z=1.959963984540054):
        if n == 0:
            return float("nan"), float("nan")
        p = successes / n
        denom = 1 + z*z/n
        center = (p + z*z/(2*n)) / denom
        half = z * math.sqrt((p*(1-p)/n) + z*z/(4*n*n)) / denom
        return max(0.0, center-half), min(1.0, center+half)

    ci_rows = []
    for row_index, row in summary.iterrows():
        group = decisions_df[
            (decisions_df["bandwidth_mbps"] == row["bandwidth_mbps"])
            & (decisions_df["method"] == row["method"])
        ]
        for metric in ("bytes", "ssim", "psnr_db", "lung_roi_ssim_p5", "max_abs_error"):
            values = group[metric].to_numpy(dtype=float)
            low, high = bootstrap_ci(values, seed_offset=int(row_index) * 11 + len(metric))
            ci_rows.append({
                "bandwidth_mbps": row["bandwidth_mbps"], "method": row["method"],
                "metric": metric, "mean": float(np.nanmean(values)) if np.isfinite(values).any() else float("inf"),
                "ci95_low": low, "ci95_high": high, "n": int(np.isfinite(values).sum()),
                "interval_method": "percentile bootstrap, 2000 resamples; non-finite values excluded",
            })
        n = int(group["deadline_met"].notna().sum())
        misses = int((~group["deadline_met"].astype(bool)).sum())
        lo, hi = wilson_interval(misses, n)
        ci_rows.append({
            "bandwidth_mbps": row["bandwidth_mbps"], "method": row["method"],
            "metric": "deadline_miss_rate", "mean": misses / n if n else float("nan"),
            "ci95_low": lo, "ci95_high": hi, "n": n,
            "interval_method": "Wilson score interval",
        })
    summary.to_csv(OUT / "summary.csv", index=False)
    pd.DataFrame(ci_rows).to_csv(OUT / "summary_confidence_intervals.csv", index=False)

    # Check empirical monotonicity of quality with increasing encoded size.
    mono_rows = []
    for (image, codec), group in candidates_df.groupby(["image", "codec"]):
        ordered = group.sort_values("size_bytes")
        ssim_values = ordered["ssim"].to_numpy(dtype=float)
        roi_values = ordered["lung_roi_ssim_p5"].to_numpy(dtype=float)
        mono_rows.append({
            "image": image, "codec": codec, "candidate_count": len(group),
            "ssim_monotonicity_violations": int(np.sum(np.diff(ssim_values) < -1e-6)),
            "roi_p5_monotonicity_violations": int(np.sum(np.diff(roi_values[np.isfinite(roi_values)]) < -1e-6)),
            "note": "Candidates sorted by measured file size; violations count adjacent quality decreases as size increases.",
        })
    pd.DataFrame(mono_rows).to_csv(OUT / "monotonicity_diagnostics.csv", index=False)

    # Paired, image-level Wilcoxon tests compare each adaptive selector with fixed JPEG-Q75.
    test_rows = []
    for mbps in BANDWIDTHS_MBPS:
        part = decisions_df[decisions_df["bandwidth_mbps"] == mbps]
        baseline = part[part["method"] == "JPEG_Q75"].set_index("image")
        for adaptive_method in ("Adaptive_mean_ssim", "Adaptive_worst_region"):
            adaptive = part[part["method"] == adaptive_method].set_index("image")
            for metric in ("ssim", "bytes", "psnr_db"):
                merged = adaptive[[metric]].join(baseline[[metric]], lsuffix="_adaptive", rsuffix="_jpeg_q75", how="inner").dropna()
                diffs = merged[f"{metric}_adaptive"] - merged[f"{metric}_jpeg_q75"]
                p_value = float("nan")
                try:
                    from scipy.stats import wilcoxon
                    finite = diffs[np.isfinite(diffs)]
                    if len(finite) and not np.allclose(finite.to_numpy(), 0):
                        p_value = float(wilcoxon(finite).pvalue)
                except Exception:
                    pass
                test_rows.append({
                    "bandwidth_mbps": mbps, "adaptive_method": adaptive_method, "metric": metric,
                    "n_pairs": int(len(diffs)),
                    "mean_paired_difference_adaptive_minus_jpeg_q75": float(diffs.mean()) if len(diffs) else float("nan"),
                    "median_paired_difference": float(diffs.median()) if len(diffs) else float("nan"),
                    "wilcoxon_p_value_unadjusted": p_value,
                    "note": "Exploratory paired comparison; p-values unadjusted across metrics/profiles.",
                })
    pd.DataFrame(test_rows).to_csv(OUT / "paired_tests.csv", index=False)

    manifest = {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "pillow": PIL.__version__,
        "jpeg2000_supported_by_pillow": jp2_available,
        "dataset": dataset_info,
        "images_processed": len(image_paths),
        "images_with_lung_masks": int(sources_df["image"].map(
            lambda name: load_lung_mask(name, (int(sources_df.loc[sources_df["image"] == name, "height"].iloc[0]),
                                               int(sources_df.loc[sources_df["image"] == name, "width"].iloc[0]))) is not None
        ).sum()),
        "normalization": "8-bit normalized copy; original source min/max/mode and fixed denominator are recorded per image.",
        "candidate_parameters": {"jpeg_quality": JPEG_QUALITIES, "jpeg2000_target_rates": JP2_RATES if jp2_available else []},
        "adaptive_quality_threshold": QUALITY_THRESHOLD,
        "worst_region_percentile": ROI_PERCENTILE,
        "maximum_absolute_error_limit": MAX_ABS_ERROR_LIMIT,
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bandwidth_profiles_mbps": BANDWIDTHS_MBPS,
        "deadline_seconds": DEADLINE_SECONDS,
        "fixed_latency_seconds": FIXED_LATENCY_SECONDS,
        "network_note": "Transfer times are mathematical simulations, not live network measurements.",
        "two_stage_note": "Base JPEG and lossless uint16 PNG residual are separate measured payloads; residual round-trip exactness is asserted.",
        "adaptive_methods": {
            "Adaptive_mean_ssim": "Smallest candidate meeting global SSIM >= 0.95 within the deadline byte budget.",
            "Adaptive_worst_region": "Smallest candidate meeting 5th-percentile SSIM-map value within the lung-mask union >= 0.95 and max absolute error <= 24 within the deadline byte budget.",
            "fallback": "If no quality-feasible candidate fits, choose the best-scoring candidate that fits; if none fits, choose the smallest and record a deadline miss.",
        },
        "clinical_safety_note": "PSNR/SSIM and lung-mask ROI metrics do not establish diagnostic safety.",
        "elapsed_seconds": round(time.time() - start, 2),
    }
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False))
    print(json.dumps({"status": "success", "manifest": str(OUT / "run_manifest.json"),
                      "summary": str(OUT / "summary.csv"), "elapsed_seconds": manifest["elapsed_seconds"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
