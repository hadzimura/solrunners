#!/usr/bin/env python3
# coding=utf-8

# Springs of Life (2025)
# rkucera@gmail.com

import cv2 as cv
from pprint import pprint
import pyglet
import numpy as np
from datetime import datetime
from datetime import timedelta
from random import randint, uniform
from random import random, choice
from platform import node
from threading import Thread

# Run pyglet in headless mode
pyglet.options['headless'] = True

from modules.Config import arg_parser
from modules.Config import wait_for_storage
from modules.Config import Configuration
from modules.Config import get_display_resolution
from modules.Config import setup_cv2_fullscreen


def countdown(bg_audio, total_playtime=None, start_playtime=None):
    """
    Countdown intro sequence.

    'bg_audio' is a pyglet.media.StaticSource created once externally and passed in.
    The Player is still created fresh each call (countdown runs infrequently so the
    OpenAL source is allocated/freed at most once per entropy cycle — low-risk).
    See __main__ for StaticSource creation.
    """

    print("Initializing COUNTDOWN video file: '{}'".format(cfg.entropy_countdown_video))
    c_video = cv.VideoCapture(str(cfg.entropy_countdown_video))
    screen_width = int(c_video.get(cv.CAP_PROP_FRAME_WIDTH))
    screen_height = int(c_video.get(cv.CAP_PROP_FRAME_HEIGHT))
    print('Video resolution detected as: {}x{}'.format(screen_width, screen_height))

    # bg_audio = pyglet.media.StaticSource(pyglet.media.load(str(cfg.entropy_countdown_audio), streaming=False))
    # ↑ MOVED to __main__ — StaticSource now passed in as 'bg_audio' to avoid reloading the file
    #   on every countdown() call. Player is still created fresh below (low risk, infrequent call).
    print('All the COUNTDOWN media loaded')

    if start_playtime is not None:
        c_video.set(cv.CAP_PROP_POS_FRAMES, start_playtime)

    # Display setup — create window once with combined flags.
    # WINDOW_NORMAL allows resizing; WINDOW_FREERATIO allows non-native aspect.
    # Without a WM (bare xinit), EWMH fullscreen hints are ignored, so we
    # manually resize to screen dims via setup_cv2_fullscreen().
    cv.namedWindow('countdown', cv.WINDOW_NORMAL | cv.WINDOW_FREERATIO)

    if cfg.fullscreen is True:
        print('Running in fullscreen mode')
        disp_w, disp_h = get_display_resolution()
        setup_cv2_fullscreen('countdown', disp_w, disp_h)
    else:
        print("Running in windowed mode (use '--fullscreen' runtime arg for fullscreen mode)")

    if node() == 'zeromini.local':
        print('Running at zeromini, sending window to another display')
        cv.moveWindow('countdown', 2600, 0)

    av_sync = 0
    frame_counter = 1
    frame_time = 25
    frame_drops = 0
    fra_min = 20
    fra_max = 30

    total_frames = c_video.get(cv.CAP_PROP_FRAME_COUNT)
    frame_effect = None

    countdown_seconds = int(total_frames / 25)
    countdown_coords = (30, 550)
    final_countdown = (countdown_seconds - 10) * 25
    countdown_sequence = False
    countdown_mask_master = np.zeros((screen_height, screen_width), dtype="uint8")

    scroll = screen_width
    change_effect_interval = 300

    playback = True
    bg_player = bg_audio.play()

    while playback is True:

        # Get next video frame
        status, frame = c_video.read()

        if total_playtime is not None and frame_counter == total_playtime:
            status = False

        if status is True:

            # AV Syncing
            current_audio_frame = round(round(bg_player.time, 6) * 25, 0)
            av_sync = current_audio_frame - frame_counter

            # Countdown number
            if frame_counter % 25 == 0:
                countdown_seconds -= 1

            if countdown_seconds < 100:
                countdown_coords = (240, 550)

            # Create blank countdown mask
            countdown_mask = countdown_mask_master.copy()
            cv.putText(countdown_mask,
                       str(countdown_seconds),
                       countdown_coords,
                       cv.FONT_HERSHEY_PLAIN,
                       43,
                       (255, 255, 255),
                       125,
                       cv.LINE_AA)

            # Generate random lines over the mask layer (Atari 800 tape loading)
            axe_y = 0
            for line_number in range(0, 100):
                line_position = randint(10, 13)
                axe_y += line_position
                cv.line(countdown_mask, (0, axe_y), (screen_width, axe_y), (255, 255, 255), 2)
                if axe_y > screen_height:
                    break

            # Apply different color tone every X seconds
            if frame_counter % change_effect_interval == 0:
                frame_effect = choice(cfg.color_effect)

            if frame_effect is not None:
                cv.applyColorMap(src=frame, colormap=frame_effect, dst=frame)

            # Blur background layer
            cv.blur(src=frame, ksize=(10, 10), dst=frame)

            # Apply countdown mask
            frame = cv.bitwise_and(frame, frame, mask=countdown_mask)

            if frame_counter > final_countdown:
                countdown_sequence =  True

            # Make thick black strip
            cv.line(frame, (0, 645), (screen_width, 645), (0, 0, 0), 70)

            if countdown_sequence is False:
                cv.putText(frame,
                           '+   {}   +   {} {} SECONDS     +'.format(cfg.entropy_overlays['countdown'][0],
                                                                     cfg.entropy_overlays['countdown'][1],
                                                                     countdown_seconds),
                           (scroll, 660),
                           cv.FONT_HERSHEY_TRIPLEX,
                           1.5,
                           (25, 190, 20),
                           randint(1, 3),
                           cv.LINE_AA)
                scroll -= 3
                if scroll < -2100:
                    scroll = screen_width
            else:
                cv.putText(frame,
                           'COUNTDOWN',
                           # (300, 660),
                           (330, 660),
                           cv.FONT_HERSHEY_TRIPLEX,
                           1.5,
                           (25, 190, 20),
                           randint(1, 3),
                           cv.LINE_AA)

            try:
                cv.imshow('countdown', frame)
            except Exception as playback_error:
                print('Playback failing...')
                print(playback_error)

            frame_counter += 1

        else:
            print('End of the countdown, releasing audio and video streams')
            c_video.release()
            cv.destroyAllWindows()
            cv.waitKey(1)  # Need this line to wait for the destroy actions to complete
            bg_player.delete()
            print('AV streams released, countdown finished')
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

def entropy(audio, total_playtime=None, start_playtime=0):
    """
    Entropy main playback loop.

    'audio' is a pyglet.media.StaticSource created ONCE in __main__ and passed in.
    The Player ('aplayer') is also created once here and reused across every cycle via
    aplayer.seek(0) + aplayer.play() — this avoids allocating a new OpenAL source
    each cycle. OpenAL-soft has a hard 256-source limit; the old pattern of
    aplayer.delete() + audio.play() on every cycle exhausted it after ~256 plays
    and crashed audio entirely.

    The function loops internally (while True) — it never returns. The outer while True
    in __main__ is therefore effectively dead after the first call; countdown() runs once
    at boot before entropy() takes over indefinitely.
    """

    print("Initializing ENTROPY video file: '{}'".format(cfg.entropy_main_video))
    e_video = cv.VideoCapture(str(cfg.entropy_main_video))
    screen_width = int(e_video.get(cv.CAP_PROP_FRAME_WIDTH))
    screen_height = int(e_video.get(cv.CAP_PROP_FRAME_HEIGHT))
    print('Video resolution detected as: {}x{}'.format(screen_width, screen_height))
    total_frames = e_video.get(cv.CAP_PROP_FRAME_COUNT)
    print('Total video frames: {}'.format(total_frames))
    print("Initializing ENTROPY audio file: '{}'".format(cfg.entropy_main_audio))
    # audio = pyglet.media.StaticSource(pyglet.media.load(str(cfg.entropy_main_audio), streaming=False))
    # ↑ MOVED to __main__ — StaticSource and the Player are now created once and reused
    #   across all cycles via seek(0). Creating it here allocated a new OpenAL source
    #   on every entropy() call, exhausting the 256-source pool after ~256 video loops.
    # video.set(cv.CAP_PROP_BUFFERSIZE, 5)
    print('All the ENTROPY media loaded')

    e_video.set(cv.CAP_PROP_POS_FRAMES, start_playtime)

    qr_code = cv.imread(str(cfg.entropy_qr_code))

    # Display setup — see countdown() for fullscreen rationale.
    cv.namedWindow('entropy', cv.WINDOW_NORMAL | cv.WINDOW_FREERATIO)
    if cfg.fullscreen is True:
        print('Running in fullscreen mode')
        disp_w, disp_h = get_display_resolution()
        setup_cv2_fullscreen('entropy', disp_w, disp_h)
    else:
        print("Running in windowed mode (use '--fullscreen' runtime arg for fullscreen mode)")

    if node() == 'zeromini.local':
        print('Running at zeromini, sending window to another display')
        cv.moveWindow('entropy', 2600, 0)

    av_sync = 0
    frame_counter = 1
    frame_time = 25
    frame_drops = 0
    fra_min = 5
    fra_max = 30

    # font_status = cfg.font['status']
    font_scale = 1
    coord = (50, 50)
    subtitle = None

    intro = (50, 850)
    outro = (7600, 8100)
    entropy_motto = None

    alpha = 0.1

    # Show QR Code
    cv.imshow('entropy', qr_code)
    cv.waitKey(100)


    # Run audio track — Player created once here; reused across all cycles via seek(0).
    # Previously: aplayer = audio.play() was inside entropy() which got called fresh each
    # cycle from the outer while True, allocating a new OpenAL source every time.
    aplayer = audio.play()
    # playback = True  # REMOVED: loop is now internal (while True below); no longer needed

    # Main video loop — runs indefinitely; entropy() never returns.
    # The outer `while True` in __main__ is dead code after the first call.
    while True:

        # Get next video frame
        status, frame = e_video.read()

        if total_playtime is not None and frame_counter * 25 == total_playtime:
            status = False

        if status is True:

            current_audio_frame = round(round(aplayer.time, 6) * 25, 0)
            av_sync = current_audio_frame - frame_counter

            # Intro and outro
            if frame_counter == intro[0]:
                entropy_motto = cfg.entropy_overlays['intro']
            elif frame_counter == intro[1]:
                entropy_motto = None
            elif frame_counter == outro[0]:
                entropy_motto = cfg.entropy_overlays['outro']
            elif frame_counter == outro[1]:
                entropy_motto = None

            if entropy_motto is not None:
                axe_y = int(screen_height / 3)
                for quote in entropy_motto:
                    thickness_intro = randint(1, 3)
                    # Get the size of the text box
                    text_box = cv.getTextSize(quote, cv.FONT_HERSHEY_TRIPLEX, 1.5, thickness_intro)
                    axe_x = int((screen_width - text_box[0][0]) / 2)
                    axe_y += text_box[0][1] + 50
                    cv.putText(frame,
                               quote,
                               (axe_x, axe_y),
                               # cv.FONT_HERSHEY_TRIPLEX,
                               cfg.font[2],
                               1.5,
                               (25, 190, 20),
                               thickness_intro,
                               cv.LINE_AA)

            # Lyrics subtitle overlay
            subtitle_cue = None

            try:
                subtitle_cue = datetime.strptime(str(timedelta(seconds=round(aplayer.time, 6))), '%H:%M:%S.%f').time().replace(microsecond=0)
            except Exception as runtime_problem:
                print('Runtime failing: {}'.format(runtime_problem))

            if subtitle_cue in cfg.entropy_subs:
                subtitle = cfg.entropy_subs[subtitle_cue]
                if subtitle is not None:
                    coord = (randint(5, 350), randint(200, 700))
                    font_scale = uniform(0.6, 1.4)
                    text_box = cv.getTextSize(subtitle, cv.FONT_HERSHEY_TRIPLEX, font_scale, 3)
                    if text_box[0][0] > screen_width - coord[0]:
                        coord = (screen_width - text_box[0][0] - 10, randint(200, 800))

            if subtitle is not None:
                cv.putText(frame,
                           subtitle,
                           coord,
                           cv.FONT_HERSHEY_TRIPLEX,
                           font_scale,
                           (25, 190, 20),
                           randint(1, 3),
                           cv.LINE_AA)

            # Statistics Overlays
            status_1 = 'a-v sync: {} ++ v{} / a{} / ft{} ++ {} / {}'.format(av_sync,
                                                                   frame_counter,
                                                                   current_audio_frame,
                                                                   frame_time,
                                                                   subtitle_cue,
                                                                   round(aplayer.time, 6))
            status_2 = 'mission time: {} ++ expedition: {} (f{} | v:{}) ++ min/max thr: <{}/{}>'.format(
                datetime.now().strftime("%H:%M:%S.%f"),
                cfg.entropy_expedition,
                frame_counter,
                aplayer.volume,
                fra_min,
                fra_max)

            cv.putText(frame,
                       status_1,
                       (50, 50),
                       cv.FONT_HERSHEY_PLAIN,
                       1.5,
                       (0, 50, 200),
                       2,
                       cv.LINE_AA)

            cv.putText(frame,
                       status_2,
                       (50, 75),
                       cv.FONT_HERSHEY_PLAIN,
                       1.5,
                       (0, 50, 200),
                       2,
                       cv.LINE_AA)

            # Display GUI
            gui_thickness = randint(1, 3)
            cv.rectangle(frame, (10, 10), (screen_width - 10, screen_height - 10), (0, 50, 200), gui_thickness)
            cv.line(frame, (10, 100), (screen_width - 10, 100), (0, 50, 200), gui_thickness)

            try:
                if frame_time > 5:
                    cv.imshow('entropy', frame)
                else:
                    print('Dropping frame {} | ft={} | avsync={} | total_drops={}'.format(frame_counter, av_sync, frame_time, frame_drops))
                    frame_drops += 1

            except Exception as playback_error:
                print('Playback failing...')
                print(playback_error)

            frame_counter += 1

        else:
            print('End of cycle {} frame_counter={}'.format(cfg.entropy_expedition, frame_counter))
            cfg.entropy_expedition += 1
            print('Releasing AV media')
            try:
                e_video.release()
                # cv.destroyAllWindows()  # OLD: destroyed window each cycle — removed to avoid flash between loops
                # cv.waitKey(1)           # OLD: was needed after destroyAllWindows; no longer required
                # aplayer.delete()        # OLD: freed the OpenAL source each cycle → exhausted pool at ~256 plays
                aplayer.seek(0)           # NEW: rewind audio to start — same OpenAL source reused indefinitely
                aplayer.play()            # resume from the beginning
                e_video = cv.VideoCapture(str(cfg.entropy_main_video))   # reopen video stream from the start
                frame_counter = 1
                print('AV media reset for next cycle')
            except Exception as av_error:
                print('AV media reset fail: {}'.format(av_error))
            # playback = False  # OLD: exited inner loop so outer while True would call entropy() fresh next cycle

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

    cfg = Configuration(arg.fullscreen, runtime='entropy')

    # Create audio StaticSources once for the entire runtime lifetime.
    # Previously these were created inside countdown()/entropy() on every call (every video cycle),
    # allocating a new OpenAL source each time. OpenAL-soft has a hard 256-source limit;
    # after ~256 cycles the pool was exhausted and audio crashed with no recovery.
    # By creating them here and passing them in, the Player is also reused via seek(0)
    # in entropy(), meaning the OpenAL source count stays constant at 1 indefinitely.
    countdown_audio = pyglet.media.StaticSource(pyglet.media.load(str(cfg.entropy_countdown_audio), streaming=False))
    entropy_audio   = pyglet.media.StaticSource(pyglet.media.load(str(cfg.entropy_main_audio),      streaming=False))

    while True:
        # countdown() runs once at boot (entropy() loops internally and never returns).
        # countdown_thread = Thread(target=countdown())  # OLD: countdown() took no audio arg
        countdown_thread = Thread(target=countdown(countdown_audio))
        # entropy_thread = Thread(target=entropy())      # OLD: entropy() took no audio arg; created StaticSource fresh each call
        entropy_thread = Thread(target=entropy(entropy_audio))
