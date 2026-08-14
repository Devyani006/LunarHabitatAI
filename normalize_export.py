import json
import numpy as np
from pyproj import Transformer

# --- Load ---
with open(r"D:\lunar-terrain-track\elevation_grid.json", encoding="utf-8") as f:
    data = json.load(f)

meta = data["grid_meta"]
shape = meta["shape"]          # [400, 400]
bounds = meta["bounds"]        # left/right/top/bottom in meters
pixel_size = (bounds["right"] - bounds["left"]) / shape[1]  # should be 1000 m

suitability_raw = np.array(data["landing_suitability_raw"])
is_flat = np.array(data["is_flat"], dtype=bool)

# --- Step 1: final 0-100 score (no extra rescaling — raw is already 0-1 bounded) ---
final_score = suitability_raw * 100.0
data["landing_suitability_score"] = final_score.tolist()

# --- Step 2: project named sites (lat/lon -> grid row/col) ---
# Source: Moon geographic sphere. Target: Moon South Polar Stereographic (matches grid_meta).
transformer = Transformer.from_crs(
    "+proj=longlat +R=1737400 +no_defs",
    "+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R=1737400 +units=m +no_defs",
    always_xy=True
)

named_sites = {
    "Shackleton Crater Rim": {"lat": -89.66, "lon": 129.88, "confidence": "high"},
    "de Gerlache Rim":       {"lat": -88.5,  "lon": -87.1,  "confidence": "medium (crater center used as rim proxy)"},
    "Malapert Massif":       {"lat": -84.9,  "lon": 12.9,   "confidence": "low (crater center used as massif proxy — not the actual peak)"},
    "Faustini Rim":          {"lat": -87.3,  "lon": 77.0,   "confidence": "medium (two published coordinate sets disagree by ~7° lon)"},
    "Nobile Rim":            {"lat": -85.28, "lon": 53.27,  "confidence": "medium (crater center used as rim proxy)"},
    "Haworth Crater":        {"lat": -86.9,  "lon": -4.0,   "confidence": "high"},
}

for name, site in named_sites.items():
    x, y = transformer.transform(site["lon"], site["lat"])
    col = int((x - bounds["left"]) / pixel_size)
    row = int((bounds["top"] - y) / pixel_size)

    if 0 <= row < shape[0] and 0 <= col < shape[1]:
        site["x_m"] = x
        site["y_m"] = y
        site["row"] = row
        site["col"] = col
        site["landing_suitability_score"] = float(final_score[row, col])
        site["is_flat"] = bool(is_flat[row, col])
    else:
        site["error"] = "falls outside the 400x400 grid bounds"
        print(f"WARNING: {name} projects outside the grid — check its coordinates.")

data["named_sites"] = named_sites

# --- Save final file ---
out_path = r"D:\lunar-terrain-track\final_terrain_hazard_output.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f)

print("\n--- Named site scores ---")
for name, site in named_sites.items():
    if "landing_suitability_score" in site:
        print(f"{name}: score={site['landing_suitability_score']:.1f}, is_flat={site['is_flat']}, confidence={site['confidence']}")
    else:
        print(f"{name}: {site.get('error')}")

print(f"\nSaved final output to {out_path}")