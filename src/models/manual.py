from __future__ import annotations

import json
from pathlib import Path


def load_model_output(path: str | Path) -> dict:
    """Load a JSON response captured from any external AI tool."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
