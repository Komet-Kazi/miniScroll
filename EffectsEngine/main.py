# demos / __main__ entrypoint
import scrollphathd

from effects import *
from runner import EffectRunner, AnimationRecorder

###-------------------------------------------------------------------------------###
# Examples
def demo_all_effects(fps: float = 25, frames_per_demo: int = 150):
    """
    Demonstrates all available effects and blending modes on Scroll pHAT HD.

    This function sequentially runs:
    - Sparkle
    - Comet
    - WaveRipple
    - ScannerSweep
    - ZigZagSweep
    - LayeredEffect combining multiple effects with different blend modes

    Args:
        fps (float): Frames per second for display update speed.
        frames_per_demo (int): Number of frames to run each effect.
    """
    # Configure display
    scrollphathd.clear()

    effects_to_demo = [
        ("PacManScene", PacManScene(
            PelletRow(y=3), 
            PacMan(0, 3, x_speed=0.25, wrap=False), 
            Ghost(-7, 2))),
        ("Layered_PacMan",LayeredEffect(
            Layer(PelletRow(y=3),BlendMode.OVERWRITE),
            Layer(Ghost(-6, 1, x_speed=0.2), BlendMode.MAX),
            Layer(PacMan(0, 3, x_speed=0.25), BlendMode.OVERWRITE))),
        ("ExpandingBox", ExpandingBox(cx=8, cy=3,speed=1)),
        ("SpiralSweep", SpiralSweep(cx=8, cy=3, speed=1)),
        ("Sparkle", Sparkle(randint(0, scrollphathd.width-1),
                            randint(0, scrollphathd.height-1))),
        ("Comet", Comet(0, 0, dx=1, dy=1, tail_length=6, bounce=True)),
        ("WaveRipple", WaveRipple(scrollphathd.width//2, scrollphathd.height//2, speed=0.7)),
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

def bake_all_effects(fps: float = 25, frames_to_save: int = 150):
    """
    Demonstrates all available effects and blending modes on Scroll pHAT HD.

    This function sequentially runs:
    - Sparkle
    - Comet
    - WaveRipple
    - ScannerSweep
    - ZigZagSweep
    - LayeredEffect combining multiple effects with different blend modes

    Args:
        fps (float): Frames per second for display update speed.
        frames_per_demo (int): Number of frames to run each effect.
    """
    # Configure display
    scrollphathd.clear()

    effects_to_bake= [
        ("PacManScene", PacManScene(
            PelletRow(y=3), 
            PacMan(0, 3, x_speed=0.25, wrap=False), 
            Ghost(-7, 2))),
        ("Layered_PacMan",LayeredEffect(
            Layer(PelletRow(y=3),BlendMode.OVERWRITE),
            Layer(Ghost(-6, 1, x_speed=0.2), BlendMode.MAX),
            Layer(PacMan(0, 3, x_speed=0.25), BlendMode.OVERWRITE))),
        ("ExpandingBox", ExpandingBox(cx=8, cy=3,speed=1)),
        ("SpiralSweep", SpiralSweep(cx=8, cy=3, speed=1)),
        ("Sparkle", Sparkle(randint(0, scrollphathd.width-1), randint(0, scrollphathd.height-1))),
        ("Comet", Comet(0, 0, dx=1, dy=1, tail_length=6, bounce=True)),
        ("WaveRipple", WaveRipple(scrollphathd.width//2, scrollphathd.height//2, speed=0.7)),
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

    try:
        for name, effect in effects_to_bake:
            print(f"Baking Effect: {name}")
            effect.reset()
            bake_animation(name, effect, fps, frames_to_save=frames_to_save)


    except KeyboardInterrupt:
        print("Demo interrupted, clearing display...")
    finally:
        scrollphathd.clear()
        scrollphathd.show()

def bake_animation(file_name: str, effect: BaseEffect, fps: float = 25, frames_to_save: int = 150):
    recorder = AnimationRecorder(effect, fps=fps)
    recorder.record(frames=frames_to_save)   # auto-stops when ripple is done
    recorder.save(f"{file_name}.anim.gz")

def demo_play_baked_animation(fps: float = 25, frames_to_play: int = 150):
    baked_animations = [
        "PacManScene.anim.gz",
        "Layered_PacMan.anim.gz",
        "ExpandingBox.anim.gz",
        "SpiralSweep.anim.gz",
        "PulseFade.anim.gz",
        "Sparkle.anim.gz",
        "Comet.anim.gz",
        "ScannerSweep.anim.gz",
        "LayeredEffect.anim.gz",
        "WaveRipple.anim.gz",
        "ZigZagSweep.anim.gz"]
    for baked_anim in baked_animations:
        anim = BakedAnimation(baked_anim, loop=False)
        runner = EffectRunner(anim, fps=fps,invert=False)
        runner.run(frames=frames_to_play)

###-------------------------------------------------------------------------------###

if __name__ == '__main__':
# Catches control-c and exits cleanly
    try:
        # Uncomment to turn off debugging
        ic.disable()

        # Set max brightness
        scrollphathd.set_brightness(0.2)

        # Uncomment the below if your display is upside down
        scrollphathd.rotate(degrees=180)

        # layered_pacman = LayeredEffect(
        #     Layer(PelletRow(y=3),BlendMode.OVERWRITE),
        #     Layer(Ghost(-6, 1, x_speed=0.2), BlendMode.MAX),
        #     Layer(PacMan(0, 3, x_speed=0.25), BlendMode.OVERWRITE))
        # layered_pacman.reset()
        # runner = EffectRunner(layered_pacman, fps=25, invert=False)
        # runner.run(frames=150)
                
        # text_mask = rasterize_string(
        #     "HELLO",
        #     x=1,
        #     y=2,
        #     brightness=1.0
        # )

        # text = RevealText(text_mask)

        # scanner = ScannerSweep(
        #     horizontal=True,
        #     speed=1,
        #     trail_length=4,
        #     bounce=False
        # )

        # scene = RevealTextScene(scanner, text, reveal_radius=0)

        # runner = EffectRunner(scene, fps=25)
        # runner.run()


        demo_all_effects()
        # bake_all_effects()
        # demo_play_baked_animation()
    

    except KeyboardInterrupt:
        scrollphathd.clear()
        scrollphathd.show()
        print("Exiting!")