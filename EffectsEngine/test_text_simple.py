#!/usr/bin/env python3
"""
Simple unit tests for TextScroller effect (no hardware required).

Tests the pixel output logic without needing the actual LED display.
"""

from effects import TextScroller, Layer, LayeredEffect, BlendMode, Comet
from scrollphathd.fonts import font5x7, font3x5


def test_static_text_pixels():
    """Test 1: Verify static text generates correct pixel structure."""
    print("\n=== Test 1: Static Text Pixel Generation ===")

    text = TextScroller("HI", x_start=0, y_pos=0, speed=0)

    # Get first frame
    pixels = text.step()

    print(f"Text: 'HI'")
    print(f"Generated {len(pixels)} pixels")
    print(f"Text width: {text.text_width} pixels")

    # Verify pixels are tuples of (x, y, brightness)
    assert all(len(p) == 3 for p in pixels), "Each pixel should be (x, y, brightness) tuple"
    assert all(isinstance(p[0], int) and isinstance(p[1], int) for p in pixels), "x, y should be integers"
    assert all(0 <= p[2] <= 1.0 for p in pixels), "Brightness should be 0-1.0"

    # Verify pixels are within bounds (17x7 display)
    assert all(0 <= p[0] < 17 for p in pixels), f"X coordinates out of bounds: {[p[0] for p in pixels if not (0 <= p[0] < 17)]}"
    assert all(0 <= p[1] < 7 for p in pixels), f"Y coordinates out of bounds: {[p[1] for p in pixels if not (0 <= p[1] < 7)]}"

    # Static text should return same pixels each frame
    pixels2 = text.step()
    assert len(pixels) == len(pixels2), "Static text should return same pixel count"

    print("[OK] Static text generates valid pixels")
    print(f"Sample pixels (first 5): {pixels[:5]}")


def test_scrolling_motion():
    """Test 2: Verify scrolling updates pixel positions."""
    print("\n=== Test 2: Scrolling Motion ===")

    text = TextScroller("A", x_start=10, y_pos=0, speed=1.0)

    # Get initial frame
    frame1 = text.step()
    x_coords_1 = [p[0] for p in frame1]

    # Get second frame (should have scrolled left by 1 pixel)
    frame2 = text.step()
    x_coords_2 = [p[0] for p in frame2]

    print(f"Frame 1 X coords: {sorted(set(x_coords_1))}")
    print(f"Frame 2 X coords: {sorted(set(x_coords_2))}")

    # X positions should generally decrease (scroll left)
    # Note: Some pixels might drop out of view
    if x_coords_2:  # If still visible
        avg_x1 = sum(x_coords_1) / len(x_coords_1) if x_coords_1 else 0
        avg_x2 = sum(x_coords_2) / len(x_coords_2) if x_coords_2 else 0
        assert avg_x2 < avg_x1, "Average X position should decrease (scrolling left)"

    print("[OK] Scrolling updates pixel positions correctly")


def test_scroll_completion():
    """Test 3: Verify scrolling completes and is_done() works."""
    print("\n=== Test 3: Scroll Completion ===")

    text = TextScroller("X", x_start=5, y_pos=0, speed=2.0, loop=False)

    assert not text.is_done(), "Should not be done initially"

    # Run until completion
    frame_count = 0
    max_frames = 100

    while not text.is_done() and frame_count < max_frames:
        pixels = text.step()
        frame_count += 1

    print(f"Completed after {frame_count} frames")
    assert text.is_done(), "Should be done after scrolling off-screen"
    assert frame_count < max_frames, "Should complete in reasonable time"

    # After done, should return empty pixels
    pixels = text.step()
    assert len(pixels) == 0, "Should return no pixels after completion"

    print("[OK] Scroll completion works correctly")


def test_looping_text():
    """Test 4: Verify looping text restarts."""
    print("\n=== Test 4: Looping Text ===")

    text = TextScroller("L", x_start=5, y_pos=0, speed=2.0, loop=True)

    # Run past where it would normally complete
    for _ in range(50):
        pixels = text.step()

    # Should never be done
    assert not text.is_done(), "Looping text should never be done"

    # Should still be generating pixels (after looping back)
    pixels = text.step()
    # Might be 0 if we're in the off-screen portion of the loop
    # But is_done() should still be False
    assert not text.is_done(), "Looping should keep effect alive"

    print("[OK] Looping text works correctly")


def test_different_fonts():
    """Test 5: Verify different fonts generate different pixel patterns."""
    print("\n=== Test 5: Different Fonts ===")

    text_5x7 = TextScroller("A", x_start=0, y_pos=0, speed=0, font=font5x7)
    text_3x5 = TextScroller("A", x_start=0, y_pos=0, speed=0, font=font3x5)

    pixels_5x7 = text_5x7.step()
    pixels_3x5 = text_3x5.step()

    print(f"font5x7: {len(pixels_5x7)} pixels, width={text_5x7.text_width}")
    print(f"font3x5: {len(pixels_3x5)} pixels, width={text_3x5.text_width}")

    # Different fonts should generate different pixel counts/patterns
    # (3x5 should generally be smaller)
    assert text_3x5.text_width <= text_5x7.text_width, "font3x5 should be narrower"

    print("[OK] Different fonts work correctly")


def test_brightness_control():
    """Test 6: Verify brightness parameter affects pixel brightness."""
    print("\n=== Test 6: Brightness Control ===")

    text_bright = TextScroller("B", x_start=0, y_pos=0, speed=0, brightness=1.0)
    text_dim = TextScroller("B", x_start=0, y_pos=0, speed=0, brightness=0.5)

    pixels_bright = text_bright.step()
    pixels_dim = text_dim.step()

    # Check brightness values
    brightness_bright = [p[2] for p in pixels_bright]
    brightness_dim = [p[2] for p in pixels_dim]

    print(f"Bright text brightness: {brightness_bright[0] if brightness_bright else 'N/A'}")
    print(f"Dim text brightness: {brightness_dim[0] if brightness_dim else 'N/A'}")

    assert all(b == 1.0 for b in brightness_bright), "Bright text should have brightness=1.0"
    assert all(b == 0.5 for b in brightness_dim), "Dim text should have brightness=0.5"

    print("[OK] Brightness control works correctly")


def test_layering_composition():
    """Test 7: Verify text can be layered with other effects."""
    print("\n=== Test 7: Layering with Effects ===")

    text = TextScroller("T", x_start=5, y_pos=2, speed=0)
    comet = Comet(x=0, y=5, dx=0.5, dy=0, tail_length=4)

    composite = LayeredEffect(
        Layer(comet, BlendMode.MAX),
        Layer(text, BlendMode.MAX)
    )

    pixels = composite.step()

    print(f"Layered effect generated {len(pixels)} pixels")

    # Should have pixels from both effects
    assert len(pixels) > 0, "Layered effect should generate pixels"

    # Verify pixels are valid
    assert all(len(p) == 3 for p in pixels), "Each pixel should be (x, y, brightness) tuple"

    print("[OK] Layering works correctly")


def test_reset():
    """Test 8: Verify reset() works correctly."""
    print("\n=== Test 8: Reset Functionality ===")

    text = TextScroller("R", x_start=10, y_pos=0, speed=2.0, loop=False)

    # Scroll for several frames
    for _ in range(10):
        text.step()

    offset_before_reset = text.scroll_offset
    print(f"Scroll offset after 10 frames: {offset_before_reset}")

    # Reset
    text.reset()

    assert text.scroll_offset == 0.0, "Reset should clear scroll offset"
    assert not text.is_done(), "Reset should clear done flag"

    print("[OK] Reset works correctly")


def test_empty_string():
    """Test 9: Verify empty string handling."""
    print("\n=== Test 9: Empty String Handling ===")

    text = TextScroller("", x_start=0, y_pos=0, speed=0)

    pixels = text.step()

    print(f"Empty text generated {len(pixels)} pixels")
    print(f"Text width: {text.text_width}")

    assert len(pixels) == 0, "Empty string should generate no pixels"
    assert text.text_width == 0, "Empty string should have width 0"

    print("[OK] Empty string handled correctly")


def run_all_tests():
    """Run all tests sequentially."""
    print("=" * 60)
    print("TextScroller Unit Test Suite (No Hardware Required)")
    print("=" * 60)

    try:
        test_static_text_pixels()
        test_scrolling_motion()
        test_scroll_completion()
        test_looping_text()
        test_different_fonts()
        test_brightness_control()
        test_layering_composition()
        test_reset()
        test_empty_string()

        print("\n" + "=" * 60)
        print("[OK] ALL TESTS PASSED!")
        print("=" * 60)
        print("\nTextScroller is working correctly!")
        print("Ready to use on hardware with EffectRunner.")

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n[FAIL] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
