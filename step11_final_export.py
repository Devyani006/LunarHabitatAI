import numpy as np
import json
from pyproj import Transformer

# --- Load the three score layers ---
sunlight = np.load("data/sunlight_score_400x400.npy")
ice = np.load("data/ice_score_400x400.npy")
dust = np.load("data/dust_risk_score_400x400.npy")

with open("grid_meta.json") as f:
    grid_meta = json.load(f)

GRID_SIZE = grid_meta["shape"][0]
HALF_EXTENT_M = grid_meta["bounds"]["right"]  # 200000

# --- Named real candidate sites (lat/lon from IAU Gazetteer / NASA Artemis III spec) ---
sites = {
    "Shackleton Crater Rim": (-89.67, 129.78),
    "de Gerlache Rim":       (-88.5,   -87.1),
    "Malapert Massif":       (-85.964,  -2.319),
    "Faustini Rim":          (-87.3,   77.0),
    "Nobile Rim":            (-85.28,  53.27),
    "Haworth Crater":        (-86.9,   -4.0),
}

# --- Set up lat/lon -> South Polar Stereographic (Moon) transformer ---
# Matches the projection baked into our source data: proj=stere, lat_0=-90,
# lon_0=0, R=1737400 (lunar mean radius), spherical (flattening 0)
transformer = Transformer.from_crs(
    "+proj=longlat +R=1737400 +no_defs",
    "+proj=stere +lat_0=-90 +lon_0=0 +x_0=0 +y_0=0 +R=1737400 +units=m +no_defs",
    always_xy=True
)

def latlon_to_rowcol(lat, lon):
    x, y = transformer.transform(lon, lat)
    # Convert projected meters -> array row/col (row 0 = top = +Y, increasing south)
    col = int((x + HALF_EXTENT_M) / (2 * HALF_EXTENT_M) * GRID_SIZE)
    row = int((HALF_EXTENT_M - y) / (2 * HALF_EXTENT_M) * GRID_SIZE)
    return row, col

site_results = {}
for name, (lat, lon) in sites.items():
    row, col = latlon_to_rowcol(lat, lon)
    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
        site_results[name] = {
            "lat": lat, "lon": lon,
            "grid_row": row, "grid_col": col,
            "sunlight_score": float(sunlight[row, col]),
            "ice_score": float(ice[row, col]),
            "dust_risk_score": float(dust[row, col]),
        }
    else:
        site_results[name] = {"lat": lat, "lon": lon, "error": "outside 400x400km grid"}

for name, r in site_results.items():
    print(name, "->", r)

# --- Final export per shared contract ---
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
