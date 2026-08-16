import numpy as np
import json
from pyproj import Transformer

# --- Regenerate sunlight_score from the corrected MAX-resampled illumination ---
illum_max = np.load("data/illumination_400x400_max.npy")
sunlight_score = np.clip(illum_max, 0, 100).astype(np.float32)

print("New sunlight_score -- Min:", sunlight_score.min(), "Max:", sunlight_score.max(), "Mean:", sunlight_score.mean())
np.save("data/sunlight_score_400x400.npy", sunlight_score)

# --- ice_score and dust_risk_score stay as-is (unaffected by this fix) ---
ice = np.load("data/ice_score_400x400.npy")
dust = np.load("data/dust_risk_score_400x400.npy")

with open("grid_meta.json") as f:
    grid_meta = json.load(f)
with open("data/sunlight_ice_dust_final.json") as f:
    final_output = json.load(f)

GRID_SIZE = grid_meta["shape"][0]
HALF_EXTENT_M = grid_meta["bounds"]["right"]

transformer = Transformer.from_crs(
    "+proj=longlat +R=1737400 +no_defs",
    "+proj=stere +lat_0=-90 +lon_0=0 +x_0=0 +y_0=0 +R=1737400 +units=m +no_defs",
    always_xy=True
)

def latlon_to_rowcol(lat, lon):
    x, y = transformer.transform(lon, lat)
    col = int((x + HALF_EXTENT_M) / (2 * HALF_EXTENT_M) * GRID_SIZE)
    row = int((HALF_EXTENT_M - y) / (2 * HALF_EXTENT_M) * GRID_SIZE)
    return row, col

RIM_SEARCH_RADIUS_KM = 20

# Re-sample each existing named site against the CORRECTED sunlight grid,
# keeping the same lat/lon and same rim-vs-exact sampling logic as before.
rim_sites = {"Shackleton Crater Rim", "de Gerlache Rim", "Faustini Rim", "Nobile Rim"}

for name, entry in final_output["named_sites"].items():
    lat, lon = entry["lat"], entry["lon"]
    row, col = latlon_to_rowcol(lat, lon)
    if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
        continue

    if name in rim_sites:
        r = RIM_SEARCH_RADIUS_KM
        r0, r1 = max(0, row - r), min(GRID_SIZE, row + r + 1)
        c0, c1 = max(0, col - r), min(GRID_SIZE, col + r + 1)
        window = sunlight_score[r0:r1, c0:c1]
        best_local = np.unravel_index(np.argmax(window), window.shape)
        best_row, best_col = int(r0 + best_local[0]), int(c0 + best_local[1])
    else:
        best_row, best_col = row, col

    entry["sampled_grid_row"] = best_row
    entry["sampled_grid_col"] = best_col
    entry["sunlight_score"] = float(sunlight_score[best_row, best_col])
    entry["ice_score"] = float(ice[best_row, best_col])
    entry["dust_risk_score"] = float(dust[best_row, best_col])

for name, r in final_output["named_sites"].items():
    print(name, "-> sunlight:", round(r["sunlight_score"], 2), " ice:", round(r["ice_score"], 2))

final_output["sunlight_score"] = sunlight_score.tolist()

with open("data/sunlight_ice_dust_final.json", "w") as f:
    json.dump(final_output, f)

print("\nSaved updated data/sunlight_ice_dust_final.json with corrected sunlight scores")
