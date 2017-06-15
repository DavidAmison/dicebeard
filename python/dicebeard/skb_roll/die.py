import os
from pathlib import Path

from PIL import Image
import pyconfig

import pydice


class ImageNotSupported(Exception):
    pass


class BeardedDie:

    def __init__(self, die):
        self.die = die
        # Time to strap our to_image to pydice's Die
        if pyconfig.get('dicebeard.images_path'):
            pydice.dice.Die.images_path = Path(pyconfig.get('dicebeard.images_path'))
        else:
            pydice.dice.Die.images_path = Path(os.path.dirname(__file__)) / 'images'

    def __getattr__(self,attr):
        return getattr(self.die, attr)

    def to_image(self):
        '''Emits a PIL.Image of the die is possible'''
        die_image_path = (self.images_path /
                          'd{}'.format(self.result.stop-1) /
                          '{}'.format(self.result))
        try:
            return Image.open(str(die_image_path))
        except FileNotFoundError:
            raise ImageNotSupported(
                    '{} is not currently supported.'.format(self.name))
