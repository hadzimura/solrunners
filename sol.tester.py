#!/usr/bin/env python3
# coding=utf-8
# Springs of Life (2025)# rkucera@gmail.com

import platform

from gpiozero import PWMLED
from time import sleep

# from gpiozero import LED, Button, MotionSensor
from signal import pause
from datetime import datetime as dt
from datetime import timedelta

app = object
app.presence_delay = False
app.next_presence = None


while True:

    current_time = dt.now()

    if app.presence_delay and current_time >= app.next_presence:
        pass

    elif app.presence_fader and current_time <= app.last_presence + timedelta(seconds=5):
        pass

    elif app.c.pir.is_active and not app.presence:

        # Keep the presence timer updated
        app.last_presence = current_time
        app.presence = True
        app.c.blue.on()
        print('Presence started')

    elif not app.c.pir.is_active and app.presence and current_time > app.last_presence + timedelta(seconds=5):

        # Starting the Presence Fader
        if app.presence_fader is False:
            app.c.blue.blink(background=True, on_time=0.1, off_time=0.3)
            app.presence_fader = True

    elif not app.c.pir.is_active and app.presence and current_time > app.c.jitter_presence:

        print('Presence stopped')
        app.presence = False
        app.presence_fader = False
        # Start timer for next presence activity
        app.presence_delay = True
        app.next_presence = current_time + timedelta(seconds=app.c.presence_delay)
        app.c.blue.off()

while True:
    sine = pyglet.media.synthesis.Sine(0.1, frequency=440, sample_rate=44800)
    sine.play()
    sleep(0.5)

n = datetime.now()


while True:
    sleep(1)
    a = datetime.now()
    print(a.microsecond-n.microsecond)

print(timedelta())

print(a.microsecond-n.microsecond)


# blue = LED(26)
# green = LED(19)
# pir = MotionSensor(15)
# button = Button(2)
#
# while True:
#     if button.is_active:
#         blue.blink(background=True, on_time=0.5, off_time=0.5)
#         # print("Button is pressed")
#     else:
#         if blue.is_active is True:
#             blue.off()
#         # print("Button is not pressed")
#
#     print(pir.value)
#     # if pir.:
#     #     green.blink(background=True, on_time=0.5, off_time=0.5)
#     # else:
#     #     green.off()
#
#
# # green.blink(background=True, on_time=0.5, off_time=0.5)
#
# pause()

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


# audio_file = '/home/zero/sol-audio/sounds/entropy/1.wav'
audio_file = 'source/sounds/entropy/1.wav'
source = pyglet.media.StaticSource(pyglet.media.load(audio_file, streaming=False))

print(source.duration)



# adsr = pyglet.media.synthesis.ADSREnvelope(attack=0.05, decay=0.2, release=0.1)
# saw = pyglet.media.synthesis.Sawtooth(duration=5.0, frequency=220, envelope=adsr)

test = source.play()
# test = saw.play()
while test.playing == True:
    print(test.time, test.volume)

    sleep(1)