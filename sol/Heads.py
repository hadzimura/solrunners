#!/usr/bin/env python3
# coding=utf-8

# Springs of Life (2025)
# rkucera@gmail.com
import cv2 as cv
from pprint import pprint
from random import choice
from time import sleep
from PIL.ImageChops import overlay
import pyglet
from random import randrange
from PIL import ImageFont, ImageDraw, Image
import numpy as np
from datetime import datetime
from datetime import timedelta

from scipy.stats import alpha
from screeninfo import get_monitors
from random import randint, uniform

from random import random, choice
from scipy.io import wavfile
import time
from glob import glob
import platform
from os.path import isfile

# Run pyglet in headless mode
pyglet.options['headless'] = True

from modules.Config import arg_parser
from modules.Config import Configuration
from modules.Audio import AudioLibrary
from pathlib import Path



def player(cfg):

    playing = True

    print("Initializing video for the first time: '{}'".format(cfg.silent_heads_video))
    video = cv.VideoCapture(str(cfg.silent_heads_video))
    # print(video.get(cv.CAP_PROP_FRAME_COUNT))
    print("Initializing audio for the first time: '{}'".format(cfg.silent_heads_audio))
    audio = pyglet.media.StaticSource(pyglet.media.load(str(cfg.silent_heads_audio), streaming=False))
    # video.set(cv.CAP_PROP_BUFFERSIZE, 5)
    print('AV media initialized')

    # Display setup
    video.set(cv.CAP_PROP_POS_FRAMES, 0)
    cv.namedWindow('heads', cv.WINDOW_NORMAL)
    cv.namedWindow('heads', cv.WINDOW_FREERATIO)
    print(video.get(cv.CAP_PROP_FRAME_HEIGHT), video.get(cv.CAP_PROP_FRAME_WIDTH))

    # cv.namedWindow('subs', cv.WINDOW_NORMAL)
    # cv.namedWindow('subs', cv.WINDOW_FREERATIO)
    # cv.moveWindow('subs',600,0)
    cv.setWindowProperty('heads', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    av_sync = 0
    frame_counter = 1

    frame_time = 25
    frame_drops = 0
    fra_min = 25
    fra_max = 25

    width = 1080
    height = 1920

    # Subtitle frames impport
    print('Importing subtitle frames from: {}'.format(cfg.silent_heads_pix))
    stills = list()
    for file in range(1, 22):
        print('Importing still ID: {} from: {}'.format(file, '{}/{}'.format(cfg.silent_heads_pix, Path('{}.png'.format(file)))))
        still = cv.imread(cfg.silent_heads_pix / Path('{}.png'.format(file)))
        print(still)

        still.resize(1050, 1680)
        # still = cv.blur(still, (5, 5))
        print(still.shape)
        stills.append(still)

    pprint(cfg.heads, indent=4)
    # font_status = cfg.font['status']
    font_scale = 1
    coord = (50, 50)
    subtitle = None
    cycle = 1

    # Run audio track
    aplayer = audio.play()

    alpha = 0
    min_alpha = 0
    max_alpha = 1
    inc_alpha = 0.05
    beat = 5

    transition = False
    cuts = 11
    cut_position = 1000
    cut_length = 40
    cut_in = list()
    cut_out = list()
    sub_in = list()
    sub_out = list()
    cutting = 1
    for cut in range(1, cuts):
        cut_frame = cut * cut_position
        cut_in.append(cut_frame - 25)
        cut_out.append(cut_frame + 25)
        sub_in.append(cut_frame - 800)
        sub_out.append(cut_frame - 200)
    blur = 1
    blur_length = 25
    blur_max = 100
    blur_step = 8
    switch = 50

    pprint(cfg.sub['silent_heads'], indent=2)

    display_still = None
    display_author = False

    # Main video loop
    video.set(cv.CAP_PROP_POS_FRAMES, frame_counter)

    current_head = None
    switch_on = 1
    switch_off = 1

    while playing is True:

        status, frame = video.read()

        if status is True:

            # Subtitles overlay
            current_audio_frame = round(round(aplayer.time, 6) * 25, 0)
            # subtitle_cue = None
            av_sync = current_audio_frame - frame_counter

            if frame_counter in cfg.heads['timeline']:
                current_head = cfg.heads['timeline'][frame_counter]
                print('projected | on: {}, off: {}'.format(switch_on, switch_off))

            # # beta = overlay saturation (0.5)
            if frame_counter in sub_in:
                get_still = cfg.heads[current_head]['track'][randint(0, 2)]
                print('on', frame_counter, get_still['text'])
                display_still = stills[randint(0, len(stills) - 1)]
                print(display_still)

            if frame_counter in sub_out:
                print('off', frame_counter)
                display_still = None
                display_author = True
            #
            # if display_still is not None:
            #     print('subbing')
            #     try:
            #         aplayer.delete()
            #     except Exception as e:
            #         pass
            #     frame = cv.addWeighted(frame, 1.5,  display_still, 0.5, 0)
            #     aplayer = sample[randint(0, len(samples) - 1)].play()

            # Blurring the persona transitions
            if frame_counter in cut_in:
                transition = True
                display_author = False
                cutting = frame_counter
                blur = 1

            if frame_counter in cut_out:
                transition = False

            if transition is True:
                frame = cv.blur(frame, (int(blur), int(blur)))
                blur += blur_step / 2

            # This is the mischiefing
           #  if frame_counter in range(int(cutting + (cut_length / 2) - 2), int(cutting + (cut_length / 2) + 4)):
                # frame = cv.addWeighted(frame, 1.5, e1, alpha, 1)
                # print(frame_counter, alpha)

                    # if switch == 0:
                    #     switch = 1
                    #     frame = cv.addWeighted(e3, 0.1, frame, 0.3, alpha)
                    # else:
                    #     switch = 0
                    #     frame = cv.addWeighted(e3, 0.1, frame, 0.3, alpha)

                    # e1 = cv.addWeighted(frame, 0.1, e1, 0.5, 0)

            if display_author is True:
                pass
            # Overlays
            status_1 = '{}'.format(frame_counter)
            # org = (randint(10, 1000), randint(10, 1900))
            org = (50, 50)
            cv.putText(frame,
                       status_1,
                       org,
                       cv.FONT_HERSHEY_PLAIN,
                       1.5,
                       (0, 50, 200),
                       2,
                       cv.LINE_AA)

            try:
                if frame_time > 5:
                    cv.imshow('heads', frame)
                    # cv.imshow('subs', frame)
                else:
                    print('Dropping frame {} | ft={} | avsync={} | total_drops={}'.format(frame_counter, av_sync, frame_time, frame_drops))
                    frame_drops += 1

            except Exception as playback_error:
                print('Playback failed')
                print('Playback error: {}'.format(playback_error))
                exit(1)

            frame_counter += 1

        else:
            print('End of cycle {}'.format(cycle))
            cycle += 1
            print('Releasing AV media')
            video.release()
            aplayer.delete()
            print('AV media released')
            playing = False

        # cv.waitKey(0)
        if av_sync == 0:
            pass
        elif av_sync > 0:
            frame_time -=1
        else:
            frame_time +=1

        if frame_time < 1:
            frame_time = 1

        if frame_time > 35:
            frame_time = 35

        if frame_time > fra_max:
            fra_max = frame_time
        if frame_time < fra_min:
            fra_min = frame_time
        # This actually controls the playback speed!
        cv.waitKey(frame_time)
        # cv.waitKey(0)

        # if frame_counter % 125 == 0:
        #     video.set(cv.CAP_PROP_POS_FRAMES, randint(1000,7000))

        if frame_counter == 1:
            print('-----------------------------')

    # Release everything
    cv.destroyAllWindows()


if __name__ == "__main__":

    if platform.system() != "Darwin":
        print('Waiting for the SHM storage to be available...')
        storage_available = False
        while storage_available is False:
            if isfile('/storage/.ready'):
                storage_available = True
                print('Storage online, starting Runner')

    heads = list()

    arg = arg_parser()
    configuration = Configuration(room=5)

    samples = list()
    print('Initializing Silent Heads samples from: {}'.format(configuration.talking_heads))
    for sample in glob(str(configuration.talking_heads)):
        samples.append(pyglet.media.StaticSource(pyglet.media.load(sample, streaming=False)))

    running = True

    while running is True:

        player(configuration)

    print('exited')