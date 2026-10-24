"""
STAGE I / STEP 3 — QUARTERLY AGGREGATION, JOIN, AND COVERAGE AUDIT

Why combine two sources?
- Gas prices are observed DAILY for each state.
- EV market share is reported QUARTERLY for each state.
- Comparing daily price rows directly to quarterly market shares would
  repeat an EV observation dozens of times and inflate the sample size.

This script:
1. Computes the arithmetic mean of available daily gas prices per quarter.
2. Counts observed days, expected calendar days, and days missing.
3. Uses pandas.merge(..., validate='one_to_one') on state + quarter.
4. Saves exactly ten combined rows (5 states x 2 quarters).
5. Produces an audit listing missing DAILY gasoline dates per state.

Important: Missing prices remain missing. No interpolation, forward fill,
or fabricated data. EV market share is reported, not modeled here.

Reproduce:
    python stage_1_data/combine_audit.py

Inputs:  data/processed/gas_daily.csv
         data/processed/ev_quarterly.csv
Outputs: data/processed/market_quarterly.csv
         outputs/stage_1_data_quality.md
"""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GAS_FILE = ROOT / "data" / "processed" / "gas_daily.csv"
EV_FILE = ROOT / "data" / "processed" / "ev_quarterly.csv"
MARKET_FILE = ROOT / "data" / "processed" / "market_quarterly.csv"
AUDIT_FILE = ROOT / "outputs" / "stage_1_data_quality.md"
QUARTERS = ("2026Q1", "2026Q2")


def combine_quarterly(gas: pd.DataFrame, ev: pd.DataFrame) -> pd.DataFrame:
    """Join at state-quarter grain (not at the individual gasoline day).

    Equation 1: mean quarterly gasoline price =
        sum(observed daily regular prices) / number of observed days.

    Missing days do NOT enter the denominator. The count is shown as
    coverage so readers know how complete each quarter is.
    """
    daily = gas.copy()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.loc[daily["quarter"].isin(QUARTERS)].copy()
    if daily.duplicated(["state", "date"]).any():
        raise ValueError("Repeated state/date detected before the aggregation.")

    quarterly = (
        daily.groupby(["state", "quarter"], as_index=False)
        .agg(
            gas_price_quarter_mean_usd=("regular_usd_per_gallon", "mean"),
            days_observed=("date", "nunique"),
        )
    )
    quarter_days = {"2026Q1": 90, "2026Q2": 91}
    quarterly["days_expected"] = quarterly["quarter"].map(quarter_days)
    quarterly["days_missing"] = (
        quarterly["days_expected"] - quarterly["days_observed"]
    )
    if (quarterly["days_missing"] < 0).any():
        raise ValueError("More observations than calendar days.")

    joined = ev.merge(
        quarterly,
        on=["state", "quarter"],
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    if len(joined) != 10 or (joined["_merge"] != "both").any():
        raise ValueError("All ten EV observations need matching gas summaries.")
    if joined["days_observed"].isna().any():
        raise ValueError("Gas coverage is missing from the merge.")

    columns = [
        "state", "quarter", "gas_price_quarter_mean_usd",
        "days_observed", "days_expected", "days_missing",
        "ev_share_pct", "bev_share_pct", "phev_share_pct", "fcev_share_pct",
        "source_url",
    ]
    return joined[columns].sort_values(["state", "quarter"]).reset_index(drop=True)


def missing_date_audit(gas: pd.DataFrame) -> list[str]:
    """Enumerate missing 2026 daily observations through latest observed day."""
    data = gas.copy()
    data["date"] = pd.to_datetime(data["date"])
    end = min(data["date"].max(), pd.Timestamp("2026-12-31"))
    expected = pd.date_range("2026-01-01", end, freq="D")
    lines = [
        "# Stage I data-quality audit",
        "",
        f"2026 coverage checked through **{end.date()}**.",
        "Missing dates are reported as gaps, never estimated or filled.",
        "",
        "| State | Observed days | Expected days | Missing dates |",
        "|---|---:|---:|---|",
    ]
    for state in sorted(data["state"].unique()):
        actual = pd.DatetimeIndex(
            data.loc[(data["state"] == state) & (data["date"].dt.year == 2026), "date"]
        )
        missing = expected.difference(actual)
        formatted = ", ".join(day.strftime("%Y-%m-%d") for day in missing)
        lines.append(
            f"| {state} | {len(actual)} | {len(expected)} | {formatted or 'None'} |"
        )
    return lines


def main() -> None:
    """Merge and write both the analytical table and transparent QA report."""
    gas = pd.read_csv(GAS_FILE, parse_dates=["date"])
    ev = pd.read_csv(EV_FILE)
    combined = combine_quarterly(gas, ev)
    MARKET_FILE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(MARKET_FILE, index=False, float_format="%.5f")

    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    audit = missing_date_audit(gas)
    audit.extend(["", "## Q1/Q2 coverage", "",
                  "Expected calendar days: Q1 = 90, Q2 = 91.", ""])
    for row in combined.itertuples(index=False):
        audit.append(
            f"- {row.state} {row.quarter}: "
            f"{row.days_observed}/{row.days_expected} days observed; "
            f"{row.days_missing} missing."
        )
    AUDIT_FILE.write_text("\n".join(audit) + "\n", encoding="utf-8")
    print("Stage I/3 complete: five states x two quarters = 10 rows.")
    print(f"Saved: {MARKET_FILE.relative_to(ROOT)}")
    print(f"Saved: {AUDIT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
