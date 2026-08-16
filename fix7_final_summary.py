import json
import numpy as np

with open("data/sunlight_ice_dust_final.json") as f:
    final_output = json.load(f)

print("=== FINAL FILE SUMMARY ===\n")
print("Top-level keys:", list(final_output.keys()))
print("Grid shape:", final_output["grid_meta"]["shape"])
print("Number of named sites:", len(final_output["named_sites"]))

for layer_name in ["sunlight_score", "ice_score", "dust_risk_score"]:
    arr = np.array(final_output[layer_name])
    print(f"\n{layer_name}:")
    print(f"  Min: {arr.min():.1f}  Max: {arr.max():.1f}  Mean: {arr.mean():.1f}")

print("\nice_score_caveat:", final_output["ice_score_caveat"])
print("dust_risk_score_note:", final_output["dust_risk_score_note"])

print("\n=== Malapert Massif entry (for review) ===")
print(json.dumps(final_output["named_sites"]["Malapert Massif"], indent=2))

print("\n=== All named site sunlight scores (best within 20km) ===")
for name, entry in final_output["named_sites"].items():
    best = entry["best_score_within_20km_search"]
    sunlight_val = best["sunlight_score"]
    print("  " + name + ": " + str(sunlight_val) + "%")
