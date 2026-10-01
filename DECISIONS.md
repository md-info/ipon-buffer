# Decisions

- 2026-09-28: Execute only kickoff M0–M1 this session, following the supplied pack's explicit milestone boundary.
- Use the bundled Python 3.12.14 and project-local virtual environment; the default Windows Python command is a Store alias. A cross-platform Python runner substitutes for unavailable make.
- FastAPI's standard extra supplies the ASGI server and HTTP test client. No additional app framework or UI library is introduced. Node build tooling uses Vite's native JSX transform.
- AI mode remains disabled until M2; neither fixtures nor the foundation screen imply a working model.
- Initialise a repository inside this new project; do not modify parent directories or publish a remote.
- M0 commit was attempted but Git has no author identity configured. Do not invent applicant identity or change global Git settings. Files remain local; milestone evidence is in PROGRESS.md.
- Daily coverage includes both endpoints (at most 90 days); 30-day buffer additions use as_of minus 29 days through as_of. Median gaps remain rational until the planning horizon is rounded upward. P75 uses nearest rank. CV uses population variance with a local 40-digit Decimal context.
- A confirmed daily-essential override takes precedence over observed daily expenses. Explicit zero is preserved and blocks saving when there are no recurring essentials; missing spending never implies surplus.
- Routine reserve covers `horizon` days; separately scheduled bills include both today and the horizon end. This deliberately protects bills due on the expected income date without adding an extra day of routine spending.
- Monthly obligations are anchored to their original day, clamped for short months, and expanded within the horizon. `paid` applies only to the anchored occurrence; monthly cost still contributes to stage targets. Duplicate bill IDs are rejected.
- Unpaid overdue bills block recommendations until reviewed; silently omitting an overdue obligation would understate reserve needs. Expected-income horizons beyond 366 days are rejected for review.
- No selected observed income event means no income-triggered recommendation can be requested. Sparse-but-present income history yields zero with an insufficient-history reason.
- Estimated daily room and ETA are unavailable when history/plan/income-date blockers exist. Zero suggestions remain valid even when the existing buffer exceeds its target or wallet balance is already short.
- English only. Synthetic IDR/VND configuration cases are arithmetic tests, not validated market packs or language support.
- PostCSS patched to 8.5.28 after npm identified a vulnerable version. Frontend audit then reported zero vulnerabilities. One Starlette/AnyIO deprecation warning is upstream and does not fail tests.
2026-09-29: User authorised continued full-plan execution after kickoff. Manual M2-M5 implemented; local model installation deferred, no weights bundled. Full AI validation remains incomplete. PDF generated with ReportLab because bundled PowerPoint authoring module is absent. Actual browser video is sampled at about 1 fps with disclosed cuts.
2026-09-29: User explicitly approved installing Ollama and qwen3:1.7b. Portable runtime and model cache stay outside the source/submission package. Local chat requests disable thinking output and bound context/generation; evaluation records runtime token counts and latency.

## September 30 measured local AI outcome

Approved Ollama/model installation completed. Initial thinking-disabled prompts produced date, currency and recurrence errors. Preserved baseline and v2, then evaluated v3 with thinking enabled, 8192 context and 3000-token limit. This supersedes the earlier thinking-disabled setting. Retain mandatory review and manual fallback; label AI experimental. Do not claim extraction reliability: final case review is 8 satisfactory, 5 rejected, 27 needing correction. No additional model downloaded without discussion of the measured need. Updated real-demo footage proves integration only.

## Conservative validation follow-up

Use the installed model; no additional dependency/download. Add deterministic removal/clearing checks around model output instead of trusting its status or invented fields. Always require an explicit inclusion choice because double counting depends on the confirmed budget. Derive review instructions and disable incomplete confirmation. Retain raw and guarded evaluation outputs. Historical 8/40 and new 11/12 are different sets/contracts, not comparable accuracy percentages. Tests and browser verify the boundaries; keep experimental labeling.
