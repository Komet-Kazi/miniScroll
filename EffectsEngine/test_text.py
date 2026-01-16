#!/usr/bin/env python3
"""
Test script for TextScroller effect.

Tests various configurations and layering capabilities.
"""

from effects import TextScroller, Layer, LayeredEffect, BlendMode, Comet, WaveRipple
from runner import EffectRunner
import time

def test_static_text():
    """Test 1: Static text display."""
    print("\n=== Test 1: Static Text Display ===")
    print("Displaying 'HELLO' statically at position (0, 1)")

    text = TextScroller("HELLO", x_start=0, y_pos=1, speed=0)
    runner = EffectRunner(text, fps=20)

    print("Running for 3 seconds...")
    runner.run(frames=60)  # 3 seconds at 20 fps
    print("[OK] Static text test complete")


def test_scrolling_text():
    """Test 2: Scrolling text animation."""
    print("\n=== Test 2: Scrolling Text ===")
    print("Scrolling 'HELLO WORLD' from right to left")

    text = TextScroller("HELLO WORLD", speed=0.5)
    runner = EffectRunner(text, fps=20)

    print("Running until complete...")
    runner.run()  # Run until done
    print("[OK] Scrolling text test complete")


def test_different_fonts():
    """Test 3: Different font sizes."""
    print("\n=== Test 3: Different Fonts ===")

    from scrollphathd.fonts import font3x5, font5x7

    print("Testing font3x5 (compact)...")
    text1 = TextScroller("COMPACT", x_start=0, y_pos=0, speed=0, font=font3x5)
    runner = EffectRunner(text1, fps=20)
    runner.run(frames=40)

    print("Testing font5x7 (default)...")
    text2 = TextScroller("STANDARD", x_start=0, y_pos=0, speed=0, font=font5x7)
    runner = EffectRunner(text2, fps=20)
    runner.run(frames=40)

    print("[OK] Font test complete")


def test_looping_text():
    """Test 4: Looping scroll."""
    print("\n=== Test 4: Looping Text ===")
    print("Scrolling 'LOOP' continuously for 5 seconds")

    text = TextScroller("LOOP", speed=1.0, loop=True)
    runner = EffectRunner(text, fps=20)

    runner.run(frames=100)  # 5 seconds
    print("[OK] Looping text test complete")


def test_layered_text_and_comet():
    """Test 5: Text layered with comet animation."""
    print("\n=== Test 5: Text + Comet Layer ===")
    print("Displaying 'COMET' with a comet animation underneath")

    text = TextScroller("COMET", x_start=0, y_pos=0, speed=0, brightness=1.0)
    comet = Comet(x=0, y=5, dx=0.3, dy=-0.1, tail_length=8, bounce=True)

    composite = LayeredEffect(
        Layer(comet, BlendMode.MAX),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(composite, fps=20)
    runner.run(frames=100)  # 5 seconds
    print("[OK] Layered text + comet test complete")


def test_layered_text_and_wave():
    """Test 6: Text with wave ripple effect."""
    print("\n=== Test 6: Text + Wave Ripple ===")
    print("Scrolling text over expanding wave")

    text = TextScroller("WAVE", y_pos=1, speed=0.3)
    wave = WaveRipple(cx=8, cy=3, speed=0.4, max_radius=10)

    composite = LayeredEffect(
        Layer(wave, BlendMode.ALPHA_SOFT),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(composite, fps=20)
    runner.run(frames=150)  # Until wave completes
    print("[OK] Layered text + wave test complete")


def test_multi_line_text():
    """Test 7: Multiple text lines at different positions."""
    print("\n=== Test 7: Multi-line Text ===")
    print("Displaying two lines of text")

    from scrollphathd.fonts import font3x5

    line1 = TextScroller("LINE 1", x_start=0, y_pos=0, speed=0, font=font3x5)
    line2 = TextScroller("LINE 2", x_start=0, y_pos=4, speed=0, font=font3x5)

    composite = LayeredEffect(
        Layer(line1, BlendMode.MAX),
        Layer(line2, BlendMode.MAX)
    )

    runner = EffectRunner(composite, fps=20)
    runner.run(frames=60)  # 3 seconds
    print("[OK] Multi-line text test complete")


def test_brightness_variations():
    """Test 8: Different brightness levels."""
    print("\n=== Test 8: Brightness Variations ===")

    bright = TextScroller("BRIGHT", x_start=0, y_pos=0, speed=0, brightness=1.0)
    dim = TextScroller("DIM", x_start=0, y_pos=0, speed=0, brightness=0.3)

    print("Testing bright text (1.0)...")
    runner1 = EffectRunner(bright, fps=20)
    runner1.run(frames=40)

    print("Testing dim text (0.3)...")
    runner2 = EffectRunner(dim, fps=20)
    runner2.run(frames=40)

    print("[OK] Brightness test complete")


def run_all_tests():
    """Run all tests sequentially."""
    print("=" * 50)
    print("TextScroller Effect Test Suite")
    print("=" * 50)

    try:
        test_static_text()
        time.sleep(0.5)

        test_scrolling_text()
        time.sleep(0.5)

        test_different_fonts()
        time.sleep(0.5)

        test_looping_text()
        time.sleep(0.5)

        test_layered_text_and_comet()
        time.sleep(0.5)

        test_layered_text_and_wave()
        time.sleep(0.5)

        test_multi_line_text()
        time.sleep(0.5)

        test_brightness_variations()

        print("\n" + "=" * 50)
        print("[OK] ALL TESTS PASSED!")
        print("=" * 50)

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
