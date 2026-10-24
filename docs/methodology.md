# Methodology 

The goal is to explain **what the software calculates and why**.

## Research design

**Geography:** CA, MI, FL, NY, IL. California offers a leading EV market; Michigan is central to the auto industry; Florida, New York and Illinois add different regional profiles. This is a purposive comparison, **not** a statistically representative selection of all U.S. states.

**Time:** regular-grade daily state-average gasoline prices from January 2025 onward (Stage I keeps 2025 as context; the analysis itself uses 2026 only); 2026 Q1 and Q2 state-level EV shares of new registrations. The core combined dataset has 10 observations (5 states × 2 quarters).

**Question:** Did these two measures move over the same period, and how did the patterns differ by state?

**Not claimed:** gas prices caused a change in EV purchases, or that aggregate trends reveal individual consumers' priorities. Vehicle transactions reflect many factors and decisions can lag price movements by weeks or months.

## Stage I: data preparation

### 1. Import and filter: clean_gas.py

- `pandas.read_csv()`: read a table directly from the downloaded original.
- `DataFrame.loc[]`: keep five named states and the fields State, Date, Regular.
- `pandas.to_datetime(..., format='%Y-%m-%d')`: parse dates reproducibly.
- `Series.str.replace()` and `pandas.to_numeric()`: convert '$3.459' text to 3.459 numeric.
- `DataFrame.duplicated()`: reject duplicate state/date observations.
- Preserve unavailable dates as missing. No forward-filling, interpolation or unlabelled estimates.

### 2. Inspect quarterly EV shares: prepare_ev.py

- Source CSV contains **published** state-level BEV/PHEV/FCEV and total EV percentages, 2026 Q1/Q2.
- Reject out-of-range shares, missing state/quarter combinations, repeated keys, and a discrepancy greater than 0.03 percentage points between component shares and the independently rounded total.
- New-registration *share* is not the stock of EVs in operation and not a conventional-hybrid share.

### 3. Quarterly join: combine_audit.py

Gasoline is measured daily while EV registrations are summarized by quarter. To avoid *pseudo-replication*, average gasoline first at the SAME state-quarter level.

**Equation 1 — observed daily gasoline mean within quarter:**

```text
MeanGas(state, quarter) = SUM(available daily price USD/gal)
                          / COUNT(available daily dates)
```

The denominator is observed dates, not total calendar dates; coverage is recorded separately. For Jan–Mar 2026 there are 90 expected days, and for Apr–Jun 2026 there are 91.

`groupby(['state','quarter']).agg(...)` computes the mean and count. `merge(on=['state','quarter'], validate='one_to_one')` joins the 10 gas summaries to the 10 EV observations. If there is no match, the pipeline fails rather than silently deleting it.

## Stage II: analysis

### 4. Descriptive state comparison: describe.py

**Equation 2 — relative change in gasoline price:**

```text
GasChangePct = 100 × (MeanGas_Q2 − MeanGas_Q1) / MeanGas_Q1
```

This is a percent change **relative to the Q1 dollar-per-gallon baseline**.

**Equation 3 — EV registration share change in percentage points:**

```text
EVChangePP = EVShare_Q2 − EVShare_Q1
```

Example: a share rising from 5% to 7% equals **+2 percentage points**, not +2% (relative increase would be +40%). Using the correct unit is central to defensible market research.

**Equation 4 — optional Spearman rank correlation:**

```text
rho = Pearson correlation between ranks(GasChangePct)
      and ranks(EVChangePP) across the five states
```

`scipy.stats.spearmanr()` supplies this single descriptive rank coefficient. With just five state aggregates, it is highly fragile: we deliberately do **not** report a p-value, conduct significance claims, or estimate causal impact. Association can have confounding variables and ecological bias.

### 5. Three charts: charts.py

- `matplotlib.pyplot.plot()`: five daily gasoline price lines for 2026. Displays observed values; absent dates remain absent.
- `matplotlib.pyplot.bar()`: grouped Q1/Q2 reported EV market-share bars, five states.
- `matplotlib.pyplot.scatter()` and `Axes.annotate()`: one labeled dot per state (gas percent change on x, EV percentage-point change on y).
- `Figure.savefig()`: save readable 175-dpi PNG output. No fitted trendline or regression is implied.

`numpy.arange()` supplies positions for the grouped bars. Other chart styling functions are cosmetic.

## Reproducibility and quality rules

1. Raw daily price records are never altered in place; Stage I produces a new file.
2. State/date and state/quarter uniqueness are explicitly checked.
3. No missing days are imputed. Stage I writes missing-date audit.
4. One row per state/quarter after joining; one row per state after comparing.
5. `tests/test_pipeline.py` exercises a few small **synthetic** examples (including bad prices, duplicates, the 3→4 dollar quarterly change and 5%→7% EV percentage-point difference). Tests are separate from real observations.
6. Keep the provenance links attached to each EV row; date-stamp the daily file retrieval when preparing external reports.

## Limitations and next research steps

Data from just five regions and two quarters cannot explain why a specific buyer picked an EV, ICE or hybrid. Gas prices are not necessarily exogenous: seasonality, taxes, refinery conditions, oil supply, geography and geopolitical events can all influence price movements. EV registrations are shaped by incentives, available inventory, model offerings, consumer incomes, charging access, business/fleet registrations, finance rates and lagged buying decisions.

A rigorous **second project**, after securing comparable data, could examine a longer monthly panel, distinguish BEV/PHEV/HEV, include vehicle class and price, add incentives and income, and test lagged specifications with sensitivity checks. None of that is represented as completed work in this repository.
