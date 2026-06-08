# FOUNTAIN — Springs of Life: Fountain Node

## Overview

The **Fountain** node is an audio-only Raspberry Pi that plays `fountain.wav`
in an endless loop with a randomised silence interval between plays. It has no
display and requires no Xorg or display server.

The node is designed in two phases:

| Phase | Status | Description |
|-------|--------|-------------|
| **1** | ✅ Implemented | WAV loop, static L/R gain, random silence |
| **2** | 🔜 Planned | Two HCY-SRF05 ultrasonic sensors → dynamic per-channel volume based on spectator distance |

---

## Phase 1 — WAV loop with static stereo gain

### Key properties

| Property         | Value                                            |
|------------------|--------------------------------------------------|
| Hardware         | Raspberry Pi 3 (or newer), no display            |
| OS user          | `zero`                                           |
| Audio output     | 3.5 mm jack (ALSA card 0, device 0)              |
| Player           | `sounddevice` + `soundfile` + `numpy` (Python)   |
| Media            | `media/fountain/fountain.wav` (stereo, 48 kHz)   |
| Loop behaviour   | Endless: play → silence → play → …               |
| Silence interval | `silence_base + random(0, silence_random)` seconds |
| Default silence  | 10 s base + 0–10 s random = 10–20 s total        |
| L/R gain         | Configurable, default 1.0 / 1.0                  |

### Playback cycle

```
┌──────────────────────────────────────────────┐
│  1. Apply L/R gain to audio array (numpy)     │
│  2. Play fountain.wav via PortAudio            │
│  3. Wait for playback to finish                │
│  4. silence = base + uniform(0, random_max)   │
│  5. Sleep silence seconds (interruptible)      │
│  6. Go to 1                                    │
└──────────────────────────────────────────────┘
```

SIGTERM / SIGINT interrupt the sleep and stop playback immediately.

### Architecture

```
systemd: sol.fountain.service
   └── fountain.py  (.venv/bin/python)
           │  load WAV once at startup (SD idle during loop)
           └── sounddevice.play(audio * gain, samplerate)
                   └── PortAudio → ALSA → 3.5 mm jack → speakers
```

### Configuration (ExecStart args in sol.fountain.service)

| Argument | Default | Description |
|----------|---------|-------------|
| `--wav` | `media/fountain/fountain.wav` | WAV file path |
| `--silence-base` | `10` | Minimum silence between plays (s) |
| `--silence-random` | `10` | Max extra random silence (s) |
| `--gain-left` | `1.0` | Left channel gain (0.0–1.0) |
| `--gain-right` | `1.0` | Right channel gain (0.0–1.0) |

To adjust balance (e.g. right speaker louder), edit `sol.fountain.service`:
```
ExecStart=... fountain.py --gain-left 0.8 --gain-right 1.0
```
Then `sudo systemctl daemon-reload && sudo systemctl restart sol.fountain.service`.

---

## Phase 2 — Ultrasonic presence detection (planned)

### Concept

Two **HCY-SRF05** ultrasonic distance sensors are placed in opposing or
perpendicular directions (e.g. North + South, or North + West). Each sensor
is mapped to one audio channel:

```
Spectator approaches from North  →  Sensor A fires  →  LEFT channel louder
Spectator approaches from South  →  Sensor B fires  →  RIGHT channel louder
Both present simultaneously       →  both channels at full volume
Nobody present                    →  ambient minimum (10% volume floor)
```

### Distance-to-volume mapping

```
distance ≤ MIN_CM  (default 20 cm)  →  gain = 1.0   (full volume)
distance ≥ MAX_CM  (default 200 cm) →  gain = 0.1   (ambient floor)
between:  linear interpolation

gain = max(0.1,  1.0 - (dist - MIN) / (MAX - MIN) * 0.9)
```

Gain is smoothed with an exponential moving average (α = 0.1) to prevent
audible clicks from sensor jitter. The audio loop switches from pre-baked
`apply_gain()` to a `sounddevice` streaming callback that re-reads sensor
distances every ~10 ms audio block.

### Why `sounddevice` + numpy (not aplay or mpv)

| Option | Real-time L/R control | Notes |
|--------|-----------------------|-------|
| `aplay` subprocess | ❌ | Can only start/stop |
| two `mpv` instances | ⚠️ | IPC sockets, not sample-accurate |
| `pygame.mixer` | ⚠️ | No true per-channel gain |
| **`sounddevice` + numpy** | ✅ | Callback runs per-block; `out[:,0] *= gain_l` |

---

## Hardware guide — Phase 2

### Components required

| Component | Qty | Notes |
|-----------|-----|-------|
| HCY-SRF05 ultrasonic sensor | 2 | 5V, 2–450 cm range, ±1 cm accuracy |
| 1 kΩ resistor | 2 | Voltage divider (ECHO line) |
| 2 kΩ resistor (or two 1 kΩ in series) | 2 | Voltage divider (ECHO line) |
| Jumper wires | ~12 | Male-to-female for breadboard → RPi header |
| Small breadboard | 1 | For voltage dividers |

### ⚠️ Critical: Voltage divider on ECHO pin

The SRF05 operates at **5V** and its ECHO output is a **5V logic signal**.
The Raspberry Pi GPIO inputs are **3.3V maximum** — connecting ECHO directly
**will permanently damage the Pi's GPIO controller**.

Each ECHO line must be stepped down with a resistor voltage divider:

```
SRF05 ECHO ──[1kΩ]──┬──── RPi GPIO input (3.3V safe)
                     │
                   [2kΩ]
                     │
                    GND

Output voltage = 5V × 2kΩ/(1kΩ+2kΩ) = 3.33V  ✅
```

TRIG is safe to connect directly — the SRF05 TRIG input accepts 3.3V signals.

### Wiring table

| Signal | Sensor A (e.g. North) | Sensor B (e.g. South/West) | RPi pin | GPIO (BCM) |
|--------|-----------------------|----------------------------|---------|------------|
| VCC | Pin 1 | Pin 1 | Pin 2 | 5V |
| GND | Pin 2 | Pin 2 | Pin 6 | GND |
| TRIG A | Pin 3 | | Pin 16 | GPIO 23 |
| ECHO A | Pin 4 → divider | | Pin 18 | GPIO 24 |
| TRIG B | | Pin 3 | Pin 22 | GPIO 25 |
| ECHO B | | Pin 4 → divider | Pin 24 | GPIO 8 |

### RPi 3 GPIO header reference (relevant pins)

```
         3V3  [ 1] [ 2]  5V       ← SRF05 VCC here (5V)
       GPIO2  [ 3] [ 4]  5V
       GPIO3  [ 5] [ 6]  GND      ← SRF05 GND here
       GPIO4  [ 7] [ 8]  GPIO14
         GND  [ 9] [10]  GPIO15
      GPIO17  [11] [12]  GPIO18
      GPIO27  [13] [14]  GND
      GPIO22  [15] [16]  GPIO23   ← TRIG A
        3V3   [17] [18]  GPIO24   ← ECHO A (via divider)
      GPIO10  [19] [20]  GND
       GPIO9  [21] [22]  GPIO25   ← TRIG B
      GPIO11  [23] [24]  GPIO8    ← ECHO B (via divider)
         GND  [25] [26]  GPIO7
```

### SRF05 jumper setting

The HCY-SRF05 has a **mode jumper** on the board:
- **Jumper installed** (pin 5 connected): Single-wire mode (TRIG and ECHO share one pin) — **do not use**
- **Jumper absent**: Two-wire mode (separate TRIG + ECHO) — **use this**

Leave the jumper uninstalled for standard two-wire operation.

### Phase 2 new Python dependencies

| Package | Purpose |
|---------|---------|
| `gpiozero` | `DistanceSensor` class wraps SRF05 TRIG/ECHO timing |
| `RPi.GPIO` | gpiozero backend for GPIO access |

Both are available as system packages (`python3-gpiozero`, `python3-rpi.gpio`)
and will be added to `sol_audio_packages` in `group_vars/fountain.yml`.

---

## System packages

| Package | Purpose |
|---------|---------|
| `alsa-utils` | `aplay` for manual audio testing |
| `libportaudio2` | PortAudio runtime — required by `sounddevice` |
| `portaudio19-dev` | PortAudio headers — needed to build `sounddevice` wheel |
| `libsndfile1` | libsndfile runtime — required by `soundfile` Python package |

### Python packages (venv)

| Package | Notes |
|---------|-------|
| `sounddevice` | NOT in pyproject.toml — requires libportaudio2 (fountain-only) |
| `soundfile` | NOT in pyproject.toml — requires libsndfile1 (fountain-only) |
| `numpy` | In pyproject.toml — shared with all nodes |

---

## Deployment

### Prerequisites

1. Fresh Raspberry Pi OS Lite on SD card, SSH enabled.
2. Node reachable on the network — update `ansible_host` in `hosts.yml`.
3. Speakers connected to 3.5 mm jack (or USB audio if using card 1).

### Full setup

```bash
cd ansible
ansible-playbook playbooks/setup-fountain.yml \
    --extra-vars "ansible_password=sh4d0w ansible_become_password=sh4d0w"
```

### Media sync

```bash
cd ansible
ansible-playbook playbooks/deploy-media.yml \
    --limit fountain-node \
    --extra-vars "ansible_password=sh4d0w ansible_become_password=sh4d0w"
```

---

## Service management

```bash
ssh zero@<fountain-ip>

systemctl status sol.fountain.service
journalctl -u sol.fountain.service -f

# Adjust gain without redeploying: edit service file on Pi
sudo nano /etc/systemd/system/sol.fountain.service
# change --gain-left / --gain-right values, then:
sudo systemctl daemon-reload && sudo systemctl restart sol.fountain.service
```

---

## Troubleshooting

### No audio output

- Check ALSA devices: `aplay -l`
- Test directly: `aplay -D default media/fountain/fountain.wav`
- If using HDMI monitor with speakers: update `/etc/asound.conf` to card 1
- Check volume: `alsamixer` → raise PCM / Master

### sounddevice import error

```
OSError: PortAudio library not found
```
- Confirm `libportaudio2` is installed: `dpkg -l libportaudio2`
- Reinstall: `sudo apt install libportaudio2`

### Service exits with code 1

- Run manually: `cd ~/solrunners && .venv/bin/python fountain.py`
- Check WAV path: `ls media/fountain/fountain.wav`
- Check storage service: `systemctl status storage.service`

### SD card wear

The WAV file is loaded once at startup into RAM — the SD card is not read
during the playback loop. See `docs/TATE.md` → SD card wear reduction for
the full three-layer strategy (`noatime`, tmpfs, `rootflags=noatime`).
