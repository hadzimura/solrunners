#!/usr/bin/env python3
# coding=utf-8

# Springs of Life (2025)
# rkucera@gmail.com
import cv2 as cv
from pprint import pprint
from time import sleep
from PIL.ImageChops import overlay
import pyglet
from random import randrange
from PIL import ImageFont, ImageDraw, Image
import numpy as np
from datetime import datetime
from datetime import timedelta
from screeninfo import get_monitors
from random import randint, uniform
from pathlib import Path
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

if platform.system() != 'Darwin':
    from gpiozero import MotionSensor

class FakeMotionSensor(object):

    def __init__(self):

        self.motion_detected = False

    def on(self):
        self.motion_detected = True
    def off(self):
        self.motion_detected = False

def countdown(cfg):

    black_bg = cv.imread(str(cfg.entropy_stills / Path('black.png')))
    white_bg = cv.imread(str(cfg.entropy_stills / Path('white.png')))
    counter = 9
    c = 1
    while counter > 0 :
        frame = white_bg.copy()
        cv.putText(frame,
                   str(counter),
                   (400, 670),
                   cv.FONT_HERSHEY_PLAIN,
                   50,
                   (0, 0, 0),
                   100,
                   cv.LINE_AA)
        cv.putText(frame,
                   str(counter),
                   (400, 670),
                   cv.FONT_HERSHEY_PLAIN,
                   50,
                   (255, 255, 255),
                   90,
                   cv.LINE_AA)
        cv.imshow('entropy', frame)
        cv.waitKey(25)
        c += 1
        if c % 50 == 0:
            counter -= 1


def player(cfg):

    overlays = True
    playing = True

    print("Initializing video for the first time: '{}'".format(cfg.entropy_video))
    video = cv.VideoCapture(str(cfg.entropy_video))
    # print(video.get(cv.CAP_PROP_FRAME_COUNT))
    print("Initializing audio for the first time: '{}'".format(cfg.entropy_audio))
    audio = pyglet.media.StaticSource(pyglet.media.load(str(cfg.entropy_audio), streaming=False))
    # video.set(cv.CAP_PROP_BUFFERSIZE, 5)
    print('AV media initialized')

    # Display setup
    video.set(cv.CAP_PROP_POS_FRAMES, 9500)
    cv.namedWindow('entropy', cv.WINDOW_NORMAL)
    cv.namedWindow('entropy', cv.WINDOW_FREERATIO)
    cv.setWindowProperty('entropy', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    countdown(cfg)

    av_sync = 0
    frame_counter = 9500
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
    aplayer = audio.play()

    # Main video loop
    while playing is True:

        status, frame = video.read()

        if status is True:

            # Subtitles overlay
            current_audio_frame = round(round(aplayer.time, 6) * 25, 0)
            subtitle_cue = None
            av_sync = current_audio_frame - frame_counter

            if overlays is True:

                try:
                    subtitle_cue = datetime.strptime(str(timedelta(seconds=round(aplayer.time, 6))), '%H:%M:%S.%f').time().replace(microsecond=0)
                except Exception as runtime_problem:
                    print('Runtime failing: {}'.format(runtime_problem))

                # if frame_counter % 100 == 0:
                #     print('swap')
                #     aplayer.eplay(action='swap')

                # Subtitles
                if subtitle_cue in cfg.sub['entropy']:
                    subtitle = cfg.sub['entropy'][subtitle_cue]
                    coord = (randint(5, 350), randint(200, 800))
                    font_scale = uniform(0.4, 1.4)

                if subtitle is not None:
                    cv.putText(frame,
                               subtitle,
                               coord,
                               cv.FONT_HERSHEY_TRIPLEX,
                               font_scale,
                               (25, 190, 20),
                               2,
                               cv.LINE_AA)

                # Overlays
                status_1 = 'a-v: {} | v:{} a:{} ft: {} / {} / {}'.format(av_sync,
                                                                       frame_counter,
                                                                       current_audio_frame,
                                                                       frame_time,
                                                                       subtitle_cue,
                                                                       round(aplayer.time, 6))
                cv.putText(frame,
                           status_1,
                           (50, 50),
                           cv.FONT_HERSHEY_PLAIN,
                           1.5,
                           (0, 50, 200),
                           2,
                           cv.LINE_AA)

                status_2 = 'T={} == c: {} // f{} // v: {} | min/max: <{}/{}>'.format(
                    datetime.now().strftime("%H:%M:%S.%f"),
                    cycle,
                    frame_counter,
                    aplayer.volume,
                    fra_min,
                    fra_max)

                cv.putText(frame,
                           status_2,
                           (50, 75),
                           cv.FONT_HERSHEY_PLAIN,
                           1.5,
                           (0, 50, 200),
                           2,
                           cv.LINE_AA)

            try:
                if frame_time > 5:
                    cv.imshow('entropy', frame)
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

        # if frame_counter % 125 == 0:
        #     video.set(cv.CAP_PROP_POS_FRAMES, randint(1000,7000))

        if frame_counter == 1:
            print('-----------------------------')

    # Release everything
    # cv.destroyAllWindows()


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
    if platform.system() != "Darwin":
        pir = MotionSensor(15)
    else:
        pir = FakeMotionSensor()

    running = True

    while running is True:

        player(configuration)

    print('exited')