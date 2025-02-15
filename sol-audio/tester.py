#!/usr/bin/env python3
# coding=utf-8
# Springs of Life (2025)# rkucera@gmail.com

import platform
import pyglet
# Run pyglet in headless mode
pyglet.options['headless'] = True
# pyglet.options['audio'] = 'pulse'
from time import sleep
from scipy.io import wavfile
from pprint import pprint

from gpiozero import PWMLED
from time import sleep

from gpiozero import LED
from signal import pause

red = LED(26)
green = LED(19)
red.blink(background=True, on_time=0.5, off_time=0.5)
green.blink(background=True, on_time=0.5, off_time=0.5)

pause()

exit(0)



anal = '/Users/zero/Develop/github.com/hadzimura/projectsol/sol-audio/sounds/entropy/voice.right.log'
frames = list()
seconds = dict()
with open(anal, "r") as anal_file:
    for a in anal_file.readlines():
        aline = a.strip().split(';')
        frames.append(bool(int(aline[1])))
        seconds[round(float(aline[0]), 5)] = bool(int(aline[1]))

pprint(len(frames))

pprint(seconds)
pprint(len(seconds))

exit(0)

print(platform.system())


# audio_file = '/home/zero/sol-audio/sounds/entropy/music.left.wav'
audio_file = '../media/sounds/entropy/music.left.wav'
source = pyglet.media.StaticSource(pyglet.media.load(audio_file, streaming=False))

print(source.duration)



# adsr = pyglet.media.synthesis.ADSREnvelope(attack=0.05, decay=0.2, release=0.1)
# saw = pyglet.media.synthesis.Sawtooth(duration=5.0, frequency=220, envelope=adsr)

test = source.play()
# test = saw.play()
while test.playing == True:
    print(test.time, test.volume)

    sleep(1)