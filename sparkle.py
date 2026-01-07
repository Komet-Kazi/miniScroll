#!/usr/bin/env python

import itertools
import scrollphathd
from random import shuffle, randint

scrollphathd.set_brightness(0.9)
class Sparkle:
    """
    Represents one pixel that brightens then fades at a fixed or random speed.
    Returns normalized intensity for use with `scrollphathd.set_pixel()` and
    can be reset for reuse.

    If `speed` is None at construction, a random speed will be chosen at reset.
    """

    def __init__(self, x:int, y:int, speed: int | None = None):
        """
        Store pixel coordinates and speed, then initialize state via `reset()`.

        Args:
            speed: Noneto randomize each reset, or a positive int to fix cycle length.
        """
        self.x = x
        self.y = y
        self._fixed_speed = speed
        self.reset()

    def step(self):
        """
        Advance the sparkle one step and return (x, y, normalized_brightness).
        Behavior mirrors `Sparkle.step()`.
        """
        if self.brightness >= self.speed:
            self.direction = -1

        if self.brightness <= 0:
            self.direction = 0

        self.brightness += self.direction

        normalized_brightness = float(self.brightness)/self.speed

        return (self.x, self.y, normalized_brightness)

    def is_done(self):
        """Return True when the sparkle cycle finishes (brightness == 0)."""
        return self.brightness == 0

    def reset(self):
        """
        Reset sparkle to start a new cycle. If `speed` was zero, pick a new random speed.
        """
        self.brightness = 1
        self.direction = 1
        self.speed = self._fixed_speed if self._fixed_speed is not None else randint(2, 50)

def sparkle_fill_light(repeat=0):
    """
    Fill the matrix with sparkles by randomly selecting up to 100 active sparkles.
    Each sparkle can have a fixed or randomized speed (here fixed).
    """
    pixels = itertools.product(
        range(scrollphathd.width), range(scrollphathd.height)
    )

    # Fixed speed for all sparkles
    sparkle_speed = 50
    sparkles = [Sparkle(x, y, sparkle_speed) for x, y in pixels]

    active = []
    run_count = 0
    while run_count <= repeat:
        shuffle(sparkles)

        # maintain up to 100 active sparkles
        if len(active) < 100:
            active.append(sparkles.pop(0))

        for sparkle in active:
            scrollphathd.set_pixel(*sparkle.step())

            if sparkle.is_done():
                active.remove(sparkle)
                sparkle.reset()
                sparkles.insert(randint(0, len(sparkles)), sparkle)
        scrollphathd.show()
        if repeat > 0:
            run_count += 1

def main():
    sparkle_fill_light()
# Catches control-c and exits cleanly
try:
    main()

except KeyboardInterrupt:
    scrollphathd.clear()
    scrollphathd.show()
    print("Exiting")

# FIN!