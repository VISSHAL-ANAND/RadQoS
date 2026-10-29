#!/usr/bin/env python3
"""Cloud benchmark on Montgomery CXR images. Synthetic data are never used here."""
import io, json, math, struct, zlib, hashlib, platform, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import PIL, scipy, skimage, huggingface_hub
from scipy.stats import wilcoxon
from PIL import Image, features
from huggingface_hub import HfApi, hf_hub_download
import os
from skimage.metrics import structural_similarity, peak_signal_noise_ratio

RATIOS = [4, 6, 8, 10, 15, 20, 30, 40, 60, 80, 120]
Q_MIN, PERCENTILE, MAX_ERROR, GRID = 0.95, 5, 24, 8
JPEG_Q, FIXED_J2K, LATENCY = 75, 20, 0.5
PROFILES = {
    "poor": (128_000.0, 0.5, 20.0),
    "moderate": (512_000.0, 0.4, 20.0),
    "good": (2_000_000.0, 0.3, 20.0),
}
SEED = 42

def encode(arr, fmt, value=None):
    b = io.BytesIO()
    im = Image.fromarray(arr.astype(np.uint8))
    if fmt == "JPEG":
        im.save(b, format="JPEG", quality=value)
    elif fmt == "JPEG2000":
        im.save(b, format="JPEG2000", quality_mode="rates", quality_layers=[value], irreversible=True)
    else:
        raise ValueError(fmt)
    data = b.getvalue()
    rec = np.asarray(Image.open(io.BytesIO(data)).convert("L"), dtype=np.uint8)
    return data, rec

def lossless_j2k(arr):
    b = io.BytesIO()
    Image.fromarray(arr).save(b, format="JPEG2000", irreversible=False)
    return b.getvalue()

def metrics(orig, rec, mask):
    _, smap = structural_similarity(orig, rec, data_range=255, full=True)
    h, w = orig.shape
    vals = []
    for gy in range(GRID):
        y0, y1 = round(gy*h/GRID), round((gy+1)*h/GRID)
        for gx in range(GRID):
            x0, x1 = round(gx*w/GRID), round((gx+1)*w/GRID)
            m = mask[y0:y1, x0:x1]
            s = smap[y0:y1, x0:x1]
            if m.size and int(m.sum()) >= max(1, int(0.05*m.size)):
                vals.append(float(s[m].mean()))
    if not vals: vals = [float(smap.mean())]
    err = np.abs(orig.astype(np.int16)-rec.astype(np.int16))
    psnr = 99.0 if int(err.max()) == 0 else float(peak_signal_noise_ratio(orig, rec, data_range=255))
    return {"psnr_db": psnr, "ssim_mean": float(smap.mean()),
            "lung_region_ssim_p05": float(np.percentile(vals, PERCENTILE)),
            "lung_region_ssim_min": float(np.min(vals)), "max_abs_error": int(err.max())}

def residual_bytes(orig, base):
    """Encode a measured, independently decodable signed-residual payload."""
    r = orig.astype(np.int16)-base.astype(np.int16)
    h,w = r.shape
    return b"RSD1"+struct.pack("<II",h,w)+zlib.compress(r.astype("<i2",copy=False).tobytes(),9)

def decode_residual(base, payload):
    """Decode the residual payload and reconstruct the normalized 8-bit image."""
    if len(payload) < 12 or payload[:4] != b"RSD1":
        raise ValueError("Invalid residual payload header")
    h,w = struct.unpack("<II", payload[4:12])
    if base.shape != (h,w):
        raise ValueError(f"Residual shape {(h,w)} does not match base {base.shape}")
    residual = np.frombuffer(zlib.decompress(payload[12:]), dtype="<i2")
    if residual.size != h*w:
        raise ValueError("Residual payload length does not match declared dimensions")
    return np.clip(base.astype(np.int16)+residual.reshape(h,w),0,255).astype(np.uint8)

def load_data():
    repo = os.environ.get("DATASET_REPO", "Famatsu123/montgomery-shenzhen-tuberculosis-cxr")
    api = HfApi()
    files = set(api.list_repo_files(repo_id=repo, repo_type="dataset"))
    image_paths = sorted(p for p in files if p.startswith("MontgomerySet/CXR_png/") and p.lower().endswith(".png"))
    if not image_paths:
        raise RuntimeError("No Montgomery PNGs found in the Hugging Face repository")
    limit = int(os.environ.get("MAX_IMAGES", "30"))
    if limit > 0 and len(image_paths) > limit:
        sample_rng = np.random.default_rng(SEED)
        idx = sorted(sample_rng.choice(len(image_paths), size=limit, replace=False).tolist())
        image_paths = [image_paths[i] for i in idx]
    out=[]
    for image_path in image_paths:
        filename = image_path.rsplit("/",1)[-1]
        path = Path(hf_hub_download(repo_id=repo, filename=image_path, repo_type="dataset"))
        with Image.open(path) as im:
            mode = im.mode
            arr0 = np.asarray(im)
        if arr0.ndim != 2:
            raise RuntimeError(f"Non-grayscale source {filename}: mode={mode}, dtype={arr0.dtype}")
        source_dtype = str(arr0.dtype)
        source_min, source_max = int(arr0.min()), int(arr0.max())
        if arr0.dtype == np.uint8:
            arr = arr0.astype(np.uint8)
            intensity_mapping = "identity_uint8"
        elif np.issubdtype(arr0.dtype, np.integer) and source_min >= 0 and source_max <= 4095:
            arr = np.rint(arr0.astype(np.float32) * (255.0 / 4095.0)).clip(0,255).astype(np.uint8)
            intensity_mapping = "fixed_linear_0_4095_to_0_255"
        else:
            raise RuntimeError(f"Unsupported source range for {filename}: mode={mode}, dtype={arr0.dtype}, min={source_min}, max={source_max}; no undocumented conversion applied.")
        mask = np.zeros_like(arr, dtype=bool)
        found = 0
        for md in ("MontgomerySet/ManualMask/leftMask", "MontgomerySet/ManualMask/rightMask"):
            mask_path = md + "/" + filename
            if mask_path in files:
                mp = Path(hf_hub_download(repo_id=repo, filename=mask_path, repo_type="dataset"))
                with Image.open(mp) as mi:
                    ma = np.asarray(mi.convert("L"))
                if ma.shape != arr.shape:
                    raise RuntimeError(f"Mask shape mismatch for {filename}: {ma.shape} vs {arr.shape}")
                mask |= ma > 0
                found += 1
        if found == 0:
            raise RuntimeError(f"No lung masks found for {filename}; refusing unmasked run")
        source_file_bytes = path.stat().st_size
        source_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        out.append((filename, arr, mask, mode, found, source_dtype, source_min, source_max,
                    intensity_mapping, source_file_bytes, source_sha256))
    return out

def main():
    if not features.check("jpg_2000"): raise RuntimeError("Pillow lacks JPEG2000 support")
    data = load_data()
    rng = np.random.default_rng(SEED)
    estimator = {k: [v[0], (0.3*v[0])**2] for k,v in PROFILES.items()}
    quality_rows, delivery_rows, manifest_rows, candidate_rows = [], [], [], []
    for ix,(name,orig,mask,mode,nmasks,source_dtype,source_min,source_max,intensity_mapping,source_file_bytes,source_sha256) in enumerate(data,1):
        candidates=[]
        for ratio in RATIOS:
            payload,rec=encode(orig,"JPEG2000",ratio)
            cm = metrics(orig,rec,mask)
            candidates.append({"ratio":ratio,"payload":payload,"rec":rec,"size":len(payload),"m":cm})
            candidate_rows.append({"image":name,"ratio":ratio,"payload_bytes":len(payload),
                                   "raw_8bit_bytes":int(orig.size),
                                   "compression_ratio_vs_raw_8bit":float(orig.size/len(payload)),**cm})
        jpeg,jrec=encode(orig,"JPEG",JPEG_Q)
        fixed=min(candidates,key=lambda c:abs(c["ratio"]-FIXED_J2K))
        mean_feasible=[c for c in candidates if c["m"]["ssim_mean"]>=Q_MIN]
        region_feasible=[c for c in candidates if c["m"]["lung_region_ssim_p05"]>=Q_MIN and c["m"]["max_abs_error"]<=MAX_ERROR]
        # If the mean-SSIM constraint is infeasible, preserve the highest-quality candidate.
        mean_pick=min(mean_feasible,key=lambda c:c["size"]) if mean_feasible else max(
            candidates,key=lambda c:(c["m"]["ssim_mean"],-c["size"]))
        if region_feasible:
            region_pick=min(region_feasible,key=lambda c:c["size"])
        else:
            lp=lossless_j2k(orig)
            lr=np.asarray(Image.open(io.BytesIO(lp)).convert("L"),dtype=np.uint8)
            region_pick={"ratio":1,"payload":lp,"rec":lr,"size":len(lp),"m":metrics(orig,lr,mask)}
        base_methods={
          "B1_fixed_jpeg":{"size":len(jpeg),"first":len(jpeg),"full":len(jpeg),"m":metrics(orig,jrec,mask),"ratio":np.nan},
          "B2_fixed_j2k":{"size":fixed["size"],"first":fixed["size"],"full":fixed["size"],"m":fixed["m"],"ratio":fixed["ratio"]},
          "B3_mean_ssim_single":{"size":mean_pick["size"],"first":mean_pick["size"],"full":mean_pick["size"],"m":mean_pick["m"],"ratio":mean_pick["ratio"]},
          "P1_lung_region_bound_single":{"size":region_pick["size"],"first":region_pick["size"],"full":region_pick["size"],"m":region_pick["m"],"ratio":region_pick["ratio"]},
        }
        for meth,item in base_methods.items():
            quality_rows.append({"image":name,"method":meth,"payload_bytes":item["size"],
                                 "raw_8bit_bytes":int(orig.size),
                                 "compression_ratio_vs_raw_8bit":float(orig.size/item["size"]),
                                 "selected_jpeg2000_ratio":item.get("ratio",np.nan),
                                 "p1_used_lossless_fallback":bool(meth=="P1_lung_region_bound_single" and not region_feasible),
                                 **item["m"]})
        for prof,(mean_bps,rel_std,deadline) in PROFILES.items():
            mu,var=estimator[prof]
            b_lo=max(mu-math.sqrt(max(var,0)),0.1*mu)
            feasible=[c for c in candidates if c["size"]*8/b_lo+LATENCY<=deadline]
            base=min(feasible,key=lambda c:c["size"]) if feasible else min(candidates,key=lambda c:c["size"])
            resid=residual_bytes(orig,base["rec"])
            residual_reconstruction=decode_residual(base["rec"],resid)
            if not np.array_equal(residual_reconstruction,orig):
                raise RuntimeError(f"Residual round-trip verification failed for {name}")
            p2={"size":len(base["payload"])+len(resid),"first":len(base["payload"]),
                "full":len(base["payload"])+len(resid),"m":metrics(orig,orig,mask),
                "base_m":base["m"],"base_ratio":base["ratio"],"residual_bytes":len(resid)}
            all_methods=dict(base_methods)
            all_methods["P2_deadline_aware_base_residual"]=p2
            actual=mean_bps*rng.lognormal(0,rel_std)/math.exp(rel_std**2/2)
            for meth,item in all_methods.items():
                tfirst=item["first"]*8/actual+LATENCY
                tfull=item["full"]*8/actual+LATENCY
                if meth=="P2_deadline_aware_base_residual" and tfull<=deadline:
                    delivered=item["m"]; delivered_bytes=item["full"]
                    bound=int(delivered["lung_region_ssim_p05"]>=Q_MIN and delivered["max_abs_error"]<=MAX_ERROR)
                elif meth=="P2_deadline_aware_base_residual" and tfirst<=deadline<tfull:
                    delivered=item["base_m"]; delivered_bytes=item["first"]
                    bound=int(delivered["lung_region_ssim_p05"]>=Q_MIN and delivered["max_abs_error"]<=MAX_ERROR)
                elif tfirst>deadline:
                    delivered={"psnr_db":np.nan,"ssim_mean":np.nan,"lung_region_ssim_p05":np.nan,
                               "lung_region_ssim_min":np.nan,"max_abs_error":np.nan}
                    delivered_bytes=0; bound=0
                else:
                    delivered=item["m"]; delivered_bytes=item["full"]
                    bound=int(delivered["lung_region_ssim_p05"]>=Q_MIN and delivered["max_abs_error"]<=MAX_ERROR and tfull<=deadline)
                delivery_rows.append({"image":name,"profile":prof,"method":meth,
                    "full_payload_kb":item["full"]/1024,"bytes_delivered_by_deadline":delivered_bytes,
                    "first_stage_seconds":tfirst,"full_delivery_seconds":tfull,"deadline_seconds":deadline,
                    "deadline_miss":int(tfirst>deadline),"full_delivery_miss":int(tfull>deadline),
                    "quality_bound_met_by_deadline":bound,"actual_bandwidth_bps":actual,
                    "estimated_lower_bandwidth_bps":b_lo,**delivered,
                    "p2_base_ratio":item.get("base_ratio",np.nan),
                    "p2_residual_bytes":item.get("residual_bytes",np.nan)})
            delta=actual-mu; a=0.3
            estimator[prof]=[a*actual+(1-a)*mu, a*delta*delta+(1-a)*var]
        manifest_rows.append({"image":name,"source_mode":mode,"source_dtype":source_dtype,
                              "source_min":source_min,"source_max":source_max,
                              "intensity_mapping":intensity_mapping,"benchmark_dtype":str(orig.dtype),
                              "width":orig.shape[1],"height":orig.shape[0],
                              "source_file_bytes":source_file_bytes,"source_sha256":source_sha256,
                              "lung_mask_files_found":nmasks,"lung_mask_pixel_fraction":float(mask.mean())})
        print(f"[{ix}/{len(data)}] {name}: {orig.shape}, mask files={nmasks}",flush=True)
    out=Path("results"); out.mkdir(exist_ok=True)
    qdf=pd.DataFrame(quality_rows); ddf=pd.DataFrame(delivery_rows)
    qdf.to_csv(out/"quality_by_image.csv",index=False)
    ddf.to_csv(out/"delivery_by_image_profile.csv",index=False)
    pd.DataFrame(manifest_rows).to_csv(out/"dataset_manifest.csv",index=False)
    cdf=pd.DataFrame(candidate_rows)
    cdf.to_csv(out/"candidate_diagnostics.csv",index=False)
    summary=ddf.groupby(["method","profile"],as_index=False).agg(
      n_images=("image","nunique"),n_images_quality_available=("psnr_db","count"),mean_full_payload_kb=("full_payload_kb","mean"),
      mean_psnr_db=("psnr_db","mean"),mean_ssim=("ssim_mean","mean"),
      mean_lung_region_ssim_p05=("lung_region_ssim_p05","mean"),
      deadline_miss_rate=("deadline_miss","mean"),
      full_delivery_miss_rate=("full_delivery_miss","mean"),
      quality_bound_met_by_deadline_rate=("quality_bound_met_by_deadline","mean"),
      mean_first_stage_seconds=("first_stage_seconds","mean"),
      mean_full_delivery_seconds=("full_delivery_seconds","mean"))
    summary.to_csv(out/"summary.csv",index=False)
    # Paired per-image inference: P1 versus B3 for quality-bound selection.
    stats=[]; boot_rng=np.random.default_rng(SEED)
    for metric in ["payload_bytes","psnr_db","ssim_mean","lung_region_ssim_p05"]:
        a=qdf[qdf.method=="B3_mean_ssim_single"].set_index("image")[metric]
        b=qdf[qdf.method=="P1_lung_region_bound_single"].set_index("image")[metric]
        pair=pd.concat([a.rename("b3"),b.rename("p1")],axis=1).dropna()
        diff=(pair.p1-pair.b3).to_numpy(float)
        if len(diff):
            boot=np.array([boot_rng.choice(diff,size=len(diff),replace=True).mean() for _ in range(2000)])
            try: p=float(wilcoxon(pair.p1,pair.b3,zero_method="wilcox").pvalue) if np.any(diff!=0) else 1.0
            except ValueError: p=1.0
            stats.append({"comparison":"P1_minus_B3","metric":metric,"n_pairs":len(diff),
              "mean_difference":float(diff.mean()),"median_difference":float(np.median(diff)),
              "bootstrap_ci95_low":float(np.percentile(boot,2.5)),
              "bootstrap_ci95_high":float(np.percentile(boot,97.5)),
              "wilcoxon_p_two_sided":p})
    # Paired bootstrap for delivery differences (P2 minus P1) by network profile.
    for prof in PROFILES:
        g=ddf[ddf.profile==prof]
        for metric in ["full_delivery_miss","quality_bound_met_by_deadline"]:
            a=g[g.method=="P1_lung_region_bound_single"].set_index("image")[metric]
            b=g[g.method=="P2_deadline_aware_base_residual"].set_index("image")[metric]
            pair=pd.concat([a.rename("p1"),b.rename("p2")],axis=1).dropna()
            diff=(pair.p2-pair.p1).to_numpy(float)
            if len(diff):
                boot=np.array([boot_rng.choice(diff,size=len(diff),replace=True).mean() for _ in range(2000)])
                stats.append({"comparison":f"P2_minus_P1_{prof}","metric":metric,"n_pairs":len(diff),
                  "mean_difference":float(diff.mean()),"median_difference":float(np.median(diff)),
                  "bootstrap_ci95_low":float(np.percentile(boot,2.5)),
                  "bootstrap_ci95_high":float(np.percentile(boot,97.5)),
                  "wilcoxon_p_two_sided":float(wilcoxon(pair.p2,pair.p1,zero_method="wilcox").pvalue) if np.any(diff!=0) else 1.0})
    pd.DataFrame(stats).to_csv(out/"paired_comparisons.csv",index=False)
    # Check monotonicity only as a diagnostic; selection itself uses exhaustive evaluation.
    mono=[]
    for image,gg in cdf.sort_values("ratio").groupby("image"):
        sizes=gg["payload_bytes"].to_numpy(); meanq=gg["ssim_mean"].to_numpy(); regionq=gg["lung_region_ssim_p05"].to_numpy()
        mono.append({"image":image,"size_monotonic_violations":int(np.sum(np.diff(sizes)>0)),
          "mean_ssim_monotonic_violations":int(np.sum(np.diff(meanq)>1e-9)),
          "region_ssim_monotonic_violations":int(np.sum(np.diff(regionq)>1e-9))})
    pd.DataFrame(mono).to_csv(out/"monotonicity_diagnostics.csv",index=False)
    meta={"run_timestamp_utc":datetime.now(timezone.utc).isoformat(),
      "python_version":sys.version,"platform":platform.platform(),
      "software_versions":{"numpy":np.__version__,"pandas":pd.__version__,"Pillow":PIL.__version__,
                           "scipy":scipy.__version__,"scikit_image":skimage.__version__,"huggingface_hub":huggingface_hub.__version__,
                           "huggingface_hub":huggingface_hub.__version__},
      "dataset_repo":"Famatsu123/montgomery-shenzhen-tuberculosis-cxr",
      "subset":"all MontgomerySet/CXR_png images when MAX_IMAGES=0; otherwise reproducible random sample with manual lung masks",
      "n_images":len(data),"expected_full_set_images":138,"max_images_env":int(os.environ.get("MAX_IMAGES","30")),
      "seed":SEED,"ratios":RATIOS,"q_min_ssim":Q_MIN,
      "region_percentile":PERCENTILE,"grid":GRID,"max_abs_error":MAX_ERROR,
      "fixed_jpeg_quality":JPEG_Q,"fixed_j2k_ratio":FIXED_J2K,"latency_seconds":LATENCY,
      "profiles":PROFILES,"synthetic":False,
      "notes":["Native 8-bit sources are unchanged. Integer sources with values in 0..4095 are mapped by a fixed linear full-range conversion to 8-bit; results therefore describe 8-bit renditions, not native 12-bit preservation.",
      "PSNR is capped at 99 dB for exact reconstruction in the metric function.",
      "The P2 residual is a separately encoded, losslessly compressed signed-pixel residual, not a progressive JPEG 2000 codestream.",
      "Network conditions are simulated and are not measured real-world traces.",
      "PSNR/SSIM do not establish diagnostic safety.",
      "The dataset mirror lists its license as 'other'; check source terms and retain attribution."]}
    (out/"run_metadata.json").write_text(json.dumps(meta,indent=2))
    print("\nSUMMARY\n"+summary.to_string(index=False),flush=True)
    print(f"Completed: {len(data)} real images. Synthetic inputs were not used.",flush=True)

if __name__=="__main__": main()
