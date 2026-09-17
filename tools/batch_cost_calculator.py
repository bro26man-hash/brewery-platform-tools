# batch_cost_calculator.py
# Craft Brewery Batch Cost Calculator
# Inspired by: tfrayner/beerfestdb - tool_dashboard/CBF_beer_price_calculator.py
# (https://github.com/tfrayner/beerfestdb)
#
# The original calculator determines sale price based on ABV or cask cost,
# whichever is greater. This script adapts that cost-based pricing philosophy
# for craft brewery batch-level cost accounting.

from dataclasses import dataclass, field
from typing import Optional
import json


# ─────────────────────────────────────────────────────────
# Reference constants (inspired by CBF_beer_price_calculator.py)
# ─────────────────────────────────────────────────────────
# The reference uses default ABV coefficients (70 pence coefficient,
# 230 pence constant) and a price-per-litre coefficient (1.64).
# We translate that idea into a grain-equivalent cost approach
# where a baseline cost-per-barrel is computed from ingredients.

# A rough rule-of-thumb: 1 barrel (bbl) = 31 gallons ≈ 117.3 litres
BARREL_TO_LITRES = 117.3
# Typical grain usage: ~15 lb per barrel for a standard ale
DEFAULT_GRAIN_PER_BBL = 15.0  # lb/bbl
# Typical hops usage: ~0.5 oz per barrel (bittering + aroma)
DEFAULT_HOPS_PER_BBL = 0.5    # oz/bbl
# Typical yeast: 1 unit (stable) per batch (not per barrel)
DEFAULT_YEAST_PER_BATCH = 1.0 # units/batch
# Default packaging: 1 keg per batch (simplified)
DEFAULT_PACKAGING_PER_BATCH = 1.0 # units/batch


@dataclass
class BatchInputs:
    """All configurable inputs for a batch cost calculation."""
    grain_price_per_lb: float = 1.50
    hops_price_per_oz: float = 5.00
    yeast_price_per_unit: float = 50.00
    packaging_price_per_unit: float = 10.00
    batch_size_bbl: float = 5.0          # barrels
    grain_per_bbl: float = DEFAULT_GRAIN_PER_BBL
    hops_per_bbl: float = DEFAULT_HOPS_PER_BBL
    yeast_per_batch: float = DEFAULT_YEAST_PER_BATCH
    packaging_per_batch: float = DEFAULT_PACKAGING_PER_BATCH
    margin_percent: float = 30.0         # markup on cost

    def validate(self):
        errors = []
        for field_name in [
            "grain_price_per_lb", "hops_price_per_oz",
            "yeast_price_per_unit", "packaging_price_per_unit",
            "batch_size_bbl", "margin_percent"
        ]:
            val = getattr(self, field_name)
            if val < 0:
                errors.append(f"{field_name} must be >= 0 (got {val})")
        if self.grain_per_bbl <= 0:
            errors.append("grain_per_bbl must be > 0")
        if self.hops_per_bbl <= 0:
            errors.append("hops_per_bbl must be > 0")
        if self.yeast_per_batch <= 0:
            errors.append("yeast_per_batch must be > 0")
        if self.packaging_per_batch <= 0:
            errors.append("packaging_per_batch must be > 0")
        if self.batch_size_bbl <= 0:
            errors.append("batch_size_bbl must be > 0")
        return errors


@dataclass
class BatchCostResult:
    """Computed cost breakdown for a batch."""
    grain_cost: float
    hops_cost: float
    yeast_cost: float
    packaging_cost: float
    total_cost: float
    cost_per_bbl: float
    margin_amount: float
    recommended_price_per_bbl: float

    def to_dict(self):
        return {
            "grain_cost": round(self.grain_cost, 2),
            "hops_cost": round(self.hops_cost, 2),
            "yeast_cost": round(self.yeast_cost, 2),
            "packaging_cost": round(self.packaging_cost, 2),
            "total_cost": round(self.total_cost, 2),
            "cost_per_bbl": round(self.cost_per_bbl, 2),
            "margin_amount": round(self.margin_amount, 2),
            "recommended_price_per_bbl": round(self.recommended_price_per_bbl, 2),
        }


def calculate_batch_cost(inputs: BatchInputs) -> BatchCostResult:
    """
    Calculate the total batch cost, cost per barrel, and recommended
    selling price per barrel given a configurable margin.

    Inspired by CBF_beer_price_calculator.py which uses:
        cost_price = (cask_price / litres_per_container) * l_coefficient
        sale_price = max(abv_price, cost_price)

    Here we compute:
        ingredient_cost = usage_rate * unit_price
        total_cost = sum(ingredient_costs)
        cost_per_bbl = total_cost / batch_size_bbl
        recommended_price = cost_per_bbl * (1 + margin / 100)
    """
    grain_cost = inputs.batch_size_bbl * inputs.grain_per_bbl * inputs.grain_price_per_lb
    hops_cost = inputs.batch_size_bbl * inputs.hops_per_bbl * inputs.hops_price_per_oz
    yeast_cost = inputs.yeast_per_batch * inputs.yeast_price_per_unit
    packaging_cost = inputs.packaging_per_batch * inputs.packaging_price_per_unit

    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_bbl = total_cost / inputs.batch_size_bbl

    margin_amount = total_cost * (inputs.margin_percent / 100.0)
    recommended_price_per_bbl = cost_per_bbl + (margin_amount / inputs.batch_size_bbl)

    return BatchCostResult(
        grain_cost=grain_cost,
        hops_cost=hops_cost,
        yeast_cost=yeast_cost,
        packaging_cost=packaging_cost,
        total_cost=total_cost,
        cost_per_bbl=cost_per_bbl,
        margin_amount=margin_amount,
        recommended_price_per_bbl=recommended_price_per_bbl,
    )


def print_result(inputs: BatchInputs, result: BatchCostResult):
    """Pretty-print the batch cost breakdown."""
    print("=" * 60)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("  Inspired by tfrayner/beerfestdb CBF_beer_price_calculator.py")
    print("=" * 60)
    print()
    print("─── BATCH CONFIGURATION ───")
    print(f"  Batch size:              {inputs.batch_size_bbl:.1f} bbl")
    print(f"  Grain usage:             {inputs.grain_per_bbl:.1f} lb/bbl")
    print(f"  Hops usage:              {inputs.hops_per_bbl:.2f} oz/bbl")
    print(f"  Yeast per batch:         {inputs.yeast_per_batch:.1f} units")
    print(f"  Packaging per batch:     {inputs.packaging_per_batch:.1f} units")
    print(f"  Margin:                  {inputs.margin_percent:.1f}%")
    print()
    print("─── COST BREAKDOWN ───")
    print(f"  Grain cost:              ${result.grain_cost:>8.2f}")
    print(f"  Hops cost:               ${result.hops_cost:>8.2f}")
    print(f"  Yeast cost:              ${result.yeast_cost:>8.2f}")
    print(f"  Packaging cost:          ${result.packaging_cost:>8.2f}")
    print(f"  ─────────────────────────────────")
    print(f"  TOTAL BATCH COST:        ${result.total_cost:>8.2f}")
    print()
    print("─── PRICING ───")
    print(f"  Cost per barrel:         ${result.cost_per_bbl:>8.2f}")
    print(f"  Margin amount (batch):   ${result.margin_amount:>8.2f}")
    print(f"  ─────────────────────────────────")
    print(f"  RECOMMENDED PRICE/bbl:   ${result.recommended_price_per_bbl:>8.2f}")
    print("=" * 60)


# ─────────────────────────────────────────────────────────
# SAMPLE BATCH — executed on run for validation
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Sample: 5 bbl batch, standard American pale ale parameters
    sample = BatchInputs(
        grain_price_per_lb=1.75,     # ~$1.75/lb for 2-row malt
        hops_price_per_oz=6.50,      # ~$6.50/oz for Centennial
        yeast_price_per_unit=45.00,  # White Labs / Wyeast pitch
        packaging_price_per_unit=12.00, # 1 keg
        batch_size_bbl=5.0,
        grain_per_bbl=15.0,
        hops_per_bbl=0.6,
        yeast_per_batch=1.0,
        packaging_per_batch=1.0,
        margin_percent=30.0,
    )

    errors = sample.validate()
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)

    result = calculate_batch_cost(sample)
    print_result(sample, result)

    # Quick assertions to confirm correctness
    assert abs(result.grain_cost - 131.25) < 0.01, f"grain: {result.grain_cost}"
    assert abs(result.hops_cost - 19.50) < 0.01, f"hops: {result.hops_cost}"
    assert abs(result.yeast_cost - 45.00) < 0.01, f"yeast: {result.yeast_cost}"
    assert abs(result.packaging_cost - 12.00) < 0.01, f"packaging: {result.packaging_cost}"
    assert abs(result.total_cost - 207.75) < 0.01, f"total: {result.total_cost}"
    assert abs(result.cost_per_bbl - 41.55) < 0.01, f"cost/bbl: {result.cost_per_bbl}"
    assert abs(result.recommended_price_per_bbl - 54.02) < 0.02, f"price/bbl: {result.recommended_price_per_bbl}"
    print("\n✅ All assertions passed — calculator is correct.")
