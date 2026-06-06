"""
fountain.py — Springs of Life: Fountain node audio player
==========================================================
Plays media/fountain/fountain.wav in an endless loop with configurable
left/right channel gain and a random silence interval between plays.

Playback cycle
--------------
  1. Play fountain.wav to completion (stereo, full quality via PortAudio).
  2. Wait: SILENCE_BASE + random(0, SILENCE_RANDOM) seconds.
  3. Go to 1.

Left/right gain is applied per-channel before each play via numpy multiply.
This is the Phase 1 baseline — gain is static per session.

Phase 2 (see docs/FOUNTAIN.md): two HCY-SRF05 ultrasonic distance sensors
replace the static gain with real-time per-channel volume derived from how
close a spectator is to each sensor. The loop structure stays identical;
only the gain source changes (sensor reading instead of CLI arg).

Configuration (CLI args, all optional):
  --wav             Path to WAV file (default: media/fountain/fountain.wav)
  --silence-base    Minimum silence between plays in seconds (default: 10)
  --silence-random  Max extra random silence in seconds (default: 10)
  --gain-left       Left channel gain 0.0–1.0 (default: 1.0)
  --gain-right      Right channel gain 0.0–1.0 (default: 1.0)

Controls:
  SIGTERM / SIGINT → quit cleanly (exits after current play or mid-silence)

Run inside the project venv:
  .venv/bin/python fountain.py

See docs/FOUNTAIN.md for full documentation and deployment instructions.
"""

from __future__ import annotations

import argparse
import random
import signal
import sys
import threading
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf


# ── Default configuration ─────────────────────────────────────────────────────
SILENCE_BASE_S     = 10    # minimum silence between plays (seconds)
SILENCE_RANDOM_S   = 10    # max extra random silence added on top (seconds)
GAIN_LEFT_DEFAULT  = 1.0   # left channel gain  (0.0 = mute, 1.0 = full)
GAIN_RIGHT_DEFAULT = 1.0   # right channel gain


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Fountain audio player — Springs of Life",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--wav",
        type=Path,
        default=Path(__file__).resolve().parent / "media" / "fountain" / "fountain.wav",
        help="Path to the WAV file to play",
    )
    p.add_argument("--silence-base",   type=float, default=SILENCE_BASE_S,
                   help="Minimum silence between plays (seconds)")
    p.add_argument("--silence-random", type=float, default=SILENCE_RANDOM_S,
                   help="Max extra random silence added on top (seconds)")
    p.add_argument("--gain-left",  type=float, default=GAIN_LEFT_DEFAULT,
                   help="Left channel gain 0.0–1.0")
    p.add_argument("--gain-right", type=float, default=GAIN_RIGHT_DEFAULT,
                   help="Right channel gain 0.0–1.0")
    return p.parse_args()


def load_wav(path: Path) -> tuple[np.ndarray, int]:
    """Load WAV into a float32 stereo numpy array.

    Mono sources are duplicated to both channels so L/R gain always applies.
    Files with more than 2 channels are downmixed to the first two.
    Loading once at startup keeps the SD card idle during the playback loop.
    """
    data, samplerate = sf.read(str(path), dtype="float32", always_2d=True)

    if data.shape[1] == 1:
        # Mono → stereo: same signal on both channels
        data = np.concatenate([data, data], axis=1)
    elif data.shape[1] > 2:
        data = data[:, :2]

    print(f"[fountain] Loaded {path.name}: "
          f"{samplerate} Hz, {data.shape[1]}ch, {len(data)/samplerate:.1f}s")
    return data, samplerate


def apply_gain(audio: np.ndarray, gain_l: float, gain_r: float) -> np.ndarray:
    """Return a copy of the audio array with per-channel gain applied.

    Phase 2 note: this function stays unchanged. Phase 2 will call it once per
    audio callback block (~10 ms) with distance-sensor-derived gain values
    rather than a single static value for the whole clip.
    """
    out = audio.copy()
    out[:, 0] *= float(np.clip(gain_l, 0.0, 1.0))
    out[:, 1] *= float(np.clip(gain_r, 0.0, 1.0))
    return out


def main() -> int:
    args = parse_args()

    if not args.wav.is_file():
        print(f"[fountain] ERROR: WAV not found: {args.wav}", file=sys.stderr)
        return 1

    # Load audio once — SD card not touched again during the loop
    audio_raw, samplerate = load_wav(args.wav)

    # Quit event: set by SIGTERM/SIGINT; also interrupts the silence wait
    quit_event = threading.Event()

    def _handle_signal(sig, _frame) -> None:
        print(f"\n[fountain] Signal {sig} — stopping")
        quit_event.set()
        sd.stop()          # interrupt any in-progress sounddevice playback

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT,  _handle_signal)

    print(f"[fountain] Starting loop  |  "
          f"gain L={args.gain_left:.2f} R={args.gain_right:.2f}  |  "
          f"silence {args.silence_base:.0f}s + rand 0–{args.silence_random:.0f}s")

    # ── Main playback loop ────────────────────────────────────────────────────
    while not quit_event.is_set():

        # Bake current gain into the audio array before handing to sounddevice.
        # Phase 2: replace with a streaming callback that re-samples gain from
        # SRF05 distance readings every ~10 ms block.
        audio_out = apply_gain(audio_raw, args.gain_left, args.gain_right)

        print(f"[fountain] ▶  {args.wav.name}")
        sd.play(audio_out, samplerate=samplerate, blocking=False)

        # Wait for playback to finish, checking quit every 100 ms
        while sd.get_stream().active and not quit_event.is_set():
            quit_event.wait(timeout=0.1)

        if quit_event.is_set():
            break

        # ── Random silence ────────────────────────────────────────────────────
        # total = silence_base + uniform(0, silence_random)
        # quit_event.wait() returns immediately if stop is requested
        extra   = random.uniform(0.0, args.silence_random)
        silence = args.silence_base + extra
        print(f"[fountain] ⏸  {silence:.1f}s silence "
              f"({args.silence_base:.0f}+{extra:.1f})")
        quit_event.wait(timeout=silence)

    print("[fountain] Stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
