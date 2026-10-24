"""
STAGE II / STEP 5 — THREE EXPLAINABLE CHARTS

Why matplotlib.pyplot?
- plot() draws a daily PRICE trend for each state.
- bar() makes a Q1-versus-Q2 GROUPED comparison of new EV share.
- scatter() compares state-level CHANGES; annotate() labels the states.
- savefig() makes portable PNGs for a README or portfolio website.

Graph 1: Daily regular gasoline prices, five states, 2026 to the last
         observed day. No smoothing or fabricated points.
Graph 2: 2026 Q1 versus Q2 EV share of NEW vehicle registrations.
         Not a share of all vehicles on the road.
Graph 3: 2026 Q1->Q2 gas price change (%) versus EV share change
         (percentage points). Five marks; no fitted trend line.

Reproduce:
    python stage_2_analysis/charts.py

Inputs:  data/processed/gas_daily.csv
         data/processed/market_quarterly.csv
         outputs/state_changes_2026.csv
Outputs: outputs/chart_1_gas_2026.png
         outputs/chart_2_ev_share.png
         outputs/chart_3_changes_scatter.png
"""

from pathlib import Path

import matplotlib

# 'Agg' saves PNG files without requiring a monitor/display server.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GAS_FILE = ROOT / "data" / "processed" / "gas_daily.csv"
MARKET_FILE = ROOT / "data" / "processed" / "market_quarterly.csv"
CHANGES_FILE = ROOT / "outputs" / "state_changes_2026.csv"
OUTPUT_DIR = ROOT / "outputs"
STATES = ["CA", "MI", "FL", "NY", "IL"]


def style_axes(ax: plt.Axes, title: str, ylabel: str) -> None:
    """Use a single legible style for graphs 1, 2, and 3."""
    ax.set_title(title, loc="left", fontsize=12, weight="bold", pad=14)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.18)
    ax.set_axisbelow(True)


def chart_1_gas_trend(gas: pd.DataFrame) -> None:
    """Function for Graph 1: plot() one daily line per state, no smoothing."""
    daily = gas.copy()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.loc[daily["date"].dt.year == 2026]
    fig, ax = plt.subplots(figsize=(10, 5.4))
    # reindex() inserts NaN at missing calendar dates. matplotlib then BREAKS
    # the line at those dates instead of joining observations across a gap.
    all_days = pd.date_range("2026-01-01", daily["date"].max(), freq="D")
    for state in STATES:
        part = daily.loc[daily["state"] == state].set_index("date")
        observed_with_gaps = part["regular_usd_per_gallon"].reindex(all_days)
        ax.plot(all_days, observed_with_gaps, label=state, linewidth=1.6)
    style_axes(ax, "2026 daily regular gasoline prices", "USD per gallon")
    ax.set_xlabel("Observation date (gaps are not interpolated)")
    ax.legend(title="State", ncol=5, frameon=False)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "chart_1_gas_2026.png", dpi=175)
    plt.close(fig)


def chart_2_ev_share(market: pd.DataFrame) -> None:
    """Function for Graph 2: two bar() groups per state using EV shares."""
    wide = market.pivot(index="state", columns="quarter", values="ev_share_pct")
    x = np.arange(len(STATES))
    width = 0.34
    fig, ax = plt.subplots(figsize=(9, 5.1))
    ax.bar(x - width / 2, wide.loc[STATES, "2026Q1"],
           width, label="Q1 2026", color="#567D95")
    ax.bar(x + width / 2, wide.loc[STATES, "2026Q2"],
           width, label="Q2 2026", color="#E6A65B")
    ax.set_xticks(x, STATES)
    style_axes(ax, "Share of NEW registrations that were plug-in EVs",
               "EV share of new registrations (%)")
    ax.set_xlabel("State")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "chart_2_ev_share.png", dpi=175)
    plt.close(fig)


def chart_3_change_comparison(changes: pd.DataFrame) -> None:
    """Function for Graph 3: scatter() with five labelled state dots.

    The scatter is a descriptive visual only. No regression line is fitted,
    because state aggregates do not identify individual purchase motivations.
    """
    fig, ax = plt.subplots(figsize=(8, 5.3))
    ax.scatter(changes["gas_change_pct"], changes["ev_change_pp"],
               color="#397E86", s=90)
    for row in changes.itertuples(index=False):
        ax.annotate(row.state, (row.gas_change_pct, row.ev_change_pp),
                    xytext=(7, 7), textcoords="offset points", fontsize=10)
    style_axes(ax, "Did the two state-level measures move together?",
               "EV share change (percentage points)")
    ax.set_xlabel("Average regular-gas price change, Q1->Q2 2026 (%)")
    ax.text(0.02, 0.03, "Five states only | association is not causation",
            transform=ax.transAxes, fontsize=9, alpha=0.8)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "chart_3_changes_scatter.png", dpi=175)
    plt.close(fig)


def main() -> None:
    """Read Stage I and Stage II tables; produce all three PNG files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    chart_1_gas_trend(pd.read_csv(GAS_FILE))
    chart_2_ev_share(pd.read_csv(MARKET_FILE))
    chart_3_change_comparison(pd.read_csv(CHANGES_FILE))
    print("Stage II/5 complete. Three PNG charts saved in outputs/.")


if __name__ == "__main__":
    main()
