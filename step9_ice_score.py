import numpy as np

data = np.load("data/illumination_400x400.npy")

# Water-ice proxy score: near-total shadow -> high ice likelihood.
# Anything at or below a small threshold (2% illumination) is treated as
# a full cold trap (score 100); above that, ice likelihood falls off as
# illumination rises, hitting 0 once illumination reaches ~53% (our data max).
SHADOW_THRESHOLD_PCT = 2.0
MAX_ILLUM_PCT = data.max()  # ~53.3 in our resampled grid

ice_score = np.where(
    data <= SHADOW_THRESHOLD_PCT,
    100.0,
    100.0 * (1 - (data - SHADOW_THRESHOLD_PCT) / (MAX_ILLUM_PCT - SHADOW_THRESHOLD_PCT))
)
ice_score = np.clip(ice_score, 0, 100).astype(np.float32)

print("Ice score shape:", ice_score.shape)
print("Min:", ice_score.min(), "Max:", ice_score.max(), "Mean:", ice_score.mean())
print("Fraction of cells scoring 100 (full cold trap):", (ice_score == 100).mean())

np.save("data/ice_score_400x400.npy", ice_score)
print("Saved data/ice_score_400x400.npy")
