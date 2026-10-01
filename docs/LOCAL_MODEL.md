# Local model setup

On September 30, 2026, the user-authorized portable Ollama 0.34.4 runtime was installed outside the submission project at `../../work/local-ai/runtime`. Its official release archive SHA-256 was verified: `535193f38f3344e5b08f5d1c171c31ce11aa17f0124ff69ae26d8ec7fe06fa62`. The selected model is `qwen3:1.7b`; evaluation results are recorded separately, not inferred from successful installation.

The runtime binds to `127.0.0.1:11434`, with `OLLAMA_NO_CLOUD=1` and a separate model cache at `../../work/local-ai/models`. The runtime detected the machine's NVIDIA RTX 2060. Model weights and runtime binaries are excluded from the code/submission package. A model file alone is insufficient; it needs a compatible inference runtime.

The 1,359,293,444-byte model download completed. Model digest: `8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7`. Launch the AI-enabled demo:

```powershell
.\.venv\Scripts\python.exe scripts/demo_local_ai.py
```

The launcher checks installed models and never downloads automatically. On another machine, install Ollama from its official distribution, run `ollama pull qwen3:1.7b`, then use the launcher. `IPON_OLLAMA_EXE` may specify a portable executable. Initial setup needs network access; inference runs locally after setup.

For explicit backend configuration:

```powershell
$env:IPON_AI_MODEL = 'qwen3:1.7b'
$env:IPON_AI_BASE_URL = 'http://127.0.0.1:11434'
$env:IPON_AI_PROTOCOL = 'ollama'
.\.venv\Scripts\python.exe scripts/tasks.py demo
```

AI requires separate consent and produces reviewable fields only. It receives the entered text and reference date, not account credentials, balances, or transaction history. Manual entry remains available. The financial engine calculates recommendations; confirmation is required before applying a draft. There is no remote fallback.

Evaluation: set the same environment variables and run `scripts/evaluate_ai.py --output reports/ai_run_baseline.json`. Schema validity is not field accuracy. Review the outputs against all 40 synthetic expectations before claiming quality. This is a development set, not independent evidence of real-world reliability.

Sources: [Ollama Windows](https://docs.ollama.com/windows), [model](https://ollama.com/library/qwen3:1.7b), [chat API](https://docs.ollama.com/api/chat), [structured outputs](https://docs.ollama.com/capabilities/structured-outputs).

Final configuration uses thinking enabled, context 8192 and 3000 generated-token limit. Three real-model runs are retained. The model failed the quality gate; see reports/ai_evaluation.md. A first cold start exceeded the 45-second application timeout; retry after the runtime warms, or use manual entry.

The same model now has conservative source checks; see reports/ai_grounding_evaluation.md. No stronger model has been installed.
