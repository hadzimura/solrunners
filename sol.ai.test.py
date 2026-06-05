#!/usr/bin/env python3
"""Smoke tests for unified AI launcher argument parsing."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_launcher(project_root: Path):
    launcher = project_root / "sol.ai.py"
    spec = importlib.util.spec_from_file_location("sol_ai", launcher)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {launcher}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    project_root = Path(__file__).resolve().parent
    launcher = _load_launcher(project_root)

    known, passthrough = launcher.parse_args(["--object", "entropy", "--system", "macos", "--fullscreen"])
    assert known.object == "entropy"
    assert known.system == "macos"
    assert passthrough == ["--fullscreen"]

    print("sol.ai launcher smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

