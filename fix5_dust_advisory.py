import json

with open("data/sunlight_ice_dust_final.json") as f:
    final_output = json.load(f)

DUST_NOTE = "Advisory only -- not included in the final weighted ranking."

# --- Confirm dust_risk_score exists as its own top-level grid field ---
print("Top-level keys:", list(final_output.keys()))
print("dust_risk_score is separate grid field:", "dust_risk_score" in final_output)

# --- Grid-level advisory note ---
final_output["dust_risk_score_note"] = DUST_NOTE

# --- Per-site advisory note ---
for name, entry in final_output["named_sites"].items():
    entry["dust_risk_score_note"] = DUST_NOTE

with open("data/sunlight_ice_dust_final.json", "w") as f:
    json.dump(final_output, f)

print("\nGrid-level dust note added:", final_output["dust_risk_score_note"])
print("\nExample site entry (Nobile Rim):")
print(json.dumps(final_output["named_sites"]["Nobile Rim"], indent=2))
