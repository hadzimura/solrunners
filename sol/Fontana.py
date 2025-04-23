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


def player():

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

    if configuration.fountain_version == 2:
        head_start = fountain_runtime / 2
    elif configuration.fountain_version == 3:
        head_start = fountain_runtime - 3
    elif configuration.fountain_version == 4:
        head_start = 3

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


if __name__ == "__main__":

    # if platform.system() != "Darwin":
    #     print('Waiting for the SHM storage to be available...')
    #     storage_available = False
    #     while storage_available is False:
    #         if isfile('/storage/.ready'):
    #             storage_available = True
    #             print('Storage online, starting Runner')

    arg = arg_parser()
    configuration = Configuration(room=arg.room, fountain_version=arg.fountain)

    print('Initializing Silent Heads samples...')
    samples = list()
    samples.append(pyglet.media.StaticSource(pyglet.media.load(configuration.fountain, streaming=False)))
    for sample in glob(str(configuration.talking_heads)):
        samples.append(pyglet.media.StaticSource(pyglet.media.load(sample, streaming=False)))
    print("All {} samples loaded".format(len(samples)))
    print(configuration.fountain_version)
    while True:

        player()
        sleep(10)


    print('exited')