import math
import numpy as np

import os
from pathlib import Path

from PIL import Image, ImageFont, ImageDraw

from .beardeddie import BeardedDie

from shapely.geometry import Polygon
from .random_points import random_shape_placement

class BeardedRoll():

    def __init__(self, roll):
        self.roll = roll
        self.images_path = Path(os.path.dirname(__file__)) / 'images'
        self._die_size = 125

    def __getattr__(self, attr):
        return getattr(self.roll, attr)

    @property
    def dice(self):
        return [BeardedDie(d) for d in self.roll.dice]

    def to_text(self, with_total=True):
        ret_str = "+".join(str(i.result) for i in self.dice)
        if self.total_mod < 0:
            ret_str += "+({})".format(self.total_mod)
        elif self.total_mod > 0:
            ret_str += "+(+{})".format(self.total_mod)

        if with_total:
            ret_str += " = {}".format(self.total)

        return ret_str

    def to_image_test(self):
        '''
        Generate an array of images with scattered dice to test various
        area ratios (i.e. area_of_dice:total_area)
        '''
        no_of_dice = len(self.roll.dice)
        rtn_img = Image.new('RGBA', (400, 800))
        rtn_corner = [0, 0]
        # Testing ratios 1:2.5, 1:3, 1:3.5, 1:4.0
        for i in [x/2 for x in range(9, 15)]:
            x_max = int(math.sqrt(i*no_of_dice)*125)
            y_max = int(math.sqrt(i*no_of_dice)*125)
            box = Polygon([(0, 0), (x_max, 0), (x_max, y_max), (0, y_max)])
            die_shape = Polygon([(0, 0), (125, 0), (125, 125), (0, 125)])
            points = random_shape_placement(no_of_dice, box, die_shape)
            # points = self._rand_points_with_push(no_of_dice, box, 170)
            print(points)
            # rotation = [random.randint(0, 360) for i in range(0, no_of_dice)]
            print(box.bounds)
            out_img = Image.new('RGBA',
                                (int(box.bounds[2]), int(box.bounds[3])),
                                color=(30, 30, 30, 255))

            for i, die in enumerate(self.dice):
                die_img = die.to_image()
                die_img = die_img.convert('RGBA').rotate(
                    points[i][2], resample=Image.BICUBIC, expand=True)
                width, height = die_img.size
                corner = (int(points[i][0]-width/2),
                          int(points[i][1]-height/2))
                out_img.paste(die_img, corner, die_img)

            out_img = out_img.resize((200, 200), Image.ANTIALIAS)
            rtn_img.paste(out_img, (rtn_corner[0], rtn_corner[1]))
            if rtn_corner[0] == 0:
                rtn_corner[0] = 200
            else:
                rtn_corner[0] = 0
                rtn_corner[1] += 200
        return rtn_img

    def to_image(self, scattered=False, dimen=(200, 200), with_total=False):
        '''
        Returns the dicec roll as an image.

        If scattered is set to true the dice in the image will be randomly
        arranged within the image
        '''

        # TODO implement totals in the image.
        #
        # When this has happened, change with_total to True.
        if with_total:
            raise NotImplementedError(
                "Totals are not currently supported in this mode.")

        no_of_dice = len(self.roll.dice)
        # Maths to figure out how many rows and columns are needed
        rows = math.ceil(math.sqrt(dimen[1]*no_of_dice/dimen[0]))
        cols = math.ceil(math.sqrt(dimen[0]*no_of_dice/dimen[0]))

        # Generates the array of points for where each dice will go (x,y)
        if scattered:
            x_max = int(math.sqrt(no_of_dice*5)*125)
            y_max = x_max
            box = Polygon([(0, 0), (x_max, 0), (x_max, y_max), (0, y_max)])
            die_shape = Polygon([(0, 0), (125, 0), (125, 125), (0, 125)])
            points = random_shape_placement(no_of_dice, box, die_shape)
            out_img = Image.new('RGBA',
                                (int(box.bounds[2]), int(box.bounds[3])),
                                color=(30, 30, 30, 255))
        else:
            points = []
            for i in range(0, rows):
                for j in range(0, cols):
                    points.append((j*self._die_size+62,
                                   i*self._die_size+62,
                                   0))
            out_img = Image.new('RGBA',
                                (10+rows*self._die_size,
                                 10+cols*self._die_size),
                                 color=(30, 30, 30, 255))

        for i, die in enumerate(self.dice):
            die_img = die.to_image()
            die_img = die_img.convert('RGBA').rotate(
                points[i][2], resample=Image.BICUBIC, expand=True)
            width, height = die_img.size
            corner = (int(points[i][0]-width/2),
                      int(points[i][1]-height/2))
            out_img.paste(die_img, corner, die_img)

        return out_img.resize(dimen,  Image.ANTIALIAS)
