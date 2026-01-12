# scrollphathd interaction + text rasterization
import scrollphathd
from contextlib import contextmanager

from contextlib import contextmanager

@contextmanager
def capture_pixels():
    """This safely hijacks rendering and restores it afterward."""
    captured = {}

    original_set_pixel = scrollphathd.set_pixel

    def fake_set_pixel(x, y, b):
        if b > 0:
            captured[(x, y)] = max(captured.get((x, y), 0.0), b)

    scrollphathd.set_pixel = fake_set_pixel
    try:
        yield captured
    finally:
        scrollphathd.set_pixel = original_set_pixel