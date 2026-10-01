# Synthetic comparison

Seed 20260928; 90 synthetic households (30 per pattern); 180 days after 30 days of history.
No real users, behavioural benefit, model extraction, or causal impact was measured.

| Scenario | Strategy | Essential shortfall days | Funded / shocks | Unmet shock PHP | Unmet discretionary PHP | Median household buffer days |
|---|---|---:|---:|---:|---:|---:|
| base | none | 1437 | 88 / 281 | 259313.00 | 98693.00 | 0.00 |
| base | fixed_10pct | 1206 | 95 / 281 | 239750.50 | 195115.10 | 1.33 |
| base | ipon | 1248 | 95 / 281 | 242085.00 | 173017.00 | 1.27 |
| delayed_income | none | 1450 | 89 / 281 | 256845.00 | 97888.00 | 0.00 |
| delayed_income | fixed_10pct | 1217 | 95 / 281 | 236808.60 | 192634.20 | 1.47 |
| delayed_income | ipon | 1254 | 96 / 281 | 238792.00 | 173624.00 | 1.40 |
| missing_bill | none | 1437 | 88 / 281 | 259313.00 | 98693.00 | 0.00 |
| missing_bill | fixed_10pct | 1206 | 95 / 281 | 239750.50 | 195115.10 | 1.33 |
| missing_bill | ipon | 1235 | 96 / 281 | 241039.00 | 176557.00 | 1.40 |
| higher_essentials | none | 3142 | 73 / 281 | 299232.00 | 178086.00 | 0.00 |
| higher_essentials | fixed_10pct | 2999 | 77 / 281 | 294338.90 | 234066.20 | 0.54 |
| higher_essentials | ipon | 2969 | 77 / 281 | 293321.00 | 228124.00 | 0.47 |
| larger_shocks | none | 1579 | 26 / 281 | 706726.00 | 106385.00 | 0.00 |
| larger_shocks | fixed_10pct | 1367 | 31 / 281 | 685933.00 | 198648.00 | 1.12 |
| larger_shocks | ipon | 1414 | 31 / 281 | 687700.00 | 176567.00 | 1.07 |

See simulation/ASSUMPTIONS.md for frozen rules, measurement definitions, and limitations.
All ledger reconciliations are zero. Raw rows include pattern, final liquid funds, stage attainment, and unavailable zero-shock rates.
Saving moves money between accounts; it creates no income. Discretionary demand is recorded even when unpaid.
Higher liquid balances can reflect suppressed discretionary spending, not greater resources or welfare.
