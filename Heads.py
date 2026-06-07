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

def heads(bg_music, talking_head, total_playtime=None, face_detection=False):
    """
    Heads main playback loop. Loops internally (while True) — never returns.

    'bg_music'     — pyglet Player for background music, created once in __main__.
                     Reused every loop via bg_music.seek(0)+play(); the audio duration
                     timer also reuses it via seek(0) instead of delete()+play().
    'talking_head' — pyglet Player for voice samples, created once in __main__.
                     Reused for every overlay trigger via seek(0)+play() instead of
                     fresh audio_sample.play(). Previously: a new OpenAL source was
                     allocated every ~40 seconds (each overlay trigger), exhausting the
                     256-source pool after ~2.8 hours.

    Both players are passed in pre-created so the OpenAL source count stays at 2
    for the entire runtime lifetime regardless of how many cycles play.
    """

    print("Initializing video: '{}'".format(cfg.heads_video))
    h_video = cv.VideoCapture(str(cfg.heads_video))
    screen_width = int(h_video.get(cv.CAP_PROP_FRAME_WIDTH))
    screen_height = int(h_video.get(cv.CAP_PROP_FRAME_HEIGHT))
    print('Video resolution detected as: {}x{}'.format(screen_width, screen_height))
    total_frames = int(h_video.get(cv.CAP_PROP_FRAME_COUNT))
    print('Total video frames: {}'.format(total_frames))

    # Display setup
    # h_video.set(cv.CAP_PROP_POS_FRAMES, 0)
    # WINDOW_NORMAL allows resizing; WINDOW_FREERATIO allows non-native aspect ratio.
    # Must be combined in a single call — two separate calls would let the second overwrite
    # the first, leaving WINDOW_FREERATIO alone (=AUTOSIZE type) which ignores WINDOW_FULLSCREEN.
    cv.namedWindow('heads', cv.WINDOW_NORMAL | cv.WINDOW_FREERATIO)
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

    # Duration from the player's current source — avoids accessing heads_overlays[0] which
    # required a special 0.*.wav file; bg_music is loaded directly from cfg.heads_audio now.
    bg_audio_frames = int(round(bg_music.source.duration * 25, 0))
    bg_audio_compensation = 0
    # bg_music = cfg.heads_overlays[0]['sample'][0].play()
    # ↑ MOVED to __main__ — Player passed in as 'bg_music'; seek(0) used on cycle reset.
    #   Creating it here allocated a new OpenAL source on every heads() entry.
    bg_music.seek(0)
    bg_music.play()

    transition = False
    cuts = 14
    cut_position = 1000
    cut_length = 25
    cut_blur_step = 10
    cut_blur_value = 1

    slide_time = 800
    slide_in = int((cut_position - slide_time) / 2)
    slide_out = cut_position - slide_in
    slide_blur_portion = 0.3
    # head = 0-1000
    # slide_in = 100
    # slide_out = 900

    cut_in = list()
    cut_out = list()
    sub_in = list()
    sub_out = list()
    volume_down = list()
    for cut in range(1, cuts):
        cut_frame = cut * cut_position
        cut_in.append(cut_frame - cut_length)
        cut_out.append(cut_frame + cut_length)
        sub_in.append(cut_frame - slide_out)
        sub_out.append(cut_frame - slide_in)
        volume_down.append(cut_frame - slide_out)

    blur = 1
    blur_length = 25
    blur_max = 100
    blur_step = 8
    switch = 50

    display_still = None
    display_still_i = None
    display_author = False

    current_head = None

    talking_head_active = False   # True while a voice sample is playing (replaces talking_head is not None)
    kill_splayer = 0

    volume_downer = False
    volume_upper = False
    volume_up = 0

    current_head_name = None
    verbose_debug = False

    blur_value = 1
    blur_interval = 0
    blur_steps = 20
    blur_step = 1
    blur_change_frame = 0
    blur_first_frame = 0
    blur_length = 0
    cmap = 0

    audio_author = None
    line_counter = int((screen_width / 1000))
    line_width = 1
    overlay = None
    display_slide = None

    while True:  # loop internally — heads() never returns (was: while playback is True)

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
                # bg_music.delete()                                    # OLD: freed source → new source on next .play()
                # bg_music = cfg.heads_overlays[0]['sample'][0].play() # OLD: allocated new OpenAL source every loop
                bg_music.seek(0)   # NEW: rewind to start — same source slot reused indefinitely
                bg_music.play()
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
                overlay_id = randint(1, 21)
                overlay = cfg.heads_overlays[overlay_id]

                print('Enabling Subtitle Overlay at frame {}: {} | still_author: {}'.format(frame_counter, overlay_id, overlay['author_name_long']))
                audio_author = None
                try:
                    get_audio = randint(0, len(cfg.heads_overlays[overlay_id]['sample']) - 1)
                    audio_author = overlay['sample_author'][get_audio]
                    audio_sample = overlay['sample'][get_audio]
                    display_slide = overlay['subtitle'].copy()
                    audio_frames = int(audio_sample.duration * 25)
                    blur_vector = choice(overlay['placeholder'])
                    # talking_head = audio_sample.play()
                    # ↑ OLD: allocated a new OpenAL source every ~40 seconds (each overlay trigger).
                    #   After ~256 triggers (~2.8 hours) the source pool was exhausted → audio crash.
                    talking_head.pause()
                    talking_head._playlists.clear()   # drop any queued sources from last trigger
                    talking_head.queue(audio_sample)  # NEW: queue the chosen sample on the shared player
                    talking_head.play()               # reuse same OpenAL source slot
                    talking_head_active = True        # mark player as active (replaces talking_head is not None)
                    kill_splayer = talking_head.time + audio_sample.duration - 0.2

                    # Set the timer for raising the Background Audio volume
                    volume_up = frame_counter + audio_frames

                    # First frame to start blurring the Display Still frame (when the Audio Sample ends)
                    blur_total_frames = int((slide_time - audio_frames) * slide_blur_portion)
                    blur_change_frame = int(blur_total_frames / blur_steps)
                    blur_first_frame = frame_counter + slide_time - blur_total_frames
                    print('Enabling Audio Overlay: {}/{} blur_change_frame: {}'.format(overlay_id, audio_author, blur_change_frame))
                except KeyError:
                    print('Skipping audio for subtitle: {}'.format(overlay_id))
                    pprint(cfg.heads_overlays[overlay_id], indent=4)
                    # blur_change_frame = int(650 / blur_steps)
                except Exception as e:
                        print('Enabling Audio Overlay FAILURE: {}'.format(overlay_id))
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

            # Subtitles and Audio Overlays Disabler
            if frame_counter in sub_out:
                print('Disabling Subtitle Overlay at: {}'.format(frame_counter))
                blur_value = 1
                blur_interval = 0
                display_slide = None

            if talking_head_active:
                if talking_head.time > kill_splayer:
                    print('Disabling Head Samples Audio Player at: {}'.format(frame_counter))
                    talking_head.pause()
                    # talking_head = None  # OLD: set to None then re-assigned fresh at next trigger
                    #                      #      now we keep the player alive; next trigger re-queues it
                    talking_head_active = False


            # Facial recognition for author's name
            # Needs to be here bc of the subtitle blender
            # ------------------------------------
            # Set current head's name
            if frame_counter in cfg.heads_framecode:
                current_head_name = cfg.heads_framecode[frame_counter]

            # Display FR bounding box
            if face_detection is True:

                if display_slide is None and transition is False:
                    detect_bounding_box(frame, current_head_name)
                #
                # if display_slide is not None and transition is False:
                #     try:
                #         detect_bounding_box(frame,
                #                             current_head_name,
                #                             still_name=cfg.heads_authors[overlay['author_name_short']]['sucher'],
                #                             sample_name=cfg.heads_authors[audio_author[0]]['sucher'],
                #                             location=overlay['placeholder'][0])
                #     except Exception as e:
                #         print('failing FD')
            # ------------------------------------

            # Blending Subtitle Overlay
            if display_slide is not None:
                if talking_head_active:   # was: talking_head is not None
                    cv.addWeighted(src1=frame, alpha=1, src2=display_slide, beta=1, gamma=1, dst=frame)
                else:
                    cv.blur(src=display_slide, dst=display_slide, ksize=(blur_value, blur_value))
                    cv.addWeighted(src1=frame, alpha=1, src2=display_slide, beta=1, gamma=1, dst=frame)
                    if frame_counter == blur_first_frame:
                        blur_interval = frame_counter + blur_change_frame
                        # print('Blur Value: {} | fc: {} bff: {} bi: {}'.format(blur_value, frame_counter, blur_first_frame, blur_interval))
                    if frame_counter == blur_interval:
                        blur_value += blur_step
                        blur_interval = frame_counter + blur_change_frame
                        # print('Blur Value: {} | fc: {} bff: {} bi: {}'.format(blur_value, frame_counter, blur_first_frame, blur_interval))

            # Blurring transition
            # -------------------
            # Start blur marker
            if frame_counter in cut_in:
                transition = True
                cut_blur_value = 1
                blur = 10
            # Stop blur marker
            if frame_counter in cut_out:
                transition = False
            # Blur itself
            if transition is True:
                frame = cv.blur(frame, (int(cut_blur_value), int(cut_blur_value)))
                if cut_blur_value > cut_length * cut_blur_step:
                    blur = -10
                cut_blur_value += blur
            # ------------------------------------

            if verbose_debug is True:
                cv.putText(frame,
                           'av:{} fc:{} bac: {} caf: {} ft:{} a_auth: {}'.format(av_sync, frame_counter, bg_audio_compensation, current_audio_frame, frame_time, str(audio_author)),
                           (10, 30),
                           cv.FONT_HERSHEY_COMPLEX,
                           1,
                           (255, 255, 255),
                           3,
                           cv.LINE_AA)

            if transition is False:
                cv.line(frame, (0, 1670), (line_width, 1670), (255, 255, 255), 10)
                line_width += +1
            if transition is True:
                line_width = 25
            # Display current frame
            try:
                cv.imshow('heads', frame)
            except Exception as playback_error:
                print('Playback failing...')
                print(playback_error)

            frame_counter += 1

        else:
            print('End of cycle')
            print('Resetting AV media for next cycle')
            try:
                h_video.release()
                # cv.waitKey(1)      # OLD: was needed after destroyAllWindows; not needed now
                # bg_music.delete()  # OLD: freed the source → required a fresh .play() on re-entry
                # h_video = None     # OLD: set to None; heads() exited and was never re-called anyway
                # bg_music = None    # OLD: same
                # talking_head = None
                bg_music.seek(0)   # rewind bg music for next cycle
                bg_music.play()
                talking_head.pause()   # stop any playing voice sample cleanly
                h_video = cv.VideoCapture(str(cfg.heads_video))   # reopen video from beginning
                frame_counter = 1
                bg_audio_compensation = 0
                talking_head_active = False
                print('AV media reset for next cycle')
            except Exception as av_error:
                print('AV media reset fail: {}'.format(av_error))
            # playback = False  # OLD: exited inner loop; outer while cycle<2 only ran once anyway

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
    face_classifier = cv.CascadeClassifier(cfg.lbp)

    # Create both Players once for the entire runtime — prevents OpenAL source pool exhaustion.
    # Previously: bg_music was created inside heads() on every call; talking_head was allocated
    # fresh on every overlay trigger (~every 40s). Both are now created here and passed in.
    # heads() loops internally (while True) and never returns.

    # Load background audio directly from cfg.heads_audio (silent_heads.wav) — previously this
    # was accessed via heads_overlays[0]['sample'][0] which required a special 0.*.wav file.
    # _bg_source = cfg.heads_overlays[0]['sample'][0]    # OLD: required 0.*.wav in samples dir
    _bg_source = pyglet.media.StaticSource(pyglet.media.load(str(cfg.heads_audio), streaming=False))
    bg_music_player = _bg_source.play()

    # Find first available overlay sample as placeholder for the talking-head player.
    # The actual sample is replaced via queue()+_playlists.clear() on each trigger.
    # Previously this hardcoded heads_overlays[1] which had no sample file on the node.
    # _sample_source = cfg.heads_overlays[1]['sample'][0]   # OLD: hardcoded sub_id 1
    _first_sample = next(
        (cfg.heads_overlays[sid]['sample'][0]
         for sid in sorted(cfg.heads_overlays.keys())
         if 'sample' in cfg.heads_overlays[sid]),
        None
    )
    if _first_sample is None:
        raise RuntimeError("No audio samples found — deploy media/heads/samples/ to node")
    talking_head_player = _first_sample.play()
    talking_head_player.pause()   # start silent; activated by overlay triggers inside heads()

    # while cycle < 2:                                                               # OLD: ran exactly once, runtime exited
    #     heads_thread = Thread(target=heads(total_playtime=None, ...))             # OLD: heads() took no audio args
    #     cycle += 1
    while True:
        # heads() loops forever internally — this outer loop is a safety restart only
        print('Start of heads runtime')
        heads_thread = Thread(target=heads(bg_music_player, talking_head_player, total_playtime=None, face_detection=arg.recognition))