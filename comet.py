#!/usr/bin/env python

# for aborting from the program
from sys import exit

import collections
import time

# for controlling the led matrix
import scrollphathd

# Uncomment the below if your display is upside down
# (e.g. if you're using it in a Pimoroni Scroll Bot)
scrollphathd.rotate(degrees=180)
scrollphathd.set_brightness(0.108)

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
        self.dx = dx
        self.dy = dy
        self.tail = collections.deque(maxlen=tail_length)
        self.bounce = bounce

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
            brightness = max(0.05, 1.0 - (i / len(self.tail)))
                             
            pix_list.append((cx, cy, brightness))
        return pix_list
    
def comet_light(repeat=0):

    comet = Comet(0, 0, dx=1, dy=1, tail_length=6, bounce=True)

    run_count = 0
    while run_count <= repeat:
        scrollphathd.clear()

        for x, y, b in comet.step():
            scrollphathd.set_pixel(x, y, b)
        scrollphathd.show()
        time.sleep(0.07)
        if repeat > 0:
            run_count += 1

if __name__ == '__main__':
# Catches control-c and exits cleanly
    try:
        comet_light()

    except KeyboardInterrupt:
        scrollphathd.clear()
        scrollphathd.show()
        print("Exiting!")