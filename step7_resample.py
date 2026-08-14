import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from rasterio.warp import reproject
import numpy as np
import json

lbl_path = "data/AVGVISIB_75S_120M_201608.LBL"

# --- Shared grid contract (must match your teammate exactly) ---
GRID_SIZE = 400
HALF_EXTENT_M = 200_000  # 200 km each direction -> 400 km square
# -----------------------------------------------------------------

with rasterio.open(lbl_path) as src:
    raw = src.read(1)
    scale = src.scales[0]
    src_crs = src.crs
    src_transform = src.transform

illumination_pct = (raw * scale * 100).astype(np.float32)

dst_transform = from_bounds(
    -HALF_EXTENT_M, -HALF_EXTENT_M, HALF_EXTENT_M, HALF_EXTENT_M,
    GRID_SIZE, GRID_SIZE
)
dst_array = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float32)

reproject(
    source=illumination_pct,
    destination=dst_array,
    src_transform=src_transform,
    src_crs=src_crs,
    dst_transform=dst_transform,
    dst_crs=src_crs,
    resampling=Resampling.average,
)

print("Resampled grid shape:", dst_array.shape)
print("Min:", dst_array.min(), "Max:", dst_array.max(), "Mean:", dst_array.mean())

grid_meta = {
    "shape": [GRID_SIZE, GRID_SIZE],
    "bounds": {
        "left": -HALF_EXTENT_M, "right": HALF_EXTENT_M,
        "bottom": -HALF_EXTENT_M, "top": HALF_EXTENT_M
    },
    "projection": src_crs.to_wkt()
}
with open("grid_meta.json", "w") as f:
    json.dump(grid_meta, f, indent=2)
print("Saved grid_meta.json")

np.save("data/illumination_400x400.npy", dst_array)
print("Saved data/illumination_400x400.npy")
