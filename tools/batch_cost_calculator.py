"""
Craft Brewery Batch Cost Calculator
====================================
Inspired by: tfrayner/beerfestdb — tool_dashboard/CBF_beer_price_calculator.py
https://github.com/tfrayner/beerfestdb

This script calculates the total cost of a brewing batch, the cost per barrel,
and the recommended selling price per barrel after applying a configurable margin.

Inputs:
  - Grain price       ($/lb)
  - Hops price        ($/oz)
  - Yeast price       ($/unit)
  - Packaging price   ($/unit)
  - Batch size        (barrels)
  - Margin percentage (%)

Outputs:
  - Total batch cost ($)
  - Cost per barrel ($)
  - Recommended selling price per barrel ($)
"""


def calculate_batch_cost(
    grain_price_per_lb: float,
    grain_lbs: float,
    hops_price_per_oz: float,
    hops_oz: float,
    yeast_price_per_unit: float,
    yeast_units: float,
    packaging_price_per_unit: float,
    packaging_units: float,
    batch_size_barrels: float,
    margin_percent: float,
) -> dict:
    """
    Calculate total cost, cost per barrel, and recommended selling price.

    Returns a dict with keys:
        total_cost, cost_per_barrel, recommended_price_per_barrel
    """
    # --- Ingredient cost breakdown ---
    grain_cost = grain_price_per_lb * grain_lbs
    hops_cost = hops_price_per_oz * hops_oz
    yeast_cost = yeast_price_per_unit * yeast_units
    packaging_cost = packaging_price_per_unit * packaging_units

    # --- Totals ---
    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_barrel = total_cost / batch_size_barrels if batch_size_barrels > 0 else 0

    # --- Recommended selling price with margin ---
    recommended_price_per_barrel = cost_per_barrel * (1 + margin_percent / 100)

    return {
        "grain_cost": grain_cost,
        "hops_cost": hops_cost,
        "yeast_cost": yeast_cost,
        "packaging_cost": packaging_cost,
        "total_cost": total_cost,
        "cost_per_barrel": cost_per_barrel,
        "recommended_price_per_barrel": recommended_price_per_barrel,
    }


def main():
    # ================================================================
    # SAMPLE BATCH — substitute these values or call calculate_batch_cost
    # directly with your own parameters.
    # ================================================================
    grain_price_per_lb = 0.80    # $/lb
    grain_lbs = 200.0   # lbs for this batch
    hops_price_per_oz = 12.50   # $/oz
    hops_oz = 8.0     # oz
    yeast_price_per_unit = 5.00    # $/unit ( one package )
    yeast_units = 4.0     # units
    packaging_price_per_unit = 3.00  # $/unit ( bottles / cans )
    packaging_units = 120.0   # units
    batch_size_barrels = 2.0     # barrels
    margin_percent = 30.0    # 30% margin

    print("=" * 60)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 60)
    print(f"\n  Batch size:        {batch_size_barrels} barrels")
    print(f"  Margin:            {margin_percent}%")
    print("-" * 60)

    results = calculate_batch_cost(
        grain_price_per_lb, grain_lbs,
        hops_price_per_oz, hops_oz,
        yeast_price_per_unit, yeast_units,
        packaging_price_per_unit, packaging_units,
        batch_size_barrels, margin_percent,
    )

    print("\n  --- Ingredient Cost Breakdown ---")
    print(f"  Grain:        ${results['grain_cost']:.2f}  ({grain_lbs} lbs x ${grain_price_per_lb:.2f}/lb)")
    print(f"  Hops:         ${results['hops_cost']:.2f}  ({hops_oz} oz x ${hops_price_per_oz:.2f}/oz)")
    print(f"  Yeast:        ${results['yeast_cost']:.2f}  ({yeast_units} units x ${yeast_price_per_unit:.2f}/unit)")
    print(f"  Packaging:    ${results['packaging_cost']:.2f}  ({packaging_units} units x ${packaging_price_per_unit:.2f}/unit)")
    print("-" * 60)
    print(f"\n  TOTAL BATCH COST:        ${results['total_cost']:.2f}")
    print(f"  COST PER BARREL:         ${results['cost_per_barrel']:.2f}")
    print(f"  RECOMMENDED SELLING PRICE (per barrel): ${results['recommended_price_per_barrel']:.2f}")
    print("\n" + "=" * 60)
    print("  Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
