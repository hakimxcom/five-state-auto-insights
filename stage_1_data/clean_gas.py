"""
STAGE I / STEP 1 — IMPORT AND CLEAN GASOLINE DATA

What this file does:
1. Reads the original daily MasterGas.csv file (downloaded separately).
2. Keeps California, Michigan, Florida, New York, and Illinois.
3. Converts dates into real dates and prices such as '$3.459' into numbers.
4. Keeps records from January 1, 2025 onward.
5. Rejects invalid prices and duplicated state/date observations.
6. Writes a clean, small CSV for the next step.

Why pandas?
- read_csv() imports a table.
- to_datetime() interprets ISO-format dates.
- to_numeric() converts text prices for calculations.
- drop_duplicates() is NOT used: duplicates are flagged instead of hidden.

Reproduce this step:
    python stage_1_data/clean_gas.py

Input:  data/raw/MasterGas.csv  [download it; not redistributed here]
Output: data/processed/gas_daily.csv

Author: Sam Hakim | Five-State Automotive Consumer Insights
"""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "MasterGas.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "gas_daily.csv"

# Exact state names in the downloaded file; short codes make charts readable.
STATES = {
    "California": "CA",
    "Michigan": "MI",
    "Florida": "FL",
    "New York": "NY",
    "Illinois": "IL",
}


def clean_gas_frame(raw: pd.DataFrame) -> pd.DataFrame:
    """Return validated daily regular-grade gas prices for our five states.

    This function accepts a DataFrame so it can be tested without downloading
    the entire source file. It never invents prices for missing dates.
    """
    required = {"State", "Date", "Regular"}
    missing_columns = required - set(raw.columns)
    if missing_columns:
        raise ValueError(f"Gasoline file is missing columns: {sorted(missing_columns)}")

    data = raw.loc[raw["State"].isin(STATES), ["State", "Date", "Regular"]].copy()
    present = set(data["State"])
    if present != set(STATES):
        raise ValueError(f"Missing states: {sorted(set(STATES) - present)}")

    # 1. Date strings become datetime values. Bad dates become NaT and fail.
    data["date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d", errors="coerce")
    if data["date"].isna().any():
        raise ValueError("Some gasoline dates could not be parsed.")

    # 2. A dollar price is text; remove '$' and ',' before converting to float.
    prices = data["Regular"].astype("string").str.replace("$", "", regex=False)
    prices = prices.str.replace(",", "", regex=False)
    data["regular_usd_per_gallon"] = pd.to_numeric(prices, errors="coerce")
    if (
        data["regular_usd_per_gallon"].isna().any()
        or (~data["regular_usd_per_gallon"].between(0.01, 15.0)).any()
    ):
        raise ValueError("Some regular-gas prices are missing or implausible.")

    # 3. Filter the research period; preserve the original day-level detail.
    data = data.loc[data["date"] >= pd.Timestamp("2025-01-01")].copy()
    data["state"] = data["State"].map(STATES)

    # 4. A day can appear only once per state. Never silently average repeats.
    if data.duplicated(["state", "date"]).any():
        raise ValueError("Duplicate state/date combinations in gasoline data.")

    data["year"] = data["date"].dt.year
    data["quarter"] = data["date"].dt.to_period("Q").astype(str)

    columns = ["state", "date", "regular_usd_per_gallon", "year", "quarter"]
    return data[columns].sort_values(["state", "date"]).reset_index(drop=True)


def main() -> None:
    """Run the full import -> clean -> local CSV export workflow."""
    if not RAW_FILE.is_file():
        raise FileNotFoundError(
            f"Missing {RAW_FILE}. See data/README.md for download instructions."
        )

    raw = pd.read_csv(RAW_FILE)
    cleaned = clean_gas_frame(raw)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(OUTPUT_FILE, index=False, float_format="%.3f")

    print(f"Stage I/1 complete: {len(cleaned):,} clean daily observations.")
    print(f"States: {', '.join(sorted(cleaned['state'].unique()))}")
    print(f"Date range: {cleaned['date'].min().date()} to "
          f"{cleaned['date'].max().date()}")
    print(f"Saved: {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
