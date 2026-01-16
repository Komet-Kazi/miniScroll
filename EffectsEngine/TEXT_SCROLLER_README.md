# TextScroller Effect

A fully-integrated text display effect for the EffectsEngine that supports scrolling, static text, and seamless layering with other animations.

## Features

- **Hardware-agnostic design**: Works with the effects architecture's pixel-based system
- **Multiple animation modes**: Scrolling, static, looping
- **Full layering support**: Blend text with any other effect using `BlendMode`
- **Font support**: All scrollphathd fonts (font5x7, font3x5, font5x5, font5x7smoothed, font5x7unicode)
- **Customizable**: Control speed, brightness, position, spacing
- **Efficient**: Pre-renders text once, applies transforms per frame
- **Clean API**: Simple `BaseEffect` interface with `step()`, `reset()`, `is_done()`

## Basic Usage

### Simple Scrolling Text

```python
from effects import TextScroller
from runner import EffectRunner

text = TextScroller("HELLO WORLD", speed=0.5)
runner = EffectRunner(text, fps=20)
runner.run()  # Scrolls until off-screen
```

### Static Text Display

```python
label = TextScroller("READY", x_start=0, y_pos=1, speed=0)
runner = EffectRunner(label, fps=20)
runner.run(frames=60)  # Display for 3 seconds
```

### Looping Marquee

```python
marquee = TextScroller("NEWS FLASH", speed=0.75, loop=True)
runner = EffectRunner(marquee, fps=20)
runner.run(frames=300)  # Loops for 15 seconds
```

## Parameters

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | str | (required) | The text string to display |
| `x_start` | int \| None | `width` | Starting X position (None = off-screen right) |
| `y_pos` | int | 0 | Vertical position (0 = top) |
| `speed` | float | 1.0 | Scroll speed in pixels/frame (0 = static) |
| `font` | font module | font5x7 | scrollphathd font to use |
| `letter_spacing` | int | 1 | Pixels between characters |
| `brightness` | float | 1.0 | Text brightness (0.0-1.0) |
| `loop` | bool | False | Whether to restart when done |
| `width` | int \| None | None | Display width (None = use DisplayConfig) |
| `height` | int \| None | None | Display height (None = use DisplayConfig) |

## Font Options

```python
from scrollphathd.fonts import (
    font5x7,        # Default, most readable (5x7 pixels)
    font3x5,        # Compact (3x5 pixels)
    font5x5,        # Square aspect (5x5 pixels)
    font5x7smoothed,  # Smoother rendering
    font5x7unicode   # Extended character support
)

text = TextScroller("Hello", font=font3x5)
```

## Layering with Other Effects

TextScroller integrates seamlessly with `LayeredEffect` and all `BlendMode` options:

### Text Over Animation

```python
from effects import LayeredEffect, Layer, BlendMode, Comet

text = TextScroller("COMET", y_pos=1, speed=0.4)
comet = Comet(x=0, y=5, dx=0.4, dy=-0.05, tail_length=10, bounce=True)

scene = LayeredEffect(
    Layer(comet, BlendMode.MAX),
    Layer(text, BlendMode.MAX)
)

runner = EffectRunner(scene, fps=20)
runner.run(frames=200)
```

### Text with Wave Ripple

```python
text = TextScroller("WAVE", y_pos=1, speed=0.3)
wave = WaveRipple(cx=8, cy=3, speed=0.5, max_radius=12)

scene = LayeredEffect(
    Layer(wave, BlendMode.ALPHA_SOFT),  # Subtle background
    Layer(text, BlendMode.MAX)          # Prominent text
)
```

### Multi-Line Text

```python
from scrollphathd.fonts import font3x5

line1 = TextScroller("LINE 1", x_start=0, y_pos=0, speed=0, font=font3x5)
line2 = TextScroller("LINE 2", x_start=0, y_pos=4, speed=0, font=font3x5)

scene = LayeredEffect(
    Layer(line1, BlendMode.MAX),
    Layer(line2, BlendMode.MAX)
)
```

## Animation Modes

### 1. Classic Scroll (Default)

Text starts off-screen right and scrolls left until fully off-screen.

```python
text = TextScroller("SCROLL ME")  # speed=1.0 by default
```

**Completion**: `is_done()` returns `True` when text fully exits left side.

### 2. Static Display

Text appears at a fixed position without moving.

```python
text = TextScroller("STATIC", x_start=0, y_pos=1, speed=0)
```

**Completion**: Never completes (always returns same pixels).

### 3. Looping Scroll

Text scrolls continuously, restarting when it exits.

```python
text = TextScroller("LOOP", speed=1.0, loop=True)
```

**Completion**: Never completes (`is_done()` always `False`).

### 4. Custom Start Position

Start text at a specific position (e.g., center).

```python
# Center text horizontally (assuming ~30 pixel width)
text = TextScroller("CENTER", x_start=8, y_pos=1, speed=0)
```

## Advanced Usage

### Brightness Control

```python
# Bright title
title = TextScroller("TITLE", brightness=1.0, font=font5x7)

# Dim subtitle
subtitle = TextScroller("subtitle", brightness=0.4, font=font3x5)
```

### Letter Spacing

```python
# Tight spacing
compact = TextScroller("COMPACT", letter_spacing=0)

# Wide spacing
spaced = TextScroller("S P A C E D", letter_spacing=2)
```

### Speed Variations

```python
slow = TextScroller("SLOW", speed=0.25)    # Slow scroll
normal = TextScroller("NORMAL", speed=1.0)  # Standard
fast = TextScroller("FAST", speed=2.5)      # Fast scroll
smooth = TextScroller("SMOOTH", speed=0.1)  # Very smooth
```

### Vertical Positioning

```python
top = TextScroller("TOP", y_pos=0)        # Top edge
middle = TextScroller("MID", y_pos=2)     # Middle (font3x5)
bottom = TextScroller("BOT", y_pos=5)     # Bottom (leaves 2px below)
```

## Blend Modes

When layering text with other effects, choose appropriate blend modes:

| Blend Mode | Effect | Use Case |
|------------|--------|----------|
| `MAX` | Take brighter pixel | Prominent text over animations |
| `ADD` | Add brightness | Glowing text effect |
| `ALPHA_SOFT` | 75% background, 25% text | Subtle text overlay |
| `ALPHA_HARD` | 40% background, 60% text | Visible but blended |
| `OVERWRITE` | Replace with text | Text replaces background |

```python
# Glowing text effect
text = TextScroller("GLOW", brightness=0.8)
pulse = PulseFade(speed=0.05, repeat=True)

scene = LayeredEffect(
    Layer(pulse, BlendMode.MAX),
    Layer(text, BlendMode.ADD)  # Text adds to pulse
)
```

## Methods

### `step() -> list[tuple[int, int, float]]`

Advance animation and return visible pixels for current frame.

**Returns**: List of `(x, y, brightness)` tuples.

### `reset()`

Reset scroll position to starting point and clear done flag.

```python
text.reset()  # Start over
```

### `is_done() -> bool`

Check if scrolling is complete (non-looping only).

```python
while not text.is_done():
    pixels = text.step()
    # render pixels
```

## Implementation Details

### How It Works

1. **Pre-rendering**: Text is rendered once in `__init__()` by accessing font bitmap data
2. **Pixel storage**: Character pixels stored as `[(x, y, brightness), ...]`
3. **Transform per frame**: `step()` applies scroll offset to pre-rendered pixels
4. **Viewport clipping**: Only pixels within display bounds are returned

### Font Data Structure

Fonts are Python modules with a `data` dictionary:
- `data[ord(char)]` returns list of columns (vertical pixel strips)
- Each column is a list of pixel values (0 or 1)
- TextScroller converts these to `(x, y, brightness)` tuples

### Performance

- **Efficient**: Text rendered once, transforms are simple arithmetic
- **Minimal allocation**: Pre-allocated pixel list, filters to visible pixels
- **Smooth scrolling**: Float scroll offset for sub-pixel precision

## Examples

See [text_examples.py](text_examples.py) for 13 complete usage examples including:
- Simple scrolling
- Static labels
- Looping marquees
- Multi-line text
- Text with various effects (comets, waves, sparkles, scanners, pulse)
- Font comparisons
- Brightness variations

## Testing

Run unit tests (no hardware required):

```bash
python test_text_simple.py
```

This validates:
- Pixel generation
- Scrolling motion
- Completion detection
- Looping behavior
- Font support
- Brightness control
- Layering compatibility
- Reset functionality

## Integration with main.py

Add TextScroller demos to your main demo loop:

```python
from effects import TextScroller

def demo_all_effects(fps=25, frames_per_demo=150):
    effects_to_demo = [
        # ... existing effects ...
        ("ScrollingText", TextScroller("HELLO WORLD", speed=0.5)),
        ("TextWithComet", LayeredEffect(
            Layer(Comet(0, 5, dx=0.4), BlendMode.MAX),
            Layer(TextScroller("COMET", y_pos=1), BlendMode.MAX)
        )),
    ]
    # ... rest of demo code
```

## Tips & Best Practices

### Font Selection

- **font5x7**: Best readability, use for important messages
- **font3x5**: Compact, good for multi-line or longer text
- **font5x7smoothed**: Smoother appearance, slightly less crisp
- **font5x7unicode**: When you need special characters

### Positioning

- Display is 17×7 pixels
- Leave 1-2 pixels padding on edges for best visibility
- For font3x5: `y_pos=1` centers vertically
- For font5x7: `y_pos=0` fills most of height

### Speed

- `0.25-0.5`: Comfortable reading speed
- `1.0`: Standard scroll speed
- `2.0+`: Quick scan
- `0`: Static display

### Layering Order

- Background effects first (waves, pulses)
- Text layers last for prominence
- Use `BlendMode.MAX` for crisp text
- Use `ALPHA_SOFT` for subtle backgrounds

## Troubleshooting

### Text not visible
- Check `brightness` parameter (should be > 0)
- Verify `y_pos` is within 0-6 range
- Ensure `x_start` allows text to enter viewport

### Text scrolling too fast/slow
- Adjust `speed` parameter
- Check `fps` setting in EffectRunner
- For smooth motion, use fractional speeds (0.25, 0.5, 0.75)

### Characters missing
- Character not in font - try different font
- Unicode characters need `font5x7unicode`

### Layering issues
- Check blend mode selection
- Verify layer order (background first, text last)
- Adjust brightness to ensure text is visible

## Future Enhancements

Potential additions (not yet implemented):
- Vertical scrolling
- Character-by-character reveal (typewriter effect)
- Per-character color/brightness modulation
- Wave/bounce effects on characters
- Text alignment options (left, center, right)
- Automatic line wrapping

## License

Part of the EffectsEngine project. See main project license.
