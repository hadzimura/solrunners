# Redesign Proposal (AI Layer)

## Goals

1. Keep original Raspberry Pi runtime unchanged by default.
2. Enable local macOS testing with a single argument switch.
3. Avoid editing original source files.

## Implemented changes

### 1) System selector

A new helper file `modules/Config.ai.py` adds `--system` parsing:

- `rpi` (default): keeps headless behavior for legacy scripts.
- `macos`: forces non-headless pyglet mode to avoid `EGL` loading path.

### 2) Wrapper entrypoints

- `Entro.ai.py` delegates to `Entro.py`
- `Heads.ai.py` delegates to `Heads.py`

Both wrappers:

1. Parse and strip `--system`.
2. Configure and lock `pyglet.options['headless']` for selected target.
3. Run the original script via `runpy` with remaining args.

### 3) Fountain runtime split

`Fountain.py` currently references arguments/fields that do not exist in `modules/Config.py`.

`Fountain.ai.py` is an audio-only runtime that:

- keeps the original cycle pattern,
- supports `--system` switch,
- uses platform audio players (`afplay` on macOS, `aplay`/`ffplay` on Linux/RPi),
- can run one cycle via `--single-cycle`.

### 4) Unified launcher

`sol.ai.py` now routes object startup through one command:

- `--object entropy|heads|fountain`
- `--system rpi|macos`

## Command examples

```zsh
python3 Entro.ai.py --system macos --fullscreen
python3 Heads.ai.py --system macos --fullscreen --recognition
python3 Fountain.ai.py --system macos --single-cycle
```

## Residual risks

- Legacy `pyglet` behavior differences across versions can still affect timing.
- `Fountain.ai.py` overlapping playback timing depends on system audio tools.
- Some RPi images might need explicit audio package installation (`alsa-utils`, `ffmpeg`).

## Simplification opportunities

1. Move all object runtimes behind one launcher command, e.g. `python3 sol.ai.py --object entropy --system macos`.
2. Replace pyglet audio in Entro/Heads with a single backend (e.g. VLC or ffplay) and drive sync from timestamps.
3. Use one process supervisor (`systemd`) instead of shell-login-triggered `startx` in `.bashrc`.
4. Keep media source fixed and skip SHM sync unless profiling confirms benefit on RPi 5.

### 5) AI systemd units

Added dedicated units and xinit scripts that run Entropy/Heads without a window manager:

- `configurations/systemd/sol.entropy.ai.service`
- `configurations/systemd/sol.heads.ai.service`
- `configurations/systemd/sol.fountain.ai.service`
- `configurations/xinit.entropy.ai.sh`
- `configurations/xinit.heads.ai.sh`
- `configurations/set_systemd.ai.sh`
