# AI UX evaluation — INCOMPLETE

No real model is configured. Real-model cases run: 0. Model identifier, schema accuracy, field accuracy, ambiguity handling, latency, usage and failure rate: unavailable. Unit-test fixtures are not inference evidence.

Implemented: local-only adapter, bounded JSON schema, exact money conversion, currency/date/excerpt validation, consent, expiring/versioned draft, explicit reviewed apply, cancellation/revocation invalidation, and manual fallback. Browser testing confirmed unavailable inference does not disable manual entry. API fixtures confirmed a proposed school bill does not alter the plan until reviewed apply, then the deterministic suggestion becomes zero. No fixture response is shown as live AI in the demo recording.

The versioned 40-case synthetic corpus is in evaluation/ai_cases.json. The separate runner writes per-case proposals, latency, schema outcome and review flags to reports/ai_run.json only when explicitly run. Human field/ambiguity review remains required. Release gate still open: choose/install a model, evaluate the corpus, correct failures, and record a reviewed real-model golden journey plus differently worded input. Do not label this build a completed AI demonstration.
