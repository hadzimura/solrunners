#!/usr/bin/env python3
"""
tate.py — Springs of Life: Tate node video player
==================================================
Plays all MP4 files from media/tate/ in an endless random loop using mpv
rendered via X11 + GPU (OpenGL). Launched by xinit from sol.tate.service.

Rendering:
  vo=gpu       — GPU-accelerated renderer over X11 (OpenGL / EGL)
  hwdec=auto   — hardware video decoding (V4L2M2M on Raspberry Pi)
  video-sync=display-resample — frame timing locked to display refresh,
                                eliminates screen tearing

Randomisation rules:
  - Next video is chosen randomly from the full library.
  - The same video cannot appear within the last NO_REPEAT_WINDOW picks,
    so a clip won't repeat sooner than 5 random choices ahead.

Controls:
  - ESC / q key → quit cleanly
  - SIGTERM      → quit cleanly (systemd stop / kill)

Run inside the project venv (requires DISPLAY to be set):
  DISPLAY=:0 .venv/bin/python tate.py

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
    # vo=gpu           — GPU-accelerated renderer via X11/OpenGL; handles vsync
    #                    correctly, eliminating the tearing seen with vo=drm.
    # hwdec=auto       — hardware video decoding (V4L2M2M on Raspberry Pi);
    #                    offloads decode from CPU, reduces latency.
    # video_sync=      — lock frame delivery to the display refresh rate;
    #  display_resample  resamples audio to compensate, giving smooth playback.
    # fullscreen=True  — fill the entire display.
    # input_default_bindings=False — disable mpv's built-in key map; only our
    #                    explicit bindings are active.
    # input_vo_keyboard=True — mpv reads keyboard events from the X11 window
    #                    (required when there is no window manager).
    player = mpv.MPV(
        vo="gpu",
        hwdec="auto",
        video_sync="display-resample",
        fullscreen=True,
        input_default_bindings=False,
        input_vo_keyboard=True,
        log_handler=print,
        loglevel="warn",
    )

    def _quit():
        """Signal the main loop to stop and terminate the current clip."""
        quit_event.set()
        player.quit()

    @player.on_key_press("ESC")
    def _on_esc() -> None:
        """ESC key: quit playback."""
        print("[tate] ESC pressed — quitting")
        _quit()

    @player.on_key_press("q")
    def _on_q() -> None:
        """q key: quit playback (convenience alias for ESC)."""
        print("[tate] q pressed — quitting")
        _quit()

    def _handle_signal(sig, _frame) -> None:
        """Handle SIGTERM / SIGINT (e.g. systemd stop or Ctrl-C)."""
        print(f"[tate] Received signal {sig} — quitting")
        _quit()

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
