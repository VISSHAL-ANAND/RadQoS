#!/usr/bin/env python3
"""Full-set standalone lossless JPEG 2000 reference baseline.

Uses the same sorted 138 public Montgomery PNGs, seed, profile order, lognormal
throughput draws, latency, and deadline parameters as benchmark_montgomery.py.
This script is a supplemental comparator and does not modify the primary benchmark.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import PIL
import huggingface_hub
from PIL import Image, features
from huggingface_hub import HfApi, hf_hub_download

SEED = 42
LATENCY = 0.5
PROFILES = {
    "poor": (128_000.0, 0.5, 20.0),
    "moderate": (512_000.0, 0.4, 20.0),
    "good": (2_000_000.0, 0.3, 20.0),
}
HF_REPO = "Famatsu123/montgomery-shenzhen-tuberculosis-cxr"


def download_data() -> list[dict]:
    api = HfApi()
    paths = sorted(
        p for p in api.list_repo_files(repo_id=HF_REPO, repo_type="dataset")
        if p.startswith("MontgomerySet/CXR_png/") and p.lower().endswith(".png")
    )
    if len(paths) != 138:
        raise RuntimeError(f"Expected 138 Montgomery images, found {len(paths)}")

    local_paths: dict[str, Path] = {}

    def download_one(remote: str) -> tuple[str, Path]:
        path = hf_hub_download(repo_id=HF_REPO, filename=remote, repo_type="dataset")
        return remote, Path(path)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(download_one, p) for p in paths]
        for i, fut in enumerate(as_completed(futures), 1):
            remote, local = fut.result()
            local_paths[remote] = local
            if i % 20 == 0 or i == len(futures):
                print(f"Downloaded {i}/{len(futures)} radiographs", flush=True)

    records = []
    for remote in paths:
        local = local_paths[remote]
        h = hashlib.sha256()
        with local.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(chunk)
        records.append({
            "filename": remote.rsplit("/", 1)[-1],
            "path": str(local),
            "source_file_bytes": local.stat().st_size,
            "source_sha256": h.hexdigest(),
        })
    return records


def encode_lossless_j2k(arr: np.ndarray) -> tuple[bytes, np.ndarray, float]:
    buf = io.BytesIO()
    start = time.perf_counter()
    Image.fromarray(arr).save(buf, format="JPEG2000", irreversible=False)
    payload = buf.getvalue()
    elapsed = time.perf_counter() - start
    decoded = np.asarray(Image.open(io.BytesIO(payload)).convert("L"), dtype=np.uint8)
    return payload, decoded, elapsed


def main() -> None:
    if not features.check("jpg_2000"):
        raise RuntimeError("Pillow build does not support JPEG 2000")
    records = download_data()
    rng = np.random.default_rng(SEED)
    quality_rows: list[dict] = []
    delivery_rows: list[dict] = []
    manifest_rows: list[dict] = []
    for ix, record in enumerate(records, 1):
        with Image.open(record["path"]) as im:
            mode = im.mode
            arr = np.asarray(im)
        if mode != "L" or arr.ndim != 2 or arr.dtype != np.uint8:
            raise RuntimeError(
                f"Unexpected input representation for {record['filename']}: "
                f"mode={mode}, shape={arr.shape}, dtype={arr.dtype}"
            )

        payload, reconstruction, encode_seconds = encode_lossless_j2k(arr)
        if not np.array_equal(arr, reconstruction):
            raise RuntimeError(f"Lossless JPEG 2000 round trip failed for {record['filename']}")
        err = np.abs(arr.astype(np.int16) - reconstruction.astype(np.int16))
        if int(err.max()) != 0:
            raise RuntimeError(f"Nonzero reconstruction error for {record['filename']}")

        size = len(payload)
        raw_size = int(arr.size)
        quality_rows.append({
            "image": record["filename"],
            "method": "B0_standalone_lossless_j2k",
            "payload_bytes": size,
            "payload_kib": size / 1024.0,
            "raw_8bit_bytes": raw_size,
            "compression_ratio_vs_raw_8bit": raw_size / size,
            "psnr_db": 99.0,  # Same capped convention as the primary benchmark for exact reconstruction.
            "ssim_mean": 1.0,
            "lung_region_ssim_p05": 1.0,
            "lung_region_ssim_min": 1.0,
            "max_abs_error": 0,
            "encode_seconds": encode_seconds,
            "round_trip_exact": True,
        })

        # RNG draw order intentionally matches the primary full-set benchmark:
        # sorted filename order, then poor/moderate/good profile order per image.
        for profile, (mean_bps, dispersion, deadline) in PROFILES.items():
            actual_bps = mean_bps * rng.lognormal(0, dispersion) / math.exp(dispersion ** 2 / 2)
            transfer_seconds = size * 8.0 / actual_bps + LATENCY
            miss = int(transfer_seconds > deadline)
            delivery_rows.append({
                "image": record["filename"],
                "profile": profile,
                "method": "B0_standalone_lossless_j2k",
                "full_payload_kb": size / 1024.0,
                "bytes_delivered_by_deadline": 0 if miss else size,
                "first_stage_seconds": transfer_seconds,
                "full_delivery_seconds": transfer_seconds,
                "deadline_seconds": deadline,
                "deadline_miss": miss,
                "full_delivery_miss": miss,
                "quality_bound_met_by_deadline": int(not miss),
                "actual_bandwidth_bps": actual_bps,
                "estimated_lower_bandwidth_bps": float("nan"),
                "psnr_db": float("nan") if miss else 99.0,
                "ssim_mean": float("nan") if miss else 1.0,
                "lung_region_ssim_p05": float("nan") if miss else 1.0,
                "lung_region_ssim_min": float("nan") if miss else 1.0,
                "max_abs_error": float("nan") if miss else 0,
                "p2_base_ratio": float("nan"),
                "p2_residual_bytes": float("nan"),
            })
        manifest_rows.append({
            "image": record["filename"],
            "source_mode": mode,
            "source_dtype": str(arr.dtype),
            "source_min": int(arr.min()),
            "source_max": int(arr.max()),
            "width": int(arr.shape[1]),
            "height": int(arr.shape[0]),
            "source_file_bytes": record["source_file_bytes"],
            "source_sha256": record["source_sha256"],
            "lossless_payload_bytes": size,
            "lossless_encode_seconds": encode_seconds,
            "round_trip_exact": True,
        })
        print(
            f"[{ix}/{len(records)}] {record['filename']}: "
            f"lossless payload={size/1024:.1f} KiB, exact=True",
            flush=True,
        )

    output = Path("lossless-results")
    output.mkdir(exist_ok=True)
    qdf = pd.DataFrame(quality_rows)
    ddf = pd.DataFrame(delivery_rows)
    mdf = pd.DataFrame(manifest_rows)
    qdf.to_csv(output / "lossless_quality_by_image.csv", index=False)
    ddf.to_csv(output / "lossless_delivery_by_image_profile.csv", index=False)
    mdf.to_csv(output / "lossless_manifest.csv", index=False)
    summary = ddf.groupby("profile", as_index=False).agg(
        n_images=("image", "nunique"),
        mean_payload_kib=("full_payload_kb", "mean"),
        median_payload_kib=("full_payload_kb", "median"),
        first_stage_miss_rate=("deadline_miss", "mean"),
        full_delivery_miss_rate=("full_delivery_miss", "mean"),
        quality_bound_met_by_deadline_rate=("quality_bound_met_by_deadline", "mean"),
        mean_transfer_seconds=("full_delivery_seconds", "mean"),
    )
    summary.to_csv(output / "lossless_delivery_summary.csv", index=False)
    quality_summary = qdf.agg(
        n_images=("image", "nunique"),
        mean_payload_bytes=("payload_bytes", "mean"),
        median_payload_bytes=("payload_bytes", "median"),
        mean_compression_ratio_vs_raw_8bit=("compression_ratio_vs_raw_8bit", "mean"),
        median_encode_seconds=("encode_seconds", "median"),
        all_round_trips_exact=("round_trip_exact", "all"),
    )
    metadata = {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "software_versions": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "Pillow": PIL.__version__,
            "huggingface_hub": huggingface_hub.__version__,
        },
        "dataset_repo": HF_REPO,
        "n_images": len(records),
        "seed": SEED,
        "latency_seconds": LATENCY,
        "deadline_seconds": 20.0,
        "profiles": PROFILES,
        "lossless_codec": "JPEG 2000 reversible mode (Pillow irreversible=False)",
        "exact_reconstruction_verified": True,
        "network_simulation_matches_primary_rng_draw_order": True,
        "notes": [
            "This is a supplemental standalone lossless baseline and does not modify the primary benchmark outputs.",
            "All sizes are measured from actual encoded JPEG 2000 payloads.",
            "The public source PNGs are 8-bit grayscale; the experiment does not claim native 12-bit preservation.",
            "PSNR is capped at 99 dB for exact reconstruction, matching the primary benchmark convention.",
            "Network outcomes are simulated, not measured from live networks.",
        ],
    }
    (output / "run_metadata.json").write_text(json.dumps(metadata, indent=2, default=str))
    print("\nLOSSLESS DELIVERY SUMMARY\n" + summary.to_string(index=False), flush=True)
    print("QUALITY SUMMARY\n" + json.dumps({k: (v.item() if hasattr(v, "item") else v) for k, v in quality_summary.items()}, indent=2, default=str), flush=True)
    print(f"Completed: {len(records)} real images, standalone lossless JPEG 2000 baseline; all round trips exact.", flush=True)


if __name__ == "__main__":
    main()
