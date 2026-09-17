# batch_cost_calculator.py
#
# Craft Brewery Batch Cost Calculator
# -----------------------------------------------------------------------------
# Inspired by tfrayner/beerfestdb's CBF_beer_price_calculator.py which derives
# a sale price from the greater of ABV-based value or ingredient cost.  This
# standalone script adapts that concept for US craftbrewery units
# (barrels, pounds, ounces) so a brewer can estimate the total cost of a
# production batch, the cost per barrel, and a recommended selling price
# that includes a configurable margin.
#
# Reference repository: https://github.com/tfrayner/beerfestdb
# Reference file:        tool_dashboard/CBF_beer_price_calculator.py
# -----------------------------------------------------------------------------

from dataclasses import dataclass, field
from typing import Optional

# --- US Beer Volume Constants -------------------------------------------------
# 1 US barrel (bbl) = 31 US gallons = 117.3478 litres
BARREL_TO_GALLONS = 31.0
BARREL_TO_LITRES  = 117.3478


@dataclass
class BatchCostCalculator:
    """
    Calculates the total cost, cost-per-barrel, and recommended selling
    price for a single production batch of beer.

    Pricing philosophy (inspired by CBF_beer_price_calculator.py):
        The reference tool sets the sale price to the *greater* of an
        ABV-based value and a cost-based value, then rounds up.  This
        script simplifies that to a cost-plus-margin model, which is the
        most common approach for craft breweries that want to guarantee
        coverage of expenses.
    """

    # -- Ingredient unit costs ------------------------------------------------
    grain_cost_per_lb:   float = 1.50    # $ per pound of malt/grain
    hops_cost_per_oz:    float = 8.00    # $ per ounce of hops
    yeast_cost_per_unit: float = 12.00   # $ per yeast unit (1 ~ 10-25B cells)
    packaging_cost_per_unit: float = 0.75  # $ per keg / bottle / can

    # -- Per-batch ingredient usage -------------------------------------------
    grain_lbs_per_batch:        float = 20.0   # lbs of grain per batch
    hops_oz_per_batch:          float = 1.0    # oz of hops per batch
    yeast_units_per_batch:      float = 1.0    # yeast units per batch
    packaging_units_per_batch:  float = 50.0   # kegs/bottles/cans per batch

    # -- Batch parameters -----------------------------------------------------
    batch_size_barrels: float = 0.65    # batch size in US barrels (approx 20 gal)

    # -- Pricing --------------------------------------------------------------
    margin_percentage: float = 30.0     # markup on cost expressed as a percent

    # -- Computed (filled by calculate) ---------------------------------------
    total_cost:        float = 0.0
    cost_per_barrel:   float = 0.0
    selling_price:     float = 0.0

    def calculate(self) -> dict:
        """Run all calculations and return a summary dict."""

        # ---- Ingredient costs ------------------------------------------------
        grain_cost       = self.grain_cost_per_lb      * self.grain_lbs_per_batch
        hops_cost        = self.hops_cost_per_oz       * self.hops_oz_per_batch
        yeast_cost       = self.yeast_cost_per_unit    * self.yeast_units_per_batch
        packaging_cost   = self.packaging_cost_per_unit * self.packaging_units_per_batch

        total_ingredient_cost = grain_cost + hops_cost + yeast_cost + packaging_cost

        # ---- Per-barrel metrics ----------------------------------------------
        total_cost   = total_ingredient_cost
        cost_per_bbl = total_cost / self.batch_size_barrels if self.batch_size_barrels > 0 else 0.0

        # ---- Sale price with margin ------------------------------------------
        selling_price = cost_per_bbl * (1.0 + self.margin_percentage / 100.0)

        # Store results
        self.total_cost      = total_cost
        self.cost_per_barrel = cost_per_bbl
        self.selling_price   = selling_price

        return {
            "grain_cost":             grain_cost,
            "hops_cost":              hops_cost,
            "yeast_cost":             yeast_cost,
            "packaging_cost":         packaging_cost,
            "total_ingredient_cost":  total_ingredient_cost,
            "total_cost":             total_cost,
            "batch_size_barrels":     self.batch_size_barrels,
            "cost_per_barrel":        cost_per_bbl,
            "margin_percentage":      self.margin_percentage,
            "selling_price_per_barrel": selling_price,
            "batch_volume_gallons":   self.batch_size_barrels * BARREL_TO_GALLONS,
            "batch_volume_litres":    round(self.batch_size_barrels * BARREL_TO_LITRES, 2),
        }

    def display_report(self) -> None:
        """Print a nicely formatted batch cost report."""
        r = self.calculate()
        separator = "-" * 58

        print(separator)
        print("  CRAFT BREWERY BATCH COST REPORT")
        print(separator)
        print(f"  Batch size          : {r['batch_size_barrels']:.2f} bbl  "
              f"({r['batch_volume_gallons']:.1f} gal / {r['batch_volume_litres']} L)")
        print()
        print("  INGREDIENT COSTS (per batch)")
        print(f"    Grain             : {r['grain_cost']:>8.2f}  "
              f"({self.grain_lbs_per_batch} lbs x ${self.grain_cost_per_lb:.2f}/lb)")
        print(f"    Hops              : {r['hops_cost']:>8.2f}  "
              f"({self.hops_oz_per_batch} oz  x ${self.hops_cost_per_oz:.2f}/oz)")
        print(f"    Yeast             : {r['yeast_cost']:>8.2f}  "
              f"({self.yeast_units_per_batch} unit x ${self.yeast_cost_per_unit:.2f}/unit)")
        print(f"    Packaging         : {r['packaging_cost']:>8.2f}  "
              f"({self.packaging_units_per_batch} units x ${self.packaging_cost_per_unit:.2f}/unit)")
        print(f"    ------------------------------" )
        print(f"    Total Ingredient  : ${r['total_ingredient_cost']:>8.2f}")
        print()
        print("  COST SUMMARY")
        print(f"    Total Batch Cost  : ${r['total_cost']:>8.2f}")
        print(f"    Cost / Barrel     : ${r['cost_per_barrel']:>8.2f}")
        print(f"    Margin            : {r['margin_percentage']:.1f}%")
        print()
        print("  RECOMMENDED SELLING PRICE")
        print(f"    Price / Barrel    : ${r['selling_price_per_barrel']:>8.2f}")
        price_per_gallon = r['selling_price_per_barrel'] / BARREL_TO_GALLONS
        print(f"    Price / Gallon    : ${price_per_gallon:>8.2f}")
        print(separator)


# =============================================================================
#  SAMPLE RUN
# =============================================================================
if __name__ == "__main__":
    print("\n>>> Sample Batch Calculation\n")

    # --- Guided Sample: a 0.65 bbl (approx 20 gallon) homebrew / pilot batch ---
    calc = BatchCostCalculator(
        grain_cost_per_lb     = 1.80,
        hops_cost_per_oz      = 9.50,
        yeast_cost_per_unit   = 15.00,
        packaging_cost_per_unit = 0.80,
        grain_lbs_per_batch   = 22.0,
        hops_oz_per_batch     = 1.5,
        yeast_units_per_batch = 1.0,
        packaging_units_per_batch = 50.0,
        batch_size_barrels    = 0.65,
        margin_percentage     = 30.0,
    )

    calc.display_report()

    # --- Second sample: a larger 10-bbl production batch -----------------------
    print("\n\n>>> Larger Production Batch (10 bbl)\n")

    prod = BatchCostCalculator(
        grain_cost_per_lb     = 1.20,   # bulk grain discount
        hops_cost_per_oz      = 7.00,
        yeast_cost_per_unit   = 10.00,
        packaging_cost_per_unit = 0.40, # bottled in cases
        grain_lbs_per_batch   = 330.0,  # approx 105 kg for 10 bbl
        hops_oz_per_batch     = 25.0,
        yeast_units_per_batch = 1.0,
        packaging_units_per_batch = 120.0,  # 120 12-oz cans approx 10 bbl
        batch_size_barrels    = 10.0,
        margin_percentage     = 25.0,
    )

    prod.display_report()

    print("\n\xealculator executed successfully — no errors.\n")
