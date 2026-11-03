# Progress - September 30, 2026

Local AI integration and evidence update completed. **AI quality gate FAILED; reliable extraction remains incomplete.** Nothing submitted or deployed.

- Existing engine, manual journey, consent, mock ledger, synthetic analysis and proposal documents retained.
- Installed user-approved portable Ollama 0.34.4 and qwen3:1.7b outside the project. Verified runtime archive SHA-256; model manifest retained. Loopback only, cloud disabled.
- Three complete 40-case real-model development evaluations retained. Final reasoning-mode v3: 35/40 adapter accepted; conservative Codex review found 8/40 satisfactory, 5 rejected, 27 requiring correction. No independent/human accuracy claim. Median 5.94s, p95 14.44s; cold-start timeouts disclosed.
- Actual browser journey verified: drafting leaves balances and recommendation unchanged; review and confirmation of PHP 300 school expense changes suggestion 120 to 0. AI cannot transfer money.
- Added local AI launcher, completion/truncation regression coverage, measured runtime metrics and experimental UI label.
- Updated ten-slide PDF and 162-second video with actual AI footage and explicit limitations. All PDF pages rendered/inspected; video decoded and AI segment visually checked.
- Final checks: 148 backend + 4 frontend tests, Ruff, TypeScript and Vite pass. One upstream deprecation warning. Prior fresh scratch install remains documented.

Open work: stronger model/semantic grounding and held-out evaluation; applicant identity/contact/background; exact portal rules/eligibility/deadline; wider accessibility/security and device review. No real-user research or partner integration has occurred.

The simulation still shows more shortfall days for Ipon than fixed 10% (1,248 versus 1,206), with equal funded shocks (95/281). No superiority claim.

Git has no configured author identity; no identity invented, no remote created.

## Follow-up: conservative draft validation

Added source checks, explicit budget-inclusion choice and disabled confirmation for incomplete drafts. Replayed 35 saved proposals (not fresh inference), removing 6 candidates and 3 income dates. A separate 12-case live exploratory run matched intended reviewed behavior in 11 cases; one incorrect month-end date was cleared for manual completion. These sets/scores are not directly comparable. General reliability remains unproven. Refreshed actual browser footage and slides 6-7; 148 backend + 4 frontend tests pass. See reports/ai_grounding_evaluation.md.

## Final handoff — September 30, 2026

User requested completion and asked to leave applicant details blank. Prototype development and local submission preparation are closed for this scope. Added HANDOFF.md and submission/SUBMISSION_DRAFT.md; updated checklist and live public portal provenance. Published deadline is October 2; exact cutoff and authenticated form rules remain unverified. Remaining applicant actions are identity/slide 10, portal checks, delivery and submission. Further AI reliability and product validation work are future development, not claimed complete. No submission or publication occurred. This final change is documentation only; prior passing checks remain the latest code validation.

## Product clarity corrections — October 30, 2026

User identified ambiguous wallet/reserve wording and unexplained scenario amounts. Savings explanations now state the wallet balance after the proposed deposit separately from the estimated essentials reserve. Scenario cards show the monthly-essentials basis, current buffer, configured month fraction, and buffer-only coverage; amounts remain hypothetical. No financial recommendation or transfer rules changed.

Fresh verification: 151 backend tests and 4 frontend tests passed; Ruff lint/format, TypeScript and Vite build passed. Three new API regression cases cover distinct remaining-wallet/reserve amounts and scenario metadata. Actual browser verification reproduced the user's example: PHP 65 suggestion, PHP 1,935 remaining wallet, PHP 1,870 reserve; PHP 8,200 monthly essentials and PHP 2,050 / 4,100 / 8,200 scenarios against a PHP 500 buffer. Local demo left running in manual mode. Earlier AI quality reports were not rerun. One existing upstream Starlette/AnyIO deprecation warning remains.

## Consent balance disclosure — October 30, 2026

Added a read-only "Your demo balances" section above permission choices. It identifies the everyday wallet and emergency buffer, explains their purposes, and labels both as synthetic money. New sessions load actual mock wallet balances before the consent screen opens; revisiting consent uses current session balances rather than misleadingly calling them starting balances. No new scopes or automatic consent introduced. Verified the live browser shows PHP 2,000 wallet/PHP 500 buffer with all choices initially off. Six frontend tests and TypeScript/Vite build passed, including read-only disclosure and changed-balance rendering. Prepared these follow-up edits for publication to md-info/ipon-buffer after user authorization.

## Ipon Nearby modular prototype — November 3, 2026

Implemented on feature/ipon-nearby: persistent local price reports with optional photos, exact pack/quantity and conditions, helpful reactions, independent self-attested confirmations, changed-price reporting, capped contribution points, flags, owner deletion and privacy cleanup. Preserved savings recommendation engine and added Nearby navigation with read-only savings context. Standalone E-Wallet demo at /nearby supports two synthetic neighbor identities. Built separate mount/update/unmount SDK with Shadow DOM styling and host-owned transport/navigation. See docs/NEARBY_INTEGRATION.md.

Validation: full suite passed 154 backend and 6 frontend tests, Ruff, TypeScript and Vite. Added and passed an additional stale-report/privacy test (4 Nearby tests total). Separate library build passed. Live browser verified publish, helpful reaction, independent confirmation and 5-point reporter reward. Local AI demo launcher is running. Native APK/AAR, production wallet integration, verified location, fraud resistance, reward funding and moderation adjudication remain outside this prototype. Existing pitch/video describe the earlier app and were not refreshed.

## Neighborhood feed UI — November 3

Restyled Nearby with a Nextdoor-inspired neighborhood feed: masthead search, sidebar, post composer, author rows, local price cards, latest/confirmed/own filters, contribution panel, savings context and responsive bottom navigation. Ipon branding retained. TypeScript, six frontend tests, application build and SDK build passed. Desktop screenshot inspected and confirmed-price filter exercised in the live browser. Mobile layout is responsive CSS; a separate device pass remains unverified. No savings engine changes.

## Unified Buffer and community home — November 3

Replaced split entry flows with a plain centered Log in button that starts a synthetic session. The post-login home displays clickable Buffer balance, wallet balance, savings setup/recommendation and community feed together. Savings setup retains explicit consent; editing/details/emergency/privacy expand on the home with Close details. Plan confirmation returns to the combined home. Both / and /nearby now enter the unified app. The login is a demo session action, not real account authentication. Six frontend tests, TypeScript and build pass; live browser verified one-button entry and simultaneous Buffer/feed display. Backend engine unchanged.

## Cohesion and navigation pass — November 3

Unified visible branding under Ipon Buffer; embedded feed keeps search without a second logo. Added explicit Back to home from consent and all detail views, Back to feed from posting, All finds from filtered feed, and Cancel changes for plan editing. Browser-back from details returns home. Leaving setup restores granted permissions, and canceling plan changes restores the saved plan. Scoped plan validation to plan inputs so community posting cannot block saving. Removed obsolete hidden sidebar. Updated AI and privacy guidance to match navigation and community deletion.

Live browser reviewed login, combined home, permission setup, plan editor, cancel-to-home, emergency view, and privacy view. Six frontend tests, TypeScript, app build and standalone module build pass. Separate mobile/device and full photo-upload interaction passes were not performed in this navigation update. Savings engine and backend unchanged.

## Photo-led demo feed — November 3

Added six explicitly fictional grocery/convenience/small-business posts with locally bundled Unsplash photographs, author credit links and sample reaction counts. Images appear directly after the author row, before price details. Store examples include fictional Puregold, 7-Eleven and Savemore branches alongside a sari-sari store, family grocery and produce stall. Photos are illustrative and do not depict those branches or prove the sample prices. Source/license metadata: web/public/demo/credits.json. Generated images were not used.

Run .venv/Scripts/python.exe scripts/seed_nearby.py from the project to populate the local SQLite demo; repeat runs preserve existing sample IDs and user reports. Seed dates are generated only when first inserted and subsequently become stale normally. Six frontend tests, TypeScript, Ruff seed-script checks, app and SDK builds passed. Live browser inspected populated feed and image rendering.

## Merchant rewards — November 3

Added Rewards & partners customer view, separate cashback balance, fictional funded grocery offer, explicit simulated purchase confirmation, reward receipts and confirmed cashback-to-buffer redemption. Partner tools create capped seven-day campaigns. Budget and wallet mutations are atomic with idempotent purchase/redemption retries, once-per-session eligibility, expiry/balance checks and own-campaign rejection. Community points remain separate noncash recognition. Privacy deletion also removes owned campaigns.

Full verification before final privacy cleanup: 157 backend + 6 frontend tests, Ruff, TypeScript and Vite passed; reward/lifecycle tests rerun after cleanup. Live browser: PHP 100 purchase reduced wallet 2000 to 1900 and earned PHP 10; separate confirmed redemption changed buffer 500 to 510 and cashback to zero. No real payment, merchant funding, SKU eligibility or partner integration claimed. See docs/REWARDS.md. Production refunds/reversals and settlement verification remain future work.

## Minimal feed copy — November 3

Removed decorative sidebar subtitle and redundant feed eyebrow. Photo posts now show author, demo badge, image, item, price, store/quantity, short freshness/confirmation indicators and primary reactions. Moved captions, exact timestamps, conditions, sample-data explanation, image credits and secondary report actions into Details. Kept visible demo badges; disclosure remains accessible. Simplified rewards introduction and collapsed offer funding/expiry details. TypeScript, six frontend tests and both builds passed. No financial logic changed.

## Compact summary — November 3

Reduced Buffer header padding and typography; changed vertically stacked actions to a two-column layout so the feed appears higher. Mobile actions retain two columns. CSS-only presentation change.
