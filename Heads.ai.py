#!/usr/bin/env python3
"""AI wrapper for Heads runtime with --system support."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_config_ai():
    config_ai_path = Path(__file__).resolve().parent / "modules" / "Config.ai.py"
    spec = importlib.util.spec_from_file_location("sol_config_ai", config_ai_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {config_ai_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    config_ai = _load_config_ai()
    config_ai.run_original_script("Heads.py", sys.argv[1:])

