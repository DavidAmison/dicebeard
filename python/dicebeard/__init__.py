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


dice_faces = {
    1: "\u2680",
    2: "\u2681",
    3: "\u2682",
    4: "\u2683",
    5: "\u2684",
    6: "\u2685",
}



images = Path(os.path.dirname(__file__))


class DiceBeard(BeardChatHandler):

    __commands__ = [
        ("roll", 'roll',
         "Rolls dice. 0 arg: rolls 3d6. 1+ args: parses args and rolls."),
    ]

    __userhelp__ = """Rolls dice."""

    async def roll(self, msg):
        # Terrible to use an or here but.......I just did.
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
        
        #Testing image manipulation  
        d20 = images / 'images' / 'd20.png'
        output = images / 'images' / 'output.png'
        print(str(d20))
        img = Image.open(str(d20))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('arial.ttf', 72)
        draw.text((200,200),'72',(200,200,200), font = font)
        img.save(str(output))
        
        print(str(output))
        await self.sender.sendPhoto(open(str(output),'rb'))

        await self.sender.sendMessage("{}".format(text))
        
        
