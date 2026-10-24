# Observed results — 2026 first half

This file records the actual output of the two-stage analysis after processing
the **MasterGas.csv** source supplied for this study (last observation:
2026-10-23) and the published Q1/Q2 EV market-share references. These are
**results**, not a copy of the underlying third-party daily dataset.

| State | Mean regular gas Q1 | Mean regular gas Q2 | Gas price change | EV share Q1 | EV share Q2 | EV share change |
|---|---:|---:|---:|---:|---:|---:|
| CA | $4.700 | $5.909 | +25.7% | 17.51% | 21.21% | +3.70 pp |
| FL | $3.109 | $4.076 | +31.1% | 7.10% | 9.28% | +2.18 pp |
| IL | $3.219 | $4.556 | +41.5% | 4.82% | 6.63% | +1.81 pp |
| MI | $3.132 | $4.280 | +36.6% | 3.75% | 4.93% | +1.18 pp |
| NY | $3.175 | $4.332 | +36.4% | 4.84% | 6.16% | +1.32 pp |

**Interpretation:** Observed Q2 average regular-gas prices exceeded Q1 averages in all
five states. The share of new registrations using plug-in or fuel-cell electric
powertrains also rose in all five states. The observed increases differ by state.

**Critical caution:** We cannot attribute EV-market changes to gasoline prices.
The state ranking of price changes does not track EV share changes in a simple,
uniform way. An exploratory Spearman rank coefficient from these five changes
is **-0.70**; with just five purposively chosen state aggregates and two
quarters, that number has no causal or reliable inferential interpretation.
It should not be used for forecasting sales, allocating advertising spend,
or describing individual consumers.

**Coverage:** 87/90 Q1 and 88/91 Q2 gasoline days in each state. Missing
observations were not interpolated. Means are based on observed dates only.

The SVG visual [market snapshot](figures/market_snapshot_2026.svg) shows both
metrics without mixing their different units. Re-run the scripts for a
reproducible CSV table and three Python-generated charts.

**Sources:** [Q1 EV report](https://www.autosinnovate.org/posts/papers-reports/Get%20Connected%20EV%20Quarterly%20Report%202026%20Q1.pdf);
[Q2 EV report](https://www.autosinnovate.org/posts/papers-reports/Get%20Connected%20EV%20Quarterly%20Report%202026%20Q2.pdf);
[gasoline data provenance](../data/README.md).
