"""
@author: David Amison
"""
import os
import random

from . import image_dice as dice
from . import image_coin as coin

import re
from timeit import default_timer

from pathlib import Path

import telepot
import telepot.aio
from telepot import glance
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from skybeard.beards import BeardChatHandler, ThatsNotMineException
from skybeard.decorators import onerror, getargsorask, getargs


class AnswerTimer:
    """Times the code within the `with` block."""
    def __enter__(self):
        self.start_time = default_timer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = default_timer()
        self.total_time = self.end_time - self.start_time


class DiceBeard(BeardChatHandler):

    __commands__ = [
        ('roll', 'roll',
         'Rolls dice. Parses args and rolls.'),
        ('train', 'train',
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
        # Objects controlling rolling dice and tossing coins
        self.my_dice = dice.Dice(self.images_path, self.font_path)
        self.my_coin = coin.Coin(self.images_path, self.font_path)

    _timeout = 90

    @onerror()
    @getargs()
    async def train(self, msg, no_of_dice=3):
        '''Game for training adding up dice.'''

        try:
            no_of_dice = int(no_of_dice)
        except ValueError:
            await self.sender.sendMessage("Sorry, '{}' is not an number.")
            return

        if no_of_dice > 10:
            await self.sender.sendMessage("Sorry, that's too many dice! Try a number under 10 ;).")
            return

        # TODO removed image use while we fix a bug with image processing.
        # i = no_of_dice
        # out, total = self.my_dice.train(i)
        # await self.sender.sendPhoto(out)
        # TODO replace this dice hacking with something better like pydice
        dice = [random.randint(1,6) for x in range(no_of_dice)]
        total = sum(dice)
        await self.sender.sendMessage(str(dice))

        with AnswerTimer() as timer:
            msg = await self.listener.wait()

        # Check if the answer is a number
        try:
            answer = int(msg['text'])
        except ValueError:
            await self.sender.sendMessage("That answer was not a number.")
            return
        except KeyError:
            await self.sender.sendMessage("Please answer with text based numbers.")
            return

        # Report back to the user about their answer
        if answer == total:
            await self.sender.sendMessage(
                '✅ Correct: {:.3}s'.format(timer.total_time))
        else:
            await self.sender.sendMessage(
                '❌ Wrong: {:.3}s'.format(timer.total_time))

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
