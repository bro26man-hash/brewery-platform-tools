from dataclasses import dataclass
from typing import Optional


@dataclass
class IngredientCosts:
    """Per-unit costs for each craft-brewery input."""
    grain_per_lb: float          # USD per pound of grain
    hops_per_oz: float          # USD per ounce of hops
    yeast_per_unit: float       # USD per yeast unit/vial
    packaging_per_unit: float   # USD per packaging unit (can, bottle, keg)


@dataclass
class BatchInputs:
    """Everything needed to price a single brew."""
    size_barrels: float                 # batch size in barrels
    grain_per_barrel: float = 14.0      # typical US craft: ~14 lb malt/barrel
    hops_per_barrel: float = 3.0        # oz of hops per barrel
    yeast_per_barrel: float = 1.0       # yeast units per barrel
    packaging_units_per_barrel: float = 330.0  # cans/bottles per barrel (~330 12-oz cans)
    margin_pct: float = 30.0            # target gross-margin %
    abv: float = 5.0                    # alcohol-by-volume (used by ABV-inspired pricing)
    abv_coefficient: float = 0.70       # mirrors ref: `abv * abv_coefficient + abv_constant`
    abv_constant: float = 2.30          # mirrors ref constant (converted to dollars)
    volume_multiplier: float = 31.0     # gallons per barrel (US beer barrel = 31 gal)
    price_per_vol_equiv: float = 0.55   # USD per gallon-equivalent (inspired by l_coefficient)


def compute_batch_costs(
    ingredients: IngredientCosts,
    batch: BatchInputs,
) -> dict:
    """Return a dict with total_cost, cost_per_barrel, abv_price, recommended_price."""
    # --- raw ingredient cost per barrel ---------------------------------------
    grain_cost       = ingredients.grain_per_lb      * batch.grain_per_barrel
    hops_cost        = ingredients.hops_per_oz       * batch.hops_per_barrel
    yeast_cost       = ingredients.yeast_per_unit    * batch.yeast_per_barrel
    packaging_cost   = ingredients.packaging_per_unit * batch.packaging_units_per_barrel
    ingredient_total = grain_cost + hops_cost + yeast_cost + packaging_cost

    # --- overheads (labour, utilities, shipping, tap-room loss, etc.) --------
    overhead_per_barrel = ingredient_total * 0.20   # typical +20 % assumption

    # --- cost per barrel --------------------------------------------------------
    cost_per_barrel = ingredient_total / batch.size_barrels + overhead_per_barrel

    # --- ABV-inspired price floor (mirrors the Streamlit 'abv_price' logic) ---
    abv_price = batch.abv * batch.abv_coefficient + batch.abv_constant

    # --- volume-based price (mirrors 'l_coefficient' logic) --------------------
    volume_based_price = (
        (ingredient_total / batch.size_barrels + overhead_per_barrel)
        * batch.volume_multiplier
        * batch.price_per_vol_equiv
    )
    volume_based_price = max(volume_based_price, 0.01)

    # --- recommended selling price: whichever is higher (matches ref philosophy)
    recommended_per_barrel = max(
        cost_per_barrel * (1 + batch.margin_pct / 100),
        abv_price,
        volume_based_price,
    )

    # --- totals -----------------------------------------------------------------
    total_cost           = cost_per_barrel * batch.size_barrels
    total_revenue_holding = recommended_per_barrel * batch.size_barrels
    gross_profit         = total_revenue_holding - total_cost

    return {
        "size_barrels":       batch.size_barrels,
        "grain_cost":         round(grain_cost, 2),
        "hops_cost":          round(hops_cost, 2),
        "yeast_cost":         round(yeast_cost, 2),
        "packaging_cost":     round(packaging_cost, 2),
        "ingredient_total":   round(ingredient_total, 2),
        "overhead_pct":       20.0,
        "overhead_cost":      round(ingredient_total * 0.20, 2),
        "cost_per_barrel":    round(cost_per_barrel, 2),
        "total_cost":         round(total_cost, 2),
        "margin_pct":         batch.margin_pct,
        "abv_price_floor":    round(abv_price, 2),
        "volume_based_price": round(volume_based_price, 2),
        "recommended_price":  round(recommended_per_barrel, 2),
        "total_revenue":      round(total_revenue_holding, 2),
        "gross_profit":       round(gross_profit, 2),
    }


def print_batch_report(r: dict) -> str:
    lines = [
        "═══════════════════════════════════════════════",
        "   CRAFT BREWERY BATCH COST REPORT",
        "═══════════════════════════════════════════════",
        f"Batch Size          : {r['size_barrels']:>8.1f} barrels",
        "───────────────────────────────────────────",
        f"  Grain ($/lb)      : ${r['grain_cost']:>8.2f}",
        f"  Hops ($/oz)       : ${r['hops_cost']:>8.2f}",
        f"  Yeast ($/unit)    : ${r['yeast_cost']:>8.2f}",
        f"  Packaging ($/unit): ${r['packaging_cost']:>8.2f}",
        "───────────────────────────────────────────",
        f"Ingredient Total    : ${r['ingredient_total']:>8.2f}",
        f"Overhead ({r['overhead_pct']:.0f}%)       : ${r['overhead_cost']:>8.2f}",
        "───────────────────────────────────────────",
        f"Cost per Barrel     : ${r['cost_per_barrel']:>8.2f}",
        f"Total Batch Cost    : ${r['total_cost']:>8.2f}",
        "───────────────────────────────────────────",
        f"ABV price floor     : ${r['abv_price_floor']:>8.2f}",
        f"Vol-based price     : ${r['volume_based_price']:>8.2f}",
        f"Recommended price   : ${r['recommended_price']:>8.2f}/barrel",
        "───────────────────────────────────────────",
        f"Margin              : {r['margin_pct']:>8.1f}%",
        f"Total Revenue       : ${r['total_revenue']:>8.2f}",
        f"Gross Profit        : ${r['gross_profit']:>8.2f}",
        "═══════════════════════════════════════════════",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    ing = IngredientCosts(
        grain_per_lb=2.50,
        hops_per_oz=1.20,
        yeast_per_unit=8.50,
        packaging_per_unit=0.12,
    )

    batch = BatchInputs(
        size_barrels=10.0,
        margin_pct=30.0,
        abv=5.2,
    )

    result = compute_batch_costs(ing, batch)
    print(print_batch_report(result))
    print("\n✅ All calculations completed successfully.")