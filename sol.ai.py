#!/usr/bin/env python3
"""Unified AI launcher for Springs of Life runtimes."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Unified SoL AI launcher")
    parser.add_argument("--object", choices=("entropy", "heads", "fountain"), required=True)
    parser.add_argument("--system", choices=("rpi", "macos"), default="rpi")
    known, passthrough = parser.parse_known_args(argv)
    return known, passthrough


def main(argv=None) -> int:
    known, passthrough = parse_args(argv)

    project_root = Path(__file__).resolve().parent
    mapping = {
        "entropy": project_root / "Entro.ai.py",
        "heads": project_root / "Heads.ai.py",
        "fountain": project_root / "Fountain.ai.py",
    }

    target = mapping[known.object]
    if not target.is_file():
        print(f"Missing target runtime: {target}")
        return 1

    cmd = [sys.executable, str(target), "--system", known.system] + passthrough
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

