#!/usr/bin/env python

from sys import exit
import time
import math
import numpy as np
import scrollphathd


fresh_buffer = np.zeros((scrollphathd.DISPLAY_WIDTH, scrollphathd.DISPLAY_HEIGHT))


def main():
    # Uncomment the below if your display is upside down
    # (e.g. if you're using it in a Pimoroni Scroll Bot)
    scrollphathd.rotate(degrees=180)

    # Dial down the brightness
    scrollphathd.set_brightness(0.2)

    #scrollphathd.write_string(" Static Border ", x=0, y=1, brightness=1.0)

    while True:
        scrollphathd.show(before_display=draw_plasma)
        scrollphathd.clear()
        time.sleep(0.05)


def draw_plasma(buf):
    i = 0
    s = math.sin(i / 50.0) * 2.0 + 6.0

    for x in range(scrollphathd.DISPLAY_WIDTH):
        for y in range(scrollphathd.DISPLAY_HEIGHT):
            v = 0.3 + (0.3 * math.sin((x * s) + i / 4.0) * math.cos((y * s) + i / 4.0))
            i += 2

            buf[x][y] = v
            scrollphathd.pixel(x, y, v)
    return buf

def draw_checkerboard(buf):
    # Buf is given as a two dimensional array of elements buf[x][y]
    # This method will draw a checkerboard pattern on the display.

    # for every column in the display width.
    for x in range(scrollphathd.DISPLAY_WIDTH):
        # For every row in the display height 
        for y in range(scrollphathd.DISPLAY_HEIGHT):

            # if the sum of the column and row is even, light up the pixel
            if (x + y) % 2 == 0:
                buf[x][y] = 1.0

    return buf

def draw_staticborder(buf):
    # Buf is given as a two dimensional array of elements buf[x][y]
    # This method will blink a frame of alternating lights around
    # our scrolling text twice a second.

    #for every column in the display width. If the column is even, light up the top and bottom pixel
    for x in range(scrollphathd.DISPLAY_WIDTH):
        buf[x][0] = 1.0
        buf[x][scrollphathd.DISPLAY_HEIGHT - 1] = 1.0

    #for every row in the display height. If the row is even, light up the leftmost and rightmost pixel
    for y in range(scrollphathd.DISPLAY_HEIGHT):
        buf[0][y] = 1.0
        buf[scrollphathd.DISPLAY_WIDTH - 1][y] = 1.0

    return buf


 