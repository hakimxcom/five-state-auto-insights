# Research note: What can five states tell an automaker?

**Sam Hakim | October 2026 | Consumer insights / market research portfolio**

## Executive take

The U.S. EV market is not one national market. In the first two quarters of 2026, public industry data show materially different levels of EV participation in new light-duty registrations in the five states examined.

California's EV share rose from 17.51% in Q1 to 21.21% in Q2; Michigan rose from 3.75% to 4.93%. Florida, New York and Illinois also showed quarter-over-quarter EV-share gains. The **difference in levels** is at least as strategically relevant as the change: an automaker should not apply a single national EV demand assumption to every state.

| State | Q1 EV share | Q2 EV share | Q2-Q1 |
|---|---:|---:|---:|
| CA | 17.51% | 21.21% | +3.70 percentage points |
| FL | 7.10% | 9.28% | +2.18 percentage points |
| IL | 4.82% | 6.63% | +1.81 percentage points |
| MI | 3.75% | 4.93% | +1.18 percentage points |
| NY | 4.84% | 6.16% | +1.32 percentage points |

*Source: Alliance for Automotive Innovation, 2026 Q1 and Q2 Get Connected EV reports. EV here is plug-in/fuel-cell powertrains, excluding ordinary hybrids.*

## How gasoline enters the question

We also have daily regular gasoline price observations. We aggregate those prices into state-level Q1/Q2 averages, calculate relative changes, and compare them descriptively with EV share changes. This is a practical first step toward studying potential price sensitivity.

But a gasoline-price shock and an EV-market-share change occurring together **do not establish causality**. Policy, vehicle availability, charging access, financing and delayed decisions can change both the level and timing of registrations. Nor can we tell whether the buyers who registered vehicles personally experienced the average state gasoline price used here.

## What I would recommend to a GM or Hyundai research team

1. **Segment research by geography.** Consumer propositions and competitive benchmarks should start from the very different observed EV shares across these states.
2. **Separate EV from conventional hybrid.** A hybrid buyer who does not plug in may respond to affordability and fueling convenience differently from a BEV buyer; the current public EV table does not measure this behavior.
3. **Use gasoline changes to generate hypotheses, not conclusions.** Follow up with actual shopping-intent, consideration, incentives, price and transaction data before reallocating media or inventory.
4. **Collect the missing buyer variables.** Model/trim, transaction price, lease versus finance, monthly payment, household context and charging access would turn a market-monitoring chart into a stronger consumer insight.

## What this project demonstrates

Source discovery and provenance; practical CSV ingestion and cleaning; one-to-one joins at the correct level; documented missing-data audits; transparent formulas; a modest statistical comparison; charts tailored to a business reader; and careful interpretation of what the data **cannot** tell us.

The code lives in Stage I and Stage II in this repository. Every calculation is written for someone with average Python literacy to review and reproduce.

**Sources:** [2026 Q1 EV report](https://www.autosinnovate.org/posts/papers-reports/Get%20Connected%20EV%20Quarterly%20Report%202026%20Q1.pdf) · [2026 Q2 EV report](https://www.autosinnovate.org/posts/papers-reports/Get%20Connected%20EV%20Quarterly%20Report%202026%20Q2.pdf) · [Daily gas price source instructions](../data/README.md).
