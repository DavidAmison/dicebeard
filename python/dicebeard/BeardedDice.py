import pydice
import math
import os
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
import io


class BeardedDice():

    def __init__(self, roll_string):
        self.roll_string = roll_string
        self.roll_result = pydice.roll(roll_string)
        self._dice_rolled = len(self.roll_result.result['faces'])
        self.images_path = Path(os.path.dirname(__file__)) / 'images'
        self._die_size = 125

    def to_image(self, scattered=False, dimen=(200, 200)):
        '''Returns the dicec roll as an image. If scattered is set to true
        the dice in the image will be randomly arranged within the image'''
        #TODO implement scattered and non-scattered

        #Maths to figure out how many rows and columns are needed
        rows = math.ceil(math.sqrt(dimen[1]*self._dice_rolled/dimen[0]))
        cols = math.ceil(math.sqrt(dimen[0]*self._dice_rolled/dimen[0]))
        #Generate background image
        out_img = Image.new('RGBA', (10+rows*self._die_size, 10+cols*self._die_size))
        x_co = 5
        y_co = 5
        for die in self.roll_result.dice:
            face = die.faces.stop - 1
            roll = die.result
            img_path = self.images_path / 'd{}'.format(face) / '{}.png'.format(roll)
            die_img = Image.open(str(img_path))
            out_img.paste(die_img, (x_co, y_co), die_img)
            if (x_co+self._die_size) > (rows*self._die_size):
                x_co = 5
                y_co += self._die_size
            else:
                x_co += self._die_size
        out_img = out_img.resize(dimen,  Image.ANTIALIAS)
        bytes_out = io.BytesIO()
        out_img.save(bytes_out, format='PNG')
        bytes_out = bytes_out.getvalue()
        return bytes_out
