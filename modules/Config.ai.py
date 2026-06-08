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
    """Set pyglet headless mode for the selected runtime target.

    On RPi (system_name='rpi') headless=True so pyglet does not try to open
    its own display window (OpenCV/xinit owns the display).
    On macOS headless=False so pyglet can use the local display.

    The monkey-patch guard that was here previously is removed: Python 3.12+
    forbids setting __setitem__ on built-in dict subclasses (TypeError: cannot
    set '__setitem__' attribute of immutable type). Plain assignment is enough.
    """
    import pyglet

    pyglet.options["headless"] = (system_name == "rpi")


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
