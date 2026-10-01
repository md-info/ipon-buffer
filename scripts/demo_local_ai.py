"""Launch the installed local-model demo. No implicit downloads or cloud access."""

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT.parents[1] / "work/local-ai"


def models():
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2) as response:
            return [item["name"] for item in json.load(response).get("models", [])]
    except (OSError, ValueError):
        return None


def main():
    environment = os.environ.copy()
    model = environment.get("IPON_AI_MODEL", "qwen3:1.7b")
    environment.update(
        IPON_AI_MODEL=model, IPON_AI_PROTOCOL="ollama", IPON_AI_BASE_URL="http://127.0.0.1:11434"
    )
    runtime = environment.get("IPON_OLLAMA_EXE") or shutil.which("ollama")
    if not runtime and (LOCAL / "runtime/ollama.exe").exists():
        runtime = str(LOCAL / "runtime/ollama.exe")
    process = None
    log = None
    try:
        available = models()
        if available is None:
            if not runtime:
                raise RuntimeError("Install Ollama and the model first. See docs/LOCAL_MODEL.md.")
            environment.update(OLLAMA_HOST="127.0.0.1:11434", OLLAMA_NO_CLOUD="1")
            if (LOCAL / "models").exists():
                environment["OLLAMA_MODELS"] = str(LOCAL / "models")
            (ROOT / ".cache").mkdir(exist_ok=True)
            log = (ROOT / ".cache/ollama.log").open("a", encoding="utf-8")
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            process = subprocess.Popen(
                [runtime, "serve"], env=environment, stdout=log, stderr=log, creationflags=flags
            )
            for _ in range(60):
                available = models()
                if available is not None:
                    break
                if process.poll() is not None:
                    raise RuntimeError("Ollama stopped. Inspect .cache/ollama.log.")
                time.sleep(0.5)
        if not available or model not in available:
            raise RuntimeError(f"Model {model} is not installed. No automatic download attempted.")
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/tasks.py"), "demo"],
            cwd=ROOT,
            env=environment,
            check=True,
        )
    finally:
        if process and process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        if log:
            log.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Local AI demo stopped.")
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
