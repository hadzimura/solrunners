#!/usr/bin/env python3
# coding=utf-8

# Springs of Life (2025)
# rkucera@gmail.com

import cv2 as cv
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from random import choice

from modules.Config import Configuration

# Parse input arguments
set_fullscreen = bool
parser = ArgumentParser(description='Entropy Video Player',
	                        epilog='Author: rkucera@gmail.com',
	                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-f', '--fullscreen',
	                    default=False,
	                    dest='set_fullscreen',
	                    help='Run Player in fullscreen mode')

# Initialize Configuration object
entropy = Configuration(fullscreen=set_fullscreen)

# Initialize Player
entropy.set_playhead(layer=0, category='feature', stream='entropy.mov')

entropy

# Global settings for runtime
cv.namedWindow('Entropy', cv.WINDOW_NORMAL)
if entropy.fullscreen is True:
    cv.setWindowProperty('Entropy', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

c = 1
ss = cv.imread('tyler/sss2.png')
# ssc = ss[0:100, 0:107]

# Main video loop
while True:

    # Main Entropy track
    status, frame = entropy.playing[0]['stream'].read()

    # Blend layer 1
    if entropy.mix.enabled is True:
        blend_status, blend_frame = entropy.playing[1]['stream'].read()
        # When blending segment ends, start a new one
        if blend_status is False:
            entropy.set_playhead(layer=1, category='face')
            blend_status, blend_frame = entropy.playing[1]['stream'].read()

    if status is True:

        # Effects first
        if entropy.flip.enabled is True:
            frame = cv.flip(frame, 0)

        if entropy.gray.enabled is True:
            a = choice([1, 2, 3])
            if a == 1:
                # ss = cv.applyColorMap(ss, cv.COLORMAP_PLASMA)
                frame = cv.addWeighted(ss, 0.5, frame, 0.5, 0.5)


            # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            # frame = cv.applyColorMap(frame, cv.COLORMAP_PLASMA)
            # frame = cv.applyColorMap(frame, cv.COLORMAP_TWILIGHT)
            # frame = cv.applyColorMap(frame, cv.COLORMAP_OCEAN)
            # frame = cv.applyColorMap(frame, cv.COLORMAP_WINTER)
            # frame = Summer(frame)
            pass

        if entropy.blur.enabled is True:
            frame = cv.blur(frame, entropy.blur_value)

        if entropy.offset.enabled is True:
            # 0,300,
            # x,
            left = frame[0:1080, 1920-c:1920].copy()
            right = frame[0:1080, 0:1920-c].copy()
            frame = cv.hconcat([left, right])
            c += 5
            if c > 1920:
                c = 0

        if entropy.mix.enabled is True:
            frame = cv.addWeighted(frame, entropy.blend_value[0], blend_frame, entropy.blend_value[1], entropy.blend_value[2])

        # final = cv.vconcat([frame, face2])
        # frame = cv.addWeighted(frame, 1, frame, 0.5, 2)

        # frame = cv.blur(frame, play.blur)
        # Create black canvas for each display
        # canvas = np.zeros((720, 1280, 3), np.uint8)
        # Apply the media image to canvas
        # canvas[:, :] = frame
        # Mix in some letters

        # Subtitles overlay
        if entropy.playing[0]['frame'] in entropy.sub:
            entropy.subtitle = entropy.sub[entropy.playing[0]['frame']]

        if entropy.subtitle is not None:
            f = entropy.font['subtitle']
            cv.putText(frame, entropy.subtitle, f.org, f.name, f.scale, f.color, f.thickness, f.type)

        # Status overlay
        f = entropy.font['status']
        cv.putText(frame, entropy.get_info('status'), f.org, f.name, f.scale, f.color, f.thickness, f.type)

        # Runtime overlay
        f = entropy.font['runtime']
        cv.putText(frame, entropy.get_info('runtime'), f.org, f.name, f.scale, f.color, f.thickness, f.type)

        # Mission time overlay
        f = entropy.font['mission']
        cv.putText(frame, entropy.get_info('mission'), f.org, f.name, f.scale, f.color, f.thickness, f.type)

        # Drawings
        for o, d in entropy.draw.items():
            if d.shape == 'rectangle':
                cv.rectangle(frame, d.pos1, d.pos2, d.color, d.thickness, d.type)

        try:
            cv.imshow("Entropy", frame)
            cv.moveWindow("Entropy", 0, 0)

        except Exception as entropy:
            print(entropy)
            exit(1)
    else:
        entropy.set_playhead(layer=0, category='feature', stream='entropy.mov')

    # cv.waitKey(0)
    # This actually controls the playback speed!
    if entropy.read_input(cv.waitKey(entropy.fps)) is False:
        # Method returns False for ESC key
        break

    # Prepare data for next frame processing
    entropy.update()


# Release everything
entropy.playing[0]['stream'].release()
try:
    entropy.playing[1]['stream'].release()
    entropy.playing[2]['stream'].release()
except KeyError: pass
cv.destroyAllWindows()
