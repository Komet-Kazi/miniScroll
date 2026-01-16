#!/usr/bin/env python3
"""
Scroll pHAT HD Effects Engine
==============================

A modular effects system for the Pimoroni Scroll pHAT HD LED matrix.

Core Architecture:
    Effect (abstract) - produces pixel data each frame
    ├── PixelEffect - returns list of (x, y, brightness) tuples
    └── BufferEffect - draws directly to scrollphathd buffer

    Layer - wraps an effect with blend mode and opacity
    Compositor - combines multiple layers
    EffectRunner - handles timing and display output

Usage:
    effect = Sparkle(x=8, y=3)
    runner = EffectRunner(effect, fps=25)
    runner.run(frames=100)
"""

import time
import math
import collections
import random
from random import randint
from enum import Enum
from abc import ABC, abstractmethod
from typing import Protocol, Iterator
from contextlib import contextmanager

try:
    from icecream import ic
except ImportError:
    ic = lambda *a: a[0] if len(a) == 1 else a

import scrollphathd
from scrollphathd.fonts import font3x5

# ============================================================================
# UTILITIES
# ============================================================================

def clamp01(v: float) -> float:
    """Clamp value to [0.0, 1.0] range."""
    return max(0.0, min(1.0, abs(v)))


@contextmanager
def capture_pixels():
    """Capture pixels written by scrollphathd drawing commands."""
    captured = {}
    original = scrollphathd.set_pixel

    def intercept(x, y, b):
        if b > 0:
            captured[(x, y)] = max(captured.get((x, y), 0.0), b)

    scrollphathd.set_pixel = intercept
    try:
        yield captured
    finally:
        scrollphathd.set_pixel = original


# ============================================================================
# BLENDING
# ============================================================================

class BlendMode(Enum):
    """Pixel blending strategies."""
    REPLACE = "replace"      # Source replaces destination
    MAX = "max"              # Maximum brightness
    ADD = "add"              # Additive (clamped)
    MULTIPLY = "multiply"    # Multiplicative
    SCREEN = "screen"        # Screen blend (inverse multiply)
    ALPHA = "alpha"          # Standard alpha blend


def blend_pixel(dst: float, src: float, mode: BlendMode, opacity: float = 1.0) -> float:
    """
    Blend source pixel onto destination pixel.
    
    Args:
        dst: Destination brightness [0.0, 1.0]
        src: Source brightness [0.0, 1.0]
        mode: Blending strategy
        opacity: Source opacity [0.0, 1.0]
    
    Returns:
        Blended brightness value
    """
    src = src * opacity
    
    if mode == BlendMode.REPLACE:
        return src if src > 0 else dst
    elif mode == BlendMode.MAX:
        return max(dst, src)
    elif mode == BlendMode.ADD:
        return min(1.0, dst + src)
    elif mode == BlendMode.MULTIPLY:
        return dst * src
    elif mode == BlendMode.SCREEN:
        return 1.0 - (1.0 - dst) * (1.0 - src)
    elif mode == BlendMode.ALPHA:
        return dst * (1.0 - opacity) + src
    
    return src


# ============================================================================
# CORE ABSTRACTIONS
# ============================================================================

class Effect(ABC):
    """
    Abstract base class for all effects.
    
    Contract:
        - step() advances one frame and returns pixel data
        - reset() restores initial state
        - is_done() indicates completion
    """
    
    @abstractmethod
    def step(self) -> list[tuple[int, int, float]]:
        """
        Advance one frame.
        
        Returns:
            List of (x, y, brightness) tuples
        """
        pass
    
    def reset(self):
        """Reset to initial state."""
        pass
    
    def is_done(self) -> bool:
        """Check if effect has completed."""
        return False


class Layer:
    """
    Wraps an effect with rendering properties.
    
    Args:
        effect: The effect to render
        blend_mode: How to blend with underlying layers
        opacity: Layer transparency [0.0, 1.0]
        visible: Whether layer is rendered
    """
    
    def __init__(
        self,
        effect: Effect,
        blend_mode: BlendMode = BlendMode.MAX,
        opacity: float = 1.0,
        visible: bool = True
    ):
        self.effect = effect
        self.blend_mode = blend_mode
        self.opacity = clamp01(opacity)
        self.visible = visible
    
    def step(self) -> list[tuple[int, int, float]]:
        """Get pixels from effect if visible."""
        if not self.visible:
            return []
        return self.effect.step()


# ============================================================================
# COMPOSITOR
# ============================================================================

class Compositor:
    """
    Combines multiple layers into a single pixel buffer.
    
    Layers are rendered bottom-to-top, with each layer blended
    onto the result according to its blend mode and opacity.
    """
    
    def __init__(self):
        self.layers: list[Layer] = []
    
    def add_layer(
        self,
        effect: Effect,
        blend_mode: BlendMode = BlendMode.MAX,
        opacity: float = 1.0
    ) -> Layer:
        """Add a new layer and return it."""
        layer = Layer(effect, blend_mode, opacity)
        self.layers.append(layer)
        return layer
    
    def remove_layer(self, layer: Layer):
        """Remove a layer from the compositor."""
        self.layers.remove(layer)
    
    def clear(self):
        """Remove all layers."""
        self.layers.clear()
    
    def composite(self) -> dict[tuple[int, int], float]:
        """
        Render all layers and return final pixel buffer.
        
        Returns:
            Dictionary mapping (x, y) -> brightness
        """
        buffer = {}
        
        for layer in self.layers:
            # Auto-reset finished effects for looping
            if layer.effect.is_done():
                layer.effect.reset()
            
            pixels = layer.step()
            
            for x, y, brightness in pixels:
                key = (x, y)
                dst = buffer.get(key, 0.0)
                buffer[key] = blend_pixel(
                    dst,
                    brightness,
                    layer.blend_mode,
                    layer.opacity
                )
        
        return buffer
    
    def step(self) -> list[tuple[int, int, float]]:
        """Step all layers and return composited pixels."""
        buffer = self.composite()
        return [(x, y, b) for (x, y), b in buffer.items()]


# ============================================================================
# EFFECT RUNNER
# ============================================================================

class EffectRunner:
    """
    Renders effects to the LED matrix with timing control.
    
    Args:
        effect: Effect to render
        fps: Frames per second
        brightness: Global brightness multiplier [0.0, 1.0]
        invert: Invert brightness values
    """
    
    def __init__(
        self,
        effect: Effect,
        fps: float = 25,
        brightness: float = 1.0,
        invert: bool = False
    ):
        self.effect = effect
        self.fps = fps
        self.brightness = clamp01(brightness)
        self.invert = invert
        self._frame_delay = 1.0 / fps
    
    def _process_brightness(self, b: float) -> float:
        """Apply global brightness and inversion."""
        b = b * self.brightness
        if self.invert:
            b = 1.0 - b
        return clamp01(b)
    
    def render_frame(self):
        """Render a single frame to the display."""
        pixels = self.effect.step()
        
        scrollphathd.clear()
        
        for x, y, brightness in pixels:
            b = self._process_brightness(brightness)
            if 0 <= x < scrollphathd.width and 0 <= y < scrollphathd.height:
                scrollphathd.set_pixel(x, y, b)
        
        scrollphathd.show()
    
    def run(self, frames: int | None = None, reset: bool = True):
        """
        Run effect for specified number of frames.
        
        Args:
            frames: Number of frames to render (None = infinite)
            reset: Reset effect before starting
        """
        if reset:
            self.effect.reset()
        
        count = 0
        while frames is None or count < frames:
            self.render_frame()
            time.sleep(self._frame_delay)
            count += 1
            
            if frames is None and self.effect.is_done():
                break


# ============================================================================
# ANIMATION RECORDING
# ============================================================================

import json
import gzip

class AnimationRecorder:
    """
    Records effect frames for later playback.
    
    Args:
        effect: Effect to record
        fps: Target playback framerate
    """
    
    def __init__(self, effect: Effect, fps: float = 25):
        self.effect = effect
        self.fps = fps
        self.frames: list[list[tuple[int, int, float]]] = []
    
    def record(self, max_frames: int | None = None):
        """
        Record frames from effect.
        
        Args:
            max_frames: Maximum frames to record (None = until done)
        """
        self.effect.reset()
        self.frames.clear()
        
        count = 0
        while max_frames is None or count < max_frames:
            frame = self.effect.step()
            self.frames.append(frame)
            count += 1
            
            if max_frames is None and self.effect.is_done():
                break
    
    def save(self, filename: str):
        """Save recorded animation to compressed file."""
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
        
        print(f"Saved: {filename} ({len(self.frames)} frames)")


class BakedAnimation(Effect):
    """
    Plays back a pre-recorded animation.
    
    Args:
        filename: Path to .anim.gz file
        loop: Whether to loop playback
    """
    
    def __init__(self, filename: str, loop: bool = True):
        self.filename = filename
        self.loop = loop
        self.reset()
    
    def reset(self):
        with gzip.open(self.filename, "rt") as f:
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


# ============================================================================
# PARTICLE EFFECTS
# ============================================================================

class Sparkle(Effect):
    """
    Single pixel that brightens and fades in a sine wave.
    
    Args:
        x, y: Pixel position
        speed: Cycle duration in frames (None = random)
    """
    
    def __init__(self, x: int, y: int, speed: int | None = None):
        self.x = x
        self.y = y
        self._fixed_speed = speed
        self.reset()
    
    def reset(self):
        self.frame = randint(0, 50)
        self.speed = self._fixed_speed or randint(10, 50)
    
    def step(self):
        t = self.frame / self.speed
        brightness = math.sin(t * math.pi)
        self.frame += 1
        
        if self.frame > self.speed:
            self.frame = 0
        
        return [(self.x, self.y, brightness)]


class Comet(Effect):
    """
    Moving point with a fading tail.
    
    Args:
        x, y: Starting position
        dx, dy: Velocity per frame
        tail_length: Number of tail segments
        bounce: Bounce off edges (vs wrap)
    """
    
    def __init__(
        self,
        x: float,
        y: float,
        dx: float = 1.0,
        dy: float = 0.0,
        tail_length: int = 6,
        bounce: bool = True
    ):
        self.start_x = float(x)
        self.start_y = float(y)
        self.dx = dx
        self.dy = dy
        self.tail_length = tail_length
        self.bounce = bounce
        self.reset()
    
    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.tail = collections.deque(maxlen=self.tail_length)
        self.vx = self.dx
        self.vy = self.dy
    
    def step(self):
        w, h = scrollphathd.width, scrollphathd.height
        
        self.x += self.vx
        self.y += self.vy
        
        if self.bounce:
            if self.x < 0 or self.x >= w:
                self.vx *= -1
                self.x = max(0, min(w - 1, self.x))
            if self.y < 0 or self.y >= h:
                self.vy *= -1
                self.y = max(0, min(h - 1, self.y))
        else:
            self.x %= w
            self.y %= h
        
        self.tail.appendleft((int(round(self.x)), int(round(self.y))))
        
        pixels = []
        for i, (tx, ty) in enumerate(self.tail):
            brightness = (1.0 - i / len(self.tail)) ** 2
            pixels.append((tx, ty, max(0.05, brightness)))
        
        return pixels


class WaveRipple(Effect):
    """
    Expanding circular wave from a center point.
    
    Args:
        cx, cy: Center position
        speed: Radial growth per frame
        max_radius: Wave stops expanding at this radius
    """
    
    def __init__(
        self,
        cx: float,
        cy: float,
        speed: float = 0.5,
        max_radius: float | None = None
    ):
        self.cx = cx
        self.cy = cy
        self.speed = speed
        self._max_radius = max_radius
        self.reset()
    
    def reset(self):
        self.radius = 0.0
        self.done = False
        
        if self._max_radius is None:
            w, h = scrollphathd.width, scrollphathd.height
            self.max_radius = math.hypot(w, h)
        else:
            self.max_radius = self._max_radius
    
    def step(self):
        if self.done:
            return []
        
        pixels = []
        w, h = scrollphathd.width, scrollphathd.height
        
        for x in range(w):
            for y in range(h):
                dist = math.hypot(x - self.cx, y - self.cy)
                delta = abs(dist - self.radius)
                
                if delta < 1.0:
                    brightness = math.cos(delta * math.pi / 2)
                    brightness *= max(0.0, 1.0 - self.radius / self.max_radius)
                    
                    if brightness > 0.05:
                        pixels.append((x, y, brightness))
        
        self.radius += self.speed
        
        if self.radius > self.max_radius:
            self.done = True
        
        return pixels
    
    def is_done(self):
        return self.done


# ============================================================================
# SCAN / SWEEP EFFECTS
# ============================================================================

class ScannerSweep(Effect):
    """
    Sweeping line with fading trail (radar/scanner style).
    
    Args:
        horizontal: True for horizontal sweep, False for vertical
        speed: Pixels per frame
        trail_length: Number of trailing pixels
        bounce: Reverse at edges (vs stop)
    """
    
    def __init__(
        self,
        horizontal: bool = True,
        speed: int = 1,
        trail_length: int = 5,
        bounce: bool = True
    ):
        self.horizontal = horizontal
        self.speed = speed
        self.trail_length = trail_length
        self.bounce = bounce
        self.reset()
    
    def reset(self):
        self.pos = 0
        self.direction = 1
        self.trail = collections.deque(maxlen=self.trail_length)
        self.done = False
    
    def step(self):
        if self.done:
            return []
        
        w, h = scrollphathd.width, scrollphathd.height
        limit = w - 1 if self.horizontal else h - 1
        
        self.pos += self.direction * self.speed
        
        if self.pos < 0 or self.pos > limit:
            if self.bounce:
                self.direction *= -1
                self.pos = max(0, min(limit, self.pos))
            else:
                self.done = True
                return []
        
        self.trail.appendleft(int(self.pos))
        
        pixels = []
        for i, p in enumerate(self.trail):
            brightness = (1.0 - i / self.trail_length) ** 2
            
            if self.horizontal:
                for y in range(h):
                    pixels.append((p, y, max(0.05, brightness)))
            else:
                for x in range(w):
                    pixels.append((x, p, max(0.05, brightness)))
        
        return pixels
    
    def is_done(self):
        return self.done


class ZigZagSweep(Effect):
    """
    Zig-zag scanning pattern with vertical bouncing.
    
    Args:
        speed: Horizontal pixels per frame
        trail_length: Number of trailing pixels
        bounce: Bounce at vertical edges
    """
    
    def __init__(
        self,
        speed: int = 1,
        trail_length: int = 6,
        bounce: bool = True
    ):
        self.speed = speed
        self.trail_length = trail_length
        self.bounce = bounce
        self.reset()
    
    def reset(self):
        self.w = scrollphathd.width
        self.h = scrollphathd.height
        self.row = 0
        self.col = 0
        self.x_dir = 1
        self.y_dir = 1
        self.trail = collections.deque(maxlen=self.trail_length)
        self.done = False
    
    def step(self):
        if self.done:
            return []
        
        self.col += self.x_dir * self.speed
        
        if self.col < 0 or self.col >= self.w:
            self.col = max(0, min(self.w - 1, self.col))
            self.row += self.y_dir
            self.x_dir *= -1
            
            if self.row < 0 or self.row >= self.h:
                if self.bounce:
                    self.row = max(0, min(self.h - 1, self.row))
                    self.y_dir *= -1
                else:
                    self.done = True
                    return []
        
        self.trail.appendleft((self.col, self.row))
        
        pixels = []
        for i, (x, y) in enumerate(self.trail):
            brightness = (1.0 - i / self.trail_length) ** 2
            pixels.append((x, y, max(0.05, brightness)))
        
        return pixels
    
    def is_done(self):
        return self.done


# ============================================================================
# SHAPE EFFECTS
# ============================================================================

class ExpandingBox(Effect):
    """Expanding rectangular outline from center."""
    
    def __init__(
        self,
        cx: float,
        cy: float,
        speed: float = 0.5,
        max_radius: float | None = None
    ):
        self.cx = cx
        self.cy = cy
        self.speed = speed
        self._max_radius = max_radius
        self.reset()
    
    def reset(self):
        self.radius = 0.0
        self.done = False
        
        if self._max_radius is None:
            w, h = scrollphathd.width, scrollphathd.height
            self.max_radius = math.hypot(w, h)
        else:
            self.max_radius = self._max_radius
    
    def step(self):
        if self.done:
            return []
        
        pixels = []
        r = int(self.radius)
        
        for x in range(scrollphathd.width):
            for y in range(scrollphathd.height):
                on_edge = (
                    (abs(x - self.cx) == r and abs(y - self.cy) <= r) or
                    (abs(y - self.cy) == r and abs(x - self.cx) <= r)
                )
                if on_edge:
                    pixels.append((x, y, 1.0))
        
        self.radius += self.speed
        
        if self.radius > self.max_radius:
            self.done = True
        
        return pixels
    
    def is_done(self):
        return self.done


class PulseFade(Effect):
    """Global brightness pulse across entire display."""
    
    def __init__(self, speed: float = 0.05, repeat: bool = True):
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


# ============================================================================
# CHARACTER EFFECTS
# ============================================================================

class PacMan(Effect):
    """
    Animated Pac-Man with chomping mouth.
    
    Args:
        x, y: Starting position
        x_speed, y_speed: Velocity per frame
        radius: Body radius in pixels
        chomp_speed: Mouth animation speed
        wrap: Wrap at edges (vs stop)
    """
    
    def __init__(
        self,
        x: float,
        y: float,
        x_speed: float = 0.25,
        y_speed: float = 0.0,
        radius: float = 3.0,
        chomp_speed: float = 1.0,
        wrap: bool = True
    ):
        self.start_x = float(x)
        self.start_y = float(y)
        self.x_speed = x_speed
        self.y_speed = y_speed
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
        
        self.x += self.x_speed
        self.y += self.y_speed
        
        if self.wrap:
            self.x %= w
            self.y %= h
        else:
            if not (0 <= self.x < w and 0 <= self.y < h):
                self.done = True
                return []
        
        # Chomp animation
        self.phase += self.chomp_speed
        mouth_open = (math.sin(self.phase) + 1.0) / 2.0
        mouth_angle = mouth_open * (math.pi / 2.2)
        
        dir_angle = math.atan2(self.y_speed, self.x_speed)
        
        pixels = []
        
        xmin = int(self.x - self.radius - 1)
        xmax = int(self.x + self.radius + 1)
        ymin = int(self.y - self.radius - 1)
        ymax = int(self.y + self.radius + 1)
        
        for ix in range(xmin, xmax + 1):
            for iy in range(ymin, ymax + 1):
                if not (0 <= ix < w and 0 <= iy < h):
                    continue
                
                dx = ix + 0.5 - self.x
                dy = iy + 0.5 - self.y
                dist = math.hypot(dx, dy)
                
                if dist > self.radius:
                    continue
                
                angle = math.atan2(dy, dx)
                rel = (angle - dir_angle + math.pi * 3) % (2 * math.pi) - math.pi
                
                # Mouth cutout
                if abs(rel) < mouth_angle:
                    continue
                
                brightness = 1.0
                if dist > self.radius - 0.6:
                    brightness = clamp01(self.radius - dist + 0.6)
                
                pixels.append((ix, iy, brightness))
        
        return pixels
    
    def is_done(self):
        return self.done


# ============================================================================
# UTILITY EFFECTS
# ============================================================================

class StaticPixels(Effect):
    """Display a static set of pixels."""
    
    def __init__(self, pixels: list[tuple[int, int, float]]):
        self.pixels = pixels
    
    def step(self):
        return self.pixels


class FunctionEffect(Effect):
    """Create an effect from a generator function."""
    
    def __init__(self, generator_func):
        self.gen = generator_func()
    
    def step(self):
        try:
            return next(self.gen)
        except StopIteration:
            return []
    
    def reset(self):
        self.gen = self.generator_func()


# ============================================================================
# DEMOS
# ============================================================================

def demo_basic_effects():
    """Demonstrate basic particle effects."""
    
    effects = [
        ("Sparkle", Sparkle(8, 3)),
        ("Comet", Comet(0, 0, dx=1, dy=0.5, bounce=True)),
        ("Ripple", WaveRipple(8, 3, speed=0.5)),
        ("Scanner", ScannerSweep(horizontal=True)),
        ("ZigZag", ZigZagSweep(speed=1)),
    ]
    
    for name, effect in effects:
        print(f"Running: {name}")
        runner = EffectRunner(effect, fps=25)
        runner.run(frames=100)
        time.sleep(0.5)


def demo_compositor():
    """Demonstrate layer compositing."""
    
    comp = Compositor()
    comp.add_layer(WaveRipple(8, 3, speed=0.5), BlendMode.MAX)
    comp.add_layer(Comet(0, 0, dx=1, dy=0.5), BlendMode.ADD, opacity=0.7)
    comp.add_layer(Sparkle(4, 2), BlendMode.SCREEN)
    
    runner = EffectRunner(comp, fps=25)
    runner.run(frames=150)


def demo_animation_recording():
    """Demonstrate recording and playback."""
    
    effect = WaveRipple(8, 3, speed=0.5)
    
    # Record
    recorder = AnimationRecorder(effect, fps=25)
    recorder.record(max_frames=100)
    recorder.save("ripple.anim.gz")
    
    # Playback
    playback = BakedAnimation("ripple.anim.gz", loop=True)
    runner = EffectRunner(playback, fps=25)
    runner.run(frames=200)


if __name__ == "__main__":
    try:
        scrollphathd.set_brightness(0.2)
        scrollphathd.rotate(180)
        
        demo_basic_effects()
        # demo_compositor()
        # demo_animation_recording()
        
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        scrollphathd.clear()
        scrollphathd.show()