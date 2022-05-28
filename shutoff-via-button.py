#!/usr/bin/python3

from gpiozero import Button
from subprocess import check_call
from signal import pause

def shutdown():
    print("Shutoff button pressed, shutting down now")
    check_call(['sudo', 'poweroff'])

shutdown_btn = Button(17, hold_time=1)
shutdown_btn.when_held = shutdown

pause()