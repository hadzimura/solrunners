# Configuration of the runtime

from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from argparse import BooleanOptionalAction
import cv2 as cv
from datetime import datetime as dt
from glob import glob
from os import environ
from pathlib import Path
from pprint import pprint
from os.path import isdir
from os.path import isfile
from random import choice
from ruamel.yaml import YAML, YAMLError
from platform import system

# Run pyglet in headless mode
import pyglet
pyglet.options['headless'] = True


def arg_parser():
    # Parse the runtime arguments to decide 'who we are'
    parser = ArgumentParser(description='Sol Audio Runner',
                            epilog='Author: rkucera@gmail.com',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--fullscreen',
                        action=BooleanOptionalAction,
                        default=False,
                        dest='fullscreen',
                        help='Play in fullscreen window')

    return parser.parse_args()

def wait_for_storage(location='/storage'):

    """ Wait for the SHM storage become available """

    if system() != "Darwin":
        print('Waiting for the SHM storage ({}) to be available...'.format(location))
        storage_available = False
        while storage_available is False:
            if isfile('{}/.ready'.format(location)):
                storage_available = True

    print('Storage available, starting runtime')
    return True

class Configuration(object):

    def __init__(self, fullscreen, runtime=None, fountain_version=1):

        if runtime is None:
            print('Need to select runtime from (entropy|heads|fountain), exiting...')
            exit(1)

        self.fullscreen = fullscreen

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
        self.entropy_path = self.media_root / Path('entropy')
        self.heads_path = self.media_root / Path('heads')
        self.fountain_path = self.media_root / Path('fountain')

        # Entropy
        self.entropy_main_audio = self.entropy_path / Path('entropy.wav')
        self.entropy_main_video = self.entropy_path / Path('entropy.mov')
        self.entropy_main_subtitles = self.entropy_path / Path('entropy.subtitles')
        self.entropy_countdown_video = self.entropy_path / Path('countdown.mov')
        self.entropy_countdown_audio = self.entropy_path / Path('countdown.wav')
        self.entropy_qr_code = self.entropy_path / Path('entropy_qr.png')

        # Heads
        self.heads_video = self.heads_path / Path('silent_heads.mov')
        self.heads_audio = self.heads_path / Path('silent_heads.wav')
        self.heads_subtitles = self.heads_path / Path('subs-1050x1680')
        self.heads_samples = self.heads_path / Path('talking/*.wav')
        self.heads_qr_code = self.heads_path / Path('heads_qr.png')

        # Fountain
        self.fountain = self.fountain_path / Path('fountain.wav')

        # Initialize YAM parser
        self.yaml = YAML()
        self.yaml.preserve_quotes = True

        # Entropy subtitles acquisition
        self.entropy_subs = dict()
        if runtime == 'entropy':
            self._get_entropy_subtitles()

        # Heads samples
        self.heads = dict()
        self.heads_overlays = dict()
        if runtime == 'heads':
            self._get_heads_data()
            self._get_heads_overlays()
            self.heads_overlays[0] = pyglet.media.StaticSource(pyglet.media.load(str(self.heads_audio),
                                                                              streaming=False))

    def _get_heads_data(self):

        """ Load the Heads samples metadata for runtime """

        heads_metadata = self.project_root / Path('sol.heads.yaml')
        authors_metadata = self.project_root / Path('sol.authors.yaml')
        quotes = dict()
        authors = dict()
        print('Importing HEADS metadata')
        try:
            print("Loading HEADS audio metadata from: {}".format(heads_metadata))
            quotes = dict(self.yaml.load(heads_metadata))
            print("Loading HEADS authors metadata from: {}".format(authors_metadata))
            authors = dict(self.yaml.load(authors_metadata))
        except FileNotFoundError as fnf:
            print('Not found HEADS metadata, exiting...')
            print(fnf)
            exit(1)
        except YAMLError as yamlerr:
            print('Problem parsing YAM file, exiting...')
            print(yamlerr)
            exit(1)
        except Exception as e:
            print('Problem exnountered, exiting...')
            print(e)
            exit(1)

        for sample, data in quotes.items():
            author = data['author']
            sub_id = data['id']
            if author not in self.heads:
                self.heads[author] = {
                    'name': authors[author]['name'],
                    'track': list()
                }
            self.heads[author]['track'].append(data)
        print('Done importing HEADS metadata')
        # pprint(self.heads, indent=4)

    def _get_heads_overlays(self):

        """ Load the Entropy subtitles for runtime """

        print('Importing HEADS overlays frames from: {}'.format(self.heads_subtitles))
        total_subs = 21
        for sub_id in range(1, total_subs + 1):
            self.heads_overlays[sub_id] = dict()
            sub_file = self.heads_subtitles / Path('{}.png'.format(sub_id))
            if isfile(sub_file):
                print("Importing: {}".format(sub_file))
                self.heads_overlays[sub_id]['sub'] = cv.imread(str(sub_file))
            else:
                print('Not found HEADS overlay frame: {}'.format(sub_id))
        print('Done importing HEADS overlay frames')

        print('Importing HEADS overlays samples from: {}'.format(self.heads_samples))
        sample_count = 0
        for sample_file in glob(str(self.heads_samples)):
            sub_id = int(sample_file.split('/')[-1].split('.')[0])
            sample_author = sample_file.split('/')[-1].split('.')[1]
            print('Importing: {}'.format(sample_file))
            if 'tracks' not in self.heads_overlays[sub_id]:
                self.heads_overlays[sub_id]['tracks'] = dict()
            self.heads_overlays[sub_id]['tracks'][sample_author] = pyglet.media.StaticSource(pyglet.media.load(sample_file, streaming=False))
            sample_count += 1
        print('Found {} HEADS overlay samples'.format(sample_count))
        print('Done importing HEADS overlays')
        # pprint(self.heads_overlays, indent=4)


    def _get_entropy_subtitles(self):

        """ Load the Entropy subtitles for runtime """

        print('Importing ENTRPY subtitles from: {}'.format(self.entropy_main_subtitles))
        with open(self.entropy_main_subtitles, 'r') as subtitles:

            for line in subtitles.read().splitlines():
                start_time = dt.strptime(line.split('|')[0], '%H:%M:%S:%f').time().replace(microsecond=0)
                stop_time = dt.strptime(line.split('|')[1], '%H:%M:%S:%f').time().replace(microsecond=0)
                stop_time.replace(second=stop_time.second)
                self.entropy_subs[start_time] = line.split('|')[2].strip()
                self.entropy_subs[stop_time] = None
        print('Done importing ENTROPY subtitles')
        pprint(self.entropy_subs, indent=4)


    def action(self):
        pass

    def update(self):
        pass

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

