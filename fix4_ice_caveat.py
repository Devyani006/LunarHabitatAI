import json

with open("data/sunlight_ice_dust_final.json") as f:
    final_output = json.load(f)

CAVEAT = ("Based on permanent shadow persistence -- indicates conditions "
          "favorable for ice preservation, not a confirmed deposit.")

# --- Grid-level note ---
final_output["ice_score_caveat"] = CAVEAT

# --- Per-site note ---
for name, entry in final_output["named_sites"].items():
    entry["ice_score_caveat"] = CAVEAT

with open("data/sunlight_ice_dust_final.json", "w") as f:
    json.dump(final_output, f)

print("Grid-level caveat added:", final_output["ice_score_caveat"])
print("\nExample site entry (Shackleton Crater Rim):")
print(json.dumps(final_output["named_sites"]["Shackleton Crater Rim"], indent=2))
