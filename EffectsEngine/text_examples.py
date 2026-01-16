#!/usr/bin/env python3
"""
TextScroller Effect - Usage Examples

Demonstrates various ways to use the TextScroller effect with
the EffectsEngine architecture. Run these on actual hardware
with Scroll pHAT HD connected.
"""

import scrollphathd
from effects import (
    TextScroller, Layer, LayeredEffect, BlendMode,
    Comet, WaveRipple, Sparkle, ScannerSweep, PulseFade
)
from runner import EffectRunner
from scrollphathd.fonts import font5x7, font3x5, font5x7smoothed


def example_simple_scroll():
    """Example 1: Simple scrolling text message."""
    print("Example 1: Simple scrolling text")

    text = TextScroller("HELLO WORLD", speed=0.5)
    runner = EffectRunner(text, fps=20)
    runner.run(frames=100)  # Runs until text scrolls off-screen


def example_static_label():
    """Example 2: Static text label (no scrolling)."""
    print("Example 2: Static label")

    label = TextScroller("READY", x_start=0, y_pos=1, speed=0)
    runner = EffectRunner(label, fps=20)
    runner.run(frames=60)  # Show for 3 seconds


def example_looping_marquee():
    """Example 3: Continuous looping marquee."""
    print("Example 3: Looping marquee")

    marquee = TextScroller("*** NEWS FLASH ***", speed=0.75, loop=True)
    runner = EffectRunner(marquee, fps=20)
    runner.run(frames=300)  # Run for 15 seconds


def example_compact_font():
    """Example 4: Using compact font for more text."""
    print("Example 4: Compact font")

    compact_text = TextScroller(
        "COMPACT TEXT FITS MORE",
        font=font3x5,
        y_pos=1,
        speed=0.6
    )
    runner = EffectRunner(compact_text, fps=20)
    runner.run(frames=100)


def example_text_with_comet():
    """Example 5: Text layered over comet animation."""
    print("Example 5: Text + Comet")

    text = TextScroller("COMET", y_pos=0, speed=0.4, brightness=1.0)
    comet = Comet(x=0, y=5, dx=1, dy=-1, tail_length=10, bounce=True)

    scene = LayeredEffect(
        Layer(comet, BlendMode.MAX),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=200)


def example_text_with_wave():
    """Example 6: Text scrolling over expanding wave."""
    print("Example 6: Text + Wave")

    text = TextScroller("WAVES", y_pos=1, speed=0.3)
    wave = WaveRipple(cx=8, cy=3, speed=0.5, max_radius=12)

    scene = LayeredEffect(
        Layer(wave, BlendMode.ALPHA_SOFT),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=180)


def example_multiline_text():
    """Example 7: Multiple lines of text at different positions."""
    print("Example 7: Multi-line text")

    line1 = TextScroller("LINE ONE", x_start=0, y_pos=0, speed=0, font=font3x5)
    line2 = TextScroller("LINE TWO", x_start=0, y_pos=4, speed=0, font=font3x5)

    scene = LayeredEffect(
        Layer(line1, BlendMode.MAX),
        Layer(line2, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=100)


def example_text_with_sparkles():
    """Example 8: Text with sparkling background."""
    print("Example 8: Text + Sparkles")

    text = TextScroller("SPARKLE", y_pos=1, speed=0.4, brightness=1.0)

    # Create sparkle background
    sparkles = LayeredEffect(
        Layer(Sparkle(2, 3, speed=15), BlendMode.MAX),
        Layer(Sparkle(7, 1, speed=20), BlendMode.MAX),
        Layer(Sparkle(12, 5, speed=18), BlendMode.MAX),
        Layer(Sparkle(15, 2, speed=22), BlendMode.MAX),
        Layer(Sparkle(5, 6, speed=16), BlendMode.MAX),
    )

    scene = LayeredEffect(
        Layer(sparkles, BlendMode.ALPHA_SOFT),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=200)


def example_text_with_scanner():
    """Example 9: Text with scanner sweep effect."""
    print("Example 9: Text + Scanner")

    text = TextScroller("SCAN", y_pos=2, speed=0, font=font3x5)
    scanner = ScannerSweep(horizontal=False, speed=1, trail_length=4, bounce=True)

    scene = LayeredEffect(
        Layer(scanner, BlendMode.ALPHA_SOFT),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=150)


def example_text_with_pulse():
    """Example 10: Text with pulsing background."""
    print("Example 10: Text + Pulse")

    text = TextScroller("PULSE", y_pos=1, speed=0, brightness=1.0)
    pulse = PulseFade(speed=0.08, repeat=True)

    scene = LayeredEffect(
        Layer(pulse, BlendMode.ALPHA_SOFT),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=120)


def example_dim_vs_bright():
    """Example 11: Comparing different brightness levels."""
    print("Example 11: Brightness comparison")

    # Show bright text
    bright = TextScroller("BRIGHT", x_start=0, y_pos=1, speed=0, brightness=1.0)
    runner = EffectRunner(bright, fps=20)
    runner.run(frames=40)

    scrollphathd.clear()

    # Show dim text
    dim = TextScroller("DIM", x_start=0, y_pos=1, speed=0, brightness=0.3)
    runner = EffectRunner(dim, fps=20)
    runner.run(frames=40)


def example_smooth_font():
    """Example 12: Smoothed font rendering."""
    print("Example 12: Smoothed font")

    smooth_text = TextScroller(
        "SMOOTH TEXT",
        font=font5x7smoothed,
        speed=0.5,
        brightness=0.8
    )

    runner = EffectRunner(smooth_text, fps=20)
    runner.run(frames=100)


def example_scrolling_announcement():
    """Example 13: Realistic announcement style."""
    print("Example 13: Announcement")

    # Show static title first
    title = TextScroller("NEWS:", x_start=0, y_pos=0, speed=0, font=font3x5)
    runner = EffectRunner(title, fps=20)
    runner.run(frames=40)

    # Then scroll the message
    message = TextScroller(
        "TEXTSCROLLER EFFECT IS NOW AVAILABLE!",
        y_pos=4,
        speed=0.5,
        font=font3x5
    )

    scene = LayeredEffect(
        Layer(title, BlendMode.MAX),
        Layer(message, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=100)


def run_all_examples():
    """Run all examples in sequence."""
    print("=" * 60)
    print("TextScroller Effect - Usage Examples")
    print("=" * 60)

    examples = [
        example_simple_scroll,
        example_static_label,
        example_looping_marquee,
        example_compact_font,
        example_text_with_comet,
        example_text_with_wave,
        example_multiline_text,
        example_text_with_sparkles,
        example_text_with_scanner,
        example_text_with_pulse,
        example_dim_vs_bright,
        example_smooth_font,
        example_scrolling_announcement,
    ]

    try:
        # Initialize display
        scrollphathd.clear()
        scrollphathd.set_brightness(0.2)
        scrollphathd.rotate(degrees=180)  # Adjust if your display is upside down

        for example_func in examples:
            print(f"\n--- Running: {example_func.__name__} ---")
            example_func()
            scrollphathd.clear()

        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    finally:
        scrollphathd.clear()
        scrollphathd.show()


if __name__ == "__main__":
    # Run all examples in sequence

    # Uncomment the below if your display is upside down
    scrollphathd.rotate(degrees=180)

    run_all_examples()

    # Or uncomment individual examples to run them:
    # example_simple_scroll()
    # example_text_with_comet()
    # example_multiline_text()
