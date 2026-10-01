# Draft validation follow-up - September 30, 2026

## Outcome

Added conservative source checks around the same qwen3:1.7b model and prompt v3. The model was not retrained or replaced. **General extraction reliability remains unproven; AI stays experimental.**

The guards only remove or clear model suggestions. They do not invent replacement amounts, dates or obligations. They are a deliberately limited English implementation, not a general semantic verifier.

- Unsupported request patterns (including known paid/cancel/transfer and foreign-currency wording) produce no draft changes.
- Amounts need a matching number in the source; ranges and negative signs trigger clarification. ISO dates are excluded from sign detection.
- Dates need one consistent supported anchor: today, tomorrow, end of month, ISO date, or English month-name date. Missing, conflicting, past or ambiguous weekday dates are cleared.
- Recurrence needs explicit matching wording. Daily-budget inclusion always starts unselected because it must agree with the user's confirmed budget.
- Income-like excerpts cannot become bills; income dates require income wording and a supported date anchor.
- Review status and instructions are generated from the surviving fields. The confirmation button stays disabled while required fields are missing.

## Evidence

**Saved-output replay, not new inference:** all 35 previously accepted proposals in ai_run_v3.json were replayed. The other five previous rejections remain recorded. The guards removed six candidates and three income dates; resulting statuses were 26 needs-clarification, 7 unsupported and 2 ready-for-review. These counts are not accuracy scores. See ai_grounding_replay.json; reproduce with scripts/replay_ai_grounding.py.

**New live inference:** 12 synthetic exploratory examples were specified in evaluation/ai_grounding_cases.json before running. All produced schema-valid adapter responses. Codex inspection found 11 matched the intended reviewed behavior; one required extra manual completion. In ground-08, the model returned February 28 as the end of February 2028; validation cleared the wrong date rather than substituting February 29. Median observed latency was 4.75 seconds. Raw and guarded proposals are both retained in ai_grounding_live.json. The replay script confirms current guard code reproduces all 12 saved guarded results.

This is a different, small development set with a revised review contract (inclusion always manual). **11/12 must not be compared directly with the earlier 8/40 as a model-accuracy improvement.** No independent assessor, held-out benchmark or user study was conducted.

**Browser:** actual local AI drafted the PHP 300 school expense due September 29. Recurrence and inclusion both started unselected. Confirmation was disabled initially and after recurrence alone, then enabled after choosing inclusion. Before confirmation, reserve 1760, suggested deposit 120, wallet 2000 and buffer 500 were unchanged. After confirmation, reserve 2090 and suggestion 0, with balances unchanged. The 162-second video was refreshed with this real journey.

**Tests:** 24 new guard tests; 148 backend tests plus 4 frontend tests pass. Ruff, TypeScript and production build passed. Tests include unsupported requests, sign loss, clipped excerpts, date ambiguity/conflict, year/leap boundaries, ISO-date sign handling, income misclassification, negated recurrence and mandatory inclusion choice. Unit responses are explicitly fixtures, separate from real inference.

## Remaining limits

Keyword and numeric matching cannot prove meaning, ownership, or which number/date belongs to which bill. Supported language is intentionally narrow and can reject useful phrasing. Negation, corrections, multi-bill statements, numeric dates, currency wording and mixed income/expense clauses need broader evaluation. Date validation can clear a correct field when its evidence is outside the model's excerpt. Review does not guarantee users catch all errors. No live funds, financial integrations or production deployment are involved.

Before expanding beyond the synthetic demo: evaluate a stronger local model, add independently reviewed cases covering these limits, test whether users understand cleared fields, and agree acceptance criteria in advance. No extra runtime/model was downloaded for this change.
