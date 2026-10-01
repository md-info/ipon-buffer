# Verification receipt — 29 September 2026

Command: .venv\Scripts\python.exe scripts/tasks.py check

Ruff lint passed; 38 Python files formatted; 122 pytest cases passed in 4.87 seconds; 4 Vitest cases passed; TypeScript noEmit and Vite production build passed. JS 165.91 kB / 53.19 kB gzip. One upstream Starlette/AnyIO deprecation warning.

Simulation completed Sep 28: 1,350 household-strategy-scenario rows, each 180 days. Daily conservation assertions passed. Unit tests independently checked numeric determinism and shared exogenous paths for a sample, not a full-cohort byte-hash rerun.

PDF: ten pages generated with ReportLab, all rendered with Poppler and individually inspected. Editable source retained. PPTX export unavailable because the configured runtime lacks @oai/artifact-tool.

Video: 155 seconds, H.264 MP4, captions, no audio. About 1 captured frame/second encoded at 25 fps. Whole-stream FFmpeg decode succeeded. Metadata in submission/video_metadata.json. Visual sampling and playback checks are documented separately; no continuous-capture claim.

Existing-environment setup/launch checked. A fresh scratch environment on this machine installed successfully, reported zero npm vulnerabilities, and passed the same 122 backend / 4 frontend tests plus lint, types and build. Logs: clean_setup.txt and clean_check.txt. A different-machine install and real-model operation remain unverified. Portal fetch Sep 29 remained inaccessible.


The browser player reached 155/155 seconds with ended=true and no media error. Sampled encoded frames were visually inspected for captions and correct balances.

September 30 final integration checks: 124 backend and 4 frontend tests passed, plus Ruff, TypeScript and Vite. Live AI tested separately; semantic quality failed despite valid-schema responses. See ai_evaluation.md.

Draft-validation follow-up: 148 backend + 4 frontend tests, Ruff, TypeScript and Vite passed. Current guards replay all 12 live saved results identically. Actual browser required recurrence and inclusion before confirmation.
