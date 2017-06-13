"""
@author: David Amison
"""
import os

from . import image_dice as dice
from . import image_coin as coin

import re
from timeit import default_timer as timer

from pathlib import Path

import telepot
import telepot.aio
from telepot import glance
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from skybeard.utils import get_args
from skybeard.beards import BeardChatHandler, ThatsNotMineException
from skybeard.decorators import onerror, getargsorask


class DiceBeard(BeardChatHandler):

    __commands__ = [
        ('roll', 'roll',
         'Rolls dice. Parses args and rolls.'),
        ('train','train',
         'does some training'),
        ('flip', 'flip_coin',
         'Flips a number of coins and returns the result'),
        ('mode', 'mode',
         ('Can change the output mode of the bot'
          ' between picture, icons and text')),
    ]

    __userhelp__ = """Can roll dice or flip coins.

To roll dice use the /roll command followed by any number of arguments of the form 3d6+5 (can be + or -) seperated by spaces. Currently, supported dice for producing images are d4, d6, d8, d10, d12 and d20. To flip coins simply type /flip followed by the number of coins you would like to flip (e.g /flip 10 will filp 10 coins)

    """.strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text='Picture', callback_data=self.serialize('Picture')),
                 InlineKeyboardButton(
                     text='Text', callback_data=self.serialize('Text'))],
            ])

        # Directory where image files are stored
        self.images_path = Path(os.path.dirname(__file__)) / 'images'
        self.font_path = self.images_path/'FiraSans-Regular.otf'
        #Objects controllling rolling dice and tossing coins
        self.my_dice = dice.Dice(self.images_path, self.font_path)
        self.my_coin = coin.Coin(self.images_path, self.font_path)


    _timeout = 90

    @onerror()
    async def train(self,msg):
        #Outputs a BytesIO stream and the total value of the dice
        my_listener = self.bot.create_listener() 
        my_listener.capture([{'from':{'id':msg['from']['id']}}])
        
        input_args = get_args(msg)
        i = 0        
        try:
            i = int(input_args[0])
            i = 10 if i > 10 else i
        except Exception:
            i = 3
        out, total = self.my_dice.train(i) 
        await self.sender.sendPhoto(out)
        start = timer()
        msg = await my_listener.wait()
        end = timer()
        elapsed = round(end - start,2)
        answer = re.match(r'^\d+', msg['text'])
        if answer:
            if int(answer.group(0)) == total:
                await self.sender.sendMessage('Correct: '+str(elapsed)+'s')
            else:
                await self.sender.sendMessage('Wrong')
        else:
            await self.sender.sendMessage('Wrong')
        
        
        
    @onerror()
    @getargsorask([('input_args', 'What dice do you want to roll?')])
    async def roll(self, msg, input_args):
        # Roll the dice
        out_dice = self.my_dice.roll_dice(input_args)
        # Try and send picture, if fails then try and send as text
        try:
            await self.sender.sendPhoto(open(str(out_dice), 'rb'))
        except FileNotFoundError:
            await self.sender.sendMessage(out_dice)
            

    @onerror()
    @getargsorask([('input_args', 'How many coins do you want to flip?')])
    async def flip_coin(self, msg, input_args):

        out_coin = self.my_coin.flip_coin(input_args)

        # Check which mode the user is in and output the correct format. Try
        # and send picture, if fails then try and send as text
        try:
            await self.sender.sendPhoto(out_coin.open('rb'))
        except AttributeError:
            await self.sender.sendMessage(out_coin)

    @onerror()
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
            self.my_coin.mode = 'pic'
        elif data == 'Text':
            self.my_dice.mode = 'txt'
            self.my_coin.mode = 'txt'