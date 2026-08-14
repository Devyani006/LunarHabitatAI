import numpy as np
import json
from pyproj import Transformer

sunlight = np.load("data/sunlight_score_400x400.npy")
ice = np.load("data/ice_score_400x400.npy")
dust = np.load("data/dust_risk_score_400x400.npy")

with open("grid_meta.json") as f:
    grid_meta = json.load(f)

GRID_SIZE = grid_meta["shape"][0]
HALF_EXTENT_M = grid_meta["bounds"]["right"]

sites = {
    "Shackleton Crater Rim": (-89.67, 129.78, True),
    "de Gerlache Rim":       (-88.5,   -87.1, True),
    "Malapert Massif":       (-85.964,  -2.319, False),
    "Faustini Rim":          (-87.3,   77.0, True),
    "Nobile Rim":            (-85.28,  53.27, True),
    "Haworth Crater":        (-86.9,   -4.0, False),
}

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

site_results = {}
for name, (lat, lon, is_rim) in sites.items():
    row, col = latlon_to_rowcol(lat, lon)
    if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
        site_results[name] = {"lat": lat, "lon": lon, "error": "outside 400x400km grid"}
        continue

    if is_rim:
        r = RIM_SEARCH_RADIUS_KM
        r0, r1 = max(0, row - r), min(GRID_SIZE, row + r + 1)
        c0, c1 = max(0, col - r), min(GRID_SIZE, col + r + 1)
        window = sunlight[r0:r1, c0:c1]
        best_local = np.unravel_index(np.argmax(window), window.shape)
        best_row, best_col = int(r0 + best_local[0]), int(c0 + best_local[1])
    else:
        best_row, best_col = int(row), int(col)

    site_results[name] = {
        "lat": lat, "lon": lon,
        "center_grid_row": int(row), "center_grid_col": int(col),
        "sampled_grid_row": best_row, "sampled_grid_col": best_col,
        "sampling_note": f"brightest cell within {RIM_SEARCH_RADIUS_KM}km (rim search)" if is_rim else "exact coordinate",
        "sunlight_score": float(sunlight[best_row, best_col]),
        "ice_score": float(ice[best_row, best_col]),
        "dust_risk_score": float(dust[best_row, best_col]),
    }

for name, r in site_results.items():
    print(name, "->", r)

final_output = {
    "grid_meta": grid_meta,
    "sunlight_score": sunlight.tolist(),
    "ice_score": ice.tolist(),
    "dust_risk_score": dust.tolist(),
    "named_sites": site_results
}

with open("data/sunlight_ice_dust_final.json", "w") as f:
    json.dump(final_output, f)

print("\nSaved data/sunlight_ice_dust_final.json")
