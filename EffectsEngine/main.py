#!/usr/bin/env python3
"""
EffectsEngine - Usage Examples

Demonstrates all 23 effects available in the EffectsEngine.
Each example shows how to configure and run individual effects
or combine them using LayeredEffect with blend modes.

Run these on actual hardware with Scroll pHAT HD connected.
"""

import scrollphathd
from effects import (
    Sparkle, SparkleField, Comet, WaveRipple, ExpandingBox,
    SpiralSweep, ScannerSweep, ZigZagSweep, PulseFade,
    TextScroller, PacMan, Ghost, PelletRow, PacManScene,
    LayeredEffect, Layer, BlendMode, BakedAnimation
)
from runner import EffectRunner, AnimationRecorder, DisplayConfig
from random import randint


###############################################################################
# CORE VISUAL EFFECTS
###############################################################################

def example_sparkle():
    """Example 1: Single sparkle at random position."""
    print("Example 1: Sparkle")

    x = randint(0, DisplayConfig.width - 1)
    y = randint(0, DisplayConfig.height - 1)
    sparkle = Sparkle(x, y, speed=20)

    runner = EffectRunner(sparkle, fps=20)
    runner.run(frames=100)


def example_sparkle_field():
    """Example 2: Field of multiple sparkles across the display."""
    print("Example 2: SparkleField")

    field = SparkleField(density=30, speed_range=(10, 50))

    runner = EffectRunner(field, fps=20)
    runner.run(frames=150)


def example_sparkle_field_dense():
    """Example 3: Dense, fast-twinkling sparkle field."""
    print("Example 3: Dense SparkleField")

    field = SparkleField(density=50, speed_range=(5, 20))

    runner = EffectRunner(field, fps=20)
    runner.run(frames=150)


def example_comet():
    """Example 4: Bouncing comet with trail."""
    print("Example 4: Comet")

    comet = Comet(x=0, y=0, dx=1, dy=1, tail_length=6, bounce=True)

    runner = EffectRunner(comet, fps=20)
    runner.run(frames=150)


def example_comet_diagonal():
    """Example 5: Fast diagonal comet."""
    print("Example 5: Diagonal Comet")

    comet = Comet(x=8, y=3, dx=0.8, dy=0.6, tail_length=10, bounce=True)

    runner = EffectRunner(comet, fps=20)
    runner.run(frames=150)


def example_wave_ripple():
    """Example 6: Expanding wave from center."""
    print("Example 6: WaveRipple")

    wave = WaveRipple(
        cx=DisplayConfig.width // 2,
        cy=DisplayConfig.height // 2,
        speed=0.7
    )

    runner = EffectRunner(wave, fps=20)
    runner.run(frames=120)


def example_wave_ripple_corner():
    """Example 7: Wave ripple from corner."""
    print("Example 7: Corner WaveRipple")

    wave = WaveRipple(cx=0, cy=0, speed=0.5, max_radius=20)

    runner = EffectRunner(wave, fps=20)
    runner.run(frames=120)


def example_expanding_box():
    """Example 8: Expanding rectangular outline."""
    print("Example 8: ExpandingBox")

    box = ExpandingBox(
        cx=DisplayConfig.width // 2,
        cy=DisplayConfig.height // 2,
        speed=0.5
    )

    runner = EffectRunner(box, fps=20)
    runner.run(frames=120)


def example_spiral_sweep():
    """Example 9: Spiral expanding from center."""
    print("Example 9: SpiralSweep")

    spiral = SpiralSweep(
        cx=DisplayConfig.width // 2,
        cy=DisplayConfig.height // 2,
        speed=0.3
    )

    runner = EffectRunner(spiral, fps=20)
    runner.run(frames=150)


def example_scanner_horizontal():
    """Example 10: Horizontal scanner sweep."""
    print("Example 10: Horizontal Scanner")

    scanner = ScannerSweep(
        horizontal=True,
        speed=1,
        trail_length=6,
        bounce=True
    )

    runner = EffectRunner(scanner, fps=20)
    runner.run(frames=100)


def example_scanner_vertical():
    """Example 11: Vertical scanner sweep."""
    print("Example 11: Vertical Scanner")

    scanner = ScannerSweep(
        horizontal=False,
        speed=1,
        trail_length=4,
        bounce=True
    )

    runner = EffectRunner(scanner, fps=20)
    runner.run(frames=100)


def example_zigzag_sweep():
    """Example 12: Zig-zag sweeping pattern."""
    print("Example 12: ZigZagSweep")

    zigzag = ZigZagSweep(speed=1, trail_length=6, bounce=True)

    runner = EffectRunner(zigzag, fps=20)
    runner.run(frames=150)


def example_pulse_fade():
    """Example 13: Global brightness pulse."""
    print("Example 13: PulseFade")

    pulse = PulseFade(speed=0.08, repeat=True)

    runner = EffectRunner(pulse, fps=20)
    runner.run(frames=120)


###############################################################################
# TEXT EFFECTS
###############################################################################

def example_text_scroll():
    """Example 14: Scrolling text message."""
    print("Example 14: Scrolling Text")

    text = TextScroller("HELLO WORLD", speed=0.5)

    runner = EffectRunner(text, fps=20)
    runner.run(frames=100)


def example_text_static():
    """Example 15: Static text label."""
    print("Example 15: Static Text")

    text = TextScroller("READY", x_start=0, y_pos=1, speed=0)

    runner = EffectRunner(text, fps=20)
    runner.run(frames=60)


def example_text_looping():
    """Example 16: Looping marquee text."""
    print("Example 16: Looping Text")

    text = TextScroller("*** LOOP ***", speed=0.75, loop=True)

    runner = EffectRunner(text, fps=20)
    runner.run(frames=200)


###############################################################################
# GAME EFFECTS
###############################################################################

def example_pacman():
    """Example 17: Animated Pac-Man character."""
    print("Example 17: Pac-Man")

    pacman = PacMan(x=0, y=3, x_speed=0.25, wrap=False)

    runner = EffectRunner(pacman, fps=20)
    runner.run(frames=150)


def example_ghost():
    """Example 18: Animated ghost character."""
    print("Example 18: Ghost")

    ghost = Ghost(x=-7, y=2, x_speed=0.2)

    runner = EffectRunner(ghost, fps=20)
    runner.run(frames=150)


def example_pellet_row():
    """Example 19: Row of pellets."""
    print("Example 19: Pellet Row")

    pellets = PelletRow(y=3)

    runner = EffectRunner(pellets, fps=20)
    runner.run(frames=60)


def example_pacman_scene():
    """Example 20: Complete Pac-Man scene with pellets and ghost."""
    print("Example 20: Pac-Man Scene")

    scene = PacManScene(
        pellets=PelletRow(y=3),
        pacman=PacMan(x=0, y=3, x_speed=0.25, wrap=False),
        ghost=Ghost(x=-7, y=2, x_speed=0.15)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=200)


###############################################################################
# LAYERED EFFECTS
###############################################################################

def example_layered_waves():
    """Example 21: Multiple overlapping wave ripples."""
    print("Example 21: Layered Waves")

    scene = LayeredEffect(
        Layer(WaveRipple(8, 3, speed=0.7), BlendMode.OVERWRITE),
        Layer(WaveRipple(3, 1, speed=0.5), BlendMode.MAX),
        Layer(WaveRipple(12, 5, speed=0.6), BlendMode.ALPHA_SOFT)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=150)


def example_layered_comets():
    """Example 22: Multiple comets with different blend modes."""
    print("Example 22: Layered Comets")

    scene = LayeredEffect(
        Layer(Comet(0, 0, dx=1, dy=1, tail_length=8, bounce=True), BlendMode.MAX),
        Layer(Comet(16, 6, dx=-1, dy=-1, tail_length=8, bounce=True), BlendMode.ADD)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=150)


def example_sparkle_field_with_comet():
    """Example 23: Sparkle field background with comet overlay."""
    print("Example 23: SparkleField + Comet")

    scene = LayeredEffect(
        Layer(SparkleField(density=20, speed_range=(15, 40)), BlendMode.ALPHA_SOFT),
        Layer(Comet(0, 0, dx=1, dy=1, tail_length=10, bounce=True), BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=200)


def example_text_with_sparkle_field():
    """Example 24: Text scrolling over sparkle field."""
    print("Example 24: Text + SparkleField")

    text = TextScroller("STARFIELD", y_pos=1, speed=0.4, brightness=1.0)

    scene = LayeredEffect(
        Layer(SparkleField(density=25, speed_range=(10, 40)), BlendMode.ALPHA_SOFT),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=180)


def example_text_with_wave():
    """Example 25: Text with expanding wave background."""
    print("Example 25: Text + Wave")

    text = TextScroller("WAVES", y_pos=1, speed=0.3)
    wave = WaveRipple(cx=8, cy=3, speed=0.5)

    scene = LayeredEffect(
        Layer(wave, BlendMode.ALPHA_SOFT),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=150)


def example_text_with_scanner():
    """Example 26: Text with scanner sweep."""
    print("Example 26: Text + Scanner")

    from scrollphathd.fonts import font3x5

    text = TextScroller("SCAN", x_start=0, y_pos=2, speed=0, font=font3x5)
    scanner = ScannerSweep(horizontal=False, speed=1, trail_length=4, bounce=True)

    scene = LayeredEffect(
        Layer(scanner, BlendMode.ALPHA_SOFT),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=120)


def example_complex_layer():
    """Example 27: Complex multi-layer composition."""
    print("Example 27: Complex Layering")

    scene = LayeredEffect(
        Layer(WaveRipple(8, 3, speed=0.7), BlendMode.OVERWRITE),
        Layer(WaveRipple(3, 1, speed=0.5), BlendMode.MAX),
        Layer(SparkleField(density=15, speed_range=(20, 40)), BlendMode.ALPHA_SOFT),
        Layer(Comet(0, 0, dx=1, dy=1, tail_length=6, bounce=True), BlendMode.ALPHA_HARD),
        Layer(Comet(16, 6, dx=-0.8, dy=-0.6, tail_length=6, bounce=True), BlendMode.ALPHA_HARD)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=200)


def example_pacman_layered():
    """Example 28: Pac-Man scene built with layers."""
    print("Example 28: Layered Pac-Man")

    scene = LayeredEffect(
        Layer(PelletRow(y=3), BlendMode.OVERWRITE),
        Layer(Ghost(x=-6, y=1, x_speed=0.2), BlendMode.MAX),
        Layer(PacMan(x=0, y=3, x_speed=0.25), BlendMode.OVERWRITE)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=200)


###############################################################################
# ANIMATION RECORDING
###############################################################################

def example_bake_animation():
    """Example 29: Record animation to file for later playback."""
    print("Example 29: Bake Animation")

    # Create an effect to record
    effect = LayeredEffect(
        Layer(WaveRipple(8, 3, speed=0.7), BlendMode.OVERWRITE),
        Layer(Comet(0, 0, dx=1, dy=1, tail_length=8, bounce=True), BlendMode.MAX)
    )

    # Record it
    recorder = AnimationRecorder(effect, fps=25)
    recorder.record(frames=150)
    recorder.save("demo_animation.anim.gz")

    print("  Animation saved to demo_animation.anim.gz")


def example_play_baked_animation():
    """Example 30: Play back a recorded animation."""
    print("Example 30: Play Baked Animation")

    # Load and play the animation
    animation = BakedAnimation("demo_animation.anim.gz", loop=False)

    runner = EffectRunner(animation, fps=25)
    runner.run(frames=150)


###############################################################################
# MAIN EXECUTION
###############################################################################

def run_all_examples():
    """Run all effect examples in sequence."""
    print("=" * 70)
    print("EffectsEngine - Complete Effect Gallery")
    print("=" * 70)

    examples = [
        # Core visual effects
        example_sparkle,
        example_sparkle_field,
        example_sparkle_field_dense,
        example_comet,
        example_comet_diagonal,
        example_wave_ripple,
        example_wave_ripple_corner,
        example_expanding_box, # a bit jittery
        example_spiral_sweep, #slow
        example_scanner_horizontal,
        example_scanner_vertical,
        example_zigzag_sweep,
        example_pulse_fade,

        # Text effects
        example_text_scroll,
        example_text_static,
        example_text_looping,

        # Game effects
        example_pacman,
        example_ghost,
        example_pellet_row,
        example_pacman_scene,

        # Layered effects
        example_layered_waves,
        example_layered_comets,
        example_sparkle_field_with_comet, # no sparkle field
        example_text_with_sparkle_field, # no sparkle field
        example_text_with_wave, # No wave
        example_text_with_scanner, # No Scan
        example_complex_layer,
        example_pacman_layered,

        # Animation recording
        example_bake_animation,
        example_play_baked_animation,
    ]

    try:
        # Initialize display
        scrollphathd.clear()
        scrollphathd.set_brightness(0.2)
        # Uncomment if your display is upside down
        # scrollphathd.rotate(degrees=180)

        for example_func in examples:
            print(f"\n--- Running: {example_func.__name__} ---")
            example_func()
            scrollphathd.clear()

        print("\n" + "=" * 70)
        print("All examples completed!")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    finally:
        scrollphathd.clear()
        scrollphathd.show()


###############################################################################
# LEGACY DEMO FUNCTIONS (for backwards compatibility)
###############################################################################

def demo_all_effects(fps: float = 25, frames_per_demo: int = 150):
    """
    Legacy function: Demonstrates effects in the old format.

    For new code, use run_all_examples() instead which follows
    the text_examples.py pattern.
    """
    scrollphathd.clear()

    effects_to_demo = [
        ("SparkleField", SparkleField(density=30)),
        ("PacManScene", PacManScene(
            PelletRow(y=3),
            PacMan(0, 3, x_speed=0.25, wrap=False),
            Ghost(-7, 2))),
        ("Layered_PacMan", LayeredEffect(
            Layer(PelletRow(y=3), BlendMode.OVERWRITE),
            Layer(Ghost(-6, 1, x_speed=0.2), BlendMode.MAX),
            Layer(PacMan(0, 3, x_speed=0.25), BlendMode.OVERWRITE))),
        ("ExpandingBox", ExpandingBox(cx=8, cy=3, speed=1)),
        ("SpiralSweep", SpiralSweep(cx=8, cy=3, speed=1)),
        ("Sparkle", Sparkle(randint(0, DisplayConfig.width-1),
                            randint(0, DisplayConfig.height-1))),
        ("Comet", Comet(0, 0, dx=1, dy=1, tail_length=6, bounce=True)),
        ("WaveRipple", WaveRipple(DisplayConfig.width//2, DisplayConfig.height//2, speed=0.7)),
        ("ScannerSweep", ScannerSweep(horizontal=True, speed=1, trail_length=6, bounce=True)),
        ("ZigZagSweep", ZigZagSweep(speed=1, trail_length=6, bounce=True)),
        ("PulseFade", PulseFade(speed=.05, repeat=True)),
        ("LayeredEffect", LayeredEffect(
            Layer(WaveRipple(8, 3, speed=0.7), BlendMode.OVERWRITE),
            Layer(WaveRipple(3, 8, speed=0.7), BlendMode.MAX),
            Layer(WaveRipple(5, 5, speed=0.7), BlendMode.ALPHA_SOFT),
            Layer(Comet(0, 0, dx=1, dy=2, tail_length=4, bounce=True), BlendMode.ALPHA_HARD),
            Layer(Comet(16, 0, dx=2, dy=1, tail_length=9, bounce=True), BlendMode.ALPHA_HARD)
        )),
    ]

    for name, effect in effects_to_demo:
        print(f"Running demo: {name}")
        effect.reset()
        runner = EffectRunner(effect, fps=fps, invert=False)
        runner.run(frames=frames_per_demo)


if __name__ == '__main__':
    """
    Main entry point - runs all effect examples.

    Uncomment individual examples below to run specific effects.
    """
    try:
        # Set display brightness
        scrollphathd.set_brightness(0.2)

        # Uncomment if your display is upside down
        scrollphathd.rotate(degrees=180)

        # Run all examples in sequence
        run_all_examples()

        # Or uncomment individual examples to run them:
        # example_sparkle_field()
        # example_comet()
        # example_text_with_sparkle_field()
        # example_complex_layer()

        # Or run the legacy demo function:
        # demo_all_effects()

    except KeyboardInterrupt:
        scrollphathd.clear()
        scrollphathd.show()
        print("\nExiting!")
