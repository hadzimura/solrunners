# TATE — Springs of Life: Tate Node

## Overview

The **Tate** node is a Raspberry Pi that plays a collection of short MP4 video
clips (with sound) in an endless, randomised loop for gallery display.

### Key properties

| Property         | Value                                            |
|------------------|--------------------------------------------------|
| Hardware         | Raspberry Pi 4 (or newer)                        |
| OS user          | `zero`                                           |
| IP address       | `192.168.0.192`                                  |
| Display output   | HDMI — full-screen via X11 (no window manager)   |
| Player           | mpv via `python-mpv` (GPU/OpenGL renderer)       |
| Media location   | `media/tate/*.mp4`                               |
| Loop behaviour   | Endless random, no-repeat window of 5 picks      |
| Quit keys        | **ESC** or **q**                                 |

---

## Architecture

```
systemd: sol.tate.service
   └── xinit configurations/xinit.tate.sh  -- :0 -nocursor
           └── Xorg :0  (bare X server, no WM)
                   └── tate.py  (.venv/bin/python)
                           └── mpv (libmpv, vo=gpu, hwdec=auto)
                                   └── renders via OpenGL → HDMI
```

### Why X11 + GPU instead of DRM/KMS?

The original framebuffer (DRM) approach (`vo=drm`) caused visible screen
tearing and unreliable keyboard events. Switching to X11:

| Concern          | DRM/KMS (`vo=drm`)              | X11/GPU (`vo=gpu`) — chosen  |
|------------------|---------------------------------|------------------------------|
| Screen tearing   | ❌ No compositor → tearing      | ✅ vsync via GPU/EGL          |
| ESC key events   | ⚠️ Requires `/dev/input` access | ✅ Reliable X11 keyboard      |
| GPU decoding     | ✅ V4L2M2M                      | ✅ V4L2M2M (hwdec=auto)       |
| Complexity       | Low                             | Moderate (+ xinit step)       |

The service follows the same xinit pattern used by the other nodes (`entropy`, `heads`).

### No-repeat logic

```
recent = deque(maxlen=5)   # automatically evicts oldest when full

pool   = all_videos − recent   # exclude recent picks
chosen = random.choice(pool)   # pick from remaining
recent.append(chosen)
```

The same clip cannot appear within the last 5 selections. If the library
contains fewer than 5 videos the window is reduced to `len(videos) − 1`,
guaranteeing at minimum that the same clip never plays back-to-back.

---

## Raspberry Pi configuration (required once)

Two settings in `raspi-config` must be applied **before** first deployment,
or the `sol.tate.service` (which starts X via xinit) will not have access
to the framebuffer.

```bash
sudo raspi-config
```

1. **System Options → Boot / Auto Login → Console Autologin**
   - Ensures the `zero` user is already logged in on `tty1` at boot.
   - xinit (run from systemd) needs an active VT session to acquire the
     GPU framebuffer on newer Raspberry Pi OS kernels.
   - Without this, the service may start but show a black screen.

2. **System Options → Boot / Auto Login** — choose **Console** (not Desktop).
   - A desktop environment is not needed and consumes GPU memory.

After changing these settings, reboot the Pi before running the Ansible
playbook.

---

## File inventory

| Path                                              | Purpose                              |
|---------------------------------------------------|--------------------------------------|
| `tate.py`                                         | Main player application              |
| `configurations/xinit.tate.sh`                    | Xinit startup script (X setup + launch) |
| `configurations/systemd/sol.tate.service`         | systemd unit file                    |
| `media/tate/*.mp4`                                | Video clips (35 clips, 1–30 s each)  |
| `media/boot_logo.png`                             | Boot splash image (all nodes)        |
| `ansible/playbooks/setup-tate.yml`                | Full node setup playbook             |
| `ansible/playbooks/setup-boot-logo.yml`           | Boot splash update playbook          |
| `ansible/roles/tate/tasks/main.yml`               | Ansible role tasks                   |
| `ansible/roles/tate/handlers/main.yml`            | Ansible role handlers                |
| `ansible/inventory/group_vars/tate.yml`           | Node variables                       |

---

## System packages installed

| Package         | Purpose                                                  |
|-----------------|----------------------------------------------------------|
| `mpv`           | Player binary + shared `libmpv.so`                       |
| `libmpv-dev`    | Provides the `libmpv.so` symlink required by python-mpv  |
| `python3-dev`   | C headers for native Python extensions                   |
| `xserver-xorg-core` | Bare X server (installed by `display` role)          |
| `xinit`         | Starts X server from a script (installed by `display` role) |
| `x11-xserver-utils` | `xset` for display power/screensaver control         |
| `plymouth`      | Boot splash daemon (all nodes)                           |
| `rpd-plym-splash` | RPi Desktop pix splash theme (all nodes)               |

### Python package (in venv)

| Package      | Source                        |
|--------------|-------------------------------|
| `python-mpv` | Installed via `uv pip install` |

`python-mpv` is **not** in `pyproject.toml` because it requires `libmpv.so`
at runtime and would cause import errors on nodes that don't have mpv installed.
The tate Ansible role installs it explicitly into the venv after mpv is present.

---

## Boot splash (all nodes)

All nodes display `media/boot_logo.png` as the Plymouth splash screen during boot.
Boot messages are suppressed via kernel parameters in `/boot/firmware/cmdline.txt`:

```
quiet splash loglevel=3 logo.nologo vt.global_cursor_default=0 plymouth.ignore-serial-consoles
```

These flags are added idempotently by the `common` Ansible role. The initramfs is
rebuilt automatically whenever the logo changes.

---

## Deployment

### Prerequisites

1. Fresh Raspberry Pi OS Lite installed on the SD card.
2. SSH enabled on the Pi (`sudo systemctl enable ssh`).
3. Node reachable at `192.168.0.192`.
4. **raspi-config**: Console Autologin enabled for user `zero` (see above).

### Full setup

```bash
# From the solrunners project root
cd ansible
ansible-playbook playbooks/setup-tate.yml \
    --extra-vars "ansible_password=sh4d0w ansible_become_password=sh4d0w"
```

### Media sync (after setup or when clips change)

```bash
cd ansible
ansible-playbook playbooks/deploy-media.yml \
    --limit tate-node \
    --extra-vars "ansible_password=sh4d0w ansible_become_password=sh4d0w"
```

### Update boot logo only (all nodes)

```bash
cd ansible
ansible-playbook playbooks/setup-boot-logo.yml \
    --extra-vars "ansible_password=sh4d0w ansible_become_password=sh4d0w"
```

---

## Service management

```bash
# SSH into the node first
ssh zero@192.168.0.192

# Check service status
systemctl status sol.tate.service

# Follow live logs
journalctl -u sol.tate.service -f

# Restart (e.g. after code change)
sudo systemctl restart sol.tate.service

# Stop playback
sudo systemctl stop sol.tate.service

# Run manually (for debugging — must have DISPLAY set)
cd ~/solrunners
DISPLAY=:0 .venv/bin/python tate.py
```

---

## Troubleshooting

### Black screen / no video

- Confirm media files are present: `ls ~/solrunners/media/tate/*.mp4`
- Check X server started: `journalctl -u sol.tate.service -n 20`
- Test mpv with X: `DISPLAY=:0 mpv --vo=gpu ~/solrunners/media/tate/1.mp4`
- Ensure `raspi-config → Console Autologin` is set (see requirements above)

### Screen tearing

- Confirm the service is using X11 (`vo=gpu`), not DRM (`vo=drm`)
- Check GPU memory split: add `gpu_mem=128` to `/boot/firmware/config.txt`

### No audio

- Check ALSA devices: `aplay -l`
- Test audio: `mpv --vo=null ~/solrunners/media/tate/1.mp4`
- Ensure HDMI audio is selected: may need `hdmi_drive=2` in `/boot/firmware/config.txt`

### ESC key not working

- With X11 + `vo=gpu`, the ESC binding is captured via the X11 window.
  The window must have keyboard focus — xinit sets this automatically.
- Fallback: `q` key also quits (same handler).
- Fallback: `sudo systemctl stop sol.tate.service`

### python-mpv fails to load libmpv

```
libmpv: cannot open shared object file
```
- Confirm `libmpv-dev` is installed: `dpkg -l libmpv-dev`
- Find the library: `ldconfig -p | grep mpv`

### Service restarts repeatedly

- Read the logs: `journalctl -u sol.tate.service -n 50`
- Exit code 203 (EXEC) = Python binary not executable — check venv ownership
- Run manually to see the Python traceback in the terminal
