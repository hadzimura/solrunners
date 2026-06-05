# Springs of Life — AI Context Document
*Last updated: 2026-05-24*

---

## Purpose of this document

This file is the **canonical starting brief** for any AI agent (or human engineer)
beginning a new session on this repository from scratch.  Read it before touching
anything else.

---

## Project overview

**Springs of Life** is a digital art exhibition by the Sucher family archive.
Five Raspberry Pi computers act as audio/visual objects installed in three
different rooms.  This repository contains the Python application code and the
Ansible deployment infrastructure for those devices.

---

## Hardware matrix

| Object   | RPi model | RAM  | Storage      | Display            | Aspect  | Resolution  | Audio              |
|----------|-----------|------|--------------|--------------------|---------|-------------|--------------------|
| Fountain | RPi 3     | 2 GB | SD card      | **None** (headless)| —       | —           | mono speaker (jack)|
| Entropy  | RPi 5     | 8 GB | M.2 SSD 128G | Sony TV (HD Ready) | 16:9    | 1360×768    | stereo built-in    |
| Heads    | RPi 5     | 8 GB | SD card 16G  | EIZO 24"           | **10:16** vertical | 1050×1680 | stereo amplifier |

> Two further nodes (*Tate* and *Credits*) exist in the full exhibition but are
> **not in scope** for this Ansible deployment cycle.

---

## Network

| Node          | IP address      | WiFi MAC            | Status         |
|---------------|-----------------|---------------------|----------------|
| entropy-node  | 192.168.0.190   | 2C:CF:67:AB:95:2A   | Known/available|
| heads-node    | TBD             | TBD                 | Not yet connected |
| fountain-node | TBD             | TBD                 | Not yet connected |

Deployment control node: developer's Mac (this machine), via SSH password auth.
SSH user on all RPis: `zero`  (password supplied interactively at deploy time —
**never committed to the repository**).

---

## Operating system

All RPi nodes run **Raspberry Pi OS Lite (64-bit)** — Bookworm-based, no desktop.
The OS is installed manually before Ansible takes over.

---

## Repository structure

```
solrunners/
├── Fountain.ai.py          # Fountain runtime — subprocess audio (aplay/ffplay)
├── Fountain.py             # Fountain runtime — original pyglet version (legacy)
├── Entro.ai.py             # Entropy wrapper → loads Config.ai.py → runs Entro.py
├── Entro.py                # Entropy main loop: OpenCV video + pyglet audio
├── Heads.ai.py             # Heads wrapper → loads Config.ai.py → runs Heads.py
├── Heads.py                # Heads main loop: OpenCV video + face detection + audio
├── modules/
│   ├── Config.py           # Configuration class + arg_parser + wait_for_storage
│   └── Config.ai.py        # AI wrapper helpers: pyglet headless guard, runpy launcher
├── configurations/
│   ├── xinit.entropy.ai.sh # xinit script: xrandr + launch Entro.ai.py
│   ├── xinit.heads.ai.sh   # xinit script: xrandr --rotate left + launch Heads.ai.py
│   ├── systemd/
│   │   ├── sol.entropy.ai.service   # systemd unit for Entropy (xinit-based)
│   │   ├── sol.heads.ai.service     # systemd unit for Heads (xinit-based)
│   │   ├── sol.fountain.ai.service  # systemd unit for Fountain (direct python)
│   │   ├── storage.service          # copies media → /storage (tmpfs) at boot
│   │   └── media_to_shm.sh          # rsync script called by storage.service
│   └── .bashrc             # reference bashrc (Ansible deploys bashrc.j2 template)
├── media/                  # NOT in git — synced via Ansible deploy-media playbook
│   ├── entropy/            # entropy.mov, entropy.wav, countdown.*, entropy_qr.png
│   ├── heads/              # silent_heads.mov, silent_heads.wav, samples/*.wav,
│   │                       #   quotes/*.png (21 subtitle PNGs), face_detections/
│   └── fountain/           # fountain.wav + optional talking-head samples
├── ansible/                # Ansible deployment infrastructure
│   ├── ansible.cfg         # Ansible configuration (inventory path, SSH opts)
│   ├── inventory/
│   │   ├── hosts.yml       # RPi host definitions with IP addresses
│   │   └── group_vars/     # Per-group variables (all, fountain, entropy, heads)
│   ├── roles/
│   │   ├── common/         # Base OS setup: apt, git clone, venv, pip, tmpfs
│   │   ├── display/        # Minimal X11: xserver-xorg-core, xinit, libgtk-3
│   │   ├── fountain/       # Audio packages + ALSA config + service
│   │   ├── entropy/        # Entropy service deployment
│   │   ├── heads/          # Heads service deployment
│   │   └── media/          # rsync media files from Mac → RPi
│   └── playbooks/
│       ├── setup-fountain.yml
│       ├── setup-entropy.yml
│       ├── setup-heads.yml
│       ├── deploy-media.yml
│       └── restart-services.yml
├── deployment.sh           # Interactive launcher for all Ansible playbooks
├── docs/
│   ├── AI_CONTEXT.md       # ← this file
│   ├── ANSIBLE.md          # Operator guide for Ansible deployment
│   └── DEPLOYMENT.md       # Manual deployment notes + network table
└── requirements.txt        # Python deps: numpy, pyglet==1.5.27, opencv-contrib-python, …
```

---

## Application architecture

### Fountain (audio-only)

- **Script**: `Fountain.ai.py`
- **Runtime**: subprocess → `aplay` (alsa-utils) or `ffplay` (ffmpeg)
- **No display stack needed** — headless
- Plays `media/fountain/fountain.wav` as the base loop
- Optionally overlaps a randomly selected `media/heads/samples/*.wav` "talking head"
- Random silence between cycles (`--min-delay` / `--max-delay` args)
- Systemd service: `sol.fountain.ai.service` → direct Python, no xinit

### Entropy (16:9 horizontal video)

- **Script**: `Entro.ai.py` (wrapper) → `Entro.py` (main logic)
- **Runtime**: Python 3 + OpenCV 4.11 + pyglet 1.5.27
- OpenCV reads `entropy.mov` frame-by-frame, applies colour effects and subtitle
  overlays, then displays via `cv2.imshow()`
- pyglet plays `entropy.wav` in headless mode; AV sync is achieved by adjusting
  `cv2.waitKey()` duration each frame
- Countdown intro sequence before main video
- Systemd service: `sol.entropy.ai.service` → `xinit xinit.entropy.ai.sh -- :0 -nocursor`

### Heads (10:16 vertical video)

- **Script**: `Heads.ai.py` (wrapper) → `Heads.py` (main logic)
- **Runtime**: Python 3 + OpenCV 4.11 + pyglet 1.5.27
- Plays `silent_heads.mov` with:
  - Per-frame blur transitions between "heads" (14 cuts, every ~1000 frames)
  - Overlay subtitle PNGs (`quotes/1-21.png`) blended via `cv2.addWeighted()`
  - Talking-head audio samples (`samples/*.wav`) via pyglet, with background
    music volume ducking
  - Optional Haar/LBP face-detection bounding boxes
- Display is portrait: xrandr `--rotate left` applied inside xinit script
- Systemd service: `sol.heads.ai.service` → `xinit xinit.heads.ai.sh -- :0 -nocursor`

### Display strategy: minimal X11

OpenCV's `cv2.imshow()` requires a display surface.  The chosen approach:

1. The systemd service launches `xinit <script> -- :0 -nocursor`
2. The xinit script configures the display (`xrandr`, `xset`) and immediately
   executes the Python application — **no window manager, no compositor, no DE**
3. This gives a bare X server with a single full-screen window

This is NOT a full Xorg desktop.  Only `xserver-xorg-core` + `xinit` are
installed by the `display` Ansible role.

**Future upgrade path**: Replace `cv2.imshow()` + `cv2.waitKey()` with direct
DRM/KMS framebuffer writes (numpy → `/dev/fb0` mmap) to eliminate Xorg entirely.
This requires modifying the display loop in `Entro.py` and `Heads.py`.

### /storage tmpfs

`modules/Config.py::wait_for_storage()` blocks on `/storage/.ready` before the
application starts.  At boot, `storage.service` runs `media_to_shm.sh` which
copies the media folder into a tmpfs mounted at `/storage`.  This reduces
repeated seeks on the SD card during video playback.

The Ansible `common` role mounts the tmpfs and enables `storage.service`.
Size is controlled per group: `sol_storage_size_mb` in `group_vars/`.

---

## uv — Python environment management

All nodes use [`uv`](https://docs.astral.sh/uv/) for venv and dependency management.

### On the RPis (Ansible-managed)
- Binary: `~/.local/bin/uv` (installed by `common` role)
- Venv: `/home/zero/solrunners/.venv` (created with `uv venv --python 3.11`)
- Deps: `uv pip install -r requirements.txt` (stable baseline, controlled by `sol_dep_mode`)

### On the development workstation
```bash
brew install uv   # or: curl -LsSf https://astral.sh/uv/install.sh | sh
cd solrunners/ && uv sync   # uses pyproject.toml + uv.lock
source .venv/bin/activate
```

### Dependencies — confirmed working stack
| Package | Pinned version | Notes |
|---------|---------------|-------|
| `pyglet` | `==1.5.27` | **Do not upgrade.** 2.x breaks the AV-sync loop in `Entro.py`/`Heads.py`. |
| `opencv-contrib-python` | latest | `contrib` variant required — includes Haar/LBP classifiers for face detection in `Heads.py`. |
| Python | `>=3.11` | 3.11 is the RPi baseline; newer versions untested with pyglet 1.5.27. |

`pyproject.toml`, `uv.lock`, and `requirements.txt` are **all in sync**. Use `uv sync` everywhere.

---

## TTY / login isolation design

| Session type | VT | App starts? | How |
|---|---|---|---|
| Boot (headless) | VT1 | ✅ Yes | systemd `sol.*.ai.service` runs `xinit ... -- :0 -nocursor` |
| SSH login | pts/x | ❌ No | `.bashrc` only activates venv; no app launch |
| Physical TTY5 (Ctrl+Alt+F5) | VT5 | ❌ No | Separate console; service already on VT1 |

`.bashrc` shows a maintenance hint (service name + log command) on SSH login.

---

## Known issues / technical debt

| Issue | Affected | Notes |
|-------|----------|-------|
| `pyglet` buffer overflow with many WAV files | Heads heavily | Root cause: pyglet 1.5.27 loads all `StaticSource` WAVs into a single OpenAL buffer; large collections exhaust it. Mitigation TBD — likely replace with streaming or subprocess playback similar to Fountain.ai.py. |
| `Heads.py` only loops once (`while cycle < 2`) | Heads | Line 422: `while cycle < 2` means a single pass then exits. Probably intentional for testing; should be `while True` for production. |
| `configurations/xinit.entropy.ai.sh` applies `xrandr --rotate normal` | Entropy | Correct — Entropy display is landscape 16:9. Fixed from an earlier erroneous `--rotate left`. |
| Fountain.py `arg_parser` mismatch | Fountain | `Fountain.py` uses `arg.room` and `arg.fountain_version` but `arg_parser()` in Config.py defines neither. `Fountain.ai.py` is the working replacement. |
| `storage.service` passes no argument to `media_to_shm.sh` | All | Script uses `$1` as media subdir but service passes none, so all of `media/` is copied. Functional but wasteful on Fountain (small node). |

---

## Deployment workflow

```
1. Flash Raspberry Pi OS Lite (64-bit) onto the SD card / SSD
2. Boot RPi, enable SSH, note IP address
3. Update ansible/inventory/hosts.yml with the IP
4. Run:  ./deployment.sh
   → Select: setup-<node>  (full OS + app setup, ~10–15 min)
5. Run:  ./deployment.sh
   → Select: deploy-media  (sync large media files, may take a while)
6. Reboot RPi:  ssh zero@<IP> sudo reboot
7. Verify service:  ssh zero@<IP> systemctl status sol.<node>.ai.service
```

---

## Session handoff checklist

When starting a new AI session on this project, verify:

- [ ] `ansible/inventory/hosts.yml` — are all node IPs up to date?
- [ ] `ansible/inventory/group_vars/heads.yml` — `sol_storage_size_mb` large enough for media?
- [ ] `configurations/xinit.entropy.ai.sh` — xrandr rotation correct for physical TV?
- [ ] `Heads.py` line 422 — loop count correct for production (`while True`)?
- [ ] pyglet buffer overflow in Heads — has a fix been implemented yet?
