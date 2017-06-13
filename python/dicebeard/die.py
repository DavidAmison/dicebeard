import os
from pathlib import Path

from PIL import Image
import pyconfig

import pydice


class ImageNotSupported(Exception):
    pass


class Die(pydice.dice.Die):
    """TODO this documentation!

    This class extends pydice's implementation of dice to include the ability
    to emit an Image.
    """

    def __init__(self, *args, **kwargs):
        super(Die, self).__init__(*args, **kwargs)
        if pyconfig.get('dicebeard.images_path'):
            self.images_path = Path(pyconfig.get('dicebeard.images_path'))
        else:
            self.images_path = Path(os.path.dirname(__file__)) / 'images'

    def to_image(self):
        """Emits a PIL.Image of the dice if possible."""
        if self.faces == range(1, 7):
            die_image_path = self.images_path / "d6/{}.png".format(self.result)
            image = Image.open(str(die_image_path))
            return image
        else:
            raise ImageNotSupported(
                "{} is not currently supported.".format(self.name))
