"""
Craft Brewery Batch Cost Calculator
====================================
Calculates total cost and cost-per-barrel for a craft brewing batch,
then applies a configurable margin to recommend selling price.

Inspired by: https://github.com/tfrayner/beerfestdb
(Reference: CBF_beer_price_calculator.py)
"""


def calculate_batch_cost(
    grain_cost_per_lb: float,
    grain_lbs: float,
    hops_cost_per_oz: float,
    hops_oz: float,
    yeast_cost_per_unit: float,
    yeast_units: float,
    packaging_cost_per_unit: float,
    packaging_units: float,
    batch_size_barrels: float,
    margin_percent: float = 30.0
) -> dict:
    """
    Calculate total batch cost, cost-per-barrel, and recommended selling price.

    Args:
        grain_cost_per_lb: Cost of grain per pound ($/lb)
        grain_lbs: Total pounds of grain used
        hops_cost_per_oz: Cost of hops per ounce ($/oz)
        hops_oz: Total ounces of hops used
        yeast_cost_per_unit: Cost per yeast unit/packet ($/unit)
        yeast_units: Number of yeast units/packets
        packaging_cost_per_unit: Cost per packaging unit (bottle/can/keg) ($/unit)
        packaging_units: Total number of packaging units
        batch_size_barrels: Batch size in barrels
        margin_percent: Desired profit margin as percentage (default 30%)

    Returns:
        Dictionary with full cost breakdown and pricing recommendations
    """
    # Ingredient costs
    grain_total = grain_cost_per_lb * grain_lbs
    hops_total = hops_cost_per_oz * hops_oz
    yeast_total = yeast_cost_per_unit * yeast_units
    packaging_total = packaging_cost_per_unit * packaging_units

    # Total batch cost
    total_cost = grain_total + hops_total + yeast_total + packaging_total

    # Cost per barrel
    cost_per_barrel = total_cost / batch_size_barrels if batch_size_barrels > 0 else 0.0

    # Recommended selling price with margin
    selling_price_per_barrel = cost_per_barrel * (1 + margin_percent / 100.0)
    profit_per_barrel = selling_price_per_barrel - cost_per_barrel
    total_revenue = selling_price_per_barrel * batch_size_barrels
    total_profit = total_revenue - total_cost

    return {
        "ingredient_costs": {
            "grain": {
                "unit_cost": grain_cost_per_lb,
                "quantity": grain_lbs,
                "total": round(grain_total, 2),
                "unit": "$/lb",
            },
            "hops": {
                "unit_cost": hops_cost_per_oz,
                "quantity": hops_oz,
                "total": round(hops_total, 2),
                "unit": "$/oz",
            },
            "yeast": {
                "unit_cost": yeast_cost_per_unit,
                "quantity": yeast_units,
                "total": round(yeast_total, 2),
                "unit": "$/unit",
            },
            "packaging": {
                "unit_cost": packaging_cost_per_unit,
                "quantity": packaging_units,
                "total": round(packaging_total, 2),
                "unit": "$/unit",
            },
        },
        "total_batch_cost": round(total_cost, 2),
        "batch_size_barrels": batch_size_barrels,
        "cost_per_barrel": round(cost_per_barrel, 2),
        "margin_percent": margin_percent,
        "selling_price_per_barrel": round(selling_price_per_barrel, 2),
        "profit_per_barrel": round(profit_per_barrel, 2),
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
    }


def print_report(results: dict) -> None:
    """Print a formatted cost report to stdout."""
    print("=" * 60)
    print("  CRAFT BEER BATCH COST CALCULATOR")
    print("=" * 60)
    print()

    print("--- Ingredient Costs ---")
    for name, data in results["ingredient_costs"].items():
        print(
            f"  {name.capitalize():12s}: {data['unit_cost']:>8.2f}"
            f" {data['unit']:>5s} x {data['quantity']:>8.2f}"
            f" = ${data['total']:>10.2f}"
        )

    print()
    print(f"  {'Total Batch Cost:':>30s}  ${results['total_batch_cost']:>10.2f}")
    print(f"  {'Batch Size:':>30s}  {results['batch_size_barrels']:>8.2f} barrels")
    print(f"  {'Cost per Barrel:':>30s}  ${results['cost_per_barrel']:>10.2f}")
    print()
    print(f"  {'Margin:':>30s}  {results['margin_percent']:>7.1f}%")
    print(f"  {'Selling Price/Barrel:':>30s}  ${results['selling_price_per_barrel']:>10.2f}")
    print(f"  {'Profit/Barrel:':>30s}  ${results['profit_per_barrel']:>10.2f}")
    print()
    print(f"  {'Total Revenue:':>30s}  ${results['total_revenue']:>10.2f}")
    print(f"  {'Total Profit:':>30s}  ${results['total_profit']:>10.2f}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    # Sample batch: 5-barrel batch of an American Pale Ale
    print("Running sample batch...\n")

    sample = calculate_batch_cost(
        grain_cost_per_lb=1.50,       # 2-row malt at $1.50/lb
        grain_lbs=50.0,               # 50 lbs of grain
        hops_cost_per_oz=3.00,        # Cascade hops at $3.00/oz
        hops_oz=8.0,                  # 8 oz of hops
        yeast_cost_per_unit=10.00,    # Yeast packet at $10/unit
        yeast_units=2.0,              # 2 yeast packets (batch + starter)
        packaging_cost_per_unit=0.75, # Cans at $0.75 each
        packaging_units=480,          # 480 cans (24 x 20 count cases)
        batch_size_barrels=5.0,       # 5 barrels
        margin_percent=30.0,          # 30% margin
    )

    print_report(sample)

    # Validate key outputs
    assert sample["total_batch_cost"] > 0, "Total cost must be positive"
    assert sample["cost_per_barrel"] > 0, "Cost per barrel must be positive"
    assert (
        sample["selling_price_per_barrel"] > sample["cost_per_barrel"]
    ), "Selling price must exceed cost"
    assert sample["batch_size_barrels"] == 5.0, "Batch size mismatch"

    print("\nAll validations passed! Calculator is working correctly.")
