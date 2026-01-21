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
from random import randint, choice
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
        if self.radius > self.max_radius:
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
                char_data = font_data[ord(char)] # pyright: ignore[reportIndexIssue]
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


class TextRevealEffect(BaseEffect):
    """
    Progressively reveals text pixel-by-pixel as another effect passes over it.

    This effect combines a static text display with a "revealer" animation
    (e.g., Comet, ScannerSweep). As the revealer passes over text pixels,
    they light up and stay permanently visible. The revealer continues
    animating after revealing all text.

    Each individual pixel of the text is revealed only when the revealer
    animation touches that specific coordinate. For effects like Comet,
    both the head and tail can reveal pixels as they pass over text.

    Args:
        text (str): Text string to reveal.
        revealer (BaseEffect): Animation that reveals text (e.g., Comet, ScannerSweep).
        x_pos (int): Text x position on display (default: 0).
        y_pos (int): Text y position on display (default: 0).
        font: scrollphathd font object (default: font5x7).
        letter_spacing (int): Pixels between characters (default: 1).
        brightness (float): Text brightness once revealed, 0.0-1.0 (default: 1.0).
        show_revealer (bool): Show revealer animation alongside revealed text (default: True).
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).

    Example:
        # Single comet reveals text
        comet = Comet(0, 0, dx=1, dy=1, tail_length=6, bounce=True)
        text_reveal = TextRevealEffect("HELLO", comet, x_pos=2, y_pos=2)

        # Scanner wipes in text line-by-line
        scanner = ScannerSweep(horizontal=False, speed=1, trail_length=4, bounce=True)
        text_reveal = TextRevealEffect("SCAN", scanner, x_pos=1, y_pos=1)

        # Multiple comets as revealer
        from scrollphathd.fonts import font3x5
        comet1 = Comet(0, 0, dx=1, dy=0.5, tail_length=4, bounce=True)
        comet2 = Comet(16, 6, dx=-0.8, dy=-0.6, tail_length=5, bounce=True)
        multi_revealer = LayeredEffect(
            Layer(comet1, BlendMode.MAX),
            Layer(comet2, BlendMode.MAX)
        )
        text_reveal = TextRevealEffect(
            "MULTI",
            multi_revealer,
            x_pos=4,
            y_pos=2,
            font=font3x5,
            show_revealer=True
        )

    Behavior:
        - Text is static (non-scrolling)
        - Revealer animation loops/bounces continuously
        - Each text pixel reveals on first touch (one-touch reveal)
        - Revealed pixels stay at full configured brightness
        - Revealer brightness does not affect revealed text brightness
    """

    def __init__(
        self,
        text: str,
        revealer,
        x_pos: int = 0,
        y_pos: int = 0,
        font=None,
        letter_spacing: int = 1,
        brightness: float = 1.0,
        show_revealer: bool = True,
        width=None,
        height=None,
    ):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height

        self.text = text
        self.revealer = revealer
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.show_revealer = show_revealer

        # Set default font if none provided
        if font is None:
            try:
                from scrollphathd.fonts import font5x7
                font = font5x7
            except ImportError:
                raise ImportError("scrollphathd.fonts not available")

        # Create static text scroller (speed=0 for non-scrolling)
        self.text_scroller = TextScroller(
            text=text,
            x_start=x_pos,
            y_pos=y_pos,
            speed=0,  # Static text
            font=font,
            letter_spacing=letter_spacing,
            brightness=brightness,
            loop=False,
            width=self.width,
            height=self.height,
        )

        self.reset()

    def reset(self):
        """
        Reset the effect to its initial state.

        Clears all revealed pixels, resets both the text and revealer,
        and pre-computes text pixel coordinates for efficient lookup.
        """
        self.text_scroller.reset()
        self.revealer.reset()

        # Clear revealed pixel tracking
        self.revealed_pixels = set()

        # Pre-compute all text pixel coordinates and brightness values
        # TextScroller with speed=0 produces identical output every frame
        # Store as dict for O(1) lookup: {(x, y): brightness}
        self.all_text_pixels = {
            (x, y): b
            for x, y, b in self.text_scroller.step()
        }

        self.done = False

    def step(self):
        """
        Advance animation one frame and return visible pixels.

        Gets revealer pixels, updates revealed set with newly touched
        text pixels, and returns only revealed text pixels. Optionally
        includes revealer pixels in output.

        Returns:
            list[tuple[int, int, float]]: Pixels as (x, y, brightness) tuples.
        """
        if self.done:
            return []

        # Get revealer pixels this frame (includes head + tail for effects like Comet)
        revealer_pixels = self.revealer.step()
        revealer_coords = {(x, y) for x, y, _ in revealer_pixels}

        # Find which text pixels are touched by revealer this frame
        # Set intersection: only coordinates that exist in BOTH sets
        newly_touched = revealer_coords & self.all_text_pixels.keys()

        # Permanently add to revealed set (accumulates across all frames)
        self.revealed_pixels.update(newly_touched)

        # Build revealed text pixels list
        # Each revealed pixel shows at full text brightness (not revealer brightness)
        revealed_text_pixels = [
            (x, y, brightness)
            for (x, y), brightness in self.all_text_pixels.items()
            if (x, y) in self.revealed_pixels
        ]

        # Merge revealer and revealed text using MAX blending to prevent dimming
        if self.show_revealer:
            # Use dictionary to track max brightness per coordinate
            pixel_dict = {}

            # Add revealed text first
            for x, y, b in revealed_text_pixels:
                pixel_dict[(x, y)] = b

            # Add revealer pixels, keeping max brightness when coordinates overlap
            for x, y, b in revealer_pixels:
                coord = (x, y)
                if coord in pixel_dict:
                    pixel_dict[coord] = max(pixel_dict[coord], b)
                else:
                    pixel_dict[coord] = b

            # Convert back to list
            result = [(x, y, b) for (x, y), b in pixel_dict.items()]
        else:
            result = revealed_text_pixels

        return result

    def is_done(self):
        """
        Return True if the effect has completed.

        This effect never completes - the revealer continues looping
        after all text is revealed.

        Returns:
            bool: Always False (effect loops forever).
        """
        return False


class TextWaveEffect(BaseEffect):
    """
    Animated text with vertical wave oscillation effect.

    Text characters oscillate vertically following a sinusoidal wave pattern
    that propagates horizontally across the display. The wave motion creates
    a smooth, undulating animation while maintaining text readability.

    Supports both static text (with wave animation) and scrolling text
    (combining horizontal scroll with wave motion). The wave is continuous
    and deterministic, making it suitable for recording and layering.

    Args:
        text (str): Text string to display.
        x_start (int | None): Starting x position (None = off-screen right for scrolling).
        y_pos (int): Base vertical position of text (default: 0).
        speed (float): Horizontal scroll speed in pixels/frame (0 = static, default: 1.0).
        wave_speed (float): Wave animation speed (radians per frame, default: 0.08).
            Lower values create slower, more subtle motion.
        wave_amplitude (float): Vertical oscillation range in pixels (default: 1.0).
            Recommended range: 0.5-2.0 for readable text on 7-pixel displays.
        wave_length (float): Wave period - pixels between wave peaks (default: 12.0).
            Longer wavelengths create smoother, more gradual waves.
        font: scrollphathd font object (default: font5x7).
        letter_spacing (int): Pixels between characters (default: 1).
        brightness (float): Text brightness 0.0-1.0 (default: 1.0).
        loop (bool): Restart scrolling when complete (default: False).
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).

    Example:
        # Basic scrolling wave text (uses subtle defaults)
        wave = TextWaveEffect("WAVE")

        # Static waving text
        static = TextWaveEffect("HELLO", x_start=0, speed=0)

        # More pronounced wave for visual effect
        dramatic = TextWaveEffect("DRAMATIC", wave_amplitude=2.0, wave_speed=0.15)

        # Layered with background effect
        from scrollphathd.fonts import font3x5
        scene = LayeredEffect(
            Layer(SparkleField(density=30), BlendMode.MAX),
            Layer(TextWaveEffect("STARS", y_pos=1, font=font3x5), BlendMode.MAX)
        )

    Behavior:
        - Wave propagates continuously across text
        - Each pixel's Y position = base_y + sin(x_position/wavelength + phase) * amplitude
        - Scrolling and wave animation are independent
        - Effect loops indefinitely (is_done() always returns False)
        - Compatible with all blend modes for layering
    """

    def __init__(
        self,
        text: str,
        x_start: int | None = None,
        y_pos: int = 0,
        speed: float = 1.0,
        wave_speed: float = 0.08,
        wave_amplitude: float = 1.0,
        wave_length: float = 12.0,
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
        self.wave_speed = wave_speed
        self.wave_amplitude = wave_amplitude
        self.wave_length = wave_length
        self.letter_spacing = letter_spacing
        self.brightness = brightness
        self.loop = loop

        # Default x_start to off-screen right for scrolling
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

        # Pre-render text to pixels with position metadata
        self.text_pixels, self.text_width = self._render_from_font_data()

        self.reset()

    def _render_from_font_data(self):
        """
        Render text by accessing font character bitmaps.

        Stores pixel data with original offsets for wave transformation.

        Returns:
            tuple: (pixels, text_width) where pixels is list of (x, y, brightness)
                   and text_width is the total width in pixels.
        """
        pixels = []
        x_offset = 0

        # Access the font data dictionary
        font_data = self.font.data if hasattr(self.font, 'data') else self.font

        for char in self.text:
            # Get character bitmap from font
            try:
                char_data = font_data[ord(char)] # pyright: ignore[reportIndexIssue]
            except (KeyError, IndexError):
                # Character not in font, skip it
                continue

            # char_data is a list of rows (horizontal strips of pixels)
            for row_idx, row in enumerate(char_data):
                for col_idx in range(len(row)):
                    if row[col_idx]:  # If pixel is set
                        pixels.append((
                            x_offset + col_idx,
                            row_idx,
                            self.brightness
                        ))

            # Move to next character position
            char_width = len(char_data[0]) if char_data else 0
            x_offset += char_width + self.letter_spacing

        # Total width is final offset minus trailing letter_spacing
        text_width = x_offset - self.letter_spacing if x_offset > 0 else 0

        return pixels, text_width

    def reset(self):
        """Reset scroll position and wave phase to starting point."""
        self.scroll_offset = 0.0
        self.wave_phase = 0.0
        self.done = False

    def step(self):
        """
        Advance animation and return visible pixels with wave transformation.

        Applies sinusoidal vertical offset to each pixel based on its
        horizontal position and current wave phase.

        Returns:
            list[tuple[int, int, float]]: Pixels as (x, y, brightness) tuples.
        """
        if self.done:
            return []

        # Use dictionary to handle multiple pixels mapping to same coordinate
        # (MAX blending for overlapping pixels)
        pixel_dict = {}

        for px, py, brightness in self.text_pixels:
            # Apply horizontal scroll transformation
            display_x = int(self.x_start + px - self.scroll_offset)

            # Calculate wave offset based on display x position
            # Wave equation: y_offset = sin((x / wavelength + phase) * 2π) * amplitude
            wave_offset = math.sin(
                (display_x / self.wave_length + self.wave_phase) * 2 * math.pi
            ) * self.wave_amplitude

            # Apply wave transformation to y position
            display_y = int(round(self.y_pos + py + wave_offset))

            # Only include pixels within viewport
            if 0 <= display_x < self.width and 0 <= display_y < self.height:
                coord = (display_x, display_y)
                # Use MAX blending if multiple pixels map to same coordinate
                if coord in pixel_dict:
                    pixel_dict[coord] = max(pixel_dict[coord], brightness)
                else:
                    pixel_dict[coord] = brightness

        # Update animation state
        self.scroll_offset += self.speed
        self.wave_phase += self.wave_speed

        # Normalize wave_phase to prevent float overflow
        if self.wave_phase > 2 * math.pi:
            self.wave_phase -= 2 * math.pi

        # Check if scrolling is complete
        if self.speed > 0 and self.scroll_offset > self.x_start + self.text_width:
            if self.loop:
                self.scroll_offset = 0.0
            else:
                self.done = True

        # Convert dictionary back to list
        return [(x, y, b) for (x, y), b in pixel_dict.items()]

    def is_done(self):
        """
        Return True if the effect has completed.

        Returns False for looping effects or static text.
        Returns True when scrolling text completes (if loop=False).
        """
        return self.done


class TextRainbowEffect(BaseEffect):
    """
    Animated text with brightness wave shimmer effect.

    Text brightness oscillates following a sinusoidal wave pattern that
    propagates horizontally across the display. The wave motion creates
    a shimmering/pulsing rainbow effect while maintaining text readability.

    Supports both static text (with shimmer animation) and scrolling text
    (combining horizontal scroll with brightness modulation). The wave is
    continuous and deterministic, making it suitable for recording and layering.

    Args:
        text (str): Text string to display.
        x_start (int | None): Starting x position (None = off-screen right for scrolling).
        y_pos (int): Vertical position of text (default: 0).
        speed (float): Horizontal scroll speed in pixels/frame (0 = static, default: 1.0).
        wave_speed (float): Rainbow wave animation speed (radians per frame, default: 0.15).
            Lower values create slower, more subtle shimmer.
        wave_length (float): Wave period - pixels between brightness peaks (default: 8.0).
            Longer wavelengths create smoother, more gradual brightness changes.
        min_brightness (float): Minimum brightness value (default: 0.6).
            Recommended range: 0.5-0.8 for subtle, readable shimmer.
            Lower values create more dramatic effect but reduce readability.
        max_brightness (float): Maximum brightness value (default: 1.0).
            Should be greater than min_brightness.
        font: scrollphathd font object (default: font5x7).
        letter_spacing (int): Pixels between characters (default: 1).
        loop (bool): Restart scrolling when complete (default: False).
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).

    Example:
        # Basic scrolling rainbow text (subtle shimmer)
        rainbow = TextRainbowEffect("PARTY")

        # Static shimmering text
        shimmer = TextRainbowEffect("HELLO", x_start=0, speed=0)

        # More dramatic shimmer effect
        dramatic = TextRainbowEffect("DISCO", wave_speed=0.25, min_brightness=0.3)

        # Layered with background effect
        from scrollphathd.fonts import font3x5
        scene = LayeredEffect(
            Layer(SparkleField(density=20), BlendMode.ADD),
            Layer(TextRainbowEffect("STARS", y_pos=1, font=font3x5), BlendMode.MAX)
        )

    Behavior:
        - Brightness wave propagates continuously across text
        - Each pixel's brightness = min + (max - min) * (sin(x/wavelength + phase) + 1) / 2
        - Scrolling and wave animation are independent
        - Effect loops indefinitely (is_done() always returns False for looping)
        - Compatible with all blend modes for layering
    """

    def __init__(
        self,
        text: str,
        x_start: int | None = None,
        y_pos: int = 0,
        speed: float = 1.0,
        wave_speed: float = 0.15,
        wave_length: float = 8.0,
        min_brightness: float = 0.6,
        max_brightness: float = 1.0,
        font=None,
        letter_spacing: int = 1,
        loop: bool = False,
        width=None,
        height=None,
    ):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height

        self.text = text
        self.y_pos = y_pos
        self.speed = speed
        self.wave_speed = wave_speed
        self.wave_length = wave_length
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.letter_spacing = letter_spacing
        self.loop = loop

        # Default x_start to off-screen right for scrolling
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

        # Pre-render text to pixels (at max brightness - will be modulated)
        self.text_pixels, self.text_width = self._render_from_font_data()

        self.reset()

    def _render_from_font_data(self):
        """
        Render text by accessing font character bitmaps.

        Renders at maximum brightness - brightness will be modulated
        per frame based on wave function.

        Returns:
            tuple: (pixels, text_width) where pixels is list of (x, y, brightness)
                   and text_width is the total width in pixels.
        """
        pixels = []
        x_offset = 0

        # Access the font data dictionary
        font_data = self.font.data if hasattr(self.font, 'data') else self.font

        for char in self.text:
            # Get character bitmap from font
            try:
                char_data = font_data[ord(char)] # pyright: ignore[reportIndexIssue]
            except (KeyError, IndexError):
                # Character not in font, skip it
                continue

            # char_data is a list of rows (horizontal strips of pixels)
            for row_idx, row in enumerate(char_data):
                for col_idx in range(len(row)):
                    if row[col_idx]:  # If pixel is set
                        # Store at max brightness (will be modulated in step())
                        pixels.append((
                            x_offset + col_idx,
                            row_idx,
                            self.max_brightness
                        ))

            # Move to next character position
            char_width = len(char_data[0]) if char_data else 0
            x_offset += char_width + self.letter_spacing

        # Total width is final offset minus trailing letter_spacing
        text_width = x_offset - self.letter_spacing if x_offset > 0 else 0

        return pixels, text_width

    def reset(self):
        """Reset scroll position and wave phase to starting point."""
        self.scroll_offset = 0.0
        self.wave_phase = 0.0
        self.done = False

    def step(self):
        """
        Advance animation and return visible pixels with brightness modulation.

        Applies sinusoidal brightness wave to each pixel based on its
        horizontal position and current wave phase.

        Returns:
            list[tuple[int, int, float]]: Pixels as (x, y, brightness) tuples.
        """
        if self.done:
            return []

        visible_pixels = []

        for px, py, base_brightness in self.text_pixels:
            # Apply horizontal scroll transformation
            display_x = int(self.x_start + px - self.scroll_offset)

            # Calculate brightness multiplier based on wave function
            # Wave ranges from 0.0 to 1.0
            wave_value = (math.sin(
                (display_x / self.wave_length + self.wave_phase) * 2 * math.pi
            ) + 1.0) / 2.0

            # Map wave value to brightness range
            brightness = self.min_brightness + (self.max_brightness - self.min_brightness) * wave_value

            # Apply to y position (no wave transformation on position)
            display_y = self.y_pos + py

            # Only include pixels within viewport
            if 0 <= display_x < self.width and 0 <= display_y < self.height:
                visible_pixels.append((display_x, display_y, brightness))

        # Update animation state
        self.scroll_offset += self.speed
        self.wave_phase += self.wave_speed

        # Normalize wave_phase to prevent float overflow
        if self.wave_phase > 2 * math.pi:
            self.wave_phase -= 2 * math.pi

        # Check if scrolling is complete
        if self.speed > 0 and self.scroll_offset > self.x_start + self.text_width:
            if self.loop:
                self.scroll_offset = 0.0
            else:
                self.done = True

        return visible_pixels

    def is_done(self):
        """
        Return True if the effect has completed.

        Returns False for looping effects or static text.
        Returns True when scrolling text completes (if loop=False).
        """
        return self.done


class TextFadeEffect(BaseEffect):
    """
    Text that gradually fades in, holds at full brightness, then fades out.

    Text brightness transitions through three phases: fade in (gradual brightness
    increase), hold (constant at peak brightness), and fade out (gradual decrease).
    The entire text fades uniformly as a cohesive unit, maintaining readability
    throughout the animation.

    Supports both static text (with fade animation) and scrolling text (combining
    horizontal scroll with fade transitions). The fade is deterministic and frame-based,
    making it suitable for recording and layering.

    Args:
        text (str): Text string to display.
        x_start (int | None): Starting x position (None = off-screen right for scrolling).
        y_pos (int): Vertical position of text (default: 0).
        speed (float): Horizontal scroll speed in pixels/frame (0 = static, default: 1.0).
        fade_in_frames (int): Number of frames for fade in phase (default: 30).
        fade_out_frames (int): Number of frames for fade out phase (default: 30).
        hold_frames (int): Number of frames to hold at full brightness (default: 40).
        min_brightness (float): Starting/ending brightness 0.0-1.0 (default: 0.0).
        max_brightness (float): Peak brightness 0.0-1.0 (default: 1.0).
        font: scrollphathd font object (default: font5x7).
        letter_spacing (int): Pixels between characters (default: 1).
        loop (bool): Restart fade cycle when complete (default: False).
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).

    Example:
        # Basic static fade (fade in, hold, fade out)
        fade = TextFadeEffect("HELLO", x_start=0, speed=0)

        # Scrolling text with fade
        scroll_fade = TextFadeEffect("WELCOME", speed=0.5)

        # Quick fade in, long hold, slow fade out
        custom = TextFadeEffect(
            "INFO",
            x_start=2,
            speed=0,
            fade_in_frames=15,
            hold_frames=60,
            fade_out_frames=45
        )

        # Layered with background effect
        from scrollphathd.fonts import font3x5
        scene = LayeredEffect(
            Layer(SparkleField(density=20), BlendMode.ADD),
            Layer(TextFadeEffect("STARS", y_pos=1, font=font3x5, loop=True), BlendMode.MAX)
        )

    Behavior:
        - All text pixels fade uniformly (entire text as one unit)
        - Fade phases: IN → HOLD → OUT (linear interpolation)
        - Scrolling and fade animation are independent
        - Effect completes when both fade cycle and scroll (if applicable) finish
        - Loop restarts both fade cycle and scroll position
        - Compatible with all blend modes for layering
    """

    def __init__(
        self,
        text: str,
        x_start: int | None = None,
        y_pos: int = 0,
        speed: float = 1.0,
        fade_in_frames: int = 30,
        fade_out_frames: int = 30,
        hold_frames: int = 40,
        min_brightness: float = 0.0,
        max_brightness: float = 1.0,
        font=None,
        letter_spacing: int = 1,
        loop: bool = False,
        width=None,
        height=None,
    ):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height

        self.text = text
        self.y_pos = y_pos
        self.speed = speed
        self.fade_in_frames = max(1, fade_in_frames)  # Prevent division by zero
        self.fade_out_frames = max(1, fade_out_frames)
        self.hold_frames = hold_frames
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.letter_spacing = letter_spacing
        self.loop = loop

        # Default x_start to off-screen right for scrolling
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

        # Pre-render text to pixels (at max brightness - will be modulated)
        self.text_pixels, self.text_width = self._render_from_font_data()

        self.reset()

    def _render_from_font_data(self):
        """
        Render text by accessing font character bitmaps.

        Renders at maximum brightness - brightness will be modulated
        per frame based on fade phase.

        Returns:
            tuple: (pixels, text_width) where pixels is list of (x, y, brightness)
                   and text_width is the total width in pixels.
        """
        pixels = []
        x_offset = 0

        # Access the font data dictionary
        font_data = self.font.data if hasattr(self.font, 'data') else self.font

        for char in self.text:
            # Get character bitmap from font
            try:
                char_data = font_data[ord(char)] # pyright: ignore[reportIndexIssue]
            except (KeyError, IndexError):
                # Character not in font, skip it
                continue

            # char_data is a list of rows (horizontal strips of pixels)
            for row_idx, row in enumerate(char_data):
                for col_idx in range(len(row)):
                    if row[col_idx]:  # If pixel is set
                        # Store at max brightness (will be modulated in step())
                        pixels.append((
                            x_offset + col_idx,
                            row_idx,
                            self.max_brightness
                        ))

            # Move to next character position
            char_width = len(char_data[0]) if char_data else 0
            x_offset += char_width + self.letter_spacing

        # Total width is final offset minus trailing letter_spacing
        text_width = x_offset - self.letter_spacing if x_offset > 0 else 0

        return pixels, text_width

    def _calculate_current_brightness(self):
        """
        Calculate brightness based on current position in fade cycle.

        Uses piecewise linear interpolation across three phases:
        1. Fade in: Linear increase from min to max
        2. Hold: Constant at max brightness
        3. Fade out: Linear decrease from max to min

        Returns:
            float: Current brightness value (0.0-1.0 range).
        """
        total_fade_frames = self.fade_in_frames + self.hold_frames + self.fade_out_frames

        if self.fade_frame_count < self.fade_in_frames:
            # Fade in phase: Linear interpolation from min to max
            progress = self.fade_frame_count / self.fade_in_frames
            return self.min_brightness + (self.max_brightness - self.min_brightness) * progress

        elif self.fade_frame_count < self.fade_in_frames + self.hold_frames:
            # Hold phase: Constant at max brightness
            return self.max_brightness

        elif self.fade_frame_count < total_fade_frames:
            # Fade out phase: Linear interpolation from max to min
            fade_out_start = self.fade_in_frames + self.hold_frames
            progress = (self.fade_frame_count - fade_out_start) / self.fade_out_frames
            return self.max_brightness - (self.max_brightness - self.min_brightness) * progress

        else:
            # Fade cycle complete
            return self.min_brightness

    def reset(self):
        """Reset scroll position and fade cycle to starting point."""
        self.scroll_offset = 0.0
        self.fade_frame_count = 0
        self.done = False

    def step(self):
        """
        Advance animation and return visible pixels with fade brightness applied.

        Applies uniform brightness (based on fade phase) to all text pixels,
        then applies scroll transformation and viewport culling.

        Returns:
            list[tuple[int, int, float]]: Pixels as (x, y, brightness) tuples.
        """
        if self.done:
            return []

        # Calculate current brightness for entire text
        current_brightness = self._calculate_current_brightness()

        visible_pixels = []

        for px, py, base_brightness in self.text_pixels:
            # Apply horizontal scroll transformation
            display_x = int(self.x_start + px - self.scroll_offset)
            display_y = self.y_pos + py

            # Only include pixels within viewport
            if 0 <= display_x < self.width and 0 <= display_y < self.height:
                # Apply fade brightness (uniform across all pixels)
                visible_pixels.append((display_x, display_y, current_brightness))

        # Update animation state
        self.scroll_offset += self.speed
        self.fade_frame_count += 1

        # Calculate fade cycle completion
        total_fade_frames = self.fade_in_frames + self.hold_frames + self.fade_out_frames
        fade_complete = self.fade_frame_count >= total_fade_frames

        # Calculate scroll completion (if scrolling)
        scroll_complete = True  # Assume complete if static (speed == 0)
        if self.speed > 0:
            scroll_complete = self.scroll_offset > self.x_start + self.text_width

        # Check overall completion
        if fade_complete and scroll_complete:
            if self.loop:
                # Reset both fade and scroll for looping
                self.fade_frame_count = 0
                self.scroll_offset = 0.0
            else:
                self.done = True

        return visible_pixels

    def is_done(self):
        """
        Return True if the effect has completed.

        Returns False for looping effects.
        Returns True when both fade cycle and scroll (if applicable) complete.
        """
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
# Tetris Effects
###------------------------------------------------------------------------###

# Piece shape definitions: list of (dx, dy) offsets from anchor point
TETRIS_SHAPES = {
    'I': [(0, 0), (0, 1), (0, 2)],           # Vertical line (3 tall)
    'O': [(0, 0), (1, 0), (0, 1), (1, 1)],   # Square (2x2)
    'L': [(0, 0), (0, 1), (1, 1)],           # L-shape
    'T': [(0, 0), (1, 0), (2, 0), (1, 1)],   # T-shape (3 wide)
    'S': [(0, 0), (1, 0)],                    # Single/small (2 wide)
}

# Brightness values for each shape type
TETRIS_BRIGHTNESS = {
    'I': 1.0,
    'O': 0.9,
    'L': 0.8,
    'T': 0.85,
    'S': 0.7,
}

# Fixed sequence of pieces (shape_key, x_position)
# x_position is the exact column where the piece spawns
# This sequence is designed to fill a complete row (17 pixels wide)
# First 9 pieces fill bottom row: S(0-1) + S(2-3) + S(4-5) + S(6-7) + S(8-9) + S(10-11) + S(12-13) + S(14-15) + I(16)
# Then continue with varied pieces
TETRIS_SEQUENCE = [
    ('S', 0),    # Fills columns 0-1
    ('L', 4),    # Fills columns 4-5
    ('S', 6),    # Fills columns 6-7
    ('O', 8),    # Fills columns 8-9
    ('S', 10),   # Fills columns 10-11
    ('L', 12),   # Fills columns 12-13
    ('O', 2),    # Fills columns 2-3
    ('S', 14),   # Fills columns 14-15
    ('I', 16),   # Fills column 16 - completes the row!
    # After line clear, continue with more interesting pieces
    ('T', 2),
    ('O', 7),
    ('L', 12),
    ('T', 5),
    ('O', 0),
    ('L', 14),
    ('L', 4),    # Fills columns 4-5
    ('S', 6),    # Fills columns 6-7
    ('O', 8),    # Fills columns 8-9
    ('S', 10),   # Fills columns 10-11
    ('L', 12),   # Fills columns 12-13
]


class TetrisPiece(BaseEffect):
    """
    A falling Tetris piece that drops from top to bottom.

    Renders a tetromino shape that falls at a configurable speed until
    it reaches a target y position (typically set by collision detection
    in TetrisScene).

    Args:
        x (int): Horizontal start position (left edge of piece).
        shape (list): List of (dx, dy) offsets defining piece shape.
        brightness (float): Piece brightness 0.0-1.0 (default: 1.0).
        fall_speed (float): Pixels per frame to fall (default: 0.2).
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).
    """

    def __init__(self, x, shape, brightness=1.0, fall_speed=0.2,
                 width=None, height=None):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
        self.start_x = x
        self.shape = shape
        self.brightness = brightness
        self.fall_speed = fall_speed
        self.target_y: int | None = None  # Set externally when landing position known
        self.reset()

    def reset(self):
        """Reset piece to starting position."""
        self.x = self.start_x
        self.y = -self._get_shape_height()  # Start above display
        self.landed = False
        self.done = False

    def _get_shape_height(self):
        """Return the height of this piece shape."""
        if not self.shape:
            return 1
        return max(dy for _, dy in self.shape) + 1

    def _get_shape_width(self):
        """Return the width of this piece shape."""
        if not self.shape:
            return 1
        return max(dx for dx, _ in self.shape) + 1

    def get_pixels_at_y(self, y_pos):
        """Return pixel coordinates if piece were at given y position."""
        pixels = []
        for dx, dy in self.shape:
            px = self.x + dx
            py = int(y_pos) + dy
            if 0 <= px < self.width and 0 <= py < self.height:
                pixels.append((px, py))
        return pixels

    def step(self):
        """Advance one frame, moving piece down."""
        if self.done:
            return []

        # Move down
        self.y += self.fall_speed

        # Check if landed at target
        if self.target_y is not None and self.y >= self.target_y:
            self.y = self.target_y
            self.landed = True
            self.done = True

        # Render current position
        pixels = []
        for dx, dy in self.shape:
            px = self.x + dx
            py = int(self.y) + dy
            if 0 <= px < self.width and 0 <= py < self.height:
                pixels.append((px, py, self.brightness))

        return pixels

    def is_done(self):
        """Return True when piece has landed."""
        return self.done


class TetrisBoard(BaseEffect):
    """
    Tracks landed Tetris pieces and handles line clearing.

    Maintains a grid of landed blocks, detects complete lines,
    plays a blink animation, then removes cleared lines and
    drops rows above. Also handles full-board blink and clear
    when the board becomes full.

    Args:
        blink_frames (int): Frames to blink before clearing lines (default: 8).
        full_blink_frames (int): Frames to blink when board is full (default: 12).
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).
    """

    def __init__(self, blink_frames=8, full_blink_frames=12, width=None, height=None):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
        self.blink_frames = blink_frames
        self.full_blink_frames = full_blink_frames
        self.reset()

    def reset(self):
        """Clear the board."""
        self.grid = {}  # (x, y) -> brightness
        self.clearing_lines = []  # y-values being cleared
        self.blink_phase = 0
        self.done = False
        # Full-board clear state
        self.full_board_clearing = False
        self.full_blink_phase = 0

    def add_piece(self, pixels, brightness):
        """
        Add landed piece pixels to the board.

        Args:
            pixels: List of (x, y) coordinates.
            brightness: Brightness value for these pixels.
        """
        for x, y in pixels:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[(x, y)] = brightness

    def check_lines(self):
        """Check for and mark complete lines for clearing.

        Note: Row 0 (top row) is never cleared during normal gameplay.
        This allows columns to fill to the top and block new pieces.
        The top row is only cleared during full-board reset.
        """
        # Start from y=1 to skip top row - top row stays filled to block columns
        for y in range(1, self.height):
            filled = sum(1 for x in range(self.width) if (x, y) in self.grid)
            if filled == self.width and y not in self.clearing_lines:
                self.clearing_lines.append(y)
                self.blink_phase = 0

    def _clear_lines(self):
        """Remove cleared lines and drop rows above."""
        if not self.clearing_lines:
            return

        # Sort lines from bottom to top for proper shifting
        lines_to_clear = sorted(self.clearing_lines, reverse=True)

        for clear_y in lines_to_clear:
            # Remove the cleared line
            for x in range(self.width):
                self.grid.pop((x, clear_y), None)

            # Drop all rows above this line down by 1
            new_grid = {}
            for (x, y), brightness in self.grid.items():
                if y < clear_y:
                    # Row above cleared line - drop it down
                    new_grid[(x, y + 1)] = brightness
                else:
                    # Row below cleared line - keep in place
                    new_grid[(x, y)] = brightness
            self.grid = new_grid

        self.clearing_lines = []

    def is_clearing(self):
        """Return True if currently in line-clear animation."""
        return len(self.clearing_lines) > 0

    def is_full(self, piece_pixels):
        """
        Check if the board is full (piece cannot land safely).

        Args:
            piece_pixels: List of (x, y) coordinates at y=0 position.

        Returns:
            True if piece would land at y < 0 (no room to spawn).
        """
        landing_y = self.get_landing_y(piece_pixels)
        return landing_y < 0

    def get_blocked_columns(self):
        """
        Return set of columns that have a block at the top row (y=0).

        These columns are considered "full" and should not receive new pieces.

        Returns:
            set[int]: Column indices that are blocked.
        """
        blocked = set()
        for x in range(self.width):
            if (x, 0) in self.grid:
                blocked.add(x)
        return blocked

    def all_columns_blocked(self):
        """
        Check if all columns have blocks at the top row.

        Returns:
            True if every column has at least one block at y=0.
        """
        return len(self.get_blocked_columns()) >= self.width

    def is_full_clearing(self):
        """Return True if currently in full-board blink animation."""
        return self.full_board_clearing

    def start_full_clear(self):
        """Begin full-board blink animation."""
        self.full_board_clearing = True
        self.full_blink_phase = 0

    def clear_board(self):
        """Reset the entire board after full-board clear."""
        self.grid.clear()
        self.full_board_clearing = False
        self.full_blink_phase = 0

    def get_landing_y(self, piece_pixels):
        """
        Calculate the y position where a piece would land.

        Args:
            piece_pixels: List of (x, y) coordinates at y=0.

        Returns:
            The y offset where the piece would stop (bottom or collision).
        """
        for test_y in range(self.height + 3):  # +3 for pieces starting above
            for px, py_offset in piece_pixels:
                py = test_y + py_offset
                # Check bottom boundary
                if py >= self.height:
                    return test_y - 1
                # Check collision with existing blocks
                if (px, py) in self.grid:
                    return test_y - 1
        return self.height - 1

    def step(self):
        """Render board and handle line-clear or full-board blink animation."""
        pixels = []

        # Handle full-board blink animation (takes priority)
        if self.full_board_clearing:
            self.full_blink_phase += 1
            blink_on = (self.full_blink_phase // 2) % 2 == 0

            # Blink all pixels on the board
            if blink_on:
                for (x, y), brightness in self.grid.items():
                    pixels.append((x, y, 1.0))

            # Check if full-board blink animation complete
            if self.full_blink_phase >= self.full_blink_frames:
                self.clear_board()

            return pixels

        # Handle blink animation for clearing lines
        if self.clearing_lines:
            self.blink_phase += 1
            blink_on = (self.blink_phase // 2) % 2 == 0

            # Render non-clearing pixels normally
            for (x, y), brightness in self.grid.items():
                if y not in self.clearing_lines:
                    pixels.append((x, y, brightness))
                elif blink_on:
                    # Clearing line - blink at full brightness
                    pixels.append((x, y, 1.0))

            # Check if blink animation complete
            if self.blink_phase >= self.blink_frames:
                self._clear_lines()
        else:
            # Normal render - all pixels
            for (x, y), brightness in self.grid.items():
                pixels.append((x, y, brightness))

        return pixels

    def is_done(self):
        """Board never marks itself as done."""
        return False


class TetrisScene(BaseEffect):
    """
    Complete Tetris scene with falling pieces and line clears.

    Orchestrates piece spawning, falling, landing, and line clearing.
    The first cycle uses a fixed piece sequence designed to demonstrate
    line clears. After the board fills and clears, subsequent cycles use
    randomized pieces for variety. Speed increases as more pieces land.

    In loop mode (default), pieces continue falling and avoid columns that
    have blocks at the top row. When a column fills to the top, new pieces
    are placed in remaining open columns. Only when ALL columns are blocked
    does the board blink and clear to start again with random pieces.

    Args:
        num_pieces (int | None): Total pieces before scene ends. None = unlimited (loop mode).
        base_fall_speed (float): Starting fall speed (default: 0.15).
        speed_increment (float): Speed increase per landed piece (default: 0.02).
        blink_frames (int): Frames for line-clear blink (default: 8).
        full_blink_frames (int): Frames for full-board blink (default: 12).
        loop (bool): If True, loops forever when board fills (default: True).
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).

    Example:
        # Continuous looping Tetris (default)
        scene = TetrisScene()
        runner = EffectRunner(scene, fps=25)
        runner.run()

        # Fixed number of pieces (no loop)
        scene = TetrisScene(num_pieces=20, loop=False)
    """

    def __init__(self, num_pieces=None, base_fall_speed=0.15,
                 speed_increment=0.02, blink_frames=8, full_blink_frames=12,
                 loop=True, width=None, height=None):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
        self.num_pieces = num_pieces
        self.base_fall_speed = base_fall_speed
        self.speed_increment = speed_increment
        self.blink_frames = blink_frames
        self.full_blink_frames = full_blink_frames
        self.loop = loop
        self.reset()

    def reset(self):
        """Reset scene to initial state."""
        self.board = TetrisBoard(
            blink_frames=self.blink_frames,
            full_blink_frames=self.full_blink_frames,
            width=self.width,
            height=self.height
        )
        self.current_piece = None
        self.pieces_dropped = 0
        self.sequence_index = 0
        self.done = False
        self.use_random = False  # Start with sequence, switch to random after first loop
        self._next_piece_data = None  # Cache for next piece (shape_key, x_pos)
        self._spawn_next_piece()

    def _get_current_speed(self):
        """Calculate current fall speed based on pieces dropped."""
        return self.base_fall_speed + (self.pieces_dropped * self.speed_increment)

    def _generate_random_piece(self):
        """
        Generate a random piece with random x position that can land safely.

        Selects a random shape and finds a valid x position where the piece
        would land at y >= 1 (has room to fall at least one row before landing).
        This ensures columns continue filling until truly full.

        Returns:
            tuple: (shape_key, x_pos) or None if no valid position exists.
        """
        from random import shuffle

        # Try multiple shapes to find one that fits
        shape_keys = list(TETRIS_SHAPES.keys())
        shuffle(shape_keys)

        for shape_key in shape_keys:
            shape = TETRIS_SHAPES[shape_key]
            piece_width = max(dx for dx, _ in shape) + 1

            # Find valid x positions where piece can land at y >= 1
            valid_positions = []
            for x_pos in range(self.width - piece_width + 1):
                # Calculate landing position for this piece at this x
                piece_pixels = [(x_pos + dx, dy) for dx, dy in shape]
                landing_y = self.board.get_landing_y(piece_pixels)

                # Valid if piece can land on the board (y >= 0)
                if landing_y >= 0:
                    valid_positions.append(x_pos)

            if valid_positions:
                x_pos = choice(valid_positions)
                return (shape_key, x_pos)

        # No valid position found for any piece - board is full
        return None

    def _get_next_piece_data(self):
        """Get the next piece data, using cache or generating new.

        In sequence mode, returns the next piece from TETRIS_SEQUENCE but
        validates that it can land. If the sequence piece can't land, falls
        back to _generate_random_piece() which tries all shapes/positions.

        Returns:
            tuple: (shape_key, x_pos) or None if no valid position exists.
        """
        if self._next_piece_data is not None:
            return self._next_piece_data

        if self.use_random:
            self._next_piece_data = self._generate_random_piece()
        else:
            # Get sequence piece but validate it can land
            shape_key, x_pos = TETRIS_SEQUENCE[self.sequence_index % len(TETRIS_SEQUENCE)]
            shape = TETRIS_SHAPES[shape_key]
            piece_width = max(dx for dx, _ in shape) + 1
            max_x = self.width - piece_width
            x = min(x_pos, max_x)

            # Check if this piece can land at this position
            piece_pixels = [(x + dx, dy) for dx, dy in shape]
            landing_y = self.board.get_landing_y(piece_pixels)

            if landing_y >= 0:
                # Sequence piece can land
                self._next_piece_data = (shape_key, x_pos)
            else:
                # Sequence piece can't land - try to find ANY valid position
                self._next_piece_data = self._generate_random_piece()

        return self._next_piece_data

    def _spawn_next_piece(self):
        """Spawn the next piece from the sequence or randomly."""
        # Check piece limit (None = unlimited)
        if self.num_pieces is not None and self.pieces_dropped >= self.num_pieces:
            self.current_piece = None
            return

        # Get piece data (cached or new)
        piece_data = self._get_next_piece_data()
        self._next_piece_data = None  # Clear cache after use

        # No valid piece available (all columns blocked)
        if piece_data is None:
            self.current_piece = None
            return

        shape_key, x_pos = piece_data
        self.sequence_index += 1

        shape = TETRIS_SHAPES[shape_key]
        brightness = TETRIS_BRIGHTNESS[shape_key]

        # Clamp x position to valid range
        piece_width = max(dx for dx, _ in shape) + 1
        max_x = self.width - piece_width
        x = min(x_pos, max_x)

        # Create piece with current speed
        self.current_piece = TetrisPiece(
            x=x,
            shape=shape,
            brightness=brightness,
            fall_speed=self._get_current_speed(),
            width=self.width,
            height=self.height
        )

        # Calculate where it will land
        shape_offsets = [(dx, dy) for dx, dy in shape]
        landing_y = self.board.get_landing_y(
            [(x + dx, dy) for dx, dy in shape_offsets]
        )
        self.current_piece.target_y = landing_y

    def _can_spawn_more(self):
        """Check if more pieces can be spawned based on num_pieces limit."""
        if self.num_pieces is None:
            return True  # Unlimited
        return self.pieces_dropped < self.num_pieces

    def _get_next_piece_pixels(self):
        """
        Get the pixel positions for the next piece at y=0 (for collision check).

        Returns:
            list or None: Pixel positions, or None if no valid piece available.
        """
        piece_data = self._get_next_piece_data()
        if piece_data is None:
            return None

        shape_key, x_pos = piece_data
        shape = TETRIS_SHAPES[shape_key]
        piece_width = max(dx for dx, _ in shape) + 1
        max_x = self.width - piece_width
        x = min(x_pos, max_x)
        return [(x + dx, dy) for dx, dy in shape]

    def step(self):
        """Advance one frame of the scene."""
        if self.done:
            return []

        pixels = []

        # If board is doing full-board clear, wait for animation
        if self.board.is_full_clearing():
            pixels += self.board.step()
            # After full clear completes, reset for next round if looping
            if not self.board.is_full_clearing() and self.loop:
                self.pieces_dropped = 0
                self.sequence_index = 0
                self.use_random = True  # Use random pieces after first loop
                self._next_piece_data = None  # Clear cached piece data
                self._spawn_next_piece()
            return pixels

        # If board is clearing lines, wait for animation
        if self.board.is_clearing():
            pixels += self.board.step()
            return pixels

        # Spawn new piece if needed (after line clear or at start)
        if self.current_piece is None and self._can_spawn_more():
            # Check if there's a valid spawn position
            next_piece_pixels = self._get_next_piece_pixels()
            if next_piece_pixels is None:
                # No valid position - board is full, start blink and clear
                if self.loop:
                    self.board.start_full_clear()
                    pixels += self.board.step()
                    return pixels
                else:
                    # Not looping - mark as done
                    self.done = True
                    pixels += self.board.step()
                    return pixels
            else:
                self._spawn_next_piece()

        # Update current piece
        if self.current_piece is not None:
            piece_pixels = self.current_piece.step()
            pixels += piece_pixels

            # Check if piece landed
            if self.current_piece.landed:
                # Add to board
                landed_coords = self.current_piece.get_pixels_at_y(
                    self.current_piece.target_y
                )
                self.board.add_piece(landed_coords, self.current_piece.brightness)
                self.pieces_dropped += 1

                # Check for line clears
                self.board.check_lines()

                # Clear current piece (will spawn next frame unless clearing)
                self.current_piece = None

        # Render board
        pixels += self.board.step()

        # Check completion (only when not looping and have piece limit)
        if not self.loop and self.num_pieces is not None:
            if self.current_piece is None and not self.board.is_clearing():
                if self.pieces_dropped >= self.num_pieces:
                    self.done = True

        return pixels

    def is_done(self):
        """Return True when scene is complete (never true in loop mode)."""
        return self.done


###------------------------------------------------------------------------###
# Snake Effects
###------------------------------------------------------------------------###

class SnakeScene(BaseEffect):
    """
    Classic Snake game scene with smart AI pathfinding.

    A snake moves around the display eating food pellets and growing longer.
    The AI automatically navigates toward food while avoiding self-collision.
    When the snake fills the screen or traps itself, it blinks and restarts.

    Args:
        start_length (int): Initial snake length (default: 3).
        speed (float): Movement speed in pixels per frame (default: 0.25).
        loop (bool): If True, restarts after game over (default: True).
        blink_frames (int): Frames to blink on game over (default: 16).
        width (int | None): Display width (None = use DisplayConfig).
        height (int | None): Display height (None = use DisplayConfig).

    Example:
        # Basic snake scene
        scene = SnakeScene(start_length=3, speed=0.3, loop=True)
        runner = EffectRunner(scene, fps=20)
        runner.run(frames=500)

        # Fast snake with sparkle background
        scene = LayeredEffect(
            Layer(SparkleField(density=10), BlendMode.ADD),
            Layer(SnakeScene(speed=0.5), BlendMode.MAX)
        )
    """

    # Direction constants: (dx, dy)
    DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # RIGHT, DOWN, LEFT, UP

    def __init__(self, start_length=3, speed=0.25, loop=True, blink_frames=16,
                 width=None, height=None):
        self.width = width if width is not None else DisplayConfig.width
        self.height = height if height is not None else DisplayConfig.height
        self.start_length = start_length
        self.speed = speed
        self.loop = loop
        self.blink_frames = blink_frames
        self.reset()

    def reset(self):
        """Reset the scene to initial state."""
        # Snake starts in center-left, moving right
        start_x = self.width // 4
        start_y = self.height // 2

        self.head_x = start_x
        self.head_y = start_y
        self.direction = 0  # Start moving RIGHT

        # Body is a deque of (x, y) positions (head is NOT in body)
        # Initialize body behind the head
        self.body = collections.deque()
        for i in range(1, self.start_length):
            self.body.append((start_x - i, start_y))

        # Pre-generate food positions for determinism
        self.food_positions = [
            (randint(0, self.width - 1), randint(0, self.height - 1))
            for _ in range(100)
        ]
        self.food_index = 0

        # Spawn first food (avoiding snake)
        self._spawn_food()

        # Movement accumulator for sub-pixel movement
        self.move_accumulator = 0.0

        # Step counter for food pulsing
        self.step_count = 0

        # Game state
        self.game_over = False
        self.blink_counter = 0
        self.blink_on = True
        self.done = False

    def _get_snake_positions(self):
        """Return set of all positions occupied by the snake."""
        positions = {(self.head_x, self.head_y)}
        positions.update(self.body)
        return positions

    def _spawn_food(self):
        """Spawn food at next pre-generated position, avoiding snake."""
        snake_positions = self._get_snake_positions()

        # Try positions from pre-generated list
        attempts = 0
        while attempts < len(self.food_positions):
            pos = self.food_positions[self.food_index % len(self.food_positions)]
            self.food_index += 1
            attempts += 1

            if pos not in snake_positions:
                self.food_x, self.food_y = pos
                return

        # Fallback: find any empty position
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in snake_positions:
                    self.food_x, self.food_y = x, y
                    return

        # No empty position (snake fills entire screen)
        self.food_x, self.food_y = -1, -1

    def _manhattan_distance(self, x1, y1, x2, y2):
        """Calculate Manhattan distance with wrap-around consideration."""
        # Direct distance
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        # Wrap-around distance
        dx_wrap = self.width - dx
        dy_wrap = self.height - dy

        return min(dx, dx_wrap) + min(dy, dy_wrap)

    def _choose_direction(self):
        """
        Choose the best direction toward food while avoiding collision.

        Uses a simple greedy approach: prefer directions that reduce distance
        to food, but avoid directions that would cause self-collision.
        """
        snake_positions = self._get_snake_positions()

        # Remove tail from collision check (it will move)
        if self.body:
            tail = self.body[-1]
            snake_positions.discard(tail)

        best_direction = self.direction
        best_distance = float('inf')
        safe_directions = []

        for dir_idx, (dx, dy) in enumerate(self.DIRECTIONS):
            # Calculate new head position
            new_x = (self.head_x + dx) % self.width
            new_y = (self.head_y + dy) % self.height

            # Skip if this would cause collision
            if (new_x, new_y) in snake_positions:
                continue

            safe_directions.append(dir_idx)

            # Calculate distance to food
            distance = self._manhattan_distance(new_x, new_y, self.food_x, self.food_y)

            if distance < best_distance:
                best_distance = distance
                best_direction = dir_idx

        # If no direction reduces distance but we have safe directions, pick one
        if best_distance == float('inf') and safe_directions:
            # Prefer continuing in current direction if safe
            if self.direction in safe_directions:
                best_direction = self.direction
            else:
                best_direction = safe_directions[0]

        return best_direction

    def _move_snake(self):
        """Move the snake one step in the current direction."""
        # Choose new direction (smart AI)
        self.direction = self._choose_direction()

        dx, dy = self.DIRECTIONS[self.direction]

        # Add current head position to body
        self.body.appendleft((self.head_x, self.head_y))

        # Move head (with wrap-around)
        self.head_x = (self.head_x + dx) % self.width
        self.head_y = (self.head_y + dy) % self.height

        # Check for food collision
        ate_food = (self.head_x == self.food_x and self.head_y == self.food_y)

        if ate_food:
            # Don't remove tail (snake grows)
            self._spawn_food()
        else:
            # Remove tail (snake moves without growing)
            self.body.pop()

        # Check for self-collision
        if (self.head_x, self.head_y) in set(self.body):
            self.game_over = True

        # Check if snake fills entire screen
        total_cells = self.width * self.height
        snake_length = 1 + len(self.body)
        if snake_length >= total_cells:
            self.game_over = True

    def step(self):
        """Advance one frame of the scene."""
        if self.done:
            return []

        self.step_count += 1
        pixels = []

        # Handle game over blinking
        if self.game_over:
            self.blink_counter += 1

            # Toggle blink state
            if self.blink_counter % (self.blink_frames // 4) == 0:
                self.blink_on = not self.blink_on

            # Check if blink animation is complete
            if self.blink_counter >= self.blink_frames:
                if self.loop:
                    self.reset()
                    return []
                else:
                    self.done = True
                    return []

            # Render blinking snake (all segments at full brightness)
            if self.blink_on:
                pixels.append((self.head_x, self.head_y, 1.0))
                for x, y in self.body:
                    pixels.append((x, y, 1.0))

            return pixels

        # Accumulate movement
        self.move_accumulator += self.speed

        # Move snake when accumulator reaches 1.0
        while self.move_accumulator >= 1.0:
            self.move_accumulator -= 1.0
            self._move_snake()

            # Check if game over happened during move
            if self.game_over:
                break

        # Render snake head (brightest)
        pixels.append((self.head_x, self.head_y, 1.0))

        # Render body with gradient (brighter near head)
        body_len = len(self.body)
        for i, (x, y) in enumerate(self.body):
            # Gradient from 0.8 to 0.3
            if body_len > 1:
                brightness = 0.8 - (i * 0.5 / (body_len - 1))
            else:
                brightness = 0.8
            pixels.append((x, y, max(0.3, brightness)))

        # Render pulsing food
        if self.food_x >= 0 and self.food_y >= 0:
            pulse = 0.6 + 0.4 * math.sin(self.step_count * 0.2)
            pixels.append((self.food_x, self.food_y, pulse))

        return pixels

    def is_done(self):
        """Return True when scene is complete (never true in loop mode)."""
        return self.done


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
