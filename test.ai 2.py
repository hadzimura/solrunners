#!/usr/bin/env python3
"""Smoke tests for AI wrappers and system selection behavior."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def load_config_ai(project_root: Path):
    cfg = project_root / "modules" / "Config.ai.py"
    spec = importlib.util.spec_from_file_location("sol_config_ai", cfg)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {cfg}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    project_root = Path(__file__).resolve().parent
    config_ai = load_config_ai(project_root)

    system_name, rest = config_ai.extract_system_arg(["--system", "macos", "--fullscreen"])
    assert system_name == "macos"
    assert rest == ["--fullscreen"]

    config_ai.configure_pyglet_for_system("macos")
    import pyglet.media as pyglet_media

    assert pyglet_media is not None

    print("AI smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
