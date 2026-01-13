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

from contextlib import contextmanager

@contextmanager
def capture_pixels():
    """This safely hijacks rendering and restores it afterward."""
    captured = {}

    original_set_pixel = scrollphathd.set_pixel

    def fake_set_pixel(x, y, b):
        if b > 0:
            captured[(x, y)] = max(captured.get((x, y), 0.0), b)

    scrollphathd.set_pixel = fake_set_pixel
    try:
        yield captured
    finally:
        scrollphathd.set_pixel = original_set_pixel
    
from scrollphathd.fonts import font3x5
def rasterize_string(
    text,
    x=0,
    y=0,
    brightness=1.0,
    **kwargs
) -> dict[tuple[int, int], float]:
    """
    Returns {(x, y): brightness} for text drawn via write_string.
    """
    with capture_pixels() as pixels:
        scrollphathd.clear()
        scrollphathd.write_string(
            text,
            x=x,
            y=y,
            font=font3x5,
            brightness=brightness,
            **kwargs
        )
    return pixels

###-------------------------------------------------------------------------------###
from enum import Enum

class BlendMode(Enum):
    """
    Enumeration of pixel blending strategies used when combining layers.

    Each mode defines how a source pixel's brightness is combined with
    an existing destination pixel's brightness.

    Modes:
        MAX: Take the maximum brightness.
        ADD: Add brightness values together.
        ALPHA_SOFT: Soft alpha blend favoring destination.
        ALPHA_HARD: Stronger alpha blend favoring source.
        OVERWRITE: Replace destination with source.
    """
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
    """
    Abstract base class for all visual effects.

    Effects are stateful objects that generate pixels frame-by-frame.
    Subclasses must implement `step()` and may optionally override
    `reset()` and `is_done()`.

    Contract:
        - step() returns a list of (x, y, brightness) tuples
        - reset() restores the effect to its initial state
        - is_done() indicates whether the effect has finished
    """
    def step(self) -> list[tuple[int, int, float]]:
        """Return (x, y, brightness) pixels for this frame."""
        raise NotImplementedError

    def reset(self):
        """Reset internal state so the effect can be replayed."""
        pass

    def is_done(self) -> bool:
        """Return True if the effect has completed execution."""
        return False

###-------------------------------------------------------------------------------###

class Layer():
    """
    Container pairing an effect with a blend mode.

    Layers are used by LayeredEffect to combine multiple effects into
    a single composite output using the specified blend strategy.

    Args:
        effect (BaseEffect): The effect to render.
        blend (BlendMode): How this effect blends with others.
    """
    def __init__(self, effect: BaseEffect, blend: BlendMode = BlendMode.MAX):
        self.effect = effect
        self.blend = blend

class LayeredEffect(BaseEffect):
    """
    Composite effect that combines multiple effects using blend modes.

    Each layer is rendered independently, and overlapping pixels are
    merged using the layer's blend mode. Finished effects are
    automatically reset, making this suitable for looping visuals.

    Args:
        *layers (Layer): One or more Layer objects.
    """
    def __init__(self, *layers: Layer):
        self.layers = layers

    def step(self):
        pixels: dict[tuple[int, int], float] = {}

        for layer in self.layers:
            if layer.effect.is_done():
                layer.effect.reset()

            if isinstance(layer.effect, BufferEffect):

                layer.effect.step()  # effect draws directly

                scrollphathd.show()
                time.sleep(1/20)
                continue

            for x, y, b in layer.effect.step():
                key = (x, y)
                pixels[key] = blend(pixels.get(key, 0.0), b, layer.blend)

        return [(x, y, b) for (x, y), b in pixels.items()]

    def reset(self):
        for layer in self.layers:
            layer.effect.reset()
###-------------------------------------------------------------------------------###

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
        return self.step_count > self.max_steps

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

    def __init__(self, cx, cy, speed:float = 0.5, max_radius:float | None = None):
        self.cx = cx
        self.cy = cy
        self.speed = speed
        self._max_radius = max_radius
        self.reset()

    def reset(self):
        self.radius = 0.0
        self.done = False

        w, h = scrollphathd.width, scrollphathd.height

        if self._max_radius is not None:
            self.max_radius = self._max_radius
        else:
            self.max_radius = math.hypot(w, h)

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

class ExpandingBox(BaseEffect):
    """
    Expanding rectangular outline from a center.
    """

    def __init__(self, cx, cy, speed:float = 0.5, max_radius:float | None = None):
        self.cx = cx
        self.cy = cy
        self.speed = speed
        self._max_radius = max_radius
        self.reset()

    def reset(self):
        self.radius = 0.0
        self.done = False

        w, h = scrollphathd.width, scrollphathd.height

        if self._max_radius is not None:
            self.max_radius = self._max_radius
        else:
            self.max_radius = math.hypot(w, h)

    def step(self):
        if self.done:
            return []

        pixels = []
        r = self.radius

        for x in range(scrollphathd.width):
            for y in range(scrollphathd.height):
                if (
                    ((abs(x - self.cx) == r) and (abs(y - self.cy) <= r)) or
                    ((abs(y - self.cy) == r) and (abs(x - self.cx) <= r))
                ):
                    pixels.append((x, y, 1.0))

        self.radius += self.speed

        if self.radius > self.max_radius:
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
#TODO: Adjust. Unimpressive as a single point moving. maybe add a tail or fill in as it goes
class SpiralSweep(BaseEffect):
    """
    Spiral sweep expanding from center.
    """

    def __init__(self, cx, cy, speed=0.2):
        self.cx = cx
        self.cy = cy
        self.speed = speed
        self.reset()

    def reset(self):
        self.angle = 0.0
        self.radius = 0.0
        self.done = False
        self.max_radius = math.hypot(scrollphathd.width, scrollphathd.height)

    def step(self):
        if self.done:
            return []

        x = int(round(self.cx + math.cos(self.angle) * self.radius))
        y = int(round(self.cy + math.sin(self.angle) * self.radius))

        self.angle += self.speed
        self.radius += self.speed * 0.1

        if self.radius > self.max_radius:
            self.done = True

        if 0 <= x < scrollphathd.width and 0 <= y < scrollphathd.height:
            return [(x, y, 1.0)]

        return []

    def is_done(self):
        return self.done

class BakedAnimation(BaseEffect):
    """
    Plays back a pre-recorded animation from a compressed file.

    Frames are loaded from a gzip-compressed JSON file produced by
    AnimationRecorder. Can loop or play once.

    Args:
        filename (str): Path to .anim.gz file.
        loop (bool): Whether to restart when finished.
    """
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

class Scene(BaseEffect):
    def __init__(self, *effects):
        self.effects = effects

    def step(self):
        pixels = []
        for e in self.effects:
            pixels.extend(e.step())
        return pixels

###------------------------------------------------------------------------###
# Pac Man, Pellet, and Ghost animation and scene logic
class PacMan(BaseEffect):
    """
    Animated Pac-Man character with a smooth chomping mouth.

    Uses subpixel movement for smooth motion while remaining stable
    on low-resolution LED matrices. Supports wrapping or finite travel.

    Args:
        x, y: Starting position.
        x_speed, dy: Movement per frame.
        radius: Body radius in pixels.
        chomp_speed: Mouth animation speed.
        wrap: Whether to wrap around display edges.
    """

    def __init__(
        self,
        x,
        y,
        x_speed=0.25,
        dy=0.0,
        radius=3.0,
        chomp_speed=1.0,
        wrap=True,
    ):
        self.start_x = float(x)
        self.start_y = float(y)
        self.dx = x_speed
        self.dy = dy
        self.radius = radius
        self.chomp_speed = chomp_speed
        self.wrap = wrap
        self.reset()

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.phase = 0.0
        self.done = False

    def step(self):
        if self.done:
            return []

        w, h = scrollphathd.width, scrollphathd.height

        # Move (subpixel, but stable)
        self.x += self.dx
        self.y += self.dy

        if self.wrap:
            self.x %= w
            self.y %= h
        else:
            if not (0 <= self.x < w and 0 <= self.y < h):
                self.done = True
                return []

        # Chomp animation (clearly visible)
        self.phase += self.chomp_speed
        mouth_open = (math.sin(self.phase) + 1.0) / 2.0
        mouth_angle = mouth_open * (math.pi / 2.2)

        # Direction Pac-Man is facing
        dir_angle = math.atan2(self.dy, self.dx)

        pixels = []

        # Tight bounding box (reduces flicker)
        xmin = int(self.x - self.radius - 1)
        xmax = int(self.x + self.radius + 1)
        ymin = int(self.y - self.radius - 1)
        ymax = int(self.y + self.radius + 1)

        for ix in range(xmin, xmax + 1):
            for iy in range(ymin, ymax + 1):
                if not (0 <= ix < w and 0 <= iy < h):
                    continue

                # Sample at pixel center
                dx = ix + 0.5 - self.x
                dy = iy + 0.5 - self.y
                dist = math.hypot(dx, dy)

                # Solid filled body
                if dist > self.radius:
                    continue

                angle = math.atan2(dy, dx)

                # Relative angle to direction
                rel = (angle - dir_angle + math.pi * 3) % (2 * math.pi) - math.pi

                # Mouth cutout (hard, stable)
                if abs(rel) < mouth_angle:
                    continue

                b = 1.0
                if dist > self.radius - 0.6:
                    b = clamp01(self.radius - dist + 0.6)
                
                pixels.append((ix, iy, 1.0))

        return pixels

    def is_done(self):
        return self.done

class PelletRow(BaseEffect):
    """
    Row of evenly spaced pellets that can be consumed.

    Pellets are removed when `eat(x)` is called, typically by a
    Pac-Man style effect.
    """
    def __init__(self, y):
        self.y = y
        self.reset()

    def reset(self):
        self.pellets = {x for x in range(0,scrollphathd.width,3)}
        self.done = False

    def eat(self, x):
        self.pellets.discard(int(x))

    def step(self):
        return [(x, self.y, 0.5) for x in self.pellets]

    def is_done(self):
        return self.done

class Ghost(BaseEffect):
    """
    Pac-Man style ghost with animated feet.

    Moves horizontally across the display and completes once fully
    off-screen.
    """
    def __init__(self, x, y, x_speed=0.15):
        self.start_x = x
        self.y = y
        self.x_speed = x_speed
        self.reset()

    def reset(self):
        self.x = self.start_x
        self.phase = 0
        self.done = False

    def step(self):
        self.x += self.x_speed
        self.phase += 1

        if self.x >= scrollphathd.width + 4:
            self.done = True
            return []

        pixels = []
        w, h = scrollphathd.width, scrollphathd.height

        cx = int(round(self.x))
        cy = int(round(self.y))

        # --- Head (semi-circle) ---
        head_radius = 2

        for dx in range(-head_radius, head_radius + 1):
            for dy in range(-head_radius, 1):
                if dx * dx + dy * dy <= head_radius * head_radius:
                    px = cx + dx
                    py = cy + dy
                    if 0 <= px < w and 0 <= py < h:
                        pixels.append((px, py, 0.6))

        # --- Body ---
        body_height = 3
        body_width = 2

        for dx in range(-body_width, body_width + 1):
            for dy in range(1, body_height + 1):
                px = cx + dx
                py = cy + dy
                if 0 <= px < w and 0 <= py < h:
                    pixels.append((px, py, 0.6))

        # --- Bumpy bottom (animated) ---
        bump_y = cy + body_height + 1
        bump_phase = self.phase % 2

        for i, dx in enumerate([-2, 0, 2]):
            if (i + bump_phase) % 2 == 0:
                px = cx + dx
                py = bump_y
                if 0 <= px < w and 0 <= py < h:
                    pixels.append((px, py, 0.6))

        return pixels

    def is_done(self):
        return self.done

class PacManScene(BaseEffect):
    """
    Coordinated scene combining Pac-Man, pellets, and a ghost.

    Handles interaction logic such as pellet consumption and scene
    termination when Pac-Man exits the display.
    """

    def __init__(self, pellets, pacman, ghost) -> None:
        self.pellets = pellets
        self.pacman = pacman
        self.ghost = ghost
        self.reset()

    def reset(self):
        self.pellets.reset()
        self.pacman.reset()
        self.ghost.reset()
        self.done = False

    def step(self):
        pacman_pixels = self.pacman.step()
        self.pellets.eat(self.pacman.x)

        pixels = []
        pixels += self.pellets.step()
        pixels += self.ghost.step()
        pixels += pacman_pixels

        if self.pacman.x > scrollphathd.width + 4:
            self.done = True

        return pixels

    def is_done(self):
        return self.done

###------------------------------------------------------------------------###
class BufferEffect(BaseEffect):
    """
    Effect that draws directly into the Scroll pHAT HD buffer.

    BaseEffect → returns pixels
    BufferEffect → draws pixels
    Writes directly to the Scroll pHAT HD buffer

    Lets the hardware library manage transforms
    - Does not return pixels
    - Responsible for calling scrollphathd.* drawing functions
    To keep sanity:

        Should NOT call scrollphathd.show()
        Should NOT sleep
        Should NOT manage FPS
        Should NOT clear the buffer unless explicitly intended

        Those are runner responsibilities.

    """
    def step(self):
        """
        Perform one frame of drawing into the hardware buffer.
        """
        raise NotImplementedError

    def render(self):
        scrollphathd.clear()
        self.step()

class StaticText(BufferEffect):
    """
    Static Text Effect
    """
    def __init__(self, text, x=0, y=0, brightness=1.0):
        self.text = text
        self.x = x
        self.y = y
        self.brightness = brightness
    
    def step(self):
        scrollphathd.write_string(
            self.text,
            x=self.x,
            y=self.y,
            font=font3x5,
            brightness=self.brightness
        )

class CameraScroll:
    """
    Camera scroll mixin for buffer-native effects.
    Controls the Scroll pHAT HD viewport position.
    """

    def __init__(self, speed=1, start_x=0):
        self.camera_x = start_x
        self.speed = speed

    def reset_camera(self):
        self.camera_x = 0

    def step_camera(self):
        scrollphathd.scroll_to(self.camera_x)
        self.camera_x += self.speed

class ScrollingText(BufferEffect):
    """
    Scrolling Text takes a String and an integer value for speed. 
    and uses them to create a Static Text Class and a Camera Scroll class. Together it gives us scrolling text!
    """
    def __init__(self, text, speed=1):
        self.text = StaticText(text)
        self.camera = CameraScroll(speed)

    def reset(self):
        self.camera.reset_camera()

    def step(self):
        self.text.step()
        self.camera.step_camera()

class RotateScene(BaseEffect):
    """ 
    Rotating scene effect
    
    Can be used for Rotating logos

    Flipping warnings

    Direction changes with zero math"""
    def __init__(self, degrees_per_step=90):
        self.deg = 0
        self.step_size = degrees_per_step

    def step(self):
        self.deg = (self.deg + self.step_size) % 360
        scrollphathd.rotate(self.deg)
        return []

class WaveGraph(BufferEffect):
    """
    An animated waveform
    """
    def __init__(self):
        self.phase = 0

    def step(self):
        values = [
            math.sin(self.phase + i * 0.4)
            for i in range(17)
        ]
        scrollphathd.set_graph(values, low=-1, high=1)
        self.phase += 0.2


###------------------------------------------------------------------------###
###------------------------------------------------------------------------###
# Effect Class Template
# Design Questions to Answer First

# Before writing code:

# Is it continuous or finite?

# Is it spatial (position-based) or temporal (global)?

# Does it need memory (trails, waves)?

# Should it layer well with others?

# Does it reset cleanly?

# When writing an effect, ask:

# “Do I want to compute pixels, or use the hardware buffer?”

# Compute pixels → subclass BaseEffect

# Use buffer features → subclass BufferEffect

# Everything else stays consistent.

class MyEffect(BaseEffect):
    """
    Template for creating new effects.

    Intended as a starting point when designing new visual effects.
    Includes the standard lifecycle methods and design questions.
    """
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
# Run an effect and display on the matrix in realtime
import time
import scrollphathd


class EffectRunner:
    """
    Drives an effect in real-time and renders it to the LED matrix.

    Handles frame timing, brightness normalization, optional inversion,
    and pushing pixel data to the Scroll pHAT HD hardware.

    Args:
        effect (BaseEffect): Effect to run.
        fps (float): Frames per second.
        invert (bool): Whether to invert brightness values.
    """
    def __init__(self, effect: BaseEffect, fps: float = 20, invert: bool = False):
        self.effect = effect
        self.delay = 1.0 / fps
        self.invert = invert

    def apply_transformation(self, b:float) -> float:
        if self.invert:
            return 1.0 - b
        return b

    def run(self, frames: int | None = None):
        count = 0

        while frames is None or count < frames:
            # NEW: buffer-native path
            if isinstance(self.effect, BufferEffect):
                scrollphathd.clear()

                self.effect.step()  # effect draws directly

                scrollphathd.show()
                time.sleep(self.delay)
                count += 1
                continue

            frame_pixels = {(x, y): b for x, y, b in self.effect.step()}
            
            scrollphathd.clear()

            for x in range(scrollphathd.width):
                for y in range(scrollphathd.height):
                    b = frame_pixels.get((x, y), 0.0)
                    b = self.apply_transformation(b)
                    b = clamp01(b)
                    scrollphathd.set_pixel(x, y, b)

            scrollphathd.show()
            time.sleep(self.delay)
            count += 1

###-------------------------------------------------------------------------------###
# AnimationRecorder a replacement for the EffectRunner Class that saves frames to a file to be read from later.

import json
import gzip

class AnimationRecorder:
    """
    Records frames from an effect and saves them to disk.

    Intended for pre-baking animations so they can be replayed later
    without recomputing effect logic.

    Args:
        effect (BaseEffect): Effect to record.
        fps (float): Playback frame rate metadata.
    """
    def __init__(self, effect: BaseEffect, fps: float = 25):
        self.effect = effect
        self.fps = fps
        self.frames: list[list[tuple[int, int, float]]] = []

    def record(self, frames: int | None = None):
        """
        Record frames from an effect.
        If frames is None, record until effect.is_done().
        """
        if frames is None and not hasattr(self.effect, "is_done"):
            raise ValueError("Finite effect required when frames=None")

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
        ("PacManScene", PacManScene(
            PelletRow(y=3), 
            PacMan(0, 3, x_speed=0.25, wrap=False), 
            Ghost(-7, 2))),
        ("Layered_PacMan",LayeredEffect(
            Layer(PelletRow(y=3),BlendMode.OVERWRITE),
            Layer(Ghost(-6, 1, x_speed=0.2), BlendMode.MAX),
            Layer(PacMan(0, 3, x_speed=0.25), BlendMode.OVERWRITE))),
        ("ExpandingBox", ExpandingBox(cx=8, cy=3,speed=1)),
        ("SpiralSweep", SpiralSweep(cx=8, cy=3, speed=1)),
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
        runner = EffectRunner(effect, fps=fps, invert=False)
        runner.run(frames=frames_per_demo)

def demo_all_effects2():
    """
    Demonstrate all effects and engine capabilities:
    - Static buffer effects
    - Camera-based scrolling
    - Composite effects
    - Pixel-based effects
    """

    effects = [

        # 6. Composite: pixel effect + text overlay
        ("Pixel + Text Overlay",
        LayeredEffect(
        Layer(PacMan(x=0, y=3, x_speed=0.25),blend=BlendMode.OVERWRITE),
        Layer(StaticText("HUD", x=0, y=1),blend=BlendMode.OVERWRITE)
        )),
        # 1. Static text (buffer-native, no camera)
        ("StaticText", StaticText("STATIC", x=0, y=1)),

        # 2. Scanner (buffer-native animation)
        ("Scanner", ScannerSweep(speed=1)),

        # 3. Scrolling text (StaticText + CameraScroll)
        ("ScrollingText", ScrollingText("SCROLLING TEXT", speed=1)),

        # 5. Pixel-based effect (example)
        ("PacMan", PacMan(x=0, y=3, x_speed=0.25)),
    ]

    for name, effect in effects:
        print(f"\n--- Running: {name} ---")

        runner = EffectRunner(
            effect=effect,
            fps=30
        )

        effect.reset()
        runner.run(frames=120)

        time.sleep(0.5)


def bake_all_effects(fps: float = 25, frames_to_save: int = 150):
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
        ("PacManScene", PacManScene(
            PelletRow(y=3), 
            PacMan(0, 3, x_speed=0.25, wrap=False), 
            Ghost(-7, 2))),
        ("Layered_PacMan",LayeredEffect(
            Layer(PelletRow(y=3),BlendMode.OVERWRITE),
            Layer(Ghost(-6, 1, x_speed=0.2), BlendMode.MAX),
            Layer(PacMan(0, 3, x_speed=0.25), BlendMode.OVERWRITE))),
        ("ExpandingBox", ExpandingBox(cx=8, cy=3,speed=1)),
        ("SpiralSweep", SpiralSweep(cx=8, cy=3, speed=1)),
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
            print(f"Baking Effect: {name}")
            effect.reset()
            bake_animation(name, effect, fps, frames_to_save=frames_to_save)


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
        "PacManScene.anim.gz",
        "Layered_PacMan.anim.gz",
        "ExpandingBox.anim.gz",
        "SpiralSweep.anim.gz",
        "PulseFade.anim.gz",
        "Sparkle.anim.gz",
        "Comet.anim.gz",
        "ScannerSweep.anim.gz",
        "LayeredEffect.anim.gz",
        "WaveRipple.anim.gz",
        "ZigZagSweep.anim.gz"]
    for baked_anim in baked_animations:
        anim = BakedAnimation(baked_anim, loop=False)
        runner = EffectRunner(anim, fps=fps,invert=False)
        runner.run(frames=frames_to_play)

###-------------------------------------------------------------------------------###

if __name__ == '__main__':
# Catches control-c and exits cleanly
    try:
        # Uncomment to turn off debugging
        ic.disable()

        # Set max brightness
        scrollphathd.set_brightness(0.2)

        # Uncomment the below if your display is upside down
        scrollphathd.rotate(degrees=180)

        # layered_pacman = LayeredEffect(
        #     Layer(PelletRow(y=3),BlendMode.OVERWRITE),
        #     Layer(Ghost(-6, 1, x_speed=0.2), BlendMode.MAX),
        #     Layer(PacMan(0, 3, x_speed=0.25), BlendMode.OVERWRITE))
        # layered_pacman.reset()
        # runner = EffectRunner(layered_pacman, fps=25, invert=False)
        # runner.run(frames=150)
        # text_effect = ScrollingText(" Hello KiKi ")
        # runner = EffectRunner(text_effect,fps=25,invert=False)
        # runner.run()

        demo_all_effects2()
        # bake_all_effects()
        # demo_play_baked_animation()
    

    except KeyboardInterrupt:
        scrollphathd.clear()
        scrollphathd.show()
        print("Exiting!")