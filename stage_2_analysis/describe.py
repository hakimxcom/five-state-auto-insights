"""
STAGE II / STEP 4 — SIMPLE, DEFENSIBLE STATISTICS

Research question:
How did regular gasoline prices and the share of new EV registrations
change between Q1 and Q2 2026 in CA, MI, FL, NY, and IL?

Libraries:
- pandas: read the joined table; pivot() puts Q1 and Q2 side by side.
- scipy.stats: spearmanr() describes a rank association across five states.
  We present it as an exploratory descriptive statistic, NOT a causal test.

Equations (also explained in docs/methodology.md):
(1) Quarterly gas mean = sum of observed daily prices / observed day count.
    This calculation was performed by Stage I / combine_audit.py.
(2) Gas price change (%) =
    100 * (Q2 mean - Q1 mean) / Q1 mean.
(3) EV share change (percentage points) =
    Q2 EV market share (%) - Q1 EV market share (%).
(4) Spearman rho = correlation of the ranks of equations (2) and (3).
    Five state observations are too few to claim a general relationship.

Reproduce:
    python stage_2_analysis/describe.py

Input:  data/processed/market_quarterly.csv
Output: outputs/state_changes_2026.csv
        outputs/analysis_notes.txt

This code is intentionally short: each calculation has a named function.
"""

from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "processed" / "market_quarterly.csv"
OUTPUT_FILE = ROOT / "outputs" / "state_changes_2026.csv"
NOTES_FILE = ROOT / "outputs" / "analysis_notes.txt"


def percent_change(before: pd.Series, after: pd.Series) -> pd.Series:
    """Equation 2: relative change in the price of one gallon of gasoline."""
    if (before <= 0).any():
        raise ValueError("Q1 gas price must be positive.")
    return 100.0 * (after - before) / before


def percentage_point_change(before: pd.Series, after: pd.Series) -> pd.Series:
    """Equation 3: absolute change between two market-share percentages."""
    return after - before


def summarize_state_changes(market: pd.DataFrame) -> pd.DataFrame:
    """Put Q1/Q2 side by side; calculate changes for each of five states.

    No regression, prediction, or consumer-level analysis is performed.
    Five aggregates cannot establish why any consumer chose an EV.
    """
    needed = {"state", "quarter", "gas_price_quarter_mean_usd", "ev_share_pct"}
    if not needed.issubset(market.columns):
        raise ValueError(f"Missing fields: {sorted(needed - set(market.columns))}")
    if len(market) != 10 or market.duplicated(["state", "quarter"]).any():
        raise ValueError("Expected ten unique state-quarter observations.")

    gas = market.pivot(
        index="state", columns="quarter", values="gas_price_quarter_mean_usd"
    )
    ev = market.pivot(index="state", columns="quarter", values="ev_share_pct")
    if set(gas.columns) != {"2026Q1", "2026Q2"}:
        raise ValueError("Both Q1 and Q2 2026 must be present.")

    result = pd.DataFrame(index=gas.index)
    result["gas_q1_usd"] = gas["2026Q1"]
    result["gas_q2_usd"] = gas["2026Q2"]
    result["gas_change_pct"] = percent_change(
        result["gas_q1_usd"], result["gas_q2_usd"]
    )
    result["ev_q1_share_pct"] = ev["2026Q1"]
    result["ev_q2_share_pct"] = ev["2026Q2"]
    result["ev_change_pp"] = percentage_point_change(
        result["ev_q1_share_pct"], result["ev_q2_share_pct"]
    )

    if result.isna().any().any():
        raise ValueError("Missing values in one of the comparison quarters.")
    return result.reset_index().sort_values("state").reset_index(drop=True)


def descriptive_rank_association(results: pd.DataFrame) -> float:
    """Equation 4: rank correlation across the FIVE states, for context only.

    It is not a causal estimate, a statistically reliable population
    association, or evidence that gasoline prices drive EV demand.
    """
    if len(results) != 5:
        raise ValueError("The exploratory comparison is scoped to five states.")
    rho, _p_value = spearmanr(
        results["gas_change_pct"], results["ev_change_pp"]
    )
    return float(rho)


def main() -> None:
    """Run the three arithmetic comparisons, export, and explain limitations."""
    market = pd.read_csv(INPUT_FILE)
    result = summarize_state_changes(market)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False, float_format="%.4f")

    rho = descriptive_rank_association(result)
    lines = [
        "FIVE-STATE AUTOMOTIVE CONSUMER INSIGHTS | 2026 Q1 -> Q2",
        "",
        "Question: How did gasoline prices and EV share of new light-duty",
        "vehicle registrations move in CA, MI, FL, NY, and IL?",
        "",
        result.round(3).to_string(index=False),
        "",
        f"Exploratory Spearman rank association (5 states): {rho:.3f}",
        "This is descriptive only; the sample has just five state aggregates.",
        "Do not interpret it as evidence that gasoline prices caused EV purchases.",
        "Variables are quarterly aggregates, not individual consumer survey data.",
        "The EV series excludes conventional hybrids (HEVs).",
        "Quarterly gas averages use observed days only; missing days are not filled.",
        "Price and market share data come from different sources and units.",
        "Potential confounders include policy, vehicle availability, model mix,",
        "incentives, household budgets, charging, and long purchase lead times.",
        "For state coverage and exact gaps see outputs/stage_1_data_quality.md.",
    ]
    NOTES_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Stage II/4 complete. State comparison:")
    print(result.round(3).to_string(index=False))
    print(f"Exploratory rho (n=5): {rho:.3f} — not causal.")
    print(f"Saved: {OUTPUT_FILE.relative_to(ROOT)}")
    print(f"Saved: {NOTES_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
