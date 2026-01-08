#!/usr/bin/env python3
from gpiozero import Button
import os

#Assign the A button or GPIO pin 5 to watch for shutdown
Button(5).wait_for_press()
os.system("sudo poweroff")