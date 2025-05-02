#!/usr/bin/env python3
# coding=utf-8
# Springs of Life (2025)
# rkucera@gmail.com

import cv2 as cv
from pprint import pprint
from time import sleep
import pyglet
from random import randint
from random import choice
from glob import glob
import platform
from os.path import isfile

# Run pyglet in headless mode
pyglet.options['headless'] = True

from modules.Config import arg_parser
from modules.Config import wait_for_storage
from modules.Config import Configuration
from pathlib import Path

from threading import Thread
from platform import node



def heads(total_playtime=None):

    playing = True

    print("Initializing video: '{}'".format(cfg.heads_video))
    h_video = cv.VideoCapture(str(cfg.heads_video))

    # Display setup
    # h_video.set(cv.CAP_PROP_POS_FRAMES, 0)
    cv.namedWindow('heads', cv.WINDOW_NORMAL)
    cv.namedWindow('heads', cv.WINDOW_FREERATIO)
    if cfg.fullscreen is True:
        print('Running in fullscreen mode')
        cv.setWindowProperty('entropy', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    else:
        print("Running in windowed mode (use '--fullscreen' runtime arg for fullscreen mode)")

    if node() == 'zeromini.local':
        print('Running at zeromini, sending window to another display')
        cv.moveWindow('entropy', 2600, 0)

    av_sync = 0
    frame_counter = 1
    frame_time = 25
    frame_drops = 0
    fra_min = 25
    fra_max = 25
    cycle = 1

    # Run audio track
    print("Initializing audio: '{}'".format(cfg.heads_audio))

    bg_music = cfg.heads_overlays[0].play()
    # bg_music.loop = True
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
    volume_up = list()
    volume_down = list()
    cutting = 1
    for cut in range(1, cuts):
        cut_frame = cut * cut_position
        cut_in.append(cut_frame - 25)
        cut_out.append(cut_frame + 25)
        sub_in.append(cut_frame - 850)
        sub_out.append(cut_frame - 200)
        volume_down.append(cut_frame - 860)

    blur = 1
    blur_length = 25
    blur_max = 100
    blur_step = 8
    switch = 50

    display_still = None
    display_author = False

    current_head = None
    switch_on = 1
    switch_off = 1

    talking_head = None
    kill_splayer = 0

    volume_downer = False
    volume_upper = False
    volume_up = 0

    while playing is True:

        status, frame = h_video.read()

        if total_playtime is not None and frame_counter == total_playtime:
            status = False

        if status is True:

            # AV Syncing
            current_audio_frame = round(round(bg_music.time, 6) * 25, 0)
            av_sync = current_audio_frame - frame_counter

            # Control the volume of background music
            if frame_counter in volume_down:
                volume_downer = True
            if frame_counter == volume_up:
                volume_upper = True

            if volume_downer is True:
                if bg_music.volume < 0.5:
                    volume_downer = False
                bg_music.volume = bg_music.volume - 0.05

            if volume_upper is True:
                if bg_music.volume >= 1:
                    volume_upper = False
                else:
                    bg_music.volume = bg_music.volume + 0.05

            # Subtitles and Audio Overlays Enabler
            if frame_counter in sub_in:
                overlay_id = randint(1, len(cfg.heads_overlays))
                display_still = cfg.heads_overlays[overlay_id]['sub']
                print('Enabling Subtitle Overlay: {}'.format(overlay_id))
                audio_var = None
                try:
                    audio_var = choice(list(cfg.heads_overlays[overlay_id]['tracks']))
                except KeyError:
                    print('Skipping audio for subtitle: {}'.format(overlay_id))

                try:
                    # Try to run audio
                    talking_head = cfg.heads_overlays[overlay_id]['tracks'][audio_var].play()
                    kill_splayer = talking_head.time + cfg.heads_overlays[overlay_id]['tracks'][audio_var].duration - 0.2
                    # Set the timer for rising the Background Audio volume
                    volume_up = int(cfg.heads_overlays[overlay_id]['tracks'][audio_var].duration * 25) + frame_counter
                    print('Enabling Audio Overlay: {}/{}'.format(overlay_id, audio_var))
                except Exception as e:
                    print('Enabling Audio Overlay FAILURE: {}/{}'.format(overlay_id, audio_var))
                    print(e)

            # Subtitles and Audio Overlays Disabler
            if frame_counter in sub_out:
                print('Disabling Subtitle Overlay')
                display_still = None

            if talking_head is not None:
                if talking_head.time > kill_splayer:
                    # print(talking_head.time, kill_splayer)
                    print('Disabling Head Audio Player')
                    talking_head.pause()
                    talking_head = None

            # Blending Subtitle Overlay
            if display_still is not None:
                # frame = cv.addWeighted(frame, 1.5,  display_still, 0.5, 0)
                cv.addWeighted(src1=frame, alpha=1.5, src2=display_still, beta=0.5, gamma=0, dst=frame)

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
                cv.imshow('heads', frame)
            except Exception as playback_error:
                print('Playback failing...')
                print(playback_error)

            frame_counter += 1

        else:
            print('End of cycle {}'.format(cycle))
            cycle += 1
            print('Releasing AV media')
            try:
                h_video.release()
                cv.waitKey(1)
                bg_music.delete()
                print('AV media released')
            except Exception as av_error:
                print('AV media releasing fail: {}'.format(av_error))

            # TODO: restart here or...?
            # h_video = cv.VideoCapture(str(cfg.heads_video))
            # bg_music = cfg.heads_overlays[0].play()
            # frame_counter = 1
            playback = False

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


if __name__ == "__main__":

    arg = arg_parser()
    wait_for_storage()

    cfg = Configuration(runtime='heads', fullscreen=arg.fullscreen)

    while True:
        heads_thread = Thread(target=heads(total_playtime=None))
