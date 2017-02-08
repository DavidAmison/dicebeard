import logging
import dice
import re
import os

from pathlib import Path

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from . import img_manip

import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler

logger = logging.getLogger(__name__)


def get_args(msg_text):
    return msg_text.split(" ")[1:]





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
        
        images = Path(os.path.dirname(__file__))
        final_img = images / 'images' / 'final.png'     
        
        # Terrible to use an or here but.......I just did.
        print('command recieved')
        roll_text = get_args(msg['text'])
        
        if len(roll_text) == 0:
            roll_text.append('3d6')
        
        #Loop through all the user dice inputs and roll them :D
        roll_out = []
        for dice_input in roll_text:
            app_text = dice.roll(dice_input)
            roll_out.append(app_text)
        
        
       
        #if re.match(r"^[0-9]+d6$", roll_text):
        #    text = "{} = {}".format(sum(roll),
        #                            "".join(dice_faces[x] for x in roll))
        #else:
        #    try:
        #        text = "{} = {}".format(sum(roll), roll)
        #    except TypeError:
        #        text = "{}".format(roll)
        #
        #await self.sender.sendMessage("{}".format(text))
        
        dice_rolled = 0
        for roll_list in roll_out:
            dice_rolled += len(roll_list)
            
        if dice_rolled < 5:
            out_img_size = [500,100]
        else:
            out_img_size = [500,100*int((dice_rolled-1)/5)+100]
    

        #out_img_size = [100*len(roll_out),100]
        out_img = Image.new('RGBA', out_img_size)
        
        #convert the rolls into pictures based on input request and roll result
        total = 0
        x_offset = 0
        y_offset = 0
        for dice_roll in roll_out:
            rolls = dice_roll
            total += sum(rolls)
            dice_sides = dice_roll.sides
            for rolled_num in rolls:
                output_img = img_manip.create_dice_img(self,dice_sides,rolled_num)
                out_img.paste(Image.open(str(output_img)),(x_offset,y_offset)) 
                x_offset += 100
                if x_offset > 400:
                    x_offset = 0
                    y_offset += 100
        
        out_img.save(str(final_img))
        await self.sender.sendPhoto(open(str(final_img),'rb'))        
        
        await self.sender.sendMessage('The total is ' + str(total))    
            
        
        #input_dice = re.findall(r'(d\d+)',roll_text)
        #print('dice rolled: ' + str(input_dice))
        
        #Roll another die for good measure
        #roll = dice.roll('1d6')
        #output_img = img_manip.create_dice_img(self,6,roll)
        #Post the image to the screen
        #await self.sender.sendPhoto(open(str(output_img),'rb'))

        

            
        
        
