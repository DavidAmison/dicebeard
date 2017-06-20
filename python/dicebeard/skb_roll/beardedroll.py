import math
import random
import numpy as np

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

    def to_text(self, with_total=True):
        ret_str = "+".join(str(i.result) for i in self.dice)
        if self.total_mod < 0:
            ret_str += "+({})".format(self.total_mod)
        elif self.total_mod > 0:
            ret_str += "+(+{})".format(self.total_mod)

        if with_total:
            ret_str += " = {}".format(self.total)

        return ret_str

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
            box = (0, int(rows*self._die_size*2.5),
                   0, int(cols*self._die_size*2.5))
            points = self._rand_points_with_push(no_of_dice, box, 170)
            rotation = [random.randint(0, 360) for x in range(0, no_of_dice)]
            out_img = Image.new('RGBA',
                                (box[1], box[3]),
                                color=(30, 30, 30, 255))
        else:
            points = []
            for i in range(0, rows):
                for j in range(0, cols):
                    points.append((j*self._die_size+90, i*self._die_size+90))
            rotation = [0] * no_of_dice
            out_img = Image.new('RGBA',
                                (10+rows*self._die_size,
                                 10+cols*self._die_size),
                                 color=(30, 30, 30, 255))

        for i, die in enumerate(self.dice):
            die_img = die.to_image()
            die_img = die_img.convert('RGBA').rotate(
                rotation[i], resample=Image.BICUBIC, expand=True)
            corner = (int(points[i][0]-85), int(points[i][1]-85))
            out_img.paste(die_img, corner, die_img)

        return out_img.resize(dimen,  Image.ANTIALIAS)

    def _rand_points_with_push(self, n, box, sep):
        '''
        Generate a set of n random points within a box.

        Box should be a tuple containing the minimum and maximum co-ordinates
        desired in the form (xmin, xmax, ymin, ymax)
        '''

        # Generate the initial set of points
        x_coord = np.random.randint(box[0], box[1], (1, n)).astype(float)
        y_coord = np.random.randint(box[2], box[3], (1, n)).astype(float)

        return self._push_points(x_coord, y_coord, box, sep)

    def _push_points(self, x_coord, y_coord, box, sep):
        n = len(x_coord[0])
        force_const = sep * 2
        found_solution = False
        for foo in range(1, 1000):
            found_solution = True
            vel_x = np.zeros((n, n))
            vel_y = np.zeros((n, n))
            vel_walls = np.zeros((n, 4))

            one_array = np.ones((n, 1))
            X = (one_array * x_coord)
            Y = (one_array * y_coord)
            dX = X.T - X
            dY = Y.T - Y
            # Find the force between the points
            force_x = np.zeros((n, n))
            force_y = np.zeros((n, n))
            for i in range(0, n):
                for j in range(0, n):
                    D = math.sqrt(dX[i][j]*dX[i][j] + dY[i][j]*dY[i][j])
                    if D < sep and i != j:
                        found_solution = False
                    if i != j and D != 0:
                        force_x[i][j] = force_const*dX[i][j]/(D*D*D)
                        force_y[i][j] = force_const*dY[i][j]/(D*D*D)
                    elif i != j and D == 0:
                        force_x[i][j] = force_const

            # Find the new velocity (based on push from all other points)
            vel_x = vel_x + force_x
            vel_y = vel_y + force_y
            # Adjust the velocity based on push from the walls
            for i, vel_all in enumerate(vel_walls):
                for j, vel in enumerate(vel_all):
                    coord = x_coord[0][i] if j < 2 else y_coord[0][i]
                    D = coord - box[j]
                    if abs(D) < sep:
                        found_solution = False
                    vel_walls[i][j] += force_const*abs(D)/(D*D*D)

            # Check if the current points are a solution
            if found_solution:
                return np.append(x_coord, y_coord, axis=0).astype(int).T.tolist()

            # Move the points based on their current velocity
            for i in range(0, n):
                t = (box[1]+box[3]-box[0]-box[2])/15
                x_coord[0][i] += (sum(vel_x[i])+sum(vel_walls[i][:2]))*t
                y_coord[0][i] += (sum(vel_y[i])+sum(vel_walls[i][2:]))*t

                # If the dice is out of bounds centre it on that axis
                if x_coord[0][i] < box[0] or x_coord[0][i] > box[1]:
                    x_coord[0][i] = (box[0]+box[1])/2
                if y_coord[0][i] < box[2] or y_coord[0][i] > box[3]:
                    y_coord[0][i] = (box[2]+box[3])/2

        return np.append(x_coord, y_coord, axis=0).astype(int).T.tolist()
