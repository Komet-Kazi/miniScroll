# All effect classes + effect utilities

from __future__ import annotations

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
# Uncomment to turn off debugging
ic.disable()


import math, collections
from random import randint
from enum import Enum

from runner import DisplayConfig

###------------------------------------------------------------------------------###
# Helper Functions

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

    Hardware Agnostic Design:
        Effects should accept optional `width` and `height` parameters in their
        __init__() methods to remain hardware-agnostic. Import DisplayConfig
        from runner module when needed for default dimensions.
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

class Layer:
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

            for x, y, b in layer.effect.step():
                key = (x, y)
                pixels[key] = blend(pixels.get(key, 0.0), b, layer.blend)

        return [(x, y, b) for (x, y), b in pixels.items()]

    def reset(self):
        for layer in self.layers:
            layer.effect.reset()
###-------------------------------------------------------------------------------###

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
        # Sparkle handles its own looping internally, never signals completion
        return False

class SparkleField(BaseEffect):
    """
    Field of multiple sparkles distributed across the display.

    Creates a shimmering starfield effect by managing multiple Sparkle
    instances that activate at random positions. Each sparkle cycles
    independently with its own timing, creating a natural twinkling
    effect across the entire display.

    The effect is continuous and deterministic - calling reset() will
    produce the same sparkle pattern each time, making it suitable for
    recording and playback.

    Args:
        density (int): Maximum number of active sparkles at once (default: 30).
        speed_range (tuple[int, int]): (min, max) speed values for sparkles.
            Each sparkle gets a random speed in this range on activation.
            Default: (10, 50).
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).

    Example:
        # Default sparkling field
        field = SparkleField()

        # Dense, fast-twinkling field
        field = SparkleField(density=50, speed_range=(5, 20))

        # Layered with other effects
        scene = LayeredEffect(
            Layer(WaveRipple(8, 3), BlendMode.ALPHA_SOFT),
            Layer(SparkleField(density=20), BlendMode.ADD)
        )
    """

    def __init__(
        self,
        density: int = 30,
        speed_range: tuple[int, int] = (10, 50),
        width=None,
        height=None,
    ):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
        self.density = density
        self.speed_range = speed_range
        self.reset()

    def reset(self):
        """
        Reset the sparkle field to initial state.

        Pre-generates a deterministic activation sequence by creating
        a shuffled list of all pixel positions and pre-assigned speeds.
        This ensures the effect is reproducible while appearing random.
        """
        import itertools
        from random import shuffle, randint

        # Create pool of all possible positions
        all_positions = list(itertools.product(
            range(self.width), range(self.height)
        ))

        # Shuffle positions for random activation order
        shuffle(all_positions)

        # Pre-assign speeds to each position
        self.position_pool = [
            (x, y, randint(self.speed_range[0], self.speed_range[1]))
            for x, y in all_positions
        ]

        self.pool_index = 0
        self.active_sparkles: list[Sparkle] = []
        self.done = False

    def step(self):
        """
        Advance animation and return visible pixels for current frame.

        Manages the lifecycle of sparkles: activates new ones when under
        the density limit, advances all active sparkles, and removes
        completed ones.

        Returns:
            list[tuple[int, int, float]]: Combined pixels from all active sparkles.
        """
        # Add new sparkles if under density limit and pool not exhausted
        while (
            len(self.active_sparkles) < self.density
            and self.pool_index < len(self.position_pool)
        ):
            x, y, speed = self.position_pool[self.pool_index]
            sparkle = Sparkle(x, y, speed=speed)
            self.active_sparkles.append(sparkle)
            self.pool_index += 1

        # Collect pixels from all active sparkles
        pixels = []
        sparkles_to_remove = []

        for sparkle in self.active_sparkles:
            sparkle_pixels = sparkle.step()
            pixels.extend(sparkle_pixels)

            # Note: Current Sparkle implementation never returns True for is_done()
            # and resets itself internally. This check is here for future-proofing
            # if Sparkle behavior changes to allow finite cycles.
            if sparkle.is_done():
                sparkles_to_remove.append(sparkle)

        # Remove completed sparkles
        for sparkle in sparkles_to_remove:
            self.active_sparkles.remove(sparkle)

        return pixels

    def is_done(self):
        """
        Return True if the effect has completed execution.

        SparkleField is a continuous effect that never completes on its own.
        Sparkles loop indefinitely, creating a persistent starfield.
        """
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
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).

    Returns:
        Each call to `step()` returns a list of (x, y, brightness) tuples
        suitable for direct use with any LED matrix.
    """
    def __init__(self, x, y, dx:float=1.0, dy:float=0.0, tail_length=6, bounce=True, width=None, height=None):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
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
        w, h = self.width, self.height
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
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).

    Returns:
        Each call to `step()` returns a list of (x, y, brightness) tuples,
        where brightness is normalized between 0.0 and 1.0.
    """

    def __init__(self, cx, cy, speed:float = 0.5, max_radius:float | None = None, width=None, height=None):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
        self.cx = cx
        self.cy = cy
        self.speed = speed
        self._max_radius = max_radius
        self.reset()

    def reset(self):
        self.radius = 0.0

        w, h = self.width, self.height

        if self._max_radius is not None:
            self.max_radius = self._max_radius
        else:
            self.max_radius = math.hypot(w, h)

    def step(self):
        pixels = []
        w, h = self.width, self.height

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

        # Loop the ripple when it reaches max radius
        if round(self.radius) > round(self.max_radius):
            self.radius = 0.0

        return pixels

    def is_done(self):
        return False

class ExpandingBox(BaseEffect):
    """
    Expanding rectangular outline from a center.

    Args:
        cx: Center x position.
        cy: Center y position.
        speed: Expansion speed per frame.
        max_radius: Maximum expansion radius (None = diagonal).
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).
    """

    def __init__(self, cx, cy, speed:float = 0.5, max_radius:float | None = None, width=None, height=None):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
        self.cx = cx
        self.cy = cy
        self.speed = speed
        self._max_radius = max_radius
        self.reset()

    def reset(self):
        self.radius = 0.0

        w, h = self.width, self.height

        if self._max_radius is not None:
            self.max_radius = self._max_radius
        else:
            self.max_radius = math.hypot(w, h)

    def step(self):
        pixels = []
        r = self.radius

        for x in range(self.width):
            for y in range(self.height):
                if (
                    ((abs(x - self.cx) == r) and (abs(y - self.cy) <= r)) or
                    ((abs(y - self.cy) == r) and (abs(x - self.cx) <= r))
                ):
                    pixels.append((x, y, 1.0))

        self.radius += self.speed

        # Loop the ripple when it reaches max radius
        if round(self.radius) > round(self.max_radius):
            self.radius = 0.0

        return pixels

    def is_done(self):
        return False
    
class ScannerSweep(BaseEffect):
    """
    Sweeping scanner / radar-style line with a fading trail.

    Args:
        horizontal: True for left→right sweep, False for top→bottom
        speed: Pixels per frame
        trail_length: Number of trailing pixels
        bounce: Reverse direction at edges
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).
    """

    def __init__(self, horizontal=True, speed=1, trail_length=5, bounce=True, width=None, height=None):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
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


    def step(self):
        w, h = self.width, self.height

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
        return False

class ZigZagSweep(BaseEffect):
    """
    Zig-zag sweeping effect with vertical bouncing.

    A single point sweeps left/right across a row, then moves up/down to the
    next row, reversing horizontal direction each time.

    Args:
        speed: Movement speed per frame.
        trail_length: Number of trailing pixels.
        bounce: Reverse direction at edges.
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).
    """

    def __init__(self, speed=1, trail_length=6, bounce=True, width=None, height=None):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
        self.speed = speed
        self.trail_length = trail_length
        self.bounce = bounce
        self.reset()

    def reset(self):
        self.w = self.width
        self.h = self.height

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

class PulseFade(BaseEffect):
    """
    Global brightness pulse across the entire display.

    Args:
        speed: Pulse speed.
        repeat: Whether to repeat continuously.
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).
    """

    def __init__(self, speed=0.05, repeat=True, width=None, height=None):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
        self.speed = speed
        self.repeat = repeat
        self.reset()

    def reset(self):
        self.phase = 0.0


    def step(self):
        brightness = (math.sin(self.phase) + 1.0) / 2.0
        self.phase += self.speed

        if self.phase >= math.pi * 2:
            if self.repeat:
                self.phase = 0.0
            else:
                self.done = True

        pixels = []
        for x in range(self.width):
            for y in range(self.height):
                pixels.append((x, y, brightness))

        return pixels

    def is_done(self):
        return False

#TODO: Adjust. Unimpressive as a single point moving. maybe add a tail or fill in as it goes
class SpiralSweep(BaseEffect):
    """
    Spiral sweep expanding from center.

    Args:
        cx: Center x position.
        cy: Center y position.
        speed: Rotation and expansion speed.
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).
    """

    def __init__(self, cx, cy, speed=0.2, width=None, height=None):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
        self.cx = cx
        self.cy = cy
        self.speed = speed
        self.reset()

    def reset(self):
        self.angle = 0.0
        self.radius = 0.0
        self.max_radius = math.hypot(self.width, self.height)

    def step(self):
        x = int(round(self.cx + math.cos(self.angle) * self.radius))
        y = int(round(self.cy + math.sin(self.angle) * self.radius))

        self.angle += self.speed
        self.radius += self.speed * 0.1

        if self.radius > self.max_radius:
            self.done = True

        if 0 <= x < self.width and 0 <= y < self.height:
            return [(x, y, 1.0)]

        return []

    def is_done(self):
        return False


###------------------------------------------------------------------------###
# Text Display Effect

class TextScroller(BaseEffect):
    """
    Scrolling or static text display effect.

    Renders text using scrollphathd fonts and returns pixels compatible
    with the layering system. Text can scroll horizontally, display
    statically, or loop continuously.

    This effect directly accesses font bitmap data to render characters
    without interfering with scrollphathd's global buffer, making it
    fully compatible with the pixel-based effects architecture.

    Args:
        text (str): The text string to display.
        x_start (int): Starting x position (default: width, off-screen right).
        y_pos (int): Vertical position of text baseline (default: 0).
        speed (float): Scroll speed in pixels per frame (default: 1.0).
                      Use 0 for static text.
        font: scrollphathd font object (default: font5x7).
        letter_spacing (int): Pixels between characters (default: 1).
        brightness (float): Text brightness 0.0-1.0 (default: 1.0).
        loop (bool): Whether to restart when scrolling completes (default: False).
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).

    Example:
        # Scrolling text
        text = TextScroller("HELLO WORLD", speed=0.5)

        # Static text overlay
        label = TextScroller("FPS: 60", x_start=0, y_pos=0, speed=0)

        # Layered with animation
        composite = LayeredEffect(
            Layer(Comet(5, 3), BlendMode.MAX),
            Layer(TextScroller("COMET", y_pos=1), BlendMode.ALPHA_HARD)
        )
    """

    def __init__(
        self,
        text: str,
        x_start: int | None = None,
        y_pos: int = 0,
        speed: float = 1.0,
        font=None,
        letter_spacing: int = 1,
        brightness: float = 1.0,
        loop: bool = False,
        width=None,
        height=None,
    ):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height

        self.text = text
        self.y_pos = y_pos
        self.speed = speed
        self.letter_spacing = letter_spacing
        self.brightness = brightness
        self.loop = loop

        # Default x_start to off-screen right
        self.x_start = x_start if x_start is not None else self.width

        # Set default font if none provided
        if font is None:
            try:
                from scrollphathd.fonts import font5x7
                self.font = font5x7
            except ImportError:
                raise ImportError("scrollphathd.fonts not available")
        else:
            self.font = font

        # Pre-render text to pixels
        self.text_pixels, self.text_width = self._render_from_font_data()

        self.reset()

    def _render_from_font_data(self):
        """
        Render text by directly accessing font character bitmaps.

        Returns:
            tuple: (pixels, text_width) where pixels is list of (x, y, brightness)
                   and text_width is the total width in pixels.
        """
        pixels = []
        x_offset = 0

        # Access the font data dictionary
        font_data = self.font.data if hasattr(self.font, 'data') else self.font

        for char in self.text:
            # Get character bitmap from font (fonts are indexed by ordinal)
            try:
                char_data = font_data[ord(char)]
            except (KeyError, IndexError):
                # Character not in font, skip it
                continue

            # char_data is a list of rows (horizontal strips of pixels)
            # Each row is a list of pixel values (0 or 1, or brightness values)
            for row_idx, row in enumerate(char_data):
                for col_idx in range(len(row)):
                    if row[col_idx]:  # If pixel is set
                        pixels.append((
                            x_offset + col_idx,
                            row_idx,
                            self.brightness
                        ))

            # Move to next character position
            # Character width is the length of the first row
            char_width = len(char_data[0]) if char_data else 0
            x_offset += char_width + self.letter_spacing

        # Total width is final offset minus the trailing letter_spacing
        text_width = x_offset - self.letter_spacing if x_offset > 0 else 0

        return pixels, text_width

    def reset(self):
        """Reset scroll position to starting point."""
        self.scroll_offset = 0.0
        self.done = False

    def step(self):
        """
        Advance animation and return visible pixels for current frame.

        Returns:
            list[tuple[int, int, float]]: Pixels as (x, y, brightness) tuples.
        """
        if self.done:
            return []

        visible_pixels = []

        for px, py, brightness in self.text_pixels:
            # Apply scroll transformation and starting position
            display_x = int(self.x_start + px - self.scroll_offset)
            display_y = self.y_pos + py

            # Only include pixels within the viewport
            if 0 <= display_x < self.width and 0 <= display_y < self.height:
                visible_pixels.append((display_x, display_y, brightness))

        # Update scroll position
        self.scroll_offset += self.speed

        # Check if scrolling is complete
        # Text is fully off-screen when scroll_offset > x_start + text_width
        if self.speed > 0 and self.scroll_offset > self.x_start + self.text_width:
            if self.loop:
                self.scroll_offset = 0.0
            else:
                self.done = True

        return visible_pixels

    def is_done(self):
        """Return True if the effect has completed (text scrolled off-screen)."""
        return self.done

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
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).
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
        width=None,
        height=None,
    ):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
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

        w, h = self.width, self.height

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

                b = self.radius - dist + 0.6   # may go >1 or <0
                pixels.append((ix, iy, b))

        return pixels

    def is_done(self):
        return self.done

class PelletRow(BaseEffect):
    """
    Row of evenly spaced pellets that can be consumed.

    Pellets are removed when `eat(x)` is called, typically by a
    Pac-Man style effect.

    Args:
        y: Y position of the pellet row.
        width (int | None): Display width (None = use DisplayConfig).
    """
    def __init__(self, y, width=None):
        self.width = width if width is not None else DisplayConfig.width
        self.y = y
        self.reset()

    def reset(self):
        self.pellets = {x for x in range(0, self.width, 3)}
        self.done = False

    def eat(self, x):
        self.pellets.discard(int(x))

    def step(self):
        return [(x, self.y, 0.8) for x in self.pellets]

    def is_done(self):
        return self.done

class Ghost(BaseEffect):
    """
    Pac-Man style ghost with animated feet.

    Moves horizontally across the display and completes once fully
    off-screen.

    Args:
        x: Starting x position.
        y: Y position.
        x_speed: Horizontal movement speed.
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).
    """
    def __init__(self, x, y, x_speed=0.15, width=None, height=None):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
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

        if self.x >= self.width + 4:
            self.done = True
            return []

        pixels = []
        w, h = self.width, self.height

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

    Note: Assumes all sub-effects (pellets, pacman, ghost) share the same
    display dimensions. Uses pacman's width for exit detection.
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

        if self.pacman.x > self.pacman.width + 4:
            self.done = True

        return pixels

    def is_done(self):
        return self.done

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
