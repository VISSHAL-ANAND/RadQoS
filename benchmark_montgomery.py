#!/usr/bin/env python3
"""Cloud benchmark on Montgomery CXR images. Synthetic data are never used here."""
import io, json, math, struct, zlib
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image, features
from huggingface_hub import snapshot_download
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
    r = orig.astype(np.int16)-base.astype(np.int16)
    h,w = r.shape
    return b"RSD1"+struct.pack("<II",h,w)+zlib.compress(r.astype("<i2",copy=False).tobytes(),9)

def load_data():
    root = Path(snapshot_download(
        repo_id="Famatsu123/montgomery-shenzhen-tuberculosis-cxr",
        repo_type="dataset",
        allow_patterns=["MontgomerySet/CXR_png/*.png",
                        "MontgomerySet/ManualMask/leftMask/*.png",
                        "MontgomerySet/ManualMask/rightMask/*.png"],
    ))
    image_dir = root/"MontgomerySet/CXR_png"
    left_dir = root/"MontgomerySet/ManualMask/leftMask"
    right_dir = root/"MontgomerySet/ManualMask/rightMask"
    images = sorted(image_dir.glob("*.png"))
    if not images: raise RuntimeError(f"No Montgomery PNGs found at {image_dir}")
    out=[]
    for path in images:
        with Image.open(path) as im:
            mode = im.mode
            arr0 = np.asarray(im)
        if arr0.ndim != 2 or arr0.dtype != np.uint8:
            raise RuntimeError(f"High-bit-depth/non-grayscale source {path.name}: mode={mode}, dtype={arr0.dtype}; refusing undocumented intensity conversion.")
        arr = arr0.astype(np.uint8)
        mask = np.zeros_like(arr, dtype=bool)
        found = 0
        for md in (left_dir, right_dir):
            mp = md/path.name
            if mp.exists():
                with Image.open(mp) as mi:
                    ma = np.asarray(mi.convert("L"))
                if ma.shape != arr.shape: raise RuntimeError(f"Mask shape mismatch for {path.name}")
                mask |= ma > 0
                found += 1
        if found == 0:
            raise RuntimeError(f"No lung masks found for {path.name}; refusing unmasked run")
        out.append((path.name, arr, mask, mode, found))
    return out

def main():
    if not features.check("jpg_2000"): raise RuntimeError("Pillow lacks JPEG2000 support")
    data = load_data()
    rng = np.random.default_rng(SEED)
    estimator = {k: [v[0], (0.3*v[0])**2] for k,v in PROFILES.items()}
    quality_rows, delivery_rows, manifest_rows = [], [], []
    for ix,(name,orig,mask,mode,nmasks) in enumerate(data,1):
        candidates=[]
        for ratio in RATIOS:
            payload,rec=encode(orig,"JPEG2000",ratio)
            candidates.append({"ratio":ratio,"payload":payload,"rec":rec,"size":len(payload),
                               "m":metrics(orig,rec,mask)})
        jpeg,jrec=encode(orig,"JPEG",JPEG_Q)
        fixed=min(candidates,key=lambda c:abs(c["ratio"]-FIXED_J2K))
        mean_feasible=[c for c in candidates if c["m"]["ssim_mean"]>=Q_MIN]
        region_feasible=[c for c in candidates if c["m"]["lung_region_ssim_p05"]>=Q_MIN and c["m"]["max_abs_error"]<=MAX_ERROR]
        mean_pick=max(mean_feasible,key=lambda c:c["ratio"]) if mean_feasible else min(candidates,key=lambda c:c["size"])
        if region_feasible:
            region_pick=max(region_feasible,key=lambda c:c["ratio"])
        else:
            lp=lossless_j2k(orig)
            lr=np.asarray(Image.open(io.BytesIO(lp)).convert("L"),dtype=np.uint8)
            region_pick={"ratio":1,"payload":lp,"rec":lr,"size":len(lp),"m":metrics(orig,lr,mask)}
        base_methods={
          "B1_fixed_jpeg":{"size":len(jpeg),"first":len(jpeg),"full":len(jpeg),"m":metrics(orig,jrec,mask)},
          "B2_fixed_j2k":{"size":fixed["size"],"first":fixed["size"],"full":fixed["size"],"m":fixed["m"]},
          "B3_mean_ssim_single":{"size":mean_pick["size"],"first":mean_pick["size"],"full":mean_pick["size"],"m":mean_pick["m"]},
          "P1_lung_region_bound_single":{"size":region_pick["size"],"first":region_pick["size"],"full":region_pick["size"],"m":region_pick["m"]},
        }
        for meth,item in base_methods.items():
            quality_rows.append({"image":name,"method":meth,"payload_bytes":item["size"],**item["m"]})
        for prof,(mean_bps,rel_std,deadline) in PROFILES.items():
            mu,var=estimator[prof]
            b_lo=max(mu-math.sqrt(max(var,0)),0.1*mu)
            feasible=[c for c in candidates if c["size"]*8/b_lo+LATENCY<=deadline]
            base=max(feasible,key=lambda c:c["ratio"]) if feasible else min(candidates,key=lambda c:c["size"])
            resid=residual_bytes(orig,base["rec"])
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
        manifest_rows.append({"image":name,"source_mode":mode,"dtype":str(orig.dtype),
                              "width":orig.shape[1],"height":orig.shape[0],
                              "lung_mask_files_found":nmasks,"lung_mask_pixel_fraction":float(mask.mean())})
        print(f"[{ix}/{len(data)}] {name}: {orig.shape}, mask files={nmasks}",flush=True)
    out=Path("results"); out.mkdir(exist_ok=True)
    qdf=pd.DataFrame(quality_rows); ddf=pd.DataFrame(delivery_rows)
    qdf.to_csv(out/"quality_by_image.csv",index=False)
    ddf.to_csv(out/"delivery_by_image_profile.csv",index=False)
    pd.DataFrame(manifest_rows).to_csv(out/"dataset_manifest.csv",index=False)
    summary=ddf.groupby(["method","profile"],as_index=False).agg(
      n_images=("image","nunique"),mean_full_payload_kb=("full_payload_kb","mean"),
      mean_psnr_db=("psnr_db","mean"),mean_ssim=("ssim_mean","mean"),
      mean_lung_region_ssim_p05=("lung_region_ssim_p05","mean"),
      full_delivery_miss_rate=("full_delivery_miss","mean"),
      quality_bound_met_by_deadline_rate=("quality_bound_met_by_deadline","mean"),
      mean_full_delivery_seconds=("full_delivery_seconds","mean"))
    summary.to_csv(out/"summary.csv",index=False)
    meta={"dataset_repo":"Famatsu123/montgomery-shenzhen-tuberculosis-cxr",
      "subset":"all available MontgomerySet/CXR_png images with both manual lung masks",
      "n_images":len(data),"seed":SEED,"ratios":RATIOS,"q_min_ssim":Q_MIN,
      "region_percentile":PERCENTILE,"grid":GRID,"max_abs_error":MAX_ERROR,
      "fixed_jpeg_quality":JPEG_Q,"fixed_j2k_ratio":FIXED_J2K,"latency_seconds":LATENCY,
      "profiles":PROFILES,"synthetic":False,
      "notes":["Dataset images must be 8-bit grayscale; script stops instead of silently converting high-bit-depth data.",
      "The P2 residual is a separately encoded, losslessly compressed signed-pixel residual, not a progressive JPEG 2000 codestream.",
      "Network conditions are simulated and are not measured real-world traces.",
      "PSNR/SSIM do not establish diagnostic safety.",
      "The dataset mirror lists its license as 'other'; check source terms and retain attribution."]}
    (out/"run_metadata.json").write_text(json.dumps(meta,indent=2))
    print("\nSUMMARY\n"+summary.to_string(index=False),flush=True)
    print(f"Completed: {len(data)} real images. Synthetic inputs were not used.",flush=True)

if __name__=="__main__": main()
