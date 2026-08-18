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

NEW_LAT, NEW_LON = -85.964, -2.319

old_entry = final_output["named_sites"]["Malapert Massif"]
print("OLD entry:")
print(json.dumps(old_entry, indent=2))

row, col = latlon_to_rowcol(NEW_LAT, NEW_LON)
if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
    print(f"WARNING: coordinate falls OUTSIDE the 400x400km grid (row={row}, col={col})")
else:
    exact = {
        "sunlight_score": round(float(sunlight[row, col]), 1),
        "ice_score": round(float(ice[row, col]), 1),
        "dust_risk_score": round(float(dust[row, col]), 1),
    }

    r = RIM_SEARCH_RADIUS_KM
    r0, r1 = max(0, row - r), min(GRID_SIZE, row + r + 1)
    c0, c1 = max(0, col - r), min(GRID_SIZE, col + r + 1)
    window = sunlight[r0:r1, c0:c1]
    best_local = np.unravel_index(np.argmax(window), window.shape)
    best_row, best_col = int(r0 + best_local[0]), int(c0 + best_local[1])

    best = {
        "grid_row": best_row, "grid_col": best_col,
        "sunlight_score": round(float(sunlight[best_row, best_col]), 1),
        "ice_score": round(float(ice[best_row, best_col]), 1),
        "dust_risk_score": round(float(dust[best_row, best_col]), 1),
    }

    new_entry = {
        "lat": NEW_LAT, "lon": NEW_LON,
        "center_grid_row": row, "center_grid_col": col,
        "score_at_exact_coordinate": exact,
        "best_score_within_20km_search": best,
        "ice_score_caveat": old_entry.get("ice_score_caveat", ""),
        "dust_risk_score_note": old_entry.get("dust_risk_score_note", ""),
        "correction_note": ("Reverted to the Mons Malapert / Malapert Massif summit "
                             "landing site coordinate (-85.964, -2.319), confirmed with "
                             "teammate. Previous value (-84.9, 12.9) corresponded to "
                             "Malapert crater, a different nearby feature."),
    }

    final_output["named_sites"]["Malapert Massif"] = new_entry
    print("\nNEW entry:")
    print(json.dumps(new_entry, indent=2))

    with open("data/sunlight_ice_dust_final.json", "w") as f:
        json.dump(final_output, f)
    print("\nSaved updated data/sunlight_ice_dust_final.json")
