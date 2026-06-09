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
    """Configure pyglet options for the selected runtime target.

    headless must be False on RPi even though OpenCV owns the video output.
    Setting headless=True disables pyglet's audio driver entirely (SilentDriver),
    producing no sound.  Pyglet's OpenAL backend only needs DISPLAY=:0 (provided
    by xinit) to initialise — it does NOT need to manage the display itself.
    """
    import pyglet

    pyglet.options["headless"] = False


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
