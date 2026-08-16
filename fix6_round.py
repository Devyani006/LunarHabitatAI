import json

with open("data/sunlight_ice_dust_final.json") as f:
    final_output = json.load(f)

def round_grid(grid):
    return [[round(v, 1) for v in row] for row in grid]

# --- Round the three grid layers ---
final_output["sunlight_score"] = round_grid(final_output["sunlight_score"])
final_output["ice_score"] = round_grid(final_output["ice_score"])
final_output["dust_risk_score"] = round_grid(final_output["dust_risk_score"])

# --- Round named_sites scores (leave lat/lon/row/col untouched) ---
score_fields = {"sunlight_score", "ice_score", "dust_risk_score"}

for name, entry in final_output["named_sites"].items():
    for sub_key in ["score_at_exact_coordinate", "best_score_within_20km_search"]:
        sub = entry[sub_key]
        for field in score_fields:
            if field in sub:
                sub[field] = round(sub[field], 1)

with open("data/sunlight_ice_dust_final.json", "w") as f:
    json.dump(final_output, f)

print("Rounded all scores to 1 decimal place.")
print("\nExample site entry (Nobile Rim) after rounding:")
print(json.dumps(final_output["named_sites"]["Nobile Rim"], indent=2))
print("\nSample grid values (sunlight_score[200][200:205]):", final_output["sunlight_score"][200][200:205])
