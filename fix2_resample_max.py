import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from rasterio.warp import reproject
import numpy as np

lbl_path = "data/AVGVISIB_75S_120M_201608.LBL"

GRID_SIZE = 400
HALF_EXTENT_M = 200_000

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
dst_array_max = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float32)

reproject(
    source=illumination_pct,
    destination=dst_array_max,
    src_transform=src_transform,
    src_crs=src_crs,
    dst_transform=dst_transform,
    dst_crs=src_crs,
    resampling=Resampling.max,   # <-- changed from .average to .max
)

print("Resampled (MAX) grid shape:", dst_array_max.shape)
print("Min:", dst_array_max.min(), "Max:", dst_array_max.max(), "Mean:", dst_array_max.mean())

# Save as the new sunlight-specific illumination array (separate from the
# original average-based illumination_400x400.npy, which we keep for ice scoring)
np.save("data/illumination_400x400_max.npy", dst_array_max)
print("Saved data/illumination_400x400_max.npy")
