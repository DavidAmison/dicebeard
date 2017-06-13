import os
from pathlib import Path

from PIL import Image
import pyconfig

import pydice


class ImageNotSupported(Exception):
    pass


# Time to strap our to_image to pydice's Die
if pyconfig.get('dicebeard.images_path'):
    pydice.dice.Die.images_path = Path(pyconfig.get('dicebeard.images_path'))
else:
    pydice.dice.Die.images_path = Path(os.path.dirname(__file__)) / 'images'


def _to_image(self):
    """Emits a PIL.Image of the dice if possible."""
    if self.faces == range(1, 7):
        die_image_path = self.images_path / "d6/{}.png".format(self.result)
        image = Image.open(str(die_image_path))
        return image
    else:
        raise ImageNotSupported(
            "{} is not currently supported.".format(self.name))


pydice.dice.Die.to_image = _to_image
