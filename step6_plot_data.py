import rasterio
import numpy as np
import matplotlib.pyplot as plt

lbl_path = "data/AVGVISIB_75S_120M_201608.LBL"

with rasterio.open(lbl_path) as src:
    raw = src.read(1)
    scale = src.scales[0]

# Convert raw integers to real illumination fraction, then to percent
illumination_pct = raw * scale * 100

plt.figure(figsize=(8, 8))
plt.imshow(illumination_pct, cmap="gray", vmin=0, vmax=100)
plt.colorbar(label="Illumination (%)")
plt.title("Lunar South Pole — Average Solar Illumination")
plt.savefig("data/illumination_preview.png", dpi=150)
print("Saved plot to data/illumination_preview.png")
plt.show()
