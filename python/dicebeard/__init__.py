import logging
import dice
import re
import os

from pathlib import Path

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler

logger = logging.getLogger(__name__)


def get_args(msg_text):
    return msg_text.split(" ")[1:]


def print_dice_img(self, sides, value):
    '''generated an image of a dice with the printed number value'''
    images = Path(os.path.dirname(__file__))
    num = int(value)
    
    dice_img = images / 'images' / ('d'+str(sides) + '.png')
    output_img = images / 'images' / 'output.png'
    
    #set x and y co-ordinates based on number
    if num < 10:
        x = 45
        y = 39
    else:
        x = 38
        y = 37
               
    #Printing of number on the dice 
    img = Image.open(str(dice_img))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('arial.ttf', 20)
    draw.text((x,y),str(num),(255,255,255), font = font)
    img.save(str(output_img))
    
    #return the file
    return output_img


dice_faces = {
    1: "\u2680",
    2: "\u2681",
    3: "\u2682",
    4: "\u2683",
    5: "\u2684",
    6: "\u2685",
}


class DiceBeard(BeardChatHandler):

    __commands__ = [
        ("roll", 'roll',
         "Rolls dice. 0 arg: rolls 3d6. 1+ args: parses args and rolls."),
    ]

    __userhelp__ = """Rolls dice."""
    

    async def roll(self, msg):
        # Terrible to use an or here but.......I just did.
        print('command recieved')
        roll_text = " ".join(get_args(msg['text'])) or "3d6"
        roll = dice.roll(roll_text)
        if re.match(r"^[0-9]+d6$", roll_text):
            text = "{} = {}".format(sum(roll),
                                    "".join(dice_faces[x] for x in roll))
        else:
            try:
                text = "{} = {}".format(sum(roll), roll)
            except TypeError:
                text = "{}".format(roll)
        
        await self.sender.sendMessage("{}".format(text))
        
        #Roll a d20 for good measure
        roll = dice.roll('1d20')
        output_img = print_dice_img(self, 20,roll)
        #Post the image to the screen
        await self.sender.sendPhoto(open(str(output_img),'rb'))
        
        

            
        
        
