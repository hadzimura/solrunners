# Springs of Life — Ansible Deployment Guide

## Requirements (control node — your Mac)

```bash
brew install ansible
ansible-galaxy collection install ansible.posix   # provides synchronize module
```

## Quick start

```bash
cd /path/to/solrunners
./deployment.sh
```

The script will walk you through:
1. Choosing a playbook (setup / media sync / service restart)
2. Choosing a target node (for media sync and restarts)
3. Optional dry-run mode
4. Running `ansible-playbook` with the correct flags

---

## Playbook reference

| Playbook | Target | What it does |
|----------|--------|--------------|
| `setup-fountain.yml` | `fountain` group | Full OS setup + audio packages + service |
| `setup-entropy.yml`  | `entropy` group  | Full OS setup + minimal X11 + service |
| `setup-heads.yml`    | `heads` group    | Full OS setup + minimal X11 + service |
| `deploy-media.yml`   | any (use `--limit`) | Rsync media files from Mac → RPi |
| `restart-services.yml` | any (use `--limit`) | Git pull + pip update + service restart |

---

## Inventory

Edit `ansible/inventory/hosts.yml` to update IP addresses as nodes come online.

```
entropy-node:   192.168.0.190   (available)
heads-node:     TBD
fountain-node:  TBD
```

---

## Roles

| Role     | Used by          | Responsibility |
|----------|------------------|----------------|
| common   | all nodes        | apt update, git clone, Python venv, `/storage` tmpfs |
| display  | entropy, heads   | xserver-xorg-core, xinit, libgtk-3, unclutter |
| fountain | fountain only    | alsa-utils, ffmpeg, ALSA config, systemd service |
| entropy  | entropy only     | systemd service deployment |
| heads    | heads only       | systemd service deployment |
| media    | all (on demand)  | rsync media files via Ansible synchronize |

---

## Variables

Key variables live in `ansible/inventory/group_vars/`:

| Variable | Default | Description |
|----------|---------|-------------|
| `sol_repo_path` | `/home/zero/solrunners` | Repository location on RPi |
| `sol_venv_path` | `/home/zero/solrunners/.venv` | Python venv |
| `sol_storage_size_mb` | `4096` | tmpfs size for `/storage` |
| `sol_media_subdir` | (per group) | Which media folder to sync |
| `sol_service_name` | (per group) | systemd service name |
| `sol_git_branch` | `main` | Branch to deploy |

---

## Authentication

- SSH: password authentication (`--ask-pass` flag)
- Sudo: same password (`--ask-become-pass` flag)
- Password is prompted interactively — **never stored in files**

To add SSH key authentication later (recommended for production):
```bash
ssh-copy-id zero@<rpi-ip>
# Then remove --ask-pass from deployment.sh
```

---

## Adding a new node

1. Flash RPi OS Lite, boot, enable SSH
2. Note the IP address and WiFi MAC address
3. Add to `ansible/inventory/hosts.yml` under the correct group
4. Update `docs/DEPLOYMENT.md` with network details
5. Run `./deployment.sh` → choose the appropriate setup playbook

---

## Troubleshooting

**"UNREACHABLE"** — Check the IP in `hosts.yml` and that the RPi is online.

**"Missing sudo password"** — Use `--ask-become-pass` or ensure passwordless sudo:
```bash
echo "zero ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/zero
```

**Media rsync very slow** — Normal for large `.mov` files over WiFi.
Use ethernet for initial media deployment if possible.

**Service not starting** — Check logs on the RPi:
```bash
journalctl -u sol.entropy.ai.service -f
```

**OpenCV cannot open display** — The X server may not be starting.  Check:
```bash
journalctl -u sol.entropy.ai.service --no-pager | grep -i "error\|xinit"
```
