#!/usr/bin/env python3
# coding=utf-8

# Springs of Life (2025)
# rkucera@gmail.com
from pprint import pprint
from random import choice
from time import sleep
import pyglet
from random import randrange
from random import randint, uniform

from random import random, choice
import time
from glob import glob
import platform
from os.path import isfile

# Run pyglet in headless mode
pyglet.options['headless'] = True

from modules.Config import arg_parser
from modules.Config import Configuration
from modules.Audio import AudioLibrary



def player(cfg):

    print("Initializing audio for the first time: '{}'".format(cfg.talking_heads))
    audio = pyglet.media.StaticSource(pyglet.media.load(str(cfg.talking_heads), streaming=False))
    print('AV media initialized')
    aplayer = audio.play()
    # Run audio track
    while True:
        print('aaak')



if __name__ == "__main__":

    if platform.system() != "Darwin":
        print('Waiting for the SHM storage to be available...')
        storage_available = False
        while storage_available is False:
            if isfile('/storage/.ready'):
                storage_available = True
                print('Storage online, starting Runner')

    arg = arg_parser()
    configuration = Configuration(room=3)

    running = True

    while running is True:

        player(configuration)
        running = False

    print('exited')