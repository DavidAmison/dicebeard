try:
    import pydice
except ImportError:
    print("WARNING: package missing for dicebeard.\n")
    print("Install custom pydice with:\n\n"
          "pip install git+git://github.com/nasfarley88/pydice.git")
    raise SystemExit

from copy import deepcopy
import io

import telepot
import telepot.aio
from telepot import glance
from telepot.namedtuple import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

from skybeard.beards import BeardChatHandler, ThatsNotMineException
from skybeard.bearddbtable import BeardDBTable, BeardInstanceDBTable
from skybeard.decorators import onerror, getargsorask, getargs
from skybeard.predicates import regex_predicate

from .skb_roll import roll, beardeddie
from .helper import TrainResult, AnswerTimer
from .utils import image_to_bytesio

import matplotlib.pyplot as plt

from multiprocessing import Pool

import asyncio

import logging

logger = logging.getLogger(__name__)


async def run_in_async_process(func, *args, **kwargs):
    """Run ordinary function truly async with processes.

    This function turns blocking ordinary functions (as opposed to coroutine
    functions) into awaitables that do not block the main thread.
    """
    with Pool(processes=1) as pool:
        result = pool.apply_async(func, args, kwargs)
        while True:
            if result.ready():
                return result.get()
            else:
                await asyncio.sleep(0.01)


class DiceBeard(BeardChatHandler):

    __commands__ = [
        ('roll', 'roll', 'Rolls dice. Parses args and rolls.'),
        ('rgurps', 'roll_gurps', 'Rolls 3d6, for GURPS!'),
        ('train', 'train', 'does some training'),
        ('trainmany', 'train_many', 'Trains dice roll <code>n</code> times.'),
        # TODO reinstate coins when imlemented
        # ('flip', 'flip_coin', 'Flips a number of coins and returns the result'),
        ('mode', 'choose_mode', ('Can change the output mode of the bot'
                                 ' between picture, icons and text')),
        ('history', 'show_results', 'prints contents of the database'),
        ('stats', 'show_stats', 'shows the users statistics'),
        ('wait', 'wait', 'Waits for 3 seconds without blocking.'),
        ('toggleautogurps', 'toggle_auto_gurps', 'Toggles automatic GURPS rolling.'),
    ]

    __userhelp__ = ('Can roll dice or flip coins.\n\n'
                    'To roll dice use the /roll command followed by any '
                    'number of arguments of the form 3d6+5 (can be + or -) '
                    'seperated by spaces. Currently, supported dice for '
                    'producing images are d4, d6, d8, d10, d12 and d20. To '
                    'flip coins simply type /flip followed by the number of '
                    'coins you would like to flip (e.g /flip 10 will filp 10 '
                    'coins)').strip()

    _timeout = 90

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text='Picture', callback_data=self.serialize('image')),
                 InlineKeyboardButton(
                     text='Text', callback_data=self.serialize('text'))],
            ])
        # Table for storing results of training
        self.train_table = BeardDBTable(self, 'train')

        self.settings_table = BeardInstanceDBTable(self, 'settings')
        if self.auto_gurps_roll_enabled:
            self.register_auto_gurps_command()

        # Can be 'text' or 'image'
        self.mode = 'image'

    def register_auto_gurps_command(self):
        self.register_command(
            regex_predicate(r'^-?\d+$'),
            self.auto_roll_gurps
        )

    @property
    def auto_gurps_roll_enabled(self):
        with self.settings_table as table:
            entries = [i for i in table.find(name='auto_gurps_roll_enabled')]
            if len(entries) > 1:
                # If there's more than one entry, there's been a problem. Drop
                # the table and remake.
                self.logger.warning("Too many entries found in settings table: {entries}".format(**locals()))
                table.drop()
                entries = []

        # If there's no entry, make one.
        if len([i for i in entries]) == 0:
            self.auto_gurps_roll_enabled = False

        with self.settings_table as table:
            entry = table.find_one(name='auto_gurps_roll_enabled')

        return entry['value']
        # return None

    @auto_gurps_roll_enabled.setter
    def auto_gurps_roll_enabled(self, value):
        assert isinstance(value, bool), "Toggle must be boolean."
        with self.settings_table as table:
            entry = table.find_one(name='auto_gurps_roll_enabled')
            if entry is not None:
                entry['value'] = value
                table.update(entry, ['id'])
            else:
                table.insert(dict(name='auto_gurps_roll_enabled', value=value))

            # Let's check the database
            entries = [i for i in table.find(name='auto_gurps_roll_enabled')]
            assert len(entries) == 1
            assert table.find_one(name='auto_gurps_roll_enabled')['value'] == value

        return value

    async def toggle_auto_gurps(self, msg):
        # This uses the database a lot. This might be a problem in the future.
        # If it is, cache it locally.
        if not self.auto_gurps_roll_enabled:
            self.register_auto_gurps_command()
            self.auto_gurps_roll_enabled = True
            await self.sender.sendMessage("Auto GURPS rolling enabled!")
        else:
            for command in self._instance_commands:
                # If command is regex predicate
                if command.toJSON()['predicate'].startswith('re.compile'):
                    self._instance_commands.remove(command)
                    self.auto_gurps_roll_enabled = False
                    await self.sender.sendMessage("Auto GURPS rolling disabled.")
                    break
            else:
                assert False, "Shouldn't get here."

    @onerror()
    @getargs()
    async def train_many(self, msg, no_of_times, no_of_dice=3):
        total_score = 0
        try:
            no_of_times = int(no_of_times)
        except ValueError:
            await self.sender.sendMessage(
                "I require an integer number of turns.")

        for i in range(int(no_of_times)):
            # Change message to be something more pallatable
            msg_edited = deepcopy(msg)
            msg_edited['text'] = "/train {}".format(no_of_dice)
            result = await self.train(msg_edited)
            if result.correct:
                total_score += result.time
            else:
                total_score += 10.

        assert isinstance(total_score, float)
        await self.sender.sendMessage(
                "Your total score is {:.3} for {} turns".format(
                    total_score, no_of_times))

    async def _create_personal_listener_from_msg(self, msg):
        my_listener = self.bot.create_listener()
        my_listener.capture([{'from': {'id': msg['from']['id']}},
                             {'chat': {'id': msg['chat']['id']}}])

        return my_listener

    @onerror()
    @getargs()
    async def train(self, msg, no_of_dice=3):
        '''Game for training adding up dice.'''
        try:
            no_of_dice = int(no_of_dice)
        except ValueError:
            await self.sender.sendMessage("Sorry, '{}' is not an number.".format(no_of_dice))
            return

        if no_of_dice > 10:
            await self.sender.sendMessage(
                "Sorry, that's too many dice! Try a number under 10.")
            return

        r = roll('{}d6'.format(no_of_dice))
        if self.mode == 'image':
            await self._send_roll(r, with_total=False, scattered=True)
            await self.sender.sendMessage(
                "What's the total?",
                reply_markup=ReplyKeyboardMarkup(keyboard=(
                    ('3', '4', '5', '6', '7', '8'),
                    ('8', '9', '10', '11', '12'),
                    ('13', '14', '15', '16', '17', '18'),
                ), one_time_keyboard=True))
        else:
            await self._send_roll(r, with_total=False)

        my_listener = await self._create_personal_listener_from_msg(msg)

        with AnswerTimer() as timer:
            msg = await my_listener.wait()

        # Check if the answer is a number
        try:
            answer = int(msg['text'])
        except ValueError:
            await self.sender.sendMessage("That answer was not a number.")
            return
        except KeyError:
            await self.sender.sendMessage(
                "Please answer with text based numbers.")
            return

        result = TrainResult(r, answer, timer.total_time)
        # Add the result to the database
        u_id = msg['from']['id']
        await self._add_result_to_table(result, u_id)

        # Report back to the user about their answer
        if result.correct:
            report_back_str = 'Correct: {:.3}s'.format(timer.total_time)
        else:
            report_back_str = 'Wrong: {:.3}s'.format(timer.total_time)

        await self.sender.sendMessage(
            report_back_str,
            reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        return result

    async def _send_roll(self, roll, *args, **kwargs):
        """Sends roll through telegram using preferred method."""

        try:
            if self.mode == "text":
                await self.sender.sendMessage(roll.to_text(*args, **kwargs))
            elif self.mode == "image":
                out_img = await run_in_async_process(
                    roll.to_image, *args, **kwargs)
                bytes_output = image_to_bytesio(out_img)

                await self.sender.sendPhoto(bytes_output)
            else:
                raise NotImplementedError(
                    "That mode is not implemented: {}".format(self.mode))
        except (NotImplementedError, beardeddie.ImageNotSupported):
            await self.sender.sendMessage("Mode not supported with this "
                                          "expression. Here's a text version: ")
            await self.sender.sendMessage(roll.to_text())

    @onerror()
    @getargsorask([('roll_expr', 'What dice do you want to roll?')])
    async def roll(self, msg, roll_expr):
        self.logger.debug(roll_expr)
        r = roll(roll_expr)
        await self._send_roll(r)

    @onerror()
    @getargs()
    async def roll_gurps(self, msg, roll_against=None):
        return await self._roll_gurps(msg, roll_against)

    @onerror()
    async def auto_roll_gurps(self, msg):
        roll_against = msg['text']
        return await self._roll_gurps(msg, roll_against)

    async def _roll_gurps(self, msg, roll_against=None):
        r = roll('3d6')
        logger.debug("Sending dice roll...")
        await self._send_roll(r, scattered=True)
        logger.debug("Sent dice roll.")
        logger.debug("Sending pass/fail...")
        if roll_against is not None:
            logger.debug("roll_against is not None!")
            roll_against = int(roll_against)
            if roll_against < 15 and r.total <= 4 or\
               roll_against == 15 and r.total <= 5 or\
               roll_against >= 16 and r.total <= 6:
                await self.sender.sendMessage("✅✅ Critical success!")
            elif (roll_against >= 16 and r.total == 18 or
                  roll_against <= 15 and r.total >= 17 or
                  r.total > roll_against+10):
                await self.sender.sendMessage("❌❌ Critical fail!")
            elif r.total <= roll_against:
                await self.sender.sendMessage("✅ Success!")
            else:
                await self.sender.sendMessage("❌ Fail!")

        logger.debug("Pass/fail should have been sent.")


    @onerror()
    @getargsorask([('input_args', 'How many coins do you want to flip?')])
    async def flip_coin(self, msg, input_args):
        raise NotImplementedError

    @onerror()
    async def choose_mode(self, msg):
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

        self.mode = data

    async def _add_result_to_table(self, result, u_id):
        '''Adds the result to the database'''
        dice = ','.join([str(die.faces.stop-1) for die in result.roll.dice])
        roll = ','.join([str(die.result) for die in result.roll.dice])
        time = result.time
        total = result.roll.total
        guess = result.guess
        correct = result.correct
        with self.train_table as table:
            table.insert(dict(
                    uid=u_id,
                    dice=dice,
                    roll=roll,
                    total=total,
                    guess=guess,
                    correct=correct,
                    time=time))

    async def show_results(self, msg):
        '''Print items in the database'''
        u_id = msg['from']['id']
        with self.train_table as table:
            matches = table.find(uid=u_id)
        items = [match for match in matches]

        await self.sender.sendMessage(
                '\n'.join(['[{}], {}, {}'.format(item['roll'], item['guess'], item['time']) for item in items[:10]]))

    async def show_stats(self, msg):
        '''Show all the statistics'''
        # Graph of roll total vs time
        u_id = msg['from']['id']
        with self.train_table as table:
            matches = table.find(uid=u_id)
        # Extracting only rolls of 3d6
        items = [match for match in matches if match['dice'] == '6,6,6']

        # Adding up all the time it took for the user to cound various values
        totals = [[0, 0] for i in range(1, 19)]
        for item in items:
            n = item['total']-1
            totals[n][0] += 1
            totals[n][1] += item['time']
        x = [i for i in range(1, 19)]
        y = [(x[1]/x[0] if x[0] != 0 else 0) for x in totals]
        plt.bar(x, y)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        await self.sender.sendPhoto(buf)

        # Comparison of different usuers
        with self.train_table as table:
            matches = table.find(dice='6,6,6')
        items = [match for match in matches]
        users = {}
        for item in items:
            u_id = item['uid']
            if u_id not in users:
                users[u_id] = [0, 0]
            users[u_id][0] += 1
            users[u_id][1] += item['time']

        totals = [users[u_id][1]/users[u_id][0] for u_id in users]
        for u_id in users:
            rtn = 'User: {}, Average time: {:.3}s'.format(u_id, users[u_id][1]/users[u_id][0])
            await self.sender.sendMessage(rtn)
