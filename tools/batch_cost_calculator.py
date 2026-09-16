# batch_cost_calculator.py
"""
Craft Brewery Batch Cost Calculator

Inspired by: https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py
Standalone CLI tool for calculating per-barrel costs and recommended selling prices.
"""

from dataclasses import dataclass
from typing import Optional


# ──────────────────────────────────────────────
# Ingredient / Input parameters
# ──────────────────────────────────────────────
@dataclass
class BatchInputs:
    """All cost inputs needed for a single batch."""
    grain_cost_per_lb: float          # $ per pound of grain
    hops_cost_per_oz: float           # $ per ounce of hops
    yeast_cost_per_unit: float        # $ per yeast unit (packet/vial)
    packaging_cost_per_unit: float    # $ per packaging unit (can/bottle/keg)
    grain_lbs: float                  # total pounds of grain used
    hops_oz: float                    # total ounces of hops used
    yeast_units: float                # total yeast units used
    packaging_units: float            # total packaging units produced
    barrel_count: float               # batch size in US beer barrels (31 gal)
    margin_pct: float = 30.0          # desired profit margin as percentage

    # ── derived constants (typical craft-brewery rules of thumb) ──
    GRAIN_LBS_PER_BARREL: float = 38.0       # lbs of grain per 31-gal bbl
    HOPS_OZ_PER_BARREL:   float = 3.5        # oz of hops per 31-gal bbl
    YEAST_UNITS_PER_BARREL: float = 2.0      # yeast units per 31-gal bbl
    PACKAGING_UNITS_PER_BARREL: float = 330  # 12-oz can/bottle count per bbl

    @classmethod
    def from_barrel_basis(cls, barrel_count: float,
                          grain_cost_per_lb: float = 3.50,
                          hops_cost_per_oz: float = 0.25,
                          yeast_cost_per_unit: float = 0.75,
                          packaging_cost_per_unit: float = 0.06,
                          margin_pct: float = 30.0) -> "BatchInputs":
        """Populate quantities using per-barrel norms × barrel_count."""
        return cls(
            grain_cost_per_lb=grain_cost_per_lb,
            hops_cost_per_oz=hops_cost_per_oz,
            yeast_cost_per_unit=yeast_cost_per_unit,
            packaging_cost_per_unit=packaging_cost_per_unit,
            grain_lbs=barrel_count * cls.GRAIN_LBS_PER_BARREL,
            hops_oz=barrel_count * cls.HOPS_OZ_PER_BARREL,
            yeast_units=barrel_count * cls.YEAST_UNITS_PER_BARREL,
            packaging_units=barrel_count * cls.PACKAGING_UNITS_PER_BARREL,
            barrel_count=barrel_count,
            margin_pct=margin_pct,
        )


# ──────────────────────────────────────────────
# Core calculations
# ──────────────────────────────────────────────
def compute_costs(inp: BatchInputs) -> dict:
    """Calculate ingredient costs, totals, and recommended sell price."""
    grain_cost     = inp.grain_lbs    * inp.grain_cost_per_lb
    hops_cost      = inp.hops_oz      * inp.hops_cost_per_oz
    yeast_cost     = inp.yeast_units  * inp.yeast_cost_per_unit
    packaging_cost = inp.packaging_units * inp.packaging_cost_per_unit

    total_cost     = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_barrel = total_cost / inp.barrel_count if inp.barrel_count else 0.0
    selling_price  = cost_per_barrel * (1 + inp.margin_pct / 100.0)

    return {
        "grain_cost":       grain_cost,
        "hops_cost":        hops_cost,
        "yeast_cost":       yeast_cost,
        "packaging_cost":   packaging_cost,
        "total_cost":       total_cost,
        "cost_per_barrel":  cost_per_barrel,
        "margin_pct":       inp.margin_pct,
        "selling_price":    round(selling_price, 2),
    }


# ──────────────────────────────────────────────
# Pretty-print report
# ──────────────────────────────────────────────
def print_report(inp: BatchInputs, res: dict) -> None:
    """Render a formatted cost report to stdout."""
    sep = "=" * 58
    print(f"\n{sep}")
    print(f"  CRAFT BREWERY BATCH COST CALCULATOR")
    print(f"{sep}")
    print(f"  Batch size      : {inp.barrel_count:>10.1f} US bbl")
    print(f"  Margin          : {inp.margin_pct:>10.1f}%")
    print(f"  {'─' * 52}")
    print(f"  Grain           : {inp.grain_lbs:>10.1f} lb  @ ${inp.grain_cost_per_lb:.2f}/lb  = ${res['grain_cost']:>8.2f}")
    print(f"  Hops            : {inp.hops_oz:>10.1f} oz  @ ${inp.hops_cost_per_oz:.2f}/oz  = ${res['hops_cost']:>8.2f}")
    print(f"  Yeast           : {inp.yeast_units:>10.1f} u   @ ${inp.yeast_cost_per_unit:.2f}/u   = ${res['yeast_cost']:>8.2f}")
    print(f"  Packaging       : {inp.packaging_units:>10.0f} u   @ ${inp.packaging_cost_per_unit:.2f}/u  = ${res['packaging_cost']:>8.2f}")
    print(f"  {'─' * 52}")
    print(f"  TOTAL COST      : ${res['total_cost']:>10.2f}")
    print(f"  COST / BARREL   : ${res['cost_per_barrel']:>10.2f}")
    print(f"  SELL / BARREL   : ${res['selling_price']:>10.2f}  (+{inp.margin_pct:.1f}% margin)")
    print(f"{sep}\n")


# ──────────────────────────────────────────────
# CLI / sample run
# ──────────────────────────────────────────────
def main():
    # ── Sample batch: 10 barrels ──
    sample = BatchInputs.from_barrel_basis(
        barrel_count=10.0,
        grain_cost_per_lb=3.00,
        hops_cost_per_oz=0.30,
        yeast_cost_per_unit=1.50,
        packaging_cost_per_unit=0.07,
        margin_pct=35.0,
    )
    results = compute_costs(sample)
    print_report(sample, results)

    # ── Assertion-based validation ──
    assert abs(results["grain_cost"] - 1140.00) < 0.01,   "Grain cost mismatch"
    assert abs(results["hops_cost"]  - 10.50)  < 0.01,    "Hops cost mismatch"
    assert abs(results["yeast_cost"] - 30.00)  < 0.01,    "Yeast cost mismatch"
    assert abs(results["packaging_cost"] - 231.00) < 0.01, "Packaging cost mismatch"
    assert abs(results["total_cost"] - 1411.50) < 0.01,   "Total cost mismatch"
    assert abs(results["cost_per_barrel"] - 141.15) < 0.01, "Cost/bbl mismatch"
    assert abs(results["selling_price"] - 190.55) < 0.10, "Selling price mismatch"
    print("✓ All assertions passed — calculator is working correctly.")


if __name__ == "__main__":
    main()
