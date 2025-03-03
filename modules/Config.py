# Configuration of the runtime

from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from argparse import BooleanOptionalAction
from platform import system
from datetime import datetime as dt
from os import environ
from pathlib import Path
from pprint import pprint
from ruamel.yaml import YAML

if system() != 'Darwin':
    from gpiozero import Button
    from gpiozero import DistanceSensor
    from gpiozero import LED
    from gpiozero import MotionSensor


def arg_parser():
    # Parse the runtime arguments to decide 'who we are'
    parser = ArgumentParser(description='Sol Audio Runner',
                            epilog='Author: rkucera@gmail.com',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--audio',
                        action=BooleanOptionalAction,
                        default=False,
                        dest='audio',
                        help='Set node as audio runner')
    parser.add_argument('-m', '--master',
                        action=BooleanOptionalAction,
                        default=False,
                        dest='master',
                        help='Master node?')
    parser.add_argument('-r', '--room',
                        default=None,
                        dest='room',
                        help='Which room is this Runner in?')
    parser.add_argument('-s', '--sol',
                        default=None,
                        dest='sol',
                        choices=['audio', 'video'],
                        help='Which kind is this Runner of?')
    parser.add_argument('-v', '--video',
                        action=BooleanOptionalAction,
                        default=False,
                        dest='video',
                        help='Set node as video runner')

    return parser.parse_args()


class Configuration(object):

    def __init__(self, audio=False, video=False, room=None, master=False, width=1920, height=1080, fps=25, fullscreen=True):

        if audio is True and video is True:
            print('Only one of the types of the SoL Runner must be specified (--audio | --video)')
            print('Exiting...')
            exit(1)
        elif audio is False and video is False:
            print('At least one of the types of the SoL Runner must be specified (--audio | --video)')
            print('Exiting...')
            exit(1)
        elif audio is True:
            print('Running as the Audio Sol Runner')
            self.sol = 'audio'
        elif video is True:
            print('Running as the Video Sol Runner')
            self.sol = 'video'

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

        self.summary = {
            'sol': self.sol,
            'room': self.room,
            'node_type': self.node_type
        }

        # Running Environment location
        env_var = environ
        self.project_root = Path(env_var['PWD'])
        self.media_root = self.project_root / Path('media')

        self.fonts = self.media_root / Path('fonts')
        self.fastapi_static = self.media_root / Path('static')
        self.fastapi_templates = self.media_root / Path('templates')

        self.audio_path = self.media_root / Path('audio')
        self.entropy_audio = self.media_root / Path('audio/entropy')
        self.entropy_video = self.media_root / Path('video/entropy.mov')
        self.entropy_subtitles = self.media_root / Path('video/entropy.subtitles')
        self.entropy = None

        # Load RPi configurations
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.configuration_file = self.project_root / Path('sol.config.yaml')
        self.configuration = self.yaml.load(self.configuration_file)

        # Initialize possible Sensors
        self.pinout = self.configuration['pinout']
        self.pir = None
        self.blue = None
        self.green = None
        self.button = None
        self.jitter_button = self.configuration['jitter']['button']
        self.jitter_presence = self.configuration['jitter']['presence']
        self.presence_delay = self.configuration['jitter']['presence_delay']
        self.pir_test = self.configuration['global']['pirTest']

        try:
            pprint(self.pinout, indent=4)
            if self.room not in self.pinout:
                print("No PINOUT config found for Runners of Room '{}'".format(self.room))
            elif self.sol not in self.pinout[self.room]:
                print("No PINOUT config found for Runner of Room '{}': '{}'".format(self.room, self.sol))
            else:
                if system() != 'Darwin':
                    self._init_sensors(self.pinout[self.room][self.sol])
        except FileNotFoundError:
            print('PINOUT Config file not found: {}'.format('sol.config.yaml'))
            exit(1)

        self.tracks = dict()
        tracks_config = self.project_root / Path('sol.audio.yaml')
        try:
            self.tracks = self.yaml.load(tracks_config)
        except FileNotFoundError:
            print("Audio tracks config file not found: '{}'".format(tracks_config))
            exit(1)

        # Total beats of the runtime
        self.beats = 0
        self.second = 0
        self.elapsed = 0

        # Video definition
        self.fps = fps
        self.width = width
        self.height = height
        self.fullscreen = fullscreen

        # Subtitle acquisition is for both Audio / Video Nodes
        self.sub = dict()
        self.subtitle = None
        self._load_subtitles(self.entropy_subtitles)

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

    def _init_sensors(self, pinout):

        """ Initialize sensor peripherals """
        print('Initializing Sensors...')
        for input_name in pinout:
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
