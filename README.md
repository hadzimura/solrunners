# Springs of Life
**From the Sucher's family archives**

---

Exh. info

---

# Summary

Digital part of the exhibition consists of **five** Raspberry Pi computers installed as audio / visual objects within **three** different rooms of the exhibition.

---

# Hardware & software runtime

## Execution environment

All [Raspberry Pi](https://www.raspberrypi.com) boards use ([Raspberry Pi OS](https://www.raspberrypi.com/software/)) that runs [Xorg](https://www.x.org) graphical session in `kiosk-mode` using [matchbox-window-manager](https://github.com/NetPLC/matchbox-window-manager) at display-manager level. Except for the `Fountain` object which is headless.

| room | object       | Raspberry Pi | RAM | display            | aspect ratio | resolution  | audio             |
|------|--------------|--------------|-----|--------------------|--------------|-------------|-------------------|
| 3    | **Entropy**  | RPi 5        | 8GB | Sony TV `HD Ready` | `16:9`       | `1360x768`  | stereo built-in   | 
| 4    | **Fountain** | RPi 2B       | 1GB | `None`             | `n/a`        | `n/a`       | mono speaker      |
| 4    | **Tate**     | RPi 3        | 2GB | Dell `21"`         | `5:4`        | `640x480`   | stereo headphones |
| 5    | **Heads**    | RPi 5        | 8GB | EIZO `24"`         | `10:16`      | `1050x1680` | stereo amplifier  |
| 5    | **Credits**  | RPi 5        | 8GB | EIZO `24"`         | `10:16`      | `1050x1680` | `None`            |

Configurations of the operating system runtime are available within the [configurations](configurations) folder of this repository. 

## Application software

Each object uses either:

### cvlc

Commandline version of the [VideoLAN](https://www.videolan.org) media player that plays either randomly chosen video (Tate) or simply loops single video. Runtime arguments used are available here: [TBD]

### python3

Entropy and Heads objects use [Python 3.11](https://python.org) interpreter for real-time post-processing of pre-recorder audio-video artefacts. To do so, there are two main Python libraries used:

1. [OpenCV](https://opencv.org) version `4.11.0` for per-frame processing of source video files
2. [pyglet](https://pyglet.readthedocs.io/en/latest/) version `1.5.27` for audio playback and synchronization purposes

---
## Challenges

Even though the python's `OpenCV` library is mostly "just" a bunch of clever wrappers for much more powerful underlying `C++` runtime that is doing all the heavy lifting manipulating the individual video frames of input stream, there is no absolutely audio handling implemented. Therefore the audio needs to be played by its own means: dubious choice of the `pyglet` framework does that quite nicely. 

### pyglet 

Even though it's quite overkill, as you can quite easily write complex videogames using the `pyglet` and you need to overcome the urge to use the latest version of anything: because the `2.0.x` mainline version has (to be fair) great prospects ahead itself, but... You do not solve all your problems by simply downgrading the module you use on daily basis. I suppose. Took me two epiphany-like moments to downgrade deep enough my code just started working. There is also the fact a lots of audio-editors save your `WAV` your downgrading comes in play, as it easily can be started in headless mode and plays 16-bit 44.1 kHz audio samples natively. 

---


(*) 

1. Simplistic video player, sporting [VideoLAN](https://www.videolan.org)'s player in `cvlc` over VideoLan [OpenCV](https://opencv.org) version `4.11.0` for runtime per-frame visual enhancements. Audio streams are handled via [pyglet](https://pyglet.readthedocs.io/en/latest/) framework (`1.5.27`). 

# Objects

Short annotations.

## Entropy

[Entropy: Behind the Screen](docs/ENTROPY.md)

## Fountain

[Fountain: Under the Water](FOUNTAIN.md)

## Tate

[Tate: ...](TATE.md)

## Heads

[Heads: Behind the Screen](docs/HEADS.md)

## Credits

[Credits: Behind the Screen](docs/CREDITS.md)
