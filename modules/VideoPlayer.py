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

# Run pyglet in headless mode
pyglet.options['headless'] = True


async def tate(config, aplayer):

    available_videos = len(config.videos)

    get_video = choice((0, available_videos-1))

    video = config.videos[get_video]
    # video.set(cv.CAP_PROP_BUFFERSIZE, 5)

    # self.playing[layer]['stream'].set(cv.CAP_PROP_POS_FRAMES, start_frame)
    # video.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    # video.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    # self.playing[layer]['stream'].set(cv.CAP_PROP_BUFFERSIZE, self.fps)
    # video.set(cv.CAP_PROP_FPS, 25)

    # video.set(cv.CAP_PROP_POS_FRAMES, 0)

    # eplayer.set_entropy_playhead(start_frame=0)
    cv.namedWindow('entropy', cv.WINDOW_NORMAL)
    # cv.namedWindow('entropy', cv.WND_PROP_FULLSCREEN)
    cv.namedWindow('entropy', cv.WINDOW_FREERATIO)

    # cv.namedWindow('entropy', cv.WINDOW_AUTOSIZE)
    cv.setWindowProperty('entropy', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    # cv.setWindowProperty('entropy', cv.WND_PROP_FULLSCREEN, 1)

    frame_time = 60
    frame_drops = 0
    fra_min = 25
    fra_max = 60
    cycle = 1

    # Run audio track
    aplayer.eplay(name='tate', tid=get_video)

    # Main video loop
    frame_counter = 1
    frame_average = 0
    while True:

        status, frame = video.read()

        if status is True:

            # Subtitles overlay
            current_audio_frame = round(aplayer.time() * 25, 0)
            subtitle_cue = None
            # kladná čísla = audio je napřed
            # záporná čísla = audio je pozadu
            av_sync = current_audio_frame - frame_counter
            # print(av_sync, current_audio_frame, frame_counter, frame_time)

            try:
                if frame_time > 5:
                    cv.imshow('entropy', frame)
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
            video.release()
            print('released')
            # video.set(cv.CAP_PROP_POS_FRAMES, 1)
            get_video = choice((0, available_videos - 1))
            video = cv.VideoCapture(get_video)
            print('New stream acquired')

            print('resetting audio')
            aplayer.eplay(name='tate', tid=get_video)
            print('audio resetted')

            frame_counter = 1

            # aplayer.stop_audio()
            # aplayer.play_audio(0, overlay=True)
            # aplayer.play_audio(1, overlay=True)
            # aplayer.play_audio(2, overlay=True)
            # aplayer.play_audio(3, overlay=True)

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

        # if frame_time == 1:
        #     print("Moving {} frames ahead".format(current_audio_frame - video.get(cv.CAP_PROP_POS_FRAMES)))
        #     video.set(cv.CAP_PROP_POS_FRAMES, current_audio_frame)

        # This actually controls the playback speed!
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

    try:
        print('Attached display info:')
        screen = get_monitors()[0]
        print(screen)
        width, height = screen.width, screen.height
    except Exception as e:
        print(e)

    print('init video')
    video = cv.VideoCapture(str(cfg.entropy_video))
    print('init audio')
    audio = pyglet.media.StaticSource(pyglet.media.load(str(cfg.entropy_audio), streaming=False))
    # video.set(cv.CAP_PROP_BUFFERSIZE, 5)
    print('Media initialized')
    # self.playing[layer]['stream'].set(cv.CAP_PROP_POS_FRAMES, start_frame)
    # video.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    # video.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    # self.playing[layer]['stream'].set(cv.CAP_PROP_BUFFERSIZE, self.fps)
    # video.set(cv.CAP_PROP_FPS, 25)

    video.set(cv.CAP_PROP_POS_FRAMES, 0)

    # eplayer.set_entropy_playhead(start_frame=0)
    cv.namedWindow('entropy', cv.WINDOW_NORMAL)
    # cv.namedWindow('entropy', cv.WND_PROP_FULLSCREEN)
    cv.namedWindow('entropy', cv.WINDOW_FREERATIO)

    # cv.namedWindow('entropy', cv.WINDOW_AUTOSIZE)
    cv.setWindowProperty('entropy', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    # cv.setWindowProperty('entropy', cv.WND_PROP_FULLSCREEN, 1)

    av_sync = 0
    frame_time = 25
    frame_drops = 0
    fra_min = 25
    fra_max = 25

    font_status = cfg.font['status']
    subtitle = None

    cycle = 1

    # Run audio track
    aplayer = audio.play()

    # Main video loop
    frame_counter = 1
    frame_average = 0
    while True:

        status, frame = video.read()

        if status is True:

            # Subtitles overlay
            current_audio_frame = round(round(aplayer.time, 6) * 25, 0)
            subtitle_cue = None
            # kladná čísla = audio je napřed
            # záporná čísla = audio je pozadu
            av_sync = current_audio_frame - frame_counter
            # print(av_sync, current_audio_frame, frame_counter, frame_time)

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
                    coo = (randint(5, 350), randint(200, 800))
                    fs = uniform(0.4, 1.4)

                if subtitle is not None:
                    cv.putText(frame, subtitle, coo, cv.FONT_HERSHEY_TRIPLEX, fs, (25, 190, 20), 2, cv.LINE_AA)

                # Overlays
                t = 'a-v: {} | v:{} a:{} ft: {} / {} / {}'.format(av_sync, frame_counter, current_audio_frame, frame_time,  subtitle_cue, round(aplayer.time, 6))
                cv.putText(frame, t, font_status.org, font_status.name, font_status.scale, (0, 50, 200), font_status.thickness, font_status.type)

                t = 'T={} // f{} // v: {} | min/max: <{}/{}>'.format(datetime.now().strftime("%H:%M:%S.%f"), frame_counter, aplayer.volume, fra_min, fra_max)
                cv.putText(frame, t, (50, 75), font_status.name, font_status.scale, (0, 50, 200), font_status.thickness, font_status.type)

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
