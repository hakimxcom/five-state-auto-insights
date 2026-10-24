# Data instructions and provenance

This project uses two sources with different observation frequencies.

## 1. Gasoline prices: daily input (you download)

Public upstream collection: [jgreathouse9/AAAGas — Prices/MasterGas.csv](https://github.com/jgreathouse9/AAAGas/blob/main/Prices/MasterGas.csv)

Download the raw file and save it **locally** as:

    data/raw/MasterGas.csv

This directory is excluded by .gitignore. The project does not redistribute the underlying price observations or claim an AAA license.

Columns needed: State, Date, Regular.
- State: full names such as Michigan.
- Date: YYYY-MM-DD.
- Regular: text dollar price such as $3.459.
- Mid-Grade, Premium and Diesel may be present but are not used.

The supplied file examined on 2026-10-24 contained daily rows from 2024-11-16 to 2026-10-23. Our code keeps January 2025 onward, for all five selected states. During 2026-01-01 through 2026-10-23, each state had 289 of 296 available calendar dates; seven dates were absent in all five states.

**Why not publish the original file?** The underlying daily prices appear to derive from AAA. Availability on an open GitHub repository does not itself grant unrestricted redistribution rights. Fetch your own copy and honor the upstream source's terms.

## 2. EV registrations: quarterly reference (included)

File: [reference/ev_market_share_2026.csv](reference/ev_market_share_2026.csv)

The ten transcribed state figures come from tables in:
- [Alliance for Automotive Innovation, 2026 Q1](https://www.autosinnovate.org/posts/papers-reports/Get%20Connected%20EV%20Quarterly%20Report%202026%20Q1.pdf)
- [Alliance for Automotive Innovation, 2026 Q2](https://www.autosinnovate.org/posts/papers-reports/Get%20Connected%20EV%20Quarterly%20Report%202026%20Q2.pdf)

EV share = (BEV + PHEV + FCEV) among **new light-duty vehicle registrations**, expressed as percentage of total new registrations. These are reported aggregate shares; there are no individual registration records in this project. Ordinary hybrid-electric vehicles (HEVs) are excluded. Powertrain components and total shares may differ by 0.01 percentage point because of source rounding.

## 3. Generated data and limitations

Run the three Stage I programs in order; they create:
- processed/gas_daily.csv — a cleaned observation for each available state/date.
- processed/ev_quarterly.csv — validated quarterly market shares.
- processed/market_quarterly.csv — the 10-row state/quarter join.
- ../outputs/stage_1_data_quality.md — exact missing-date and coverage audit.

No missing gasoline days are filled. If a future upstream file adds or changes rows, re-run Stage I and note the retrieval date in any publication. A quarter's mean gas price represents **observed days only**.

Market share and gas price are at distinct units and geographic aggregation levels. No insurance-cost, vehicle make/model, financing/lease, income, individual purchases or consumer survey variables are available in this source pair. Those questions need a separate study.
