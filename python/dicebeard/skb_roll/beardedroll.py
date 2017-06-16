import math
import random

import os
from pathlib import Path

from PIL import Image, ImageFont, ImageDraw

from .beardeddie import BeardedDie

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

    def to_text(self):
        ret_str = "+".join(str(i.result) for i in self.dice)
        if self.total_mod < 0:
            ret_str += "+({})".format(self.total_mod)
        elif self.total_mod > 0:
            ret_str += "+(+{})".format(self.total_mod)

        ret_str += " = {}".format(self.total)

        return ret_str

    def to_image(self, scattered=False, dimen=(200, 200)):
        '''
        Returns the dicec roll as an image.

        If scattered is set to true the dice in the image will be randomly
        arranged within the image
        '''
        no_of_dice = len(self.roll.dice)
        # Maths to figure out how many rows and columns are needed
        rows = math.ceil(math.sqrt(dimen[1]*no_of_dice/dimen[0]))
        cols = math.ceil(math.sqrt(dimen[0]*no_of_dice/dimen[0]))

        # Generates the array of points for where each dice will go (x,y,rotation)
        if scattered:
            box = (int(rows*self._die_size*2.5), int(cols*self._die_size*2.5))
            points = self._rand_points_with_push(no_of_dice, box, 180)
            out_img = Image.new('RGBA', box)
        else:
            points = []
            for i in range(0, rows):
                for j in range(0, cols):
                    points.append((j*self._die_size+5, i*self._die_size+5, 0))
            out_img = Image.new('RGBA',
                                (10+rows*self._die_size,
                                 10+cols*self._die_size))

        for i, die in enumerate(self.dice):
            die_img = die.to_image()
            die_img = die_img.convert('RGBA').rotate(
                points[i][2], resample=Image.BICUBIC, expand=True)
            corner = (int(points[i][0]-90),int(points[i][1]-90))
            out_img.paste(die_img, corner, die_img)

        return out_img.resize(dimen,  Image.ANTIALIAS)

    def _rand_points_with_push(self, n, box, spread):
        '''Generate n random points in a box seperated by a minimum distance'''
        # Genereate the initial set of points
        points = [[random.randint(0,box[0]-spread),
                   random.randint(0,box[1]-spread),
                   random.randint(0,360)] for x in range(0,n)]
        # Calculate the 'force' each point is experiencing
        while True:
            forces = [None]*n
            for i, point in enumerate(points):
                tot_fx = 0
                tot_fy = 0
                for repel in [x for j, x in enumerate(points) if j != i]:
                    # print(point,repel)
                    sep_x = point[0] - repel[0]
                    sep_y = point[1] - repel[1]
                    #T o account for occasional situation where points are on top of each other
                    sep_x += 5 if sep_x == 0 else 0
                    sep_y += 5 if sep_y == 0 else 0
                    dist_sq = sep_x*sep_x + sep_y*sep_y
                    tot_fx += math.ceil(5*spread*sep_x/dist_sq) if (dist_sq-spread*spread) < 0 else 0
                    tot_fy += math.ceil(5*spread*sep_y/dist_sq) if (dist_sq-spread*spread) < 0 else 0
                # Check distance to walls
                point[0] += 5 if point[0] == 0 else 0
                point[1] += 5 if point[1] == 0 else 0
                tot_fx += math.ceil(abs(15*spread/point[0])) if point[0] < spread/2 else 0
                tot_fx -= math.ceil(abs(15*spread/(point[0]-box[0]))) if point[0] > (box[0]-spread/2) else 0
                tot_fy += math.ceil(abs(15*spread/point[1])) if point[1] < spread/2 else 0
                tot_fy -= math.ceil(abs(15*spread/(point[1]-box[1]))) if point[1] > (box[1]-spread/2) else 0
                # Append to a list of forces
                forces[i] = [tot_fx, tot_fy]
            # If all forces are zero then we are good, else move the points and repeat
            if sum([f[0]+f[1] for f in forces]) == 0:
                print(points)
                return points
            else:
                # Move the points the distance denoted by forces
                for i in range(0,n):
                    points[i][0] += forces[i][0]
                    points[i][1] += forces[i][1]
