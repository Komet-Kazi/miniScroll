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

###------------------------------------------------------------------------------###
# Helper Functions

def clamp01(v: float) -> float:
    """
    Clamp and normalize a value to the range [0.0, 1.0].

    Any negative input is converted to positive using abs().
    Values greater than 1.0 are clamped to 1.0.

    This is used to ensure LED brightness values are always valid
    before being sent to the display hardware.
    """
    return max(0.0, min(1.0, abs(v)))

###----------------------
from enum import Enum

class BlendMode(Enum):
    MAX = "max"
    ADD = "add"
    ALPHA_SOFT = "alpha_soft"
    ALPHA_HARD = "alpha_hard"
    OVERWRITE = "overwrite"

def blend(dst: float, src: float, mode: BlendMode) -> float:
    if mode == BlendMode.MAX:
        return max(dst, src)
    if mode == BlendMode.ADD:
        return dst + src
    if mode == BlendMode.ALPHA_SOFT:
        return dst * 0.75 + src * 0.25
    if mode == BlendMode.ALPHA_HARD:
        return dst * 0.4 + src * 0.6
    return src  # OVERWRITE


class BaseEffect:
    def step(self) -> list[tuple[int, int, float]]:
        """Return (x, y, brightness) pixels for this frame."""
        raise NotImplementedError

    def reset(self):
        pass

    def is_done(self) -> bool:
        return False

###----------------

class Layer:
    def __init__(self, effect: BaseEffect, blend: BlendMode = BlendMode.MAX):
        self.effect = effect
        self.blend = blend

class LayeredEffect(BaseEffect):
    def __init__(self, *layers: Layer):
        self.layers = layers

    def step(self):
        pixels: dict[tuple[int, int], float] = {}

        for layer in self.layers:
            if layer.effect.is_done():
                layer.effect.reset()

            for x, y, b in layer.effect.step():
                key = (x, y)
                pixels[key] = blend(pixels.get(key, 0.0), b, layer.blend)

        return [(x, y, b) for (x, y), b in pixels.items()]

###-------------------------------------------------------------------------------###
###---------------------------------------------------------------###
import math
import collections
import random
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

class Comet(BaseEffect):
    """
    A moving point with a fading tail, similar to a comet or tracer round.

    The comet advances by (dx, dy) each frame and leaves behind a short
    brightness trail that fades quadratically. The head of the comet is
    brightest, with older tail segments dimming smoothly over time.

    Movement behavior:
    - If `bounce` is True, the comet reflects off the display edges.
    - If `bounce` is False, the comet wraps around the display.

    The effect is continuous by default and does not automatically finish.
    It can be layered with other effects and blended using blend modes.

    Args:
        x (int | float): Starting x position.
        y (int | float): Starting y position.
        dx (float): Horizontal movement per frame.
        dy (float): Vertical movement per frame.
        tail_length (int): Number of pixels in the trailing tail.
        bounce (bool): Whether to bounce off edges or wrap around.

    Returns:
        Each call to `step()` returns a list of (x, y, brightness) tuples
        suitable for direct use with the Scroll pHAT HD.
    """
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
        # return self.distance > self.max_distance
        return False

class WaveRipple(BaseEffect):
    """
    An expanding circular wave that radiates outward from a center point.

    The ripple begins at radius zero and grows outward each frame, forming
    a thin circular wavefront. Pixels near the current wave radius are lit
    with a smooth, bell-shaped brightness profile, while the wave gradually
    fades as it expands.

    This effect is finite: once the ripple reaches its maximum radius,
    it automatically completes and reports `is_done() == True`. It can be
    reset and reused or layered with other effects using blend modes.

    Common uses include water ripples, shockwaves, sonar pings, or pulse
    effects.

    Args:
        cx (int | float): X-coordinate of the ripple center.
        cy (int | float): Y-coordinate of the ripple center.
        speed (float): Radial growth per frame (pixels per frame).
        max_radius (float | None): Maximum ripple radius. If None, the
            diagonal of the display is used to fully cover the matrix.

    Returns:
        Each call to `step()` returns a list of (x, y, brightness) tuples,
        where brightness is normalized between 0.0 and 1.0.
    """

    def __init__(self, cx, cy, speed=0.5, max_radius:float | None=None):
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

class BakedAnimation(BaseEffect):
    def __init__(self, filename: str, loop: bool = True):
        self.filename = filename
        self.loop = loop
        self.reset()

    def reset(self):
        import json, gzip

        with gzip.open(self.filename, "rt", encoding="utf-8") as f:
            data = json.load(f)

        self.frames = data["frames"]
        self.index = 0
        self.done = False

    def step(self):
        if self.done:
            return []

        frame = self.frames[self.index]
        self.index += 1

        if self.index >= len(self.frames):
            if self.loop:
                self.index = 0
            else:
                self.done = True

        return frame

    def is_done(self):
        return self.done

class PulseFade(BaseEffect):
    """
    Global brightness pulse across the entire display.
    """

    def __init__(self, speed=0.05, repeat=True):
        self.speed = speed
        self.repeat = repeat
        self.reset()

    def reset(self):
        self.phase = 0.0
        self.done = False

    def step(self):
        if self.done:
            return []

        brightness = (math.sin(self.phase) + 1.0) / 2.0
        self.phase += self.speed

        if self.phase >= math.pi * 2:
            if self.repeat:
                self.phase = 0.0
            else:
                self.done = True

        pixels = []
        for x in range(scrollphathd.width):
            for y in range(scrollphathd.height):
                pixels.append((x, y, brightness))

        return pixels

    def is_done(self):
        return self.done

###------------------------------------------------------------------------###
#Effect Class Template
# Design Questions to Answer First

# Before writing code:

# Is it continuous or finite?

# Is it spatial (position-based) or temporal (global)?

# Does it need memory (trails, waves)?

# Should it layer well with others?

# Does it reset cleanly?

class MyEffect(BaseEffect):
    def __init__(self, params):
        self.params = params
        self.reset()

    def reset(self):
        self.state = ...
        self.done = False

    def step(self):
        if self.done:
            return []
        pixels = []
        # update state
        # compute pixels

        return pixels

    def is_done(self):
        return self.done


###-------------------------------------------------------------------------------###
#run an effect and display on the matrix in realtime
import time
import scrollphathd

class EffectRunner:
    def __init__(self, effect: BaseEffect, fps: float = 20):
        self.effect = effect
        self.delay = 1.0 / fps

    def run(self, frames: int | None = None):
        count = 0

        while frames is None or count < frames:
            scrollphathd.clear()

            for x, y, b in self.effect.step():
                scrollphathd.set_pixel(x, y, clamp01(abs(b)))

            scrollphathd.show()
            time.sleep(self.delay)
            count += 1

###-------------------------------------------------------------------------------###
# AnimationRecorder a replacement for the EffectRunner Class that saves frames to a file to be read from later.

import json
import gzip

class AnimationRecorder:
    def __init__(self, effect: BaseEffect, fps: float = 25):
        self.effect = effect
        self.fps = fps
        self.frames: list[list[tuple[int, int, float]]] = []

    def record(self, frames: int | None = None):
        """
        Record frames from an effect.
        If frames is None, record until effect.is_done().
        """
        self.effect.reset()
        count = 0

        while frames is None or count < frames:
            frame = self.effect.step()
            self.frames.append(frame)

            count += 1
            if frames is None and self.effect.is_done():
                break

    def save(self, filename: str):
        data = {
            "version": 1,
            "width": scrollphathd.width,
            "height": scrollphathd.height,
            "fps": self.fps,
            "frame_count": len(self.frames),
            "frames": self.frames,
        }

        with gzip.open(filename, "wt", encoding="utf-8") as f:
            json.dump(data, f)

        print(f"Saved animation: {filename} ({len(self.frames)} frames)")

###-------------------------------------------------------------------------------###
# Examples
def demo_all_effects(fps: float = 25, frames_per_demo: int = 150):
    """
    Demonstrates all available effects and blending modes on Scroll pHAT HD.

    This function sequentially runs:
    - Sparkle
    - Comet
    - WaveRipple
    - ScannerSweep
    - ZigZagSweep
    - LayeredEffect combining multiple effects with different blend modes

    Args:
        fps (float): Frames per second for display update speed.
        frames_per_demo (int): Number of frames to run each effect.
    """
    # Configure display
    scrollphathd.clear()

    effects_to_demo = [
        ("Sparkle", Sparkle(randint(0, scrollphathd.width-1),
                            randint(0, scrollphathd.height-1))),
        ("Comet", Comet(0, 0, dx=1, dy=1, tail_length=6, bounce=True)),
        ("WaveRipple", WaveRipple(scrollphathd.width//2, scrollphathd.height//2, speed=0.7)),
        ("ScannerSweep", ScannerSweep(horizontal=True, speed=1, trail_length=6, bounce=True)),
        ("ZigZagSweep", ZigZagSweep(speed=1, trail_length=6, bounce=True)),
        ("PulseFade", PulseFade(speed=.05, repeat=True)),
        ("LayeredEffect", LayeredEffect(
            Layer(WaveRipple(8, 3, speed=0.7), BlendMode.OVERWRITE),
            Layer(WaveRipple(3, 8, speed=0.7), BlendMode.MAX),
            Layer(WaveRipple(5, 5, speed=0.7), BlendMode.ALPHA_SOFT),
            Layer(Comet(0, 0, dx=1, dy=2, tail_length=4, bounce=True), BlendMode.ALPHA_HARD),
            Layer(Comet(16, 0, dx=2, dy=1, tail_length=9, bounce=True), BlendMode.ALPHA_HARD)
        )),
    ]

    for name, effect in effects_to_demo:
        print(f"Running demo: {name}")
        effect.reset()
        runner = EffectRunner(effect,fps=fps)
        runner.run(frames=frames_per_demo)

def bake_all_effects(fps: float = 25, frames_per_demo: int = 150):
    """
    Demonstrates all available effects and blending modes on Scroll pHAT HD.

    This function sequentially runs:
    - Sparkle
    - Comet
    - WaveRipple
    - ScannerSweep
    - ZigZagSweep
    - LayeredEffect combining multiple effects with different blend modes

    Args:
        fps (float): Frames per second for display update speed.
        frames_per_demo (int): Number of frames to run each effect.
    """
    # Configure display
    scrollphathd.clear()

    effects_to_bake= [
        ("Sparkle", Sparkle(randint(0, scrollphathd.width-1), randint(0, scrollphathd.height-1))),
        ("Comet", Comet(0, 0, dx=1, dy=1, tail_length=6, bounce=True)),
        ("WaveRipple", WaveRipple(scrollphathd.width//2, scrollphathd.height//2, speed=0.7)),
        ("ScannerSweep", ScannerSweep(horizontal=True, speed=1, trail_length=6, bounce=True)),
        ("ZigZagSweep", ZigZagSweep(speed=1, trail_length=6, bounce=True)),
        ("PulseFade", PulseFade(speed=.05, repeat=True)),
        ("LayeredEffect", LayeredEffect(
            Layer(WaveRipple(8, 3, speed=0.7), BlendMode.OVERWRITE),
            Layer(WaveRipple(3, 8, speed=0.7), BlendMode.MAX),
            Layer(WaveRipple(5, 5, speed=0.7), BlendMode.ALPHA_SOFT),
            Layer(Comet(0, 0, dx=1, dy=2, tail_length=4, bounce=True), BlendMode.ALPHA_HARD),
            Layer(Comet(16, 0, dx=2, dy=1, tail_length=9, bounce=True), BlendMode.ALPHA_HARD)
        )),
    ]

    try:
        for name, effect in effects_to_bake:
            print(f"Running demo: {name}")
            effect.reset()
            bake_animation(name, effect, fps)


    except KeyboardInterrupt:
        print("Demo interrupted, clearing display...")
    finally:
        scrollphathd.clear()
        scrollphathd.show()

def bake_animation(file_name: str, effect: BaseEffect, fps: float = 25, frames_to_save: int = 150):
    recorder = AnimationRecorder(effect, fps=fps)
    recorder.record(frames=frames_to_save)   # auto-stops when ripple is done
    recorder.save(f"{file_name}.anim.gz")

def demo_play_baked_animation(fps: float = 25, frames_to_play: int = 150):
    baked_animations = [
        "Sparkle.anim.gz",
        "Comet.anim.gz",
        "ScannerSweep.anim.gz",
        "LayeredEffect.anim.gz",
        "WaveRipple.anim.gz",
        "ZigZagSweep.anim.gz"]
    for baked_anim in baked_animations:
        anim = BakedAnimation(baked_anim, loop=False)
        runner = EffectRunner(anim, fps=fps)
        runner.run(frames=frames_to_play)

###-------------------------------------------------------------------------------###

if __name__ == '__main__':
# Catches control-c and exits cleanly
    try:
        # Uncomment to turn off debugging
        ic.disable()

        # Uncomment the below if your display is upside down
        scrollphathd.rotate(degrees=180)

        pulse_fade = PulseFade(speed=.05, repeat=True)
        pulse_fade.reset()
        runner = EffectRunner(pulse_fade,fps=25)
        runner.run(frames=150)
        # Set max brightness
        #scrollphathd.set_brightness(0.8)
        #demo_all_effects()
        #bake_all_effects()
        #demo_play_baked_animation()
    

    except KeyboardInterrupt:
        scrollphathd.clear()
        scrollphathd.show()
        print("Exiting!")