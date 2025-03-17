#!/usr/bin/env python3
# coding=utf-8

# Springs of Life (2025)
# rkucera@gmail.com
import asyncio
import cv2 as cv
from pprint import pprint
from random import choice
from time import sleep

from modules.SolVideo import Configuration

async def ppl(config):
    pass

async def ocv(config, player_name='Entropy'):

    c = config
    # Initialize Player
    # entropy.set_playhead(layer=0, category='feature', stream='entropy.mov')
    c.set_playhead2(layer='main', category='tate')
    c.set_playhead2(layer='overlay', category='tate')

    # Global settings for runtime
    cv.namedWindow(player_name, cv.WINDOW_NORMAL)
    # if c.fullscreen is True:
    cv.setWindowProperty(player_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    # Main video loop
    while True:

        # Main Entropy track
        status, frame = c.playing['main']['stream'].read()

        # Blend layer 1
        if c.mix.enabled is True:
            blend_status, blend_frame = c.playing['overlay']['stream'].read()
            # When blending segment ends, start a new one
            if blend_status is False:
                c.set_playhead2(layer='overlay', category='tate')
                blend_status, blend_frame = c.playing['overlay']['stream'].read()

        if status is True:

            # Effects first
            # if entropy.flip.enabled is True:
            #     frame = cv.flip(frame, 0)
            #
            # if entropy.gray.enabled is True:
            #     a = choice([1, 2, 3])
            #     if a == 1:
            #         # ss = cv.applyColorMap(ss, cv.COLORMAP_PLASMA)
            #         frame = cv.addWeighted(ss, 0.5, frame, 0.5, 0.5)
            #
            #
            #     # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            #     # frame = cv.applyColorMap(frame, cv.COLORMAP_PLASMA)
            #     # frame = cv.applyColorMap(frame, cv.COLORMAP_TWILIGHT)
            #     # frame = cv.applyColorMap(frame, cv.COLORMAP_OCEAN)
            #     # frame = cv.applyColorMap(frame, cv.COLORMAP_WINTER)
            #     # frame = Summer(frame)
            #     pass

            if c.blur.enabled is True:
                frame = cv.blur(frame, c.blur_value)

            if c.offset.enabled is True:
                # 0,300,
                # x,
                left = frame[0:1080, 1920-c:1920].copy()
                right = frame[0:1080, 0:1920-c].copy()
                frame = cv.hconcat([left, right])
                c += 5
                if c > 1920:
                    c = 0

            if c.mix.enabled is True:
                # frame = cv.addWeighted(frame, c.blend_value[0], blend_frame, c.blend_value[1], c.blend_value[2])
                frame = cv.addWeighted(frame, c.mix.value[0], blend_frame, c.mix.value[1], c.mix.value[2])

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
                cv.putText(frame, c.subtitle, f.org, f.name, f.scale, f.color, f.thickness, f.type)

            # Status overlay
            # f = c.font['status']
            # cv.putText(frame, c.get_info('status'), f.org, f.name, f.scale, f.color, f.thickness, f.type)

            # Runtime overlay
            # f = c.font['runtime']
            # cv.putText(frame, c.get_info('runtime'), f.org, f.name, f.scale, f.color, f.thickness, f.type)

            # Mission time overlay
            # f = c.font['mission']
            # cv.putText(frame, c.get_info('mission'), f.org, f.name, f.scale, f.color, f.thickness, f.type)

            # Drawings
            for o, d in c.draw.items():
                if d.shape == 'rectangle':
                    cv.rectangle(frame, d.pos1, d.pos2, d.color, d.thickness, d.type)

            try:
                cv.imshow(player_name, frame)
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


    # Release everything
    c.playing[0]['stream'].release()
    try:
        c.playing[1]['stream'].release()
        c.playing[2]['stream'].release()
    except KeyError: pass
    cv.destroyAllWindows()
