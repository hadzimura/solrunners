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
from os.path import isdir
from random import choice
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
    parser.add_argument('-m', '--master',
                        action=BooleanOptionalAction,
                        default=False,
                        dest='master',
                        help='Master node?')
    parser.add_argument('-r', '--room',
                        default=None,
                        dest='room',
                        help='Which room is this Runner in?')
    parser.add_argument('-f', '--fountain',
                        default=1,
                        dest='fountain_version',
                        help='Fountain version')

    return parser.parse_args()


class Configuration(object):

    def __init__(self, room=None, fountain_version=None):

        if room is None:
            print('No room specified, exiting')
            exit(1)

        self.room = int(room)
        if fountain_version is None:
            self.fountain_version = None
        else:
            self.fountain_version = int(fountain_version)

        # Running Environment locations
        env_var = environ
        self.project_root = Path(env_var['PWD'])

        if system() == 'Darwin' or not isdir('/storage'):
            self.media_root = self.project_root / Path('media')
        else:
            self.media_root = Path('/storage')

        # Path definitions
        self.fonts = self.media_root / Path('fonts')
        self.fastapi_static = self.media_root / Path('static')
        self.fastapi_templates = self.media_root / Path('templates')
        self.audio_path = self.media_root / Path('audio')
        self.video_path = self.media_root / Path('video')

        # Entropy
        self.entropy_audio = self.audio_path / Path('entropy/entropy.wav')
        self.entropy_video = self.video_path / Path('entropy/entropy.mov')
        self.entropy_countdown_video = self.video_path / Path('entropy/countdown.mov')
        # self.entropy_countdown_audio = self.video_path / Path('entropy/countdown.wav')
        self.entropy_stills = self.video_path / Path('entropy/stills')
        self.entropy_subtitles = self.video_path / Path('entropy/entropy.subtitles')

        # Silent Heads
        self.silent_heads_subtitles = self.video_path / Path('heads/silent_heads.subtitles')
        self.silent_heads_pix = self.video_path / Path('heads/subtitles')
        self.silent_heads_audio = self.audio_path / Path('heads/silent/silent_heads.wav')
        self.silent_heads_video = self.video_path / Path('heads/silent_heads.mov')
        # self.talking_heads = self.audio_path / Path('heads/talking/entropie-roman-multiple.wav')
        self.talking_heads = self.audio_path / Path('heads/talking/*.wav')
        self.fountain = self.audio_path / Path('fountain/fountain.wav')
        self.heads = dict()

        # Load RPi configurations
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.configuration_file = self.project_root / Path('sol.config.yaml')

        try:
            print("Loading configuration file: '{}'".format(self.configuration_file))
            self.configuration = dict(self.yaml.load(self.configuration_file))
            self.runner = self.configuration['runners'][self.room]
        except FileNotFoundError:
            print("Configuration file not found: {}".format(self.configuration_file))
            exit(1)

        # Initialize possible Sensors
        self.pinout = {'enabled': False}
        self.authors = dict()

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
            if self.runner['pinout']['enabled'] is True:
                self._init_sensors(self.runner['pinout'])
        except KeyError as error:
            print("Configuration file does not contain a pinout section: {}".format(error))

        # Subtitle acquisition is for both Audio / Video Nodes
        self.sub = dict()
        self.subtitle = None
        self._get_subtitles(self.entropy_subtitles)
        self._get_subtitles(self.silent_heads_subtitles)

        # Heads audio tracks metadata
        heads_metadata = self.project_root / Path('sol.audio.heads.yaml')
        authors_metadata = self.project_root / Path('sol.authors.yaml')
        try:
            print("Loading audio heads metadata: {}".format(heads_metadata))
            lines = dict(self.yaml.load(heads_metadata))
            print("Loading authors metadata: {}".format(authors_metadata))
            authors = dict(self.yaml.load(authors_metadata))

            for line in lines:
                author = lines[line]['author']
                lines[line]['name'] = line
                if author not in self.heads:
                    self.heads[author] = {
                        'name': authors[author]['name'],
                        'track': list()
                    }
                self.heads[author]['track'].append(lines[line])

            # Timeline
            self.heads['timeline'] = dict()
            for author, data  in authors.items():
                for window in data['window']:
                    print(window)
                    self.heads['timeline'][int(window)] = author

        except FileNotFoundError as e:
            print('Audio metadata config file not found')
            print(e)
            exit(1)
        pprint(self.heads, indent=4)

    def _get_subtitles(self,srt_file):

        """ Load the subtitles for runtime """

        try:
            # track = srt_file.split('.')[0]
            track = srt_file.stem
            if track not in self.sub:
                self.sub[track] = dict()

            print('Importing subtitles: {}'.format(srt_file))
            with open(srt_file, 'r') as subtitles:

                for line in subtitles.read().splitlines():
                    # start_time = dt.strptime(line.split('|')[0].removesuffix(':{}'.format(line.split('|')[0].split(':')[-1])), '%H:%M:%S').time()
                    # stop_time = dt.strptime(line.split('|')[1].removesuffix(':{}'.format(line.split('|')[1].split(':')[-1])), '%H:%M:%S').time()
                    start_time = dt.strptime(line.split('|')[0], '%H:%M:%S:%f').time().replace(microsecond=0)
                    stop_time = dt.strptime(line.split('|')[1], '%H:%M:%S:%f').time().replace(microsecond=0)
                    stop_time.replace(second=stop_time.second)
                    self.sub[track][start_time] = line.split('|')[2].strip()
                    self.sub[track][stop_time] = None
            print("Subtitles loaded: '{}'".format(srt_file))
            pprint(self.sub, indent=4)

        except Exception as e:
            print(e)

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

    def action(self):
        pass

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

