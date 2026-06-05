# TATE — Springs of Life: Tate Node

## Overview

The **Tate** node is a Raspberry Pi that plays a collection of short MP4 video
clips (with sound) in an endless, randomised loop for gallery display.

### Key properties

| Property         | Value                                          |
|------------------|------------------------------------------------|
| Hardware         | Raspberry Pi (any model with DRM/KMS support)  |
| OS user          | `zero`                                         |
| IP address       | `192.168.0.192`                                |
| Display output   | HDMI (full-screen, no Xorg / Wayland)          |
| Player           | mpv via `python-mpv` (DRM/KMS framebuffer)     |
| Media location   | `media/tate/*.mp4`                             |
| Loop behaviour   | Endless random, no-repeat window of 5 picks    |
| Quit key         | **ESC**                                        |

---

## Architecture

```
systemd: sol.tate.service
   └── /home/zero/solrunners/.venv/bin/python tate.py
           └── mpv (libmpv, vo=drm, ao=alsa)
                   └── renders to /dev/dri/card0 (DRM/KMS framebuffer)
```

### Why mpv over VLC / omxplayer?

| Criterion          | mpv (chosen)                       | VLC                          |
|--------------------|------------------------------------|------------------------------|
| No-Xorg playback   | ✅ `vo=drm` built-in               | ❌ Requires Xorg or Wayland  |
| Python API         | ✅ `python-mpv` (ctypes, official) | ⚠️ subprocess / HTTP only   |
| Key-event handling | ✅ `on_key_press()` callback        | ❌ Complex                   |
| RPi GPU decoding   | ✅ `hwdec=v4l2m2m` supported       | ✅ Also supported            |
| Maintenance        | ✅ Actively maintained             | ✅ Actively maintained       |

`omxplayer` is no longer maintained and was removed from Raspberry Pi OS Bullseye onwards.

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

## File inventory

| Path                                              | Purpose                              |
|---------------------------------------------------|--------------------------------------|
| `tate.py`                                         | Main player application              |
| `media/tate/*.mp4`                                | Video clips (35 clips, 1–30 s each)  |
| `media/boot_logo.png`                             | Boot splash image (all nodes)        |
| `configurations/systemd/sol.tate.service`         | systemd unit file                    |
| `ansible/playbooks/setup-tate.yml`                | Full node setup playbook             |
| `ansible/playbooks/setup-boot-logo.yml`           | Boot splash update playbook          |
| `ansible/roles/tate/tasks/main.yml`               | Ansible role tasks                   |
| `ansible/roles/tate/handlers/main.yml`            | Ansible role handlers                |
| `ansible/inventory/group_vars/tate.yml`           | Node variables                       |

---

## System packages installed

| Package        | Purpose                                                 |
|----------------|---------------------------------------------------------|
| `mpv`          | Player binary + shared `libmpv.so`                      |
| `libmpv-dev`   | Provides the `libmpv.so` symlink required by python-mpv |
| `python3-dev`  | C headers for native Python extensions                  |
| `plymouth`     | Boot splash daemon (all nodes)                          |
| `plymouth-themes-pix` | Full-screen PNG splash theme (all nodes)         |

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
2. Node is reachable at `192.168.0.192` (check with `ping 192.168.0.192`).
3. SSH enabled on the Pi (create empty `ssh` file in boot partition if needed).

### Full setup

```bash
# From the solrunners project root (with the venv active)
ansible-playbook ansible/playbooks/setup-tate.yml \
    --ask-pass --ask-become-pass
# SSH password:    sh4d0w
# Become password: sh4d0w
```

### Media sync (after setup or when clips change)

```bash
ansible-playbook ansible/playbooks/deploy-media.yml \
    --limit tate-node --ask-pass
```

### Update boot logo only (all nodes)

```bash
ansible-playbook ansible/playbooks/setup-boot-logo.yml \
    --ask-pass --ask-become-pass
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

# Run manually (for debugging)
cd ~/solrunners
.venv/bin/python tate.py
```

---

## Troubleshooting

### Black screen / no video

- Confirm media files are present: `ls ~/solrunners/media/tate/*.mp4`
- Check DRM device: `ls /dev/dri/` — should show `card0`
- Test mpv directly: `mpv --vo=drm ~/solrunners/media/tate/1.mp4`

### No audio

- Check ALSA devices: `aplay -l`
- Test audio: `mpv --vo=null --ao=alsa ~/solrunners/media/tate/1.mp4`
- Ensure HDMI audio is selected if using HDMI output (may need `/boot/firmware/config.txt` changes)

### python-mpv fails to load libmpv

```
libmpv: cannot open shared object file
```
- Confirm `libmpv-dev` is installed: `dpkg -l libmpv-dev`
- Find the library: `ldconfig -p | grep mpv`

### Service restarts repeatedly

- Read the logs: `journalctl -u sol.tate.service -n 50`
- Run manually to see the Python traceback in the terminal
