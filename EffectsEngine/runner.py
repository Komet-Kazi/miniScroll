# EffectRunner + AnimationRecorder
# Run an effect and display on the matrix in realtime
import time
import json
import gzip
import scrollphathd
from effects import BaseEffect

###------------------------------------------------------------------------------###
# Helper Functions

def clamp01(v: float) -> float:
    """
    Clamp and normalize a value to the range [0.0, 1.0].

    Any negative input is converted to positive using abs().
    Values greater than 1.0 are clamped to 1.0.

    This is used to ensure LED brightness values are always valid
    before being sent to the display hardware.
    """
    return max(0.0, min(1.0, abs(v)))


class EffectRunner:
    """
    Drives an effect in real-time and renders it to the LED matrix.

    Handles frame timing, brightness normalization, optional inversion,
    and pushing pixel data to the Scroll pHAT HD hardware.

    Args:
        effect (BaseEffect): Effect to run.
        fps (float): Frames per second.
        invert (bool): Whether to invert brightness values.
    """
    def __init__(self, effect: BaseEffect, fps: float = 20, invert: bool = False):
        self.effect = effect
        self.delay = 1.0 / fps
        self.invert = invert

    def apply_transformation(self, b:float) -> float:
        if self.invert:
            return 1.0 - b
        return b

    def run(self, frames: int | None = None):
        count = 0

        while frames is None or count < frames:
            frame_pixels = {(x, y): b for x, y, b in self.effect.step()}

            scrollphathd.clear()

            for x in range(scrollphathd.width):
                for y in range(scrollphathd.height):
                    b = frame_pixels.get((x, y), 0.0)
                    b = self.apply_transformation(b)
                    b = clamp01(b)
                    scrollphathd.set_pixel(x, y, b)

            scrollphathd.show()
            time.sleep(self.delay)
            count += 1

###-------------------------------------------------------------------------------###
# AnimationRecorder a replacement for the EffectRunner Class that saves frames to a file to be read from later.

import json
import gzip

class AnimationRecorder:
    """
    Records frames from an effect and saves them to disk.

    Intended for pre-baking animations so they can be replayed later
    without recomputing effect logic.

    Args:
        effect (BaseEffect): Effect to record.
        fps (float): Playback frame rate metadata.
    """
    def __init__(self, effect: BaseEffect, fps: float = 25):
        self.effect = effect
        self.fps = fps
        self.frames: list[list[tuple[int, int, float]]] = []

    def record(self, frames: int | None = None):
        """
        Record frames from an effect.
        If frames is None, record until effect.is_done().
        """
        if frames is None and not hasattr(self.effect, "is_done"):
            raise ValueError("Finite effect required when frames=None")

        self.effect.reset()
        count = 0

        while frames is None or count < frames:
            frame = self.effect.step()
            self.frames.append(frame)

            count += 1
            if frames is None and self.effect.is_done():
                break

    def save(self, filename: str):
        data = {
            "version": 1,
            "width": scrollphathd.width,
            "height": scrollphathd.height,
            "fps": self.fps,
            "frame_count": len(self.frames),
            "frames": self.frames,
        }

        with gzip.open(filename, "wt", encoding="utf-8") as f:
            json.dump(data, f)

        print(f"Saved animation: {filename} ({len(self.frames)} frames)")
