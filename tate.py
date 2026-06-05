#!/usr/bin/env python3
"""
tate.py — Springs of Life: Tate node video player
==================================================
Plays all MP4 files from media/tate/ in an endless random loop using mpv
rendered directly to the framebuffer via DRM/KMS (no Xorg required).

Randomisation rules:
  - Next video is chosen randomly from the full library.
  - The same video cannot appear within the last NO_REPEAT_WINDOW picks,
    so a clip won't repeat sooner than 5 random choices ahead.

Controls:
  - ESC key   → quit cleanly
  - SIGTERM   → quit cleanly (systemd stop / kill)

Run inside the project venv:
  .venv/bin/python tate.py

See docs/TATE.md for full documentation and deployment instructions.
"""

import signal
import sys
import threading
from collections import deque
from pathlib import Path
import random

import mpv  # python-mpv: ctypes wrapper around libmpv

# ── Configuration ─────────────────────────────────────────────────────────────

# Absolute path to the media directory, relative to this script's location.
MEDIA_DIR = Path(__file__).parent / "media" / "tate"

# A video that was recently played cannot be selected again until at least
# this many other different videos have been played since it last appeared.
NO_REPEAT_WINDOW = 5


# ── Helpers ───────────────────────────────────────────────────────────────────

def discover_videos(media_dir: Path) -> list[Path]:
    """Return a sorted list of MP4 files found in media_dir."""
    videos = sorted(media_dir.glob("*.mp4"))
    if not videos:
        sys.exit(f"[tate] ERROR: no MP4 files found in {media_dir}")
    print(f"[tate] Found {len(videos)} video(s) in {media_dir}")
    return videos


def pick_next(videos: list[Path], recent: deque) -> Path:
    """
    Choose a random video that is not in the recent-play window.

    If the library is smaller than or equal to NO_REPEAT_WINDOW, the window
    is implicitly reduced to len(videos)-1 so playback always progresses.
    """
    pool = [v for v in videos if v not in recent]
    if not pool:
        # Library too small to honour the full window; pick any video that
        # was not played most recently (just avoid immediate repetition).
        last = recent[-1] if recent else None
        pool = [v for v in videos if v != last] or list(videos)
    return random.choice(pool)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    videos = discover_videos(MEDIA_DIR)

    # Event set by ESC key press or OS signal; main loop checks it between clips.
    quit_event = threading.Event()

    # ── mpv player setup ──────────────────────────────────────────────────────
    # vo=drm  — render directly to the Linux framebuffer (KMS/DRM).
    #           No Xorg, no Wayland, no window manager required.
    # ao=alsa — ALSA audio output; default on Raspberry Pi OS Lite.
    # fs      — start in fullscreen (fills the entire display).
    # input_default_bindings=False — disable mpv's built-in key map so only
    #           our explicit bindings are active (prevents accidental q/Quit).
    # input_vo_keyboard=True       — mpv reads keyboard events from the VO
    #           (needed for DRM mode where there is no X window manager).
    player = mpv.MPV(
        vo="drm",
        ao="alsa",
        fs=True,
        input_default_bindings=False,
        input_vo_keyboard=True,
        log_handler=print,
        loglevel="warn",
    )

    @player.on_key_press("ESC")
    def _on_esc() -> None:
        """Handle ESC key: signal the main loop and stop current playback."""
        print("[tate] ESC pressed — quitting")
        quit_event.set()
        player.quit()

    def _handle_signal(sig, _frame) -> None:
        """Handle SIGTERM / SIGINT (e.g. systemd stop or Ctrl-C)."""
        print(f"[tate] Received signal {sig} — quitting")
        quit_event.set()
        player.quit()

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    # ── Playback loop ─────────────────────────────────────────────────────────
    # deque with maxlen automatically evicts the oldest entry once full,
    # so `recent` always contains at most NO_REPEAT_WINDOW entries.
    recent: deque[Path] = deque(maxlen=NO_REPEAT_WINDOW)

    print("[tate] Starting playback loop (ESC to quit)")

    while not quit_event.is_set():
        chosen = pick_next(videos, recent)
        recent.append(chosen)
        print(f"[tate] Playing: {chosen.name}  "
              f"(pool size: {len(videos) - len(recent)}/{len(videos)})")

        player.play(str(chosen))

        # wait_until_playing() blocks until the video actually starts;
        # it raises ShutdownError if the player was quit before starting.
        try:
            player.wait_until_playing()
        except mpv.ShutdownError:
            break

        # wait_for_playback() blocks until the clip ends or player is quit.
        # When player.quit() is called (ESC / signal), this returns immediately.
        player.wait_for_playback()

    # ── Clean shutdown ────────────────────────────────────────────────────────
    try:
        player.terminate()
    except Exception:
        pass

    print("[tate] Exited cleanly")


if __name__ == "__main__":
    main()
