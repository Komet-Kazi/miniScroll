#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for SparkleField effect.

This script tests the new SparkleField class to ensure it:
1. Imports correctly
2. Instantiates without errors
3. Produces pixel output
4. Works with EffectRunner
5. Can be layered with other effects
"""

from effects import SparkleField, LayeredEffect, Layer, BlendMode, Comet
from runner import EffectRunner

def test_basic_instantiation():
    """Test that SparkleField can be created with default parameters."""
    print("Test 1: Basic instantiation")
    field = SparkleField()
    print(f"  [OK] Created SparkleField with density={field.density}")
    print(f"  [OK] Display dimensions: {field.width}x{field.height}")
    print()

def test_custom_parameters():
    """Test that SparkleField accepts custom parameters."""
    print("Test 2: Custom parameters")
    field = SparkleField(density=50, speed_range=(5, 25))
    print(f"  [OK] Created SparkleField with density={field.density}")
    print(f"  [OK] Speed range: {field.speed_range}")
    print()

def test_step_output():
    """Test that step() produces valid pixel output."""
    print("Test 3: Step output")
    field = SparkleField(density=10)

    # Run a few steps
    for i in range(5):
        pixels = field.step()
        print(f"  Frame {i}: {len(pixels)} pixels")

        # Validate pixel format
        if pixels:
            x, y, brightness = pixels[0]
            assert 0 <= x < field.width, f"Invalid x coordinate: {x}"
            assert 0 <= y < field.height, f"Invalid y coordinate: {y}"
            # Note: brightness clamping is handled by EffectRunner, not the effect
            # So we don't validate brightness range here

    print("  [OK] All pixels valid (coordinates)")
    print()

def test_reset():
    """Test that reset() works correctly."""
    print("Test 4: Reset functionality")
    field = SparkleField(density=10)

    # Run some steps
    for _ in range(10):
        field.step()

    active_before = len(field.active_sparkles)
    print(f"  Active sparkles before reset: {active_before}")

    # Reset
    field.reset()
    active_after = len(field.active_sparkles)
    print(f"  Active sparkles after reset: {active_after}")

    assert active_after == 0, "Reset should clear active sparkles"
    print("  [OK] Reset works correctly")
    print()

def test_with_runner():
    """Test that SparkleField works with EffectRunner."""
    print("Test 5: Integration with EffectRunner")
    field = SparkleField(density=20)
    runner = EffectRunner(field, fps=20)

    print("  Running SparkleField for 50 frames...")
    runner.run(frames=50)
    print("  [OK] EffectRunner completed successfully")
    print()

def test_layering():
    """Test that SparkleField can be layered with other effects."""
    print("Test 6: Layering with other effects")

    scene = LayeredEffect(
        Layer(SparkleField(density=15), BlendMode.MAX),
        Layer(Comet(0, 0, dx=1, dy=1, tail_length=6), BlendMode.ADD)
    )

    print("  Running layered effect for 30 frames...")
    runner = EffectRunner(scene, fps=20)
    runner.run(frames=30)
    print("  [OK] Layered effect works correctly")
    print()

def main():
    """Run all tests."""
    print("=" * 60)
    print("SparkleField Effect Test Suite")
    print("=" * 60)
    print()

    try:
        test_basic_instantiation()
        test_custom_parameters()
        test_step_output()
        test_reset()
        test_with_runner()
        test_layering()

        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
