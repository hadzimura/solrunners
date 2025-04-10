import cv2 as cv
import numpy as np
from scipy.interpolate import UnivariateSpline
from PIL import ImageFont, ImageDraw, Image

class Effect(object):

    def __init__(self, name):

        self.name = name
        self.enabled = False
        self.value = None

        match self.name:
            case 'blur':
                self.value = [1, 1]
            case 'offset':
                pass
            case 'mix':
                self.value = [0.5, 0.5, 0.5]
            case 'flip' | 'gray':
                # Plugin only supports enable/disable
                pass
            case _:
                # Unknown plugin
                pass

    @staticmethod
    def lookup_table(self, x, y):
        spline = UnivariateSpline(x, y)
        return spline(range(256))

    @staticmethod
    def summer(self, img):
        increaseLookupTable = self.lookup_table([0, 64, 128, 256], [0, 80, 160, 256])
        decreaseLookupTable = self.lookup_table([0, 64, 128, 256], [0, 50, 100, 256])
        blue_channel, green_channel, red_channel = cv.split(img)
        red_channel = cv.LUT(red_channel, increaseLookupTable).astype(np.uint8)
        blue_channel = cv.LUT(blue_channel, decreaseLookupTable).astype(np.uint8)
        sum = cv.merge((blue_channel, green_channel, red_channel))
        return sum


class Input(object):
    """ All the input actions consolidated """

    # Key code: name, alternate name, category
    volumes = {
        0: 'up',
        1: 'down',
        2: 'left',
        3: 'right',
        104: 'gamma-up',
        110: 'gamma-down'
    }

    #             102: ['f', 'flip'],
    #             103: ['g', 'gray'],
    #             109: ['m', 'mix'],
    #             104: ['h', 'gamma-up'],
    #             110: ['n', 'gamma-down'],
    #             111: ['b', 'blur'],
    #             112: ['p', 'blur'],
    #             114: ['r', 'reset']

    keys = {
        'macos': {
            0: 'up',
            1: 'down',
            2: 'left',
            3: 'right',
            9: 'tab',
            102: 'f',
            103: 'g',
            109: 'm',
            104: 'h',
            110: 'n',
            111: 'b',
            112: 'p',
            114: 'r'
        },
        'rpi': {
            0: 'up',
            1: 'down',
            2: 'left',
            3: 'right',
            9: 'tab',
            102: 'f',
            103: 'g',
            109: 'm',
            104: 'h',
            110: 'n',
            111: 'b',
            112: 'p',
            114: 'r'
        }
    }

    def __init__(self, system='macos'):

        self.k = self.keys[system]




class Control(object):
    elements = {
        'flip': False,
        'gray': False,
        'offset': False,
        'another': False
    }
    active = 0

    def __init__(self):
        pass

    def current(self):

        if self.active == len(self.elements.keys()) + 1:
            self.active = 0
        else:
            self.active += 1


class Draw(object):

    def __init__(self, shape, pos1, pos2, color, thickness):
        self.shape = shape
        self.pos1 = pos1
        self.pos2 = pos2
        self.color = color
        self.thickness = thickness
        self.type = cv.LINE_AA

    # cv.rectangle(frame, (x, y), (x+250, y+50), green, 4, cv.LINE_AA)

class Text(object):

    def __init__(self, coordinates):

        self.coordinates = coordinates
        self.font = ImageFont.truetype("/home/zero/solrunners/media/fonts/IBM_Logo_Regular_400.ttf", 50)
        self.numbers = ImageFont.truetype("/home/zero/solrunners/media/fonts/Mx437_EpsonMGA_Mono.ttf", 50)

    def source(self, data):
        self.data = data

    def write(self, frame, text):

        cv2_im_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im_rgb)
        draw = ImageDraw.Draw(pil_im)

        # Draw the text
        draw.text(self.coordinates, 'mission time', font=self.font, fill="#41FF00")
        draw.text((50, 100), str(text), font=self.numbers, fill="#41FF00")
        return np.array(pil_im)

class Font(object):

    def __init__(self, font_name=cv.FONT_HERSHEY_COMPLEX_SMALL, font_org=(50, 50), font_scale=1.5,
                 font_color=(255, 255, 0), font_thickness=2, font_type=cv.LINE_AA):
        self.name = font_name
        self.org = font_org
        self.scale = font_scale
        self.color = font_color
        self.thickness = font_thickness
        # FILLED, LINE_4, LINE_8, LINE_AA (AntiAliased)
        self.type = font_type

