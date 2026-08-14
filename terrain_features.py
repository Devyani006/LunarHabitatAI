import numpy as np
import json

with open(r"D:\lunar-terrain-track\elevation_grid.json", encoding="utf-8") as f:
    data = json.load(f)

elevation = np.array(data["elevation_m"])
pixel_size = 1000.0

# --- SLOPE ---
dz_dy, dz_dx = np.gradient(elevation, pixel_size)
slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
slope_deg = np.degrees(slope_rad)

print("Slope - min:", np.nanmin(slope_deg), "max:", np.nanmax(slope_deg), "mean:", np.nanmean(slope_deg))

# --- ROUGHNESS ---
from scipy.ndimage import generic_filter

def local_std(values):
    return np.std(values)

roughness = generic_filter(elevation, local_std, size=3)

print("Roughness - min:", np.nanmin(roughness), "max:", np.nanmax(roughness), "mean:", np.nanmean(roughness))

# --- FLAT-AREA % ---
FLAT_THRESHOLD_DEG = 10
is_flat = slope_deg < FLAT_THRESHOLD_DEG
flat_percent_overall = 100 * np.sum(is_flat) / is_flat.size

print(f"Overall flat area (<{FLAT_THRESHOLD_DEG} deg): {flat_percent_overall:.1f}%")

# --- SAVE (once, at the end, with everything included) ---
data["slope_deg"] = slope_deg.tolist()
data["roughness_m"] = roughness.tolist()
data["is_flat"] = is_flat.astype(int).tolist()

with open(r"D:\lunar-terrain-track\elevation_grid.json", "w", encoding="utf-8") as f:
    json.dump(data, f)

print("Saved slope, roughness, and flatness into elevation_grid.json")