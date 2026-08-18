"""
scoring_engine.py — Lunar Habitat Site Scoring Engine
======================================================
Weights default: AHP-derived (Analytic Hierarchy Process, Saaty scale).
Override: pass a custom `weights` dict to score_sites() — slider-override compatible.

Usage
-----
    # Default AHP weights
    python scoring_engine.py

    # From another module
    from scoring_engine import score_sites, get_weight_metadata

    results = score_sites(named_sites)                  # AHP defaults
    results = score_sites(named_sites, weights={...})   # slider override
    meta    = get_weight_metadata()                     # provenance string for UI
"""

import json
import os

# ---------------------------------------------------------------------------
# Paths (relative to this file's location)
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_AHP_CONFIG_PATH  = os.path.join(_HERE, "ahp_config.json")
_DATA_PATH        = os.path.join(_HERE, "sunlight_ice_dust_final.json")


# ---------------------------------------------------------------------------
# Load AHP configuration
# ---------------------------------------------------------------------------
with open(_AHP_CONFIG_PATH) as _f:
    _AHP_CFG = json.load(_f)

# AHP default weights — keyed by factor id, value is 0-1 float
AHP_WEIGHTS: dict[str, float] = {
    factor["id"]: factor["ahp_weight"]
    for factor in _AHP_CFG["factors"]
}

# Human-readable labels (id -> label)
FACTOR_LABELS: dict[str, str] = {
    factor["id"]: factor["label"]
    for factor in _AHP_CFG["factors"]
}

# Ordered list of factor ids (preserves AHP rank order)
FACTOR_ORDER: list[str] = [f["id"] for f in _AHP_CFG["factors"]]


# ---------------------------------------------------------------------------
# Factor score computation  (maps data layers → per-factor 0-100 scores)
# ---------------------------------------------------------------------------

def _compute_factor_scores(site_entry: dict) -> dict[str, float]:
    """
    Derive a 0–100 score for each AHP factor from a named-site entry.

    The entry is expected to contain:
        best_score_within_20km_search:
            sunlight_score  (0-100)
            ice_score       (0-100)
            dust_risk_score (0-100, higher = more dust = worse)
    """
    # Prefer the 'best within 20km' values (rim-search corrected).
    # Fall back to exact-coordinate values if the key is absent.
    if "best_score_within_20km_search" in site_entry:
        raw = site_entry["best_score_within_20km_search"]
    elif "score_at_exact_coordinate" in site_entry:
        raw = site_entry["score_at_exact_coordinate"]
    else:
        # Legacy format (step11 era — flat keys)
        raw = site_entry

    sunlight  = float(raw.get("sunlight_score",   0.0))
    ice       = float(raw.get("ice_score",         0.0))
    dust_risk = float(raw.get("dust_risk_score",   0.0))

    safety           = max(0.0, min(100.0, 100.0 - dust_risk))  # inverse of dust
    water_ice        = ice
    sunlight_score   = sunlight
    resources        = (ice + sunlight) / 2.0                   # proxy
    expansion        = 50.0                                      # neutral placeholder
    scientific_value = (sunlight + ice + dust_risk) / 3.0       # proxy: avg all layers

    return {
        "safety":          round(safety,          2),
        "water_ice":       round(water_ice,        2),
        "sunlight":        round(sunlight_score,   2),
        "resources":       round(resources,        2),
        "expansion":       round(expansion,        2),
        "scientific_value":round(scientific_value, 2),
    }


# ---------------------------------------------------------------------------
# Weight normalisation (safety net for slider rounding errors)
# ---------------------------------------------------------------------------

def _normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    """Ensure weights sum to exactly 1.0. Raises ValueError if any weight < 0."""
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("Weights must sum to a positive number.")
    for k, v in weights.items():
        if v < 0:
            raise ValueError(f"Weight for '{k}' is negative ({v}). All weights must be >= 0.")
    return {k: v / total for k, v in weights.items()}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_sites(
    named_sites: dict,
    weights: dict[str, float] | None = None,
) -> list[dict]:
    """
    Score and rank candidate lunar habitat sites.

    Parameters
    ----------
    named_sites : dict
        The ``named_sites`` sub-dict from ``sunlight_ice_dust_final.json``.
    weights : dict or None
        Factor weights keyed by factor id (e.g. ``{"safety": 0.5, ...}``).
        If None, AHP-derived defaults are used.
        Weights do NOT need to sum to 1 — they are normalised automatically.

    Returns
    -------
    list[dict]
        Sites sorted by composite score (descending). Each entry contains:
            name            : site name
            composite_score : weighted sum 0–100
            rank            : 1-based rank
            factor_scores   : raw 0–100 score per factor (before weighting)
            factor_weighted : weighted contribution per factor
            weights_used    : the normalised weights that were applied
            weight_source   : "AHP_DEFAULT" or "SLIDER_OVERRIDE"
    """
    if weights is None:
        w = _normalize_weights(AHP_WEIGHTS.copy())
        weight_source = "AHP_DEFAULT"
    else:
        # Validate that all factor keys are recognised
        unknown = set(weights.keys()) - set(AHP_WEIGHTS.keys())
        if unknown:
            raise ValueError(
                f"Unknown factor id(s) in weights: {unknown}. "
                f"Valid ids: {list(AHP_WEIGHTS.keys())}"
            )
        # Fill any missing factors with 0 so the engine doesn't crash
        full_weights = {fid: 0.0 for fid in AHP_WEIGHTS}
        full_weights.update(weights)
        w = _normalize_weights(full_weights)
        weight_source = "SLIDER_OVERRIDE"

    results = []
    for name, entry in named_sites.items():
        if "error" in entry:
            results.append({
                "name": name,
                "composite_score": None,
                "rank": None,
                "error": entry["error"],
                "weights_used": w,
                "weight_source": weight_source,
            })
            continue

        factor_scores = _compute_factor_scores(entry)

        # Weighted sum
        composite = sum(
            w.get(fid, 0.0) * factor_scores[fid]
            for fid in FACTOR_ORDER
        )

        factor_weighted = {
            fid: round(w.get(fid, 0.0) * factor_scores[fid], 3)
            for fid in FACTOR_ORDER
        }

        results.append({
            "name":             name,
            "composite_score":  round(composite, 2),
            "factor_scores":    factor_scores,
            "factor_weighted":  factor_weighted,
            "weights_used":     {fid: round(v, 4) for fid, v in w.items()},
            "weight_source":    weight_source,
            "lat":              entry.get("lat"),
            "lon":              entry.get("lon"),
        })

    # Sort by composite score descending; error sites go to the end
    results.sort(
        key=lambda r: r["composite_score"] if r["composite_score"] is not None else -1,
        reverse=True,
    )
    for i, r in enumerate(results):
        if r.get("composite_score") is not None:
            r["rank"] = i + 1

    return results


def get_weight_metadata() -> dict:
    """
    Return AHP provenance information for frontend display.

    Returns
    -------
    dict with keys:
        display_note    : human-readable string suitable for a UI banner
        method          : full method description
        consistency_ratio : CR float
        is_consistent   : bool
        weights         : {label -> pct_string} e.g. {"Safety": "39.66%"}
        ahp_config_path : absolute path to ahp_config.json
    """
    cr_info = _AHP_CFG["ahp_consistency"]
    weights_display = {
        factor["label"]: f"{factor['ahp_weight_pct']:.2f}%"
        for factor in _AHP_CFG["factors"]
    }
    return {
        "display_note":       _AHP_CFG["display_note"],
        "method":             _AHP_CFG["method"],
        "consistency_ratio":  cr_info["consistency_ratio"],
        "lambda_max":         cr_info["lambda_max"],
        "is_consistent":      cr_info["is_consistent"],
        "threshold":          cr_info["threshold"],
        "weights":            weights_display,
        "ahp_config_path":    _AHP_CONFIG_PATH,
    }


# ---------------------------------------------------------------------------
# Self-test / CLI demo
# ---------------------------------------------------------------------------

def _run_selftest():
    print("=" * 65)
    print("  Lunar Habitat Scoring Engine — Self-Test")
    print("=" * 65)

    # --- Load data ---
    with open(_DATA_PATH) as f:
        data = json.load(f)
    named_sites = data["named_sites"]

    # ── Test 1: AHP default weights ─────────────────────────────────
    print("\n[ TEST 1 ]  AHP Default Weights\n")
    meta = get_weight_metadata()
    print(f"  {meta['display_note']}\n")
    print(f"  {'Factor':<20}  {'AHP Weight':>10}")
    print(f"  {'-'*20}  {'-'*10}")
    for label, pct in meta["weights"].items():
        print(f"  {label:<20}  {pct:>10}")

    results_ahp = score_sites(named_sites)
    print(f"\n  {'Rank':<5} {'Site':<28} {'Score':>7}  {'Source'}")
    print(f"  {'-'*5} {'-'*28} {'-'*7}  {'-'*14}")
    for r in results_ahp:
        if r["composite_score"] is not None:
            print(f"  #{r['rank']:<4} {r['name']:<28} {r['composite_score']:>6.2f}   {r['weight_source']}")
        else:
            print(f"  #ERR  {r['name']:<28} {'N/A':>6}   {r.get('error','')}")

    # ── Test 2: Slider override (equal weights) ──────────────────────
    print("\n[ TEST 2 ]  Slider Override — Equal Weights (16.67% each)\n")
    equal_weights = {fid: 1.0 for fid in AHP_WEIGHTS}
    results_eq = score_sites(named_sites, weights=equal_weights)
    print(f"  {'Rank':<5} {'Site':<28} {'Score':>7}  {'Source'}")
    print(f"  {'-'*5} {'-'*28} {'-'*7}  {'-'*14}")
    for r in results_eq:
        if r["composite_score"] is not None:
            print(f"  #{r['rank']:<4} {r['name']:<28} {r['composite_score']:>6.2f}   {r['weight_source']}")
        else:
            print(f"  #ERR  {r['name']:<28} {'N/A':>6}   {r.get('error','')}")

    # ── Test 3: Weights sum to 1.0 ───────────────────────────────────
    print("\n[ TEST 3 ]  Normalisation check\n")
    normalised = results_ahp[0]["weights_used"]
    total = sum(normalised.values())
    status = "PASS" if abs(total - 1.0) < 1e-9 else "FAIL"
    print(f"  Weights sum: {total:.10f}  [{status}]")

    print("\n" + "=" * 65)
    print("  Self-test complete.")
    print("=" * 65)


if __name__ == "__main__":
    _run_selftest()
