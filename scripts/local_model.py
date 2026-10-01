"""Read local runtime status. Never downloads, installs, or selects a model."""

import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.assistant.service import ModelAdapter  # noqa: E402

model = ModelAdapter()
path = "/api/tags" if model.protocol == "ollama" else "/v1/models"
base = model.base.removesuffix("/v1") if model.protocol != "ollama" else model.base
try:
    with urllib.request.urlopen(base + path, timeout=3) as response:
        print(json.dumps(json.load(response), indent=2))
except OSError:
    print("No local runtime answered. Manual mode remains available. See docs/LOCAL_MODEL.md.")
    sys.exit(1)
