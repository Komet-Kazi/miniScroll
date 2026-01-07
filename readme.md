https://docs.pimoroni.com/scrollphathd/

### ScrollPhat Commands At A Glance

    scrollphathd.clear()

    scrollphathd.clear_rect(x, y, width, height)

    scrollphathd.draw_char(x, y, char, font=None, brightness=1.0, monospaced=False)

    scrollphathd.fill(brightness, x=0, y=0, width=None, height=None)

    scrollphathd.flip(x=False, y=False)

    scrollphathd.get_buffer_shape()

    scrollphathd.get_shape()

    scrollphathd.rotate(degrees=0)

    scrollphathd.scroll(x=1, y=0)

    scrollphathd.scroll_to(x=0, y=0)

    scrollphathd.set_brightness(brightness)

    scrollphathd.set_clear_on_exit(value=True)

    scrollphathd.set_font(font)

    scrollphathd.set_gamma(gamma_table)

    scrollphathd.set_graph(values, low=None, high=None, brightness=1.0, x=0, y=0, width=None, height=None)

    scrollphathd.set_pixel(x, y, brightness)

    scrollphathd.show(before_display=None)

    scrollphathd.write_string(string, x=0, y=0, font=None, letter_spacing=1, brightness=1.0, monospaced=False, fill_background=False)

Visual representation of LED Matrix Where all lights are off

matrix = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

Individual Pixels can be described by (column, row), brightness

### Personal Classes

Sparkle()
    Represents one pixel that brightens and then fades out with a random speed.
    Returns a normalized intensity for `scrollphathd.set_pixel()` and can be reset for reuse.
    Provide it the pixel x,y and every frame it will cause the led to brighten or dim.

Blinker()
    Represents one pixel that brightens then fades at a fixed or random speed.
    Returns normalized intensity for use with `scrollphathd.set_pixel()` and
    can be reset for reuse. If `speed` is 0 at construction, a random speed will be chosen at reset.

Comet() - to implement
    A Comet moves across the matrix (with bouncing or wrapping) and leaves a tail whose pixels fade out progressively.
    This is spatially different from Blinker/Sparkle (which only change brightness in place) and gives the display motion plus a trailing falloff.

### Personal Functions

scan_trail_light(repeat=0):
blinker_scan_light(repeat=0):
blinker_fill_light(repeat=0):
sparkle_scan_light(repeat=0):
sparkle_fill_light(repeat=0):
checker_fill_light(repeat=0):
random_fill_light(repeat=0):
row_zigzag_fill_light(repeat=0):
row_zigzag_light(repeat=0):
column_fill_light(repeat=0):
row_fill_light(repeat=0):
column_sweep_light(repeat=0):
row_sweep_light(repeat=0):