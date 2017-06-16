import pydice
from .beardedroll import BeardedRoll


def roll(roll_expr):
    raw_roll = pydice.roll(roll_expr)
    return BeardedRoll(raw_roll)
