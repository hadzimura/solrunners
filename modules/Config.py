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
    parser.add_argument('-r', '--recognition',
                        action=BooleanOptionalAction,
                        default=False,
                        dest='recognition',
                        help='Enable Face Recognition runtime')

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
            print('Need to select runtime from (entropy|heads), exiting...')
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

        # Base Path definitions
        self.entropy_path = self.media_root / Path('entropy')
        self.heads_path = self.media_root / Path('heads')

        # Video Color Effects
        self.color_effect = [
            cv.COLOR_BGR2GRAY,
            cv.COLORMAP_PLASMA,
            cv.COLORMAP_TWILIGHT,
            cv.COLORMAP_OCEAN,
            cv.COLORMAP_WINTER
        ]

        # text Fonts
        self.font = [
            cv.FONT_HERSHEY_SIMPLEX,
            cv.FONT_HERSHEY_PLAIN,
            cv.FONT_HERSHEY_TRIPLEX,
            cv.FONT_HERSHEY_COMPLEX,
            cv.FONT_HERSHEY_DUPLEX,
            cv.FONT_HERSHEY_COMPLEX_SMALL
        ]

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
        self.heads_subtitles = self.heads_path / Path('quotes')
        self.heads_samples = self.heads_path / Path('samples/*.wav')
        self.heads_qr_code = self.heads_path / Path('heads_qr.png')
        self.heads_metadata = self.project_root / Path('sol.heads.yaml')
        self.authors_metadata = self.project_root / Path('sol.authors.yaml')

        # Face Recognition models
        self.fr = self.media_root / Path('face_detections/haarcascade_frontalface_alt.xml')
        self.fre = self.media_root / Path('face_detections/haarcascade_eye_tree_eyeglasses.xml')
        self.frex = self.media_root / Path('face_detections/haarcascade_frontalcatface_extended.xml')
        self.lbp = self.media_root / Path('face_detections/lbpcascade_frontalface_improved.xml')

        # Initialize YAM parser
        self.yaml = YAML()
        self.yaml.preserve_quotes = True

        # Entropy initialization
        if runtime == 'entropy':
            self.entropy_subs = dict()
            self.entropy_expedition = 1
            # Entropy runtime text overlays
            self.entropy_overlays = {
                'countdown': ['PLEASE STAND BY', 'THE ENTROPY WILL LAND IN'],
                'intro': ['WE ARE SEARCHING', 'FOR ANYTHING', 'THAT IS LEFT'],
                'outro': ['WE ARE SEARCHING', 'FOR THE THINGS', 'THAT ARE STILL RIGHT']
            }
            self._get_entropy_subtitles()

        # Heads initialization
        if runtime == 'heads':
            self.heads_framecode = dict()
            self.heads_authors = dict()
            self.heads_overlays = {
                0: {
                    'author_name_long': 'Roman Neruda',
                    'author_name_short': 'roman',
                    'text': 'Podkresová audio stopa',
                    'subtitle': None,
                    'sample': [pyglet.media.StaticSource(pyglet.media.load(str(self.heads_audio), streaming=False))],
                    'sample_author': [['roman', 'Roman Neruda']]
                }
            }
            self._get_heads_data()
            self._get_heads_overlays()

    def _get_heads_data(self):

        """ Load the Heads samples metadata for runtime """
        quotes = dict()
        print('Importing HEADS metadata')
        try:
            print("Loading HEADS audio metadata from: {}".format(self.heads_metadata))
            quotes = dict(self.yaml.load(self.heads_metadata))
            print("Loading HEADS authors metadata from: {}".format(self.authors_metadata))
            self.heads_authors = dict(self.yaml.load(self.authors_metadata))
        except FileNotFoundError as fnf:
            print('Not found HEADS metadata, exiting...')
            print(fnf)
            exit(1)
        except YAMLError as yamlerr:
            print('Problem parsing YAM file, exiting...')
            print(yamlerr)
            exit(1)
        except Exception as e:
            print('Problem encountered, exiting...')
            print(e)
            exit(1)

        for sub_id, data in quotes.items():
            author = data['author']
            self.heads_overlays[int(sub_id)] = {
                'author_name_long': self.heads_authors[author]['name'],
                'author_name_short': data['author'],
                'text': data['text'],
                'placeholder': data['placeholder']
            }

            # Prepare TIMECODE for Silent Heada video
            for f_code in self.heads_authors[author]['position']:
                self.heads_framecode[f_code] = self.heads_authors[author]['sucher']
        print('Done importing HEADS metadata')

    def _get_heads_overlays(self):

        """ Load the Entropy subtitles for runtime """

        print('Importing HEADS overlays frames from: {}'.format(self.heads_subtitles))
        total_subs = 21
        for sub_id in range(1, total_subs + 1):
            sub_file = self.heads_subtitles / Path('{}.png'.format(sub_id))
            if isfile(sub_file):
                print("Importing: {}".format(sub_file))
                self.heads_overlays[sub_id]['subtitle'] = cv.imread(str(sub_file))
            else:
                print('Not found HEADS overlay frame: {}'.format(sub_id))
        print('Done importing HEADS overlay frames')

        print('Importing HEADS overlays samples from: {}'.format(self.heads_samples))
        sample_count = 0
        for sample_file in glob(str(self.heads_samples)):
            sub_id = int(sample_file.split('/')[-1].split('.')[0])
            sample_author = sample_file.split('/')[-1].split('.')[1]
            print('Importing: {}'.format(sample_file))
            if 'sample' not in self.heads_overlays[sub_id]:
                self.heads_overlays[sub_id]['sample'] = list()
                self.heads_overlays[sub_id]['sample_author'] = list()
            self.heads_overlays[sub_id]['sample'].append(pyglet.media.StaticSource(pyglet.media.load(sample_file, streaming=False)))
            self.heads_overlays[sub_id]['sample_author'].append([sample_author, self.heads_authors[sample_author]['name']])
            sample_count += 1
        print('Found {} HEADS overlay samples'.format(sample_count))
        print('Done importing HEADS overlays')

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
        # pprint(self.entropy_subs, indent=4)
