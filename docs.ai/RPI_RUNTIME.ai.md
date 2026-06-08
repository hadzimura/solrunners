# Raspberry Pi Runtime Notes (No Window Manager Option)

Current setup (from `configurations/.xinitrc.entropy` and `.xinitrc.heads`) starts:

- Xorg session
- `matchbox-window-manager`
- `unclutter`
- `xterm`

Since OpenCV windows are directly created by the Python processes, a full window manager is optional.

## Option A: keep Xorg, remove window manager (recommended first step)

Use this pattern in `.xinitrc` on RPi nodes:

```sh
xrandr --output HDMI-1 --rotate left
cd /home/zero/solrunners
export PYTHONPATH=$PYTHONPATH:/home/zero/solrunners
export PYTHONUNBUFFERED=1
source /home/zero/solrunners/.venv/bin/activate
xset -dpms
xset s off
xset s noblank
exec python3 /home/zero/solrunners/Entro.ai.py --system rpi --fullscreen
```

For Heads node, replace entrypoint with `Heads.ai.py`.

## Option B: skip Xorg entirely

Not recommended with current code because `cv.imshow` paths require display server and input loop integration.

A true no-X redesign would require:

1. replacing `cv.imshow` with direct DRM/KMS rendering, or
2. moving playback to `ffplay`/`vlc` overlays and dropping OpenCV windows.

## Suggested systemd approach

Prefer explicit systemd unit over auto-start from shell profile:

1. Keep `sol.service` as startup unit.
2. Replace `ExecStart=/usr/bin/startx` with direct command to a node-specific script.
3. Let the script run either:
   - `xinit ... python3 Entro.ai.py --system rpi`, or
   - direct `python3 Fountain.ai.py --system rpi` for audio-only node.

This makes startup deterministic and easier to debug remotely.

