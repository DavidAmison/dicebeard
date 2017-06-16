from timeit import default_timer


class AnswerTimer:
    """Times the code within the `with` block."""
    def __enter__(self):
        self.start_time = default_timer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = default_timer()
        self.total_time = self.end_time - self.start_time


class TrainResult:
    # TODO better docstring
    """Keeps results of a single training."""
    def __init__(self, r, guess, time):
        self.roll = r
        self.guess = guess
        self.time = time

    @property
    def correct(self):
        return self.roll.total == self.guess

    @property
    def too_high(self):
        return self.roll.total < self.guess

    @property
    def too_low(self):
        return self.roll.total > self.guess
