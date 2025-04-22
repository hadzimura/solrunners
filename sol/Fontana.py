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
from modules.Audio import AudioLibrary



def player(cfg):

    # print("Initializing audio for the first time: '{}'".format(cfg.talking_heads))
    # print(samples)
    # aplayer = Player()
    # for s in samples:
    #     aplayer.queue(s)
    samples = list()
    for sample in glob(str(cfg.talking_heads)):
        samples.append(pyglet.media.StaticSource(pyglet.media.load(sample, streaming=False)))

    playback = True
    print( samples[0])

    # last_sample = 0
    # current_sample = 0
    # while current_sample != last_sample:
    #
    #     current_sample = randint(0, len(samples))
    #     print(current_sample, last_sample)
    # else:
    #     print('wtf')
    # last_sample = current_sample
    play_sample = None
    play_sample = samples[0].play()
    playing = True
    a = 0
    b = 0
    while playing is True:
        try:
            a = play_sample.time
            if a != b:
                b = a
                print('+++++', a, b)

            else:
                print('else', a, b)
                play_sample.delete()
                playing = False
        except Exception as e:
            print(e)
    play_sample.delete()
    print('......')
        # play_sample.delete()
        # print('playing', current_sample)
        # play_sample.play()
        # Run audio track
        # aplayer.on_player_eos = aplayer.next_source()


if __name__ == "__main__":

    # if platform.system() != "Darwin":
    #     print('Waiting for the SHM storage to be available...')
    #     storage_available = False
    #     while storage_available is False:
    #         if isfile('/storage/.ready'):
    #             storage_available = True
    #             print('Storage online, starting Runner')

    arg = arg_parser()
    configuration = Configuration(room=4)

    running = True


    player(configuration)
    running = False

    print('exited')