import logging
import re
import os

#Based on the dice class
from . import image_dice as img_dice

from pathlib import Path

import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler
from skybeard.utils import get_args
#For handling the callback buttons part thing
from telepot import glance
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from skybeard.beards import BeardChatHandler, ThatsNotMineException

#logger = logging.getLogger(__name__)

class DiceBeard(BeardChatHandler):

    __commands__ = [
        ("roll", 'roll',
         "Rolls dice. 0 arg: rolls 3d6. 1+ args: parses args and rolls."),
        ("mode", 'mode',
         "Can change the output mode of the bot between picture, icons and text"),
    ]

    __userhelp__ = """Rolls dice."""
          
    images_path = Path(os.path.dirname(__file__)) / 'images'
    my_dice = img_dice.ImageDice(images_path)
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text='Picture', callback_data=self.serialize('Picture')),
                 InlineKeyboardButton(
                     text='Text', callback_data=self.serialize('Text'))],
                [InlineKeyboardButton(
                    text='Icons', callback_data=self.serialize('Icon'))],
            ])
    
    
    
    
    async def roll(self, msg):

        input_args = get_args(msg, return_string = True)        
        out_dice = self.my_dice.roll_dice(input_args)
        
        #Check which mode the user is in and output the correct format
        if self.my_dice.mode == 'pic':
            #Check a file path has been output, output picture if so and text otherwise
            if isinstance(out_dice, Path):
                await self.sender.sendPhoto(open(str(out_dice),'rb'))
            elif isinstance(out_dice, str):
                await self.sender.sendMessage(out_dice)
            else:
                await self.sender.sendMessage('Input was invalid')
        elif self.my_dice.mode == 'icon':
            await self.sender.sendMessage('Not yet formatted')
        else:
            await self.sender.sendMessage(out_dice)


    async def mode(self, msg):
        await self.sender.sendMessage('Please choose:',
                                      reply_markup=self.keyboard)

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')

        try:
            data = self.deserialize(query_data)
        except ThatsNotMineException:
            return

        await self.bot.editMessageText(
            telepot.origin_identifier(msg),
            text="Mode changed to: {}".format(data),
            reply_markup=self.keyboard)
               
        if data == 'Picture':
            self.my_dice.mode = 'pic'
        elif data == 'Text':
            self.my_dice.mode = 'txt'
        elif data == 'Icon':
            self.my_dice.mode = 'icon'
            

        

            
        
        
