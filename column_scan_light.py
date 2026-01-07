#!/usr/bin/env python

# for aborting from the program
from sys import exit
import time

# for ease of making nested for loops to represent the 2D Led matrix
import itertools

# different data structures
import collections

from random import shuffle, randint

# for handling array operations
import numpy as np

# for controlling the led matrix
import scrollphathd

# Uncomment the below if your display is upside down
# (e.g. if you're using it in a Pimoroni Scroll Bot)
scrollphathd.rotate(degrees=180)
scrollphathd.set_brightness(0.8)

class Sparkle:
    """
    Represents one pixel that brightens then fades at a fixed or random speed.
    Returns normalized intensity for use with `scrollphathd.set_pixel()` and
    can be reset for reuse.

    If `speed` is 0 at construction, a random speed will be chosen at reset.
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

class Comet:
    """A Comet moves across the matrix and leaves a tail whose pixels fade out progressively.
    
    Attributes:
        x (int): Current x position of the comet head.
        y (int): Current y position of the comet head.
        dx (int): Change in x position per step.
        dy (int): Change in y position per step.
        tail_length (int): Length of the comet's tail.
        bounce (bool): Whether the comet bounces off edges or wraps around.
    """

    def __init__(self, x:int, y:int, dx=1, dy=0, tail_length:int=6, bounce:bool=True):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.dx = dx
        self.dy = dy
        self.tail = collections.deque(maxlen=tail_length)
        self.bounce = bounce
        self._has_left_start = False
        self._bounces = 0


    def step(self):
        # advance head
        # compute new x,y position based off current x,yposition and velocity
        nx = self.x + self.dx
        ny = self.y + self.dy

        w, h = scrollphathd.width, scrollphathd.height

        # handle bouncing or wrapping
        if self.bounce:
            if nx < 0 or nx >= w:
                self.dx *= -1
                nx = self.x + self.dx
            if ny < 0 or ny >= h:
                self.dy *= -1
                ny = self.y + self.dy
                self._bounces += 1
        else:
            nx %= w
            ny %= h

        # update position
        self.x, self.y = nx, ny
        # add current position to tail
        self.tail.appendleft((self.x, self.y))

        # produce list of (x, y, brightness) with falloff
        pix_list = []

        # iterate over tail positions and assign brightness based on position in tail
        for i, (cx, cy) in enumerate(self.tail):

            # brightness falls off linearly from 1.0 to 0.05
            # brightness = max(0.05, 1.0 - (i / len(self.tail)))

            # Alternative: exponential falloff
            brightness = max(0.05, (1.0 - (i / len(self.tail)) ** 2))
                             
            pix_list.append((cx, cy, brightness))
        return pix_list
    
    def is_done(self):
        if not self._has_left_start:
            if (self.x, self.y) != (self.start_x, self.start_y):
                self._has_left_start = True
            return False
        if not self.bounce:
            return (self.x, self.y) == (self.start_x, self.start_y)

        return self._bounces >= 20

def comet_light(repeat=0):

    comet = Comet(0, 0, dx=1, dy=1, tail_length=6, bounce=True)

    run_count = 0
    while run_count <= repeat:
        scrollphathd.clear()
        for x, y, b in comet.step():
            scrollphathd.set_pixel(x, y, b)
        scrollphathd.show()
        if repeat > 0:
            run_count += 1
        if comet.is_done():
            break

#TODO Needs work doesnt do what i want
def sine_wave_light():
    """
    Create a sine wave pattern that moves across the display from left to right.
    Each column's brightness is determined by a sine function, creating a wave effect.
    """

    # amplitude = scrollphathd.height / 2
    # frequency = 0.3
    # offset = amplitude

    # while True:
    #     for phase in range(0, 360, 5):
    #         scrollphathd.clear()
    #         for col in range(scrollphathd.width):
    #             # Calculate the sine value for the current column
    #             radians = (phase + col * frequency) * (3.14159 / 180)
    #             sine_value = int((amplitude * (1 + np.sin(radians))) + offset)

    #             # Light up the pixel at the calculated row
    #             if 0 <= sine_value < scrollphathd.height:
    #                 scrollphathd.set_pixel(col, sine_value, 1.0)

    #         scrollphathd.show()
    #         time.sleep(0.05)

#TODO Needs work doesnt do what i want
def scan_trail_light(repeat=0):
    """
    Single moving LED with a trailing fade: travels top-to-bottom inside each column,
    processing columns left to right.

    Behavior:
      - Leading pixel is full brightness (1.0).
      - A trailing set of pixels is lit at decreasing brightness controlled by `trail_length`.
      - Calls `scrollphathd.show()` and sleeps briefly between steps.
      - Runs forever and updates the physical display.
    """
    trail_length = 4
    brightness_step = 1.0 / trail_length
    
    run_count = 0
    while run_count <= repeat:
        for col in range(scrollphathd.width):
            for row in range(scrollphathd.height):
                # light up the leading pixel
                scrollphathd.set_pixel(col, row, 1.0)

                # light up the trailing pixels with decreasing brightness
                for t in range(1, trail_length + 1):
                    if row - t >= 0:
                        scrollphathd.set_pixel(col, row - t, max(0.1, 1.0 - (brightness_step * t)))

                scrollphathd.show()
                time.sleep(0.05)
            scrollphathd.clear()
        if repeat > 0:
            run_count += 1

def sparkle_scan_light(repeat=0):
    """
    Run a single `Sparkle` at a time, scanning the display column by column,
    top-to-bottom. Each active sparkle brightens and then dims in place.
    """
    # create a list of Sparkle objects, one per pixel
    pixels = itertools.product(
        range(scrollphathd.width), range(scrollphathd.height)
    )
    sparkle_speed = 50
    sparkles = [Sparkle(x, y, sparkle_speed) for x, y in pixels]

    active = []
    run_count = 0
    while run_count <= repeat:
        # keep one active sparkle at a time
        if len(active) < 1:
            active.append(sparkles.pop(0))

        for sparkle in active:
            scrollphathd.set_pixel(*sparkle.step())

            if sparkle.is_done():
                active.remove(sparkle)
                sparkle.reset()
                # append back to pool
                sparkles.insert(len(sparkles), sparkle)
        scrollphathd.show()
        if repeat > 0:
            run_count += 1

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

def checker_fill_light(repeat=0):
    """
    Fill the matrix with a checkerboard pattern: pixels where (col+row) % 2 == 0
    are lit at 0.8 brightness. Repeats indefinitely.
    """
    pixels = itertools.product(
        range(scrollphathd.width), range(scrollphathd.height)
    )
    pix_list = list(pixels)

    run_count = 0
    while run_count <= repeat:
        scrollphathd.clear()
        for col, row in pix_list:
            if (col + row) % 2 == 0:
                scrollphathd.set_pixel(col, row, .8)
        scrollphathd.show()
        if repeat > 0:
            run_count += 1

def random_fill_light(repeat=0):
    """
    Light every LED in a random order each iteration. After the board is filled,
    the order is reshuffled and the process repeats.
    """
    pixels = itertools.product(
        range(scrollphathd.width), range(scrollphathd.height)
    )

    pix_list = list(pixels)

    run_count = 0
    while run_count <= repeat:
        scrollphathd.clear()
        shuffle(pix_list)
        for col, row in pix_list:
            scrollphathd.set_pixel(col, row, .8)
            scrollphathd.show()
        if repeat > 0:
            run_count += 1

def row_zigzag_fill_light(repeat=0):
    """
    Fill the matrix row-by-row, zig-zagging: one row left->right, next row right->left,
    continuing down the display to create a serpentine fill.
    """
    run_count = 0
    while run_count <= repeat:
        scrollphathd.clear()
        direction = 1  # 1 for left to right, -1 for right to left

        for row in range(scrollphathd.height):
            if direction == 1:
                for col in range(scrollphathd.width):
                    scrollphathd.set_pixel(col, row, .8)
                    scrollphathd.show()
                    if col == scrollphathd.width - 1:
                        direction = -1
            else:
                for col in reversed(range(scrollphathd.width)):
                    scrollphathd.set_pixel(col, row, .8)
                    scrollphathd.show()

                    if col == 0:
                        direction = 1
        if repeat > 0:
            run_count += 1

def row_zigzag_light(repeat=0):
    """
    Single moving LED that zig-zags across rows, left->right then right->left,
    clearing after each step (single dot motion).
    """
    run_count = 0
    while run_count <= repeat:
        direction = 1  # 1 for left to right, -1 for right to left

        for row in range(scrollphathd.height):
            if direction == 1:
                for col in range(scrollphathd.width):
                    scrollphathd.set_pixel(col, row, .8)
                    scrollphathd.show()
                    scrollphathd.clear()
                    if col == scrollphathd.width - 1:
                        direction = -1
            else:
                for col in reversed(range(scrollphathd.width)):
                    scrollphathd.set_pixel(col, row, .8)
                    scrollphathd.show()
                    scrollphathd.clear()
                    if col == 0:
                        direction = 1
        if repeat > 0:
            run_count += 1

def column_fill_light(repeat=0):
    """
    Turn on all LEDs, column by column, top-to-bottom, left-to-right.
    """
    run_count = 0
    while run_count <= repeat:
        scrollphathd.clear()
        for col in range(scrollphathd.width):
            for row in range(scrollphathd.height):
                scrollphathd.set_pixel(col, row, .8)
                scrollphathd.show()
        if repeat > 0:
            run_count += 1

def row_fill_light(repeat=0):
    """
    Turn on all LEDs, row by row, left-to-right across each row.
    """
    run_count = 0
    while run_count <= repeat:
        scrollphathd.clear()
        for row in range(scrollphathd.height):
            for col in range(scrollphathd.width):
                scrollphathd.set_pixel(col, row, .8)
                scrollphathd.show()
        if repeat > 0:
            run_count += 1

def column_sweep_light(repeat=0):
    """
    Single LED that sweeps top-to-bottom within each column (one dot at a time).
    """
    run_count = 0
    while run_count <= repeat:
        for col in range(scrollphathd.width):
            for row in range(scrollphathd.height):
                scrollphathd.set_pixel(col, row, .8)
                scrollphathd.show()
                scrollphathd.clear()
        if repeat > 0:
            run_count += 1

def row_sweep_light(repeat=0):
    """
    Single LED that sweeps left-to-right within each row (one dot at a time).
    """
    run_count = 0
    while run_count <= repeat:
        for row in range(scrollphathd.height):
            for col in range(scrollphathd.width):
                scrollphathd.set_pixel(col, row, .8)
                scrollphathd.show()
                scrollphathd.clear()
        if repeat > 0:
            run_count += 1

def main():
    comet_light()
    #scan_trail_light(0)
    # sparkle_scan_light(1)
    # sparkle_fill_light(1)
    # checker_fill_light(1)
    # random_fill_light(1)
    # column_fill_light(1)
    # row_fill_light(1)
    # row_zigzag_fill_light(1)
    # row_zigzag_light(1)
    # row_sweep_light(1)
    # column_sweep_light(1)
    pass


if __name__ == '__main__':
# Catches control-c and exits cleanly
    try:
        main()

    except KeyboardInterrupt:
        scrollphathd.clear()
        scrollphathd.show()
        print("Exiting!")