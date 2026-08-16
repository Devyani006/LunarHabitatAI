import json

with open("data/sunlight_ice_dust_final.json") as f:
    final_output = json.load(f)

final_output["named_sites"]["Malapert Massif"]["review_note"] = (
    "Coordinate (-84.9, 12.9) matches teammate's terrain file exactly, "
    "but corresponds to the IAU Gazetteer center of Malapert CRATER, not "
    "the Mons Malapert / Malapert Massif summit landing site (commonly "
    "cited near -86.0, 0.0). Resulting sunlight score here (~2.3%) is "
    "atypically low for a site labeled 'Massif' -- published sources "
    "describe the massif summit as 87-93% illuminated. Confirm with "
    "teammate whether crater or massif summit was intended before final handoff."
)

with open("data/sunlight_ice_dust_final.json", "w") as f:
    json.dump(final_output, f)

print("Added review_note to Malapert Massif entry.")
print(final_output["named_sites"]["Malapert Massif"])
