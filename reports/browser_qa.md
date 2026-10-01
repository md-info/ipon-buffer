# Browser verification

Actual local API and React interface, September 28–29, 2026. No mocked frontend successes.

Consent initially off. Confirm PHP 250/day, PHP 600 bill and October 2 income: reserve PHP 1,760, suggestion PHP 120. Unavailable AI returns an error and preserves manual entry. Add school PHP 300 due September 29: reserve PHP 2,090, suggestion zero, deposit disabled. Remove it: PHP 120 restored. Deposit: wallet/buffer PHP 1,880/620. Withdraw 600: 2,480/20. Separate payment 600: 1,880/20. Revoke analysis/AI, withdraw 10: 1,890/10, refill estimate paused.

Current screenshots: overview-verified.png and mobile-verified.png. Older overview.png has a full-page stitching artefact; do not use it in submission material. emergency.png is the actual deck screenshot.

360px viewport: client and scroll width both 345px excluding scrollbar, no page overflow. Visible focus styling and 44px main controls exist. Formal accessibility, screen-reader and dialog focus-trap validation remain outstanding.

Video uses actual browser screenshots sampled about once per second during operation, with captions and cuts between segments. It is not narrated or a continuous high-frame-rate capture. It contains no fixture AI response or animated mockup. First three segments precede a session interruption; the same initial fixture was recreated for the rest.


## September 30 actual AI journey

qwen3:1.7b via Ollama produced a PHP 300 school draft for Sep 29. Before confirmation, wallet 2000, buffer 500, reserve 1760, recommendation 120 remained unchanged. Tester reviewed one-time recurrence and selected No for daily-budget inclusion. Confirming produced reserve 2090 and recommendation 0 with disabled deposit, while balances stayed unchanged. Actual captures: ai-draft.png, ai-confirmed.png, and updated video. This successful example does not establish general model quality; the 40-case evaluation failed its quality gate.

Validation follow-up: actual model draft starts recurrence and inclusion unselected. Confirm disabled initially and after recurrence alone, enabled after inclusion selected. Initial PHP120/reserve1760 and unchanged wallet2000/buffer500 verified; apply yields PHP0/reserve2090, balances unchanged. ai-grounded-draft.png and ai-grounded-confirmed.png capture these states.
