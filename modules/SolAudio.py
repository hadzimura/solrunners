# Configuration of the runtime

from copy import deepcopy
from datetime import datetime as dt
from glob import glob
from os import environ
from pathlib import Path
import platform
from pprint import pprint
from random import randint, choice
from ruamel.yaml import YAML

from modules.Config import Configuration

class SolAudioConfig(Configuration):
    pass
