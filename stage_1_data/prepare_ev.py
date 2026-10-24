"""
STAGE I / STEP 2 — VALIDATE THE EV MARKET-SHARE REFERENCE TABLE

What this file does:
1. Imports ten manually transcribed, PUBLICLY REPORTED observations:
   five states x Q1/Q2 2026.
2. Checks state codes, quarter labels, numbers, percentages, and duplicates.
3. Checks that the published EV total approximately equals BEV+PHEV+FCEV.
4. Exports a small clean table for merging with quarterly gasoline averages.

Why pandas?
- read_csv() imports the published report transcription.
- to_numeric() ensures percentages can be compared mathematically.
- duplicated() and merge(validate=...) protect against bad joins.

Definitions: BEV=battery electric, PHEV=plug-in hybrid,
FCEV=fuel-cell electric. Conventional HEVs are NOT included.
The published components and totals are rounded independently.

Reproduce:
    python stage_1_data/prepare_ev.py

Input:  data/reference/ev_market_share_2026.csv
Output: data/processed/ev_quarterly.csv
"""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "data" / "reference" / "ev_market_share_2026.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "ev_quarterly.csv"
STATES = {"CA", "MI", "FL", "NY", "IL"}
QUARTERS = {"2026Q1", "2026Q2"}
SHARE_FIELDS = [
    "bev_share_pct", "phev_share_pct", "fcev_share_pct", "ev_share_pct"
]


def clean_ev_frame(raw: pd.DataFrame) -> pd.DataFrame:
    """Check the published EV share observations, without changing values."""
    required = {"state", "quarter", "source_url", *SHARE_FIELDS}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"EV source file is missing columns: {sorted(missing)}")

    data = raw[list(required)].copy()
    if set(data["state"]) != STATES:
        raise ValueError("EV market share must cover exactly the five states.")
    if set(data["quarter"]) != QUARTERS:
        raise ValueError("EV reference must cover both Q1 and Q2 2026.")
    if len(data) != len(STATES) * len(QUARTERS):
        raise ValueError("Expected exactly ten state/quarter observations.")
    if data.duplicated(["state", "quarter"]).any():
        raise ValueError("Duplicate state/quarter in EV market share.")

    for column in SHARE_FIELDS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
        if data[column].isna().any() or (~data[column].between(0, 100)).any():
            raise ValueError(f"Missing or invalid percentage: {column}")

    if data["source_url"].isna().any() or (
        data["source_url"].astype(str).str.strip() == ""
    ).any():
        raise ValueError("Each EV observation requires a report URL.")

    component_sum = (
        data["bev_share_pct"] + data["phev_share_pct"] + data["fcev_share_pct"]
    )
    # Source tables round shares to hundredths of a percentage point.
    if ((component_sum - data["ev_share_pct"]).abs() > 0.03).any():
        raise ValueError("EV total differs unexpectedly from powertrain parts.")

    columns = ["state", "quarter", *SHARE_FIELDS, "source_url"]
    return data[columns].sort_values(["state", "quarter"]).reset_index(drop=True)


def main() -> None:
    """Validate the small hand-transcribed report table, then export it."""
    data = clean_ev_frame(pd.read_csv(SOURCE_FILE))
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUTPUT_FILE, index=False)
    print(f"Stage I/2 complete: {len(data)} validated EV market-share rows.")
    print(f"Saved: {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
