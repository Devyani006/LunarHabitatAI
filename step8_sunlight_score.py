import numpy as np

data = np.load("data/illumination_400x400.npy")

# Sunlight-availability score: illumination % maps directly to 0-100 score
# (higher illumination = more usable solar power = better score)
sunlight_score = np.clip(data, 0, 100).astype(np.float32)

print("Sunlight score shape:", sunlight_score.shape)
print("Min:", sunlight_score.min(), "Max:", sunlight_score.max(), "Mean:", sunlight_score.mean())

np.save("data/sunlight_score_400x400.npy", sunlight_score)
print("Saved data/sunlight_score_400x400.npy")
