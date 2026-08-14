import numpy as np
from scipy import ndimage

data = np.load("data/illumination_400x400.npy")

# Compute local gradient magnitude (how sharply illumination changes
# from one 1km cell to its neighbors) using a Sobel-style edge filter.
grad_x = ndimage.sobel(data, axis=0)
grad_y = ndimage.sobel(data, axis=1)
gradient_magnitude = np.hypot(grad_x, grad_y)

# Normalize gradient magnitude to a 0-100 dust risk score
# (higher gradient = sharper lit/shadow boundary = higher risk)
max_grad = gradient_magnitude.max()
dust_risk_score = (gradient_magnitude / max_grad) * 100
dust_risk_score = np.clip(dust_risk_score, 0, 100).astype(np.float32)

print("Dust risk score shape:", dust_risk_score.shape)
print("Min:", dust_risk_score.min(), "Max:", dust_risk_score.max(), "Mean:", dust_risk_score.mean())

np.save("data/dust_risk_score_400x400.npy", dust_risk_score)
print("Saved data/dust_risk_score_400x400.npy")
