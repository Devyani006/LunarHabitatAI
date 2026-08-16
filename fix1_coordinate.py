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

# --- Corrected coordinate from teammate (per QuickMap check) ---
# NOTE: this is the IAU Gazetteer coordinate for "Malapert" crater
# (84.9S, 12.9E), NOT the Mons Malapert / Malapert Massif summit
# landing site (85.964S, -2.319E) used previously. Confirm with your
# teammate this is intentional before treating this as final.
NEW_LAT, NEW_LON = -84.9, 12.9

old_entry = final_output["named_sites"]["Malapert Massif"]
print("OLD entry:", old_entry)

row, col = latlon_to_rowcol(NEW_LAT, NEW_LON)
if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
    print(f"WARNING: corrected coordinate falls OUTSIDE the 400x400km grid (row={row}, col={col})")
else:
    new_entry = {
        "lat": NEW_LAT, "lon": NEW_LON,
        "center_grid_row": row, "center_grid_col": col,
        "sampled_grid_row": row, "sampled_grid_col": col,
        "sampling_note": "exact coordinate",
        "sunlight_score": float(sunlight[row, col]),
        "ice_score": float(ice[row, col]),
        "dust_risk_score": float(dust[row, col]),
    }
    final_output["named_sites"]["Malapert Massif"] = new_entry
    print("\nNEW entry:", new_entry)

    with open("data/sunlight_ice_dust_final.json", "w") as f:
        json.dump(final_output, f)
    print("\nSaved updated data/sunlight_ice_dust_final.json")
