# batch_cost_calculator.py
# Craft Brewery Batch Cost Calculator
# Inspired by: tfrayner/beerfestdb — CBF_beer_price_calculator.py
# (https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py)
#
# The original reference calculates beer sale prices based on ABV-based pricing
# vs. cask cost (whichever is greater), then applies rounding. This script
# adapts that cost-vs-price philosophy for home/craft brewery batch costing:
# ingredient cost inputs → total batch cost → cost per barrel → margin → selling price.

# ── Default constants (mirroring the reference's default_abv_coefficient / default_abv_constant pattern) ──
DEFAULT_MARGIN_PERCENT = 30  # default markup, analogous to the reference code's default coefficients


def calculate_batch_cost(
    grain_cost_per_lb: float,   # $/lb
    hops_cost_per_oz: float,    # $/oz
    yeast_cost_per_unit: float, # $/unit
    packaging_cost_per_unit: float, # $/unit (bottles, kegs, caps, etc.)
    grain_lbs: float,           # lbs of grain in the batch
    hops_oz: float,             # oz of hops in the batch
    yeast_units: float,         # units of yeast (e.g., dry yeast packets / liquid starters)
    packaging_units: float,     # units of packaging (bottles, kegs, etc.)
    batch_barrels: float,       # batch size in barrels (1 bbl = 31 US gallons)
    margin_percent: float = DEFAULT_MARGIN_PERCENT,
) -> dict:
    """
    Calculate total batch cost, cost per barrel, and recommended selling price.

    Returns a dict with all intermediate and final values.
    """
    # ── Ingredient cost breakdown ──
    grain_cost   = grain_cost_per_lb  * grain_lbs
    hops_cost    = hops_cost_per_oz    * hops_oz
    yeast_cost   = yeast_cost_per_unit * yeast_units
    packaging_cost = packaging_cost_per_unit * packaging_units

    total_ingredient_cost = grain_cost + hops_cost + yeast_cost + packaging_cost

    # ── Per-barrel metrics ──
    cost_per_barrel = total_ingredient_cost / batch_barrels if batch_barrels > 0 else 0

    # ── Apply margin (same "whichever is greater" philosophy as the reference:
    #    the selling price must cover cost AND desired margin) ──
    margin_multiplier = 1 + (margin_percent / 100)
    recommended_price_per_barrel = cost_per_barrel * margin_multiplier

    return {
        "grain_cost":          grain_cost,
        "hops_cost":           hops_cost,
        "yeast_cost":          yeast_cost,
        "packaging_cost":      packaging_cost,
        "total_ingredient_cost": total_ingredient_cost,
        "batch_barrels":       batch_barrels,
        "cost_per_barrel":     cost_per_barrel,
        "margin_percent":      margin_percent,
        "recommended_price_per_barrel": recommended_price_per_barrel,
    }


def print_recipe_summary(results: dict) -> None:
    """Pretty-print the calculation results."""
    print("=" * 60)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 60)
    print(f"\n{'Ingredient Cost Breakdown':}")
    print(f"  Grain:              ${results['grain_cost']:>10,.2f}")
    print(f"  Hops:               ${results['hops_cost']:>10,.2f}")
    print(f"  Yeast:              ${results['yeast_cost']:>10,.2f}")
    print(f"  Packaging:          ${results['packaging_cost']:>10,.2f}")
    print(f"  {'─' * 42}")
    print(f"  TOTAL BATCH COST:   ${results['total_ingredient_cost']:>10,.2f}")
    print(f"\n  Batch Size:         {results['batch_barrels']:>10.2f} bbl")
    print(f"  Cost / Barrel:      ${results['cost_per_barrel']:>10,.2f}")
    print(f"  Margin:             {results['margin_percent']:>10.1f}%")
    print(f"  {'─' * 42}")
    print(f"  ★ RECOMMENDED SELLING PRICE / BARREL: ${results['recommended_price_per_barrel']:>10,.2f}")
    print(f"\n{'=' * 60}")


# ── Sample batch (run as a self-test) ──
if __name__ == "__main__":
    sample = calculate_batch_cost(
        grain_cost_per_lb     = 1.50,   # $/lb
        hops_cost_per_oz      = 8.00,   # $/oz
        yeast_cost_per_unit   = 5.00,   # $/unit
        packaging_cost_per_unit = 0.75,  # $/unit (bottles/caps)
        grain_lbs             = 100,    # lbs
        hops_oz               = 8,      # oz
        yeast_units           = 2,      # units
        packaging_units       = 120,    # bottles
        batch_barrels         = 5,      # 5 bbl batch
        margin_percent        = 30,     # 30% margin
    )
    print_recipe_summary(sample)
