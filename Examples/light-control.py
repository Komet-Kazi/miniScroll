#!/usr/bin/env python

from sys import exit
import time
import scrollphathd


class ScrollPhatHD(object):
    def __init__(self):
        # Scroll pHAT HD  dimensions
        self.height = scrollphathd.height
        self.width = scrollphathd.width

        # Rotate and clear the Display on init
        scrollphathd.rotate(180)
        scrollphathd.clear()
        scrollphathd.show()

    def set_pixel(self, x, y, brightness):
        """
        Docstring for set_pixel
        
        :param self: Description
        :param x: Position of pixel from left side of buffer
        :param y: Position of pixel from top side of buffer
        :param brightness: brightness value (0.0 to 1.0)
        """
        scrollphathd.set_pixel(x, y, brightness)

    def show(self):
        """
        Updates the display with the current buffer content.
        
        :param self:
        """
        scrollphathd.show()

    def clear(self):
        """
        Clears the buffer and immediately updates the display.
        
        :param self:
        """
        scrollphathd.clear()
        scrollphathd.show()



    def scroll_message(self, message):
        #scrollphathd.set_font(font)
        self.clear()                         # Clear the display and reset scrolling to (0, 0)
        length = scrollphathd.write_string(message)  # Write out your message
        scrollphathd.show()                          # Show the result
        time.sleep(0.5)                              # Initial delay before scrolling

        length -= scrollphathd.width

        # Now for the scrolling loop...
        while length > 0:
            scrollphathd.scroll(1)                   # Scroll the buffer one place to the left
            scrollphathd.show()                      # Show the result
            length -= 1
            time.sleep(0.02)                         # Delay for each scrolling step

        time.sleep(0.5)                              # Delay at the end of scrolling


def main():
    # set up the scrollPhat
    sphd = ScrollPhatHD()
    
    messages = [
        "Hello, World! ",
        "Welcome to Scroll pHAT HD! ",
        "Enjoy controlling your lights! ",
    ]

    for message in messages:
        sphd.scroll_message(message)


if __name__ == '__main__':
# Catches control-c and exits cleanly
    try:
        main()

    except KeyboardInterrupt:
        scrollphathd.clear()
        scrollphathd.show()
        print("Exiting!")