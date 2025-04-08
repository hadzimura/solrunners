# Configuration of the runtime

from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from argparse import BooleanOptionalAction
from platform import system
from datetime import datetime as dt
from glob import glob
from os import environ
from pathlib import Path
from pprint import pprint
from random import choice
import requests
from ruamel.yaml import YAML

if system() != 'Darwin':
    from gpiozero import Button
    from gpiozero import DistanceSensor
    from gpiozero import LED
    from gpiozero import MotionSensor

import cv2 as cv
from modules.Controllers import Effect
from modules.Controllers import Font
from modules.Controllers import Draw


def arg_parser():
    # Parse the runtime arguments to decide 'who we are'
    parser = ArgumentParser(description='Sol Audio Runner',
                            epilog='Author: rkucera@gmail.com',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m', '--master',
                        action=BooleanOptionalAction,
                        default=False,
                        dest='master',
                        help='Master node?')
    parser.add_argument('-r', '--room',
                        default=None,
                        dest='room',
                        help='Which room is this Runner in?')

    return parser.parse_args()


class Configuration(object):

    def __init__(self, room=None, master=False, width=1920, height=1080, fps=25, fullscreen=True):

        if room is None:
            print('Room needs to be specified, exiting...')
            exit(1)
        else:
            self.room = int(room)

        self.node_type = 'slave'
        self.master = False
        if master is True:
            print('This is the Master Node')
            self.node_type = 'master'
            self.master = True
        else:
            print('This is Slave Node')

        # Running Environment locations
        env_var = environ
        self.project_root = Path(env_var['PWD'])
        self.media_root = self.project_root / Path('media')

        self.fonts = self.media_root / Path('fonts')
        self.fastapi_static = self.media_root / Path('static')
        self.fastapi_templates = self.media_root / Path('templates')

        self.audio_path = self.media_root / Path('audio')
        self.video_path = self.media_root / Path('video')
        self.entropy_audio = self.media_root / Path('audio/entropy')
        self.entropy_video = self.media_root / Path('video/entropy.mov')
        self.entropy_subtitles = self.media_root / Path('video/entropy.subtitles')
        self.entropy = False
        self.tate = False

        # Load RPi configurations
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.configuration_file = self.project_root / Path('sol.config.yaml')

        try:
            print("Loading configuration file: '{}'".format(self.configuration_file))
            self.configuration = dict(self.yaml.load(self.configuration_file))
            self.runners = self.configuration['runners'][self.room]
        except FileNotFoundError:
            print("Configuration file not found: {}".format(self.configuration_file))
            exit(1)

        # Initialize possible Sensors
        self.pinout = dict()
        self.media = dict()
        self.files = dict()
        self.authors = dict()
        self.mix_queues = dict()
        self.tracks = dict()
        self.audio_queue = dict()

        self.pir = None
        self.blue = None
        self.green = None
        self.button = None
        self.jitter_button = self.configuration['jitter']['button']
        self.jitter_presence = self.configuration['jitter']['presence']
        self.presence_delay = self.configuration['jitter']['presence_delay']
        self.pir_test = self.configuration['global']['pirTest']

        # Pinout definitions
        try:
            print('Loading pinout for room: {}'.format(self.room))
            if self.runners['pinout']['enabled'] is True:
                self._init_sensors(self.runners['pinout'])
        except KeyError as error:
            print("Configuration file does not contain a pinout section: {}".format(error))

        # Audio tracks metadata
        # tracks_metadata = self.project_root / Path('sol.audio.yaml')
        # try:
        #     print("Loading audio metadata: {}".format(tracks_metadata))
        #     all_tracks = self.yaml.load(tracks_metadata)
        #     for batch_name in all_tracks:
        #         if batch_name in self.instance['audio']:
        #             print("Initializing tracks for: '{}'".format(batch_name))
        #             self.tracks[batch_name] = dict(all_tracks[batch_name])
        #     # pprint(self.tracks, indent=2)
        # except KeyError as error:
        #     print("Audio not configured".format(tracks_metadata))
        # except FileNotFoundError:
        #     print("Audio metadata config file not found: '{}'".format(tracks_metadata))
        #     exit(1)

        heads_metadata = self.project_root / Path('sol.audio.heads.yaml')
        authors_metadata = self.project_root / Path('sol.authors.yaml')
        try:
            print("Loading audio heads metadata: {}".format(heads_metadata))
            self.tracks['heads'] = dict(self.yaml.load(heads_metadata))
            print("Loading authors metadata: {}".format(authors_metadata))
            authors = dict(self.yaml.load(authors_metadata))
            for head in self.tracks['heads']:
                a = self.tracks['heads'][head]['author']
                self.tracks['heads'][head]['fullname'] = authors[a]['name']
        except FileNotFoundError as e:
            print('Audio metadata config file not found')
            print(e)
            exit(1)

        # Total beats of the runtime
        self.beats = 0
        self.second = 0
        self.elapsed = 0

        # Video attributes definition
        self.fps = fps
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.x = 0
        self.y = 0

        # Video effects definitions
        self.blur = Effect('blur')
        self.mix = Effect('mix')
        self.offset = Effect('offset')

        # Video streams and functions definitions
        self.video = dict()
        self.videos = list()
        self.font = dict()
        self.draw = dict()

        self.playing = dict()

        if 'video' in self.runners:

            # Fonts
            self.font = {
                'subtitle': Font(font_org=(50, 800)),
                'status': Font(font_org=(50, 50)),
                'runtime': Font(font_org=(50, 1050)),
                'mission': Font(font_org=(1700, 1050))
            }
            # Drawings
            self.draw = {
                'mission': Draw(shape='rectangle',
                                pos1=(1680, 1015),
                                pos2=(1920, 1065),
                                color=(36, 204, 68),
                                thickness=3)
            }

            self._load_assets(self.runners['video'])

        # Subtitle acquisition is for both Audio / Video Nodes
        self.sub = dict()
        self.subtitle = None
        self._get_subtitles(self.entropy_subtitles)

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

        # Publish summary of the runtime
        self.summary = {
            'room': self.room,
            'node_type': self.node_type
        }

    def scheduler(self, play_time, track_id):
        self.audio_queue[play_time] = track_id

    def dispatcher(self):
        payload = {'play_time': dt.now(), 'track_id': 1}
        response = requests.post(url='http://127.0.0.1:8002/schedule', params=payload)

    def _get_subtitles(self, srt_file):

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

    def _load_assets(self, entities):
        for entity in entities:
            if '.' in entity:
                # These are singular video files
                self._get_file(entity)
            else:
                # These are folders of video files
                self._get_folder(entity)

    def _get_folder(self, folder_name):

        folder_path = self.video_path / Path(folder_name)
        print("Processing videos in folder: '{}'".format(folder_path))

        for filename in sorted(glob('{}/*.mp4'.format(folder_path))):

            try:
                video_name = filename.split('/')[-1]
                print("Importing video: '{}'".format(video_name))
                if folder_name not in self.video:
                    self.video[folder_name] = dict()

                self.video[folder_name][video_name] = dict()
                self.video[folder_name][video_name] = self._stream_metadata(cv.VideoCapture(filename), folder_name, video_name)

            except Exception as error:
                print('Problem acquiring video stream: {}'.format(filename))
                print(error)
                exit(1)

        self._reset_queue(folder_name, 'main')
        # self._reset_queue(folder_name, 'overlay')

    def _get_file(self, filename):
        """ Video streams """
        video_file = self.video_path / Path(filename)
        try:
            self.entropy = self._stream_metadata(cv.VideoCapture(str(video_file)), 'entropy', filename)
        except Exception as error:
            print('Problem acquiring video stream: {}'.format(video_file))
            print(error)
            exit(1)

    def _init_sensors(self, pinout):

        """ Initialize sensor peripherals """
        print('Initializing Sensors...')
        for input_name in pinout:

            if input_name == 'enabled':
                # Skip the 'enabled' key
                continue

            pin = pinout[input_name]

            if input_name == 'pir':
                print('Initializing PIR ({})'.format(pin))
                self.pir = MotionSensor(pin)
            elif input_name == 'blue':
                print('Initializing Blue LED ({})'.format(pin))
                self.blue = LED(pin)
            elif input_name == 'green':
                print('Initializing Green LED ({})'.format(pin))
                self.green = LED(pin)
            elif input_name == 'button':
                print('Initializing Button ({})'.format(pin))
                self.button = Button(pin)
        print('Done initializing Sensors')

    @staticmethod
    def _stream_metadata(stream, category, filename):
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

    def _reset_queue(self, category, q_name):
        if category not in self.mix_queues:
            self.mix_queues[category] = dict()
        self.mix_queues[category][q_name] = list(self.video[category].keys())

    def action(self):

        pass

    def get_info(self, resource):

        """ Get runtime information for various resources. Intended for text overlays. """

        result = str()
        if resource == 'status':

            result = '(b)lur: {} {} | (m)ix: {} {}'.format(
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
                self.mix.enabled = not self.mix.enabled
                print('Mix: {}'.format(self.mix.enabled))
            case 98:
                # 'b'
                self.blur.enabled = not self.blur.enabled
            case _:
                # if input_key in self.volumes:
                #     self.volume = self.volumes[input_key]
                # else:
                print("Undefined key pressed: '{}'".format(input_key))
        return True

    def set_playhead2(self, layer='main', category=None, stream=None, start_frame=0):

        """ Set playhead of Tate stream """

        if len(self.mix_queues[category][layer]) == 0:
            self._reset_queue(category, layer)
        stream = choice(self.mix_queues[category][layer])

        # Set stream into the layer
        self.playing[layer] = self.video[category][stream]
        self.playing[layer]['frame'] = start_frame
        self.playing[layer]['stream'].set(cv.CAP_PROP_POS_FRAMES, start_frame)
        self.playing[layer]['stream'].set(cv.CAP_PROP_FRAME_WIDTH, self.width)
        self.playing[layer]['stream'].set(cv.CAP_PROP_FRAME_HEIGHT, self.height)
        self.playing[layer]['stream'].set(cv.CAP_PROP_FPS, self.fps)

        # Remove latest stream from selector queue
        self.mix_queues[category][layer].remove(stream)
