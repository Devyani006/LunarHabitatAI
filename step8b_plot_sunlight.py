import numpy as np
import matplotlib.pyplot as plt

data = np.load("data/sunlight_score_400x400.npy")

plt.figure(figsize=(7, 7))
plt.imshow(data, cmap="inferno", vmin=0, vmax=100, extent=[-200, 200, -200, 200])
plt.colorbar(label="Sunlight-Availability Score (0-100)")
plt.title("Sunlight-Availability Score — South Pole")
plt.xlabel("km from pole (X)")
plt.ylabel("km from pole (Y)")
plt.savefig("data/sunlight_score_preview.png", dpi=150)
print("Saved data/sunlight_score_preview.png")
plt.show()
