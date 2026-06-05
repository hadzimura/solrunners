# AI Deployment Guide

## Runtime choice

All AI entrypoints accept:

- `--system rpi` (default)
- `--system macos`

## Local macOS test commands

```zsh
cd /Users/zero/Documents/Develop/hadzimura/solrunners
./.venv/bin/python test.ai.py
./.venv/bin/python sol.ai.py --object entropy --system macos --fullscreen
./.venv/bin/python sol.ai.py --object heads --system macos --fullscreen --recognition
./.venv/bin/python sol.ai.py --object fountain --system macos --single-cycle
```

## Raspberry Pi 5 deployment (no window manager)

### 1) Install/refresh AI units and scripts

```bash
cd /home/zero/solrunners
chmod +x configurations/set_systemd.ai.sh
chmod +x configurations/xinit.entropy.ai.sh
chmod +x configurations/xinit.heads.ai.sh
```

### 2) Enable service per node role

Entropy node:

```bash
/home/zero/solrunners/configurations/set_systemd.ai.sh entropy
```

Heads node:

```bash
/home/zero/solrunners/configurations/set_systemd.ai.sh heads
```

Fountain node:

```bash
/home/zero/solrunners/configurations/set_systemd.ai.sh fountain
```

### 3) Validate runtime status

```bash
systemctl status sol.entropy.ai.service --no-pager
systemctl status sol.heads.ai.service --no-pager
systemctl status sol.fountain.ai.service --no-pager
journalctl -u sol.entropy.ai.service -n 80 --no-pager
```

## Notes

- Entropy/Heads services use `xinit` directly and do not start `matchbox-window-manager`.
- Fountain is audio-only and runs without Xorg.
- Keep `media/tate` untouched.
