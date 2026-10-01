# Ipon Buffer — application text draft

Local handoff, September 30, 2026. Reusable answers, not a transcription of authenticated portal fields. Adapt to actual field limits. Applicant fields remain blank by request.

## Applicant

Name:

Team name:

Country of residence:

Contact email:

Solo or team:

Relevant background:

## Project and track

Ipon Buffer — Track 02: Emergency Savings; Format 1: Technical and product-led.

## Short description

Ipon Buffer helps people with irregular income review what they can set aside for emergencies after accounting for everyday needs and upcoming bills. An optional local AI assistant turns written notes into editable planning drafts. Users confirm all changes; deterministic rules calculate recommendations and AI cannot move money.

## Problem and intended users

The initial design focuses on Philippine workers with irregular income. A fixed savings percentage can overlook an upcoming bill or the gap until the next income date. Ipon Buffer makes those assumptions visible before suggesting a contribution, while keeping emergency withdrawals available in the mock wallet. This is a design hypothesis, not a validated finding from user research.

## Working solution

Users review daily needs, bills and their expected next income date. An integer-centavo engine reserves planned essentials plus a margin, then calculates a suggested contribution. Deposits and withdrawals require explicit confirmation. Emergency withdrawals are separate from spending, and an optional refill estimate does not debit funds. Analysis consent can be revoked without blocking mock emergency withdrawals.

## AI role

Ollama and qwen3:1.7b run locally after separate installation. The assistant proposes fields from user-entered text, with conservative source checks and mandatory human review. It has no transfer tools or ledger-write access. Manual entry remains available. The model failed the development quality gate, so the feature is explicitly experimental; a successful demonstration does not establish reliable extraction. Model weights are not included in the review ZIP.

## Implementation and evidence

The prototype uses FastAPI, SQLite and React/TypeScript with a synthetic wallet. Latest checks passed: 148 backend tests, 4 frontend tests, Ruff, TypeScript and Vite. A ten-slide PDF and 162-second recording demonstrate the real local application and model inference. No live funds, partner integration, customers or real-world impact are claimed.

Synthetic comparison results are mixed: the base scenario funded 95 of 281 shocks for both Ipon Buffer and fixed 10% saving; Ipon recorded 1,248 essential-shortfall days versus 1,206 for fixed 10%. This is not evidence of superiority. Raw AI development review found 8 of 40 cases satisfactory. A different 12-case exploratory follow-up matched intended reviewed behavior in 11 cases; these sets and criteria are not comparable accuracy measurements.

## Sustainability and validation plan

A future distribution hypothesis is a partner-paid service inside a wallet or financial institution. Illustrative monthly economics assume PHP 20 revenue and PHP 8 variable cost per active user against PHP 120,000 fixed cost, implying 10,000 active users to break even before integration costs. These are unvalidated planning assumptions. Next steps would be interviews, usability testing, independent AI evaluation and a partner-supervised pilot; none has occurred.

## Attachments and final check

- Ipon_Buffer_Pitch.pdf — 10 slides; applicant placeholder requires completion.
- Ipon_Buffer_Demo.mp4 — 162 seconds; captioned, without narration.
- Source and supporting reports — included in local review ZIP; repository publication optional.

Published deadline: October 2, 2026. Confirm exact cutoff/timezone, application requirements, eligibility and terms inside the portal. Nothing has been submitted.
