# Ipon Buffer project instructions

## Objective
Build a functional, honest emergency-savings prototype and its technical-format submission package for ASEAN Financial Health Challenge Track 02. Required deliverables: functioning prototype, pitch deck PDF <=10 slides, demo video <=180 seconds showing the working prototype. Optional hosted link and code publication are not prerequisites.

## Priorities
1. Complete demonstrable user journey and correct financial state changes.
2. Accurate claims, readable deck, and real demo recording.
3. Reproducibility, validation readiness, and credible partner economics.
4. Optional breadth only after required deliverables are complete.
No numerical judging weights have been verified.

## Non-negotiables
- Synthetic data and mock partner only. No live funds, secrets, or personal data.
- The financial engine, manual forms, and mock wallet work offline after setup. AI assistance may call a configured model through the backend with explicit separate consent, or use an available local model. Never claim the hosted AI path works offline. No remote fonts or analytics.
- AI produces proposed plan fields only. User review and confirmation are mandatory before any plan update. AI has no access to transfer tools, credentials, raw transaction history, or ledger writes. The engine computes all monetary recommendations and explanations.
- An actual model-backed demonstration is required to claim working AI. Recorded fixtures support tests but must be labelled fixtures; a parser or mocked response is not a completed AI integration. If model access is unavailable, preserve manual functionality and report AI as incomplete.
- Initial setup may require network access; never promise a fresh dependency install works offline.
- Money is integer minor units with ISO currency metadata. Use Decimal or integer ratios for rates and intermediate financial calculations, with explicit rounding. No binary floating-point money calculations.
- Never guarantee future affordability. User-confirmed obligations and observed income are incomplete estimates.
- No invented interviews, integrations, legal compliance, traction, effectiveness, team credentials, or market statistics.
- Historical comparisons are synthetic tests, not causal or real-world evidence.
- No automatic transfer. Confirmation uses a freshly validated recommendation.
- Emergency withdrawals remain available in the mock without transaction-analysis consent. Authentication and explicit withdrawal authorisation are separate from optional analysis consent.
- No unsolicited account creation, publication, deployment, application submission, or external messaging.
- Keep the approved stack. Use standard-library modules freely. Ask before adding third-party dependencies; first attempt a solution within the approved stack.

## Stack
Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2/SQLite, PyYAML; pytest, hypothesis, ruff; React 18, TypeScript, Vite, Tailwind, vitest. Optional simulation dependencies: numpy, matplotlib. Use standard-library Decimal for exact financial arithmetic. Dependency versions must be pinned compatibly. Put model access behind a small provider-neutral backend adapter, using standard-library HTTP where practical. Select a real available model at implementation time and consult its current primary documentation; do not invent model names, pricing, retention guarantees, or capabilities. Credentials are supplied through server-side environment variables, never committed or sent to the browser. Do not purchase access or create provider accounts without authorisation.

## Layout
backend/app/{engine,consent,adapters,api,sandbox,assistant}/
backend/config/{rules.yaml,markets/PH.yaml}
backend/tests/
web/src/{pages,components,i18n}/
simulation/
docs/
reports/
submission/
scripts/
README.md
PROGRESS.md
DECISIONS.md
CLAIMS.md
Makefile

## Working agreement
Inspect local instructions and existing work first. Preserve user changes. Work in milestones, update PROGRESS.md, and run applicable checks before declaring a milestone complete. Provide an equivalent cross-platform Python task runner if make is unavailable. Keep setup, check, demo, and sim commands consistent between both interfaces.
Log routine ambiguities and choices in DECISIONS.md and continue. Ask only for missing information that actually blocks the next required action. Do not fabricate applicant details to unblock submission work.
When a Git repository exists and commits are supported, commit each completed milestone. If unavailable, report that limitation without blocking useful work or modifying unrelated repositories.
Test behaviours and financial invariants, not merely implementation shape. Never tune simulation parameters to improve comparative results.
Keep a claims ledger: claim, source/artifact, evidence type, limitation, approved wording. Separate implemented behaviour, synthetic observations, hypotheses, and future work.
