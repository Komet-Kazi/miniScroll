This file is a merged representation of the entire codebase, combined into a single document by Repomix.
The content has been processed where empty lines have been removed, content has been compressed (code blocks are separated by ⋮---- delimiter), security check has been disabled.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Empty lines have been removed from all files
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Security check has been disabled - content may contain sensitive information
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
documentation/
  REFERENCE.md
examples/
  mini/
    button-splash.py
    buttons.py
    README.md
    rockfall.py
    simon.py
  tests/
    check-test.py
    fill-test.py
    font-test.py
    gamma-test.py
    rotation-test.py
    scroll-test.py
    transform-test.py
  advanced-scrolling.py
  binary-clock.py
  cellular-automata.py
  clock.py
  cpu.py
  font-gallery.py
  forest-fire.py
  gameoflife.py
  graph.py
  hello-pigpiod.py
  hello-utf8.py
  hello-world_w_thread.py
  hello-world-3x5.py
  hello-world.py
  inverse-text.py
  mouth.bmp
  openweather-temp-display.py
  plasma.py
  portraitclock.py
  precip.py
  robot-mouth.py
  scroll-and-static.py
  sideways.py
  simple-scrolling.py
  swirl.py
  twitter-hashtag.py
  unicode-scrolling.py
  web-api.py
library/
  scrollphathd/
    api/
      __init__.py
      action.py
      http.py
      stoppablethread.py
    fonts/
      __init__.py
      font3x5.py
      font5x5.py
      font5x7.py
      font5x7smoothed.py
      font5x7unicode.py
      fontd3.py
      fontgauntlet.py
      fonthachicro.py
      fontorgan.py
    __init__.py
    is31fl3731.py
  CHANGELOG.txt
  LICENSE.txt
  MANIFEST.in
  README.rst
  setup.py
packaging/
  debian/
    source/
      format
      options
    changelog
    clean
    compat
    control
    copyright
    docs
    README
    rules
  CHANGELOG
  makeall.sh
  makedeb.sh
  makedoc.sh
  makelog.sh
simulator/
  README.md
  scroll_phat_simulator.py
  simulator.gif
  smbus2.py
sphinx/
  _static/
    custom.css
  _templates/
    breadcrumbs.html
    layout.html
  conf.py
  favicon.png
  index.rst
  requirements.txt
  shop-logo.png
tools/
  3x5-font.png
  5x5-font.png
  5x7-font-smoothed.png
  5x7-font-unicode.png
  5x7-font.png
  d3.png
  gauntlet.png
  hachicro.png
  makefonts.sh
  mkfont.py
  organ.png
.gitignore
.stickler.yml
LICENSE
README.md
scroll-phat-hd-logo.png
terminal.jpg
```

# Files

## File: documentation/REFERENCE.md
````markdown
# Scroll pHAT HD Function Reference

Scroll pHAT HD uses white LEDs which can be brightness controlled. Note that when you set a pixel it will not immediately display on Scroll pHAT HD, you must call scrollphathd.show().

## Set A Single Pixel In Buffer

```python
scrollphathd.set_pixel(x, y, brightness)
```

Parameters:  
x – Position of pixel from left of buffer  
y – Position of pixel from top of buffer  
brightness – Intensity of the pixel, from 0.0 to 1.0 or 0 to 255  

## Write A Text String

```python
scrollphathd.write_string(string, x=0, y=0, font=None, letter_spacing=1, brightness=1.0)
```

Parameters:  
string – The string to display  
x – Offset x - distance of the string from the left of the buffer  
y – Offset y - distance of the string from the top of the buffer  
font – Font to use, default is to use the one specified with set_font  
brightness – Brightness of the pixels that compromise the text, from 0.0 to 1.0  

## Draw A Single Char

```python
scrollphathd.draw_char(x, y, char, font=None, brightness=1.0)
```

Parameters:  
x – Offset x - distance of the char from the left of the buffer  
y – Offset y - distance of the char from the top of the buffer  
char – Char to display- either an integer ordinal or a single letter  
font – Font to use, default is to use one specified with set_font  
brightness – Brightness of the pixels that compromise the char, from 0.0 to 1.0  

## Display A Graph

```python
scrollphathd.set_graph(values, low=None, high=None, brightness=1.0, x=0, y=0, width=None, height=None)
```

Parameters:  
values – A list of numerical values to display  
low – The lowest possible value (default min(values))  
high – The highest possible value (default max(values))  
brightness – Maximum graph brightness (from 0.0 to 1.0)  
x – x position of graph in display buffer (default 0)  
y – y position of graph in display buffer (default 0)  
width – width of graph in display buffer (default 17)  
height – height of graph in display buffer (default 7)  
Returns: None  

## Fill An Area

```python
scrollphathd.fill(brightness, x=0, y=0, width=0, height=0)
```

Parameters:  
brightness – Brightness of pixels  
x – Offset x - distance of the area from the left of the buffer  
y – Offset y - distance of the area from the top of the buffer  
width – Width of the area (default is 17)  
height – Height of the area (default is 7)  

## Clear An Area
```python
scrollphathd.clear_rect(x, y, width, height)
```

Parameters:  
x – Offset x - distance of the area from the left of the buffer  
y – Offset y - distance of the area from the top of the buffer  
width – Width of the area (default is 17)  
height – Height of the area (default is 7)  

## Display Buffer
All of your changes to Scroll pHAT HD are stored in a Python buffer. To display them on Scroll pHAT HD you must call scrollphthd.show().

```python
scrollphathd.show()
```

The buffer is copied, then scrolling, rotation and flip y/x transforms applied before taking a 17x7 slice and displaying.

## Clear Buffer

```python
scrollphathd.clear()
```

You must call show after clearing the buffer to update the display.

## Scroll The Buffer

```python
scrollphathd.scroll(x=0, y=0)
```

Scroll pHAT HD displays an 17x7 pixel window into the buffer, which starts at the left offset and wraps around.
The x and y values are added to the internal scroll offset. If called with no arguments, a horizontal right to left scroll is used.

Parameters:  
x – Amount to scroll on x-axis  
y – Amount to scroll on y-axis  

## Scroll To A Position

```python
scrollphathd.scroll_to(x=0, y=0)
```

Scroll pHAT HD displays a 17x7 pixel window into the buffer, which starts at the left offset and wraps around.
The x and y values set the internal scroll offset. If called with no arguments, the scroll offset is reset to 0,0

Parameters:  
x – Position to scroll to on x-axis  
y – Position to scroll to on y-axis  

## Rotate The Display

```python
scrollphathd.rotate(degrees=0)
```

Parameters:	degrees – Amount to rotate- will snap to the nearest 90 degrees


## Flip The Display

```python
scrollphathd.flip(x=False, y=False)
```

Parameters:  
x – Flip horizontally left to right  
y – Flip vertically up to down  

## Run a http API

flask must be installed before the api bluerint can be imported. 
To build up a flask api using the blueprint you can use the following and add your own blueprints to the api as you choose:

```python
from scrollphathd.api.http import scrollphathd_blueprint
from flask import Flask


app = Flask(__name__)
app.register_blueprint(scrollphathd_blueprint, url_prefix='/scrollphathd')
app.run()
```

Alternatively, with the module installed you should be able to run `python -m scrollphathd.api.http` and optionally supply `-p|--port` and `-H|--host` which will start the same api as described above.


Both options will start a http flask server with the endpoints:

* `/scrollphathd/show` - post `{"text": "helloworld"}` with the content type of the post request set to `application/json`
* `/scrollphathd/clear` - post to clear the screen
* `/scrollphathd/scroll` - post `{"x": 1,"y": 1}` to move it 1 in each direction. Content type must be set to `application/json`
* `/scrollphathd/flip` - post `{"x": "true||false", "y": "true||false"}` to flip either, both or none of the directions. 

If any data is formatted incorrectly, the blueprint api will respond with 422 (unprocessable entity) with a JSON response containing an indication of how the data was unprocessable, in the format `{"error": <string>}`.

If all was ok, you'll get a 200 response with no data.
````

## File: examples/mini/button-splash.py
````python
#!/usr/bin/env python3
⋮----
splash_origin = (0, 0)
splash_time = 0
def pressed(button)
⋮----
splash_origin = (x, y)
splash_time = time.time()
⋮----
button_map = {5: ("A", 0, 0),    # Top Left
⋮----
6: ("B", 0, 6),    # Bottom Left
16: ("X", 16, 0),  # Top Right
24: ("Y", 16, 7)}  # Bottom Right
button_a = Button(5)
button_b = Button(6)
button_x = Button(16)
button_y = Button(24)
def distance(x1, y1, x2, y2)
⋮----
splash_progress = time.time() - splash_time
⋮----
d = distance(x, y, splash_x, splash_y)
⋮----
h = d / 20.0
⋮----
h = min(1, h)
````

## File: examples/mini/buttons.py
````python
#!/usr/bin/env python3
⋮----
def pressed(button)
⋮----
button_name = button_map[button.pin.number]
⋮----
button_map = {5: "A",
button_a = Button(5)
button_b = Button(6)
button_x = Button(16)
button_y = Button(24)
````

## File: examples/mini/README.md
````markdown
# Examples for Scroll HAT Mini

Scroll HAT Mini includes four tactile push buttons connected to GPIO pins 5, 6, 16 and 24.

These examples demonstrate the use of the buttons, and combining them with display output for interesting results.

You can use these with the original Scroll pHAT HD, but you'll need to add buttons to these GPIO pins somehow!
````

## File: examples/mini/rockfall.py
````python
#!/usr/bin/env python3
"""
Little game for the Scroll HAT Mini.
"""
⋮----
# ------------------------------------------------------------
⋮----
class Rockfall()
⋮----
"""
    Main game class.
    """
# The extents of the screen
WIDTH = scrollphathd.DISPLAY_WIDTH
HEIGHT = scrollphathd.DISPLAY_HEIGHT
# THe istarting wait time between ticks
WAIT = 0.5
# How much to change the wait time by each tick
WAIT_DIFF = 0.001
# The min and max population fractions, and how much the butttons change
# it by
MIN_FRAC = 1.0 / HEIGHT
MAX_FRAC = 4.0 / HEIGHT
FRAC_STEP = 1.0 / HEIGHT
def __init__(self)
⋮----
# Set up the buttons
⋮----
# How easy or hard
⋮----
# The wait time between tocks
⋮----
# The game area as a boolean bitmap. A True means there is a rock in an
# entry. This is stored as a tuple of rows.
⋮----
# The player's position, at the end of the display
⋮----
def init(self)
⋮----
"""
        Reset the state to start of game.
        """
⋮----
def step(self)
⋮----
# Scroll the current values along by one
⋮----
# This fraction new, an interval between the minimum and the
# difficulty value
frac_new = max(self.MIN_FRAC, self._frac_new * random())
# Add new ones at random indices
indices = list(range(len(self._arena)))
⋮----
end = round(min(1, max(0, frac_new)) * len(indices))
⋮----
def explode(self)
⋮----
c = 1 + int(math.pi * 2 * r)
⋮----
o = 2 * math.pi / c * a
x = int(math.sin(o) * s + self.WIDTH - 1)
y = int(math.cos(o) * s + self._hpos)
v = s / r * (0.2 + 0.8 * random())
⋮----
def run(self)
⋮----
"""
        The main running loop.
        """
# State variables
⋮----
last = time.time()
start = last
# Set things to the starting values
# Loop forever now
⋮----
now = time.time()
since = now - last
# Move the things down
⋮----
last = now
⋮----
# Make it easier or harder
⋮----
# Move the player
⋮----
# Draw the field
⋮----
v = 0.5 if e else 0.0
⋮----
# Draw the player
⋮----
# And display it all
⋮----
# Collision?
⋮----
# Print stats
⋮----
# Draw the explosion
⋮----
# And reset things
⋮----
start = now
⋮----
# Wait for  bit befor emoving on
⋮----
# ----------------------------------------------------------------------
⋮----
game = Rockfall()
````

## File: examples/mini/simon.py
````python
#!/usr/bin/env python3
⋮----
# Set up Scroll HAT Mini.
⋮----
# Digits as 3x5 pixel elements stored as 15bits
# MSB is top-left, each 5 bits are a column.
digits_5x3 = [
⋮----
0b111111000111111,  # 0
0b100011111100001,  # 1
0b101111010111101,  # 2
0b101011010111111,  # 3
0b111000010011111,  # 4
0b111011010110111,  # 5
0b111111010100111,  # 6
0b100001000011111,  # 7
0b111111010111111,  # 8
0b111001010011111   # 9
⋮----
R = 0
G = 1
B = 2
Y = 3
class Display()
⋮----
"""Virtual Simon display class.
    This class wraps an output device (minicorn) and makes it behave like a display
    with four fixed colour lights (Red, Yellow, Blue and Green) and two 3x5 numeric digits.
    """
def __init__(self, output_device)
def _draw_light(self, brightness, x, y, r, g, b)
def _draw_rect(self, x, y, w, h, r, g, b)
def _draw_digit(self, digit, x, y, r, g, b)
⋮----
digit = digits_5x3[digit]
cols = [
⋮----
col = cols[dx]
⋮----
def clear(self)
def update(self)
⋮----
# Draw the current digts (score/level/lives, kinda)
⋮----
def set_light_brightness(self, red, green, blue, yellow)
def set_digits(self, left, right)
def set_digit_brightness(self, left, right)
def set_digit_color(self, left, right)
class Game()
⋮----
def __init__(self, display, starting_lives=3, starting_level=0, mode='attract')
⋮----
def _set_mode(self, mode)
def _attract(self, time)
⋮----
"""Mode: Attract.
        Pulses all the virtual lights and fades the numbers "51" ([si]mon) on the virtual digits.
        """
⋮----
def _play_pattern(self, time)
⋮----
"""Mode: Play Pattern.
        Steps through the current sequence and pulses each virtual light.
        Drops into "wait_for_input" mode when it's finished, this is
        determined by checking if the elapsed time is greater than the
        sequence length- since each "light" takes 1 second to pulse.
        """
⋮----
br = [0, 0, 0, 0]
color = self._sequence[self._current_playback_step]
⋮----
def _flash_lives(self, time)
⋮----
"""Mode: Flash Lives.
        Flash the players lives count at them.
        Re-play the pattern if they have lives left, otherwise jump to "you_lose"
        """
# To show the player that they've lost one life we flash
# the lives count up in red.
# We fake add one life to their count (which has been already deducted)
# for half of the flash cycle, so they visibly see the count go down!
fake_lives = self._lives
⋮----
# Flash lives for 3 seconds and then switch back to playing pattern
⋮----
def _you_win(self, time)
⋮----
"""Need a better win animation!"""
⋮----
def _you_lose(self, time)
⋮----
"""Flash the player's 0 lives at them in red!"""
⋮----
# Return back to attract mode after displaying losing zeros for 20s
⋮----
def _wait_for_input(self, time)
⋮----
"""Just display the current level and wait for the players input.
        This constantly checks the players input against the sequence,
        if it ever mismatches it deducts one life and switches to "flash_lives".
        A successful sequence match will call "next_level()"
        """
⋮----
# Remove the last (incorrect) guess
⋮----
def _display_level(self, color=(255, 255, 255))
⋮----
"""Helper to display the current level on the virtual digits."""
⋮----
def _pulse(self, time)
⋮----
"""Helper to produce a sine wave with a period of 1sec"""
⋮----
def _hue(self, h)
⋮----
"""Helper to return an RGB colour from HSV"""
⋮----
def start(self)
⋮----
"""Start the game.
        Sets the level to the starting level and builds a long-enough sequence to begin.
        """
⋮----
def next_level(self)
⋮----
"""Proceed to the next level.
        Adds 1 to the current level and a new random item to the end of the sequence.
        Jumps to the win state if the level hits 100!
        """
⋮----
def _handle_choice(self, button)
⋮----
"""Handle a specific choice."""
⋮----
def _handle_generic_input(self)
⋮----
"""Handle user input that's not button-specific.
        This function should be called for any button if it has not otherwise been handled.
        It's responsible for starting the game, mostly.
        """
⋮----
def button_a(self)
def button_b(self)
def button_x(self)
def button_y(self)
button_a = Button(5)   # Red
button_b = Button(6)   # [B]lue
button_x = Button(16)  # Green
button_y = Button(24)  # [Y]ellow
display = Display(output_device=scrollphathd)
game = Game(display)
````

## File: examples/tests/check-test.py
````python
#!/usr/bin/env python
⋮----
speed_factor = 10
⋮----
scale = (math.sin(time.time() * speed_factor) + 1) / 2
offset = 0
⋮----
color = 0.25 * scale * (offset % 2)
````

## File: examples/tests/fill-test.py
````python
#!/usr/bin/env python
````

## File: examples/tests/font-test.py
````python
#!/usr/bin/env python
⋮----
# Uncomment the below if your display is upside down
# (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
````

## File: examples/tests/gamma-test.py
````python
#!/usr/bin/env python
⋮----
DELAY = 0.0001
````

## File: examples/tests/rotation-test.py
````python
#!/usr/bin/env python
````

## File: examples/tests/scroll-test.py
````python
#!/usr/bin/env python
````

## File: examples/tests/transform-test.py
````python
#!/usr/bin/env python
⋮----
parser = argparse.ArgumentParser(description='Scroll Hat HD transformation test.')
⋮----
args = parser.parse_args()
````

## File: examples/advanced-scrolling.py
````python
#!/usr/bin/env python
⋮----
# Uncomment the below if your display is upside down
#   (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
# Dial down the brightness
⋮----
# If rewind is True the scroll effect will rapidly rewind after the last line
rewind = True
# Delay is the time (in seconds) between each pixel scrolled
delay = 0.03
# Change the lines below to your own message
lines = ["In the old #BILGETANK we'll keep you in the know",
# Determine how far apart each line should be spaced vertically
line_height = scrollphathd.DISPLAY_HEIGHT + 2
# Store the left offset for each subsequent line (starts at the end of the last line)
offset_left = 0
# Draw each line in lines to the Scroll pHAT HD buffer
# scrollphathd.write_string returns the length of the written string in pixels
# we can use this length to calculate the offset of the next line
# and will also use it later for the scrolling effect.
lengths = [0] * len(lines)
⋮----
# This adds a little bit of horizontal/vertical padding into the buffer at
# the very bottom right of the last line to keep things wrapping nicely.
⋮----
# Reset the animation
⋮----
# Keep track of the X and Y position for the rewind effect
pos_x = 0
pos_y = 0
⋮----
# Delay a slightly longer time at the start of each line
⋮----
# Scroll to the end of the current line
⋮----
# If we're currently on the very last line and rewind is True
# We should rapidly scroll back to the first line.
⋮----
# Otherwise, progress to the next line by scrolling upwards
````

## File: examples/binary-clock.py
````python
#!/usr/bin/env python
#
# binary_clock.py - A Python implementation of a binary clock
# for the Pimoroni Scroll Bot.
# Copyright (C) 2018 Freddy Spierenburg
⋮----
class Time(object)
⋮----
def __init__(self)
def hour(self)
def minute(self)
def second(self)
def update(self)
class Clock(Time)
⋮----
def _hour(self)
def _minute(self)
def _second(self)
def draw(self)
class BinaryClock(Clock)
⋮----
def _draw_binary(self, x, value)
def _draw_hand(self, x_left, x_right, value)
⋮----
def _intensities_init(self, max_intensity)
def _brightness_step(self)
def _intensity(self, max_intensity)
⋮----
class ScrollPhatHD(object)
⋮----
def set_pixel(self, x, y, brightness)
def show(self)
def main()
⋮----
clock = BinaryClock()
````

## File: examples/cellular-automata.py
````python
#!/usr/bin/env python
# simple CA
# loops through a bunch of interesting simple CA
⋮----
def mainloop()
⋮----
# set up the scrollPhat
⋮----
# Uncomment the below if your display is upside down
# (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
⋮----
# define a list of some interesting rule numbers to loop through
rules = [22, 30, 54, 60, 75, 90, 110, 150]
rule = rules[0]
# how many evolve steps to perform before starting the next CA rule
maxSteps = 100
loopCount = 0
# define the matrix of cells and rows that we will be displaying
matrix = numpy.zeros((7, 17), dtype=numpy.int)
# set the initial condition of the first row
# "dot" = single cell at position (0,8); top row, middle LED
firstRow = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
⋮----
# We need to keep track of which row we are working on
# the CA fills in from the top row and evolves downwards.
# When we have filled the last row we'll scroll all the
# rows up and just evolve the bottom row from then on.
row = 0
speed = 10
⋮----
# redraw first so that it shows the initial contitions when first run
⋮----
# if we have performed maxSteps...
⋮----
# reset a bunch of stuff
⋮----
# get a new rule
rules = numpy.roll(rules, -1, axis=0)
⋮----
# use the current row as the input for the next row
inputRow = matrix[row]
# make an empty array to fill with values
outputRow = numpy.zeros((17), dtype=numpy.int)
#  the secret sauce...
#  step through each cell in the output row, calculate its value
#  from the state of the input cell above and its left and right neighbour
⋮----
#  for each output cell, get the values of the input cell
#  and its left and right neighbours.
#  because cell 0 has no left neighbour we will
#  get that value from the last cell in the row.
#  similarly, the last cell in the row has no right neighbour
#  so we will use the value of cell 0, effectively wrapping
#  the horizontal edges of the display
a = inputRow[x - 1] if x > 0 else inputRow[16]
b = inputRow[x]
c = inputRow[x + 1] if x < 16 else inputRow[0]
#  a, b and c now contain the states of the three input cells
#  that determine the state of our output cell
#  there are 8 possible combinations for a,b,c
#  they are:
#  abc   abc   abc   abc   abc   abc   abc   abc
#  111   110   101   100   011   010   001   000
#  an abc combination will prodcude an output of either
#  1 or 0 depending on the rule we are using
#  for example, if we are running rule 30:
#  the binary representation of 30 is 11110.
#  we have to left-pad that out a bit so that we also have
#  8 digits : "00011110"
#  the rule can then be mapped onto our abc combinations like so:
#  inputs   111   110   101   100   011   010   001   000
#  outputs   0     0     0     1     1     1     1     0
#  if we find an abc of a=1, b=0, c=0 we would match
#  with "100" and output a 1
#  if we were using rule number 110 we would get this mapping
⋮----
#  outputs   0     1     1     0     1     1     0     0
#  because the padded binary representation of the number 110 is
#  "01101100" we get no match for "100"
#  ok, so lets consider the first evolution of rule 30 starting
#  with a single dot in the center of the first row.
#  (using a row of seven cells, 17 is too many to type!)
#  given row 0 =>   0001000
#  our first abc is "000", 00]0100[0  (remember that we are wrapping)
#  > this maps to 0
#  our next abc is "000", [000]1000
⋮----
#  our next abc is "001", 0[001]000
#  > this maps to 1 yay!
#  our next abc is "010", 00[010]00
#  > this maps to 1
#  our next abc is "100", 000[100]0
⋮----
#  our next abc is "000", 0001[000]
⋮----
#  our next abc is "000", 0]0010[00
⋮----
#  we now have seven new cells and our our output row will be
#  > "0011100"
#  and our cumulative rows will be :
#  row 0 > 0001000
#  row 1 > 0011100
#  after the next step, our cumulative output will be :
⋮----
#  row 2 > 0110010
#  so that's nice, but we need a general way to do this for any rule
#  ...
#  to convert our input values (abc) into output values for any
#  rule we will first notice that the input combinations "111",
#  "110" etc are themselves binary representations of the numbers
#  7,6,5,4,3,2,1,0 and that they are in index order if we read
#  right to left.
#  we can turn our abc result into a number and this will give
#  the index position of our abc combination using our right to left order.
#  for example, the abc pattern "011" is binary for 3
#  ...  int("011", 2) === 3
#  so we put a 1 in index position 3 (counting from 0, starting from the right)
#  ... "00001000"
#  and see if it matches against our binary rule 30
#  0 0 0 0 1 0 0 0
#  0 0 0 1 1 1 1 0
#          ^
⋮----
#      a match!
#  this is equivelant to the bitwise AND operation:
#  3&30
#  see here :
#  https://wiki.python.org/moin/BitwiseOperators
#  x & y Does a "bitwise and". Each bit of the output is 1 if the
#  corresponding bit of x AND of y is 1, otherwise it's 0.
#  so, after all that we now know the state of this output cell.
#  fortunately the algorithm is a lot shorter than the explaination ;)
#  construct our abc by bitshift and move a 1 to that index.
o = 1 << ((a << 2) + (b << 1) + c)
#  set the output cell to 1 if it &s with the rule, othewise 0
⋮----
# incrementally fill in the rows until we fill the last row
# then roll up the display matrix and evolve the last row
⋮----
row = row + 1
⋮----
matrix = numpy.roll(matrix, -1, axis=0)
# set the matrix new row for the next redraw
⋮----
# have a nap
⋮----
# here endeth the script
````

## File: examples/clock.py
````python
#!/usr/bin/env python
⋮----
# Display a progress bar for seconds
# Displays a dot if False
DISPLAY_BAR = False
# Brightness of the seconds bar and text
BRIGHTNESS = 0.3
# Uncomment the below if your display is upside down
#   (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
⋮----
# Grab the "seconds" component of the current time
# and convert it to a range from 0.0 to 1.0
float_sec = (time.time() % 60) / 59.0
# Multiply our range by 15 to spread the current
# number of seconds over 15 pixels.
#
# 60 is evenly divisible by 15, so that
# each fully lit pixel represents 4 seconds.
⋮----
# For example this is 28 seconds:
# [x][x][x][x][x][x][x][ ][ ][ ][ ][ ][ ][ ][ ]
#  ^ - 0 seconds                59 seconds - ^
seconds_progress = float_sec * 15
⋮----
# Step through 15 pixels to draw the seconds bar
⋮----
# For each pixel, we figure out its brightness by
# seeing how much of "seconds_progress" is left to draw
# If it's greater than 1 (full brightness) then we just display 1.
current_pixel = min(seconds_progress, 1)
# Multiply the pixel brightness (0.0 to 1.0) by our global brightness value
⋮----
# Subtract 1 now we've drawn that pixel
⋮----
# If we reach or pass 0, there are no more pixels left to draw
⋮----
# Just display a simple dot
⋮----
# Display the time (HH:MM) in a 5x5 pixel font
⋮----
x=0,                   # Align to the left of the buffer
y=0,                   # Align to the top of the buffer
font=font5x5,          # Use the font5x5 font we imported above
brightness=BRIGHTNESS  # Use our global brightness value
⋮----
# int(time.time()) % 2 will tick between 0 and 1 every second.
# We can use this fact to clear the ":" and cause it to blink on/off
# every other second, like a digital clock.
# To do this we clear a rectangle 8 pixels along, 0 down,
# that's 1 pixel wide and 5 pixels tall.
⋮----
# Display our time and sleep a bit. Using 1 second in time.sleep
# is not recommended, since you might get quite far out of phase
# with the passing of real wall-time seconds and it'll look weird!
⋮----
# 1/10th of a second is accurate enough for a simple clock though :D
````

## File: examples/cpu.py
````python
#!/usr/bin/env python
⋮----
i = 0
cpu_values = [0] * scrollphathd.DISPLAY_WIDTH
# Uncomment the below if your display is upside down
# (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
````

## File: examples/font-gallery.py
````python
#!/usr/bin/env python
⋮----
def scroll_message(font, message)
⋮----
scrollphathd.clear()                         # Clear the display and reset scrolling to (0, 0)
length = scrollphathd.write_string(message)  # Write out your message
scrollphathd.show()                          # Show the result
time.sleep(0.5)                              # Initial delay before scrolling
⋮----
# Now for the scrolling loop...
⋮----
scrollphathd.scroll(1)                   # Scroll the buffer one place to the left
scrollphathd.show()                      # Show the result
⋮----
time.sleep(0.02)                         # Delay for each scrolling step
time.sleep(0.5)                              # Delay at the end of scrolling
````

## File: examples/forest-fire.py
````python
#!/usr/bin/env python
# Forest fire model cellular automaton. Simulates the growth
# of trees in a forest, with sporadic outbreaks of forest fires.
# https://en.wikipedia.org/wiki/Forest-fire_model
# Based on Rosetta Code Python Forest Fire example.
# https://rosettacode.org/wiki/Forest_fire#Python
⋮----
# Avoid retina-searage!
⋮----
# The height and width of the forest. Same as Scroll pHAT HD
# dimensions
height = scrollphathd.height
width = scrollphathd.width
# Initial probability of a grid square having a tree
initial_trees = 0.55
# p = probability of tree growing, f = probability of fire
p = 0.01
f = 0.001
# Brightness values for a tree, fire, and blank space
⋮----
# Each square's neighbour coordinates
hood = ((-1, -1), (-1, 0), (-1, 1),
# Function to populate the initial forest
def initialise()
⋮----
grid = {(x, y): (tree if random.random() <= initial_trees else space) for x in range(width) for y in range(height)}
⋮----
# Display the forest, in its current state, on Scroll pHAT HD
def show_grid(grid)
# Go through grid, update grid squares based on state of
# square and neighbouring squares
def update_grid(grid)
⋮----
new_grid = {}
⋮----
# Main function. Initialises grid, then shows, updates, and
# waits for 1/20 of a second.
def main()
⋮----
grid = initialise()
⋮----
grid = update_grid(grid)
⋮----
# Catches control-c and exits cleanly
⋮----
# FIN!
````

## File: examples/gameoflife.py
````python
#!/usr/bin/env python
⋮----
YSIZE = 7
XSIZE = 17
BRIGHT = 0.3
# Control update speed: 1 fastest - 5 slowest
SPEED = 3
⋮----
def generatemap()
⋮----
# crude way to start with live cells, but adds count diversity
⋮----
y = random.randint(0, YSIZE - 1)
x = random.randint(0, XSIZE - 1)
⋮----
def printmap(sleeptime)
⋮----
alive_counter = 0
⋮----
def lifecycle()
⋮----
# preparing next cycle
soonmatrix = {key: value for key, value in matrix.items()}
⋮----
neighbors = countneighbors(y, x, matrix[y, x])
⋮----
# activating next cycle
⋮----
def countneighbors(py, px, status)
⋮----
# Counts live neighbors by checking within a 3x3 grid
neighbors = -1 if status else 0
⋮----
matrix = {}
max_iterations = 100
stagnation_max = 10
alive_count_old = 0
stagnation_count = 0
⋮----
active_count = printmap(SPEED)
# checks if the amount of live cells changed
⋮----
alive_count_old = active_count
````

## File: examples/graph.py
````python
#!/usr/bin/env python
⋮----
MIN_VALUE = 0
MAX_VALUE = 50
# Uncomment the below if your display is upside down
#   (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
# Begin with a list of 17 zeros
values = [0] * scrollphathd.DISPLAY_WIDTH
⋮----
# Insert a random value at the beginning
⋮----
# Get rid of the last value, keeping the list at 17 (DISPLAY_WIDTH) items
values = values[:scrollphathd.DISPLAY_WIDTH]
# Plot the random values onto Scroll pHAT HD
````

## File: examples/hello-pigpiod.py
````python
#!/usr/bin/env python
⋮----
class I2C_PIGPIO()
⋮----
def __init__(self)
def write_byte_data(self, address, register, value)
def read_byte_data(self, address, register)
def write_i2c_block_data(self, address, register, values)
⋮----
# Uncomment the below if your display is upside down
# (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
# Write the "Hello World!" string in the buffer and
# set a more eye-friendly default brightness
⋮----
# Auto scroll using a while + time mechanism (no thread)
⋮----
# Show the buffer
⋮----
# Scroll the buffer content
⋮----
# Wait for 0.1s
````

## File: examples/hello-utf8.py
````python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
⋮----
# Uncomment to rotate the text
# scrollphathd.rotate(180)
# Set a more eye-friendly default brightness
⋮----
text = [unichr(x) for x in range(256)]
text = u"{}        ".format(u"".join(text))
````

## File: examples/hello-world_w_thread.py
````python
#!/usr/bin/env python
⋮----
def autoscroll(interval=0.1)
⋮----
"""Autoscroll with a thread (recursive function).
    Automatically show and scroll the buffer according to the interval value.
    :param interval: Amount of seconds (or fractions thereof), not zero
    """
# Start a timer
⋮----
# Show the buffer
⋮----
# Scroll the buffer content
⋮----
# Uncomment the below if your display is upside down
#   (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
# Write the "Hello World!" string in the buffer and
#   set a more eye-friendly default brightness
⋮----
# Auto scroll using a thread
````

## File: examples/hello-world-3x5.py
````python
#!/usr/bin/env python
⋮----
# Uncomment the below if your display is upside down
# (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
# Write the "Hello World!" string in the buffer and
# set a more eye-friendly default brightness
⋮----
# Auto scroll using a while + time mechanism (no thread)
⋮----
# Show the buffer
⋮----
# Scroll the buffer content
⋮----
# Wait for 0.1s
````

## File: examples/hello-world.py
````python
#!/usr/bin/env python
⋮----
# Uncomment the below if your display is upside down
# (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
# Write the "Hello World!" string in the buffer and
# set a more eye-friendly default brightness
⋮----
# Auto scroll using a while + time mechanism (no thread)
⋮----
# Show the buffer
⋮----
# Scroll the buffer content
⋮----
# Wait for 0.1s
````

## File: examples/inverse-text.py
````python
#!/usr/bin/env python
````

## File: examples/openweather-temp-display.py
````python
# !/usr/bin/env python
#
⋮----
# Update to the wunderground-temp-display.py script to use the OpenWeather API and display on scrollphathd.
# This script shows the current temperature along with an indicator of
# the temperature trend (same, going up, going down), averaged over a given period of time.
# It also shows a small line at the bottom which indicates current wind speed and gusts.
# Current speed is shown using a brighter color and gusts are show using a dimmer color.
⋮----
# Development environment: Python v3 on a Raspberry Pi Zero-W running Raspbian and default scrollphathd libraries
⋮----
# Originally built by Mark Ehr, 1/12/18, and released to the public domain with no warranties expressed or implied. Or something along those lines.
# Feel free to use this code any way that you'd like. If you want to give credit, that's great.
⋮----
# Note: if you want this to auto-run upon boot, add this line to the bottom of /etc/rc.local just above the "exit 0" line:
#   sudo python {path}/wunderground-temp-display.py &
⋮----
# Also note that if you receive an odd "Remote I/O" error, that's the scrollphathd's odd way of saying that it can't
# communicate with the display. Check the hardware connection to make sure all of the pins are seated. In Mark's case, it
# happened randomly until they re-soldered the header connections on the RPi as well as the hat.
⋮----
# Default scrollphathd library
⋮----
# Used to make web calls to OpenWeather
⋮----
# Used to parse OpenWeather JSON data
⋮----
# Returns time values
⋮----
# Uncomment the below if your display is upside down
# (e.g. if you're using it in a Pimoroni Scroll Bot)
⋮----
# OpenWeather API key. Make sure to put your unique OpenWeather key in here
OW_API_KEY = "YOUR_API_KEY_GOES_HERE"
# Or set the OW_API_KEY environment variable
OW_API_KEY = os.environ.get("OW_API_KEY", OW_API_KEY)
# Customize this for your desired location. Find a JSON list of all city IDs here: http://bulk.openweathermap.org/sample/
OW_STATION = "5799841"
# Kirkland, WA
# Weather polling interval (seconds). Free OpenWeather API accounts allow 60 calls/minute and 1Mil/month.
POLL_INTERVAL = 30
# Interval after which the average temp is reset in Minutes. Used to make sure that the temp trending indicator stays accurate. Default is 15 min.
AVG_TEMP_RESET_INTERVAL = 15
# Flags used to specify whether to display actual or "feels like" temperature.
# Change CURRENT_TEMP_DISPLAY to 1 for actual temp and anything other than 1 for feels like temperature
CURRENT_TEMP_DISPLAY = 1
# Display settings
BRIGHT = 0.2
DIM = 0.1
# Show gusts as a bright dot
GUST_BRIGHTNESS = 0.3
# Show current speed as a slightly dimmer line
WIND_BRIGHTNESS = 0.1
# "Knight Rider" pulse delay. See comments below for description of what this is.
# Note that this loop uses the lion's share of CPU, so if your goal is to minimize CPU usage, increase the delay.
# Of course, increasing the delay results in a slightly less cool KR pulse. In practice, a value of 0.05 results in ~16% Python CPU utilization on
# a Raspberry Pi Zero-W. Increasing this to 0.1 drops CPU to ~10%, of course YMMV.
KR_PULSE_DELAY = 0.2
# Temperature scale (C or F). MUST USE UPPERCASE.
TEMP_SCALE = "F"
# Max wind speed. Used to calculate the wind speed bar graph
# (17 "x" pixels / max wind speed = ratio to multiply current wind speed by in order to determine much much of a line to draw)
# Set max wind speed according to scale
⋮----
MAX_WIND_SPEED = 42.0
# MPH; default was set to 75.0, I lowered to 42 for better viewing of lower wind speeds
⋮----
MAX_WIND_SPEED = 100.0
# KPH; default 100.0
# Debug flag  - set to 1 if you want to print(informative console messages)
DEBUG = 0
# Initialize global variables before use
current_temp = 0.0
average_temp = 0.0
wind_chill = 0.0
average_temp_counter = 0
average_temp_cumulative = 0.0
total_poll_time = 0   # Used to reset the average temp after a defined amount of time has passed
wind_speed = 0.0
wind_gusts = 0
actual_str = " "
feels_like_str = " "
feels_like = 0
# get_weather_data() - Retrieves and parses the weather data we want to display from OpenWeather.
# Updates global variables with weather data formatted for display use
# To request a free API key, go here: https://openweathermap.org/price
def get_weather_data()
⋮----
# Make sure that the module updates the global variables instead of creating local copies
⋮----
# Get current conditions. Substitute your personal OpenWeather API key and the desired weather station code.
# Build OpenWeather URL using API key and station specified at top.
# This code retrieves a complete set of current weather conditions and loads them up into a JSON catalog.
# Note that JSON, while very powerful, can also be very confusing to decode. Take care especially when memory and compute resources are scarce.
# Removed the Raise Exception as it was closing the program when WiFi was lost. Added a sleep to give WiFi time to reconnect.
url_str = "http://api.openweathermap.org/data/2.5/weather?id=" + OW_STATION + "&appid=" + OW_API_KEY + "&units=imperial"
⋮----
conditions = urllib2.urlopen(url_str)
json_string = conditions.read()         # Load into a json string
parsed_cond = json.loads(json_string.decode())      # Parse the string into a json catalog
⋮----
# Build current temperature string
# Check to see if average temp counters need to be reset
⋮----
# Parse out the current temperature and wind speeds from the json catalog based on which temperature scale is being used
# Assumption was made that if C is being used for temp, kph is also in use. Apologies if that is not the case everywhere. :-)
if TEMP_SCALE == "F":   # Fahrenheit
current_temp = parsed_cond['main']['temp']   # String used for calculations
wind_speed = float(parsed_cond['wind']['speed'])
wind_gusts = float(parsed_cond['wind']['gust'])
feels_like = float(parsed_cond['main']['feels_like'])
else:   # Celsius
current_temp = parsed_cond['main']['temp']
⋮----
wind_gusts = float(parsed_cond['wind']['speed'])
⋮----
# Calculate average temperature, which is used to determine temperature trending (same, up, down)
average_temp_cumulative = average_temp_cumulative + current_temp
average_temp_counter = average_temp_counter + 1
average_temp = average_temp_cumulative / average_temp_counter
# Convert to integer from float. For some reason you can't cast the above directly as an int, so need to take an extra step.
# Mark thinks there is a more elegant way to doing this. I think this way works great. :-D
fl_int = int(feels_like)
fl_str = str(fl_int)
as_int = int(current_temp)
actual_str = str(as_int)
⋮----
# If you want to play around with displaying other measurements.
# You can view all available data by pasting the OpenWeather API URL above into a web browser, which will return the raw json output.
# Or by reading their documentation: https://openweathermap.org/current
actual_str = actual_str + TEMP_SCALE   # remove unneeded trailing data and append temperature scale (C or F) to the end
feels_like_str = fl_str + TEMP_SCALE   # remove unneeded trailing data and append temperature scale (C or F) to the end
⋮----
actual_str = ""
⋮----
def draw_kr_pulse(pos, dir)
⋮----
# Clear 5 pixel line (easier than keeping track of where the previous illuminated pixel was)
⋮----
x = pos + 11   # Increase position to the actual x offset we need
scrollphathd.set_pixel(x, 5, 0.2)   # Turn on the current pixel
⋮----
def draw_temp_trend(dir)
⋮----
if dir == 0:   # Equal - don't display anything. Clear the area where direction arrow is shown
⋮----
elif dir == 1:   # Increasing = up arrow. Draw an up arrow symbol on the right side of the display
⋮----
scrollphathd.set_pixel(15, y, BRIGHT)   # Draw middle line of arrow
scrollphathd.set_pixel(14, 1, BRIGHT)   # Draw the 'wings' of the arrow
⋮----
elif dir == -1:   # Decreasing = down arrow
⋮----
# draw_wind_line() - draws a single line indicator of wind speed and wind gusts on the bottom of the display
# Current wind speed is shown as as bright line and gusts as as dim line.
⋮----
# Calculation: calculate a ratio (17 pixels / max wind speed) and multiply by actual wind speed, rounding
#   to integer, yielding the number of pixels on 'x' axis to illuminate.
def draw_wind_line()
⋮----
wind_multiplier = (17.0 / MAX_WIND_SPEED)
⋮----
wind_calc = wind_multiplier * wind_speed
⋮----
wind_calc = int(wind_calc)   # Convert to int
if wind_calc > 17:   # Just in case something goes haywire, like a hurricane :-)
wind_calc = 17
gust_calc = wind_multiplier * wind_gusts
⋮----
gust_calc = int(gust_calc)
⋮----
gust_calc = 17
⋮----
# Draw the wind speed first
⋮----
# Now draw the gust indicator as a single pixel
if gust_calc:   # Only draw if non zero
⋮----
# display_temp_value()
# This module allows the user to specify if they want actual or "feels like" temperature displayed.
# 'Feels like' includes things like wind and humidity.
# CURRENT_TEMP_DISPLAY controls which temperature to display.
def display_temp_value()
⋮----
# clear the old temp reading. If temp > 100 then clear an extra digit's worth of pixels
⋮----
if CURRENT_TEMP_DISPLAY == 1:   # show actual temp
⋮----
else:   # Show feels_like temp
⋮----
# BEGIN MAIN LOGIC
⋮----
# Initial weather data poll and write to display
⋮----
# Loop forever until user hits Ctrl-C
# Ctrl-C raises a KeyboardInterrupt and prevents any code below the 'while True' statement from running.
⋮----
prev_temp = current_temp
⋮----
# Don't show temp trend arrow if > 100 degrees or < -10 degrees -- not enough room on the display.
⋮----
display_temp_value()   # If you want actual temp, just change to ACTUAL
# Pulse a pixel, Knight Rider style, just to show that everything is alive and working.
# Sleep function in draw_kr_pulse keeps Python from consuming 100% CPU
# Use display line 5, 14-17
⋮----
draw_kr_pulse(pulse, 1)   # Left to right
⋮----
draw_kr_pulse(pulse, -1)   # Back the other way
````

## File: examples/plasma.py
````python
#!/usr/bin/env python
⋮----
i = 0
⋮----
s = math.sin(i / 50.0) * 2.0 + 6.0
⋮----
v = 0.3 + (0.3 * math.sin((x * s) + i / 4.0) * math.cos((y * s) + i / 4.0))
````

## File: examples/portraitclock.py
````python
#!/usr/bin/env python
⋮----
# See https://docs.python.org/2/library/time.html
# for more information on what the time formats below do.
# Display the hour as two digits
⋮----
# Display the minute as two digits
⋮----
# Display the second as two digits
````

## File: examples/precip.py
````python
#!/usr/bin/env python
⋮----
def generate_lightning(intensity)
⋮----
"""Generate a lightning bolt"""
⋮----
x = random.randint(0, width - 1)
# generate a random crooked path from top to bottom,
# making sure to not go off the sides
⋮----
branch = random.random()
⋮----
x = 0
⋮----
x = width - 1
# generate a wider flash around the bolt itself
wide = [int(x - (width / 2)), int(x + (width / 2))]
med = [int(x - (width / 4)), int(x + (width / 4))]
small = [x - 1, x + 1]
⋮----
def new_drop(pixels, values)
⋮----
"""Generate a new particle at the top of the board"""
# First, get a list of columns that haven't generated
# a particle recently
cols = []
⋮----
good_col = True
⋮----
good_col = False
⋮----
# Then pick a random value from this list,
# test a random number against the amount variable,
# and generate a new particle in that column.
# Then remove it from the list.
# Do this as many times as required by the intensity variable
⋮----
cols_left = values['intensity']
⋮----
def fade_pixels(pixel_array, fade)
⋮----
"""Fade all the lit particles on the board by the fade variable"""
⋮----
def update_pixels(pixels, values)
⋮----
"""Update the board by lighting new pixels as they fall"""
⋮----
x = range(width)
y = range(height)
⋮----
# Command line argument parsing functions
def msg(name=None)
def setup_parser()
⋮----
parser = argparse.ArgumentParser(
⋮----
# Set up command line argument parsing
parser = setup_parser()
args = parser.parse_args()
arguments = vars(args)
⋮----
# Board rotation
⋮----
width = scrollphathd.get_shape()[0]
height = scrollphathd.get_shape()[1]
presets = {
values = {}
conditions = [
# Set initial values from arguments or preset
⋮----
# Set up initial pixel matrix
pixels = []
⋮----
# Print conditions
⋮----
# Run display loop
````

## File: examples/robot-mouth.py
````python
#!/usr/bin/env python
⋮----
IMAGE_BRIGHTNESS = 0.5
img = Image.open("mouth.bmp")
def get_pixel(x, y)
⋮----
p = img.getpixel((x, y))
⋮----
p = max(r, g, b)
⋮----
brightness = get_pixel(x, y)
````

## File: examples/scroll-and-static.py
````python
#!/usr/bin/env python
⋮----
# Uncomment the below if your display is upside down
#   (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
# Set a more eye-friendly default brightness
⋮----
# Write the string to scroll
⋮----
def draw_static_elements(buf)
⋮----
# Buf is given as a two dimensional array of elements buf[x][y]
# This method will blink a frame of alternating lights around
# our scrolling text twice a second.
````

## File: examples/sideways.py
````python
#!/usr/bin/env python
⋮----
# Set a more eye-friendly default brightness
````

## File: examples/simple-scrolling.py
````python
#!/usr/bin/env python
⋮----
def scroll_message(message)
⋮----
scrollphathd.clear()                         # Clear the display and reset scrolling to (0, 0)
length = scrollphathd.write_string(message)  # Write out your message
scrollphathd.show()                          # Show the result
time.sleep(0.5)                              # Initial delay before scrolling
⋮----
# Now for the scrolling loop...
⋮----
scrollphathd.scroll(1)                   # Scroll the buffer one place to the left
scrollphathd.show()                      # Show the result
⋮----
time.sleep(0.02)                         # Delay for each scrolling step
time.sleep(0.5)                              # Delay at the end of scrolling
````

## File: examples/swirl.py
````python
#!/usr/bin/env python
⋮----
def swirl(x, y, step)
⋮----
dist = math.sqrt(pow(x, 2) + pow(y, 2))
angle = (step / 10.0) + dist / 1.5
s = math.sin(angle)
c = math.cos(angle)
xs = x * c - y * s
ys = x * s + y * c
r = abs(xs + ys)
⋮----
timestep = math.sin(time.time() / 18) * 1500
⋮----
v = swirl(x, y, timestep)
````

## File: examples/twitter-hashtag.py
````python
#!/usr/bin/env python
# made by @mrglennjones with help from @pimoroni & pb
⋮----
# adjust the tracked keyword below to your keyword or #hashtag
keyword = '#bilgetank'
# enter your twitter app keys here
# you can get these at apps.twitter.com
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''
⋮----
# make FIFO queue
q = queue.Queue()
# define main loop to fetch formatted tweet from queue
def mainloop()
⋮----
# Uncomment the below if your display is upside down
#   (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
⋮----
# grab the tweet string from the queue
⋮----
status = q.get(False)
⋮----
status_length = scrollphathd.write_string(status, x=0, y=0, font=font5x7, brightness=0.1)
⋮----
class MyStreamListener(tweepy.StreamListener)
⋮----
def on_status(self, status)
⋮----
# format the incoming tweet string
status = u'     >>>>>     @{name}: {text}     '.format(name=status.user.screen_name.upper(), text=status.text.upper())
⋮----
status = unicodedata.normalize('NFKD', status).encode('ascii', 'ignore')
⋮----
# put tweet into the fifo queue
⋮----
def on_error(self, status_code)
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
⋮----
api = tweepy.API(auth)
myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
````

## File: examples/unicode-scrolling.py
````python
#!/usr/bin/env python
⋮----
# For python 2/3 compatibility, check to see if `unichr` is defined.
# If it isn't, then this is python3, in which case the `chr` builtin can
# be used instead.
⋮----
unichr = chr
def scroll_message(message)
⋮----
scrollphathd.clear()                         # Clear the display and reset scrolling to (0, 0)
length = scrollphathd.write_string(message)  # Write out your message
scrollphathd.show()                          # Show the result
time.sleep(0.5)                              # Initial delay before scrolling
⋮----
# Now for the scrolling loop...
⋮----
scrollphathd.scroll(1)                   # Scroll the buffer one place to the left
scrollphathd.show()                      # Show the result
⋮----
time.sleep(0.02)                         # Delay for each scrolling step
time.sleep(0.5)                              # Delay at the end of scrolling
message = "".join([unichr(x) for x in range(256)])
````

## File: examples/web-api.py
````python
#!/usr/bin/env python
⋮----
# Set the font
⋮----
# Set the brightness
⋮----
# Uncomment the below if your display is upside down
# (e.g. if you're using it in a Pimoroni Scroll Bot)
# scrollphathd.rotate(degrees=180)
⋮----
app = Flask(__name__)
⋮----
@app.route('/')
    def index()
````

## File: library/scrollphathd/api/__init__.py
````python

````

## File: library/scrollphathd/api/action.py
````python
class Action(object)
⋮----
def __init__(self, action_type, data)
````

## File: library/scrollphathd/api/http.py
````python
scrollphathd_blueprint = Blueprint('scrollhat', __name__)
api_queue = Queue()
class AutoScroll()
⋮----
_is_enabled = False
_interval = 0.1
def config(self, is_enabled="False", interval=0.1)
def run(self)
⋮----
# Start a timer
⋮----
# Scroll the buffer content
⋮----
# Show the buffer
⋮----
@scrollphathd_blueprint.route('/autoscroll', methods=["POST"])
def autoscroll()
⋮----
response = {"result": "success"}
status_code = http_status.OK
data = request.get_json()
⋮----
data = request.form
⋮----
response = {"result": "KeyError", "error": "keys is_enabled and interval not posted."}
status_code = http_status.UNPROCESSABLE_ENTITY
⋮----
response = {"result": "ValueError", "error": "invalid data type(s)."}
⋮----
@scrollphathd_blueprint.route('/scroll', methods=["POST"])
def scroll()
⋮----
response = {"result": "KeyError", "error": "keys x and y not posted."}
⋮----
response = {"result": "ValueError", "error": "invalid integer."}
⋮----
@scrollphathd_blueprint.route('/show', methods=["POST"])
def show()
⋮----
response = {"result": "KeyError", "error": "key 'text' not set"}
⋮----
@scrollphathd_blueprint.route('/clear', methods=["POST"])
def clear()
⋮----
@scrollphathd_blueprint.route('/flip', methods=["POST"])
def flip()
⋮----
response = {"result": "TypeError", "error": "Could not cast data correctly. Both `x` and `y` must be set to true or false."}
⋮----
response = {"result": "KeyError", "error": "Could not cast data correctly. Both `x` and `y` must be in the posted json data."}
⋮----
def cleanup()
⋮----
# Reset the autoscroll
⋮----
# Clear the buffer before writing new text
⋮----
def run()
⋮----
action = api_queue.get(block=True)
⋮----
def start_background_thread()
⋮----
api_thread = StoppableThread(target=run)
⋮----
# Autoscroll handling
autoscroll = AutoScroll()
def main()
⋮----
# Parser handling
parser = ArgumentParser()
⋮----
args = parser.parse_args()
# TODO Check
⋮----
# Flash usage
app = Flask(__name__)
````

## File: library/scrollphathd/api/stoppablethread.py
````python
class StoppableThread(threading.Thread)
⋮----
"""Basic Stoppable Thread Wrapper
    Adds event for stopping the execution
    loop and exiting cleanly."""
def __init__(self, *args, **kwargs)
def start(self)
def stop(self)
````

## File: library/scrollphathd/fonts/__init__.py
````python

````

## File: library/scrollphathd/fonts/font3x5.py
````python
data = {
width = 3
height = 5
````

## File: library/scrollphathd/fonts/font5x5.py
````python
data = {
width = 5
height = 5
````

## File: library/scrollphathd/fonts/font5x7.py
````python
data = {
width = 5
height = 7
````

## File: library/scrollphathd/fonts/font5x7smoothed.py
````python
data = {
width = 5
height = 7
````

## File: library/scrollphathd/fonts/font5x7unicode.py
````python
data = {
width = 5
height = 7
````

## File: library/scrollphathd/fonts/fontd3.py
````python
data = {
width = 6
height = 5
````

## File: library/scrollphathd/fonts/fontgauntlet.py
````python
data = {
width = 7
height = 7
````

## File: library/scrollphathd/fonts/fonthachicro.py
````python
data = {
width = 7
height = 7
````

## File: library/scrollphathd/fonts/fontorgan.py
````python
data = {
width = 13
height = 7
````

## File: library/scrollphathd/__init__.py
````python
"""Python library for the Pimoroni Scroll pHAT HD 17x7 pixel LED display."""
⋮----
__version__ = '1.3.0'
DISPLAY_WIDTH = width = 17
DISPLAY_HEIGHT = height = 7
_clear_on_exit = True
_current_frame = 0
_font = font5x7
_flipx = False
_flipy = False
_scroll = [0, 0]
_rotate = 0
_brightness = 1.0
_gamma_table = [
display = None
buf = None
def setup(i2c_dev=None, i2c_address=0x74)
⋮----
"""Set up Scroll pHAT HD.
    :param i2c_dev: smbus-compatible i2c object
    :param i2c_address: 7-bit i2c address
    """
⋮----
display = is31fl3731.IS31FL3731(
enable_pattern = [
⋮----
# Matrix A   Matrix B
⋮----
def set_clear_on_exit(value=True)
⋮----
"""Set whether Scroll pHAT HD should be cleared upon exit.
    By default Scroll pHAT HD will turn off the pixerl on exit, but calling::
        scrollphathd.set_clear_on_exit(False)
    Will ensure that it does not.
    :param value: True or False (default True)
    """
⋮----
_clear_on_exit = value
def set_pixel(x, y, brightness)
⋮----
"""Set a single pixel in the buffer.
    :param x: Position of pixel from left of buffer
    :param y: Position of pixel from top of buffer
    :param brightness: Intensity of the pixel, from 0.0 to 1.0
    """
⋮----
buf = grow_buffer(x + 1, y + 1)
⋮----
def pixel(x, y, brightness)
def grow_buffer(x, y)
⋮----
"""Grows a copy of the buffer until the new shape fits inside it.
    :param x: Minimum x size
    :param y: Minimum y size
    """
x_pad = max(0, x - buf.shape[0])
y_pad = max(0, y - buf.shape[1])
⋮----
def get_shape()
⋮----
"""Get the size/shape of the display.
    Returns a tuple containing the width and height of the display, after applying rotation.
    """
⋮----
def show(before_display=None)
⋮----
"""Show the buffer contents on the display.
    The buffer is copied, then scrolling, rotation and flip y/x transforms applied before taking a 17x7 slice and displaying.
    """
⋮----
_current_frame = not _current_frame
⋮----
display_buffer = grow_buffer(display_width, display_height)
⋮----
display_buffer = numpy.roll(
# Chop a width * height window out of the display buffer
display_buffer = display_buffer[:display_width, :display_height]
# Allow the cropped buffer to be modified in-place before it's transformed and displayed
# This permits static elements to be drawn over the top of a scrolling buffer
⋮----
display_buffer = before_display(display_buffer)
⋮----
display_buffer = numpy.flipud(display_buffer)
⋮----
display_buffer = numpy.fliplr(display_buffer)
⋮----
display_buffer = numpy.rot90(display_buffer, _rotate)
⋮----
idx = _pixel_addr(x, height - (y + 1))
⋮----
value = _gamma_table[int(display_buffer[x][y] * 255 * _brightness)]
⋮----
value = 0
⋮----
def set_graph(values, low=None, high=None, brightness=1.0, x=0, y=0, width=None, height=None)
⋮----
"""Plot a series of values into the display buffer."""
⋮----
width = DISPLAY_WIDTH
⋮----
height = DISPLAY_HEIGHT
⋮----
low = min(values)
⋮----
high = max(values)
buf = grow_buffer(x + width, y + height)
span = high - low
⋮----
value = values[p_x]
⋮----
value = min(value, height * 10)
value = max(value, 0)
⋮----
b = brightness
⋮----
b = (value / 10.0) * brightness
⋮----
def set_brightness(brightness)
⋮----
"""Set a global brightness value.
    :param brightness: Brightness value from 0.0 to 1.0
    """
⋮----
_brightness = brightness
def scroll(x=1, y=0)
⋮----
"""Offset the buffer by x/y pixels.
    Scroll pHAT HD displaya a 17x7 pixel window into the buffer,
    which starts at the left/x offset and wraps around.
    Supplied x and y values are added to the internal scroll offset.
    If called with no arguments, a horizontal right to left scroll by 1 pixel is applied.
    :param x: Number of pixels to scroll on x-axis (default 1)
    :param y: Number of pixels to scroll on y-axis (default 0)
    """
⋮----
def scroll_to(x=0, y=0)
⋮----
"""Scroll the buffer to a specific location.
    Scroll pHAT HD displays a 17x7 pixel window into the buffer.
    which starts at the left/x offset and wraps around.
    Supplied x and y values set the internal scroll offset.
    If called with no arguments, the scroll offset is reset to 0, 0
    :param x: Pixel position to scroll to on x-axis (default 0)
    :param y: Pixel position to scroll to on y-axis (default 0)
    """
⋮----
def rotate(degrees=0)
⋮----
"""Rotate the buffer 0, 90, 180 or 270 degrees before displaying.
    :param degrees: Amount to rotate- will snap to nearest 90
    """
⋮----
_rotate = int(round(degrees / 90.0))
def flip(x=False, y=False)
⋮----
"""Flip the buffer horizontally and/or vertically before displaying.
    :param x: Flip horizontally left to right
    :param y: Flip vertically up to down
    """
⋮----
_flipx = x
_flipy = y
def set_font(font)
⋮----
"""Set a global font value.
    :param font: Font value from .font (font3x5, font5x5, font5x7, font5x7smoothed)
    Note: Import the font before invoking set_font(), (available by) default is font5x7.
    """
⋮----
_font = font
def draw_char(x, y, char, font=None, brightness=1.0, monospaced=False)
⋮----
"""Draw a single character to the buffer.
    Returns the x and y coordinates of the bottom-left most corner of the drawn character.
    :param o_x: Offset x - distance of char from left of the buffer.
    :param o_y: Offset y - distance of char from top of the buffer.
    :param char: Char to display- either an integer ordinal or a single character.
    :param font: Font to use, default is to use the one specified with `set_font`
    :param brightness: Brightness of the pixels that comprise the char, from 0.0 to 1.0.
    :param monospaced: Whether to space characters out evenly using `font.width`
    """
⋮----
font = _font
⋮----
char_map = font.data[char]
⋮----
char_map = font.data[ord(char)]
⋮----
pixel = char_map[py][px]
⋮----
px = font.width - 1
⋮----
def calculate_string_width(string, font=None, letter_spacing=1, monospaced=False)
⋮----
"""Calculate the width of a string.
    :param string: The string to measure
    :param font: Font to use, by default the one specified with `set_font` is used.
    :param letter_spacing: Distance (in pixels) between characters.
    :param monospaced: Whether to space characters out evenly using `font.width`
    """
width = 0
⋮----
def calculate_char_width(char, font=None, monospaced=False)
⋮----
"""Calculate the width of a single character in the current or specified font.
    :param char: The character to measure
    :param font: Font to use, by default the one specified with `set_font` is used.
    :param monospaced: Whether to space characters out evenly using `font.width`
    """
⋮----
def write_string(string, x=0, y=0, font=None, letter_spacing=1, brightness=1.0, monospaced=False, fill_background=False)
⋮----
"""Write a string to the buffer. Calls draw_char for each character.
    :param string: The string to display.
    :param x: Offset x - distance of string from left of the buffer
    :param y: Offset y - distance of string from right of the buffer
    :param letter_spacing: Distance (in pixels) between characters
    :param font: Font to use, defualt is to use the one specified with `set_font`
    :param brightness: Brightness of the pixels that comprise the text, from 0.0 to 1.0
    :param monospaced: Whether to space characters evenly using `font.width`
    :param fill_background: Not used
    """
⋮----
o_x = x
⋮----
string_width = calculate_string_width(
buf = grow_buffer(x + string_width, y + font.height)
⋮----
def fill(brightness, x=0, y=0, width=None, height=None)
⋮----
"""Fill an area of the display.
    :param brightness: Brightness of pixels.
    :param x: Offset x - distance of area from left of buffer.
    :param y: Offset y - distance of area from top of buffer.
    :param width: Width of area (default is buffer width).
    :param height: Height of area (default is buffer height).
    """
⋮----
width = buf.shape[0]
⋮----
height = buf.shape[1]
⋮----
# fill in one operation using a slice
⋮----
def clear_rect(x, y, width, height)
⋮----
"""Clear a rectangular area.
    :param x: Offset x - distance from left of buffer
    :param y: Offset y - distance from top of buffer
    :param width: Width of area (default is 17)
    :param height: Heigh of area (default is 7)
    """
⋮----
def clear()
⋮----
"""Clear the buffer.
    You must call `show` after clearing the buffer to update the display.
    """
⋮----
buf = numpy.zeros((DISPLAY_WIDTH, DISPLAY_HEIGHT))
def get_buffer_shape()
⋮----
"""Get the size/shape of the internal buffer.
    Returns a tuple containing the width and height of the buffer.
    """
⋮----
def _pixel_addr(x, y)
⋮----
"""Translate an x,y coordinate to a pixel index."""
⋮----
x = x - 8
y = 6 - (y + 8)
⋮----
x = 8 - x
⋮----
def _exit()
````

## File: library/scrollphathd/is31fl3731.py
````python
"""IS31FL3731 144 LED Matrix Driver."""
⋮----
_MODE_REGISTER = 0x00
_FRAME_REGISTER = 0x01
_AUTOPLAY1_REGISTER = 0x02
_AUTOPLAY2_REGISTER = 0x03
_BLINK_REGISTER = 0x05
_AUDIOSYNC_REGISTER = 0x06
_BREATH1_REGISTER = 0x08
_BREATH2_REGISTER = 0x09
_SHUTDOWN_REGISTER = 0x0a
_GAIN_REGISTER = 0x0b
_ADC_REGISTER = 0x0c
_CONFIG_BANK = 0x0b
_BANK_ADDRESS = 0xfd
_PICTURE_MODE = 0x00
_AUTOPLAY_MODE = 0x08
_AUDIOPLAY_MODE = 0x18
_ENABLE_OFFSET = 0x00
_BLINK_OFFSET = 0x12
_COLOR_OFFSET = 0x24
_NUM_PIXELS = 144
_NUM_FRAMES = 8
class IS31FL3731
⋮----
"""Class representing the IS31FL3731 matrix driver."""
def __init__(self, i2c=None, address=0x74)
⋮----
"""Initialise the IS31FL3731.
        :param i2c: smbus-compatible i2c object
        :param address: 7-bit i2c address of attached IS31FL3731
        """
⋮----
def set_mode(self, mode)
⋮----
"""Set display mode."""
⋮----
def set_audiosync(self, state)
⋮----
"""Set Audio Sync mode."""
⋮----
def enable_leds(self, frame, enable_pattern)
⋮----
"""Enable LEDs."""
⋮----
def clear(self)
⋮----
"""Clear the buffer.
        You must call `show` after clearing the buffer to update the display.
        """
⋮----
def set_pixel(self, frame, index, brightness)
⋮----
"""Set a single pixel in the buffer.
        :param x: Position of pixel from 0 to 143
        :param brightness: Intensity of the pixel, from 0 to 255.
        """
⋮----
def set_frame(self, frame, values)
⋮----
"""Set the entire display buffer for a frame."""
⋮----
def update_frame(self, frame)
⋮----
"""Show the buffer contents on the display."""
⋮----
offset = 0
⋮----
def reset(self)
⋮----
"""Reset the IS31FL3731."""
⋮----
def sleep(self, value)
⋮----
"""Put the IS31FL3731 into sleep mode."""
⋮----
def show_frame(self, frame)
⋮----
"""Switch to showing a specific frame.
        :param frame: Frame to show
        """
⋮----
def set_bank(self, bank)
⋮----
"""Set the current memory bank/frame."""
⋮----
def get_bank(self)
⋮----
"""Get the current memory bank/frame."""
⋮----
def _i2c_write(self, register, value, bank=None)
⋮----
"""Write a byte to an i2c register."""
⋮----
def _i2c_read(self, register, bank=None)
⋮----
"""Read a byte from an i2c register."""
⋮----
def _chunk(self, l, n)
⋮----
"""Split a list of values in to chunks of length n."""
````

## File: library/CHANGELOG.txt
````
1.3.0
-----

* Improvement: Default i2c library is now smbus2
* Improvement: Significant restructure of library around generic is31fl3731 driver
* Improvement: Allow for alternate i2c addresses
* BugFix: Add missing get_buffer_shape
* BugFix: Fix malformed chars in font5x7
* New: Fonts, fonts, fonts, and a set_font method to use them

1.2.1
-----

* New: Exposed set_gamma method for user gamma correction
* Improvement: Removed web API import to prevent hard dependency on Flask
* Improvement: Many improvements to the HTTP API including autoscroll
* Optimisation: write_string will calculate string size and grow buffer once to fit
* Optimisation: set_graph will grow buffer to fit the graph
* Bugfix: Fixed ASCII font to place accented characters at correct codepoints

1.2.0
-----

* New: Added set_font to set current font for all write_string calls
* New: Added before_display argument to show to modify the display buffer

1.1.1
-----

* Bugfix: Removed Flask HTTP API entry_point to prevent bin file conflict between Python 2 and 3

1.1.0
-----

* New: Added Flask HTTP API
* New: Init is deferred until the library is used

1.0.1
-----

* New: Added gamma correction

1.0.0
-----

* New: Added set_brightness to globally set maximum display brightness
* New: Added get_buffer_shape to return internal buffer shape
* New: Added get_shape to return display shape
* New: Added set_clear_on_exit, pass True/False to set/clear
* Improvement: draw_char no longer fills black pixels, which was incongruent with letter spacing
* Improvement: '1' in font3x5 is now 3 pixels wide
* Improvement: Monospacing option for fonts
* Improvement: Fonts can now be indexed by char in addition to ordinal
* Improvement: Clear now resets scroll position
* Improvement: Fill now grows buffer and fills in single operations
* Improvement: scroll(0,0) no longer enforces a default scroll
* Improvement: width/height now private, reimplemented as read-only properties
* Improvement: initialization now detects disabled i2c or missing pHAT and emits a friendly error
* Improvement: cleared display sooner to mitigate flash of lit pixels on startup
* Bugfix: Corrected default scroll direction
* Bugfix: 90 and 270 degree rotations are no longer cropped to 7 pixels wide
* Bugfix: Fixed missing version_info
* Bugfix: Graph catches IndexError and gracefully ignores missing values

0.0.1
-----

* Initial release
````

## File: library/LICENSE.txt
````
The MIT License (MIT)

Copyright (c) 2017 Pimoroni Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
````

## File: library/MANIFEST.in
````
include CHANGELOG.txt
include LICENSE.txt
include README.rst
include setup.py
recursive-include scrollphathd *.py
````

## File: library/README.rst
````rst
|Scroll pHAT HD| https://shop.pimoroni.com/products/scroll-phat-hd

17x7 pixels of single-colour, brightness-controlled, message scrolling
goodness!

Installing
----------

Full install (recommended):
~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've created an easy installation script that will install all
pre-requisites and get your Scroll pHAT HD up and running with minimal
efforts. To run it, fire up Terminal which you'll find in Menu ->
Accessories -> Terminal on your Raspberry Pi desktop, as illustrated
below:

.. figure:: http://get.pimoroni.com/resources/github-repo-terminal.png
   :alt: Finding the terminal

In the new terminal window type the command exactly as it appears below
(check for typos) and follow the on-screen instructions:

.. code:: bash

    curl https://get.pimoroni.com/scrollphathd | bash

Alternatively, on Raspbian, you can download the ``pimoroni-dashboard``
and install your product by browsing to the relevant entry:

.. code:: bash

    sudo apt-get install pimoroni

(you will find the Dashboard under 'Accessories' too, in the Pi menu -
or just run ``pimoroni-dashboard`` at the command line)

If you choose to download examples you'll find them in
``/home/pi/Pimoroni/scrollphathd/``.

Manual install:
~~~~~~~~~~~~~~~

Library install for Python 3:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

on Raspbian:

.. code:: bash

    sudo apt-get install python3-scrollphathd

other environments:

.. code:: bash

    sudo pip3 install scrollphathd

Library install for Python 2:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

on Raspbian:

.. code:: bash

    sudo apt-get install python-scrollphathd

other environments:

.. code:: bash

    sudo pip2 install scrollphathd

Development:
~~~~~~~~~~~~

If you want to contribute, or like living on the edge of your seat by
having the latest code, you should clone this repository, ``cd`` to the
library directory, and run:

.. code:: bash

    sudo python3 setup.py install

(or ``sudo python setup.py install`` whichever your primary Python
environment may be)

In all cases you will have to enable the i2c bus.

Documentation & Support
-----------------------

-  Guides and tutorials - https://learn.pimoroni.com/scroll-phat-hd
-  Function reference - http://docs.pimoroni.com/scrollphathd/
-  GPIO Pinout - https://pinout.xyz/pinout/scroll\_phat\_hd
-  Get help - http://forums.pimoroni.com/c/support

Unofficial / Third-party libraries
----------------------------------

-  Java library by Jim Darby - https://github.com/hackerjimbo/PiJava
-  Rust library by Tiziano Santoro -
   https://github.com/tiziano88/scroll-phat-hd-rs
-  Go library by Tom Mitchell -
   https://github.com/tomnz/scroll-phat-hd-go

.. |Scroll pHAT HD| image:: https://raw.githubusercontent.com/pimoroni/scroll-phat-hd/master/scroll-phat-hd-logo.png
````

## File: library/setup.py
````python
#!/usr/bin/env python
"""
Copyright (c) 2017 Pimoroni
Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
⋮----
classifiers = ['Development Status :: 5 - Production/Stable',
````

## File: packaging/debian/source/format
````
3.0 (native)
````

## File: packaging/debian/source/options
````
extend-diff-ignore = "^[^/]+\.egg-info/"
````

## File: packaging/debian/changelog
````
scrollphathd (1.2.1) stable; urgency=low

  * New: Exposed set_gamma method for user gamma correction
  * Improvement: Removed web API import to prevent hard dependency on Flask
  * Improvement: Many improvements to the HTTP API including autoscroll
  * Optimisation: write_string will calculate string size and grow buffer once to fit
  * Optimisation: set_graph will grow buffer to fit the graph
  * Bugfix: Fixed ASCII font to place accented characters at correct codepoints

 -- Phil Howard <phil@pimoroni.com>  Wed, 21 Mar 2018 00:00:00 +0000

scrollphathd (1.2.0) stable; urgency=low

  * New: Added set_font to set current font for all write_string calls
  * New: Added before_display argument to show to modify the display buffer

 -- Phil Howard <phil@pimoroni.com>  Mon, 12 Feb 2018 00:00:00 +0000

scrollphathd (1.1.1) stable; urgency=low

  * Bugfix: Removed Flask HTTP API entry_point to prevent bin file conflict between Python 2 and 3

 -- Phil Howard <phil@pimoroni.com>  Tue, 16 Jan 2018 00:00:00 +0000

scrollphathd (1.1.0) stable; urgency=low

  * New: Added Flask HTTP API
  * New: Init is deferred until the library is used

 -- Phil Howard <phil@pimoroni.com>  Thu, 11 Jan 2018 00:00:00 +0000

scrollphathd (1.0.1) stable; urgency=low

  * New: Added gamma correction

 -- Phil Howard <phil@pimoroni.com>  Fri, 12 May 2017 00:00:00 +0000

scrollphathd (1.0.0) stable; urgency=low

  * New: Added set_brightness to globally set maximum display brightness
  * New: Added get_buffer_shape to return internal buffer shape
  * New: Added get_shape to return display shape
  * New: Added set_clear_on_exit, pass True/False to set/clear
  * Improvement: draw_char no longer fills black pixels, which was incongruent with letter spacing
  * Improvement: '1' in font3x5 is now 3 pixels wide
  * Improvement: Monospacing option for fonts
  * Improvement: Fonts can now be indexed by char in addition to ordinal
  * Improvement: Clear now resets scroll position
  * Improvement: Fill now grows buffer and fills in single operations
  * Improvement: scroll(0,0) no longer enforces a default scroll
  * Improvement: width/height now private, reimplemented as read-only properties
  * Improvement: initialization now detects disabled i2c or missing pHAT and emits a friendly error
  * Improvement: cleared display sooner to mitigate flash of lit pixels on startup
  * Bugfix: Corrected default scroll direction
  * Bugfix: 90 and 270 degree rotations are no longer cropped to 7 pixels wide
  * Bugfix: Fixed missing version_info
  * Bugfix: Graph catches IndexError and gracefully ignores missing values

 -- Phil Howard <phil@pimoroni.com>  Tue, 13 Mar 2017 00:00:00 +0000

scrollphathd (0.0.1) stable; urgency=low

  * Initial release

 -- Phil Howard <phil@pimoroni.com>  Tue, 14 Feb 2017 00:00:00 +0000
````

## File: packaging/debian/clean
````
*.egg-info/*
````

## File: packaging/debian/compat
````
9
````

## File: packaging/debian/control
````
Source: scrollphathd
Maintainer: Phil Howard <phil@pimoroni.com>
Homepage: https://github.com/pimoroni/scroll-phat-hd
Section: python
Priority: extra
Build-Depends: debhelper (>= 9.0.0), dh-python, python-all (>= 2.7), python-setuptools, python3-all (>= 3.4), python3-setuptools
Standards-Version: 3.9.6
X-Python-Version: >= 2.7
X-Python3-Version: >= 3.4

Package: python-scrollphathd
Architecture: all
Section: python
Depends: ${misc:Depends}, ${python:Depends}, python-smbus, python-numpy
Suggests: i2c-tools, python-psutil
Description: Python library for the Pimoroni Scroll pHAT HD.
 Scroll pHAT HD provides a matrix of 119, brightness controlled,
 white LED pixels.
 It's ideal for writing messages, showing graphs, and drawing pictures.
 .
 This is the Python 2 version of the package.

Package: python3-scrollphathd
Architecture: all
Section: python
Depends: ${misc:Depends}, ${python3:Depends}, python3-smbus, python3-numpy
Suggests: i2c-tools, python3-psutil
Description: Python library for the Pimoroni Scroll pHAT HD.
 Scroll pHAT HD provides a matrix of 119, brightness controlled,
 white LED pixels.
 It's ideal for writing messages, showing graphs, and drawing pictures.
 .
 This is the Python 3 version of the package.
````

## File: packaging/debian/copyright
````
Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: scrollphathd
Source: https://github.com/pimoroni/scroll-phat-hd

Files: *
Copyright: 2017 Pimoroni Ltd <phil@pimoroni.com>
License: MIT

License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
````

## File: packaging/debian/docs
````

````

## File: packaging/debian/README
````
README

Scroll pHAT HD provides a matrix of 119, brightness controlled, white LED pixels. It's ideal for writing messages, showing graphs, and drawing pictures.

Learn more: https://shop.pimoroni.com/products/scroll-phat-hd
For examples run: `curl -sS get.pimoroni.com/scrollphathd | bash`

IMPORTANT

Scroll pHAT HD requires i2c.
To enable run `curl get.pimoroni.com/i2c | bash`
or use raspi-config and reboot your Raspberry Pi.
````

## File: packaging/debian/rules
````
#!/usr/bin/make -f
# -*- makefile -*-

#export DH_VERBOSE=1
export DH_OPTIONS

%:
	dh $@ --with python2,python3 --buildsystem=python_distutils

override_dh_auto_install:
	python setup.py install --root debian/python-scrollphathd --install-layout=deb
	python3 setup.py install --root debian/python3-scrollphathd --install-layout=deb
````

## File: packaging/CHANGELOG
````
scrollphathd (1.2.1) stable; urgency=low

  * New: Exposed set_gamma method for user gamma correction
  * Improvement: Removed web API import to prevent hard dependency on Flask
  * Improvement: Many improvements to the HTTP API including autoscroll
  * Optimisation: write_string will calculate string size and grow buffer once to fit
  * Optimisation: set_graph will grow buffer to fit the graph
  * Bugfix: Fixed ASCII font to place accented characters at correct codepoints

 -- Phil Howard <phil@pimoroni.com>  Wed, 21 Mar 2018 00:00:00 +0000

scrollphathd (1.2.0) stable; urgency=low

  * New: Added set_font to set current font for all write_string calls
  * New: Added before_display argument to show to modify the display buffer

 -- Phil Howard <phil@pimoroni.com>  Mon, 12 Feb 2018 00:00:00 +0000

scrollphathd (1.1.1) stable; urgency=low

  * Bugfix: Removed Flask HTTP API entry_point to prevent bin file conflict between Python 2 and 3

 -- Phil Howard <phil@pimoroni.com>  Tue, 16 Jan 2018 00:00:00 +0000

scrollphathd (1.1.0) stable; urgency=low

  * New: Added Flask HTTP API
  * New: Init is deferred until the library is used

 -- Phil Howard <phil@pimoroni.com>  Thu, 11 Jan 2018 00:00:00 +0000

scrollphathd (1.0.1) stable; urgency=low

  * New: Added gamma correction

 -- Phil Howard <phil@pimoroni.com>  Fri, 12 May 2017 00:00:00 +0000

scrollphathd (1.0.0) stable; urgency=low

  * New: Added set_brightness to globally set maximum display brightness
  * New: Added get_buffer_shape to return internal buffer shape
  * New: Added get_shape to return display shape
  * New: Added set_clear_on_exit, pass True/False to set/clear
  * Improvement: draw_char no longer fills black pixels, which was incongruent with letter spacing
  * Improvement: '1' in font3x5 is now 3 pixels wide
  * Improvement: Monospacing option for fonts
  * Improvement: Fonts can now be indexed by char in addition to ordinal
  * Improvement: Clear now resets scroll position
  * Improvement: Fill now grows buffer and fills in single operations
  * Improvement: scroll(0,0) no longer enforces a default scroll
  * Improvement: width/height now private, reimplemented as read-only properties
  * Improvement: initialization now detects disabled i2c or missing pHAT and emits a friendly error
  * Improvement: cleared display sooner to mitigate flash of lit pixels on startup
  * Bugfix: Corrected default scroll direction
  * Bugfix: 90 and 270 degree rotations are no longer cropped to 7 pixels wide
  * Bugfix: Fixed missing version_info
  * Bugfix: Graph catches IndexError and gracefully ignores missing values

 -- Phil Howard <phil@pimoroni.com>  Tue, 13 Mar 2017 00:00:00 +0000

scrollphathd (0.0.1) stable; urgency=low

  * Initial release

 -- Phil Howard <phil@pimoroni.com>  Tue, 14 Feb 2017 00:00:00 +0000
````

## File: packaging/makeall.sh
````bash
#!/bin/bash
# script control variables
reponame="" # leave this blank for auto-detection
libname="" # leave this blank for auto-detection
packagename="" # leave this blank for auto-selection
debianlog="debian/changelog"
debcontrol="debian/control"
debcopyright="debian/copyright"
debrules="debian/rules"
debreadme="debian/README"
debdir="$(pwd)"
rootdir="$(dirname $debdir)"
libdir="$rootdir/library"
FLAG=false
# function define
success() {
    echo "$(tput setaf 2)$1$(tput sgr0)"
}
inform() {
    echo "$(tput setaf 6)$1$(tput sgr0)"
}
warning() {
    echo "$(tput setaf 1)$1$(tput sgr0)"
}
newline() {
    echo ""
}
# assessing repo and library variables
if [ -z "$reponame" ] || [ -z "$libname" ]; then
    inform "detecting reponame and libname..."
else
    inform "using reponame and libname overrides"
fi
if [ -z "$reponame" ]; then
    if [[ $rootdir == *"python"* ]]; then
        repodir="$(dirname $rootdir)"
        reponame="$(basename $repodir)"
    else
        repodir="$rootdir"
        reponame="$(basename $repodir)"
    fi
    reponame=$(echo "$reponame" | tr "[A-Z]" "[a-z]")
fi
if [ -z "$libname" ]; then
    cd "$libdir"
    libname=$(grep "name" setup.py | tr -d "[:space:]" | cut -c 7- | rev | cut -c 3- | rev)
    libname=$(echo "$libname" | tr "[A-Z]" "[a-z]") && cd "$debdir"
fi
if [ -z "$packagename" ]; then
    packagename="$libname"
fi
echo "reponame is $reponame and libname is $libname"
echo "output packages will be python-$packagename and python3-$packagename"
# checking generating changelog file
./makelog.sh
version=$(head -n 1 "$libdir/CHANGELOG.txt")
echo "building $libname version $version"
# checking debian/changelog file
inform "checking debian/changelog file..."
if ! head -n 1 $debianlog | grep "$libname" &> /dev/null; then
    warning "library not mentioned in header!" && FLAG=true
elif head -n 1 $debianlog | grep "UNRELEASED"; then
    warning "this changelog is not going to generate a release!"
    warning "change distribution to 'stable'" && FLAG=true
fi
# checking debian/copyright file
inform "checking debian/copyright file..."
if ! grep "^Source" $debcopyright | grep "$reponame" &> /dev/null; then
    warning "$(grep "^Source" $debcopyright)" && FLAG=true
fi
if ! grep "^Upstream-Name" $debcopyright | grep "$libname" &> /dev/null; then
    warning "$(grep "^Upstream-Name" $debcopyright)" && FLAG=true
fi
# checking debian/control file
inform "checking debian/control file..."
if ! grep "^Source" $debcontrol | grep "$libname" &> /dev/null; then
    warning "$(grep "^Source" $debcontrol)" && FLAG=true
fi
if ! grep "^Homepage" $debcontrol | grep "$reponame" &> /dev/null; then
    warning "$(grep "^Homepage" $debcontrol)" && FLAG=true
fi
if ! grep "^Package: python-$packagename" $debcontrol &> /dev/null; then
    warning "$(grep "^Package: python-" $debcontrol)" && FLAG=true
fi
if ! grep "^Package: python3-$packagename" $debcontrol &> /dev/null; then
    warning "$(grep "^Package: python3-" $debcontrol)" && FLAG=true
fi
if ! grep "^Priority: extra" $debcontrol &> /dev/null; then
    warning "$(grep "^Priority" $debcontrol)" && FLAG=true
fi
# checking debian/rules file
inform "checking debian/rules file..."
if ! grep "debian/python-$packagename" $debrules &> /dev/null; then
    warning "$(grep "debian/python-" $debrules)" && FLAG=true
fi
if ! grep "debian/python3-$packagename" $debrules &> /dev/null; then
    warning "$(grep "debian/python3-" $debrules)" && FLAG=true
fi
# checking debian/README file
inform "checking debian/readme file..."
if ! grep -e "$libname" -e "$reponame" $debreadme &> /dev/null; then
    warning "README does not seem to mention product, repo or lib!" && FLAG=true
fi
# summary of checks pre build
if $FLAG; then
    warning "Check all of the above and correct!" && exit 1
else
    inform "we're good to go... bulding!"
fi
# building deb and final checks
./makedeb.sh
inform "running lintian..."
lintian -v $(find -name "python*$version*.deb")
lintian -v $(find -name "python3*$version*.deb")
inform "checking signatures..."
gpg --verify $(find -name "*$version*changes")
gpg --verify $(find -name "*$version*dsc")
exit 0
````

## File: packaging/makedeb.sh
````bash
#!/bin/bash
gettools="no" # if set to yes downloads the tools required
setup="yes" # if set to yes populates library folder
buildeb="yes" # if set to yes builds the deb files
cleanup="yes" # if set to yes cleans up build files
pkgfiles=( "build" "changes" "deb" "dsc" "tar.xz" )
if [ $gettools == "yes" ]; then
    sudo apt-get update && sudo apt-get install build-essential debhelper devscripts dh-make dh-python dput gnupg
    sudo apt-get install python-all python-setuptools python3-all python3-setuptools
    sudo apt-get install python-mock python-sphinx python-sphinx-rtd-theme
    sudo pip install Sphinx --upgrade && sudo pip install sphinx_rtd_theme --upgrade
fi
if [ $setup == "yes" ]; then
    rm -R ../library/build ../library/debian &> /dev/null
    cp -R ./debian ../library/ && cp -R ../sphinx ../library/doc
fi
cd ../library
if [ $buildeb == "yes" ]; then
    debuild -aarmhf
    for file in ${pkgfiles[@]}; do
        rm ../packaging/*.$file &> /dev/null
        mv ../*.$file ../packaging
    done
    rm -R ../documentation/html &> /dev/null
    cp -R ./build/sphinx/html ../documentation
fi
if [ $cleanup == "yes" ]; then
    debuild clean
    rm -R ./build ./debian ./doc &> /dev/null
fi
exit 0
````

## File: packaging/makedoc.sh
````bash
#!/bin/bash
gettools="no" # if set to yes downloads the tools required
setup="yes" # if set to yes populates library folder
buildoc="yes" # if set to yes builds the deb files
cleanup="yes" # if set to yes cleans up build files
pkgfiles=( "build" "changes" "deb" "dsc" "tar.xz" )
if [ $gettools == "yes" ]; then
    sudo apt-get update && sudo apt-get install build-essential debhelper devscripts dh-make dh-python
    sudo apt-get install python-all python-setuptools python3-all python3-setuptools
    sudo apt-get install python-mock python-sphinx python-sphinx-rtd-theme
    sudo pip install Sphinx --upgrade && sudo pip install sphinx_rtd_theme --upgrade
fi
if [ $setup == "yes" ]; then
    rm -R ../library/build ../library/debian &> /dev/null
    cp -R ./debian ../library/ && cp -R ../sphinx ../library/doc
fi
cd ../library
if [ $buildoc == "yes" ]; then
    debuild
    for file in ${pkgfiles[@]}; do
        rm ../*.$file &> /dev/null
    done
    rm -R ../documentation/html &> /dev/null
    cp -R ./build/sphinx/html ../documentation
fi
if [ $cleanup == "yes" ]; then
    debuild clean
    rm -R ./build ./debian ./doc &> /dev/null
fi
exit 0
````

## File: packaging/makelog.sh
````bash
#!/bin/bash
# script control variables
libname="" # leave this blank for auto-detection
sibname=() # name of sibling in packages list
versionwarn="yes" # set to anything but 'yes' to turn off warning
debdir="$(pwd)"
rootdir="$(dirname $debdir)"
libdir="$rootdir/library"
mainlog="CHANGELOG"
debianlog="debian/changelog"
pypilog="$libdir/CHANGELOG.txt"
# function define
success() {
    echo "$(tput setaf 2)$1$(tput sgr0)"
}
inform() {
    echo "$(tput setaf 6)$1$(tput sgr0)"
}
warning() {
    echo "$(tput setaf 1)$1$(tput sgr0)"
}
newline() {
    echo ""
}
# generate debian changelog
cat $mainlog > $debianlog
inform "seeded debian changelog"
# generate pypi changelog
sed -e "/--/d" -e "s/  \*/\*/" \
    -e "s/.*\([0-9].[0-9].[0-9]\).*/\1/" \
    -e '/[0-9].[0-9].[0-9]/ a\
-----' $mainlog | cat -s > $pypilog
version=$(head -n 1 $pypilog)
inform "pypi changelog generated"
# touch up version in setup.py file
if [ -n $(grep version "$libdir/setup.py" &> /dev/null) ]; then
    inform "touched up version in setup.py"
    sed -i "s/'[0-9].[0-9].[0-9]'/'$version'/" "$libdir/setup.py"
else
    warning "couldn't touch up version in setup, no match found"
fi
# touch up version in lib or package siblings
if [ -z "$libname" ]; then
    cd "$libdir"
    libname=$(grep "name" setup.py | tr -d "[:space:]" | cut -c 7- | rev | cut -c 3- | rev)
    libname=$(echo "$libname" | tr "[A-Z]" "[a-z]") && cd "$debdir"
    sibname+=( "$libname" )
elif [ "$libname" != "package" ]; then
    sibname+=( "$libname" )
fi
for sibling in ${sibname[@]}; do
    if grep -e "__version__" "$libdir/$sibling.py" &> /dev/null; then
        sed -i "s/__version__ = '[0-9].[0-9].[0-9]'/__version__ = '$version'/" "$libdir/$sibling.py"
        inform "touched up version in $sibling.py"
    elif grep -e "__version__" "$libdir/$sibling/__init__.py" &> /dev/null; then
        sed -i "s/__version__ = '[0-9].[0-9].[0-9]'/__version__ = '$version'/" "$libdir/$sibling/__init__.py"
        inform "touched up version in $sibling/__init__.py"
    elif [ "$versionwarn" == "yes" ]; then
        warning "couldn't touch up __version__ in $sibling, no match found"
    fi
done
exit 0
````

## File: simulator/README.md
````markdown
# Scroll pHAT HD Simulator

A Tk based server to simulate Scroll pHAT HD on your Windows, Linux or macOS PC.

![Swirl running in Scroll pHAT HD simulator](simulator.gif)

Works by hijacking the `smbus` module imported by `scrollphathd` and replacing it with a FIFO pipe to the Tk based simulator.

## Usage

Set the `PYTHONPATH` variable to the simulator directory and run an example. The fake `smbus` will be loaded instead of the real one and output will launch in a new window:

```
PYTHONPATH=simulator python3 examples/clock.py
```
````

## File: simulator/scroll_phat_simulator.py
````python
ROWS = 7
COLUMNS = 17
LED_SIZE_PX = 50
LINE_WIDTH_PX = 5
WINDOW_HEIGHT_PX = LED_SIZE_PX * ROWS + LINE_WIDTH_PX * (ROWS - 1)
WINDOW_WIDTH_PX = LED_SIZE_PX * COLUMNS + LINE_WIDTH_PX * (COLUMNS - 1)
DRAW_TIMEOUT_MS = 100
class ScrollPhatSimulator
⋮----
def set_pixels(self, vals)
def set_brightness(self, brightness)
def run(self)
def running(self)
def destroy(self)
class TkPhatSimulator(ScrollPhatSimulator)
⋮----
def __init__(self)
def pixel_addr(self, x, y)
⋮----
"""Translate an x,y coordinate to a pixel index."""
⋮----
x = x - 8
y = 6 - (y + 8)
⋮----
x = 8 - x
⋮----
def draw_pixels(self)
⋮----
b = self.pixels[col][row]
color = '#{:02x}{:02x}{:02x}'.format(b, b, b)
x = (LED_SIZE_PX + LINE_WIDTH_PX) * col
y = (LED_SIZE_PX + LINE_WIDTH_PX) * row
⋮----
addr = self.pixel_addr(col, ROWS - (row + 1))
⋮----
class ReadThread
⋮----
def __init__(self, scroll_phat_simulator)
def start(self)
def join(self)
def _read_stdin(self)
def _handle_update(self, buffer)
def main()
⋮----
phat = TkPhatSimulator()
thread = ReadThread(phat)
````

## File: simulator/smbus2.py
````python
class SMBus
⋮----
def __init__(self, dummy)
def _start_simulator(self)
def write_byte_data(self, addr, reg, data)
def write_i2c_block_data(self, addr, cmd, vals)
⋮----
I2C_ADDR = 0x74
⋮----
if cmd < 0x24:  # Start of pixel data
⋮----
offset = cmd - 0x24
````

## File: sphinx/_static/custom.css
````css
.rst-content a, .rst-content a:focus {
.rst-content a:visited, .rst-content a:active {
.rst-content .highlighted {
.wy-side-nav-search {
.wy-nav-side {
.wy-menu-vertical a {
.wy-menu-vertical p.caption {
.rst-content dl:not(.docutils) dt {
.rst-content .viewcode-link, .rst-content .viewcode-back {
code.literal {
.rst-content #at-a-glance {
.rst-content #at-a-glance blockquote {
.rst-content #at-a-glance dl:not(.docutils) dt {
.rst-content #at-a-glance dl:not(.docutils) dd,
.rst-content #at-a-glance dl:not(.docutils) {
````

## File: sphinx/_templates/breadcrumbs.html
````html

````

## File: sphinx/_templates/layout.html
````html
{% extends "!layout.html" %}
{% block extrahead %}
	<link rel="stylesheet" href="{{ pathto("_static/custom.css", True) }}" type="text/css">
{% endblock %}
{% block footer %}
<script type="text/javascript">
	var menuItems = $('.wy-menu-vertical').find('a');
	var scrollItems = menuItems.map(function(){
		var item = $($(this).attr('href'));
		if (item.length) { return item; }
	});
	$(window).on('scroll',function(){
		var fromTop = $(this).scrollTop()
		var cur = scrollItems.map(function(){
			if ($(this).offset().top < fromTop+30) return this;
		});
		cur = cur[cur.length-1];
		var id = cur && cur.length ? cur[0].id : "";
		var target = $('#'+id);
		target.attr('id','');
		window.location.hash = '#'+id;
		target.attr('id',id);
		menuItems
			.parent().removeClass("current")
			.end().filter("[href='#"+id+"']").parent().addClass("current");
	});
	$(window).on('hashchange',function(){
		var hash = window.location.hash.replace('#','');
		menuItems
			.parent().removeClass("current")
			.end().filter("[href='#"+hash+"']").parent().addClass("current");
	})
</script>
{% endblock %}
````

## File: sphinx/conf.py
````python
#-*- coding: utf-8 -*-
⋮----
PACKAGE_NAME = u"Scroll pHAT HD"
PACKAGE_HANDLE = "ScrollpHATHD"
PACKAGE_MODULE = "scrollphathd"
⋮----
MOCK_MODULES = ['smbus', 'numpy']
⋮----
class OutlineClassDocumenter(autodoc.ClassDocumenter)
⋮----
objtype = 'class'
def add_content(self, more_content, no_docstring=False)
class OutlineMethodDocumenter(autodoc.MethodDocumenter)
⋮----
objtype = 'method'
⋮----
def add_directive_header(self, sig)
class OutlineFunctionDocumenter(autodoc.FunctionDocumenter)
⋮----
objtype = 'function'
⋮----
class MethodDocumenter(autodoc.MethodDocumenter)
class ModuleOutlineDocumenter(autodoc.ModuleDocumenter)
⋮----
objtype = 'moduleoutline'
⋮----
pass  # Squash directive header for At A Glance view
def __init__(self, directive, name, indent=u'')
⋮----
# Monkey patch the Method and Function documenters
⋮----
# sphinx_app.add_autodocumenter(OutlineClassDocumenter)
⋮----
def __del__(self)
⋮----
# Return the Method and Function documenters to normal
# sphinx_app.add_autodocumenter(autodoc.ClassDocumenter)
⋮----
def setup(app)
⋮----
sphinx_app = app
⋮----
# -- General configuration ------------------------------------------------
# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
⋮----
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'
# The encoding of source files.
⋮----
# source_encoding = 'utf-8-sig'
# The master toctree document.
master_doc = 'index'
# General information about the project.
project = PACKAGE_NAME
copyright = u'2017, Pimoroni Ltd'
author = u'Phil Howard'
# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
⋮----
# The short X.Y version.
version = u'{}'.format(scrollphathd.__version__)
# The full version, including alpha/beta/rc tags.
release = u'{}'.format(scrollphathd.__version__)
# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
⋮----
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None
# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
⋮----
# today = ''
⋮----
# Else, today_fmt is used as the format for a strftime call.
⋮----
# today_fmt = '%B %d, %Y'
# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
# The reST default role (used for this markup: `text`) to use for all
# documents.
⋮----
# default_role = None
# If true, '()' will be appended to :func: etc. cross-reference text.
⋮----
# add_function_parentheses = True
# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
⋮----
# add_module_names = True
# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
⋮----
# show_authors = False
# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'
# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []
# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False
# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False
# -- Options for HTML output ----------------------------------------------
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
⋮----
html_theme = 'sphinx_rtd_theme'
# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
⋮----
html_theme_options = {
# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = [
# The name for this set of Sphinx documents.
# "<project> v<release> documentation" by default.
⋮----
# html_title = PACKAGE_NAME + u' v0.1.2'
# A shorter title for the navigation bar.  Default is the same as html_title.
⋮----
# html_short_title = None
# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
⋮----
html_logo = 'shop-logo.png'
# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
⋮----
html_favicon = 'favicon.png'
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
⋮----
# html_extra_path = []
# If not None, a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
# The empty string is equivalent to '%b %d, %Y'.
⋮----
# html_last_updated_fmt = None
# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
⋮----
# html_use_smartypants = True
# Custom sidebar templates, maps document names to template names.
⋮----
# html_sidebars = {}
# Additional templates that should be rendered to pages, maps page names to
# template names.
⋮----
# html_additional_pages = {}
# If false, no module index is generated.
⋮----
# html_domain_indices = True
# If false, no index is generated.
⋮----
html_use_index = False
# If true, the index is split into individual pages for each letter.
⋮----
# html_split_index = False
# If true, links to the reST sources are added to the pages.
⋮----
html_show_sourcelink = False
# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
⋮----
html_show_sphinx = False
# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
⋮----
# html_show_copyright = True
# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
⋮----
# html_use_opensearch = ''
# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None
# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'ru', 'sv', 'tr', 'zh'
⋮----
# html_search_language = 'en'
# A dictionary with options for the search language support, empty by default.
# 'ja' uses this config value.
# 'zh' user can custom change `jieba` dictionary path.
⋮----
# html_search_options = {'type': 'default'}
# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
⋮----
# html_search_scorer = 'scorer.js'
# Output file base name for HTML help builder.
htmlhelp_basename = PACKAGE_HANDLE + 'doc'
# -- Options for LaTeX output ---------------------------------------------
latex_elements = {
⋮----
# The paper size ('letterpaper' or 'a4paper').
⋮----
# 'papersize': 'letterpaper',
# The font size ('10pt', '11pt' or '12pt').
⋮----
# 'pointsize': '10pt',
# Additional stuff for the LaTeX preamble.
⋮----
# 'preamble': '',
# Latex figure (float) alignment
⋮----
# 'figure_align': 'htbp',
⋮----
# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
# The name of an image file (relative to this directory) to place at the top of
# the title page.
⋮----
# latex_logo = None
# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
⋮----
# latex_use_parts = False
# If true, show page references after internal links.
⋮----
# latex_show_pagerefs = False
# If true, show URL addresses after external links.
⋮----
# latex_show_urls = False
# Documents to append as an appendix to all manuals.
⋮----
# latex_appendices = []
# It false, will not define \strong, \code, 	itleref, \crossref ... but only
# \sphinxstrong, ..., \sphinxtitleref, ... To help avoid clash with user added
# packages.
⋮----
# latex_keep_old_macro_names = True
⋮----
# latex_domain_indices = True
# -- Options for manual page output ---------------------------------------
# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
⋮----
# man_show_urls = False
# -- Options for Texinfo output -------------------------------------------
# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
⋮----
# texinfo_appendices = []
⋮----
# texinfo_domain_indices = True
# How to display URL addresses: 'footnote', 'no', or 'inline'.
⋮----
# texinfo_show_urls = 'footnote'
# If true, do not generate a @detailmenu in the "Top" node's menu.
⋮----
# texinfo_no_detailmenu = False
````

## File: sphinx/index.rst
````rst
.. role:: python(code)
   :language: python

Welcome
-------

This documentation will guide you through the methods available in the Scroll pHAT HD python library.

Scroll pHAT provides a matrix of 119 individually brightness controlled white LED pixels that is ideal for writing messages, showing graphs, and drawing pictures. Use it to output your IP address, show CPU usage, or just play pong!

* More information - https://shop.pimoroni.com/products/scroll-phat-hd
* Get the code - https://github.com/pimoroni/scroll-phat-hd
* GPIO pinout - https://pinout.xyz/pinout/scroll_phat_hd
* Soldering - https://learn.pimoroni.com/tutorial/sandyj/soldering-phats
* Get help - http://forums.pimoroni.com/c/support

.. currentmodule:: scrollphathd

At A Glance
-----------

.. automoduleoutline:: scrollphathd
   :members:

.. toctree::
   :titlesonly:
   :maxdepth: 0

Set A Single Pixel In Buffer
----------------------------

Scroll pHAT HD uses white LEDs which can be brightness controlled.

When you set a pixel it will not immediately display on Scroll pHAT HD, you must call :python:`scrollphathd.show()`.

.. autofunction:: scrollphathd.set_pixel
   :noindex:

Write A Text String
-------------------

.. autofunction:: scrollphathd.write_string
   :noindex:

Draw A Single Char
------------------

.. autofunction:: scrollphathd.draw_char
   :noindex:

Display A Graph
---------------

.. autofunction:: scrollphathd.set_graph
   :noindex:

Fill An Area
------------

.. autofunction:: scrollphathd.fill
   :noindex:

Clear An Area
-------------

.. autofunction:: scrollphathd.clear_rect
   :noindex:

Display Buffer
--------------

All of your changes to Scroll pHAT HD are stored in a Python buffer. To display them
on Scroll pHAT HD you must call :python:`scrollphathd.show()`.

.. autofunction:: scrollphathd.show
   :noindex:

Clear Buffer
------------

.. autofunction:: scrollphathd.clear
   :noindex:

Scroll The Buffer
-----------------

.. autofunction:: scrollphathd.scroll
   :noindex:

Scroll To A Position
--------------------

.. autofunction:: scrollphathd.scroll_to
   :noindex:

Rotate The Display
------------------

.. autofunction:: scrollphathd.rotate
   :noindex:

Flip The Display
----------------

.. autofunction:: scrollphathd.flip
   :noindex:

Get The Display Size
--------------------

.. autofunction:: scrollphathd.get_shape
   :noindex:

Get The Buffer Size
-------------------

.. autofunction:: scrollphathd.get_buffer_shape
   :noindex:
````

## File: sphinx/requirements.txt
````
alabaster==0.7.12
Babel==2.9.1
certifi==2018.11.29
chardet==3.0.4
colorama==0.4.1
docutils==0.14
funcsigs==1.0.2
idna==2.8
imagesize==1.1.0
Jinja2==2.11.3
MarkupSafe==1.1.0
mock==2.0.0
pbr==5.1.1
Pygments==2.7.4
pytz==2018.9
requests==2.21.0
six==1.12.0
snowballstemmer==1.2.1
Sphinx==1.5.3
sphinx-rtd-theme==0.4.2
urllib3==1.26.5
````

## File: tools/makefonts.sh
````bash
DEST=../library/scrollphathd/fonts/
./mkfont.py 5x7-font.png -m 2 2 -s 2 2 > $DEST/font5x7.py
./mkfont.py 5x7-font-smoothed.png -m 2 2 -s 2 2 > $DEST/font5x7smoothed.py
./mkfont.py 5x7-font-unicode.png -sz 16 16 -fz 5 7 -m 1 1 > $DEST/font5x7unicode.py
./mkfont.py 3x5-font.png -sz 32 3 -fz 3 5 -c " \!\"#\$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_\`abcdefghijklmnopqrstuvwxyz{|}~" > $DEST/font3x5.py
./mkfont.py 5x5-font.png -sz 3 32 -vert -fz 5 5 -c " \!\"#\$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_" > $DEST/font5x5.py
./mkfont.py gauntlet.png -sz 13 3 -fz 7 7 -c 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' > $DEST/fontgauntlet.py
./mkfont.py organ.png -sz 13 3 -fz 13 7 -m 1 1 -s 1 1 -c 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890' > $DEST/fontorgan.py
./mkfont.py hachicro.png -sz 13 4 -fz 7 7 -s 1 1 -m 0 1 -c 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789' > $DEST/fonthachicro.py
./mkfont.py d3.png -sz 13 4 -fz 6 5 -s 0 1 -c 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789' > $DEST/fontd3.py
````

## File: tools/mkfont.py
````python
#!/usr/bin/env python
⋮----
parser = argparse.ArgumentParser(description='Process bitmap into scroll-phat-hd font')
⋮----
args = parser.parse_args()
FONT_FILE = args.file
⋮----
CHAR_SET = []
⋮----
lc = ''
⋮----
lc = c
def get_char_position(char)
⋮----
"""Get the x/y position of the char"""
i = CHAR_SET.index(char)
⋮----
y = i % SHEET_HEIGHT
x = i // SHEET_HEIGHT
⋮----
x = i % SHEET_WIDTH
y = i // SHEET_WIDTH
⋮----
def get_char_coords(x, y)
⋮----
"""Get the x/y position of the char in pixels"""
x = MARGIN_X + (x * (FONT_WIDTH + CHAR_SPACING_X))
y = MARGIN_Y + (y * (FONT_HEIGHT + CHAR_SPACING_Y))
⋮----
def get_color(font_image, color)
⋮----
offset = color * 3
⋮----
def get_char_data(font_image, o_x, o_y)
⋮----
char = [[0 for x in range(FONT_WIDTH)] for y in range(FONT_HEIGHT)]
⋮----
palette_index = font_image.getpixel((o_x + x, o_y + y))
⋮----
color = get_color(font_image, palette_index)
⋮----
def load_font(font_file)
⋮----
font = {}
font_path = os.path.join(os.path.dirname(__file__), font_file)
font_image = Image.open(font_path)
font_image = font_image.convert("P", palette=Image.ADAPTIVE, colors=256)
⋮----
def kern_font(font)
⋮----
badcols = [x == 0 for x in numpy.sum(data, axis=0)]
⋮----
data = numpy.delete(data, 0, axis=1)
⋮----
data = numpy.delete(data, -1, axis=1)
⋮----
badrows = [x == 0 for x in numpy.sum(data, axis=1)]
⋮----
data = numpy.delete(data, -1, axis=0)
⋮----
def show_font_string(font, string)
⋮----
value = font[ord(char)]
⋮----
a = u'\u2591'
⋮----
a = u'\u258b'
⋮----
a = u'\u2593'
⋮----
a = u'\u2592'
⋮----
font = kern_font(load_font(FONT_FILE))
````

## File: .gitignore
````
__pycache__/
sphinx/_build/
*.py[cod]
*.swp
dist/
sdist/
env/
build/
develop-eggs/
eggs/
*.egg-info/
.installed.cfg
*.egg
*.deb
*.dsc
*.build
*.changes
*.orig.*
testing/
MANIFEST
.idea
pip-log.txt
pip-delete-this-directory.txt
library/test/scrollphat/
library/debian/
packaging/*tar.xz
.DS_Store
sphinx.virtualenv
````

## File: .stickler.yml
````yaml
---
linters:
    flake8:
        python: 3
        max-line-length: 160
files:
    ignore:
        - 'library/scrollphathd/fonts/*'
````

## File: LICENSE
````
MIT License

Copyright (c) 2017 Pimoroni Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
````

## File: README.md
````markdown
![Scroll pHAT HD](scroll-phat-hd-logo.png)
https://shop.pimoroni.com/products/scroll-phat-hd

https://shop.pimoroni.com/products/scroll-hat-mini

17x7 pixels of single-colour, brightness-controlled, message scrolling goodness! This library will work with Scroll pHAT HD and Scroll HAT Mini.

## Installing

### Full install (recommended):

We've created an easy installation script that will install all pre-requisites and get your Scroll pHAT HD
up and running with minimal efforts. To run it, fire up Terminal which you'll find in Menu -> Accessories -> Terminal
on your Raspberry Pi desktop, as illustrated below:

![Finding the terminal](http://get.pimoroni.com/resources/github-repo-terminal.png)

In the new terminal window type the command exactly as it appears below (check for typos) and follow the on-screen instructions:

```bash
curl https://get.pimoroni.com/scrollphathd | bash
```

Alternatively, on Raspbian, you can download the `pimoroni-dashboard` and install your product by browsing to the relevant entry:

```bash
sudo apt-get install pimoroni
```
(you will find the Dashboard under 'Accessories' too, in the Pi menu - or just run `pimoroni-dashboard` at the command line)

If you choose to download examples you'll find them in `/home/pi/Pimoroni/scrollphathd/`.

### Manual install:

#### Library install for Python 3:

on Raspbian:

```bash
sudo apt-get install python3-scrollphathd
```

other environments: 

```bash
sudo pip3 install scrollphathd
```

#### Library install for Python 2:

on Raspbian:

```bash
sudo apt-get install python-scrollphathd
```

other environments: 

```bash
sudo pip2 install scrollphathd
```

### Development:

If you want to contribute, or like living on the edge of your seat by having the latest code, you should clone this repository, `cd` to the library directory, and run:

```bash
sudo python3 setup.py install
```
(or `sudo python setup.py install` whichever your primary Python environment may be)

In all cases you will have to enable the i2c bus.

## Alternative Libraries

* Node JS library by @whatsim - https://github.com/whatsim/scrollcontroller

## Documentation & Support

* Guides and tutorials - https://learn.pimoroni.com/scroll-phat-hd
* Function reference - http://docs.pimoroni.com/scrollphathd/
* GPIO Pinout - https://pinout.xyz/pinout/scroll_phat_hd
* Get help - http://forums.pimoroni.com/c/support

## Unofficial / Third-party libraries

* Java library by Jim Darby - https://github.com/hackerjimbo/PiJava
* Rust library by Tiziano Santoro - https://github.com/tiziano88/scroll-phat-hd-rs
* Go library by Tom Mitchell - https://github.com/tomnz/scroll-phat-hd-go
````
