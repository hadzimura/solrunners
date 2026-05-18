#!/usr/bin/env python3
"""AI compatibility helpers for cross-platform runtime selection.

This file is intentionally standalone so AI entrypoints can load it via
importlib (the filename contains dots and is not importable as a normal module).
"""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def extract_system_arg(argv: Optional[List[str]] = None) -> Tuple[str, List[str]]:
    """Parse --system and return (system, passthrough_args)."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--system", choices=("rpi", "macos"), default="rpi")
    known, passthrough = parser.parse_known_args(argv)
    return known.system, passthrough


def configure_pyglet_for_system(system_name: str) -> None:
    """Set and lock pyglet headless mode for the selected runtime target."""
    import pyglet

    target_headless = system_name == "rpi"
    pyglet.options["headless"] = target_headless

    # Guard future writes so legacy files cannot override the selected mode.
    options_type = type(pyglet.options)
    if not getattr(options_type, "_sol_ai_guard_installed", False):
        original_setitem = options_type.__setitem__

        def _guarded_setitem(self, key, value):
            if key == "headless" and hasattr(self, "_sol_ai_headless_lock"):
                value = getattr(self, "_sol_ai_headless_lock")
            return original_setitem(self, key, value)

        options_type.__setitem__ = _guarded_setitem
        options_type._sol_ai_guard_installed = True

    setattr(pyglet.options, "_sol_ai_headless_lock", target_headless)


def run_original_script(original_script_name: str, argv: Optional[List[str]] = None) -> None:
    """Run an original script with --system handled at wrapper level."""
    system_name, passthrough = extract_system_arg(argv)
    configure_pyglet_for_system(system_name)

    project_root = Path(__file__).resolve().parents[1]
    original_script = project_root / original_script_name

    if not original_script.is_file():
        raise FileNotFoundError(f"Original script not found: {original_script}")

    sys.argv = [original_script_name] + passthrough
    runpy.run_path(str(original_script), run_name="__main__")
