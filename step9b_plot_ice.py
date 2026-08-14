import numpy as np
import matplotlib.pyplot as plt

data = np.load("data/ice_score_400x400.npy")

plt.figure(figsize=(7, 7))
plt.imshow(data, cmap="Blues", vmin=0, vmax=100, extent=[-200, 200, -200, 200])
plt.colorbar(label="Water-Ice Proxy Score (0-100)")
plt.title("Water-Ice Proxy Score — South Pole")
plt.xlabel("km from pole (X)")
plt.ylabel("km from pole (Y)")
plt.savefig("data/ice_score_preview.png", dpi=150)
print("Saved data/ice_score_preview.png")
plt.show()
