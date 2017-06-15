import pydice

import math
import random

import os
from pathlib import Path

from PIL import Image, ImageFont, ImageDraw


class BeardedRoll():

    def __init__(self, roll):
        self.roll = roll
        self.images_path = Path(os.path.dirname(__file__)) / 'images'
        self._die_size = 125

    def to_image(self, scattered=False, dimen=(200, 200)):
        '''Returns the dicec roll as an image. If scattered is set to true
        the dice in the image will be randomly arranged within the image'''
        no_of_dice = len(self.roll.dice)
        #Maths to figure out how many rows and columns are needed        
        rows = math.ceil(math.sqrt(dimen[1]*no_of_dice/dimen[0]))
        cols = math.ceil(math.sqrt(dimen[0]*no_of_dice/dimen[0]))
        
        #Generates the array of points for where each dice will go (x,y,rotation)
        if scattered:             
            box = (int(rows*self._die_size*2.5),int(cols*self._die_size*2.5))
            points = self._rand_points(no_of_dice,box,180)
            out_img = Image.new('RGBA', box)
        else: 
            points = []
            for i in range(0,rows):
                for j in range(0,cols):
                    points.append((j*self._die_size+5,i*self._die_size+5,0))
            out_img = Image.new('RGBA', (10+rows*self._die_size, 10+cols*self._die_size))
                     
        for i, die in enumerate(self.roll.dice):
            die_img = die.to_image()
            die_img = die_img.convert('RGBA').rotate(
                points[i][2], resample=Image.BICUBIC, expand=True)
            out_img.paste(die_img, (points[i][0],points[i][1]), die_img)
                
        return out_img.resize(dimen,  Image.ANTIALIAS)
    
    
    def _rand_points(self, n, box, border=0):
            '''Returns co-ordinates for n points within the 'box' area.'''
            points = []
            for i in range(0,n):
                accepted = False
                while accepted == False:
                    x_y_r = [random.randint(0,box[0]-border),
                             random.randint(0,box[1]-border),
                             random.randint(0,360)]
                    accepted = True
                    for point in points:
                        if (abs(x_y_r[0]-point[0]) <= border) and (abs(x_y_r[1]-point[1]) <= border):
                            accepted = False
                #print('point found: {}'.format(x_y_r))
                points.append(x_y_r)
            return points
    
    