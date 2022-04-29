#!/usr/bin/python3

import math
from gpiozero import Button
from signal import pause
from time import sleep

from sensors import RainVolume

bucket = RainVolume()

print("Waiting for 5 second rain bucket test: add water now")
#pause()

acc = 0
while acc<5:
    sleep(1)
    acc += 1

drops = bucket.getBucketDrops()
print("At the end of 5 seconds, %d bucket drop(s) recorded." % drops)
bucket.resetBucketDrops()
print("----- Rain sensor test complete -----")