import rasterio
import numpy as np
from rasterio.windows import from_bounds

lbl_path = "data/AVGVISIB_75S_120M_201608.LBL"

with rasterio.open(lbl_path) as src:
    scale = src.scales[0]

    # (1) True max across the ENTIRE raw dataset
    full_raw = src.read(1)
    full_illum_pct = full_raw * scale * 100
    print("=== (1) Full raw dataset (whole 75S product) ===")
    print("Max illumination %:", full_illum_pct.max())

    # (2) Max within just our 400x400km crop area, still at native 120m resolution
    window = from_bounds(-200000, -200000, 200000, 200000, transform=src.transform)
    cropped_raw = src.read(1, window=window)
    cropped_illum_pct = cropped_raw * scale * 100
    print("\n=== (2) Cropped to 400x400km area, native 120m resolution ===")
    print("Shape:", cropped_illum_pct.shape)
    print("Max illumination %:", cropped_illum_pct.max())

# (3) After our resampling to 400x400 (1km cells) -- already computed
resampled = np.load("data/illumination_400x400.npy")
print("\n=== (3) After resampling to 400x400 (1km cells) ===")
print("Max illumination %:", resampled.max())
