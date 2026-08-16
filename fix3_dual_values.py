import numpy as np
import json
from pyproj import Transformer

sunlight = np.load("data/sunlight_score_400x400.npy")
ice = np.load("data/ice_score_400x400.npy")
dust = np.load("data/dust_risk_score_400x400.npy")

with open("grid_meta.json") as f:
    grid_meta = json.load(f)
with open("data/sunlight_ice_dust_final.json") as f:
    final_output = json.load(f)

GRID_SIZE = grid_meta["shape"][0]
HALF_EXTENT_M = grid_meta["bounds"]["right"]
RIM_SEARCH_RADIUS_KM = 20

for name, entry in final_output["named_sites"].items():
    lat, lon = entry["lat"], entry["lon"]
    row, col = entry["center_grid_row"], entry["center_grid_col"]

    # --- Value at the exact coordinate ---
    exact = {
        "sunlight_score": float(sunlight[row, col]),
        "ice_score": float(ice[row, col]),
        "dust_risk_score": float(dust[row, col]),
    }

    # --- Best (highest-sunlight) value within a 20km search window ---
    r = RIM_SEARCH_RADIUS_KM
    r0, r1 = max(0, row - r), min(GRID_SIZE, row + r + 1)
    c0, c1 = max(0, col - r), min(GRID_SIZE, col + r + 1)
    window = sunlight[r0:r1, c0:c1]
    best_local = np.unravel_index(np.argmax(window), window.shape)
    best_row, best_col = int(r0 + best_local[0]), int(c0 + best_local[1])

    best = {
        "grid_row": best_row, "grid_col": best_col,
        "sunlight_score": float(sunlight[best_row, best_col]),
        "ice_score": float(ice[best_row, best_col]),
        "dust_risk_score": float(dust[best_row, best_col]),
    }

    # Clean up old/ambiguous fields, replace with clearly-named pair
    for old_key in ["sampled_grid_row", "sampled_grid_col", "sampling_note",
                     "sunlight_score", "ice_score", "dust_risk_score"]:
        entry.pop(old_key, None)

    entry["score_at_exact_coordinate"] = exact
    entry["best_score_within_20km_search"] = best

for name, entry in final_output["named_sites"].items():
    print(name)
    print("  exact:", entry["score_at_exact_coordinate"])
    print("  best within 20km:", entry["best_score_within_20km_search"])

with open("data/sunlight_ice_dust_final.json", "w") as f:
    json.dump(final_output, f)

print("\nSaved data/sunlight_ice_dust_final.json with both exact and searched values")
