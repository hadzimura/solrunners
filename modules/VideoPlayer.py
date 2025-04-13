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

from modules.Controllers import Text

# font = ImageFont.truetype("/home/zero/solrunners/media/fonts/Mx437_EpsonMGA_Mono.ttf", 50)
# font = ImageFont.truetype("/Users/zero/Develop/github.com/hadzimura/solrunners/media/fonts/Mx437_EpsonMGA_Mono.ttf", 50)

# def text_overlay(frame, text, coordinates, fa, type_of='console'):
#     # font_subs = ImageFont.truetype("/Users/zero/Develop/github.com/hadzimura/solrunners/media/fonts/IBM_Logo_Regular_400.ttf", fa)
#     font_subs = ImageFont.truetype("/home/zero/solrunners/media/fonts/IBM_Logo_Regular_400.ttf", fa)
#
#     cv2_im_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
#     pil_im = Image.fromarray(cv2_im_rgb)
#     draw = ImageDraw.Draw(pil_im)
#
#     # Draw the text
#     # draw.text(self.coordinates, 'mission time', font=self.font, fill="#41FF00")
#     if type_of == 'subtitle':
#         draw.text(coordinates, str(text), font=font_subs, fill="#41FF00")
#     else:
#         draw.text(coordinates, str(text), font=font, fill="#41FF00")
#     return np.array(pil_im)

async def heads(config, audio_player):
    # Initialize Player Layers
    c = config
    c.set_playhead2(layer='main', category='tate')
    player_name = 'tate'
    frame = 0
    defined_sync = 14
    sync = defined_sync
    # pitch = 0.5

    # Global settings for runtime
    cv.namedWindow(player_name, cv.WINDOW_AUTOSIZE)
    # cv.namedWindow(player_name, cv.WINDOW_FREERATIO)
    cv.setWindowProperty(player_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    # cv.setWindowProperty(player_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)

    audio_player.play_audio(int(c.playing['main']['name']) - 1)
    # audio_player.p.pitch = pitch
    # Main video loop
    while True:

        try:
            c.playing['main']['stream'].set(cv.CAP_PROP_FRAME_WIDTH, 640)
            c.playing['main']['stream'].set(cv.CAP_PROP_FRAME_HEIGHT, 480)
            c.playing['main']['stream'].get(cv.CAP_PROP_FRAME_WIDTH)

            main_status, main_frame = c.playing['main']['stream'].read()
            width, height = c.playing['main']['stream'].get(3), c.playing['main']['stream'].get(4)
            frame += 1
            # if frame / sync == 1:
            #     v = round(c.playing['main']['stream'].get(cv.CAP_PROP_POS_MSEC)/1000, 3)
            #     a = round(audio_player.p.time, 3)
            #     print(a, v)
            #     if a != v:
            #     # print(frame, c.playing['main']['stream'].get(cv.CAP_PROP_POS_FRAMES), audio_player.p.time)
            #         audio_player.p.seek(c.playing['main']['stream'].get(cv.CAP_PROP_POS_MSEC)/1000)
            #     sync += defined_sync

            # cv.namedWindow(player_name, cv.WINDOW_NORMAL)
            # cv.namedWindow(player_name, cv.WINDOW_FREERATIO)
            # cv.setWindowProperty(player_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
            # cv.moveWindow(player_name, int((640 / 2) - (width / 2)), int((480 / 2) - (height / 2)))
            if main_status is True:

                if c.blur.enabled is True:
                    main_frame = cv.blur(main_frame, c.blur.value)

                # if c.mix.enabled is True:
                    # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                    # frame = cv.applyColorMap(frame, cv.COLORMAP_PLASMA)
                    # frame = cv.applyColorMap(frame, cv.COLORMAP_TWILIGHT)
                    # frame = cv.applyColorMap(frame, cv.COLORMAP_OCEAN)
                    # frame = cv.applyColorMap(frame, cv.COLORMAP_WINTER)
                    # frame = Summer(frame)

                    # overlay_frame = cv.applyColorMap(overlay_frame, cv.COLORMAP_PLASMA)
                    # # frame = cv.addWeighted(frame, c.blend_value[0], blend_frame, c.blend_value[1], c.blend_value[2])
                    # main_frame = cv.addWeighted(main_frame, c.mix.value[0], overlay_frame, c.mix.value[1],
                    #                             c.mix.value[2])

                f = c.font['runtime']
                # cv.putText(main_frame, c.playing['main']['name'], [50, 50], f.name, f.scale, f.color, f.thickness, f.type)
                # cv.putText(main_frame, str(c.playing['main']['stream'].get(cv.CAP_PROP_POS_FRAMES)), [50, 50], f.name, f.scale, f.color, f.thickness, f.type)
                cv.putText(main_frame, 'v: {}'.format(str(round(c.playing['main']['stream'].get(cv.CAP_PROP_POS_MSEC)/1000, 3))), [50, 50], f.name, f.scale, f.color, f.thickness, f.type)
                cv.putText(main_frame, 'a: {}'.format(str(round(audio_player.p.time, 3))), [50, 100], f.name, f.scale, f.color, f.thickness, f.type)
                cv.putText(main_frame, '{}x{}'.format(c.playing['main']['stream'].get(cv.CAP_PROP_FRAME_WIDTH), height), [50, 150], f.name, f.scale, f.color, f.thickness, f.type)
                # int(c.playing['main']['name'])

                cv.imshow(player_name, main_frame)
                cv.moveWindow(player_name, 0, 0)

            else:
                # e.set_playhead(layer=0, category='feature', stream='entropy.mov')
                c.set_playhead2(layer='main', category='tate')
                audio_player.play_audio(int(c.playing['main']['name']) - 1)
                # audio_player.p.pitch = pitch
                frame = 0
                sync = defined_sync

            # cv.waitKey(0)
            # This actually controls the playback speed!
            if c.read_input(cv.waitKey(int(c.playing['main']['stream'].get(cv.CAP_PROP_FPS)))) is False:
                # Method returns False for ESC key
                break

            # Prepare data for next frame processing
            c.update()
            await asyncio.sleep(0.001)

        except Exception as runtime_problem:
            print('Runtime failing: {}'.format(runtime_problem))

    # Release everything
    c.playing[0]['stream'].release()
    try:
        c.playing[1]['stream'].release()
        c.playing[2]['stream'].release()
    except KeyError:
        pass
    cv.destroyAllWindows()

async def tate_linear(config, audio_player):
    # Initialize Player Layers
    c = config
    c.set_playhead2(layer='main', category='tate')
    player_name = 'tate'
    frame = 0
    defined_sync = 14
    sync = defined_sync
    # pitch = 0.5

    # Global settings for runtime
    cv.namedWindow(player_name, cv.WINDOW_AUTOSIZE)
    # cv.namedWindow(player_name, cv.WINDOW_FREERATIO)
    cv.setWindowProperty(player_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    # cv.setWindowProperty(player_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)

    audio_player.play_audio(int(c.playing['main']['name']) - 1)
    # audio_player.p.pitch = pitch
    # Main video loop
    while True:

        try:
            c.playing['main']['stream'].set(cv.CAP_PROP_FRAME_WIDTH, 640)
            c.playing['main']['stream'].set(cv.CAP_PROP_FRAME_HEIGHT, 480)
            c.playing['main']['stream'].get(cv.CAP_PROP_FRAME_WIDTH)

            main_status, main_frame = c.playing['main']['stream'].read()
            width, height = c.playing['main']['stream'].get(3), c.playing['main']['stream'].get(4)
            frame += 1
            # if frame / sync == 1:
            #     v = round(c.playing['main']['stream'].get(cv.CAP_PROP_POS_MSEC)/1000, 3)
            #     a = round(audio_player.p.time, 3)
            #     print(a, v)
            #     if a != v:
            #     # print(frame, c.playing['main']['stream'].get(cv.CAP_PROP_POS_FRAMES), audio_player.p.time)
            #         audio_player.p.seek(c.playing['main']['stream'].get(cv.CAP_PROP_POS_MSEC)/1000)
            #     sync += defined_sync

            # cv.namedWindow(player_name, cv.WINDOW_NORMAL)
            # cv.namedWindow(player_name, cv.WINDOW_FREERATIO)
            # cv.setWindowProperty(player_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
            # cv.moveWindow(player_name, int((640 / 2) - (width / 2)), int((480 / 2) - (height / 2)))
            if main_status is True:

                if c.blur.enabled is True:
                    main_frame = cv.blur(main_frame, c.blur.value)

                # if c.mix.enabled is True:
                    # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                    # frame = cv.applyColorMap(frame, cv.COLORMAP_PLASMA)
                    # frame = cv.applyColorMap(frame, cv.COLORMAP_TWILIGHT)
                    # frame = cv.applyColorMap(frame, cv.COLORMAP_OCEAN)
                    # frame = cv.applyColorMap(frame, cv.COLORMAP_WINTER)
                    # frame = Summer(frame)

                    # overlay_frame = cv.applyColorMap(overlay_frame, cv.COLORMAP_PLASMA)
                    # # frame = cv.addWeighted(frame, c.blend_value[0], blend_frame, c.blend_value[1], c.blend_value[2])
                    # main_frame = cv.addWeighted(main_frame, c.mix.value[0], overlay_frame, c.mix.value[1],
                    #                             c.mix.value[2])

                f = c.font['runtime']
                # cv.putText(main_frame, c.playing['main']['name'], [50, 50], f.name, f.scale, f.color, f.thickness, f.type)
                # cv.putText(main_frame, str(c.playing['main']['stream'].get(cv.CAP_PROP_POS_FRAMES)), [50, 50], f.name, f.scale, f.color, f.thickness, f.type)
                cv.putText(main_frame, 'v: {}'.format(str(round(c.playing['main']['stream'].get(cv.CAP_PROP_POS_MSEC)/1000, 3))), [50, 50], f.name, f.scale, f.color, f.thickness, f.type)
                cv.putText(main_frame, 'a: {}'.format(str(round(audio_player.p.time, 3))), [50, 100], f.name, f.scale, f.color, f.thickness, f.type)
                cv.putText(main_frame, '{}x{}'.format(c.playing['main']['stream'].get(cv.CAP_PROP_FRAME_WIDTH), height), [50, 150], f.name, f.scale, f.color, f.thickness, f.type)
                # int(c.playing['main']['name'])

                cv.imshow(player_name, main_frame)
                cv.moveWindow(player_name, 0, 0)

            else:
                # e.set_playhead(layer=0, category='feature', stream='entropy.mov')
                c.set_playhead2(layer='main', category='tate')
                audio_player.play_audio(int(c.playing['main']['name']) - 1)
                # audio_player.p.pitch = pitch
                frame = 0
                sync = defined_sync

            # cv.waitKey(0)
            # This actually controls the playback speed!
            if c.read_input(cv.waitKey(int(c.playing['main']['stream'].get(cv.CAP_PROP_FPS)))) is False:
                # Method returns False for ESC key
                break

            # Prepare data for next frame processing
            c.update()
            await asyncio.sleep(0.001)

        except Exception as runtime_problem:
            print('Runtime failing: {}'.format(runtime_problem))

    # Release everything
    c.playing[0]['stream'].release()
    try:
        c.playing[1]['stream'].release()
        c.playing[2]['stream'].release()
    except KeyError:
        pass
    cv.destroyAllWindows()

async def tate(config):

    # Initialize Player Layers
    c = config
    c.set_playhead2(layer='main', category='tate')
    c.set_playhead2(layer='overlay', category='tate')

    player_name = 'tate'

    # Global settings for runtime
    cv.namedWindow(player_name, cv.WINDOW_NORMAL)
    cv.namedWindow(player_name, cv.WINDOW_FREERATIO)
    cv.setWindowProperty(player_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    # Main video loop
    while True:

        try:

            main_status, main_frame = c.playing['main']['stream'].read()

            # Overlay Tate Layer
            if c.mix.enabled is True:
                overlay_status, overlay_frame = c.playing['overlay']['stream'].read()
                
                # When blending segment ends, start a new one
                if overlay_status is False:
                    c.set_playhead2(layer='overlay', category='tate')
                    overlay_status, overlay_frame = c.playing['overlay']['stream'].read()

            if main_status is True:

                if c.blur.enabled is True:
                    main_frame = cv.blur(main_frame, c.blur.value)

                if c.offset.enabled is True:
                    # 0,300,
                    # x,
                    left = main_frame[0:1080, 1920-c:1920].copy()
                    right = main_frame[0:1080, 0:1920-c].copy()
                    main_frame = cv.hconcat([left, right])
                    c += 5
                    if c > 1920:
                        c = 0

                if c.mix.enabled is True:
                    # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                    # frame = cv.applyColorMap(frame, cv.COLORMAP_PLASMA)
                    # frame = cv.applyColorMap(frame, cv.COLORMAP_TWILIGHT)
                    # frame = cv.applyColorMap(frame, cv.COLORMAP_OCEAN)
                    # frame = cv.applyColorMap(frame, cv.COLORMAP_WINTER)
                    # frame = Summer(frame)

                    overlay_frame = cv.applyColorMap(overlay_frame, cv.COLORMAP_PLASMA)
                    # frame = cv.addWeighted(frame, c.blend_value[0], blend_frame, c.blend_value[1], c.blend_value[2])
                    main_frame = cv.addWeighted(main_frame, c.mix.value[0], overlay_frame, c.mix.value[1], c.mix.value[2])

                # final = cv.vconcat([frame, face2])
                # frame = cv.addWeighted(frame, 1, frame, 0.5, 2)

                # frame = cv.blur(frame, play.blur)
                # Create black canvas for each display
                # canvas = np.zeros((720, 1280, 3), np.uint8)
                # Apply the media image to canvas
                # canvas[:, :] = frame
                # Mix in some letters

                # Subtitles overlay
                if c.playing['main']['frame'] in c.sub:
                    c.subtitle = c.sub[c.playing['main']['frame']]

                if c.subtitle is not None:
                    f = c.font['subtitle']
                    cv.putText(main_frame, c.subtitle, f.org, f.name, f.scale, f.color, f.thickness, f.type)

                # Status overlay
                f = c.font['status']
                cv.putText(main_frame, c.playing['main']['name'], f.org, f.name, f.scale, f.color, f.thickness, f.type)
                if c.mix.enabled:
                    cv.putText(main_frame, c.playing['overlay']['name'], [50,100], f.name, f.scale, f.color, f.thickness, f.type)

                # Runtime overlay
                # f = c.font['runtime']
                # cv.putText(frame, c.get_info('runtime'), f.org, f.name, f.scale, f.color, f.thickness, f.type)

                # Mission time overlay
                # f = c.font['mission']
                # cv.putText(frame, c.get_info('mission'), f.org, f.name, f.scale, f.color, f.thickness, f.type)

                # Drawings
                for o, d in c.draw.items():
                    if d.shape == 'rectangle':
                        cv.rectangle(main_frame, d.pos1, d.pos2, d.color, d.thickness, d.type)

                try:
                    cv.imshow(player_name, main_frame)
                    cv.moveWindow(player_name, 0, 0)

                except Exception as c:
                    print(c)
                    exit(1)
            else:
                # e.set_playhead(layer=0, category='feature', stream='entropy.mov')
                c.set_playhead2(layer='main', category='tate')

            # cv.waitKey(0)
            # This actually controls the playback speed!
            if c.read_input(cv.waitKey(c.fps)) is False:
                # Method returns False for ESC key
                break

            # Prepare data for next frame processing
            c.update()
            await asyncio.sleep(0.00005)

        except Exception as runtime_problem:
            print('Runtime failing: {}'.format(runtime_problem))

    # Release everything
    c.playing[0]['stream'].release()
    try:
        c.playing[1]['stream'].release()
        c.playing[2]['stream'].release()
    except KeyError: pass
    cv.destroyAllWindows()

async def entropy(cfg, aplayer):

    overlays = False

    try:
        print('Attached display info:')
        screen = get_monitors()[0]
        print(screen)
    except Exception as e:
        print(e)

    width, height = screen.width, screen.height

    video = cv.VideoCapture(str(cfg.entropy_video))
    # video.set(cv.CAP_PROP_BUFFERSIZE, 25)

    # self.playing[layer]['stream'].set(cv.CAP_PROP_POS_FRAMES, start_frame)
    # video.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    # video.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    # self.playing[layer]['stream'].set(cv.CAP_PROP_BUFFERSIZE, self.fps)
    # video.set(cv.CAP_PROP_FPS, 25)

    # eplayer.set_entropy_playhead(start_frame=0)
    # cv.namedWindow('entropy', cv.WINDOW_NORMAL)
    cv.namedWindow('entropy', cv.WND_PROP_FULLSCREEN)
    # cv.namedWindow('entropy', cv.WINDOW_FREERATIO)

    # cv.namedWindow('entropy', cv.WINDOW_AUTOSIZE)
    cv.setWindowProperty('entropy', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    # cv.setWindowProperty('entropy', cv.WND_PROP_FULLSCREEN, 1)

    frame_time = 25
    fra_min = 25
    fra_max = 25

    font_status = cfg.font['status']
    subtitle = None

    # Run audio track
    aplayer.eplay(action='init')
    # aplayer.play_audio(1, overlay=True)
    # aplayer.play_audio(2, overlay=True)
    # aplayer.play_audio(3, overlay=True)

    # Main video loop
    frame_counter = 0
    frame_average = 0
    while True:

        status, frame = video.read()

        if status is True:

            # Subtitles overlay
            current_audio_frame = round(aplayer.etime() * 25, 0)
            subtitle_cue = None
            av_sync = current_audio_frame - frame_counter

            if overlays is True:

                try:
                    subtitle_cue = datetime.strptime(str(timedelta(seconds=aplayer.etime())), '%H:%M:%S.%f').time().replace(microsecond=0)
                except Exception as runtime_problem:
                    print('Runtime failing: {}'.format(runtime_problem))

                # if frame_counter % 100 == 0:
                #     print('swap')
                #     aplayer.eplay(action='swap')



                if subtitle_cue in cfg.sub['entropy']:
                    subtitle = cfg.sub['entropy'][subtitle_cue]
                    coo = (randint(5, 400), randint(300, 1000))
                    fs = uniform(0.5, 1.9)

                if subtitle is not None:
                    cv.putText(frame, subtitle, coo, font_status.name, fs, font_status.color, font_status.thickness, font_status.type)
                t = 'a-v: {} | v:{} a:{} ft: {} / {} / {}'.format(av_sync, frame_counter, current_audio_frame, frame_time,  subtitle_cue, aplayer.etime())
                cv.putText(frame, t, font_status.org, font_status.name, font_status.scale, font_status.color, font_status.thickness, font_status.type)

                t = 'f: {} // l: {} x {} | r: {} x {} | min/max: {}/{}'.format(frame_counter, aplayer.p['L'][0].volume, aplayer.p['L'][1].volume, aplayer.p['R'][0].volume, aplayer.p['R'][1].volume, fra_min, fra_max)
                cv.putText(frame, t, (50, 100), font_status.name, font_status.scale, font_status.color, font_status.thickness, font_status.type)

            try:
                cv.imshow('entropy', frame)
                # cv.moveWindow('entropy', 0, 0)

            except Exception as playback:
                print(playback)
                exit(1)
            frame_counter += 1

        else:
            print('End of cycle')
            video.set(cv.CAP_PROP_POS_FRAMES, 0)
            # aplayer.eplay(action='init')
            frame_counter = 0
            # aplayer.stop_audio()
            # aplayer.play_audio(0, overlay=True)
            # aplayer.play_audio(1, overlay=True)
            # aplayer.play_audio(2, overlay=True)
            # aplayer.play_audio(3, overlay=True)

        # cv.waitKey(0)
        if av_sync > 0:
            frame_time -=1
        else:
            frame_time +=1
        if frame_time < 1:
            frame_time = 1

        if frame_time > fra_max:
            fra_max = frame_time
            print('max', fra_max)
        if frame_time < fra_min:
            fra_min = frame_time
            print('min', fra_min)

        if frame_time == 1:
            print("Moving {} frames ahead".format(current_audio_frame - video.get(cv.CAP_PROP_POS_FRAMES)))
            video.set(cv.CAP_PROP_POS_FRAMES, current_audio_frame)

        # This actually controls the playback speed!
        if cfg.read_input(cv.waitKey(frame_time)) is False:
            # Method returns False for ESC key
            break

        # Prepare data for next frame processing
        # eplayer.update()
        # await asyncio.sleep(0.0000005)


    # Release everything
    video.release()
    cv.destroyAllWindows()
