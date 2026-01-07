#!/usr/bin/env python

# Import IceCream for debugging (if available)
try:
    from icecream import ic
except ImportError:
    ic = lambda *a: a[0] if len(a) == 1 else a

# Fallback incase ic is not available.
if hasattr(ic, "configureOutput"):
    ic.configureOutput(
        prefix='[effects_engine] ',
        includeContext=True,
    )

class BaseEffect:
    def step(self) -> list[tuple[int,int,float]]:
        """
        Returns a list of (x, y, brightness) for the current frame.
        """
        raise NotImplementedError

    def is_done(self) -> bool:
        """Return True if the effect is finished, else False"""
        return False  # default: run forever

    def reset(self):
        """Reset internal state. Effects should be reusable."""
        pass

class LayeredEffect(BaseEffect):
    def __init__(self, *effects):
        self.effects = effects

    def step(self):
        pixels = {}

        for effect in self.effects:    
            for x, y, b in effect.step():
                pixels[(x,y)] = max(pixels.get((x,y), 0), b)
        
        return [(x,y,b) for (x,y), b in pixels.items()]


import math
from random import randint

class Sparkle(BaseEffect):
    """
    Represents one pixel that brightens then fades at a fixed or random speed.
    Returns normalized intensity for use with `scrollphathd.set_pixel()` and
    can be reset for reuse.

    If `speed` is None at construction, a random speed will be chosen at reset.
    """

    def __init__(self, x, y, speed: int | None = None):
        """
        Store pixel coordinates and speed, then initialize state via `reset()`.

        Args:
            speed: None to randomize each reset, or a positive int to fix cycle length.
        """
        self.x = x
        self.y = y
        self._fixed_speed = speed
        self.reset()

    def reset(self):
        """
        Reset sparkle to start a new cycle. If `speed` was zero, pick a new random speed.
        """
        self.step_count = randint(0, 50)
        self.speed = self._fixed_speed or randint(10, 50)
        self.max_steps = self.speed
        self.brightness = 1

    def step(self):
        """Advance the sparkle one step and return (x, y, normalized_brightness)."""
        t = self.step_count / self.max_steps

        brightness = math.sin(t * math.pi)  # smooth in/out

        self.step_count += 1

        if self.step_count > self.max_steps:
            self.reset()

        return [(self.x, self.y, brightness)]

    def is_done(self):
        # """Return True when the sparkle cycle finishes (brightness == 0)."""
        # return self.step_count > self.max_steps
        return False

import collections

class Comet(BaseEffect):
    def __init__(self, x, y, dx=1, dy=0, tail_length=6, bounce=True):
        self.dx = dx
        self.dy = dy
        self.tail = collections.deque(maxlen=tail_length)
        self.bounce = bounce
        self.start_x = float(x)
        self.start_y = float(y)
        self.max_distance = 100
        self.reset()

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.tail.clear()
        self.distance = 0.0

    def step(self):
        w, h = scrollphathd.width, scrollphathd.height
        nx = self.x + self.dx
        ny = self.y + self.dy

        if self.bounce:
            if nx < 0 or nx >= w:
                ic("X bounce", self.x, self.dx)
                self.dx *= -1
                nx = self.x + self.dx
            if ny < 0 or ny >= h:
                ic("Y bounce", self.y, self.dy)
                self.dy *= -1
                ny = self.y + self.dy
        else:
            nx %= w
            ny %= h

        self.x, self.y = nx, ny
        self.tail.appendleft((int(round(self.x)), int(round(self.y))))

        pixels = []
        for i, (cx, cy) in enumerate(self.tail):
            brightness = max(0.05, (1.0 - i / len(self.tail))**2)
            pixels.append((cx, cy, brightness))
        self.distance += math.hypot(self.dx, self.dy)
        return pixels

    def is_done(self):
        return self.distance > self.max_distance

class WaveRipple(BaseEffect):
    """
    Expanding circular ripple effect.

    A ripple originates from a point, expands outward, and fades over time.
    Each step returns a list of (x, y, brightness) tuples.
    """

    def __init__(self, cx, cy, speed=0.5, max_radius=None):
        """
        Args:
            cx, cy: Center of the ripple
            speed: How fast the ripple expands per frame
            max_radius: Optional cutoff radius (defaults to matrix diagonal)
        """
        self.cx = cx
        self.cy = cy
        self.speed = speed
        self._max_radius = max_radius
        self.reset()

    def reset(self):
        self.radius = 0.0
        self.done = False

        w, h = scrollphathd.width, scrollphathd.height

        self.max_radius = self._max_radius or math.hypot(w, h)

    def step(self):
        if self.done:
            return []

        pixels = []
        w, h = scrollphathd.width, scrollphathd.height

        for x in range(w):
            for y in range(h):
                dist = math.hypot(x - self.cx, y - self.cy)

                # thickness of the wave front
                delta = abs(dist - self.radius)

                if delta < 1.0:
                    # smooth bell-shaped brightness
                    brightness = math.cos(delta * math.pi / 2)
                    brightness *= max(0.0, 1.0 - round(self.radius) / round(self.max_radius))

                    if brightness > 0:
                        pixels.append((x, y, brightness))

        self.radius += self.speed

        if round(self.radius) > round(self.max_radius):
            ic("Ripple done",self.radius)
            self.done = True

        return pixels

    def is_done(self):
        return self.done

class ScannerSweep(BaseEffect):
    """
    Sweeping scanner / radar-style line with a fading trail.
    """

    def __init__(self, horizontal=True, speed=1, trail_length=5, bounce=True):
        """
        Args:
            horizontal: True for left→right sweep, False for top→bottom
            speed: Pixels per frame
            trail_length: Number of trailing pixels
            bounce: Reverse direction at edges
        """
        self.horizontal = horizontal
        self.speed = speed
        self.trail_length = trail_length
        self.bounce = bounce
        self._bounces = 0
        self.reset()

    def reset(self):
        self.pos = 0
        self.x_direction = 1
        self.trail = collections.deque(maxlen=self.trail_length)
        self.done = False

    def step(self):
        if self.done:
            return []

        w, h = scrollphathd.width, scrollphathd.height

        # move scanner
        self.pos += self.x_direction * self.speed

        limit = w - 1 if self.horizontal else h - 1

        if self.pos < 0 or self.pos > limit:
            if self.bounce:
                self.x_direction *= -1
                self.pos += self.x_direction * self.speed
                self._bounces += 1
            else:
                self.pos = 0
                self.done = True

        self.trail.appendleft(int(self.pos))

        pixels = []

        for i, p in enumerate(self.trail):
            brightness = max(0.05, (1.0 - i / self.trail_length) ** 2)

            if self.horizontal:
                for y in range(h):
                    pixels.append((p, y, brightness))
            else:
                for x in range(w):
                    pixels.append((x, p, brightness))

        return pixels

    def is_done(self):
        return self.done

class ZigZagSweep(BaseEffect):
    """
    Zig-zag sweeping effect with vertical bouncing.

    A single point sweeps left/right across a row, then moves up/down to the
    next row, reversing horizontal direction each time.
    """

    def __init__(self, speed=1, trail_length=6, bounce=True):
        self.speed = speed
        self.trail_length = trail_length
        self.bounce = bounce
        self.reset()

    def reset(self):
        self.w = scrollphathd.width
        self.h = scrollphathd.height

        self.row = 0
        self.col = 0
        self.x_direction = 1   # +1 → right, -1 → left
        self.y_direction = 1   # +1 → down, -1 → up

        self.trail = collections.deque(maxlen=self.trail_length)
        self.done = False

    def step(self):
        if self.done:
            return []

        pixels = []

        # Move horizontally
        self.col += self.x_direction * self.speed

        # Hit left/right edge?
        if self.col < 0 or self.col >= self.w:
            ic("row change", self.row, self.x_direction)
            # Clamp column
            self.col = max(0, min(self.w - 1, self.col))

            # Move vertically using y_direction
            self.row += self.y_direction

            # Reverse horizontal direction
            self.x_direction *= -1

            # Hit top/bottom?
            if self.row < 0 or self.row >= self.h:
                ic("Reverse vertical", self.row, self.y_direction)
                if self.bounce:
                    # Clamp row
                    self.row = max(0, min(self.h - 1, self.row))

                    # Reverse vertical direction
                    self.y_direction *= -1
                else:
                    self.done = True

        self.trail.appendleft((self.col, self.row))

        for i, (x, y) in enumerate(self.trail):
            brightness = max(0.05, (1.0 - i / self.trail_length) ** 2)
            pixels.append((x, y, brightness))

        return pixels

    def is_done(self):
        return self.done


import time
import scrollphathd

class EffectRunner:
    """
    Runs any BaseEffect on Scroll pHAT HD.
    """
    def __init__(self, effect: BaseEffect, fps: float = 20.0):

        self.effect = effect
        self.frame_delay = 1.0 / fps

    def run(self, repeat: int = 0):
        # How many times we've run the effect, how many 'Frames' if you will
        run_count = 0

        # Main loop
        while True:
            # clear buffer
            scrollphathd.clear()
            # get frame pixels from effect
            pixels = self.effect.step()

            # update pixels in buffer
            for x, y, b in pixels:
                scrollphathd.set_pixel(x, y, abs(b))

            # display buffer
            scrollphathd.show()

            # check if effect is done
            if self.effect.is_done():
                ic(type(self.effect).__name__, "completed")
                self.effect.reset()

            # handle repeat count
            if repeat > 0:
                run_count += 1
                if run_count > repeat:
                    break

            # wait for next frame
            time.sleep(self.frame_delay)


if __name__ == '__main__':
# Catches control-c and exits cleanly
    try:
        # Uncomment to turn off debugging
        # ic.disable()

        # Uncomment the below if your display is upside down
        scrollphathd.rotate(degrees=180)

        # Set max brightness
        scrollphathd.set_brightness(0.8)

        # This Works so Well!
        layered = LayeredEffect(
            Comet(0, 0, dx=1, dy=2, tail_length=4, bounce=True),
            Comet(16, 0, dx=2, dy=1, tail_length=9, bounce=True))
        runner = EffectRunner(layered, fps=25)
        runner.run(repeat=200)

        zigzag = ZigZagSweep(speed=1,trail_length=5,bounce=True)

        runner = EffectRunner(zigzag, fps=25)
        runner.run(repeat=400)

        scanner = ScannerSweep(horizontal=True,speed=1,trail_length=6,bounce=True)

        runner = EffectRunner(scanner, fps=20)
        runner.run(repeat=400)


        ripple = WaveRipple(8, 3, speed=0.7)

        runner = EffectRunner(ripple, fps=30)
        runner.run(repeat=200)

        sparkle = Sparkle(3, 4)
        comet = Comet(0, 0, dx=1, dy=1, tail_length=6)

        runner = EffectRunner(sparkle)
        runner.run(repeat=200)  # run sparkle

        runner = EffectRunner(comet)
        runner.run(repeat=200)
        pass

    except KeyboardInterrupt:
        scrollphathd.clear()
        scrollphathd.show()
        print("Exiting!")