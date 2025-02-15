# Configuration of the runtime

from copy import deepcopy
from datetime import datetime as dt
from os import environ
from pathlib import Path
import platform


from glob import glob
from pprint import pprint
from random import randint, choice

from modules.Controllers import Effect
from modules.Controllers import Input
from modules.Controllers import Control
from modules.Controllers import Font
from modules.Controllers import Draw


# import numpy as np


class Configuration(object):

    def __init__(self, sol=None, room=None, master=False, width=1920, height=1080, fps=25, fullscreen=True):

        if sol is None:
            print('One of the types of the SoL Runner must be specified (audio / video)')
            print('Exiting...')
            exit(1)
        else:
            self.sol = sol

        if room is None:
            print('Room needs to be specified, exiting...')
            exit(1)
        else:
            self.room = room

        self.node_type = 'slave'
        self.master = False
        if master is True:
            print('This is the Master Node')
            self.node_type = 'master'
            self.master = True
        else:
            print('This is Slave Node')

        # Running Environment location
        env_var = environ
        self. project_root = Path(env_var['PWD'])
        self.media_root = self.project_root / Path('media')
        self.fonts = self.media_root / Path('fonts')
        self.fastapi_static = self.media_root / Path('static')
        self.fastapi_templates = self.media_root / Path('templates')
        self.entropy_audio = self.media_root / Path('audio/entropy')
        self.entropy_video = self. media_root / Path('video/entropy')

        # Total beats of the runtime
        self.beats = 0
        self.second = 0
        self.elapsed = 0

        # Video definition
        self.fps = fps
        self.width = width
        self.height = height
        self.fullscreen = fullscreen

        if sol == 'video':
            import cv2 as cv
            # Canvas definition
            self.frame_area = {'x': range(0, width), 'y': range(0, height)}
            self.x = 0
            self.y = 0

            # Effects states
            self.flip = Effect('flip')
            self.gray = Effect('gray')
            self.blur = Effect('blur')
            self.mix = Effect('mix')
            self.offset = Effect('offset')

            # Input handlers
            self.input = Input()
            self.control = Control()

            # Effect values
            self.offset_value = []
            self.blur_value = [1, 1]
            self.blend_value = [0, 0, 1]
            self.blur_control = {'left': 'x', 'right': 'x', 'up': 'y', 'down': 'y'}

            # Register runtimes
            self.control = str()
            self.effect = str()
            self.volume = None
            self.event = False

            # Video acquisition
            self.video = dict()
            self.video_seg = list()
            self._get_stream(folder='segments')
            self._get_stream(path='entropy.mov', category='feature')
            self.playing = {
                0: {'category': str(), 'name': str(), 'frame': int()},
                1: {'category': str(), 'name': str(), 'frame': int()},
                2: {'category': str(), 'name': str(), 'frame': int()}
            }
            # Subtitle fonts / per type
            self.font = {
                'subtitle': Font(font_org=(50,800)),
                'status': Font(font_org=(50,1000)),
                'runtime': Font(font_org=(50,1050)),
                'mission': Font(font_org=(1700,1050))
            }

            # Drawings
            self.draw = {
                'mission': Draw(shape='rectangle',
                                pos1=(1680, 1015),
                                pos2=(1920, 1065),
                                color=(36, 204, 68),
                                thickness=3)
            }


        # Subtitle acquisition is for both Audio / Video Nodes
        self.sub = dict()
        self.subtitle = None
        self._load_subtitles(self.entropy_video / Path('entropy.subtitles'))

        # Presence setup
        self.presence = {
            1: dict(),
            2: dict(),
            3: dict(),
            4: dict(),
            5: dict(),
        }
        if self.node_type is True:
            # TBD
            pass

    def _load_subtitles(self, srt_file):

        """ Load the subtitles for runtime """

        try:
            # track = srt_file.split('.')[0]
            track = srt_file.stem
            if track not in self.sub:
                self.sub[track] = dict()

            print('Importing subtitles: {}'.format(srt_file))
            with open(srt_file, 'r') as subtitles:

                for line in subtitles.read().splitlines():
                    start_time = dt.strptime(line.split('|')[0], '%H:%M:%S:%f').time()
                    stop_time = dt.strptime(line.split('|')[1], '%H:%M:%S:%f').time()
                    self.sub[track][start_time] = line.split('|')[2].strip()
                    self.sub[track][stop_time] = None
            print("Subtitles loaded: '{}'".format(srt_file))

        except FileNotFoundError as e:

            print('Subtitle file not found: {}'.format(srt_file))

    @staticmethod
    def _stream_metadata(stream, filename, category):
        """ Get metadata from stream"""
        metadata = dict()
        metadata['name'] = filename.split('.')[0]
        metadata['filename'] = filename
        metadata['category'] = category
        metadata['frames'] = int(stream.get(cv.CAP_PROP_FRAME_COUNT))
        metadata['fps'] = int(stream.get(cv.CAP_PROP_FPS))
        metadata['duration'] = round(metadata['frames'] / metadata['fps'])
        metadata['stream'] = stream
        return metadata

    def _get_stream(self, folder=None, path=None, category=None):

        """ Prepare and categorize all the video streams """

        if path is not None and category is not None:

            try:
                name = path
                if category not in self.video:
                    self.video[category] = dict()
                self.video[category][name] = dict()
                self.video[category][name] = self._stream_metadata(cv.VideoCapture(path), name, category)
            except Exception as error:
                print('Problem acquiring video stream: {}'.format(path))
                print(error)
                exit(1)

        elif folder is not None:

            try:
                for filename in glob('{}/*.mov'.format(folder)):
                    name = filename.split('/')[-1]
                    category = name.split('.')[0][0:len(name.split('.')[0]) - 3]

                    if category not in self.video:
                        self.video[category] = dict()

                    self.video[category][name] = dict()
                    self.video[category][name] = self._stream_metadata(cv.VideoCapture(filename), name, category)
                    if category not in self.video_seg:
                        self.video_seg.append(category)

            except Exception as error:
                print('Problem acquiring video stream: {}'.format(path))
                print(error)
                exit(1)

    def set_playhead(self, layer=0, category=None, stream=None, start_frame=0):

        """ Set playhead of stream """

        if stream is None and category is None:

            # Set category
            if self.playing[layer]['category'] is None:
                # Set random category
                category = choice(self.video_seg)
            else:
                # Set random category but different from the currently selected
                cats = self.video_seg
                cats.remove(self.playing[layer]['category'])
                category = choice(cats)
            # From selected category get random stream
            stream = choice(list(self.video[category].keys()))

        elif stream is None and category is not None:
            if self.playing[layer]['name'] is None:
                # Set random stream
                stream = choice(list(self.video[category].keys()))
            else:
                # Get random stream from the selected category but different from the currently selected
                pprint(self.playing[layer])
                streams = list(self.video[category].keys())
                streams.remove(self.playing[layer]['filename'])
                stream = choice(streams)

        # Set stream into the layer
        self.playing[layer] = self.video[category][stream]
        self.playing[layer]['frame'] = start_frame
        self.playing[layer]['stream'].set(cv.CAP_PROP_POS_FRAMES, start_frame)
        self.playing[layer]['stream'].set(cv.CAP_PROP_FRAME_WIDTH, self.width)
        self.playing[layer]['stream'].set(cv.CAP_PROP_FRAME_HEIGHT, self.height)
        self.playing[layer]['stream'].set(cv.CAP_PROP_FPS, self.fps)

    def get_info(self, resource):

        """ Get runtime information for various resources. Intended for text overlays. """

        result = str()
        if resource == 'status':

            result = '(g)ray: {} | (f)lip: {} | (b)lur: {} {} | (m)ix: {} {}'.format(
                int(self.gray.enabled),
                int(self.flip.enabled),
                int(self.blur.enabled),
                self.blur_value,
                int(self.mix.enabled),
                self.blend_value
            )

        elif resource == 'runtime':

            result = '{}: {} | {} frames | {} fps | duration: {}'.format(
                self.playing[0]['name'],
                self.playing[0]['category'],
                self.playing[0]['frames'],
                self.playing[0]['fps'],
                self.playing[0]['duration']
            )

        elif resource == 'mission':

            result = '{}f | {}s'.format(self.playing[0]['frame'], int(self.second))

        return result

    def update(self):

        # Accumulate runtime beats
        self.beats += 1

        # Update frame for each layer
        for layer in self.playing:
            if self.playing[layer]['frame'] is not None:
                self.playing[layer]['frame'] += 1

        # Total runtime seconds
        if (self.beats / self.fps).is_integer():
            self.second = self.beats / self.fps

        #25 fps = HH:MM:SS:
        # Divide 1,000 by the frame rate will give you milliseconds per frame..
        # 1000ms = 1 second
        self.elapsed = self.beats / self.fps
        self.action()

    def set_mix(self):
        self.mix = not self.mix
        if self.mix is True:
            self.set_playhead(layer=1, category='face')

    def action(self):

        """ Do stuff when an event received """
        if self.mix.enabled is True and self.volume is not None:

            # Get current setting
            value = 0.1
            if self.volume == 'up':
                self.blend_value[0] += value
            elif self.volume == 'down':
                self.blend_value[0] -= value
            elif self.volume == 'left':
                self.blend_value[1] -= value
            elif self.volume == 'right':
                self.blend_value[1] += value
            elif self.volume == 'gamma-up':
                self.blend_value[2] += value
            elif self.volume == 'gamma-down':
                self.blend_value[2] -= value
            print(self.blur_value)

        elif self.blur.enabled is True and self.volume is not None:

            # Get current setting
            # a = self._blur_mapping(self.blur_control[self.volume])

            bx = self.blur_value[0]
            by = self.blur_value[1]

            if bx == 1 or by == 1:
                value = 4
            else:
                value = 5

            # if self.volume == 'down':
            #     by =


            if self.volume == 'up':
                self.blur_value[0] += value
            elif self.volume == 'down':
                self.blur_value[0] -= value
            elif self.volume == 'left':
                self.blur_value[1] -= value
            elif self.volume == 'right':
                self.blur_value[1] += value
            print(self.blur_value)

    def read_input(self, input_key):

        match input_key:

            case -1:
                # Nothing pressed
                # zc.volume = None
                return True
            # case 9:
            #     # 'tab'
            #     self.control.active()
            case 27:
                # 'esc'
                return False
            case 102:
                # 'f'
                self.flip.enabled = not self.flip.enabled
            case 103:
                # 'g'
                self.gray.enabled = not self.gray.enabled
            case 111:
                # 'o'
                self.offset.enabled = not self.offset.enabled
            case 109:
                # 'm'
                self.set_mix()
            case 98:
                # 'b'
                self.blur.enabled = not self.blur.enabled
            case _:
                # if input_key in self.volumes:
                #     self.volume = self.volumes[input_key]
                # else:
                print("Undefined key pressed: '{}'".format(input_key))
        return True