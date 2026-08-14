import numpy as np
import matplotlib.pyplot as plt

data = np.load("data/dust_risk_score_400x400.npy")

plt.figure(figsize=(7, 7))
plt.imshow(data, cmap="magma", vmin=0, vmax=100, extent=[-200, 200, -200, 200])
plt.colorbar(label="Dust/Electrostatic Risk Score (0-100)")
plt.title("Dust Risk (Illumination Boundary Proxy) — South Pole")
plt.xlabel("km from pole (X)")
plt.ylabel("km from pole (Y)")
plt.savefig("data/dust_risk_preview.png", dpi=150)
print("Saved data/dust_risk_preview.png")
plt.show()
