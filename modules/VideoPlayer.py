#!/usr/bin/env python3
# coding=utf-8

# Springs of Life (2025)
# rkucera@gmail.com
import asyncio
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
from screeninfo import get_monitors
from random import randint, uniform

from random import random, choice
from scipy.io import wavfile
import time
from glob import glob

# Run pyglet in headless mode
pyglet.options['headless'] = True


async def tate(config, aplayer):

    print('tate', config.tate_audio)
    audios = list()
    videos = list()
    for filenumber in range(1, 36):
        audioname = '{}/{}.wav'.format(config.tate_audio, filenumber)
        audios.append(pyglet.media.StaticSource(pyglet.media.load(audioname, streaming=False)))
        videoname = '{}/{}.mp4'.format(config.tate_video, filenumber)
        videos.append(cv.VideoCapture(videoname))

    random_play = randint(1, 36)

    # eplayer.set_entropy_playhead(start_frame=0)
    cv.namedWindow('tate', cv.WINDOW_NORMAL)
    # cv.namedWindow('entropy', cv.WND_PROP_FULLSCREEN)
    cv.namedWindow('tate', cv.WINDOW_FREERATIO)

    # cv.namedWindow('entropy', cv.WINDOW_AUTOSIZE)
    cv.setWindowProperty('tate', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    # cv.setWindowProperty('entropy', cv.WND_PROP_FULLSCREEN, 1)

    frame_time = 30
    frame_drops = 0
    fra_min = 5
    fra_max = 40
    cycle = 1

    # Run audio track
    aplayer = audios[random_play].play()
    vplayer  = videos[random_play]
    frame_counter = 1
    while True:

        status, frame = vplayer.read()

        if status is True:

            current_audio_frame = round(round(aplayer.time, 6) * 25, 0)
            av_sync = current_audio_frame - frame_counter
            print(av_sync, current_audio_frame, frame_counter, frame_time)

            try:
                if frame_time > 5:
                    cv.imshow('tate', frame)
                else:
                    print('Dropping frame {} | ft={} | avsync={} | total_drops={}'.format(frame_counter, av_sync, frame_time, frame_drops))
                    # frame_drops += 1
                # cv.moveWindow('entropy', 0, 0)

            except Exception as playback:
                print(playback)
                exit(1)

            frame_counter += 1

        else:
            print('End of cycle {}'.format(cycle))
            cycle += 1
            print('releasing video')
            vplayer.release()
            aplayer.delete()
            print('released')
            # video.set(cv.CAP_PROP_POS_FRAMES, 1)
            random_play = randint(1, 36)
            # Run audio track

            vplayer = videos[random_play]
            print('New stream acquired')

            print('resetting audio')
            aplayer = audios[random_play].play()
            print('audio resetted')

            frame_counter = 1

            # aplayer.stop_audio()
            # aplayer.play_audio(0, overlay=True)
            # aplayer.play_audio(1, overlay=True)
            # aplayer.play_audio(2, overlay=True)
            # aplayer.play_audio(3, overlay=True)

        # cv.waitKey(0)
        if av_sync == 0:
            frame_time = 30
        elif av_sync > 0:
            frame_time -=1
        else:
            frame_time +=1

        if frame_time < 1:
            frame_time = 1

        if frame_time > 40:
            frame_time = 40

        if frame_time > fra_max:
            fra_max = frame_time
            print('max', fra_max)
        if frame_time < fra_min:
            fra_min = frame_time
            print('min', fra_min)

        cv.waitKey(frame_time)
        # if cfg.read_input(cv.waitKey(frame_time)) is False:
        #     # Method returns False for ESC key
        #     break

        # Prepare data for next frame processing
        # eplayer.update()
        if frame_counter == 1:
            print('----')
        await asyncio.sleep(0.00001)


    # Release everything
    video.release()
    cv.destroyAllWindows()

async def entropy(cfg):

    overlays = True

    print("Initializing video for the first time: '{}'".format(cfg.entropy_video))
    video = cv.VideoCapture(str(cfg.entropy_video))
    print("Initializing audio for the first time: '{}'".format(cfg.entropy_audio))
    audio = pyglet.media.StaticSource(pyglet.media.load(str(cfg.entropy_audio), streaming=False))
    # video.set(cv.CAP_PROP_BUFFERSIZE, 5)
    print('AV media initialized')

    # Display setup
    video.set(cv.CAP_PROP_POS_FRAMES, 0)
    cv.namedWindow('entropy', cv.WINDOW_NORMAL)
    cv.namedWindow('entropy', cv.WINDOW_FREERATIO)
    cv.setWindowProperty('entropy', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

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
    aplayer = audio.play()

    # Main video loop
    while True:

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
                # cv.moveWindow('entropy', 0, 0)

            except Exception as playback:
                print(playback)
                exit(1)

            frame_counter += 1

        else:
            print('End of cycle {}'.format(cycle))
            cycle += 1
            print('Releasing video')
            video.release()
            aplayer.delete()
            print('released')
            video = cv.VideoCapture(str(cfg.entropy_video))
            print('New stream acquired')
            print('start audio')
            aplayer = audio.play()
            print('audio resetted')
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
            print('max', fra_max)
        if frame_time < fra_min:
            fra_min = frame_time
            print('min', fra_min)
        # This actually controls the playback speed!
        cv.waitKey(frame_time)

        # if frame_counter % 125 == 0:
        #     video.set(cv.CAP_PROP_POS_FRAMES, randint(1000,7000))

        if frame_counter == 1:
            print('----')
        await asyncio.sleep(0.00001)

    # Release everything
    cv.destroyAllWindows()
