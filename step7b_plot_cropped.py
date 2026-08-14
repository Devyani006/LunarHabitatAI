import numpy as np
import matplotlib.pyplot as plt

data = np.load("data/illumination_400x400.npy")

plt.figure(figsize=(7, 7))
plt.imshow(data, cmap="gray", vmin=0, vmax=100, extent=[-200, 200, -200, 200])
plt.colorbar(label="Illumination (%)")
plt.title("400x400 km Grid — South Pole Illumination")
plt.xlabel("km from pole (X)")
plt.ylabel("km from pole (Y)")
plt.savefig("data/illumination_400x400_preview.png", dpi=150)
print("Saved data/illumination_400x400_preview.png")
plt.show()
