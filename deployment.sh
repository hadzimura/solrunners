#!/usr/bin/env bash
# deployment.sh — Interactive Springs of Life deployment launcher
# ─────────────────────────────────────────────────────────────────────────────
# Run from the repository root:  ./deployment.sh
# Ansible runs from the project venv — no system-level install needed.
# Create/update the venv with:   uv sync
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Locate repo root, venv binaries, and ansible/ dir ────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
ANSIBLE_BIN="${VENV_DIR}/bin/ansible-playbook"
GALAXY_BIN="${VENV_DIR}/bin/ansible-galaxy"
ANSIBLE_DIR="${SCRIPT_DIR}/ansible"

# ── Colours (disable if not a terminal) ──────────────────────────────────────
if [ -t 1 ]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
    CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; RESET=''
fi

# ── Helpers ───────────────────────────────────────────────────────────────────
header() {
    echo -e "\n${CYAN}${BOLD}╔══════════════════════════════════════╗${RESET}"
    echo -e "${CYAN}${BOLD}║  Springs of Life — Deployment Tool  ║${RESET}"
    echo -e "${CYAN}${BOLD}╚══════════════════════════════════════╝${RESET}\n"
}
section() { echo -e "\n${YELLOW}▶ $*${RESET}"; }
ok()      { echo -e "${GREEN}✔ $*${RESET}"; }
err()     { echo -e "${RED}✘ $*${RESET}" >&2; }

# ── Pre-flight: venv must exist ───────────────────────────────────────────────
if [ ! -x "${ANSIBLE_BIN}" ]; then
    err "Ansible not found in venv (${ANSIBLE_BIN})."
    echo "Run:  uv sync"
    exit 1
fi

# ── Pre-flight: install ansible.posix collection if missing ──────────────────
# ansible.posix is needed for the synchronize (rsync) module used in deploy-media.
if ! "${GALAXY_BIN}" collection list 2>/dev/null | grep -q "ansible.posix"; then
    section "Installing ansible.posix collection (first-time setup)…"
    "${GALAXY_BIN}" collection install ansible.posix
    ok "ansible.posix installed."
fi

# ── Ensure ansible/ directory is present ─────────────────────────────────────
if [ ! -d "${ANSIBLE_DIR}" ]; then
    err "ansible/ directory not found at ${ANSIBLE_DIR}"
    exit 1
fi

cd "${ANSIBLE_DIR}"

# ─────────────────────────────────────────────────────────────────────────────
header

# ── STEP 1: Choose a playbook ─────────────────────────────────────────────────
section "Which operation do you want to perform?"
echo ""

PLAYBOOKS=(
    "setup-fountain    — Full setup of Fountain node (RPi 3, audio-only)"
    "setup-entropy     — Full setup of Entropy node (RPi 5, M.2 SSD, 16:9 video)"
    "setup-heads       — Full setup of Heads node (RPi 5, SD card, 10:16 video)"
    "setup-tate        — Full setup of Tate node (RPi, random MP4 loop, DRM/KMS)"
    "deploy-media      — Sync media files to one or all RPi nodes"
    "restart-services  — Pull latest code + restart service on a target RPi"
    "quit              — Exit without doing anything"
)

PS3=$'\nEnter number: '
select choice in "${PLAYBOOKS[@]}"; do
    PLAYBOOK_KEY="${choice%% *}"   # extract first word (the key before the dash)
    case "${PLAYBOOK_KEY}" in
        setup-fountain|setup-entropy|setup-heads|setup-tate|deploy-media|restart-services)
            PLAYBOOK="playbooks/${PLAYBOOK_KEY}.yml"
            ok "Selected playbook: ${PLAYBOOK}"
            break ;;
        quit)
            echo "Bye."; exit 0 ;;
        *)
            err "Invalid selection, try again." ;;
    esac
done

# ── STEP 2: Choose a target node ──────────────────────────────────────────────
# For setup playbooks the target is fixed (the playbook already specifies hosts).
# For deploy-media and restart-services we allow per-node targeting.

LIMIT_FLAG=""

if [[ "${PLAYBOOK_KEY}" == "deploy-media" || "${PLAYBOOK_KEY}" == "restart-services" ]]; then
    section "Which RPi node should be targeted?"
    echo ""

    NODES=(
        "all             — All nodes (unreachable ones are skipped)"
        "tate-node       — RPi   @ 192.168.0.192 (Tate)"
        "entropy-node    — RPi 5 @ 192.168.0.190 (Entropy)"
        "heads-node      — RPi 5 @ TBD           (Heads)"
        "fountain-node   — RPi 3 @ TBD           (Fountain)"
    )

    PS3=$'\nEnter number: '
    select node_choice in "${NODES[@]}"; do
        NODE_KEY="${node_choice%% *}"
        case "${NODE_KEY}" in
            all|tate-node|entropy-node|heads-node|fountain-node)
                if [[ "${NODE_KEY}" != "all" ]]; then
                    LIMIT_FLAG="--limit ${NODE_KEY}"
                fi
                ok "Target: ${NODE_KEY}"
                break ;;
            *)
                err "Invalid selection, try again." ;;
        esac
    done
fi

# ── STEP 3: Authentication ────────────────────────────────────────────────────
section "Authentication"
echo ""
echo "All RPi nodes use password authentication."
echo "You will be prompted for the SSH password (and sudo password if needed)."
echo ""

# Decide whether this playbook needs privilege escalation (become/sudo).
# Setup and restart playbooks do; media-only sync does not.
BECOME_FLAG="--ask-become-pass"
if [[ "${PLAYBOOK_KEY}" == "deploy-media" ]]; then
    BECOME_FLAG=""
fi

# ── STEP 4: Dry-run option ────────────────────────────────────────────────────
section "Dry-run?"
echo ""
echo "A dry-run checks what WOULD be changed without actually changing anything."
read -rp "Run in dry-run (check) mode? [y/N]: " dryrun_answer
CHECK_FLAG=""
if [[ "${dryrun_answer,,}" == "y" ]]; then
    CHECK_FLAG="--check"
    echo -e "${YELLOW}Dry-run mode enabled.${RESET}"
fi

# ── STEP 5: Confirmation ──────────────────────────────────────────────────────
section "Summary"
echo ""
echo -e "  Playbook : ${BOLD}${PLAYBOOK}${RESET}"
echo -e "  Target   : ${BOLD}${LIMIT_FLAG:-all hosts in playbook}${RESET}"
echo -e "  Dry-run  : ${BOLD}${CHECK_FLAG:-(no)}${RESET}"
echo ""
read -rp "Proceed? [y/N]: " confirm
if [[ "${confirm,,}" != "y" ]]; then
    echo "Aborted."; exit 0
fi

# ── STEP 6: Run ansible-playbook from the project venv ───────────────────────
section "Running Ansible…"
echo ""

# shellcheck disable=SC2086
"${ANSIBLE_BIN}" \
    "${PLAYBOOK}" \
    --ask-pass \
    ${BECOME_FLAG} \
    ${LIMIT_FLAG} \
    ${CHECK_FLAG} \
    -v

echo ""
ok "Done."
