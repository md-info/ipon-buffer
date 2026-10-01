# Ipon Buffer

A functioning emergency-savings prototype for irregular income. **Synthetic data, mock wallet, no real funds.**

Manual flow is implemented and browser-tested: consent, confirmed bills/income date, recommendations, deposits, withdrawals, separate emergency payments, optional refill estimate, revocation, deletion and audit verification. Actual local inference is demonstrated with Ollama 0.34.4 and qwen3:1.7b. **This model failed the quality gate**: it can invent or misclassify fields. Use only as an experimental, reviewed drafting aid. See reports/ai_evaluation.md and the new source-check evaluation in reports/ai_grounding_evaluation.md. The demo uses a fixed September 28, 2026 scenario.

## Run locally

Requires Python 3.12 and Node 22.12+ with npm. From this directory:

```sh
python scripts/tasks.py setup
python scripts/tasks.py check
python scripts/tasks.py demo
```

Open http://127.0.0.1:5173 and stop with Ctrl+C. On Windows, use py -3.12 for setup where available. After setup, .venv\Scripts\python.exe scripts/tasks.py demo also works. Make targets delegate to the same runner. Setup downloads dependencies; the installed manual application requires no external services.

Use the virtual-environment Python for scripts/tasks.py sim and scripts/engine_demo.py. Reports go to reports/. All money is integer centavos. Recommendations depend on incomplete assumptions and are not guarantees.

## Deliverables

- submission/Ipon_Buffer_Pitch.pdf: 10-slide draft, including visibly missing applicant details.
- submission/Ipon_Buffer_Demo.mp4: 162-second captioned actual-browser recording, including real AI drafting and confirmation.
- submission/build_deck.py: editable PDF source; artifact tooling requires ReportLab and Arial.
- submission/SUBMISSION_CHECKLIST.md: remaining model-quality/applicant/portal requirements.
- reports/simulation.md: synthetic comparison, including unfavourable results.
- docs/LOCAL_MODEL.md: local inference setup. Weights were downloaded separately on the development machine and are not bundled.

Run `.venv\Scripts\python.exe scripts/demo_local_ai.py` for the installed local AI demo. Integration and evaluation are complete; reliable AI extraction remains **INCOMPLETE**. These are local review artifacts, not public judge-accessible links. Nothing has been submitted or deployed.

See PROGRESS.md, CLAIMS.md, docs/ARCHITECTURE.md and docs/PRIVACY_SECURITY.md. API schemas are at http://127.0.0.1:8000/docs while running, and exported in docs/openapi.json.


Final handoff: see HANDOFF.md and submission/SUBMISSION_DRAFT.md. Applicant details intentionally remain blank. Public portal requirements were checked September 30; see docs/REQUIREMENTS.md. Development is closed for this prototype scope; applicant submission actions remain.
