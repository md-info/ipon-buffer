# Local AI evaluation - September 30, 2026

Historical raw-model evaluation, before the additional source checks. See ai_grounding_evaluation.md for the subsequent guarded-workflow results; the original findings below are retained.

**Decision: integration demonstrated; model quality gate NOT PASSED. Experimental synthetic-demo feature only.**

Ollama 0.34.4; qwen3:1.7b (manifest reports 2.0B, Q4_K_M); RTX 2060, approximately 24 GiB system RAM. Exact model digest and size are in local_model_manifest.json. No model weights are bundled.

| Run | Adapter accepted | Median seconds | p95 seconds | Output tokens |
|---|---:|---:|---:|---:|
| Prompt 1 | 23/40 | 1.48 | 2.16 | 6512 |
| Prompt 2 | 36/40 | 1.39 | 1.86 | 5901 |
| Prompt 3 | 35/40 | 5.94 | 14.44 | 27661 |

Baseline used thinking off, 4096 context, 1500 generated-token limit. V2 tightened instructions and currency schema. Final v3 enables thinking, 8192 context, 3000-token limit and removes an example amount that leaked into drafts. Temperature 0. Per-case prompt/output counts and timing are in each raw JSON; thinking tokens are included in runtime output counts. Latencies are observed on this machine, with occasional additional demo/diagnostic requests during evaluation; they are not isolated benchmarks. No paid model API was used; electricity/hardware cost was not measured.

The initial cold-start run was interrupted after two 45-second timeouts and six further cases (case 03 failed, case 04 passed, 05-08 failed). Its partial proposals were not saved. All three complete runs are retained. Warm responses do not establish reliable cold-start latency.

**Final v3 review: 8/40 meet the conservative whole-case expectation, 5/40 are rejected by the adapter, and 27/40 need correction.** This is Codex inspection, not a human study. Acceptance by the schema is NOT extraction accuracy. The same development corpus informed prompt revisions; there is no held-out accuracy claim. No success rate for real customers is established.

Frequent errors: assumed recurrence, income turned into bills, invented income dates, paid/cancelled bills proposed again, ambiguous date guesses and sign loss. Reasoning mode did not resolve these. Invalid amounts/dates and incomplete output fail closed, but semantically wrong valid fields can still reach review. Mandatory confirmation reduces autonomous risk; it does not guarantee the user catches an error.

The browser golden example used actual inference: PHP 300 / 2026-09-29, with a suggested one-time recurrence that the tester explicitly reviewed and budget inclusion completed as No. Before confirmation, wallet 2000, buffer 500, reserve 1760 and suggestion 120 remained unchanged. After confirmation, reserve 2090 and suggestion 0; wallet/buffer unchanged. Existing lifecycle tests cover cancellation/revocation/version changes; they are fixture tests, not model-quality evidence.

Recommended next quality work: evaluate a stronger local model on a separate held-out set; add semantic grounding checks and explicit review of recurrence/income; repeat user-facing failure tests before any deployment. Do not present this model as reliable financial understanding.

| Case | Verdict | Observation |
|---|---|---|
| case-01 | needs_correction | Invented one_off recurrence. |
| case-02 | needs_correction | Invented one_off recurrence. |
| case-03 | meets_review_expectation | Complete explicit fields matched. |
| case-04 | needs_correction | Invented recurrence; ready status despite missing inclusion. |
| case-05 | needs_correction | Core fields correct; missing-field status and clarification wrong. |
| case-06 | rejected_by_adapter | Rejected fractional centavo; safe fallback, not successful clarification. |
| case-07 | meets_review_expectation | Monthly amount correct; due date left for confirmation as allowed. |
| case-08 | needs_correction | Invented date for ambiguous next Friday (also not a Friday). |
| case-09 | needs_correction | Correct amount/date; invented monthly recurrence. |
| case-10 | needs_correction | Income incorrectly duplicated as expense. |
| case-11 | needs_correction | Income incorrectly made expense; income date omitted. |
| case-12 | needs_correction | Already-paid expense incorrectly proposed as new bill. |
| case-13 | meets_review_expectation | No new bill; unsupported response. |
| case-14 | meets_review_expectation | Range kept null; clarification requested. |
| case-15 | meets_review_expectation | USD rejected without PHP conversion. |
| case-16 | rejected_by_adapter | Token limit reached; incomplete response rejected. |
| case-17 | meets_review_expectation | Missing amount kept null; tomorrow correct. |
| case-18 | needs_correction | Missing date invented as today. |
| case-19 | needs_correction | Inclusion correct; recurrence invented. |
| case-20 | needs_correction | Inclusion correct; recurrence invented. |
| case-21 | needs_correction | Corrected amount extracted but income date invented. |
| case-22 | needs_correction | Cancellation incorrectly proposed as new bill. |
| case-23 | needs_correction | Unsupported/no fields, but explanation incorrectly says text absent. |
| case-24 | needs_correction | Tool request incorrectly proposed as bill; no tool was available or invoked. |
| case-25 | meets_review_expectation | No changes proposed for instruction-like text. |
| case-26 | needs_correction | Two amounts/dates correct; rent recurrence invented and ready status incorrect. |
| case-27 | needs_correction | Core fields correct; asks about income although none is present. |
| case-28 | needs_correction | Monthly bill correct; income date invented. |
| case-29 | needs_correction | Bill correct; income date invented. |
| case-30 | needs_correction | Date correct; recurrence invented. |
| case-31 | needs_correction | Year boundary correct; recurrence invented. |
| case-32 | rejected_by_adapter | Invalid calendar date rejected rather than clarified. |
| case-33 | needs_correction | Leap-day date correct; recurrence invented. |
| case-34 | needs_correction | Income also incorrectly proposed as expense. |
| case-35 | meets_review_expectation | Tentative date left null; clarification requested. |
| case-36 | rejected_by_adapter | Nonpositive amount rejected rather than clarified. |
| case-37 | needs_correction | Negative amount incorrectly changed to positive. |
| case-38 | needs_correction | Decimal normalised correctly; recurrence invented. |
| case-39 | rejected_by_adapter | Out-of-range amount rejected. |
| case-40 | needs_correction | Expense extracted despite malformed JSON; recurrence invented. |
