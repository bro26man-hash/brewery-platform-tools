#!/usr/bin/env python3
"""
batch_cost_calculator.py
=========================
Craft Brewery Batch Cost Calculator

Inspired by: tfrayner/beerfestdb - CBF_beer_price_calculator.py
(https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py)

This script calculates the total cost of brewing a batch of beer,
the cost per barrel, and the recommended selling price per barrel
based on a configurable margin percentage.

Inputs:
    - Grain cost ($/lb)
    - Hops cost ($/oz)
    - Yeast cost ($/unit)
    - Packaging cost ($/unit)
    - Batch size (barrels)
    - Margin (%)

Outputs:
    - Total ingredient cost
    - Cost per barrel
    - Recommended selling price per barrel
"""

from dataclasses import dataclass, field
from typing import Optional
import json
import sys


@dataclass
class BrewCostInputs:
    """Ingredient and batch parameters for cost calculation."""
    grain_cost_per_lb: float       # $/lb
    hops_cost_per_oz: float        # $/oz
    yeast_cost_per_unit: float     # $/unit
    packaging_cost_per_unit: float # $/unit
    batch_size_barrels: float      # barrels (1 barrel = 31 gallons)
    grain_lbs_per_barrel: float = 60.0   # typical grain usage per barrel
    hops_oz_per_barrel: float = 1.0     # typical hops usage per barrel
    yeast_units_per_barrel: float = 1.0 # typical yeast usage per barrel
    packaging_units_per_barrel: float = 31.0  # 1 unit per gallon (31 gal/barrel)
    margin_percent: float = 30.0   # markup percentage on cost


class BatchCostCalculator:
    """
    Calculates batch costs and recommended selling prices for a craft brewery.

    Methodology (inspired by beer price calculators that use cost-based pricing):
      1. Compute total ingredient cost from per-unit rates and batch size.
      2. Divide by batch size to get cost per barrel.
      3. Apply margin to derive the recommended selling price per barrel.
    """

    def __init__(self, inputs: BrewCostInputs):
        self.inputs = inputs

    def compute_total_grain_cost(self) -> float:
        """Total grain cost = grain_price_per_lb * lbs_per_barrel * batch_size."""
        return (
            self.inputs.grain_cost_per_lb
            * self.inputs.grain_lbs_per_barrel
            * self.inputs.batch_size_barrels
        )

    def compute_total_hops_cost(self) -> float:
        """Total hops cost = hops_price_per_oz * oz_per_barrel * batch_size."""
        return (
            self.inputs.hops_cost_per_oz
            * self.inputs.hops_oz_per_barrel
            * self.inputs.batch_size_barrels
        )

    def compute_total_yeast_cost(self) -> float:
        """Total yeast cost = yeast_price_per_unit * units_per_barrel * batch_size."""
        return (
            self.inputs.yeast_cost_per_unit
            * self.inputs.yeast_units_per_barrel
            * self.inputs.batch_size_barrels
        )

    def compute_total_packaging_cost(self) -> float:
        """
        Total packaging cost = packaging_price_per_unit * units_per_barrel * batch_size.
        Typically one packaging unit per gallon of beer.
        """
        return (
            self.inputs.packaging_cost_per_unit
            * self.inputs.packaging_units_per_barrel
            * self.inputs.batch_size_barrels
        )

    def compute_total_cost(self) -> float:
        """Sum of all ingredient and packaging costs."""
        return (
            self.compute_total_grain_cost()
            + self.compute_total_hops_cost()
            + self.compute_total_yeast_cost()
            + self.compute_total_packaging_cost()
        )

    def compute_cost_per_barrel(self) -> float:
        """Total cost / batch size in barrels."""
        if self.inputs.batch_size_barrels == 0:
            raise ValueError("Batch size must be greater than zero.")
        return self.compute_total_cost() / self.inputs.batch_size_barrels

    def compute_recommended_selling_price(self) -> float:
        """
        Recommended selling price per barrel = cost_per_barrel * (1 + margin_percent / 100).

        Similar to the reference implementation, which applies a coefficient
        to the cost price to determine the final sale price.
        """
        cost_per_barrel = self.compute_cost_per_barrel()
        return cost_per_barrel * (1 + self.inputs.margin_percent / 100)

    def summary(self) -> dict:
        """Return a structured summary of all computed values."""
        return {
            "batch_size_barrels": self.inputs.batch_size_barrels,
            "grain_cost_per_lb": self.inputs.grain_cost_per_lb,
            "hops_cost_per_oz": self.inputs.hops_cost_per_oz,
            "yeast_cost_per_unit": self.inputs.yeast_cost_per_unit,
            "packaging_cost_per_unit": self.inputs.packaging_cost_per_unit,
            "margin_percent": self.inputs.margin_percent,
            "total_grain_cost": round(self.compute_total_grain_cost(), 2),
            "total_hops_cost": round(self.compute_total_hops_cost(), 2),
            "total_yeast_cost": round(self.compute_total_yeast_cost(), 2),
            "total_packaging_cost": round(self.compute_total_packaging_cost(), 2),
            "total_cost": round(self.compute_total_cost(), 2),
            "cost_per_barrel": round(self.compute_cost_per_barrel(), 2),
            "recommended_selling_price_per_barrel": round(
                self.compute_recommended_selling_price(), 2
            ),
        }


def run_sample_batch():
    """Run a sample calculation and print formatted results."""
    print("=" * 60)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 60)
    print()

    # --- Sample batch inputs ---
    inputs = BrewCostInputs(
        grain_cost_per_lb=1.50,       # $/lb for pale malt
        hops_cost_per_oz=8.00,        # $/oz for Centennial hops
        yeast_cost_per_unit=5.00,     # $/unit for Safale US-05
        packaging_cost_per_unit=0.50, # $/unit for cans/bottles
        batch_size_barrels=5.0,       # 5 barrel batch
        margin_percent=35.0,          # 35% margin
    )

    calc = BatchCostCalculator(inputs)

    print(f"Batch size                : {inputs.batch_size_barrels} barrels")
    print(f"Grain cost                : ${inputs.grain_cost_per_lb:.2f}/lb")
    print(f"Hops cost                 : ${inputs.hops_cost_per_oz:.2f}/oz")
    print(f"Yeast cost                : ${inputs.yeast_cost_per_unit:.2f}/unit")
    print(f"Packaging cost            : ${inputs.packaging_cost_per_unit:.2f}/unit")
    print(f"Margin                    : {inputs.margin_percent:.0f}%")
    print("-" * 60)

    grain_total = calc.compute_total_grain_cost()
    hops_total = calc.compute_total_hops_cost()
    yeast_total = calc.compute_total_yeast_cost()
    packaging_total = calc.compute_total_packaging_cost()
    total = calc.compute_total_cost()
    per_barrel = calc.compute_cost_per_barrel()
    selling_price = calc.compute_recommended_selling_price()

    print(f"Grain cost (total)        : ${grain_total:.2f}")
    print(f"Hops cost (total)         : ${hops_total:.2f}")
    print(f"Yeast cost (total)        : ${yeast_total:.2f}")
    print(f"Packaging cost (total)    : ${packaging_total:.2f}")
    print("-" * 60)
    print(f"TOTAL BATCH COST          : ${total:.2f}")
    print(f"COST PER BARREL           : ${per_barrel:.2f}")
    print(f"RECOMMENDED SELLING PRICE : ${selling_price:.2f}/barrel")
    print("=" * 60)

    # Also print the structured summary
    print("\nStructured summary (JSON):")
    print(json.dumps(calc.summary(), indent=2))

    return calc


if __name__ == "__main__":
    run_sample_batch()
