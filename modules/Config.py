# Configuration of the runtime

from datetime import datetime as dt
from os import environ
from pathlib import Path
from pprint import pprint
from ruamel.yaml import YAML

from modules.Sensors import Led
from modules.Sensors import Pir
from modules.Sensors import RedButton

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
        self.project_root = Path(env_var['PWD'])
        self.media_root = self.project_root / Path('media')
        self.fonts = self.media_root / Path('fonts')
        self.fastapi_static = self.media_root / Path('static')
        self.fastapi_templates = self.media_root / Path('templates')
        self.entropy_audio = self.media_root / Path('audio/entropy')
        self.entropy_video = self. media_root / Path('video/entropy')
        self.sol_sensors = self.project_root / Path('sol.config.yaml')

        # Load PINOUT configuration
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.pinout = dict()

        # Possible Sensors
        self.pir = None
        self.blue = None
        self.green = None
        self.button = None
        try:
            self.pinout = self.yaml.load(self.sol_sensors)
            pprint(self.pinout, indent=4)
            if self.room not in self.pinout:
                print("No PINOUT config found for Runners of Room '{}'".format(self.room))
            elif self.sol not in self.pinout[self.room]:
                print("No PINOUT config found for Runner of Room '{}': '{}'".format(self.room, self.sol))
            else:
                self._init_sensors(self.pinout[self.room][self.sol])
        except FileNotFoundError:
            print('PINOUT Config file not found: {}'.format('sol.config.yaml'))
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

    def _init_sensors(self, pinout):

        """ Initialize sensor peripherals """

        for input_name in pinout:

            if input_name == 'pir':
                self.pir = Pir(pinout[input_name])
            elif input_name == 'blue':
                self.blue = Led(pinout[input_name], input_name)
            elif input_name == 'green':
                self.blue = Led(pinout[input_name], input_name)
            elif input_name == 'button':
                self.button = RedButton(pinout[input_name])


