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
from pathlib import Path

def credits(cfg):
    pass


def player(cfg):

    playing = True

    print("Initializing video for the first time: '{}'".format(cfg.silent_heads_video))
    video = cv.VideoCapture(str(cfg.silent_heads_video))


    # Display setup
    video.set(cv.CAP_PROP_POS_FRAMES, 0)
    cv.namedWindow('heads', cv.WINDOW_NORMAL)
    cv.namedWindow('heads', cv.WINDOW_FREERATIO)

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

    # font_status = cfg.font['status']
    font_scale = 1
    coord = (50, 50)
    subtitle = None
    cycle = 1

    # Run audio track
    aplayer = drone.play()

    authors = {
        0: 'adela'
    }

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
        sub_in.append(cut_frame - 850)
        sub_out.append(cut_frame - 200)
    blur = 1
    blur_length = 25
    blur_max = 100
    blur_step = 8
    switch = 50

    # pprint(cfg.sub['silent_heads'], indent=2)

    display_still = None
    display_author = False

    # Main video loop
    # video.set(cv.CAP_PROP_POS_FRAMES, frame_counter)

    current_head = None
    switch_on = 1
    switch_off = 1

    splayer = None
    kill_splayer = 0

    while playing is True:

        status, frame = video.read()

        if status is True:

            try:
                # Subtitles overlay
                current_audio_frame = round(round(aplayer.time, 6) * 25, 0)
                # subtitle_cue = None
                av_sync = current_audio_frame - frame_counter

                # # beta = overlay saturation (0.5)
                if frame_counter in sub_in:
                    print('-----------')
                    # get_still = cfg.heads[current_head]['track'][randint(0, 2)]
                    # print(len(stills))
                    over = randint(3, len(overlays))
                    display_still = overlays[over]['sub']
                    print(len(overlays[over]['tracks']) - 1)
                    audio_var = randint(0, len(overlays[over]['tracks']) - 1)
                    print(over, audio_var)
                    try:
                        splayer = overlays[over]['tracks'][audio_var].play()
                        kill_splayer = splayer.time + overlays[over]['tracks'][audio_var].duration - 0.2
                    except Exception as e:
                        pass
                if splayer is not None:
                    #
                    if splayer.time > kill_splayer:
                        print(splayer.time, kill_splayer)
                        print('killing splayer')
                        splayer.pause()
                        if splayer.playing is False:
                            print('splayer was false')
                            # splayer.delete()
                            # splayer.delete()
                            splayer = None
                        else:
                            print('splayer was true')
                            splayer.delete()
                            splayer = None

                if frame_counter in sub_out:
                    print('off', frame_counter)
                    display_still = None

                if display_still is not None:
                    frame = cv.addWeighted(frame, 1.5,  display_still, 0.5, 0)

                # Blurring the persona transitions
                if frame_counter in cut_in:
                    transition = True
                    cutting = frame_counter
                    blur = 1

                if frame_counter in cut_out:
                    transition = False

                if transition is True:
                    frame = cv.blur(frame, (int(blur), int(blur)))
                    blur += blur_step / 2

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
            except Exception as error:
                print('Error {}'.format(error))


        else:
            print('End of cycle {}'.format(cycle))
            cycle += 1
            print('Releasing AV media')
            video.release()
            aplayer.delete()
            print('AV media released')
            video = cv.VideoCapture(str(cfg.silent_heads_video))
            aplayer = drone.play()
            frame_counter = 1

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
    drone = pyglet.media.StaticSource(pyglet.media.load(str(configuration.silent_heads_audio), streaming=False))

    print('Importing subtitle frames from: {}'.format(configuration.silent_heads_pix))
    overlays = dict()
    for file in range(1, 22):
        print('Importing still ID: {} from: {}'.format(file, '{}/{}'.format(configuration.silent_heads_pix, Path('{}.png'.format(file)))))
        still = cv.imread(configuration.silent_heads_pix / Path('{}.png'.format(file)))
        overlays[file] = dict()
        overlays[file]['sub'] = still

    print('Initializing Silent Heads samples from: {}'.format(configuration.talking_heads))
    for sample in glob(str(configuration.talking_heads)):
        sample_id = int(sample.split('/')[-1].split('.')[0])
        sample_author = sample.split('/')[-1].split('.')[1]
        print('Loading file: {}'.format(sample))
        if 'tracks' not in overlays[sample_id]:
            overlays[sample_id]['tracks'] = list()
        l = pyglet.media.StaticSource(pyglet.media.load(sample, streaming=False))
        overlays[sample_id]['tracks'].append(l)

    running = True

    while running is True:

        player(configuration)

    print('Exited')