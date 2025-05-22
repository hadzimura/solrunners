#!/usr/bin/env python3
# coding=utf-8
# Springs of Life (2025)
# rkucera@gmail.com
from ipaddress import summarize_address_range

import cv2 as cv
from pprint import pprint
from time import sleep
import pyglet
import numpy as np
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


def detect_bounding_box(video_frame, head_name, still_name=None, sample_name=None, location=None):

    # color = (0, 0, 250) red
    # color = (0, 0, 0) black
    # color = (255, 255, 255) white
    color = (randint(0, 255), randint(0, 255), randint(0, 255))

    gray_image = cv.cvtColor(video_frame, cv.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_image, 1.2, 5, minSize=(40, 40))
    for (x, y, w, h) in faces:
        upscale = 150
        print(x, y, w, h)

        cv.rectangle(video_frame, (x - upscale, y - upscale), (x + w + upscale, y + h + upscale), color, randint(1, 6))

        top_line = '{} SUCHER'.format(head_name.upper())
        # org (x + 10 - upscale, y - upscale + 35),
        cv.putText(video_frame,
                   top_line,
                   (x + 10 - upscale, y - upscale + 35),
                   cv.FONT_HERSHEY_COMPLEX,
                   1,
                   color,
                   3,
                   cv.LINE_AA)


    bottom_line = None
    org_bottom = None

    if still_name == sample_name:
        sample_name = None

    # if head_name == still_name:
    #     still_name = None
    # if head_name == sample_name:
    #     sample_name = True

    if still_name is not None:
        bottom_line = '{} SUCHER'.format(still_name.upper())
    if sample_name is not None:
        bottom_line = '{} (feat: {})'.format(bottom_line, sample_name.upper())

    if location == 'top':
        org_bottom = (20, 100)

    elif location == 'bottom':
        org_bottom = (20, 1600)



    # org: (x + w - upscale + 30, y + h + upscale + 30),
    if org_bottom is not None:
        cv.putText(video_frame,
                   bottom_line,
                   org_bottom,
                   cv.FONT_HERSHEY_COMPLEX,
                   1,
                   (255, 255, 255),
                   2,
                   cv.LINE_AA)

# def heads_old(total_playtime=None):
#
#     playing = True
#
#     print("Initializing video: '{}'".format(cfg.heads_video))
#     h_video = cv.VideoCapture(str(cfg.heads_video))
#
#     # Display setup
#     # h_video.set(cv.CAP_PROP_POS_FRAMES, 0)
#     cv.namedWindow('heads', cv.WINDOW_NORMAL)
#     cv.namedWindow('heads', cv.WINDOW_FREERATIO)
#     if cfg.fullscreen is True:
#         print('Running in fullscreen mode')
#         cv.setWindowProperty('heads', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
#     else:
#         print("Running in windowed mode (use '--fullscreen' runtime arg for fullscreen mode)")
#
#     if node() == 'zeromini.local':
#         print('Running at zeromini, sending window to another display')
#         cv.moveWindow('heads', 2600, 0)
#
#     av_sync = 0
#     frame_counter = 1
#     frame_time = 25
#     frame_drops = 0
#     fra_min = 25
#     fra_max = 25
#     cycle = 1
#
#     # Run audio track
#     print("Initializing audio: '{}'".format(cfg.heads_audio))
#
#     bg_music = cfg.heads_overlays[0].play()
#     # bg_music.loop = True
#     alpha = 0
#     min_alpha = 0
#     max_alpha = 1
#     inc_alpha = 0.05
#     beat = 5
#
#     transition = False
#     cuts = 11
#     cut_position = 1000
#     cut_length = 40
#     cut_in = list()
#     cut_out = list()
#     sub_in = list()
#     sub_out = list()
#     volume_up = list()
#     volume_down = list()
#     cutting = 1
#     for cut in range(1, cuts):
#         cut_frame = cut * cut_position
#         cut_in.append(cut_frame - 25)
#         cut_out.append(cut_frame + 25)
#         sub_in.append(cut_frame - 850)
#         sub_out.append(cut_frame - 200)
#         volume_down.append(cut_frame - 860)
#
#     blur = 1
#     blur_length = 25
#     blur_max = 100
#     blur_step = 8
#     switch = 50
#
#     display_still = None
#     display_author = False
#
#     current_head = None
#     switch_on = 1
#     switch_off = 1
#
#     talking_head = None
#     kill_splayer = 0
#
#     volume_downer = False
#     volume_upper = False
#     volume_up = 0
#
#     while playing is True:
#
#         status, frame = h_video.read()
#
#         if total_playtime is not None and frame_counter == total_playtime:
#             status = False
#
#         if status is True:
#
#             # AV Syncing
#             current_audio_frame = round(round(bg_music.time, 6) * 25, 0)
#             av_sync = current_audio_frame - frame_counter
#
#             # Control the volume of background music
#             if frame_counter in volume_down:
#                 volume_downer = True
#             if frame_counter == volume_up:
#                 volume_upper = True
#
#             if volume_downer is True:
#                 if bg_music.volume < 0.5:
#                     volume_downer = False
#                 bg_music.volume = bg_music.volume - 0.05
#
#             if volume_upper is True:
#                 if bg_music.volume >= 1:
#                     volume_upper = False
#                 else:
#                     bg_music.volume = bg_music.volume + 0.05
#
#             # Subtitles and Audio Overlays Enabler
#             if frame_counter in sub_in:
#                 overlay_id = randint(1, len(cfg.heads_overlays))
#                 display_still = cfg.heads_overlays[overlay_id]['sub']
#                 print('Enabling Subtitle Overlay: {}'.format(overlay_id))
#                 audio_var = None
#                 try:
#                     audio_var = choice(list(cfg.heads_overlays[overlay_id]['tracks']))
#                 except KeyError:
#                     print('Skipping audio for subtitle: {}'.format(overlay_id))
#
#                 try:
#                     # Try to run audio
#                     talking_head = cfg.heads_overlays[overlay_id]['tracks'][audio_var].play()
#                     kill_splayer = talking_head.time + cfg.heads_overlays[overlay_id]['tracks'][audio_var].duration - 0.2
#                     # Set the timer for rising the Background Audio volume
#                     volume_up = int(cfg.heads_overlays[overlay_id]['tracks'][audio_var].duration * 25) + frame_counter
#                     print('Enabling Audio Overlay: {}/{}'.format(overlay_id, audio_var))
#                 except Exception as e:
#                     print('Enabling Audio Overlay FAILURE: {}/{}'.format(overlay_id, audio_var))
#                     print(e)
#
#             # Subtitles and Audio Overlays Disabler
#             if frame_counter in sub_out:
#                 print('Disabling Subtitle Overlay')
#                 display_still = None
#
#             if talking_head is not None:
#                 if talking_head.time > kill_splayer:
#                     # print(talking_head.time, kill_splayer)
#                     print('Disabling Head Audio Player')
#                     talking_head.pause()
#                     talking_head = None
#
#             # Blending Subtitle Overlay
#             if display_still is not None:
#                 # frame = cv.addWeighted(frame, 1.5,  display_still, 0.5, 0)
#                 cv.addWeighted(src1=frame, alpha=1.5, src2=display_still, beta=0.5, gamma=0, dst=frame)
#
#             # Blurring the persona transitions
#             if frame_counter in cut_in:
#                 transition = True
#                 cutting = frame_counter
#                 blur = 1
#
#             if frame_counter in cut_out:
#                 transition = False
#
#             if transition is True:
#                 frame = cv.blur(frame, (int(blur), int(blur)))
#                 blur += blur_step / 2
#
#             try:
#                 cv.imshow('heads', frame)
#             except Exception as playback_error:
#                 print('Playback failing...')
#                 print(playback_error)
#
#             frame_counter += 1
#
#         else:
#             print('End of cycle {}'.format(cycle))
#             cycle += 1
#             print('Releasing AV media')
#             try:
#                 h_video.release()
#                 cv.waitKey(1)
#                 bg_music.delete()
#                 print('AV media released')
#             except Exception as av_error:
#                 print('AV media releasing fail: {}'.format(av_error))
#
#             # TODO: restart here or...?
#             # h_video = cv.VideoCapture(str(cfg.heads_video))
#             # bg_music = cfg.heads_overlays[0].play()
#             # frame_counter = 1
#             playback = False
#
#         # cv.waitKey(0)
#         if av_sync == 0:
#             pass
#         elif av_sync > 0:
#             frame_time -=1
#         else:
#             frame_time +=1
#
#         if frame_time < 1:
#             frame_time = 1
#
#         if frame_time > 35:
#             frame_time = 35
#
#         if frame_time > fra_max:
#             fra_max = frame_time
#         if frame_time < fra_min:
#             fra_min = frame_time
#
#         # This actually controls the playback speed!
#         cv.waitKey(frame_time)
#         # cv.waitKey(0)

def heads(total_playtime=None, face_detection=False):

    playback = True

    print("Initializing video: '{}'".format(cfg.heads_video))
    h_video = cv.VideoCapture(str(cfg.heads_video))
    screen_width = int(h_video.get(cv.CAP_PROP_FRAME_WIDTH))
    screen_height = int(h_video.get(cv.CAP_PROP_FRAME_HEIGHT))
    print('Video resolution detected as: {}x{}'.format(screen_width, screen_height))
    total_frames = h_video.get(cv.CAP_PROP_FRAME_COUNT)
    print('Total video frames: {}'.format(total_frames))

    # Display setup
    # h_video.set(cv.CAP_PROP_POS_FRAMES, 0)
    cv.namedWindow('heads', cv.WINDOW_NORMAL)
    cv.namedWindow('heads', cv.WINDOW_FREERATIO)
    if cfg.fullscreen is True:
        print('Running in fullscreen mode')
        cv.setWindowProperty('heads', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    else:
        print("Running in windowed mode (use '--fullscreen' runtime arg for fullscreen mode)")

    if node() == 'zeromini.local':
        print('Running at zeromini, sending window to another display')
        cv.moveWindow('heads', 2600, 0)

    av_sync = 0
    frame_counter = 1
    frame_time = 25
    frame_drops = 0
    fra_min = 20
    fra_max = 30

    # Run audio track
    print("Initializing audio: '{}'".format(cfg.heads_audio))

    bg_audio_frames = int(round(round(cfg.heads_overlays[0]['sample'][0].duration, 2) * 25, 0))
    bg_audio_compensation = 0
    bg_music = cfg.heads_overlays[0]['sample'][0].play()

    transition = False
    cuts = 12
    cut_position = 1000
    cut_in = list()
    cut_out = list()
    sub_in = list()
    sub_out = list()
    volume_down = list()
    for cut in range(1, cuts):
        cut_frame = cut * cut_position
        cut_in.append(cut_frame - 25)
        cut_out.append(cut_frame + 25)
        sub_in.append(cut_frame - 850)
        sub_out.append(cut_frame - 200)
        volume_down.append(cut_frame - 860)

    # sub_in = 150f
    # sub_out = 800f

    blur = 1
    blur_length = 25
    blur_max = 100
    blur_step = 8
    switch = 50

    display_still = None
    display_still_i = None
    display_author = False

    current_head = None

    talking_head = None
    kill_splayer = 0

    volume_downer = False
    volume_upper = False
    volume_up = 0

    current_head_name = None

    blur_value = 1
    blur_interval = 0
    blur_steps = 6
    blur_step = 1
    blur_change_frame = 0
    blur_first_frame = 0
    blur_length = 0
    cmap = 0

    audio_author = None

    overlay = None

    while playback is True:

        status, frame = h_video.read()

        # Test individual play-throughs
        if total_playtime is not None and frame_counter == total_playtime:
            status = False

        if status is True:

            # AV Syncing
            current_audio_frame = round(round(bg_music.time, 6) * 25, 0) + bg_audio_compensation
            av_sync = current_audio_frame - frame_counter

            # Monitor if the background audio track is still playing, re-enable if ain't
            if frame_counter % bg_audio_frames == 0:
                print('Restarting Background Audio Player at: {}'.format(frame_counter))
                bg_music.delete()
                bg_music = cfg.heads_overlays[0]['sample'][0].play()
                bg_audio_compensation += bg_audio_frames

            # Control the volume of background music
            if frame_counter in volume_down:
                volume_downer = True
            if frame_counter == volume_up:
                volume_upper = True
            # Audio fade-out at the end of the video
            if total_frames - frame_counter == 100:
                volume_downer = True

            # Subtitles and Audio Overlays Enabler
            if frame_counter in sub_in:
                # TODO: Are we showing all the variations?
                # overlay_id = randint(1, len(cfg.heads_overlays))
                overlay_id = randint(1, 21)
                overlay = cfg.heads_overlays[overlay_id]

                print('Enabling Subtitle Overlay at frame {}: {} | still_author: {}'.format(frame_counter, overlay_id, overlay['author_name_long']))
                audio_author = None
                try:
                    # audio_author = choice(list(cfg.heads_overlays[overlay_id]['tracks']))
                    get_audio = randint(0, len(cfg.heads_overlays[overlay_id]['sample']) - 1)
                    audio_author = overlay['sample_author'][get_audio]
                    audio_sample = overlay['sample'][get_audio]
                    blur_vector = choice(overlay['placeholder'])
                    talking_head = audio_sample.play()
                    kill_splayer = talking_head.time + audio_sample.duration - 0.2
                    # Set the timer for raising the Background Audio volume
                    volume_up = int(audio_sample.duration * 25) + frame_counter

                    # First frame to start blurring the Display Still frame (when the Audio Sample ends)
                    blur_total_frames = (650 - int(audio_sample.duration * 25)) * 0.6
                    blur_first_frame = frame_counter + (650 - int(audio_sample.duration * 25)) - blur_total_frames
                    # blur_change_frame = int((650 - int(audio_sample.duration * 25)) / blur_steps)
                    blur_change_frame = int(blur_total_frames / blur_steps)
                    print('Enabling Audio Overlay: {}/{} blur_change_frame: {}'.format(overlay_id, audio_author, blur_change_frame))
                except KeyError:
                    print('Skipping audio for subtitle: {}'.format(overlay_id))
                    blur_change_frame = int(650 / blur_steps)
                except Exception as e:
                        print('Enabling Audio Overlay FAILURE: {}/{}'.format(overlay_id, audio_var))
                        print(e)

            try:
                if volume_downer is True:
                    # if talking_head is None:
                    #     # In case the sample audio is missing...
                    #     volume_downer = False
                    if bg_music.volume < 0.3:
                        volume_downer = False
                    bg_music.volume = bg_music.volume - 0.05

                if volume_upper is True:
                    if bg_music.volume >= 1:
                        volume_upper = False
                    else:
                        bg_music.volume = bg_music.volume + 0.05
            except Exception as bg_player_error:
                print('Problem adjusting Background Audio')
                print(bg_player_error)

                #
                #
                # if audio_version is not None:
                #     try:
                #         # Try to run audio
                #         talking_head = cfg.heads_overlays[overlay_id]['tracks'][audio_var].play()
                #         kill_splayer = talking_head.time + cfg.heads_overlays[overlay_id]['tracks'][audio_var].duration - 0.2
                #         # Set the timer for rising the Background Audio volume
                #         volume_up = int(cfg.heads_overlays[overlay_id]['tracks'][audio_var].duration * 25) + frame_counter
                #         print('Enabling Audio Overlay: {}/{}'.format(overlay_id, audio_var))
                #     except Exception as e:
                #         print('Enabling Audio Overlay FAILURE: {}/{}'.format(overlay_id, audio_var))
                #         print(e)

            # Subtitles and Audio Overlays Disabler
            if frame_counter in sub_out:
                print('Disabling Subtitle Overlay at: {}'.format(frame_counter))
                overlay = None
                blur_value = 1
                blur_interval = 0

            if talking_head is not None:
                if talking_head.time > kill_splayer:
                    # print(talking_head.time, kill_splayer)
                    print('Disabling Head Samples Audio Player at: {}'.format(frame_counter))
                    talking_head.pause()
                    talking_head = None

                    # Calculate time left for blurring out the subtitle

                    blur_interval = frame_counter + blur_step
                    print('Setting f:{} bi:{} bs: {}'.format(frame_counter, blur_interval, blur_step))

            # Facial recognition for author's name
            # Needs to be here bc of the subtitle blender
            # ------------------------------------
            # Set current head's name
            if frame_counter in cfg.heads_framecode:
                current_head_name = cfg.heads_framecode[frame_counter]

            # Display FR bounding box
            if face_detection is True:

                if overlay is None and transition is False:
                    detect_bounding_box(frame, current_head_name)

                if overlay is not None and transition is False:
                    try:
                        detect_bounding_box(frame,
                                            current_head_name,
                                            still_name=cfg.heads_authors[overlay['author_name_short']]['sucher'],
                                            sample_name=cfg.heads_authors[audio_author[0]]['sucher'],
                                            location=overlay['placeholder'][0])
                    except Exception as e:
                        print('failing FD')
            # ------------------------------------

            # Blending Subtitle Overlay
            if overlay is not None:
                # frame = cv.addWeighted(frame, 1.5,  display_still, 0.5, 0)
                if talking_head is not None:
                    cv.addWeighted(src1=frame, alpha=1, src2=overlay['subtitle'], beta=1, gamma=1, dst=frame)
                else:
                    # cv.addWeighted(src1=frame, alpha=1.5, src2=display_still, beta=0.5, gamma=0, dst=frame)
                    # cv.blur(src=display_still, dst=display_still, ksize=(blur_value, blur_value), borderType=cv.BORDER_REFLECT101)
                    cv.blur(src=overlay['subtitle'], dst=overlay['subtitle'], ksize=(blur_value, blur_value))
                    # cv.blur(src=display_still, dst=display_still, ksize=(blur_value, blur_value), borderType=cv.BORDER_CONSTANT)
                    # cv.blur(src=display_still, dst=display_still, ksize=(blur_value, blur_value), borderType=cv.BORDER_ISOLATED)
                    # cv.GaussianBlur(src=display_still, dst=display_still, ksize=(blur_value, blur_value), borderType=cv.BORDER_WRAP)
                    cv.addWeighted(src1=frame, alpha=1, src2=overlay['subtitle'], beta=1, gamma=1, dst=frame)
                    # print(frame_counter, blur_interval, blur_step)
                    if frame_counter == blur_first_frame or frame_counter == blur_interval:
                        blur_value += blur_step
                        blur_interval = frame_counter + blur_change_frame
                        print('Blur Value: {}'.format(blur_value))

            # Blurring transition
            # -------------------
            # Start blur marker
            if frame_counter in cut_in:
                transition = True
                blur = 1
            # Stop blur marker
            if frame_counter in cut_out:
                transition = False
            # Blur itself
            if transition is True:
                frame = cv.blur(frame, (int(blur), int(blur)))
                blur += 10
            # ------------------------------------
            cv.putText(frame,
                       'av:{} fc:{} bac: {} caf: {} ft:{} a_auth: {}'.format(av_sync, frame_counter, bg_audio_compensation, current_audio_frame, frame_time, str(audio_author)),
                       (10, 30),
                       cv.FONT_HERSHEY_COMPLEX,
                       1,
                       (255, 255, 255),
                       3,
                       cv.LINE_AA)

            # Display current frame
            try:
                cv.imshow('heads', frame)
            except Exception as playback_error:
                print('Playback failing...')
                print(playback_error)

            frame_counter += 1

        else:
            print('End of cycle')
            print('Releasing AV media')
            try:
                h_video.release()
                cv.waitKey(1)
                bg_music.delete()
                print('AV media released')
            except Exception as av_error:
                print('AV media releasing fail: {}'.format(av_error))
            playback = False

        # cv.waitKey(0)
        if av_sync == 0:
            frame_time = 25
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
    # face_classifier = cv.CascadeClassifier(cfg.fr)
    # face_classifier = cv.CascadeClassifier(cfg.fr)
    face_classifier = cv.CascadeClassifier(cfg.lbp)
    cycle = 1
    while True:
        print('Start of cycle: {}'.format(cycle))
        heads_thread = Thread(target=heads(total_playtime=None, face_detection=arg.recognition))
        cycle += 1