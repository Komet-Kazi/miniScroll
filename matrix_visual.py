#!/usr/bin/env python

# for aborting from the program
from sys import exit

# for handling array operations
import numpy as np

# for controlliung the led matrix
import scrollphathd

# Uncomment the below if your display is upside down
# (e.g. if you're using it in a Pimoroni Scroll Bot)
scrollphathd.rotate(degrees=180)


# Create an 7x17 numpy array of zeros
numpy_matrix = np.zeros((7, 17), dtype=float)

# Accessing and modifying is the same:
numpy_matrix[3, 5] = 1.0

# Numpy arrays print neatly by default and offer powerful array operations
print(numpy_matrix)

# A simple 7x17 matrix initialized with all LEDs off (0 - 1 brightness)
matrix = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

def update_display_loop(matrix):
    #Iterate over matrix and set each pixel according to matrix values
    while True:
        for y in range(0, 7):
            for x in range(0, 17):
                scrollphathd.pixel(x, y, (matrix[y][x]))
        scrollphathd.show()

if __name__ == '__main__':
# Catches control-c and exits cleanly
    try:
        update_display_loop(matrix)

    except KeyboardInterrupt:
        scrollphathd.clear()
        scrollphathd.show()
        print("Exiting!")