#!/usr/bin/env python3
"""
EffectsEngine - Usage Examples

Demonstrates all 24 effects available in the EffectsEngine.
Each example shows how to configure and run individual effects
or combine them using LayeredEffect with blend modes.

Run these on actual hardware with Scroll pHAT HD connected.
"""

import os
import scrollphathd
from effects import (
    Sparkle, SparkleField, Comet, WaveRipple, ExpandingBox,
    SpiralSweep, ScannerSweep, ZigZagSweep, PulseFade,
    TextScroller, TextRevealEffect, TextWaveEffect, TextRainbowEffect, TextFadeEffect,
    PacMan, Ghost, PelletRow, PacManScene,
    TetrisScene,
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

def example_text_fade_basic():
    """Example 14: Text that fades in, holds, then fades out."""
    print("Example 14: Text Fade - Basic")

    fade = TextFadeEffect(
        "HELLO",
        x_start=0,
        y_pos=1,
        speed=0,  # Static text
        fade_in_frames=25,
        hold_frames=50,
        fade_out_frames=25,
        min_brightness=0.0,
        max_brightness=1.0
    )

    runner = EffectRunner(fade, fps=20)
    runner.run(frames=120)


def example_text_fade_scrolling():
    """Example 15: Scrolling text with fade effect."""
    print("Example 15: Text Fade - Scrolling")

    fade_scroll = TextFadeEffect(
        "Max and KiKi",
        speed=0.5,
        y_pos=1,
        fade_in_frames=30,
        hold_frames=40,
        fade_out_frames=30,
        min_brightness=0.1,
        max_brightness=1.0
    )

    runner = EffectRunner(fade_scroll, fps=20)
    runner.run(frames=250)

# This looks amazing!
def example_text_fade_layered():
    """Example 16: Fading text layered over sparkle field."""
    print("Example 16: Text Fade - Layered")

    from scrollphathd.fonts import font3x5

    fade_text = TextFadeEffect(
        "STARS",
        x_start=1,
        y_pos=1,
        speed=0,
        fade_in_frames=20,
        hold_frames=60,
        fade_out_frames=20,
        min_brightness=0.0,
        max_brightness=1.0,
        font=font3x5,
        loop=True
    )

    scene = LayeredEffect(
        Layer(SparkleField(density=20, speed_range=(15, 30)), BlendMode.ADD),
        Layer(fade_text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=200)


def example_text_scroll():
    """Example 14: Scrolling text message."""
    print("Example 14: Scrolling Text")

    text = TextScroller("Max and KiKi", speed=0.5)

    runner = EffectRunner(text, fps=20)
    runner.run(frames=100)


def example_text_static():
    """Example 15: Static text label."""
    print("Example 15: Static Text")

    text = TextScroller("Max", speed=0)

    runner = EffectRunner(text, fps=20)
    runner.run(frames=60)


def example_text_looping():
    """Example 16: Looping marquee text."""
    print("Example 16: Looping Text")

    text = TextScroller("*** KiKi ***", speed=0.75, loop=True)

    runner = EffectRunner(text, fps=20)
    runner.run(frames=200)

#TODO: Adjust, Does not work wellbecause  normal comet hits the same spots each time and doesnt light the whole text
def example_text_reveal_comet():
    """Example 17: Text revealed pixel-by-pixel by bouncing comet."""
    print("Example 17: Text Reveal - Comet")

    # Create bouncing comet that will reveal the text
    comet = Comet(x=0, y=0, dx=1, dy=1, tail_length=6, bounce=True)

    # Text reveal effect - shows revealer and revealed text
    text_reveal = TextRevealEffect(
        text="Max",
        revealer=comet,
        x_pos=2,
        y_pos=2,
        brightness=1.0,
        show_revealer=True
    )

    runner = EffectRunner(text_reveal, fps=20)
    runner.run(frames=250)


def example_text_reveal_scanner():
    """Example 18: Text revealed line-by-line by vertical scanner."""
    print("Example 18: Text Reveal - Scanner")

    # Create vertical scanner that will reveal the text
    scanner = ScannerSweep(horizontal=False, speed=1, trail_length=4, bounce=True)

    # Text reveal effect
    text_reveal = TextRevealEffect(
        text="KiKi",
        revealer=scanner,
        x_pos=1,
        y_pos=1,
        brightness=1.0,
        show_revealer=True
    )

    runner = EffectRunner(text_reveal, fps=20)
    runner.run(frames=200)


def example_text_reveal_multi_comet():
    """Example 19: Text revealed by multiple comets working together."""
    print("Example 19: Text Reveal - Multi Comet")

    from scrollphathd.fonts import font3x5

    # Create multiple comets as the revealer
    comet1 = Comet(0, 0, dx=1, dy=0.5, tail_length=4, bounce=True)
    comet2 = Comet(16, 6, dx=-0.8, dy=-0.6, tail_length=5, bounce=True)

    # Combine comets into one revealer effect
    multi_revealer = LayeredEffect(
        Layer(comet1, BlendMode.MAX),
        Layer(comet2, BlendMode.MAX)
    )

    # Text reveal with multiple comets
    text_reveal = TextRevealEffect(
        text="KiKi",
        revealer=multi_revealer,
        x_pos=2,
        y_pos=2,
        font=font3x5,
        brightness=1.0,
        show_revealer=True
    )

    runner = EffectRunner(text_reveal, fps=20)
    runner.run(frames=300)


def example_text_wave():
    """Example 20: Scrolling text with wave animation."""
    print("Example 20: Text Wave - Scrolling")

    wave = TextWaveEffect(
        "Max",
        speed=0.5,
        wave_speed=0.1,
        wave_amplitude=1.0,
        wave_length=12.0
    )

    runner = EffectRunner(wave, fps=20)
    runner.run(frames=200)


def example_text_wave_static():
    """Example 21: Static text with wave animation."""
    print("Example 21: Text Wave - Static")

    wave = TextWaveEffect(
        "KiKi",
        x_start=0,
        y_pos=1,
        speed=0,
        wave_speed=0.08,
        wave_amplitude=1.0,
        wave_length=14.0
    )

    runner = EffectRunner(wave, fps=20)
    runner.run(frames=150)


def example_text_wave_layered():
    """Example 22: Wave text layered over sparkle field."""
    print("Example 22: Text Wave - Layered")

    from scrollphathd.fonts import font3x5

    wave_text = TextWaveEffect(
        "Max",
        y_pos=1,
        speed=0.4,
        wave_speed=0.09,
        wave_amplitude=0.8,
        wave_length=12.0,
        font=font3x5,
        brightness=1.0
    )

    scene = LayeredEffect(
        Layer(SparkleField(density=30, speed_range=(15, 30)), BlendMode.MAX),
        Layer(wave_text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=200)


def example_text_rainbow():
    """Example 23: Scrolling text with subtle brightness shimmer effect."""
    print("Example 23: Text Rainbow - Scrolling")

    from effects import TextRainbowEffect

    rainbow = TextRainbowEffect(
        "KiKi",
        speed=0.5,
        wave_speed=0.15,
        wave_length=8.0,
        min_brightness=0.6,  # Subtle shimmer (default)
        max_brightness=1.0
    )

    runner = EffectRunner(rainbow, fps=20)
    runner.run(frames=200)


def example_text_rainbow_static():
    """Example 24: Static text with shimmering brightness wave."""
    print("Example 24: Text Rainbow - Static")

    from effects import TextRainbowEffect

    shimmer = TextRainbowEffect(
        "Max",
        x_start=0,
        y_pos=1,
        speed=0,
        wave_speed=0.2,
        wave_length=6.0,
        min_brightness=0.5,  # Slightly more pronounced
        max_brightness=1.0
    )

    runner = EffectRunner(shimmer, fps=20)
    runner.run(frames=150)


def example_text_rainbow_layered():
    """Example 25: Rainbow text layered over sparkle field."""
    print("Example 25: Text Rainbow - Layered")

    from scrollphathd.fonts import font3x5
    from effects import TextRainbowEffect

    rainbow_text = TextRainbowEffect(
        "KiKi",
        y_pos=1,
        speed=0.4,
        wave_speed=0.18,
        wave_length=7.0,
        min_brightness=0.5,  # Readable shimmer
        max_brightness=1.0,
        font=font3x5
    )

    scene = LayeredEffect(
        Layer(SparkleField(density=20, speed_range=(15, 30)), BlendMode.ADD),
        Layer(rainbow_text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=200)


###############################################################################
# GAME EFFECTS
###############################################################################

def example_pacman():
    """Example 23: Animated Pac-Man character."""
    print("Example 23: Pac-Man")

    pacman = PacMan(x=0, y=3, x_speed=0.25, wrap=False)

    runner = EffectRunner(pacman, fps=20)
    runner.run(frames=150)


def example_ghost():
    """Example 24: Animated ghost character."""
    print("Example 24: Ghost")

    ghost = Ghost(x=-7, y=2, x_speed=0.2)

    runner = EffectRunner(ghost, fps=20)
    runner.run(frames=150)


def example_pellet_row():
    """Example 25: Row of pellets."""
    print("Example 25: Pellet Row")

    pellets = PelletRow(y=3)

    runner = EffectRunner(pellets, fps=20)
    runner.run(frames=60)


def example_pacman_scene():
    """Example 26: Complete Pac-Man scene with pellets and ghost."""
    print("Example 26: Pac-Man Scene")

    scene = PacManScene(
        pellets=PelletRow(y=3),
        pacman=PacMan(x=0, y=3, x_speed=0.25, wrap=False),
        ghost=Ghost(x=-7, y=2, x_speed=0.15)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=200)


def example_tetris():
    """Example 27: Continuous Tetris - fills screen, blinks, clears, repeats."""
    print("Example 27: Continuous Tetris (loops when full)")

    # Default loop=True: pieces fall until screen full, then blink and restart
    scene = TetrisScene(
        base_fall_speed=0.15,
        speed_increment=0.01,
        blink_frames=8,
        full_blink_frames=12
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=800)  # Watch it fill up, blink, and restart


def example_tetris_fast():
    """Example 28: Fast continuous Tetris."""
    print("Example 28: Fast Continuous Tetris")

    scene = TetrisScene(
        base_fall_speed=0.25,
        speed_increment=0.015,
        blink_frames=6,
        full_blink_frames=10
    )

    runner = EffectRunner(scene, fps=25)
    runner.run(frames=1000)


def example_tetris_fixed():
    """Example 29: Fixed piece count Tetris (non-looping)."""
    print("Example 29: Fixed Tetris (15 pieces, no loop)")

    scene = TetrisScene(
        num_pieces=15,
        base_fall_speed=0.18,
        speed_increment=0.02,
        loop=False  # Stops after num_pieces
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=500)


def example_tetris_layered():
    """Example 30: Continuous Tetris with sparkle background."""
    print("Example 30: Tetris + Sparkles")

    tetris = TetrisScene(
        base_fall_speed=0.18,
        speed_increment=0.01
    )

    scene = LayeredEffect(
        Layer(SparkleField(density=15, speed_range=(20, 40)), BlendMode.ADD),
        Layer(tetris, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=800)


###############################################################################
# LAYERED EFFECTS
###############################################################################

def example_layered_waves():
    """Example 27: Multiple overlapping wave ripples."""
    print("Example 27: Layered Waves")

    scene = LayeredEffect(
        Layer(WaveRipple(8, 3, speed=0.7), BlendMode.OVERWRITE),
        Layer(WaveRipple(3, 1, speed=0.5), BlendMode.MAX),
        Layer(WaveRipple(12, 5, speed=0.6), BlendMode.ALPHA_SOFT)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=150)


def example_layered_comets():
    """Example 28: Multiple comets with different blend modes."""
    print("Example 28: Layered Comets")

    scene = LayeredEffect(
        Layer(Comet(0, 0, dx=1, dy=1, tail_length=8, bounce=True), BlendMode.MAX),
        Layer(Comet(16, 6, dx=-1, dy=-1, tail_length=8, bounce=True), BlendMode.ADD)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=150)


def example_sparkle_field_with_comet():
    """Example 29: Sparkle field background with comet overlay."""
    print("Example 29: SparkleField + Comet")

    scene = LayeredEffect(
        Layer(Comet(0, 0, dx=1, dy=1, tail_length=10, bounce=True), BlendMode.OVERWRITE),
        Layer(SparkleField(density=40, speed_range=(15, 30)), BlendMode.ADD)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=200)


def example_text_with_sparkle_field():
    """Example 30: Text scrolling over sparkle field."""
    print("Example 30: Text + SparkleField")

    text = TextScroller("Max", y_pos=1, speed=0.4, brightness=1.0)

    scene = LayeredEffect(
        Layer(SparkleField(density=40, speed_range=(15, 30)), BlendMode.MAX),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=180)


def example_text_with_wave():
    """Example 31: Text with expanding wave background."""
    print("Example 31: Text + Wave")

    text = TextScroller("KiKi", y_pos=1, speed=0.3)
    wave = WaveRipple(cx=8, cy=3, speed=0.5)

    scene = LayeredEffect(
        Layer(wave, BlendMode.MAX),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=150)


def example_text_with_scanner():
    """Example 32: Text with scanner sweep."""
    print("Example 32: Text + Scanner")

    from scrollphathd.fonts import font3x5

    text = TextScroller("Max", x_start=0, y_pos=2, speed=0, font=font3x5)
    scanner = ScannerSweep(horizontal=False, speed=1, trail_length=4, bounce=True)

    scene = LayeredEffect(
        Layer(scanner, BlendMode.MAX),
        Layer(text, BlendMode.MAX)
    )

    runner = EffectRunner(scene, fps=20)
    runner.run(frames=120)


def example_complex_layer():
    """Example 33: Complex multi-layer composition."""
    print("Example 33: Complex Layering")

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
    """Example 34: Pac-Man scene built with layers."""
    print("Example 34: Layered Pac-Man")

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
    """Example 35: Record animation to file for later playback."""
    print("Example 35: Bake Animation")

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
    """Example 36: Play back a recorded animation."""
    print("Example 36: Play Baked Animation")

    # Load and play the animation
    animation = BakedAnimation("demo_animation.anim.gz", loop=False)

    runner = EffectRunner(animation, fps=25)
    runner.run(frames=150)


def bake_all_animations():
    """
    Bake all example effects to .anim.gz files for later playback.

    Creates a 'baked_animations' directory and saves each effect as a
    compressed animation file. Each animation is recorded with enough
    frames for at least one full cycle plus ~1 second buffer.

    This is a utility function for pre-computing animations that can
    be played back later without recalculating effect logic.
    """
    from scrollphathd.fonts import font3x5

    # Create output directory
    output_dir = "baked_animations"
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("Baking All Animations")
    print("=" * 70)

    # Define all animations: (filename, effect, frames, fps)
    animations = [
        # ===== CORE VISUAL EFFECTS =====
        ("sparkle", Sparkle(x=8, y=3, speed=20), 75, 20),
        ("sparkle_field", SparkleField(density=30, speed_range=(10, 50)), 100, 20),
        ("sparkle_field_dense", SparkleField(density=50, speed_range=(5, 20)), 100, 20),
        ("comet_bounce", Comet(x=0, y=0, dx=1, dy=1, tail_length=6, bounce=True), 100, 20),
        ("comet_diagonal", Comet(x=8, y=3, dx=0.8, dy=0.6, tail_length=10, bounce=True), 100, 20),
        ("wave_ripple_center", WaveRipple(
            cx=DisplayConfig.width // 2,
            cy=DisplayConfig.height // 2,
            speed=0.7
        ), 80, 20),
        ("wave_ripple_corner", WaveRipple(cx=0, cy=0, speed=0.5, max_radius=20), 100, 20),
        ("expanding_box", ExpandingBox(
            cx=DisplayConfig.width // 2,
            cy=DisplayConfig.height // 2,
            speed=0.5
        ), 80, 20),
        ("spiral_sweep", SpiralSweep(
            cx=DisplayConfig.width // 2,
            cy=DisplayConfig.height // 2,
            speed=0.3
        ), 150, 20),
        ("scanner_horizontal", ScannerSweep(
            horizontal=True, speed=1, trail_length=6, bounce=True
        ), 80, 20),
        ("scanner_vertical", ScannerSweep(
            horizontal=False, speed=1, trail_length=4, bounce=True
        ), 60, 20),
        ("zigzag_sweep", ZigZagSweep(speed=1, trail_length=6, bounce=True), 150, 20),
        ("pulse_fade", PulseFade(speed=0.08, repeat=True), 150, 20),

        # ===== TEXT EFFECTS =====
        ("text_fade_static", TextFadeEffect(
            "HELLO", x_start=0, y_pos=1, speed=0,
            fade_in_frames=25, hold_frames=50, fade_out_frames=25
        ), 125, 20),
        ("text_fade_scrolling", TextFadeEffect(
            "Max and KiKi", speed=0.5, y_pos=1,
            fade_in_frames=30, hold_frames=40, fade_out_frames=30
        ), 275, 20),
        ("text_scroller", TextScroller("Max and KiKi", speed=0.5), 150, 20),
        ("text_static", TextScroller("Max", speed=0), 80, 20),
        ("text_looping", TextScroller("*** KiKi ***", speed=0.75, loop=True), 200, 20),
        ("text_reveal_comet", TextRevealEffect(
            text="Max",
            revealer=Comet(x=0, y=0, dx=1, dy=1, tail_length=6, bounce=True),
            x_pos=2, y_pos=2, brightness=1.0, show_revealer=True
        ), 275, 20),
        ("text_reveal_scanner", TextRevealEffect(
            text="KiKi",
            revealer=ScannerSweep(horizontal=False, speed=1, trail_length=4, bounce=True),
            x_pos=1, y_pos=1, brightness=1.0, show_revealer=True
        ), 225, 20),
        ("text_wave", TextWaveEffect(
            "Max", speed=0.5, wave_speed=0.1, wave_amplitude=1.0, wave_length=12.0
        ), 225, 20),
        ("text_wave_static", TextWaveEffect(
            "KiKi", x_start=0, y_pos=1, speed=0,
            wave_speed=0.08, wave_amplitude=1.0, wave_length=14.0
        ), 175, 20),
        ("text_rainbow", TextRainbowEffect(
            "KiKi", speed=0.5, wave_speed=0.15, wave_length=8.0,
            min_brightness=0.6, max_brightness=1.0
        ), 225, 20),
        ("text_rainbow_static", TextRainbowEffect(
            "Max", x_start=0, y_pos=1, speed=0,
            wave_speed=0.2, wave_length=6.0, min_brightness=0.5, max_brightness=1.0
        ), 175, 20),

        # ===== GAME SCENES (Full scenes only) =====
        ("pacman_scene", PacManScene(
            pellets=PelletRow(y=3),
            pacman=PacMan(x=0, y=3, x_speed=0.25, wrap=False),
            ghost=Ghost(x=-7, y=2, x_speed=0.15)
        ), 225, 20),
        ("tetris_scene", TetrisScene(
            base_fall_speed=0.15, speed_increment=0.01,
            blink_frames=8, full_blink_frames=12
        ), 500, 20),
        ("tetris_fast", TetrisScene(
            base_fall_speed=0.25, speed_increment=0.015,
            blink_frames=6, full_blink_frames=10
        ), 400, 25),

        # ===== LAYERED EFFECTS =====
        ("layered_waves", LayeredEffect(
            Layer(WaveRipple(8, 3, speed=0.7), BlendMode.OVERWRITE),
            Layer(WaveRipple(3, 1, speed=0.5), BlendMode.MAX),
            Layer(WaveRipple(12, 5, speed=0.6), BlendMode.ALPHA_SOFT)
        ), 175, 20),
        ("layered_comets", LayeredEffect(
            Layer(Comet(0, 0, dx=1, dy=1, tail_length=8, bounce=True), BlendMode.MAX),
            Layer(Comet(16, 6, dx=-1, dy=-1, tail_length=8, bounce=True), BlendMode.ADD)
        ), 175, 20),
        ("sparkle_comet", LayeredEffect(
            Layer(Comet(0, 0, dx=1, dy=1, tail_length=10, bounce=True), BlendMode.OVERWRITE),
            Layer(SparkleField(density=40, speed_range=(15, 30)), BlendMode.ADD)
        ), 225, 20),
        ("text_sparkle_field", LayeredEffect(
            Layer(SparkleField(density=40, speed_range=(15, 30)), BlendMode.MAX),
            Layer(TextScroller("Max", y_pos=1, speed=0.4, brightness=1.0), BlendMode.MAX)
        ), 200, 20),
        ("text_wave_bg", LayeredEffect(
            Layer(WaveRipple(cx=8, cy=3, speed=0.5), BlendMode.MAX),
            Layer(TextScroller("KiKi", y_pos=1, speed=0.3), BlendMode.MAX)
        ), 175, 20),
        ("complex_layer", LayeredEffect(
            Layer(WaveRipple(8, 3, speed=0.7), BlendMode.OVERWRITE),
            Layer(WaveRipple(3, 1, speed=0.5), BlendMode.MAX),
            Layer(SparkleField(density=15, speed_range=(20, 40)), BlendMode.ALPHA_SOFT),
            Layer(Comet(0, 0, dx=1, dy=1, tail_length=6, bounce=True), BlendMode.ALPHA_HARD),
            Layer(Comet(16, 6, dx=-0.8, dy=-0.6, tail_length=6, bounce=True), BlendMode.ALPHA_HARD)
        ), 225, 20),

        # ===== TEXT LAYERED EFFECTS =====
        ("text_fade_layered", LayeredEffect(
            Layer(SparkleField(density=20, speed_range=(15, 30)), BlendMode.ADD),
            Layer(TextFadeEffect(
                "STARS", x_start=1, y_pos=1, speed=0, font=font3x5,
                fade_in_frames=20, hold_frames=60, fade_out_frames=20, loop=True
            ), BlendMode.MAX)
        ), 200, 20),
        ("text_wave_layered", LayeredEffect(
            Layer(SparkleField(density=30, speed_range=(15, 30)), BlendMode.MAX),
            Layer(TextWaveEffect(
                "Max", y_pos=1, speed=0.4, wave_speed=0.09,
                wave_amplitude=0.8, wave_length=12.0, font=font3x5, brightness=1.0
            ), BlendMode.MAX)
        ), 200, 20),
        ("text_rainbow_layered", LayeredEffect(
            Layer(SparkleField(density=20, speed_range=(15, 30)), BlendMode.ADD),
            Layer(TextRainbowEffect(
                "KiKi", y_pos=1, speed=0.4, wave_speed=0.18, wave_length=7.0,
                min_brightness=0.5, max_brightness=1.0, font=font3x5
            ), BlendMode.MAX)
        ), 200, 20),
    ]

    # Bake each animation
    total = len(animations)
    for i, (name, effect, frames, fps) in enumerate(animations, 1):
        filepath = os.path.join(output_dir, f"{name}.anim.gz")
        print(f"[{i}/{total}] Baking {name} ({frames} frames @ {fps} fps)...")

        recorder = AnimationRecorder(effect, fps=fps)
        recorder.record(frames=frames)
        recorder.save(filepath)

    print("\n" + "=" * 70)
    print(f"Baked {total} animations to '{output_dir}/'")
    print("=" * 70)


def play_all_baked_animations():
    """
    Play back all baked animations from the 'baked_animations' directory.

    Iterates through all .anim.gz files in the baked_animations folder
    and plays each one in sequence. Useful for previewing all pre-baked
    animations on the hardware.
    """
    import glob
    import gzip
    import json

    output_dir = "baked_animations"

    # Find all baked animation files
    pattern = os.path.join(output_dir, "*.anim.gz")
    anim_files = sorted(glob.glob(pattern))

    if not anim_files:
        print(f"No baked animations found in '{output_dir}/'")
        print("Run bake_all_animations() first to create them.")
        return

    print("=" * 70)
    print("Playing All Baked Animations")
    print("=" * 70)

    total = len(anim_files)
    for i, filepath in enumerate(anim_files, 1):
        name = os.path.basename(filepath).replace(".anim.gz", "")
        print(f"\n[{i}/{total}] Playing: {name}")

        try:
            # Read metadata from file to get fps and frame count
            with gzip.open(filepath, "rt", encoding="utf-8") as f:
                data = json.load(f)
            fps = data.get("fps", 20)
            frame_count = data.get("frame_count", len(data.get("frames", [])))

            animation = BakedAnimation(filepath, loop=False)
            runner = EffectRunner(animation, fps=fps, invert=True)
            runner.run(frames=frame_count)
        except Exception as e:
            print(f"  Error playing {name}: {e}")
            continue

        scrollphathd.clear()
        scrollphathd.show()

    print("\n" + "=" * 70)
    print(f"Finished playing {total} animations")
    print("=" * 70)


###############################################################################
# MAIN EXECUTION
###############################################################################

def run_all_examples():
    """Run all effect examples in sequence."""
    print("=" * 70)
    print("EffectsEngine - Complete Effect Gallery")
    print("=" * 70)

    examples = [
        # Text effects
        example_text_fade_basic,
        example_text_fade_scrolling,
        example_text_fade_layered,
        example_text_rainbow,
        example_text_rainbow_static,
        example_text_rainbow_layered,
        example_text_wave,
        example_text_wave_static,
        example_text_wave_layered,
        example_text_scroll,
        example_text_static,
        example_text_looping,
        example_text_reveal_comet,
        example_text_reveal_scanner,
        example_text_reveal_multi_comet,
        
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


        # Game effects
        example_tetris,
        example_tetris_fast,
        example_tetris_fixed,
        example_tetris_layered,
        example_pacman,
        example_ghost,
        example_pellet_row,
        example_pacman_scene,

        # Layered effects
        example_layered_waves,
        example_layered_comets,
        example_sparkle_field_with_comet,
        example_text_with_sparkle_field,
        example_text_with_wave,
        example_text_with_scanner,
        example_complex_layer,
        example_pacman_layered,

        # Animation recording
        example_bake_animation,
        example_play_baked_animation,
        # bake_all_animations,  # Utility: bakes all effects to files (not a visual demo)
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
        scrollphathd.set_brightness(0.5)

        # Uncomment if your display is upside down
        scrollphathd.rotate(degrees=180)

        # Run all examples in sequence
        # run_all_examples()

        # Bake all examples in sequence
        # bake_all_animations()

        # Play all Baked examples
        play_all_baked_animations()

        # Or uncomment individual examples to run them:
        # example_tetris_fast()
        # example_expanding_box()
        # example_sparkle_field()
        # example_comet()
        # example_text_with_sparkle_field()
        # example_complex_layer()
        # example_text_reveal_multi_comet()

        # Or run the legacy demo function:
        # demo_all_effects()

    except KeyboardInterrupt:
        scrollphathd.clear()
        scrollphathd.show()
        print("\nExiting!")
