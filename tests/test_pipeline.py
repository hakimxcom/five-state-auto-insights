"""
RECONSTRUCTION TESTS — small invented examples, NOT empirical observations.

The tests use tiny synthetic tables to check the code's behavior.
They are not added to the real gas or EV source datasets.

Run: python -m unittest discover -s tests -v
"""

import unittest

import pandas as pd

from stage_1_data.clean_gas import clean_gas_frame
from stage_1_data.prepare_ev import clean_ev_frame
from stage_1_data.combine_audit import combine_quarterly
from stage_2_analysis.describe import (
    percent_change, percentage_point_change, summarize_state_changes,
)


STATE_NAMES = {
    "California": "CA", "Michigan": "MI", "Florida": "FL",
    "New York": "NY", "Illinois": "IL",
}


class TestStageOne(unittest.TestCase):
    def gas_raw(self):
        return pd.DataFrame([
            {"State": name, "Date": day, "Regular": price}
            for name in STATE_NAMES
            for day, price in [("2026-01-01", "$3.000"),
                               ("2026-01-02", "$5.000")]
        ])

    def test_dollar_strings_become_numeric(self):
        clean = clean_gas_frame(self.gas_raw())
        self.assertEqual(len(clean), 10)
        self.assertEqual(clean["regular_usd_per_gallon"].dtype.kind, "f")
        self.assertAlmostEqual(clean.iloc[0]["regular_usd_per_gallon"], 3.0)

    def test_duplicate_state_day_fails(self):
        duplicated = pd.concat(
            [self.gas_raw(), self.gas_raw().iloc[[0]]], ignore_index=True
        )
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            clean_gas_frame(duplicated)

    def test_invalid_gas_price_fails(self):
        raw = self.gas_raw()
        raw.loc[0, "Regular"] = "not a price"
        with self.assertRaisesRegex(ValueError, "price"):
            clean_gas_frame(raw)

    def test_bad_price_before_research_period_is_ignored(self):
        raw = self.gas_raw()
        old_row = {"State": "Michigan", "Date": "2024-12-31", "Regular": "n/a"}
        raw = pd.concat([raw, pd.DataFrame([old_row])], ignore_index=True)
        clean = clean_gas_frame(raw)
        self.assertEqual(len(clean), 10)
        self.assertTrue((clean["date"] >= pd.Timestamp("2025-01-01")).all())

    def test_quarterly_mean_uses_observed_days_only(self):
        # Two observed Q1 days per state, $3 and $5, plus one Q2 day.
        # combine_quarterly() must report a $4.00 Q1 mean, i.e. (3+5)/2,
        # not (3+5)/90. Missing calendar days stay out of the denominator.
        gas = clean_gas_frame(pd.concat([
            self.gas_raw(),
            pd.DataFrame([
                {"State": name, "Date": "2026-04-01", "Regular": "$4.500"}
                for name in STATE_NAMES
            ]),
        ], ignore_index=True))
        ev = pd.DataFrame([
            {"state": code, "quarter": quarter, "ev_share_pct": 4.0,
             "bev_share_pct": 4.0, "phev_share_pct": 0.0,
             "fcev_share_pct": 0.0, "source_url": "https://example.org"}
            for code in STATE_NAMES.values()
            for quarter in ["2026Q1", "2026Q2"]
        ])
        joined = combine_quarterly(gas, ev)
        q1 = joined.loc[joined["quarter"] == "2026Q1"]
        self.assertTrue(
            ((q1["gas_price_quarter_mean_usd"] - 4.0).abs() < 1e-9).all()
        )
        self.assertTrue((q1["days_observed"] == 2).all())
        self.assertTrue((q1["days_missing"] == 88).all())

    def test_ev_reference_values_accepted(self):
        rows = []
        for state in STATE_NAMES.values():
            for quarter in ["2026Q1", "2026Q2"]:
                rows.append({
                    "state": state, "quarter": quarter,
                    "bev_share_pct": 3.0, "phev_share_pct": 1.0,
                    "fcev_share_pct": 0.0, "ev_share_pct": 4.0,
                    "source_url": "https://example.org/illustrative",
                })
        cleaned = clean_ev_frame(pd.DataFrame(rows))
        self.assertEqual(len(cleaned), 10)


class TestStageTwo(unittest.TestCase):
    def test_relative_percent_change(self):
        first = pd.Series([4.0])
        second = pd.Series([5.0])
        self.assertAlmostEqual(percent_change(first, second).iloc[0], 25.0)

    def test_percentage_points_not_relative_percent(self):
        self.assertAlmostEqual(
            percentage_point_change(pd.Series([10.0]), pd.Series([12.0])).iloc[0],
            2.0,
        )

    def test_end_to_end_quarterly_join(self):
        gas_rows, ev_rows = [], []
        for code in STATE_NAMES.values():
            for quarter, day, price, share in [
                ("2026Q1", "2026-01-10", 3.0, 5.0),
                ("2026Q2", "2026-04-10", 4.0, 7.0),
            ]:
                gas_rows.append({
                    "state": code, "quarter": quarter, "date": day,
                    "regular_usd_per_gallon": price,
                })
                ev_rows.append({
                    "state": code, "quarter": quarter, "ev_share_pct": share,
                    "bev_share_pct": share, "phev_share_pct": 0.0,
                    "fcev_share_pct": 0.0, "source_url": "https://example.org",
                })
        joined = combine_quarterly(pd.DataFrame(gas_rows), pd.DataFrame(ev_rows))
        self.assertEqual(len(joined), 10)
        self.assertEqual(int(joined["days_missing"].min()), 89)
        comparisons = summarize_state_changes(joined)
        self.assertEqual(len(comparisons), 5)
        self.assertTrue((comparisons["ev_change_pp"] == 2.0).all())
        self.assertTrue(
            ((comparisons["gas_change_pct"] - 33.333333).abs() < 0.001).all()
        )


if __name__ == "__main__":
    unittest.main()
