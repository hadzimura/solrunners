#!/usr/bin/env python3
# coding=utf-8

# Springs of Life (2025)
# rkucera@gmail.com
from pprint import pprint
from random import choice
from time import sleep
import pyglet
from random import randrange
from random import randint, uniform, choice

from random import random, choice
import time
from glob import glob
import platform
from os.path import isfile

# Run pyglet in headless mode
pyglet.options['headless'] = True

from modules.Config import arg_parser
from modules.Config import Configuration


def head_timer(fr, v=None):

    variations = [
        0,
        0,
        fr / 2,
        fr - 3,
        3
    ]

    if v == 0:
        return variations[randint(2, len(variations) - 1)]
    else:
        return variations[v]


def player():

    try:

        print("Fountain version: {}".format(configuration.fountain_version))

        fountain_audio = samples[0]
        fountain_runtime = fountain_audio.duration

        head_audio = None
        head_runtime = None
        head_start = None
        fountain_delay = None

        if configuration.fountain_version != 1:
            head_audio = samples[randint(1, len(samples) - 1)]
            head_runtime = head_audio.duration
            head_start = head_timer(fountain_runtime, configuration.fountain_version)

        if head_audio is not None:
            head_end = head_start + head_runtime
            fountain_delay = fountain_runtime - head_end

        fountain_player = fountain_audio.play()

        if configuration.fountain_version != 1:
            print('Waiting for: {}'.format(head_start))
            sleep(head_start)
            head_player = head_audio.play()
            sleep(head_runtime)
            head_player.delete()
            sleep(fountain_delay)
        else:
            sleep(fountain_runtime)

        fountain_player.delete()
    except Exception as e:
        print(e)


if __name__ == "__main__":

    arg = arg_parser()
    configuration = Configuration(room=arg.room, fountain_version=arg.fountain_version)

    samples = list()

    print('Loading fountain sample: {}'.format(configuration.fountain))
    samples.append(pyglet.media.StaticSource(pyglet.media.load(configuration.fountain, streaming=False)))

    print('Initializing Silent Heads samples from: {}'.format(configuration.talking_heads))
    for sample in glob(str(configuration.talking_heads)):
        samples.append(pyglet.media.StaticSource(pyglet.media.load(sample, streaming=False)))

    print("All {} samples loaded".format(len(samples)))

    print("Running in the '{}' mode".format(configuration.fountain_version))

    while True:

        player()
        silenzio = randint(60, 300)
        print('Being silent for: {} seconds...'.format(silenzio))
        sleep(randint(60, 300))

    print('Exited gracefuly')
