# for aborting from the program
from sys import exit
import time

# for ease of making nested for loops to represent the 2D Led matrix
import itertools

# different data structures
import collections

from random import shuffle, randint

# for handling array operations
import numpy as np

# for controlling the led matrix
import scrollphathd



def main():
    pass

if __name__ == '__main__':
# Catches control-c and exits cleanly
    try:
        main()

    except KeyboardInterrupt:
        scrollphathd.clear()
        scrollphathd.show()
        print("Exiting!")