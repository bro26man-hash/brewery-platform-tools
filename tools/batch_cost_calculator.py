# batch_cost_calculator.py
# Craft Brewery Batch Cost Calculator
# Inspired by: tfrayner/beerfestdb — CBF_beer_price_calculator.py
# https://github.com/tfrayner/beerfestdb

"""
Batch Cost Calculator for Craft Breweries
==========================================
Calculates total batch cost, cost per barrel, and recommended
selling price per barrel based on ingredient costs and desired margin.

Reference logic inspired by:
  tfrayner/beerfestdb — tool_dashboard/CBF_beer_price_calculator.py
  https://github.com/tfrayner/beerfestdb
"""

# ── Constants ──────────────────────────────────────────────────────────────
# Standard conversion helpers
LB_PER_BARREL = 260          # approx. lbs of grain per barrel of wort (typical homebrew scale)
OZ_HOPS_PER_BARREL = 1.0      # oz hops per barrel (example rate; adjust per recipe)

# ── Ingredient Cost Inputs ─────────────────────────────────────────────────
def get_ingredient_costs():
    """Return a dict of ingredient unit costs."""
    return {
        "grain": 0.50,      # $/lb
        "hops":   8.00,     # $/oz
        "yeast":  1.50,     # $/unit (one packet/vial)
        "packaging": 0.75,  # $/unit (bottles, caps, keg, etc.)
    }

# ── Consumption Rates (per barrel) ─────────────────────────────────────────
def get_consumption_rates():
    """Return consumption rates per barrel."""
    return {
        "grain_lb_per_bbl": 10.0,   # lbs of grain per barrel
        "hops_oz_per_bbl":  1.0,    # oz of hops per barrel
        "yeast_units_per_bbl": 1.0, # yeast units per barrel
        "packaging_units_per_bbl": 100.0, # bottles per barrel (example)
    }

# ── Core Calculation ───────────────────────────────────────────────────────
def calculate_batch_cost(
    batch_size_bbl: float,
    ingredient_costs: dict,
    consumption_rates: dict,
    margin_pct: float = 30.0,
) -> dict:
    """
    Calculate total batch cost, cost per barrel, and recommended selling price.

    Parameters
    ----------
    batch_size_bbl : float
        Batch size in barrels.
    ingredient_costs : dict
        Unit costs for grain, hops, yeast, packaging.
    consumption_rates : dict
        Consumption rates per barrel for each ingredient.
    margin_pct : float
        Desired profit margin percentage (default 30%).

    Returns
    -------
    dict with keys:
        grain_cost_total, hops_cost_total, yeast_cost_total, packaging_cost_total,
        total_cost, cost_per_barrel, recommended_selling_price_per_bbl
    """
    grain_cost_total = ingredient_costs["grain"] * consumption_rates["grain_lb_per_bbl"] * batch_size_bbl
    hops_cost_total   = ingredient_costs["hops"]   * consumption_rates["hops_oz_per_bbl"]    * batch_size_bbl
    yeast_cost_total  = ingredient_costs["yeast"]  * consumption_rates["yeast_units_per_bbl"] * batch_size_bbl
    packaging_cost_total = ingredient_costs["packaging"] * consumption_rates["packaging_units_per_bbl"] * batch_size_bbl

    total_cost = grain_cost_total + hops_cost_total + yeast_cost_total + packaging_cost_total
    cost_per_barrel = total_cost / batch_size_bbl if batch_size_bbl > 0 else 0.0

    # Recommended selling price = cost per barrel × (1 + margin / 100)
    recommended_selling_price = cost_per_barrel * (1 + margin_pct / 100)

    return {
        "grain_cost_total": round(grain_cost_total, 2),
        "hops_cost_total": round(hops_cost_total, 2),
        "yeast_cost_total": round(yeast_cost_total, 2),
        "packaging_cost_total": round(packaging_cost_total, 2),
        "total_cost": round(total_cost, 2),
        "cost_per_barrel": round(cost_per_barrel, 2),
        "recommended_selling_price_per_bbl": round(recommended_selling_price, 2),
    }

# ── Sample Run ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 60)

    # Sample batch parameters
    sample_batch_size_bbl = 5.0       # 5 barrels
    sample_margin_pct = 35.0          # 35% margin

    costs = get_ingredient_costs()
    rates = get_consumption_rates()

    print(f"\n  Batch Size          : {sample_batch_size_bbl} barrels")
    print(f"  Desired Margin      : {sample_margin_pct}%")
    print(f"\n  Ingredient Unit Costs:")
    print(f"    Grain             : ${costs['grain']:.2f}/lb")
    print(f"    Hops              : ${costs['hops']:.2f}/oz")
    print(f"    Yeast             : ${costs['yeast']:.2f}/unit")
    print(f"    Packaging         : ${costs['packaging']:.2f}/unit")

    results = calculate_batch_cost(
        batch_size_bbl=sample_batch_size_bbl,
        ingredient_costs=costs,
        consumption_rates=rates,
        margin_pct=sample_margin_pct,
    )

    print(f"\n  ── Cost Breakdown ──────────────────────────")
    print(f"    Grain cost total      : ${results['grain_cost_total']:.2f}")
    print(f"    Hops cost total       : ${results['hops_cost_total']:.2f}")
    print(f"    Yeast cost total      : ${results['yeast_cost_total']:.2f}")
    print(f"    Packaging cost total  : ${results['packaging_cost_total']:.2f}")
    print(f"    ───────────────────────────────────────────")
    print(f"    TOTAL BATCH COST      : ${results['total_cost']:.2f}")
    print(f"    COST PER BARREL       : ${results['cost_per_barrel']:.2f}")
    print(f"    RECOMMENDED SELLING PRICE / BBL : ${results['recommended_selling_price_per_bbl']:.2f}")
    print("\n" + "=" * 60)
    print("  ✅ Calculation complete — no errors.")
    print("=" * 60)
