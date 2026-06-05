#!/usr/bin/env python3
"""AI runtime for Fountain audio-only playback with --system support."""

from __future__ import annotations

import argparse
import random
import subprocess
import time
from pathlib import Path
from typing import List, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fountain audio runtime")
    parser.add_argument("--system", choices=("rpi", "macos"), default="rpi")
    parser.add_argument("--fountain-version", type=int, default=1)
    parser.add_argument("--min-delay", type=int, default=11)
    parser.add_argument("--max-delay", type=int, default=300)
    parser.add_argument("--single-cycle", action="store_true")
    return parser.parse_args()


def _pick_player(system_name: str) -> Optional[List[str]]:
    if system_name == "macos":
        return ["afplay"]

    # Raspberry Pi/Linux default path. Keep fallback order simple and explicit.
    for candidate in (["aplay", "-q"], ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error"]):
        try:
            subprocess.run([candidate[0], "--help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            return candidate
        except FileNotFoundError:
            continue
    return None


def _play_blocking(cmd_prefix: List[str], wav_file: Path) -> int:
    proc = subprocess.run(cmd_prefix + [str(wav_file)], check=False)
    return proc.returncode


def _play_async(cmd_prefix: List[str], wav_file: Path) -> subprocess.Popen:
    return subprocess.Popen(cmd_prefix + [str(wav_file)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _head_timer(total_seconds: float, variation: Optional[int] = None) -> float:
    values = [0.0, 0.0, total_seconds / 2.0, max(total_seconds - 3.0, 0.0), 3.0]
    if variation == 0:
        return random.choice(values[2:])
    if variation is None:
        return random.choice(values)
    if 0 <= variation < len(values):
        return values[variation]
    return random.choice(values)


def run_cycle(base_wav: Path, head_samples: List[Path], cmd_prefix: List[str], fountain_version: int) -> None:
    if fountain_version == 1 or not head_samples:
        _play_blocking(cmd_prefix, base_wav)
        return

    # Estimate duration using ffprobe if available; fall back to a conservative 60s.
    est_duration = 60.0
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(base_wav)],
            capture_output=True,
            text=True,
            check=False,
        )
        if probe.returncode == 0:
            est_duration = max(float(probe.stdout.strip()), 1.0)
    except Exception:
        pass

    selected_head = random.choice(head_samples)
    head_start = _head_timer(est_duration, fountain_version)

    fountain_proc = _play_async(cmd_prefix, base_wav)
    time.sleep(head_start)

    head_proc = _play_async(cmd_prefix, selected_head)
    head_proc.wait()
    fountain_proc.wait()


def main() -> int:
    args = parse_args()

    project_root = Path(__file__).resolve().parent
    media_root = project_root / "media"
    fountain_wav = media_root / "fountain" / "fountain.wav"
    head_samples = sorted((media_root / "heads" / "samples").glob("*.wav"))

    if not fountain_wav.is_file():
        print(f"Missing fountain sample: {fountain_wav}")
        return 1

    player = _pick_player(args.system)
    if player is None:
        print("No supported audio player found. Install 'afplay' (macOS default) or 'aplay'/'ffplay' (Linux).")
        return 1

    while True:
        run_cycle(fountain_wav, head_samples, player, args.fountain_version)

        if args.single_cycle:
            break

        delay = random.randint(args.min_delay, args.max_delay)
        print(f"Being silent for: {delay} seconds...")
        time.sleep(delay)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
