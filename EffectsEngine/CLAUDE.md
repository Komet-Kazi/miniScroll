# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**EffectsEngine** is a Python-based animation framework for the **Scroll pHAT HD** (17×7 LED matrix display). It provides a composable, hardware-agnostic system for creating visual effects that can be layered and blended together.

### Core Architecture

All effects follow the `BaseEffect` interface:

```python
class BaseEffect:
    def step(self) -> list[tuple[int, int, float]]  # Advance one frame, return pixels
    def reset(self) -> None                          # Reinitialize to start state
    def is_done(self) -> bool                        # Signal completion (default: False)
```

Effects are:
- **Pure animations**: Deterministic, stateless functions that emit pixel coordinates
- **Hardware-agnostic**: No direct hardware calls (use DisplayConfig for dimensions)
- **Composable**: Can be layered using `LayeredEffect` with `BlendMode` (MAX, ADD, ALPHA_SOFT, ALPHA_HARD, OVERWRITE)
- **Sparse**: Only emit pixels that are visible

## Development Commands

### Virtual Environment

Before running any Python files, activate the virtual environment:

```bash
C:\Users\levit\.virtualenvs\Pimoroni\Scripts\Activate.ps1
```

### Running Code

```bash
python main.py              # Run effect demos
python test_text_simple.py  # Run unit tests (no hardware required)
python text_examples.py     # Run TextScroller examples
```

### Testing Individual Effects

```python
from effects import Comet, TextScroller
from runner import EffectRunner

effect = Comet(x=0, y=0, dx=1, dy=1, tail_length=6, bounce=True)
runner = EffectRunner(effect, fps=20)
runner.run(frames=150)  # Run for specific frame count
```

## File Structure

| File | Purpose | Size |
|------|---------|------|
| **effects.py** | All 23 effect implementations | ~1300 lines |
| **runner.py** | EffectRunner (real-time) + AnimationRecorder (pre-baking) | ~150 lines |
| **main.py** | Demo entry point with demo functions | ~200 lines |
| **test_text_simple.py** | Unit tests for TextScroller | ~300 lines |
| **text_examples.py** | TextScroller usage examples | ~250 lines |

## Available Effects (23 Classes)

### Core Visual Effects
- **Sparkle**: Random bright pixel
- **SparkleField**: Multiple sparkles distributed across the display
- **Comet**: Moving point with trail (supports bounce)
- **WaveRipple**: Concentric wave from center point
- **ExpandingBox**: Growing rectangular outline
- **SpiralSweep**: Rotating spiral pattern
- **ScannerSweep**: Horizontal/vertical sweep with trail
- **ZigZagSweep**: Diagonal back-and-forth pattern
- **PulseFade**: Global brightness pulse

### Text Effects
- **TextScroller**: Scrolling, static, or looping text with font support

### Game-Like Effects
- **PacMan**, **Ghost**, **PelletRow**: Animated game characters
- **PacManScene**: Pre-composed scene combining above

### Composite Effects
- **LayeredEffect**: Combines multiple effects with blend modes
- **BakedAnimation**: Plays pre-recorded animations from disk

## Effect Development Guidelines

When creating or modifying effects, follow the **LED_Effect_style_guide.md** specification:

### Required Behaviors
1. **Subclass BaseEffect** and implement step(), reset(), is_done()
2. **Initialize all state in reset()**, not __init__
3. **Return sparse pixels**: Only emit `(x, y, brightness)` tuples for visible pixels
4. **Use normalized brightness**: 0.0 to 1.0 (clamping happens in renderer)
5. **No hardware calls**: Use DisplayConfig for dimensions (default: 17×7)

### Forbidden Behaviors
- ❌ No randomness in step() (only in reset())
- ❌ No time measurement or sleep() calls
- ❌ No caching of display dimensions
- ❌ No direct imports of scrollphathd in effects
- ❌ No clearing or overwriting pixels (layering is external)

### Effect Categories
- **Point Effects**: Sparkle, Comet head
- **Sweep Effects**: Scanner, ZigZag, Spiral
- **Field Effects**: Ripples, Waves, Noise
- **Hybrid Effects**: Comet (point + memory), Pulse waves

### Example Effect Structure

```python
class MyEffect(BaseEffect):
    def __init__(self, speed=1.0):
        self.speed = speed
        self.reset()

    def reset(self):
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.step_count = 0
        self.done = False

    def step(self):
        if self.done:
            return []

        self.pos_x += self.speed
        self.step_count += 1

        # Check completion
        if self.pos_x > DisplayConfig.width:
            self.done = True

        # Return sparse pixels
        x = int(self.pos_x)
        y = int(self.pos_y)
        return [(x, y, 1.0)]

    def is_done(self):
        return self.done
```

## Key Architectural Patterns

### Effect Composition

```python
from effects import LayeredEffect, Layer, BlendMode, Comet, WaveRipple

scene = LayeredEffect(
    Layer(WaveRipple(cx=8, cy=3, speed=0.7), BlendMode.OVERWRITE),  # Background
    Layer(Comet(0, 0, dx=1, dy=1, tail_length=6), BlendMode.MAX)    # Foreground
)
```

### Animation Recording

```python
from runner import AnimationRecorder

effect = MyEffect()
recorder = AnimationRecorder(effect, fps=25)
recorder.record(frames=150)
recorder.save("animation.anim.gz")

# Later playback
from effects import BakedAnimation
playback = BakedAnimation("animation.anim.gz", loop=True)
```

### TextScroller Usage

```python
from effects import TextScroller
from scrollphathd.fonts import font5x7, font3x5

# Scrolling text
text = TextScroller("HELLO WORLD", speed=0.5)

# Static text
label = TextScroller("READY", x_start=0, y_pos=1, speed=0)

# Looping marquee
marquee = TextScroller("NEWS", speed=0.75, loop=True)

# Multi-line with LayeredEffect
line1 = TextScroller("LINE 1", x_start=0, y_pos=0, speed=0, font=font3x5)
line2 = TextScroller("LINE 2", x_start=0, y_pos=4, speed=0, font=font3x5)
scene = LayeredEffect(Layer(line1, BlendMode.MAX), Layer(line2, BlendMode.MAX))
```

## Known Issues

- **TextScroller compatibility**: Some effects and text combinations don't work correctly (commit cf5476d). When debugging TextScroller layering issues, check blend modes and brightness levels.

## Documentation References

- **LED_Effect_style_guide.md**: Formal architecture specification (15 sections, ~360 lines)
- **TEXT_SCROLLER_README.md**: Complete TextScroller documentation (~385 lines)
- **scroll-phat-hd-repomix.md**: Hardware library reference

## Python Development Rules

- **Docstrings**: If you add or update a Class, Method, or Function, you must update its docstring with relevant information.
- **Chat History**: Append all chat input and output to `.chat_history` in markdown format.
