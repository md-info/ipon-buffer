# Ipon Buffer

A functioning emergency-savings prototype for irregular income. **Synthetic data, mock wallet, no real funds.**

The current demo combines an emergency buffer banner with a photo-first local price feed. Customers can share reports, thank contributors and independently confirm prices. The savings engine uses reviewed expenses to recommend exact-centavo contributions. Deposits, withdrawals and AI-proposed plan changes require explicit confirmation. Merchant offers, cashback and cashback-to-buffer redemption are simulated.

Demo login enables the synthetic planning and local-AI options automatically; the old permission-checkbox setup screen has been removed. Analysis can still be revoked from Permissions. The scenario uses a fixed September 28, 2026 reference date. No real funds, live wallet integration or retailer partnership is involved.

Actual local inference has been demonstrated using Ollama 0.34.4 and qwen3:1.7b. **The model failed the development quality gate** and can invent or misclassify fields. Treat it as an experimental drafting aid, review every field, or use the manual form. See reports/ai_evaluation.md and reports/ai_grounding_evaluation.md.

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

Run `.venv\Scripts\python.exe scripts/demo_local_ai.py` for the installed local AI demo. Integration and evaluation are complete; reliable AI extraction remains **INCOMPLETE**. The local app is not publicly hosted. The repository is public and linked from the existing BuilderBase submission.

See PROGRESS.md, CLAIMS.md, docs/ARCHITECTURE.md and docs/PRIVACY_SECURITY.md. API schemas are at http://127.0.0.1:8000/docs while running, and exported in docs/openapi.json.


## Current app, Android and presentations

Both / and /nearby open the same unified Ipon Buffer app. After logging in, the feed appears below the buffer banner. Open Edit savings plan to review expenses or use the local AI assistant. Open View buffer details to review and confirm a suggested deposit. A completed deposit stays visible until you explicitly review and save another plan.

The Android app uses a native Java WebView shell with the React/TypeScript UI. The backend, SQLite database and local model run on the development computer. It is not React Native, a standalone offline app, or a production wallet SDK. See [Android instructions](android/README.md). A development-signed APK is included at [android/Ipon-Buffer-demo.apk](android/Ipon-Buffer-demo.apk); build sources and scripts are included, while signing keys and SDK installations are excluded.

Current presentation materials are in submission/november-pitch:

- Ipon-Buffer-Visual-Pitch.pptx: 12-slide stakeholder presentation with Android views and explanatory illustrations.
- Presentation-script.md: accompanying presentation script.
- android-screens/: actual screenshots from a fresh Pixel 9 Android 15 emulator.
- Ipon-Buffer-*-Transparent.png: generated phone mockups based on supplied app screenshots.

The twelve-slide stakeholder deck is separate from the historical challenge PDF (at most ten slides). The older video and challenge draft describe an earlier prototype and must not be presented as a recording of every current feature.

The submitted BuilderBase entry already links to this repository. On November 3, 2026, the signed-in portal showed Submitted / submissions closed. Updating GitHub changes the linked repository, not the submitted form text or attachments. See docs/REQUIREMENTS.md for current portal observations.

## Modular wallet feature

A host can embed the community feature as a React component or build the mount/update/unmount module with `npm run build:nearby` from web. See docs/NEARBY_INTEGRATION.md for the host contract. This is an integration starting point; production identity, settlement, permissions and wallet adapters still require partner engineering.

Populate the sample community feed with `.venv\Scripts\python.exe scripts/seed_nearby.py`. Six fictional reports include credited stock photos stored in web/public/demo. Sample chains/branches, prices, authors and reactions are illustrative; no retailer affiliation is claimed. Photos are bundled for offline use after setup. Existing reports are preserved.

Merchant rewards prototype: open Rewards & partners from the Buffer header. Includes a capped fictional grocery offer, simulated purchases, cashback receipts, explicit cashback-to-buffer redemption and partner campaign tools. Community points stay nonredeemable. See docs/REWARDS.md for limits and integration requirements.

## Copyright and licence

Copyright © 2026 Michel Deosaran (md-info). All rights reserved in original protectable contributions owned by the author. This is proprietary software, not an open-source release. See [LICENSE](LICENSE), [COPYRIGHT.md](COPYRIGHT.md), and [third-party notices](THIRD_PARTY_NOTICES.md). Public access does not grant commercial reuse rights.
