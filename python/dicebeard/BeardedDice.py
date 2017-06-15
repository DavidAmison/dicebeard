import pydice
import math
import os
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw


def roll(roll_expr):
    raw_roll = pydice.roll(roll_expr)
    return BeardedRoll(raw_roll)


class BeardedRoll():

    def __init__(self, roll):
        self.roll = roll
        self.images_path = Path(os.path.dirname(__file__)) / 'images'
        self._die_size = 125

    def to_image(self, scattered=False, dimen=(200, 200)):
        '''Returns the dicec roll as an image. If scattered is set to true
        the dice in the image will be randomly arranged within the image'''
        #TODO implement scattered and non-scattered

        #Maths to figure out how many rows and columns are needed
        no_of_dice = len(self.roll.dice)
        rows = math.ceil(math.sqrt(dimen[1]*no_of_dice/dimen[0]))
        cols = math.ceil(math.sqrt(dimen[0]*no_of_dice/dimen[0]))
        #Generate background image
        out_img = Image.new('RGBA', (10+rows*self._die_size, 10+cols*self._die_size))
        # TODO figure out what these numbers are
        x_co = 5
        y_co = 5
        for die in self.roll.dice:
            die_img = die.to_image()
            out_img.paste(die_img, (x_co, y_co), die_img)
            if (x_co+self._die_size) > (rows*self._die_size):
                x_co = 5
                y_co += self._die_size
            else:
                x_co += self._die_size
        out_img = out_img.resize(dimen,  Image.ANTIALIAS)
        # Return an Image, and process it elsewhere (since it may want to be
        # saved to file, or BytesIO, etc.)
        #
        # Also, it's less cognative load for the programmer, since it's
        # to_image() rather than to_image_then_bytesio()
        out_img = out_img.resize(dimen,  Image.ANTIALIAS)
        return out_img
