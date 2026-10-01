"""Cross-platform tasks. Python 3.12 and Node 22.12+ are prerequisites."""

import argparse
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
WEB = ROOT / "web"


def run(*command: str, cwd: Path = ROOT) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def node() -> str:
    executable = shutil.which("node")
    if not executable:
        raise RuntimeError("Install Node 22.12+ to run the web application.")
    return executable


def setup() -> None:
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError("Run setup with Python 3.12.")
    if not PYTHON.exists():
        run(sys.executable, "-m", "venv", str(ROOT / ".venv"))
    run(str(PYTHON), "-m", "pip", "install", "-r", "requirements.txt")
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise RuntimeError("Install npm with Node.")
    run(npm, "ci", "--offline=false", "--cache", str(ROOT / ".cache/npm"), cwd=WEB)


def check(tests_only: bool = False) -> None:
    if not tests_only:
        run(str(PYTHON), "-m", "ruff", "check", "backend", "scripts", "simulation")
        run(str(PYTHON), "-m", "ruff", "format", "--check", "backend", "scripts", "simulation")
    run(str(PYTHON), "-m", "pytest")
    run(node(), "node_modules/vitest/vitest.mjs", "run", cwd=WEB)
    if not tests_only:
        run(node(), "node_modules/typescript/bin/tsc", "--noEmit", cwd=WEB)
        run(node(), "node_modules/vite/bin/vite.js", "build", cwd=WEB)


def wait_ready(url: str, processes: list[subprocess.Popen], seconds: int = 30) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if any(process.poll() is not None for process in processes):
            raise RuntimeError("A demo process stopped before readiness; inspect its output.")
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(0.2)
    raise RuntimeError(f"Timed out waiting for {url}")


def demo(smoke: bool) -> None:
    processes: list[subprocess.Popen] = []
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        processes.append(
            subprocess.Popen(
                [
                    str(PYTHON),
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--app-dir",
                    "backend",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                ],
                cwd=ROOT,
                creationflags=flags,
            )
        )
        wait_ready("http://127.0.0.1:8000/health", processes)
        processes.append(
            subprocess.Popen(
                [
                    node(),
                    "node_modules/vite/bin/vite.js",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "5173",
                    "--strictPort",
                ],
                cwd=WEB,
                creationflags=flags,
            )
        )
        wait_ready("http://127.0.0.1:5173/health", processes)
        wait_ready("http://127.0.0.1:5173", processes)
        mode = (
            "local model configured"
            if os.environ.get("IPON_AI_MODEL")
            else "manual mode; AI not configured"
        )
        print(f"Demo ready: http://127.0.0.1:5173 ({mode})", flush=True)
        if smoke:
            print("Backend, frontend, and proxied health are ready.", flush=True)
            return
        while all(process.poll() is None for process in processes):
            time.sleep(0.5)
        raise RuntimeError("A demo process stopped unexpectedly.")
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=["setup", "check", "test", "demo", "sim"])
    parser.add_argument(
        "--smoke", action="store_true", help="Start demo, verify, then shut it down"
    )
    args = parser.parse_args()
    if args.task == "setup":
        setup()
    elif args.task in {"check", "test"}:
        check(args.task == "test")
    elif args.task == "demo":
        demo(args.smoke)
    else:
        run(str(PYTHON), "simulation/run.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Demo stopped.")
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
