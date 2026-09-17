"""
Craft Brewery Batch Cost Calculator
====================================
Inspired by the reference implementation:
    tfrayner/beerfestdb -> tool_dashboard/CBF_beer_price_calculator.py

The reference tool prices festival beers from a database using a cask-cost
plus an ABV coefficient. This standalone script instead builds the cost of a
brewing batch from first principles: individual ingredient costs (grain, hops,
yeast, packaging), a batch size in barrels, and a configurable margin that
yields a recommended selling price per barrel.

Author: Platform Team
License: Unlicensed
"""

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Default ingredient consumption rates per one-barrel (31 US gal) batch.
# These can be overridden per BatchConfig to match a given recipe.
# ---------------------------------------------------------------------------
DEFAULT_GRAIN_PER_BBL = 10.0   # lbs of malt per barrel
DEFAULT_HOPS_PER_BBL = 1.0     # oz of hops per barrel
DEFAULT_YEAST_PER_BBL = 1.0    # yeast units (packets/vials) per barrel
DEFAULT_PACKAGING_PER_BBL = 1.0  # packaging units (kegs/bottles) per barrel


@dataclass
class BatchConfig:
    """Configurable rates and economic parameters for the calculation."""

    # Ingredient unit costs ($)
    grain_cost_per_lb: float = 0.0
    hops_cost_per_oz: float = 0.0
    yeast_cost_per_unit: float = 0.0
    packaging_cost_per_unit: float = 0.0

    # Batch size
    batch_size_barrels: float = 1.0

    # Ingredient consumption per barrel (overridable)
    grain_per_bbl: float = DEFAULT_GRAIN_PER_BBL
    hops_per_bbl: float = DEFAULT_HOPS_PER_BBL
    yeast_per_bbl: float = DEFAULT_YEAST_PER_BBL
    packaging_per_bbl: float = DEFAULT_PACKAGING_PER_BBL

    # Margin applied on top of cost to derive the sale price
    margin_percent: float = 30.0  # e.g. 30 == 30%


@dataclass
class BatchResult:
    """Holds the computed cost breakdown and recommended pricing."""

    grain_cost: float
    hops_cost: float
    yeast_cost: float
    packaging_cost: float
    total_cost: float
    cost_per_barrel: float
    margin_amount_per_bbl: float
    recommended_price_per_barrel: float

    def display(self, batch_size: float, margin_percent: float) -> None:
        print("=" * 60)
        print("       CRAFT BREWERY BATCH COST CALCULATOR")
        print("=" * 60)
        print("\n--- Ingredient Cost Breakdown ---")
        print(f"  Grain cost ..........: ${self.grain_cost:>10,.2f}")
        print(f"  Hops cost ...........: ${self.hops_cost:>10,.2f}")
        print(f"  Yeast cost ..........: ${self.yeast_cost:>10,.2f}")
        print(f"  Packaging cost ......: ${self.packaging_cost:>10,.2f}")
        print("-" * 60)
        print(f"  TOTAL BATCH COST ....: ${self.total_cost:>10,.2f}")
        print("-" * 60)
        print(f"  Batch size ..........: {batch_size} bbl")
        print(f"  Cost per barrel .....: ${self.cost_per_barrel:>10,.2f}")
        print(f"  Margin ..............: {margin_percent:.1f}%")
        print(f"  Margin per barrel ...: ${self.margin_amount_per_bbl:>10,.2f}")
        print("-" * 60)
        print(f"  *** RECOMMENDED SELLING PRICE / BARREL: "
              f"${self.recommended_price_per_barrel:>10,.2f} ***")
        print("=" * 60)


def calculate_batch_cost(cfg: BatchConfig) -> BatchResult:
    """Compute all cost figures from the provided configuration."""
    grain_cost = (cfg.grain_cost_per_lb * cfg.grain_per_bbl
                  * cfg.batch_size_barrels)
    hops_cost = (cfg.hops_cost_per_oz * cfg.hops_per_bbl
                 * cfg.batch_size_barrels)
    yeast_cost = (cfg.yeast_cost_per_unit * cfg.yeast_per_bbl
                  * cfg.batch_size_barrels)
    packaging_cost = (cfg.packaging_cost_per_unit
                      * cfg.packaging_per_bbl * cfg.batch_size_barrels)

    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_barrel = (total_cost / cfg.batch_size_barrels
                       if cfg.batch_size_barrels else 0.0)

    multiplier = 1.0 + (cfg.margin_percent / 100.0)
    recommended_price = cost_per_barrel * multiplier
    margin_amount = recommended_price - cost_per_barrel

    return BatchResult(
        grain_cost=grain_cost,
        hops_cost=hops_cost,
        yeast_cost=yeast_cost,
        packaging_cost=packaging_cost,
        total_cost=total_cost,
        cost_per_barrel=cost_per_barrel,
        margin_amount_per_bbl=margin_amount,
        recommended_price_per_barrel=recommended_price,
    )


def run_sample() -> None:
    """Run the calculator against a sample 5-barrel batch."""
    config = BatchConfig(
        grain_cost_per_lb=0.80,     # $0.80 / lb of malt
        hops_cost_per_oz=1.20,      # $1.20 / oz of hops
        yeast_cost_per_unit=1.50,   # $1.50 / yeast unit
        packaging_cost_per_unit=3.00,  # $3.00 / keg
        batch_size_barrels=5.0,     # 5 barrels
        grain_per_bbl=10.0,
        hops_per_bbl=1.0,
        yeast_per_bbl=1.0,
        packaging_per_bbl=1.0,
        margin_percent=30.0,        # 30% margin
    )

    result = calculate_batch_cost(config)
    result.display(config.batch_size_barrels, config.margin_percent)

    # --- Validation assertions ---
    assert abs(result.grain_cost - 40.00) < 1e-6
    assert abs(result.hops_cost - 6.00) < 1e-6
    assert abs(result.yeast_cost - 7.50) < 1e-6
    assert abs(result.packaging_cost - 15.00) < 1e-6
    assert abs(result.total_cost - 68.50) < 1e-6
    assert abs(result.cost_per_barrel - 13.70) < 1e-6
    assert abs(result.recommended_price_per_barrel - 17.81) < 1e-6
    print("\n[OK] Sample batch validated successfully - all figures correct.")


if __name__ == "__main__":
    run_sample()
