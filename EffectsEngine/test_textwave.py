#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test for TextWaveEffect without requiring hardware.
"""

from effects import TextWaveEffect
from runner import EffectRunner

def test_basic_wave():
    """Test basic scrolling wave text."""
    print("Testing TextWaveEffect - Basic scrolling")

    wave = TextWaveEffect(
        "WAVE",
        speed=0.5,
        wave_speed=0.2,
        wave_amplitude=2.0,
        wave_length=8.0
    )

    print(f"  Created effect: {wave}")
    print(f"  Text width: {wave.text_width}")
    print(f"  Wave amplitude: {wave.wave_amplitude}")

    # Test step function
    for i in range(5):
        pixels = wave.step()
        print(f"  Frame {i}: {len(pixels)} pixels")
        if i == 0 and len(pixels) > 0:
            print(f"    Sample pixel: {pixels[0]}")

    # Test reset
    wave.reset()
    print("  Reset successful")

    print("[PASS] Basic test passed")

def test_static_wave():
    """Test static waving text."""
    print("\nTesting TextWaveEffect - Static wave")

    wave = TextWaveEffect(
        "HELLO",
        x_start=0,
        y_pos=1,
        speed=0,
        wave_speed=0.15,
        wave_amplitude=1.5,
        wave_length=10.0
    )

    # Should produce pixels immediately since x_start=0
    pixels = wave.step()
    print(f"  Frame 0: {len(pixels)} pixels")
    assert len(pixels) > 0, "Static text should produce pixels immediately"

    # Wave phase should advance
    initial_phase = wave.wave_phase
    wave.step()
    assert wave.wave_phase > initial_phase, "Wave phase should advance"

    print("[PASS] Static wave test passed")

def test_layering():
    """Test that wave effect works with LayeredEffect."""
    print("\nTesting TextWaveEffect - Layering compatibility")

    from effects import LayeredEffect, Layer, BlendMode, SparkleField

    wave_text = TextWaveEffect(
        "TEST",
        y_pos=1,
        speed=0.4,
        wave_speed=0.18,
        wave_amplitude=1.5
    )

    scene = LayeredEffect(
        Layer(SparkleField(density=10, speed_range=(15, 30)), BlendMode.MAX),
        Layer(wave_text, BlendMode.MAX)
    )

    # Test a few frames
    for i in range(3):
        pixels = scene.step()
        print(f"  Layered frame {i}: {len(pixels)} pixels")

    print("[PASS] Layering test passed")

def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("\nTesting TextWaveEffect - Edge cases")

    # Empty text
    wave = TextWaveEffect("")
    pixels = wave.step()
    assert len(pixels) == 0, "Empty text should produce no pixels"
    print("  [PASS] Empty text handled")

    # Single character
    wave = TextWaveEffect("A", x_start=0, speed=0)
    pixels = wave.step()
    assert len(pixels) > 0, "Single character should produce pixels"
    print("  [PASS] Single character handled")

    # Very large amplitude (should clip to display bounds)
    wave = TextWaveEffect("TEST", x_start=0, speed=0, wave_amplitude=10.0)
    pixels = wave.step()
    # Pixels should be filtered to valid coordinates
    for x, y, b in pixels:
        assert 0 <= y < 7, f"Pixel y={y} should be within display bounds"
    print("  [PASS] Large amplitude clipped correctly")

    print("[PASS] Edge case tests passed")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("TextWaveEffect Unit Tests")
        print("=" * 60)

        test_basic_wave()
        test_static_wave()
        test_layering()
        test_edge_cases()

        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
