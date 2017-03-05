"""
@author: David Amison
"""
import dice
import random

from pathlib import Path
import re

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


class Dice:
    '''Class for implementing the python dice and producing images'''

    def __init__(self, images_folder, mode='pic'):
        self.images_path = Path(images_folder)
        self.mode = mode

    def roll_dice(self, input_string):
        '''Rolls the dice and produces output as defined in mode'''
        # Converts the string to a list of arguments
        input_args = input_string.split(" ")

        roll_out = []
        total = 0
        mod = 0
        # Arguments must be a list of strings of format 3d6+/-5 (any number is
        # fine)
        for arg in input_args:
            # remove any + or - then roll the dice
            arg_roll = re.findall(r'(\d*d\d+)', arg)
            for rolls in arg_roll:
                this_roll = dice.roll(rolls)
                roll_out.append(this_roll)
                total += sum(this_roll)

            # Extract the modifier and modify :D
            mod_temp = re.findall(r'([+-]\s*\d+)', arg)
            str_mod_temp = str(mod_temp).strip('\'[]\'')
            mod += int(str_mod_temp or '0')  # probably not a good idea...

        '''Check what kind of output the user wants and give it'''
        if self.mode == 'pic':
            # create and return the combined image
            try:
                out_img = self.mode_pic(roll_out, total+mod)
                final_img = self.images_path / ('final.png')
                out_img.save(str(final_img))
                return final_img
            except FileNotFoundError:
                return self.mode_txt(roll_out, total+mod, mod)
        elif self.mode == 'icon':
            return ''
        else:
            # convert the rolls into strings
            return self.mode_txt(roll_out, total+mod, mod)

    def dice_image_manip(self, sides, value):
        '''Generates an image of a dice with the printed number value. Returns the
        image'''
        dice_img = self.images_path / ('d'+str(sides) + '.png')

        # set the correct font size depending on dice
        font_sz = 20
        if int(sides) == 6:
            font_sz = 50

        # Open correct image and add the number
        img = Image.open(str(dice_img))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('arial.ttf', font_sz)
        # set x and y co-ordinates based on number
        W, H = img.size
        w, h = draw.textsize(str(value), font=font)
        x = (W-w)/2
        y = (H-h)/2

        draw.text((x, y), str(value),(255, 255, 255), font=font)

        # return the image
        return img

    def mode_pic(self, roll_out, total):
        '''Code for generating the large picture'''
        # First determine number of dice
        dice_rolled = 0
        for roll_list in roll_out:
            dice_rolled += len(roll_list)

        if dice_rolled < 3:
            out_img_size = [300, 150]
        elif dice_rolled < 5:
            # extra 50 for total
            out_img_size = [100*dice_rolled, 150]
        else:
            # extra 50 for total
            out_img_size = [500, 100*int((dice_rolled-1)/5)+150]

        # Create the image to be output
        out_img = Image.new('RGBA', out_img_size)

        # determine whether coins or dice and convert the rolls into pictures
        # based on input request and roll result

        x_offset = 0
        y_offset = 0
        for dice_roll in roll_out:
            rolls = dice_roll
            dice_sides = dice_roll.sides
            for rolled_num in rolls:
                output_img = self.dice_image_manip(dice_sides, rolled_num)
                out_img.paste(output_img, (x_offset, y_offset))
                x_offset += 100
                if x_offset > 400:
                    x_offset = 0
                    y_offset += 100

        # Add text giving the total roll to the bottom
        draw = ImageDraw.Draw(out_img)
        font = ImageFont.truetype('arial.ttf', 38)
        w, h = draw.textsize('TOTAL = '+str(total), font=font)
        draw.text(
            ((out_img_size[0]-w)/2, out_img_size[1]-50),
            'TOTAL = '+str(total),
            (0, 0, 0),
            font=font)

        return out_img

    def mode_txt(self, roll_out, total, mod):
        # convert the rolls into strings
        out_str = ''
        for out in roll_out:
            out_str = out_str + ('+'.join(map(str, out))) + '+'

        out_str = out_str+'['+str(mod)+']='+str(total)

        return out_str

    def flip_coin(self, n):
        '''Flip a coin n times'''
        results = []
        for i in range(0, n):
            flip = random.randomint(0, 1)
            # Heads is equivalent to 1, tails to 0
            if flip == 0:
                results.append('T')
            else:
                results.append('H')
