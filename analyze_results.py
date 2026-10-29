#!/usr/bin/env python3
"""Validate completed Montgomery benchmark outputs and produce publication statistics.

This post-processing script does not encode images or invent measurements. It reads
only the completed benchmark CSV/JSON/log files, validates the output contract, and
computes paired inference from per-image rows.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy.stats import binomtest, wilcoxon

EXPECTED_IMAGES = 138
EXPECTED_QUALITY_ROWS = 138 * 4
EXPECTED_CANDIDATE_ROWS = 138 * 11
EXPECTED_DELIVERY_ROWS = 138 * 3 * 5
EXPECTED_SUMMARY_ROWS = 3 * 5
EXPECTED_PAIRED_ROWS = 10
EXPECTED_MONOTONICITY_ROWS = 138
BOOTSTRAP_RESAMPLES = 2000
SEED = 42

REQUIRED_FILES = [
    "quality_by_image.csv",
    "delivery_by_image_profile.csv",
    "candidate_diagnostics.csv",
    "dataset_manifest.csv",
    "summary.csv",
    "paired_comparisons.csv",
    "monotonicity_diagnostics.csv",
    "run_metadata.json",
    "run.log",
]

def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, returned in input order."""
    if not p_values:
        return []
    p = np.asarray(p_values, dtype=float)
    if np.any(~np.isfinite(p)) or np.any((p < 0) | (p > 1)):
        raise ValueError("p-values must be finite values in [0, 1]")
    order = np.argsort(p)
    adjusted = np.empty(len(p), dtype=float)
    running = 0.0
    m = len(p)
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * float(p[idx]))
        adjusted[idx] = min(1.0, running)
    return adjusted.tolist()

def paired_bootstrap_mean_ci(differences, *, seed=SEED, n_resamples=BOOTSTRAP_RESAMPLES):
    """Percentile 95% CI for the mean of paired per-unit differences."""
    d = np.asarray(differences, dtype=float)
    d = d[np.isfinite(d)]
    if len(d) == 0:
        raise ValueError("No finite paired differences available")
    if len(d) == 1:
        value = float(d[0])
        return value, value
    rng = np.random.default_rng(seed)
    # 2,000 x 138 is small; resample paired differences, not individual methods.
    sample_idx = rng.integers(0, len(d), size=(n_resamples, len(d)))
    means = d[sample_idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))

def paired_numeric_test(differences):
    """Two-sided Wilcoxon signed-rank p-value for nonzero paired differences."""
    d = np.asarray(differences, dtype=float)
    d = d[np.isfinite(d)]
    if len(d) == 0:
        raise ValueError("No finite paired differences available")
    if not np.any(d != 0):
        return 1.0
    return float(wilcoxon(d, zero_method="wilcox", alternative="two-sided").pvalue)

def paired_binary_mcnemar_p(p1_values, p2_values):
    """Exact two-sided McNemar/binomial test for paired binary outcomes.

    p2_better counts pairs where P2=1 and P1=0; p1_better counts the reverse.
    The interpretation of 'better' depends on the metric (the sign is reported
    separately as the P2-minus-P1 risk/rate difference).
    """
    a = np.asarray(p1_values, dtype=int)
    b = np.asarray(p2_values, dtype=int)
    if len(a) != len(b) or len(a) == 0:
        raise ValueError("Paired binary arrays must have equal nonzero length")
    if not np.isin(a, [0, 1]).all() or not np.isin(b, [0, 1]).all():
        raise ValueError("Paired binary values must be 0 or 1")
    p2_better = int(np.sum((a == 0) & (b == 1)))
    p1_better = int(np.sum((a == 1) & (b == 0)))
    discordant = p2_better + p1_better
    if discordant == 0:
        return 1.0, p2_better, p1_better
    p_value = float(binomtest(min(p2_better, p1_better), n=discordant, p=0.5,
                              alternative="two-sided").pvalue)
    return p_value, p2_better, p1_better

def _bool_series(series: pd.Series) -> pd.Series:
    values = series.astype(str).str.strip().str.lower()
    if not values.isin(["true", "false", "1", "0"]).all():
        raise ValueError(f"Unexpected boolean values: {sorted(values.unique())}")
    return values.isin(["true", "1"])

def _close(a, b, tol=1e-6):
    if pd.isna(a) and pd.isna(b):
        return True
    if pd.isna(a) or pd.isna(b):
        return False
    return bool(np.isclose(float(a), float(b), rtol=tol, atol=tol))

def validate_results(results_dir: Path, lossless_dir: Path | None = None):
    """Return loaded dataframes, passed checks, and failures."""
    passed, failed = [], []
    def check(condition, label):
        (passed if condition else failed).append(label)

    missing = [name for name in REQUIRED_FILES if not (results_dir / name).is_file()]
    if missing:
        return {}, passed, [f"Missing required files: {', '.join(missing)}"]

    try:
        qdf = pd.read_csv(results_dir / "quality_by_image.csv")
        ddf = pd.read_csv(results_dir / "delivery_by_image_profile.csv")
        cdf = pd.read_csv(results_dir / "candidate_diagnostics.csv")
        mdf = pd.read_csv(results_dir / "dataset_manifest.csv")
        sdf = pd.read_csv(results_dir / "summary.csv")
        pdf = pd.read_csv(results_dir / "paired_comparisons.csv")
        mono = pd.read_csv(results_dir / "monotonicity_diagnostics.csv")
        meta = json.loads((results_dir / "run_metadata.json").read_text())
        log = (results_dir / "run.log").read_text(errors="replace")
    except Exception as exc:
        return {}, passed, [f"Could not parse one or more required outputs: {type(exc).__name__}: {exc}"]

    data = {"quality": qdf, "delivery": ddf, "candidates": cdf, "manifest": mdf,
            "summary": sdf, "paired": pdf, "monotonicity": mono, "metadata": meta, "log": log}

    # The standalone lossless baseline is produced on its own branch but uses the
    # same sorted image order, seed, profile order, and throughput draws.
    if lossless_dir is not None:
        lossless_required = [
            "lossless_quality_by_image.csv", "lossless_delivery_by_image_profile.csv",
            "lossless_manifest.csv", "lossless_delivery_summary.csv", "run_metadata.json", "run.log"
        ]
        missing_lossless = [name for name in lossless_required if not (lossless_dir / name).is_file()]
        if missing_lossless:
            failed.append(f"Missing required lossless-baseline files: {', '.join(missing_lossless)}")
        else:
            try:
                lq = pd.read_csv(lossless_dir / "lossless_quality_by_image.csv")
                ld = pd.read_csv(lossless_dir / "lossless_delivery_by_image_profile.csv")
                lm = pd.read_csv(lossless_dir / "lossless_manifest.csv")
                ls = pd.read_csv(lossless_dir / "lossless_delivery_summary.csv")
                lmeta = json.loads((lossless_dir / "run_metadata.json").read_text())
                llog = (lossless_dir / "run.log").read_text(errors="replace")
                data.update({"lossless_quality": lq, "lossless_delivery": ld,
                             "lossless_manifest": lm, "lossless_summary": ls,
                             "lossless_metadata": lmeta, "lossless_log": llog})
                check(len(lq) == EXPECTED_IMAGES, f"Lossless quality row count is {len(lq)} (expected {EXPECTED_IMAGES})")
                check(len(ld) == EXPECTED_IMAGES * 3, f"Lossless delivery row count is {len(ld)} (expected {EXPECTED_IMAGES * 3})")
                check(len(lm) == EXPECTED_IMAGES, f"Lossless manifest row count is {len(lm)} (expected {EXPECTED_IMAGES})")
                check(not lq["image"].duplicated().any(), "No duplicate lossless quality image keys")
                check(not ld.duplicated(["image", "profile"]).any(), "No duplicate lossless image/profile keys")
                check(set(lm["image"]) == set(mdf["image"]), "Lossless and primary runs contain the same 138 image names")
                check(bool(_bool_series(lq["round_trip_exact"]).all()), "Lossless JPEG 2000 round trips are exact for all images")
                check(lmeta.get("exact_reconstruction_verified") is True, "Lossless metadata confirms exact reconstruction")
                check("all round trips exact" in llog.lower(), "Lossless log records exact reconstruction completion")
                check(len(ls) == 3 and set(ls["profile"]) == {"poor", "moderate", "good"},
                      "Lossless summary contains all three network profiles")
                # Confirm the two runs used the same seeded throughput draws before making paired comparisons.
                primary_bw = ddf.groupby(["image", "profile"])["actual_bandwidth_bps"].first().sort_index()
                lossless_bw = ld.set_index(["image", "profile"])["actual_bandwidth_bps"].sort_index()
                same_draws = primary_bw.index.equals(lossless_bw.index) and np.allclose(
                    primary_bw.to_numpy(dtype=float), lossless_bw.to_numpy(dtype=float), rtol=1e-12, atol=1e-9
                )
                check(bool(same_draws), "Lossless and primary runs use identical per-image/profile throughput draws")
            except Exception as exc:
                failed.append(f"Could not parse or validate lossless-baseline outputs: {type(exc).__name__}: {exc}")

    check(len(mdf) == EXPECTED_IMAGES, f"Manifest row count is {len(mdf)} (expected {EXPECTED_IMAGES})")
    check(mdf["image"].nunique() == EXPECTED_IMAGES, "Manifest contains 138 unique images")
    check(len(qdf) == EXPECTED_QUALITY_ROWS, f"Quality row count is {len(qdf)} (expected {EXPECTED_QUALITY_ROWS})")
    check(len(cdf) == EXPECTED_CANDIDATE_ROWS, f"Candidate row count is {len(cdf)} (expected {EXPECTED_CANDIDATE_ROWS})")
    check(len(ddf) == EXPECTED_DELIVERY_ROWS, f"Delivery row count is {len(ddf)} (expected {EXPECTED_DELIVERY_ROWS})")
    check(len(sdf) == EXPECTED_SUMMARY_ROWS, f"Summary row count is {len(sdf)} (expected {EXPECTED_SUMMARY_ROWS})")
    check(len(pdf) == EXPECTED_PAIRED_ROWS, f"Existing paired-comparison row count is {len(pdf)} (expected {EXPECTED_PAIRED_ROWS})")
    check(len(mono) == EXPECTED_MONOTONICITY_ROWS, f"Monotonicity row count is {len(mono)} (expected {EXPECTED_MONOTONICITY_ROWS})")

    check(not mdf["image"].duplicated().any(), "No duplicate manifest image keys")
    check(not qdf.duplicated(["image", "method"]).any(), "No duplicate image/method quality keys")
    check(not ddf.duplicated(["image", "profile", "method"]).any(), "No duplicate image/profile/method delivery keys")
    check(not cdf.duplicated(["image", "ratio"]).any(), "No duplicate image/candidate-ratio keys")
    check(not mono["image"].duplicated().any(), "No duplicate monotonicity image keys")

    check(set(qdf["method"].unique()) == {
        "B1_fixed_jpeg", "B2_fixed_j2k", "B3_mean_ssim_single", "P1_lung_region_bound_single"
    }, "Quality output has exactly the four documented single-stage methods")
    check(set(ddf["method"].unique()) == {
        "B1_fixed_jpeg", "B2_fixed_j2k", "B3_mean_ssim_single",
        "P1_lung_region_bound_single", "P2_deadline_aware_base_residual"
    }, "Delivery output has exactly the five documented methods")
    check(set(ddf["profile"].unique()) == {"poor", "moderate", "good"},
          "Delivery output has exactly the three documented profiles")
    check(bool((mdf["lung_mask_files_found"] == 2).all()),
          "Both left/right lung-mask files were found for every image")
    check(bool((mdf["lung_mask_pixel_fraction"] > 0).all() and
               (mdf["lung_mask_pixel_fraction"] <= 1).all()),
          "All lung-mask coverage fractions are in (0, 1]")

    check(bool((qdf["payload_bytes"] > 0).all() and (cdf["payload_bytes"] > 0).all()),
          "All measured payload sizes are positive")
    for col in ["ssim_mean", "lung_region_ssim_p05", "lung_region_ssim_min"]:
        check(bool(qdf[col].dropna().between(0, 1).all()), f"Quality metric {col} lies in [0, 1]")
    check(bool(qdf["max_abs_error"].dropna().between(0, 255).all()),
          "Maximum absolute error lies in [0, 255]")
    check(bool(ddf["deadline_miss"].dropna().isin([0, 1]).all() and
               ddf["full_delivery_miss"].dropna().isin([0, 1]).all() and
               ddf["quality_bound_met_by_deadline"].dropna().isin([0, 1]).all()),
          "Deadline and quality-bound indicators are binary")

    p1 = qdf[qdf["method"] == "P1_lung_region_bound_single"].copy()
    fallback = _bool_series(p1["p1_used_lossless_fallback"])
    feasible = p1.loc[~fallback]
    check(bool((feasible["lung_region_ssim_p05"] >= 0.95).all() and
               (feasible["max_abs_error"] <= 24).all()),
          "Every non-fallback P1 selection meets both specified quality/error bounds")
    check(bool((p1.loc[fallback, "selected_jpeg2000_ratio"] == 1).all()),
          "Every P1 fallback is marked as lossless JPEG 2000 ratio 1")
    check(int(fallback.sum()) >= 0, f"P1 lossless fallback count is {int(fallback.sum())}")

    check(int(meta.get("n_images", -1)) == EXPECTED_IMAGES, "Run metadata reports 138 images")
    check(meta.get("synthetic") is False, "Run metadata confirms no synthetic benchmark images")
    check("Completed: 138 real images" in log, "Run log records successful completion of all 138 real images")
    check("Traceback (most recent call last)" not in log, "Run log contains no Python traceback")

    # Independently recompute summary aggregates from per-image delivery rows.
    agg = ddf.groupby(["method", "profile"], as_index=False).agg(
        n_images=("image", "nunique"),
        n_images_quality_available=("psnr_db", "count"),
        mean_full_payload_kb=("full_payload_kb", "mean"),
        mean_psnr_db=("psnr_db", "mean"),
        mean_ssim=("ssim_mean", "mean"),
        mean_lung_region_ssim_p05=("lung_region_ssim_p05", "mean"),
        deadline_miss_rate=("deadline_miss", "mean"),
        full_delivery_miss_rate=("full_delivery_miss", "mean"),
        quality_bound_met_by_deadline_rate=("quality_bound_met_by_deadline", "mean"),
        mean_first_stage_seconds=("first_stage_seconds", "mean"),
        mean_full_delivery_seconds=("full_delivery_seconds", "mean"),
    )
    summary_keys = ["method", "profile"]
    check(not sdf.duplicated(summary_keys).any(), "Summary has unique method/profile keys")
    merged = agg.merge(sdf, on=summary_keys, suffixes=("_recomputed", "_stored"), how="outer", indicator=True)
    check(bool((merged["_merge"] == "both").all()), "Stored summary has exactly the method/profile groups present in delivery rows")
    numeric_cols = [c for c in agg.columns if c not in summary_keys]
    summary_matches = True
    for _, row in merged.iterrows():
        if row["_merge"] != "both":
            summary_matches = False
            continue
        for col in numeric_cols:
            if not _close(row[f"{col}_recomputed"], row[f"{col}_stored"]):
                summary_matches = False
    check(summary_matches, "Stored summary aggregates match independent recomputation from delivery rows")
    return data, passed, failed

def build_publication_statistics(data):
    qdf, ddf = data["quality"], data["delivery"]
    rows = []

    # Continuous paired comparisons: P1 minus B3, paired by radiograph filename.
    b3 = qdf[qdf.method == "B3_mean_ssim_single"].set_index("image")
    p1 = qdf[qdf.method == "P1_lung_region_bound_single"].set_index("image")
    for metric in ["payload_bytes", "psnr_db", "ssim_mean", "lung_region_ssim_p05"]:
        pair = pd.concat([b3[metric].rename("b3"), p1[metric].rename("p1")], axis=1).dropna()
        diff = (pair["p1"] - pair["b3"]).to_numpy(dtype=float)
        lo, hi = paired_bootstrap_mean_ci(diff, seed=SEED)
        rows.append({
            "comparison": "P1_minus_B3", "profile": "all", "metric": metric,
            "n_pairs": int(len(diff)), "mean_difference": float(diff.mean()),
            "median_difference": float(np.median(diff)), "bootstrap_ci95_low": lo,
            "bootstrap_ci95_high": hi, "test": "Wilcoxon signed-rank",
            "p_value_raw": paired_numeric_test(diff), "discordant_p2_ones_p1_zeros": np.nan,
            "discordant_p1_ones_p2_zeros": np.nan, "direction": "P1 minus B3",
        })

    # Paired binary outcomes: P2 minus P1, by profile. Exact McNemar is appropriate
    # for paired binary outcomes; bootstrap intervals describe the paired rate difference.
    for profile in ["poor", "moderate", "good"]:
        group = ddf[ddf.profile == profile]
        p1g = group[group.method == "P1_lung_region_bound_single"].set_index("image")
        p2g = group[group.method == "P2_deadline_aware_base_residual"].set_index("image")
        for metric in ["full_delivery_miss", "quality_bound_met_by_deadline"]:
            pair = pd.concat([p1g[metric].rename("p1"), p2g[metric].rename("p2")], axis=1).dropna()
            a = pair["p1"].to_numpy(dtype=int)
            b = pair["p2"].to_numpy(dtype=int)
            diff = b.astype(float) - a.astype(float)
            lo, hi = paired_bootstrap_mean_ci(diff, seed=SEED)
            p_value, p2_ones_p1_zeros, p1_ones_p2_zeros = paired_binary_mcnemar_p(a, b)
            rows.append({
                "comparison": f"P2_minus_P1_{profile}", "profile": profile, "metric": metric,
                "n_pairs": int(len(diff)), "mean_difference_p2_minus_p1_or_p1_minus_b3": float(diff.mean()),
                "median_difference": float(np.median(diff)), "bootstrap_ci95_low": lo,
                "bootstrap_ci95_high": hi, "test": "Exact McNemar",
                "p_value_raw": p_value, "discordant_p2_ones_p1_zeros": p2_ones_p1_zeros,
                "discordant_p1_ones_p2_zeros": p1_ones_p2_zeros, "direction": "P2 minus P1",
            })

    # Add the full-set lossless baseline (B0) only when its raw per-image
    # outputs are available and have passed the validation gates.
    if "lossless_delivery" in data:
        b0g = data["lossless_delivery"]
        for profile in ["poor", "moderate", "good"]:
            p1g = ddf[(ddf.profile == profile) & (ddf.method == "P1_lung_region_bound_single")].set_index("image")
            b0p = b0g[b0g.profile == profile].set_index("image")
            for metric in ["full_delivery_miss", "quality_bound_met_by_deadline"]:
                pair = pd.concat([p1g[metric].rename("p1"), b0p[metric].rename("b0")], axis=1).dropna()
                p1_values = pair["p1"].to_numpy(dtype=int)
                b0_values = pair["b0"].to_numpy(dtype=int)
                diff = b0_values.astype(float) - p1_values.astype(float)
                lo, hi = paired_bootstrap_mean_ci(diff, seed=SEED)
                p_value, b0_ones_p1_zeros, p1_ones_b0_zeros = paired_binary_mcnemar_p(p1_values, b0_values)
                rows.append({
                    "comparison": f"B0_minus_P1_{profile}", "profile": profile, "metric": metric,
                    "n_pairs": int(len(diff)), "mean_difference": float(diff.mean()),
                    "median_difference": float(np.median(diff)), "bootstrap_ci95_low": lo,
                    "bootstrap_ci95_high": hi, "test": "Exact McNemar",
                    "p_value_raw": p_value, "discordant_b0_ones_p1_zeros": b0_ones_p1_zeros,
                    "discordant_p1_ones_b0_zeros": p1_ones_b0_zeros,
                    "direction": "B0 minus P1",
                })

    adjusted = holm_adjust([float(row["p_value_raw"]) for row in rows])
    for row, p_adj in zip(rows, adjusted):
        row["p_value_holm_adjusted"] = p_adj
        row["bootstrap_resamples"] = BOOTSTRAP_RESAMPLES
        row["bootstrap_seed"] = SEED
    return pd.DataFrame(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True,
                        help="Directory containing the completed primary benchmark outputs")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Directory to write the QC report and adjusted paired statistics")
    parser.add_argument("--lossless-results-dir", type=Path, default=None,
                        help="Optional directory containing the completed standalone B0 lossless baseline outputs")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    data, passed, failed = validate_results(args.results_dir, args.lossless_results_dir)
    timestamp = datetime.now(timezone.utc).isoformat()
    report = [
        "# Primary Benchmark Quality-Control Report", "",
        f"Analysis timestamp (UTC): {timestamp}", "",
        "This report validates the existing benchmark outputs; it does not encode images or create experimental measurements.", "",
        f"Checks passed: {len(passed)}", f"Checks failed: {len(failed)}", "",
        "## Passed checks",
    ]
    report.extend([f"- PASS — {item}" for item in passed] or ["- None"])
    report.extend(["", "## Failed checks"])
    report.extend([f"- FAIL — {item}" for item in failed] or ["- None"])
    if not failed:
        try:
            stats = build_publication_statistics(data)
            stats.to_csv(args.output_dir / "paired_comparisons_adjusted.csv", index=False)
            report.extend([
                "", "## Statistical analysis",
                "- P1 versus B3: paired per-image differences for payload bytes, PSNR, global SSIM, and regional SSIM; two-sided Wilcoxon signed-rank tests.",
                "- P2 versus P1: paired per-image binary outcomes by network profile; exact two-sided McNemar tests and discordant-pair counts.",
                f"- Paired bootstrap percentile 95% confidence intervals use {BOOTSTRAP_RESAMPLES} resamples of image-level paired differences, seed {SEED}.",
                "- Holm adjustment is applied across all comparisons in the generated table (10 primary comparisons, plus 6 B0-versus-P1 comparisons when the validated lossless baseline is supplied).",
                "- Interpret the P2 quality metric as the reconstruction available by the deadline: if the base arrives but the residual does not, this is base-stage quality, not exact full reconstruction.",
                "- These comparisons do not establish clinical diagnostic safety; the network is simulated."
            ])
        except Exception as exc:
            failed.append(f"Statistical analysis failed: {type(exc).__name__}: {exc}")
            report.extend(["", "## Statistical analysis error", f"- {type(exc).__name__}: {exc}"])
    report_path = args.output_dir / "quality_control_report.md"
    report_path.write_text("\n".join(report) + "\n")
    print("\n".join(report))
    if failed:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
